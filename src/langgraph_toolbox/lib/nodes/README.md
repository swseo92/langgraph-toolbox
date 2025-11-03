# Generic Nodes Library

**Layer**: Shared Capabilities - Nodes
**Purpose**: Generic, reusable nodes that can be used across any agent or subgraph

---

## 📋 Overview

This directory contains atomic, single-purpose nodes that implement common operations. These nodes are **domain-agnostic** and **highly reusable** across different agents and subgraphs.

---

## 🎯 Responsibilities

**This layer SHOULD**:
- ✅ Implement atomic, single-purpose operations
- ✅ Be generic (work with any compatible state)
- ✅ Use Protocol/ABC for type hints (not concrete states)
- ✅ Delegate to `lib/services/` for external interactions
- ✅ Register with NodeRegistry for discoverability

**This layer SHOULD NOT**:
- ❌ Know about specific domains (search, analysis, etc.)
- ❌ Make assumptions about state structure
- ❌ Directly interact with external APIs (use services)
- ❌ Implement complex workflows (use subgraphs)

---

## 📁 Structure

```
lib/nodes/
├── __init__.py
├── retrieval.py          # Vector search, document retrieval
├── routing.py            # Conditional routing logic
├── llm_nodes.py          # LLM interaction nodes
├── transformation.py     # Data transformation nodes
└── tests/
    ├── test_retrieval.py
    ├── test_routing.py
    └── test_llm_nodes.py
```

**Naming Convention**:
- Group by capability (retrieval, routing, transformation)
- One file per category
- Clear, descriptive function names

---

## 🚀 Creating a Generic Node

### Step 1: Define State Protocol

Use Protocols to define required state fields without concrete types:

```python
# lib/nodes/retrieval.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class RetrievableState(Protocol):
    """Protocol for states that support retrieval operations."""
    query: str
```

**Why Protocols?**
- Flexible: Any state with `query` field works
- Type-safe: Static type checkers validate
- No coupling: Don't depend on concrete state classes

### Step 2: Implement Node

```python
from langgraph_toolbox.core.registry import NodeRegistry
from langgraph_toolbox.lib.services.vectorstore import VectorStoreService

@NodeRegistry.register("vector_search", category="retrieval")
def vector_search_node(state: RetrievableState, top_k: int = 10) -> dict:
    """
    Perform vector similarity search.

    Args:
        state: State with 'query' field
        top_k: Number of results to return

    Returns:
        dict with 'results' field containing search results
    """
    service = VectorStoreService()
    results = service.search(state.query, top_k=top_k)

    return {"results": results}
```

**Best Practices**:
- ✅ Use `@NodeRegistry.register` decorator
- ✅ Add category for organization
- ✅ Include comprehensive docstring
- ✅ Return dict (LangGraph merges into state)
- ✅ Keep logic simple (delegate to services)

### Step 3: Write Tests

```python
# lib/nodes/tests/test_retrieval.py
import pytest
from unittest.mock import Mock, patch
from langgraph_toolbox.lib.nodes.retrieval import vector_search_node

class MockState:
    """Mock state for testing."""
    query: str = "test query"

def test_vector_search_node():
    """Test vector search returns results."""
    with patch('langgraph_toolbox.lib.services.vectorstore.VectorStoreService') as mock:
        mock.return_value.search.return_value = [{"id": 1, "text": "result"}]

        state = MockState()
        result = vector_search_node(state)

        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["id"] == 1

def test_vector_search_node_top_k():
    """Test vector search respects top_k parameter."""
    with patch('langgraph_toolbox.lib.services.vectorstore.VectorStoreService') as mock:
        mock.return_value.search.return_value = []

        state = MockState()
        vector_search_node(state, top_k=5)

        mock.return_value.search.assert_called_once_with("test query", top_k=5)
```

---

## 📝 Node Categories

### Retrieval Nodes

**Purpose**: Fetch data from external sources

**Examples**:
- `vector_search_node`: Semantic search
- `keyword_search_node`: Traditional search
- `document_retrieval_node`: Fetch specific documents

```python
@NodeRegistry.register("vector_search", category="retrieval")
def vector_search_node(state: RetrievableState, top_k: int = 10) -> dict:
    # Implementation
    pass
```

### Routing Nodes

**Purpose**: Conditional branching logic

**Examples**:
- `route_by_confidence`: Route based on confidence scores
- `route_by_length`: Route based on content length
- `route_by_topic`: Route based on topic classification

```python
@NodeRegistry.register("route_by_confidence", category="routing")
def route_by_confidence(state: RoutableState) -> str:
    """Return route name based on confidence score."""
    return "high" if state.confidence > 0.8 else "low"
```

### LLM Nodes

**Purpose**: Interact with language models

