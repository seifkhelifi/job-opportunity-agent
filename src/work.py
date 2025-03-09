import os
from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict, Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_experimental.utilities import PythonREPL
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langchain_community.tools.tavily_search import TavilySearchResults


import getpass
import os

from dotenv import load_dotenv

load_dotenv()


def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("GROQ_API_KEY")
_set_if_undefined("TAVILY_API_KEY")


# Initialize tools
repl = PythonREPL()

tavily_tool = TavilySearchResults(max_results=5)


@tool
def python_repl_tool(
    code: Annotated[
        str,
        "The python code to execute to generate your chart or perform calculations.",
    ],
):
    """Use this to execute python code for mathematical calculations or data visualization. If you want to see the output of a value,
    you should print it out with print(...). This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n\npython\n{code}\n\nStdout: {result}"
    return result_str


# Define LLM
llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")


# Create extended state to track task progress
class State(MessagesState):
    next: str
    task_status: Dict[str, Any] = {}  # Track completion status of tasks
    iteration_count: Dict[str, int] = (
        {}
    )  # Track calls to each agent to prevent infinite loops


# Define structured output for supervisor decisions
class Router(TypedDict):
    """Worker to route to next."""

    next: Literal["researcher", "coder", "FINISH"]
    reasoning: str  # Require reasoning to be explicit


# Create improved agent prompts with clearer roles and examples
researcher_prompt = """
You are a Research Agent specialized in gathering accurate information.

YOUR RESPONSIBILITIES:
1. Find factual information, statistics, and data
2. Answer knowledge-based questions
3. DO NOT perform calculations - that's the Coder's job
4. DO NOT write code - that's the Coder's job

EXAMPLES OF APPROPRIATE TASKS:
- "What is the GDP of New York?"
- "Find information about the latest AI developments"
- "What was the unemployment rate in 2023?"

WHEN YOU COMPLETE YOUR TASK:
- Clearly state that your research is complete
- Summarize what information you found
- If you need calculations on the data you found, clearly state what calculations are needed

Only use the tools provided to you for research purposes.
"""

coder_prompt = """
You are a Coding Agent specialized in executing Python code for calculations and data visualization.

YOUR RESPONSIBILITIES:
1. Write and execute Python code
2. Perform mathematical calculations
3. Create data visualizations when requested
4. Process and transform data

EXAMPLES OF APPROPRIATE TASKS:
- "Calculate the square root of 42"
- "Compute the average of these numbers: 10, 15, 20"
- "Create a bar chart comparing these values"
- "Process this dataset to find patterns"

WHEN YOU COMPLETE YOUR TASK:
- Clearly state that your coding task is complete
- Summarize the results of your calculations or code execution
- If the results need explanation, provide a brief interpretation

Always make sure your code is correct before execution and handle potential errors appropriately.
"""

# Create an improved supervisor with clear decision criteria
supervisor_prompt = """
You are a Supervisor Agent responsible for coordinating a team of specialized agents to complete a user's request efficiently.

TEAM MEMBERS:
1. Researcher: Gathers factual information and data. Cannot perform calculations or write code.
2. Coder: Writes and executes Python code for calculations and data visualization. Needs clear instructions on what to calculate.

YOUR RESPONSIBILITIES:
1. Analyze the user's request and determine which agent should act next
2. Avoid unnecessary agent calls - only use agents when their specific skills are needed
3. Prevent infinite loops by ensuring progress is made with each agent call
4. Decide when the task is complete and can be finished

ROUTING GUIDELINES:
- Route to Researcher first when factual information or data is needed
- Route to Coder when calculations, code execution, or data processing is needed
- Route to FINISH when the user's request has been completely addressed

EXAMPLES OF GOOD ROUTING:
1. User asks "What's the square root of 42?"
   - Route directly to Coder (no research needed for known mathematical operations)

2. User asks "Find the GDP of California and New York, then calculate the average"
   - First route to Researcher to get the GDP figures
   - Then route to Coder to calculate the average
   - Then FINISH when the average is calculated

