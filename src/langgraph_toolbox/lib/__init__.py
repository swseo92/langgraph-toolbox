"""
Shared capabilities layer.

Provides:
- Generic nodes (lib/nodes/)
- Service adapters (lib/services/)
"""

# Import to trigger node registrations
from langgraph_toolbox.lib import nodes
from langgraph_toolbox.lib import services

__all__ = ["nodes", "services"]
