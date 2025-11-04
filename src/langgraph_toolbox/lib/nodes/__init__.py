"""
Generic, reusable nodes for LangGraph workflows.

These nodes are domain-independent and can be used across
any agent or subgraph. They use Protocol-based type hints
for maximum flexibility.

Categories:
- research: Web search, filtering, summarization
- (more categories coming soon)
"""

# Research nodes are registered via NodeRegistry
# Import the module to trigger registration
from langgraph_toolbox.lib.nodes import research_nodes

__all__ = ["research_nodes"]
