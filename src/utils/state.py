from typing import List
from langgraph.graph import MessagesState


class State(MessagesState):
    next: str
    used_agents: List[str]  # Track which agents have been used
