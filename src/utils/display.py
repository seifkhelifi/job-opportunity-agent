from typing import Dict, List, Any
import json
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
import pandas as pd
from IPython.display import display, HTML
import re


def parse_workflow_data(file_path: str) -> List[Any]:
    """
    Parse the workflow data from a text file.

    Args:
        file_path: Path to the file containing the workflow data

    Returns:
        List of parsed workflow data items
    """
    with open(file_path, "r") as f:
        data_str = f.read()

    # Split the data by the separator
    lines = data_str.strip().split("\n----\n")
    parsed_data = []

    for line in lines:
        try:
            # Convert the string representation to actual Python objects
            parsed_line = eval(line.strip())
            parsed_data.append(parsed_line)
        except Exception as e:
            print(f"Failed to parse line: {e}")

    return parsed_data


def extract_messages(parsed_data: List[Any]) -> List[Dict]:
    """
    Extract messages from the parsed workflow data.

    Args:
        parsed_data: List of parsed workflow data items

    Returns:
        List of messages with agent information
    """
    all_messages = []

    for item in parsed_data:
        # Skip entries without data dictionary
        if len(item) < 2:
            continue

        data_dict = item[1]

        # Extract messages from each agent or tool entry
        for key, value in data_dict.items():
            if isinstance(value, dict) and "messages" in value:
                messages = value["messages"]
                for msg in messages:
                    # Create message info
                    message_info = {
                        "agent": key,
                        "type": msg.__class__.__name__,
                        "content": getattr(msg, "content", ""),
                        "name": getattr(msg, "name", None),
                        "timestamp": None,  # Could be added if available
                    }

                    # Add additional info for specific message types
                    if hasattr(msg, "additional_kwargs"):
                        message_info["additional_kwargs"] = msg.additional_kwargs

                        # Extract tool calls if present
                        if "tool_calls" in msg.additional_kwargs:
                            message_info["tool_calls"] = msg.additional_kwargs[
                                "tool_calls"
                            ]

                    # Add tool call ID for tool messages
                    if hasattr(msg, "tool_call_id"):
                        message_info["tool_call_id"] = msg.tool_call_id

                    all_messages.append(message_info)

    return all_messages


def format_search_results(content: str) -> str:
    """
    Format search results from the Tavily search into a readable format.

    Args:
        content: JSON string containing search results

    Returns:
        Formatted string with search results
    """
    try:
        # Parse the JSON content
        results = json.loads(content)

        # Create a formatted string
        formatted = "Search Results:\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('title', 'No Title')}\n"
            formatted += f"   URL: {result.get('url', 'No URL')}\n"
            formatted += f"   Relevance: {result.get('score', 'N/A'):.2f}\n"

            # Trim content if too long
            content_text = result.get("content", "No content")
            if len(content_text) > 150:
                content_text = content_text[:150] + "..."
            formatted += f"   Preview: {content_text}\n\n"

        return formatted
    except:
        # If parsing fails, return the raw content
        return f"Raw Content: {content[:300]}..." if len(content) > 300 else content


def display_messages_console(messages: List[Dict]) -> None:
    """
    Display messages in a readable format in the console.

    Args:
        messages: List of message dictionaries
    """
    print("\n========== AGENT WORKFLOW MESSAGES ==========\n")

    for i, msg in enumerate(messages, 1):
        agent = msg["agent"]
        msg_type = msg["type"]

        print(f"Message {i} | Agent: {agent} | Type: {msg_type}")
        print("-" * 50)

        # Handle different message types
        if msg_type == "AIMessage":
            # Display AI message content
            content = msg["content"]
            if content:
                print(
                    f"AI Response: {content[:500]}..."
                    if len(content) > 500
                    else f"AI Response: {content}"
                )
            else:
                # Check for tool calls
                if (
                    "additional_kwargs" in msg
                    and "tool_calls" in msg["additional_kwargs"]
                ):
                    tool_calls = msg["additional_kwargs"]["tool_calls"]
                    print(f"Tool Call Request:")
                    for tool_call in tool_calls:
                        tool_name = tool_call.get("function", {}).get(
                            "name", tool_call.get("name", "Unknown Tool")
                        )
                        args = tool_call.get("function", {}).get("arguments", "{}")
                        print(f"  Tool: {tool_name}")
                        print(f"  Arguments: {args}")

        elif msg_type == "ToolMessage":
            # Format tool message based on the tool name
            if msg.get("name") == "tavily_search_results_json":
                print(format_search_results(msg["content"]))
            else:
                print(
                    f"Tool Response: {msg['content'][:300]}..."
                    if len(msg["content"]) > 300
                    else f"Tool Response: {msg['content']}"
                )

        elif msg_type == "HumanMessage":
            print(
                f"Human Input: {msg['content'][:500]}..."
                if len(msg["content"]) > 500
                else f"Human Input: {msg['content']}"
            )

        else:
            # Generic display for other message types
            print(
                f"Content: {msg['content'][:500]}..."
                if len(msg["content"]) > 500
                else f"Content: {msg['content']}"
            )

        print("\n" + "=" * 50 + "\n")


def display_workflow_summary(parsed_data: List[Any]) -> None:
    """
    Display a summary of the workflow, including agents used and the flow.

    Args:
        parsed_data: List of parsed workflow data items
    """
    # Extract workflow information
    agents_used = set()
    workflow_steps = []

    for item in parsed_data:
        if len(item) == 2 and "supervisor" in item[1]:
            supervisor_data = item[1]["supervisor"]

            if "next" in supervisor_data:
                next_step = supervisor_data["next"]
                used_agents = supervisor_data.get("used_agents", [])

                # Add to agents used
                agents_used.update(used_agents)

                # Add step info
                workflow_steps.append({"next": next_step, "used_agents": used_agents})

    # Display summary
    print("\n========== WORKFLOW SUMMARY ==========\n")
    print(f"Agents Used: {', '.join(agents_used)}")
    print("\nWorkflow Steps:")

    for i, step in enumerate(workflow_steps, 1):
        next_step = step["next"]
        agents = ", ".join(step["used_agents"]) if step["used_agents"] else "None"

        if next_step == "__end__":
            print(f"Step {i}: Used agents: {agents} → End of workflow")
        else:
            print(f"Step {i}: Used agents: {agents} → Next: {next_step}")

    print("\n" + "=" * 40 + "\n")


def process_and_display_workflow(file_path: str, display_mode="console") -> Dict:
    """
    Process workflow data from file and display messages.

    Args:
        file_path: Path to the workflow data file
        display_mode: Display mode ('console', 'html', or 'both')

    Returns:
        Dictionary with parsed data and messages
    """
    # Parse workflow data
    parsed_data = parse_workflow_data(file_path)

    # Extract messages
    messages = extract_messages(parsed_data)

    # Display workflow summary
    display_workflow_summary(parsed_data)

    # Display messages based on the specified mode
    if display_mode == "console" or display_mode == "both":
        display_messages_console(messages)

    return {"parsed_data": parsed_data, "messages": messages}


# Example usage
if __name__ == "__main__":
    # Replace with the path to your workflow data file
    file_path = "out.txt"

    # Process and display the workflow
    result = process_and_display_workflow(file_path, display_mode="console")
