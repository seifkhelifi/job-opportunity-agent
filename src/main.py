from langgraph.graph import StateGraph, START

from agents.supervisor_agent import supervisor_node
from agents.retreival_agent import retrival_node
from agents.resume_consultant_agent import resume_node

from utils.state import State
from utils.display import process_and_display_workflow

if __name__ == "__main__":
    builder = StateGraph(State)
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("retrival", retrival_node)
    builder.add_node("resume", resume_node)
    graph = builder.compile()

    print("Test Case 1:")
    for s in graph.stream(
        {
            "messages": [
                (
                    "user",
                    "I am looking for a job in software engineering in California with a bachelor's degree",
                )
            ],
            "used_agents": [],  # Initialize empty list of used agents
        },
        subgraphs=True,
    ):
        process_and_display_workflow(s, display_mode="console")
        print("----")

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

    # print("\nTest Case 3:")
    # for s in graph.stream(
    #     {
    #         "messages": [
    #             (
    #                 "user",
    #                 "Hello, i am a passionate about cloud technologies however i don't now where to start in order to get a job in the current market",
    #             )
    #         ],
    #         "used_agents": [],  # Initialize empty list of used agents
    #     },
    #     subgraphs=True,
    # ):
    #     process_and_display_workflow(s, display_mode="console")
    #     print("----")
