"""
Core infrastructure for langgraph-toolbox.

Provides foundational components:
- State management (BaseState, ErrorState, TimestampedState)
- Node registry (NodeRegistry)
- State patterns (merge, update, reducers)
- Observability (tracing, metrics)
"""

from langgraph_toolbox.core.state_base import (
    BaseState,
    ErrorState,
    TimestampedState,
)
from langgraph_toolbox.core.registry import (
    NodeRegistry,
    NodeMetadata,
)
from langgraph_toolbox.core.patterns import (
    merge_subgraph_state,
    update_metadata,
    increment_metadata_counter,
    append_to_metadata_list,
    create_state_reducer,
    merge_lists_unique,
    merge_dicts_deep,
    extract_fields,
)
from langgraph_toolbox.core.tracing import (
    trace_node,
    Span,
    MetricsCollector,
    configure_logging,
    get_default_tracer,
)

__all__ = [
    # State
    "BaseState",
    "ErrorState",
    "TimestampedState",
    # Registry
    "NodeRegistry",
    "NodeMetadata",
    # Patterns
    "merge_subgraph_state",
    "update_metadata",
    "increment_metadata_counter",
    "append_to_metadata_list",
    "create_state_reducer",
    "merge_lists_unique",
    "merge_dicts_deep",
    "extract_fields",
    # Tracing
    "trace_node",
    "Span",
    "MetricsCollector",
    "configure_logging",
    "get_default_tracer",
]
