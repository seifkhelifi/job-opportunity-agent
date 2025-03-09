# import getpass
# import os

# from dotenv import load_dotenv

# load_dotenv()


# def _set_if_undefined(var: str):
#     if not os.environ.get(var):
#         os.environ[var] = getpass.getpass(f"Please provide your {var}")


# _set_if_undefined("GROQ_API_KEY")
# _set_if_undefined("TAVILY_API_KEY")


# from typing import Annotated

# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_core.tools import tool
# from langchain_experimental.utilities import PythonREPL

# tavily_tool = TavilySearchResults(max_results=5)


# # This executes code locally, which can be unsafe
# repl = PythonREPL()


# @tool
# def python_repl_tool(
#     code: Annotated[str, "The python code to execute to generate your chart."],
# ):
#     """Use this to execute python code and do math. If you want to see the output of a value,
#     you should print it out with `print(...)`. This is visible to the user."""
#     try:
#         result = repl.run(code)
#     except BaseException as e:
#         return f"Failed to execute. Error: {repr(e)}"
#     result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
#     return result_str


# from typing_extensions import TypedDict, Literal

# from langchain_groq import ChatGroq
# from langgraph.graph import MessagesState, END
# from langgraph.types import Command


# members = ["retrival", "resume"]
# # Our team supervisor is an LLM node. It just picks the next agent to process
# # and decides when the work is completed
# options = members + ["FINISH"]

# system_prompt = """
# You are the Orchestrator for a job plateform, responsible for coordinating specialized agents to help users with their job search and career questions.

# TEAM MEMBERS:
# 1. retrieval: Searches for job listings and provides market information
# 2. resume: Offers resume optimization and career advice

# YOUR RESPONSIBILITIES:
# 1. Analyze the current state of the conversation
# 2. Classify user's intent: retrieval, resume and route to the appropriate agent
# 3. Ensure the user gets a complete and helpful response
# 4. Avoid unnecessary agent calls - only use agents when their specific skills are needed
# 5. Decide when the task is complete

# ROUTING GUIDELINES:
# - Route to Retrieval Agent when job listings or job market information is needed
# - Route to Resume Agent when resume advice or career guidance is needed
# - Route to FINISH when the user's request has been completely addressed

# EXAMPLES OF GOOD ROUTING:

# 1. User asks: "I'm looking for nursing jobs in California with a BSN degree"
#    - First route to Retrieval Agent to find matching nursing jobs
#    - Then FINISH (resume advice not explicitly requested)

# 2. User asks: "I'm a financial analyst with these skills and certifications and can't get interviews"
#    - First route to Retrieval Agent to find relevant financial analyst jobs
#    - Then route to Resume Agent to provide tailored advice
#    - Then FINISH (both job listings and resume were advice provided)

# IMPORTANT:
# - Only route to each agent once, once the age,t returns , ther is no going back to it

# """


# class Router(TypedDict):
#     """Worker to route to next. If no workers needed, route to FINISH."""

#     next: Literal["retrival", "resume", "FINISH"]


# llm = ChatGroq(temperature=1, model_name="llama-3.3-70b-specdec")
# # llm = ChatGroq(temperature=0, model_name="deepseek-r1-distill-llama-70b")


# class State(MessagesState):
#     next: str


# def supervisor_node(state: State) -> Command[Literal["retrival", "resume", "__end__"]]:
#     messages = [
#         {"role": "system", "content": system_prompt},
#     ] + state["messages"]
#     response = llm.with_structured_output(Router).invoke(messages)
#     goto = response["next"]
#     if goto == "FINISH":
#         goto = END

#     return Command(goto=goto, update={"next": goto})


# from langchain_core.messages import HumanMessage
# from langgraph.graph import StateGraph, START, END
# from langgraph.prebuilt import create_react_agent


# # research_agent = create_react_agent(
# #     llm, tools=[tavily_tool], prompt="You are a researcher. DO NOT do any math. you always be happy with first reult even if it is the same"
# # )

# retrival_agent = create_react_agent(
#     llm,
#     tools=[tavily_tool],
#     prompt="""
# You are the Job Retrieval Agent, specialized in finding relevant job opportunities and market information.

# YOUR RESPONSIBILITIES:
# 1. Search for job listings that match the user's criteria and nothing more

# IMPORTANT:
# - Focus on providing factual information about jobs and the job market

