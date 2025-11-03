"""
Example agent for LangGraph Studio testing.

This is a simple example agent that demonstrates LangGraph Studio integration.
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    """Agent state with message history."""

    messages: Annotated[list, add_messages]


def chatbot_node(state: State) -> dict:
    """
    Simple chatbot node that echoes messages.

    Args:
        state: Current state with messages

    Returns:
        Updated state with response
    """
    messages = state["messages"]
    last_message = messages[-1]

    response = {
        "role": "assistant",
        "content": f"Echo: {last_message['content']}"
    }

    return {"messages": [response]}


# Build the graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# Compile the graph
graph = builder.compile()
