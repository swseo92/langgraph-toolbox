# Core Infrastructure

**Layer**: Foundation
**Purpose**: Foundational infrastructure used by all other layers

---

## 📋 Overview

The core layer provides the fundamental building blocks for the entire library: state management, node registry, common patterns, and observability. All other layers depend on core, but core depends on nothing.

---

## 🎯 Responsibilities

**This layer SHOULD**:
- ✅ Define base state classes
- ✅ Implement node registry system
- ✅ Provide state manipulation patterns
- ✅ Handle observability (tracing, logging)
- ✅ Define common interfaces and protocols

**This layer SHOULD NOT**:
- ❌ Implement business logic
- ❌ Know about specific domains (search, analysis, etc.)
- ❌ Know about specific agents or subgraphs
- ❌ Import from `lib/`, `subgraphs/`, or `agents/`

---

## 📁 Structure

```
core/
├── __init__.py
├── state_base.py         # Base state classes
├── registry.py           # Node registry system
├── patterns.py           # State manipulation patterns
├── tracing.py            # Observability infrastructure
└── tests/
    ├── test_state_base.py
    ├── test_registry.py
    ├── test_patterns.py
    └── test_tracing.py
```

---

## 🧩 Core Components

### 1. State Base (`state_base.py`)

**Purpose**: Provide base state class that all other states inherit from.

**Features**:
- Common fields (messages, metadata)
- Type safety (Pydantic validation)
- Serialization support

**Implementation**:
```python
# core/state_base.py
from pydantic import BaseModel, Field
from typing import Optional

class BaseState(BaseModel):
    """
    Base state class for all LangGraph states.

    All agent and subgraph states should inherit from this.

    Attributes:
        messages: Conversation history
        metadata: Arbitrary metadata (workflow info, timing, etc.)
    """
    messages: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
        # Allow adding fields at runtime for flexibility
        extra = "allow"
```

**Usage**:
```python
from langgraph_toolbox.core.state_base import BaseState

class MyState(BaseState):
    """Custom state with additional fields."""
    query: str
    results: list[dict] = []
```

### 2. Node Registry (`registry.py`)

**Purpose**: Central registry for discovering and using nodes.

**Features**:
- Decorator-based registration
- Category organization
- Metadata tracking
- Runtime lookup

**Implementation**:
```python
# core/registry.py
from typing import Callable, Dict, Optional
from dataclasses import dataclass

@dataclass
class NodeMetadata:
    """Metadata about a registered node."""
    name: str
    func: Callable
    category: str
    description: str

class NodeRegistry:
    """
    Central registry for all nodes in the library.

    Nodes register themselves using the @NodeRegistry.register decorator.
    Agents and subgraphs look up nodes using NodeRegistry.get().
    """
    _nodes: Dict[str, NodeMetadata] = {}

    @classmethod
    def register(cls, name: str, category: str = "general"):
        """
        Decorator to register a node.

        Args:
            name: Unique node identifier
            category: Category for organization (retrieval, routing, llm, etc.)

        Example:
            @NodeRegistry.register("my_node", category="processing")
            def my_node(state: State) -> dict:
                return {"result": "value"}
        """
        def decorator(func: Callable) -> Callable:
            cls._nodes[name] = NodeMetadata(
                name=name,
                func=func,
                category=category,
                description=func.__doc__ or ""
            )
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Callable:
        """
        Get a registered node by name.

        Args:
            name: Node identifier

        Returns:
            Node function

        Raises:
            KeyError: If node not found
        """
        if name not in cls._nodes:
            available = ", ".join(cls._nodes.keys())
            raise KeyError(
                f"Node '{name}' not registered. "
                f"Available nodes: {available}"
            )
        return cls._nodes[name].func

    @classmethod
    def list_nodes(cls, category: Optional[str] = None) -> list[NodeMetadata]:
        """
        List all registered nodes, optionally filtered by category.

        Args:
            category: Filter by category (optional)

        Returns:
            List of node metadata
        """
        nodes = list(cls._nodes.values())
        if category:
            nodes = [n for n in nodes if n.category == category]
        return nodes

    @classmethod
    def clear(cls):
        """Clear all registered nodes (for testing)."""
        cls._nodes.clear()
```

