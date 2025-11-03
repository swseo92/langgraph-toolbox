# Subgraphs

**Layer**: Reusable Workflows
**Purpose**: Domain-specific workflows that can be composed into agents

---

## 📋 Overview

Subgraphs are reusable, domain-specific workflows that encapsulate a complete process (e.g., search, analysis, code review). They can be used by multiple agents and nested within other graphs.

---

## 🎯 Responsibilities

**This layer SHOULD**:
- ✅ Define subgraph-specific state schemas
- ✅ Implement domain logic (search workflow, analysis workflow, etc.)
- ✅ Compose nodes from `lib/nodes/` into workflows
- ✅ Provide builder functions that return compiled graphs
- ✅ Be independently testable

**This layer SHOULD NOT**:
- ❌ Know about specific agents (must be agent-agnostic)
- ❌ Access configuration directly (accept parameters instead)
- ❌ Implement generic utilities (put in `lib/` or `core/`)

---

## 📁 Structure

Each subgraph follows this structure:

```
subgraphs/
└── my_workflow/
    ├── __init__.py           # Public exports
    ├── builder.py            # Graph builder function
    ├── state.py              # Workflow state schema
    ├── nodes.py              # Workflow-specific nodes
    ├── README.md             # Workflow documentation (optional)
    └── tests/
        └── test_builder.py   # Integration tests
```

---

## 🚀 Creating a New Subgraph

### Step 1: Create Directory

```bash
mkdir -p src/langgraph_toolbox/subgraphs/my_workflow
cd src/langgraph_toolbox/subgraphs/my_workflow
touch __init__.py builder.py state.py nodes.py
mkdir tests
```

### Step 2: Define State Schema

```python
# subgraphs/my_workflow/state.py
from core.state_base import BaseState

class MyWorkflowState(BaseState):
    """State schema for MyWorkflow subgraph."""
    # Input fields
    input_data: str

    # Output fields
    result: dict
    processed: bool = False
```

### Step 3: Implement Nodes

```python
# subgraphs/my_workflow/nodes.py
from langgraph_toolbox.subgraphs.my_workflow.state import MyWorkflowState
from langgraph_toolbox.lib.services.my_service import MyService

def process_node(state: MyWorkflowState) -> dict:
    """Process the input data."""
    service = MyService()
    result = service.process(state.input_data)
    return {"result": result, "processed": True}

def validate_node(state: MyWorkflowState) -> dict:
    """Validate the result."""
    is_valid = len(state.result) > 0
    return {"metadata": {"valid": is_valid}}
```

**Best Practices**:
- Reuse nodes from `lib/nodes/` when possible
- Only create workflow-specific nodes here
- Keep nodes focused (single responsibility)
- Include docstrings

### Step 4: Build Graph

```python
# subgraphs/my_workflow/builder.py
from langgraph.graph import StateGraph, START, END
from langgraph_toolbox.subgraphs.my_workflow.state import MyWorkflowState
from langgraph_toolbox.subgraphs.my_workflow.nodes import process_node, validate_node
from langgraph_toolbox.core.registry import NodeRegistry

def build_my_workflow(config: dict = None) -> CompiledGraph:
    """
    Build MyWorkflow subgraph.

    Args:
        config: Optional configuration (e.g., model, parameters)

    Returns:
        Compiled LangGraph ready to use as a node
    """
    config = config or {}

    builder = StateGraph(MyWorkflowState)

    # Add workflow-specific nodes
    builder.add_node("process", process_node)
    builder.add_node("validate", validate_node)

    # Or reuse generic nodes
    builder.add_node("enrich", NodeRegistry.get("enrich_metadata"))

    # Define workflow
    builder.add_edge(START, "process")
    builder.add_edge("process", "validate")
    builder.add_edge("validate", "enrich")
    builder.add_edge("enrich", END)

    return builder.compile()
```

**Key Points**:
- Accept optional config parameter
- Return compiled graph (not builder)
- Use clear node names
- Document parameters

### Step 5: Export

```python
# subgraphs/my_workflow/__init__.py
"""MyWorkflow - Description of what this workflow does."""

from langgraph_toolbox.subgraphs.my_workflow.builder import build_my_workflow
from langgraph_toolbox.subgraphs.my_workflow.state import MyWorkflowState

__all__ = ["build_my_workflow", "MyWorkflowState"]
```

### Step 6: Write Tests

```python
# subgraphs/my_workflow/tests/test_builder.py
import pytest
from langgraph_toolbox.subgraphs.my_workflow.builder import build_my_workflow
from langgraph_toolbox.subgraphs.my_workflow.state import MyWorkflowState

def test_build_my_workflow():
    """Test graph can be built."""
    graph = build_my_workflow()
    assert graph is not None

def test_my_workflow_execution():
    """Test workflow executes end-to-end."""
    graph = build_my_workflow()

    input_state = {
        "input_data": "test data",
        "messages": []
    }

    result = graph.invoke(input_state)

    assert result["processed"] is True
    assert "result" in result
    assert result["metadata"]["valid"] is True

def test_my_workflow_with_config():
    """Test workflow accepts configuration."""
    graph = build_my_workflow(config={"param": "value"})
    result = graph.invoke({"input_data": "test"})
    assert result is not None
```