# WHEN YOUR TASK IS COMPLETE:
# - Summarize the key findings from your research

# Only use the tools provided to you for research purposes.
# """,
# )


# def retrival_node(state: State) -> Command[Literal["supervisor"]]:
#     result = retrival_agent.invoke(state)
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(content=result["messages"][-1].content, name="retrival")
#             ]
#         },
#         goto="supervisor",
#     )


# resume_prompt = """
# You are the Resume and Career Advice Agent, specialized in helping job seekers optimize their applications and career strategies.

# YOUR RESPONSIBILITIES:
# 1. Search for carrer advice that match the user's criteria
# 1. Provide tailored resume advice for specific roles or industries based on the job retreved from the retrival agent
# 2. Suggest improvements to highlight relevant skills and experiences

# WHEN YOUR TASK IS COMPLETE:
# - Summarize the key findings you arrived at in a clear and concise manner

# Only use the tools provided to you for research purposes.
# """
# # NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION, WHICH CAN BE UNSAFE WHEN NOT SANDBOXED
# resume_agent = create_react_agent(
#     llm,
#     tools=[tavily_tool],
#     prompt=resume_prompt,
# )


# def resume_node(state: State) -> Command[Literal["supervisor"]]:
#     result = resume_agent.invoke(state)
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(content=result["messages"][-1].content, name="resume")
#             ]
#         },
#         goto="supervisor",
#     )


# if __name__ == "__main__":
#     builder = StateGraph(State)
#     builder.add_edge(START, "supervisor")
#     builder.add_node("supervisor", supervisor_node)
#     builder.add_node("retrival", retrival_node)
#     builder.add_node("resume", resume_node)
#     graph = builder.compile()

#     from IPython.display import display, Image

#     display(Image(graph.get_graph().draw_mermaid_png()))

#     # for s in graph.stream(
#     #     {
#     #         "messages": [
#     #             (
#     #                 "user",
#     #                 "I am looking for a job in software engineering in California with a bachelor's degree",
#     #             )
#     #         ]
#     #     },
#     #     subgraphs=True,
#     # ):
#     #     print(s)
#     #     print("----")

#     for s in graph.stream(
#         {
#             "messages": [
#                 (
#                     "user",
#                     "I am an ML engineer with skills in Python, TensorFlow, and data analysis. I have a Master's degree in Computer Science and 2 years of experience, but I can't get interviews",
#                 )
#             ]
#         },
#         subgraphs=True,
#     ):
#         print(s)
#         print("----")


import getpass
import os
from typing import Annotated, List, Set
from typing_extensions import TypedDict, Literal

from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState, END, StateGraph, START
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent

load_dotenv()


def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("GROQ_API_KEY")
_set_if_undefined("TAVILY_API_KEY")

tavily_tool = TavilySearchResults(max_results=5)

# This executes code locally, which can be unsafe
repl = PythonREPL()


@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code and do math. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return result_str


members = ["retrival", "resume"]
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = members + ["FINISH"]

system_prompt = """
You are the Orchestrator for a job platform, responsible for coordinating specialized agents to help users with their job search and career questions.

TEAM MEMBERS:
1. retrieval: Searches for job listings and provides market information
2. resume: Offers resume optimization and career advice

YOUR RESPONSIBILITIES:
1. Analyze the current state of the conversation
2. Classify user's intent: retrieval, resume and route to the appropriate agent
3. Ensure the user gets a complete and helpful response
4. Avoid unnecessary agent calls - only use agents when their specific skills are needed
5. Decide when the task is complete

ROUTING GUIDELINES:
- Route to Retrieval Agent when job listings or job market information is needed
- Route to Resume Agent when resume advice or career guidance is needed
- Route to FINISH when the user's request has been completely addressed
- IMPORTANT: You can only route to each agent ONCE. Once an agent has been used, you cannot route to it again.

EXAMPLES OF GOOD ROUTING:

1. User asks: "I'm looking for nursing jobs in California with a BSN degree" ==> intent : retrieval
   - First route to Retrieval Agent to find matching nursing jobs
   - Then FINISH (resume advice not explicitly requested)

2. User asks: "I'm a financial analyst with these skills and certifications and can't get interviews" ==> intent : retrieval, resume
   - First route to Retrieval Agent to find relevant financial analyst jobs
   - Then route to Resume Agent to provide tailored advice
   - Then FINISH (both job listings and resume were advice provided)
   
IMPORTANT:
- Check the list of already_used_agents before making your routing decision
- Always comapare your the intent with the routed agent : 1 agent route for each intent
- In the case you used 2 agents , always route to finish
"""


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal["retrival", "resume", "FINISH"]