**Usage**:
```python
# Register a node
from langgraph_toolbox.core.registry import NodeRegistry

@NodeRegistry.register("my_node", category="processing")
def my_node(state: State) -> dict:
    """Process state."""
    return {"processed": True}

# Use a node
from langgraph_toolbox.core.registry import NodeRegistry

builder.add_node("process", NodeRegistry.get("my_node"))

# List all nodes in a category
retrieval_nodes = NodeRegistry.list_nodes(category="retrieval")
for node in retrieval_nodes:
    print(f"{node.name}: {node.description}")
```

### 3. State Patterns (`patterns.py`)

**Purpose**: Common state manipulation patterns.

**Features**:
- State merging
- State reducers
- State transformation utilities

**Implementation**:
```python
# core/patterns.py
from typing import TypeVar, Callable

T = TypeVar('T')

def merge_subgraph_state(
    parent: dict,
    child: dict,
    field_mapping: dict[str, str]
) -> dict:
    """
    Merge child subgraph state into parent state.

    Args:
        parent: Parent state dict
        child: Child subgraph result state
        field_mapping: Map child fields to parent fields
                      {"parent_field": "child_field"}

    Returns:
        Merged state dict

    Example:
        parent = {"query": "test", "results": []}
        child = {"search_results": [1, 2, 3]}
        mapping = {"results": "search_results"}

        merged = merge_subgraph_state(parent, child, mapping)
        # merged = {"query": "test", "results": [1, 2, 3]}
    """
    merged = dict(parent)
    for parent_key, child_key in field_mapping.items():
        if child_key in child:
            merged[parent_key] = child[child_key]
    return merged

def create_state_reducer(field_name: str, reducer_func: Callable) -> Callable:
    """
    Create a state reducer function for a specific field.

    Args:
        field_name: Field to reduce
        reducer_func: Function to apply (e.g., sum, max, concatenate)

    Returns:
        Reducer function for use with Annotated[type, reducer]

    Example:
        from langgraph.graph.message import add_messages

        # Built-in
        messages: Annotated[list, add_messages]

        # Custom
        def merge_scores(existing: list, new: list) -> list:
            return existing + new

        scores: Annotated[list, create_state_reducer("scores", merge_scores)]
    """
    def reducer(existing, new):
        return reducer_func(existing, new)
    return reducer

def update_metadata(
    state: dict,
    updates: dict
) -> dict:
    """
    Update metadata without overwriting entire dict.

    Args:
        state: Current state
        updates: Metadata fields to update

    Returns:
        State dict with updated metadata

    Example:
        state = {"metadata": {"step": 1}}
        updated = update_metadata(state, {"status": "processing"})
        # metadata = {"step": 1, "status": "processing"}
    """
    metadata = state.get("metadata", {})
    metadata.update(updates)
    return {"metadata": metadata}
```

**Usage**:
```python
# Merge subgraph results
from langgraph_toolbox.core.patterns import merge_subgraph_state

def orchestrator_node(state: ResearchState) -> dict:
    # Run search subgraph
    search_result = search_graph.invoke({"query": state.query})

    # Merge results into parent state
    mapping = {
        "search_results": "results",
        "search_metadata": "metadata"
    }
    merged = merge_subgraph_state(state, search_result, mapping)

    return merged

# Update metadata
from langgraph_toolbox.core.patterns import update_metadata

def my_node(state: State) -> dict:
    # Do work
    result = process(state)

    # Update metadata
    return update_metadata(
        {"result": result},
        {"processed_at": time.time(), "version": "1.0"}
    )
```

### 4. Tracing (`tracing.py`)

**Purpose**: Observability infrastructure for debugging and monitoring.