**Examples**:
- `llm_generate`: Generate text
- `llm_classify`: Classify text
- `llm_extract`: Extract structured data

```python
@NodeRegistry.register("llm_generate", category="llm")
def llm_generate_node(state: GeneratableState, model: str = "gpt-4o") -> dict:
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model=model)
    response = llm.invoke(state.messages)

    return {"messages": [response]}
```

### Transformation Nodes

**Purpose**: Transform data structures

**Examples**:
- `format_results`: Format search results
- `merge_data`: Merge multiple data sources
- `filter_content`: Filter content by criteria

```python
@NodeRegistry.register("format_results", category="transformation")
def format_results_node(state: FormattableState) -> dict:
    formatted = [
        {"title": r["title"], "summary": r["text"][:200]}
        for r in state.results
    ]
    return {"formatted_results": formatted}
```

---

## 🎨 Design Patterns

### Pattern 1: Factory Functions

For nodes with configuration:

```python
def create_llm_node(model: str, temperature: float = 0.7):
    """Factory function for creating configured LLM nodes."""
    @NodeRegistry.register(f"llm_{model}", category="llm")
    def llm_node(state: GeneratableState) -> dict:
        llm = ChatOpenAI(model=model, temperature=temperature)
        response = llm.invoke(state.messages)
        return {"messages": [response]}

    return llm_node

# Usage
create_llm_node("gpt-4o", temperature=0.3)
create_llm_node("gpt-4o-mini", temperature=0.9)
```

### Pattern 2: Composable Nodes

Nodes that wrap other nodes:

```python
@NodeRegistry.register("cached_search", category="retrieval")
def cached_search_node(state: RetrievableState) -> dict:
    """Vector search with caching."""
    cache_key = f"search:{state.query}"

    if cache_key in cache:
        return {"results": cache[cache_key]}

    # Delegate to base search node
    results = vector_search_node(state)
    cache[cache_key] = results["results"]

    return results
```

### Pattern 3: Traced Nodes

All nodes should support tracing:

```python
from langgraph_toolbox.core.tracing import trace_node

@NodeRegistry.register("my_node", category="general")
def my_node(state: MyState) -> dict:
    with trace_node("my_node", state):
        # Implementation
        result = do_work(state)
        return {"result": result}
```

---

## 🧪 Testing Guidelines

### Unit Test Template

```python
import pytest
from unittest.mock import Mock, patch

def test_node_happy_path():
    """Test node with valid input."""
    state = MockState(field="value")
    result = my_node(state)

    assert "expected_key" in result
    assert result["expected_key"] == "expected_value"

def test_node_error_handling():
    """Test node handles errors gracefully."""
    state = MockState(field=None)

    with pytest.raises(ValueError):
        my_node(state)

def test_node_calls_service():
    """Test node delegates to service."""
    with patch('langgraph_toolbox.lib.services.my_service.MyService') as mock:
        state = MockState(field="value")
        my_node(state)

        mock.return_value.method.assert_called_once()
```

---

## 📚 Examples

### Example 1: Retrieval Node

```python
# lib/nodes/retrieval.py
from typing import Protocol
from langgraph_toolbox.core.registry import NodeRegistry
from langgraph_toolbox.lib.services.vectorstore import VectorStoreService

@runtime_checkable
class SearchableState(Protocol):
    query: str

@NodeRegistry.register("semantic_search", category="retrieval")
def semantic_search_node(
    state: SearchableState,
    top_k: int = 10,
    similarity_threshold: float = 0.7
) -> dict:
    """
    Perform semantic vector search.

    Args:
        state: State with query field
        top_k: Max results to return
        similarity_threshold: Minimum similarity score

    Returns:
        dict with 'results' and 'result_count'
    """
    service = VectorStoreService()
    results = service.search(
        query=state.query,
        top_k=top_k,
        threshold=similarity_threshold
    )

    return {
        "results": results,
        "result_count": len(results)
    }
```

### Example 2: Routing Node

```python
# lib/nodes/routing.py
from typing import Protocol, Literal

@runtime_checkable
class RoutableState(Protocol):
    result_count: int

@NodeRegistry.register("route_by_result_count", category="routing")
def route_by_result_count(state: RoutableState) -> Literal["many", "few", "none"]:
    """
    Route based on number of results.

    Returns:
        - "many": > 10 results
        - "few": 1-10 results
        - "none": 0 results
    """
    if state.result_count == 0:
        return "none"
    elif state.result_count <= 10:
        return "few"
    else:
        return "many"
```

---

## 🔗 See Also

- [Design Philosophy](../../../../docs/architecture/design-philosophy.md)
- [Lib Services](../services/README.md) - Service adapters
- [Core Registry](../../core/README.md) - Node registry system
- [Subgraphs](../../subgraphs/README.md) - Using nodes in workflows