llm = ChatGroq(temperature=1, model_name="llama-3.3-70b-specdec")
# llm = ChatGroq(temperature=0, model_name="deepseek-r1-distill-llama-70b")


class State(MessagesState):
    next: str
    used_agents: List[str]  # Track which agents have been used


def supervisor_node(state: State) -> Command[Literal["retrival", "resume", "__end__"]]:
    # Create a modified system prompt that includes info about already used agents
    used_agents_list = state.get("used_agents", [])
    used_agents_str = ", ".join(used_agents_list) if used_agents_list else "None"

    modified_system_prompt = (
        system_prompt + f"\n\nALREADY USED AGENTS: {used_agents_str}"
    )

    messages = [
        {"role": "system", "content": modified_system_prompt},
    ] + state["messages"]

    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]

    # Check if the agent has already been used
    if goto in used_agents_list and goto != "FINISH":
        # If already used, force to FINISH
        goto = "FINISH"

    if goto == "FINISH":
        goto = END
    else:
        # Add the agent to the used_agents list
        used_agents_list.append(goto)

    return Command(goto=goto, update={"next": goto, "used_agents": used_agents_list})


retrival_agent = create_react_agent(
    llm,
    tools=[tavily_tool],
    prompt="""
You are the Job Retrieval Agent, specialized in finding relevant job opportunities and market information.

YOUR RESPONSIBILITIES:
1. Search for job listings that match the user's criteria and nothing more

IMPORTANT:
- Focus on providing factual information about jobs and the job market

WHEN YOUR TASK IS COMPLETE:
- Summarize the key findings from your research

Only use the tools provided to you for research purposes.
""",
)


def retrival_node(state: State) -> Command[Literal["supervisor"]]:
    result = retrival_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="retrival")
            ]
        },
        goto="supervisor",
    )


resume_prompt = """
You are the Resume and Career Advice Agent, specialized in helping job seekers optimize their applications and career strategies.

YOUR RESPONSIBILITIES:
1. Search for career advice that match the user's criteria 
2. Provide tailored resume advice for specific roles or industries based on the job retrieved from the retrieval agent
3. Suggest improvements to highlight relevant skills and experiences

WHEN YOUR TASK IS COMPLETE:
- Summarize the key findings you arrived at in a clear and concise manner

Only use the tools provided to you for research purposes.
"""

resume_agent = create_react_agent(
    llm,
    tools=[tavily_tool],
    prompt=resume_prompt,
)


def resume_node(state: State) -> Command[Literal["supervisor"]]:
    result = resume_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="resume")
            ]
        },
        goto="supervisor",
    )


if __name__ == "__main__":
    builder = StateGraph(State)
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("retrival", retrival_node)
    builder.add_node("resume", resume_node)
    graph = builder.compile()

    from IPython.display import display, Image

    display(Image(graph.get_graph().draw_mermaid_png()))

    # print("Test Case 1:")
    # for s in graph.stream(
    #     {
    #         "messages": [
    #             (
    #                 "user",
    #                 "I am looking for a job in software engineering in California with a bachelor's degree",
    #             )
    #         ],
    #         "used_agents": [],  # Initialize empty list of used agents
    #     },
    #     subgraphs=True,
    # ):
    #     print(s)
    #     print("----")

    # print("\nTest Case 2:")
    # for s in graph.stream(
    #     {
    #         "messages": [
    #             (
    #                 "user",
    #                 "I am an ML engineer with skills in Python, TensorFlow, and data analysis. I have a Master's degree in Computer Science and 2 years of experience, but I can't get interviews",
    #             )
    #         ],
    #         "used_agents": [],  # Initialize empty list of used agents
    #     },
    #     subgraphs=True,
    # ):
    #     print(s)
    #     print("----")

    print("\nTest Case 3:")
    for s in graph.stream(
        {
            "messages": [
                (
                    "user",
                    "Hello, i am a passionate about cloud technologies however i don't now where to start in order to get a job in the current market",
                )
            ],
            "used_agents": [],  # Initialize empty list of used agents
        },
        subgraphs=True,
    ):
        print(s)
        print("----")
