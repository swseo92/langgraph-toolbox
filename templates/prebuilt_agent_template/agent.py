"""
{AgentName} - {Brief Description}

Can be used both as library import and standalone with langgraph dev.

Example:
    >>> from langgraph_toolbox.agents import {AgentName}
    >>> agent = {AgentName}(model="gpt-4o")
    >>> result = agent.invoke({"input": "..."})
"""

from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

# ============= State Definition =============


class {AgentName}State(TypedDict):
    """
    State schema for {AgentName}.

    Attributes:
        messages: Conversation history (required)
        # Add other fields as needed
    """

    messages: Annotated[list, add_messages]
    # Add other fields here
    # example_field: str


# ============= Agent Class =============


class {AgentName}:
    """
    {Detailed description of what this agent does}

    Features:
        - Feature 1
        - Feature 2
        - Feature 3

    Args:
        model: LLM model to use (default: "gpt-4o")
        # Add other parameters

    Examples:
        Basic usage:
            >>> agent = {AgentName}()
            >>> result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})

        Custom configuration:
            >>> agent = {AgentName}(model="claude-sonnet-4")
            >>> result = agent.invoke({...})

    Attributes:
        model: The LLM model instance
        graph: Compiled LangGraph workflow
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        # Add other parameters as needed
    ):
        """Initialize the agent."""
        self.model = ChatOpenAI(model=model)
        # Initialize other attributes
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """
        Create the agent workflow graph.

        Returns:
            Compiled StateGraph
        """
        builder = StateGraph({AgentName}State)

        # Add nodes
        builder.add_node("process", self._process_handler)

        # Add edges
        builder.add_edge(START, "process")
        builder.add_edge("process", END)

        return builder.compile()

    def _process_handler(self, state: {AgentName}State) -> dict:
        """
        Handle main processing logic.

        Args:
            state: Current agent state

        Returns:
            Updated state fields
        """
        messages = state["messages"]
        last_message = messages[-1]

        # TODO: Implement your logic here
        response = self.model.invoke(messages)

        return {"messages": [response]}

    def invoke(self, input_data: dict) -> dict:
        """
        Run the agent.

        Args:
            input_data: Input matching {AgentName}State schema

        Returns:
            Final state after graph execution
        """
        return self.graph.invoke(input_data)

    async def ainvoke(self, input_data: dict) -> dict:
        """Async version of invoke."""
        return await self.graph.ainvoke(input_data)


# ============= Standalone Graph Export =============

# This allows langgraph.json to reference this agent
_default_agent = {AgentName}()
graph = _default_agent.graph


# ============= CLI Entry Point =============

if __name__ == "__main__":
    """
    Direct execution: python -m langgraph_toolbox.agents.prebuilt.{agent_name}.agent
    """
    import sys
    import json

    # Parse CLI arguments
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = {"messages": [{"role": "user", "content": "Hello"}]}

    # Run agent
    agent = {AgentName}()
    result = agent.invoke(input_data)

    # Print result
    print(json.dumps(result, indent=2, default=str))
