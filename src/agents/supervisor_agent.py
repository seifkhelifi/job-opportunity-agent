from typing_extensions import  Literal
from langgraph.graph import END
from langgraph.types import Command


from prompts.supervisor_prompt import system_prompt
from utils.state import State
from utils.router import Router
from utils.llm import llm


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
