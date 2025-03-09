from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START

from agents.supervisor_agent import supervisor_node 
from agents.reasoning_agent import reasoning_node
from agents.retreival_agent import retrieval_node
from agents.resume_consultant_agent import resume_node

from utils.state import State



# Build graph
builder = StateGraph(State)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("reasoning", reasoning_node)
builder.add_node("retrieval", retrieval_node)
builder.add_node("resume", resume_node)
graph = builder.compile()


# Example invocation function
def invoke_job_agent(query):
    """Invoke the job agent with better logging and error handling"""
    print(f"Starting job search query: {query}\n")
    # try:
    #     # messages = []
    #     # for s in graph.stream(
    #     #     {"messages": [HumanMessage(content=query)]},
    #     #     subgraphs=True,
    #     # ):
    #     #     # Handle different types of stream output
    #     #     if isinstance(s, tuple) and len(s) == 2:
    #     #         node_id, state_dict = s
    #     #         print(
    #     #             f"Currently at node: {node_id[0] if isinstance(node_id, tuple) else node_id}"
    #     #         )

    #     #         # Extract agent messages when available
    #     #         if (
    #     #             isinstance(state_dict, dict)
    #     #             and "agent" in state_dict
    #     #             and "messages" in state_dict["agent"]
    #     #         ):
    #     #             latest_messages = state_dict["agent"]["messages"]
    #     #             if latest_messages and len(latest_messages) > 0:
    #     #                 latest_message = latest_messages[-1]
    #     #                 content = getattr(
    #     #                     latest_message, "content", str(latest_message)
    #     #                 )
    #     #                 print(
    #     #                     f"Latest message: {content[:100]}..."
    #     #                     if len(content) > 100
    #     #                     else content
    #     #                 )

    #     #     elif isinstance(s, dict):
    #     #         current_step = s.get("next", "unknown")
    #     #         print(f"Currently at: {current_step}")

    #     #         # Extract and print the latest message if available
    #     #         if "messages" in s and s["messages"]:
    #     #             latest_message = s["messages"][-1]
    #     #             if hasattr(latest_message, "content"):
    #     #                 sender = (
    #     #                     latest_message.name
    #     #                     if hasattr(latest_message, "name")
    #     #                     else "system"
    #     #                 )
    #     #                 content = latest_message.content
    #     #                 print(
    #     #                     f"Latest from {sender}: {content[:100]}..."
    #     #                     if len(content) > 100
    #     #                     else content
    #     #                 )

    #     #         # Store the messages for final return
    #     #         messages = s.get("messages", messages)

    #     #     else:
    #     #         print(f"Received unexpected stream item type: {type(s)}")
    #     #         print(f"Content: {str(s)[:200]}...")

    #         print("----")

    #     # Prepare final response by combining all agent outputs
    #     final_response = ""
    #     agents_contributed = set()

    #     for message in messages:
    #         if hasattr(message, "name"):
    #             if message.name not in agents_contributed:
    #                 if (
    #                     message.name == "reasoning"
    #                     and "more information" in message.content
    #                 ):
    #                     # If reasoning agent asked for more info, make that the main response
    #                     final_response = message.content
    #                     break

    #                 agent_prefix = {
    #                     "reasoning": "Analysis: ",
    #                     "retrieval": "Job Market Information: ",
    #                     "resume": "Resume & Career Advice: ",
    #                 }.get(message.name, "")

    #                 if agent_prefix:
    #                     final_response += f"\n\n{agent_prefix}\n{message.content}"
    #                     agents_contributed.add(message.name)

    #     print("\n\nFINAL RESPONSE:")
    #     print(final_response)
    #     return final_response

    # except Exception as e:
    #     print(f"Error during execution: {str(e)}")
    #     import traceback

    #     traceback.print_exc()
    #     return f"I encountered an error while processing your request: {str(e)}"
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
    # Test Case 1: Simple job search query (should use retrieval agent)
    print("\n\n=== Testing with job search query ===")
    invoke_job_agent(
        "I am looking for a job in software engineering in California with a bachelor's degree"
    )

    # Test Case 2: Complex query needing both agents
    print("\n\n=== Testing with complex query needing career advice ===")
    invoke_job_agent(
        "I am an ML engineer with skills in Python, TensorFlow, and data analysis. I have a Master's degree in Computer Science and 2 years of experience, but I can't get interviews"
    )

    # Test Case 3: Insufficient information
    print("\n\n=== Testing with insufficient information ===")
    invoke_job_agent("I am a designer and struggling to find a job")