**Features**:
- Node execution tracing
- Performance metrics
- Error tracking
- LangSmith integration

**Implementation**:
```python
# core/tracing.py
from contextlib import contextmanager
from typing import Optional, Any
import time
import logging

logger = logging.getLogger(__name__)

class Span:
    """Represents a traced operation."""

    def __init__(self, name: str, state: dict):
        self.name = name
        self.state = state
        self.start_time = time.time()
        self.error: Optional[Exception] = None
        self.metrics: dict = {}

    def log_success(self, **metrics):
        """Log successful completion with metrics."""
        duration = time.time() - self.start_time
        self.metrics = {"duration_ms": duration * 1000, **metrics}
        logger.info(f"✓ {self.name} completed in {duration*1000:.2f}ms")

    def log_error(self, error: Exception):
        """Log error."""
        duration = time.time() - self.start_time
        self.error = error
        self.metrics = {"duration_ms": duration * 1000}
        logger.error(f"✗ {self.name} failed after {duration*1000:.2f}ms: {error}")

    def end(self):
        """End span."""
        pass  # Hook for external tracers (LangSmith, OpenTelemetry)

@contextmanager
def trace_node(node_name: str, state: dict):
    """
    Trace node execution.

    Args:
        node_name: Name of the node being executed
        state: Current state

    Yields:
        Span object for logging additional info

    Example:
        def my_node(state: State) -> dict:
            with trace_node("my_node", state) as span:
                result = do_work(state)
                span.log_success(items_processed=len(result))
                return {"result": result}
    """
    span = Span(node_name, state)
    logger.info(f"→ {node_name} starting")

    try:
        yield span
        span.log_success()
    except Exception as e:
        span.log_error(e)
        raise
    finally:
        span.end()

def get_default_tracer():
    """Get default tracer (LangSmith if available)."""
    try:
        from langsmith import Client
        return Client()
    except ImportError:
        return None
```

**Usage**:
```python
from langgraph_toolbox.core.tracing import trace_node

@NodeRegistry.register("my_node")
def my_node(state: State) -> dict:
    with trace_node("my_node", state) as span:
        # Do work
        results = process(state.query)

        # Log metrics
        span.log_success(
            result_count=len(results),
            cache_hit=True
        )

        return {"results": results}
```

---

## 🧪 Testing

```bash
# Test all core components
pytest src/langgraph_toolbox/core/tests/

# Test specific component
pytest src/langgraph_toolbox/core/tests/test_registry.py

# Test with coverage
pytest src/langgraph_toolbox/core/ --cov=langgraph_toolbox.core
```

---

## 📚 Examples

### Example 1: Custom Base State

```python
# core/state_base.py extension
from langgraph_toolbox.core.state_base import BaseState
from pydantic import Field

class TimestampedState(BaseState):
    """State with automatic timestamp tracking."""
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def update(self, **kwargs):
        """Update state and refresh timestamp."""
        self.updated_at = time.time()
        for key, value in kwargs.items():
            setattr(self, key, value)
```

### Example 2: Registry with Validation

```python
# core/registry.py extension
from typing import get_type_hints

class ValidatedNodeRegistry(NodeRegistry):
    """Registry with runtime type validation."""

    @classmethod
    def register(cls, name: str, category: str = "general", validate: bool = True):
        def decorator(func: Callable):
            if validate:
                # Validate node signature
                hints = get_type_hints(func)
                if "state" not in hints:
                    raise TypeError(f"Node {name} must have 'state' parameter")
                if hints.get("return") != dict:
                    raise TypeError(f"Node {name} must return dict")

            return super().register(name, category)(func)
        return decorator
```

---

## 🔗 See Also

- [Design Philosophy](../../../docs/architecture/design-philosophy.md)
- [Lib Nodes](../lib/nodes/README.md) - Using the registry
- [Subgraphs](../subgraphs/README.md) - Using state patterns
- [Agents](../agents/prebuilt/README.md) - Using core infrastructure
