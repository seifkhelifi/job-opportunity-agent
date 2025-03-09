# Create resume agent for career advice
from typing_extensions import Literal

from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langchain_core.messages import HumanMessage


from utils.llm import llm
from prompts.resume_prompt import resume_prompt
from tools.tavily_search import tavily_tool

from utils.state import State

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
