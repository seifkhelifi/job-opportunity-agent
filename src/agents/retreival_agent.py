from typing_extensions import Literal
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage


from prompts.retrieve_prompt import prompt
from utils.llm import llm
from utils.state import State
from tools.tavily_search import tavily_tool

retrival_agent = create_react_agent(
    llm,
    tools=[tavily_tool],
    prompt=prompt,
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