3. User asks "Tell me a joke about cats"
   - Route to FINISH (neither research nor coding needed for this simple request)

IMPORTANT: Always include your reasoning for why you're routing to a specific agent. If you've routed to the same agent more than twice in a row without progress, consider a different approach.
"""


# Create improved supervisor node with loop prevention
def supervisor_node(state: State) -> Command[Literal["researcher", "coder", "__end__"]]:
    # Initialize iteration counts if not present
    if "iteration_count" not in state:
        state["iteration_count"] = {"researcher": 0, "coder": 0}

    messages = [
        {"role": "system", "content": supervisor_prompt},
    ] + state["messages"]

    # Add context about current state to help supervisor make better decisions
    status_message = {
        "role": "system",
        "content": f"Current task status: {state.get('task_status', {})}. Iteration counts: {state.get('iteration_count', {})}",
    }
    messages.append(status_message)

    structured_model = llm.with_structured_output(Router)
    response = structured_model.invoke(messages)

    goto = response["next"]
    reasoning = response["reasoning"]

    # Update iteration count
    if goto != "FINISH":
        state["iteration_count"][goto] = state["iteration_count"].get(goto, 0) + 1

        # Prevent infinite loops - if an agent has been called more than 3 times, force completion
        if state["iteration_count"][goto] > 3:
            print(
                f"WARNING: Potential infinite loop detected with {goto}. Forcing completion."
            )
            goto = "FINISH"

    if goto == "FINISH":
        goto = END

    # Add reasoning to state for transparency
    if "task_status" not in state:
        state["task_status"] = {}
    state["task_status"]["last_routing_decision"] = reasoning

    return Command(
        goto=goto,
        update={
            "next": goto,
            "iteration_count": state["iteration_count"],
            "task_status": state["task_status"],
        },
    )


# Create improved agent nodes
research_agent = create_react_agent(
    llm,
    tools=[tavily_tool],
    prompt=researcher_prompt,
)


def research_node(state: State) -> Command[Literal["supervisor"]]:
    # Check if we already have research results for this query to avoid duplication
    if "research_complete" in state.get("task_status", {}):
        # Add a message indicating we're using existing research
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content="Using existing research results.", name="researcher"
                    )
                ],
                "task_status": {
                    **state.get("task_status", {}),
                    "research_reused": True,
                },
            },
            goto="supervisor",
        )

    result = research_agent.invoke(state)

    # Mark research as complete
    task_status = state.get("task_status", {})
    task_status["research_complete"] = True
    task_status["research_results"] = result["messages"][-1].content

    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="researcher")
            ],
            "task_status": task_status,
        },
        goto="supervisor",
    )


code_agent = create_react_agent(
    llm,
    tools=[python_repl_tool],
    prompt=coder_prompt,
)


def code_node(state: State) -> Command[Literal["supervisor"]]:
    result = code_agent.invoke(state)

    # Mark coding as complete
    task_status = state.get("task_status", {})
    task_status["coding_complete"] = True
    task_status["coding_results"] = result["messages"][-1].content

    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="coder")
            ],
            "task_status": task_status,
        },
        goto="supervisor",
    )


# Build graph
builder = StateGraph(State)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("researcher", research_node)
builder.add_node("coder", code_node)
graph = builder.compile()


# Example invocation function
def invoke_team(query):
    """Invoke the team with better logging and error handling"""
    print(f"Starting task: {query}\n")
    try:
        messages = []
        for s in graph.stream(
            {"messages": [HumanMessage(content=query)]},
            subgraphs=True,
        ):
            print(s)
            print("==============================================")
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        return []


# Example usage
if __name__ == "__main__":
    # Simple math query (should go straight to coder)
    # print("\n\n=== Testing with math query ===")
    # invoke_team("What is the circumfrence of a circle with diameter 10?")

    # Complex query requiring both agents
    print("\n\n=== Testing with complex query ===")
    invoke_team(
        "Find the latest GDP of New York and California, then calculate the average"
    )