---

## 🧩 Using Subgraphs in Agents

### As a Node

```python
# agents/prebuilt/my_agent/agent.py
from langgraph_toolbox.subgraphs.my_workflow.builder import build_my_workflow

class MyAgent:
    def _create_graph(self):
        builder = StateGraph(MyAgentState)

        # Use subgraph as a node
        builder.add_node("workflow", build_my_workflow())

        builder.add_edge(START, "workflow")
        builder.add_edge("workflow", END)

        return builder.compile()
```

### With Configuration

```python
# Pass config to subgraph
workflow_config = {"model": "gpt-4o", "top_k": 5}
builder.add_node("workflow", build_my_workflow(config=workflow_config))
```

### Nested Subgraphs

```python
# Subgraphs can use other subgraphs
from langgraph_toolbox.subgraphs.search.builder import build_search_graph
from langgraph_toolbox.subgraphs.analysis.builder import build_analysis_graph

def build_research_workflow():
    builder = StateGraph(ResearchState)

    # Nest subgraphs
    builder.add_node("search", build_search_graph())
    builder.add_node("analyze", build_analysis_graph())

    builder.add_edge(START, "search")
    builder.add_edge("search", "analyze")
    builder.add_edge("analyze", END)

    return builder.compile()
```

---

## 📊 Design Guidelines

### Domain Cohesion

Keep related code together in one subgraph folder:
- ✅ `search/` contains all search-related state, nodes, builder
- ✅ `analysis/` contains all analysis-related components
- ❌ Don't split across multiple folders

### State Management

**Pattern 1: Inherit from BaseState**
```python
class MyWorkflowState(BaseState):
    # BaseState provides: messages, metadata
    my_field: str
```

**Pattern 2: Compose States**
```python
class SearchState(BaseState):
    query: str
    results: list[dict]

class AnalysisState(BaseState):
    search_results: list[dict]  # References SearchState.results
    insights: list[str]
```

### Reusability

**Good** (Reusable):
```python
def build_search_graph(provider: str = "google"):
    """Generic search workflow, provider-agnostic."""
    # Implementation
```

**Bad** (Agent-specific):
```python
def build_research_agent_search_graph():
    """Search workflow tied to research agent."""
    # DON'T DO THIS - belongs in agents/
```

---

## 🧪 Testing Strategy

### Integration Tests (Required)

Test the ENTIRE subgraph workflow:

```python
def test_full_workflow():
    graph = build_my_workflow()
    result = graph.invoke({"input": "test"})
    assert result["processed"] is True
```

### Unit Tests (For Complex Nodes)

Test individual nodes in isolation:

```python
def test_process_node():
    state = MyWorkflowState(input_data="test")
    result = process_node(state)
    assert "result" in result
```

### Contract Tests (For Public APIs)

Ensure state schema compatibility:

```python
def test_state_has_required_fields():
    state = MyWorkflowState(input_data="test")
    assert hasattr(state, "result")
    assert hasattr(state, "processed")
```

---

## 📚 Examples

### Example 1: Search Subgraph

```python
# subgraphs/search/builder.py
def build_search_graph(provider: str = "google", top_k: int = 10):
    builder = StateGraph(SearchState)

    # Reuse generic nodes
    builder.add_node("query", NodeRegistry.get("vector_search"))
    builder.add_node("rerank", NodeRegistry.get("rerank"))

    # Add search-specific logic
    builder.add_node("filter", filter_results_node)

    builder.add_edge(START, "query")
    builder.add_edge("query", "rerank")
    builder.add_edge("rerank", "filter")
    builder.add_edge("filter", END)

    return builder.compile()
```

### Example 2: Analysis Subgraph with Conditional Logic

```python
# subgraphs/analysis/builder.py
def build_analysis_graph(depth: str = "medium"):
    builder = StateGraph(AnalysisState)

    builder.add_node("quick_analysis", quick_analysis_node)
    builder.add_node("deep_analysis", deep_analysis_node)
    builder.add_node("summarize", NodeRegistry.get("summarize"))

    builder.add_edge(START, "quick_analysis")
    builder.add_conditional_edges(
        "quick_analysis",
        route_by_complexity,
        {"deep": "deep_analysis", "done": "summarize"}
    )
    builder.add_edge("deep_analysis", "summarize")
    builder.add_edge("summarize", END)

    return builder.compile()
```

---

## 🔗 See Also

- [Design Philosophy](../../../docs/architecture/design-philosophy.md)
- [Lib Nodes](../lib/nodes/README.md) - Generic reusable nodes
- [Core Patterns](../core/README.md) - State management patterns
