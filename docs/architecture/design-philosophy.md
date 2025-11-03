# LangGraph-Toolbox Design Philosophy

**Version**: 1.0.0
**Last Updated**: 2025-11-04
**Status**: Draft

This document defines the architectural principles and design philosophy behind `langgraph-toolbox`, a community library for building complex multi-agent LangGraph systems.

---

## 📐 Core Design Principles

### 1. Separation of Concerns

**Principle**: Each layer has a single, well-defined responsibility.

```
agents/     → Orchestration (how workflows are composed)
subgraphs/  → Reusable workflows (domain-specific logic)
lib/        → Atomic capabilities (generic, reusable nodes)
core/       → Foundation (state, registry, tracing)
```

**Rationale**: Clear boundaries enable independent testing, parallel development, and easier onboarding.

### 2. Dependency Direction

**Principle**: Dependencies flow in ONE direction only.

```
agents → subgraphs → lib/nodes → lib/services → core
```

**Rules**:
- ✅ `agents/` can import from `subgraphs/`, `lib/`, `core/`
- ✅ `subgraphs/` can import from `lib/`, `core/`
- ✅ `lib/nodes/` can import from `lib/services/`, `core/`
- ❌ NEVER reverse: `core/` importing from `lib/` is FORBIDDEN
- ❌ NEVER circular: `subgraphs/search/` importing from `agents/` is FORBIDDEN

**Rationale**: Prevents circular dependencies, limits blast radius of changes, enables incremental refactoring.

### 3. Reusability Through Composition

**Principle**: Build complex agents by composing simple, reusable components.

**Levels of Reuse**:
1. **Node Level**: Generic nodes in `lib/nodes/` (e.g., `retrieval.py`, `routing.py`)
2. **Subgraph Level**: Domain workflows in `subgraphs/` (e.g., `search/`, `analysis/`)
3. **Service Level**: External integrations in `lib/services/` (e.g., `vectorstore.py`)

**Example**:
```python
# lib/nodes/retrieval.py - Reusable across all agents
@NodeRegistry.register("vector_search")
def vector_search_node(state: SearchState) -> dict:
    results = search_service.query(state["query"])
    return {"results": results}

# subgraphs/search/builder.py - Reusable workflow
def build_search_graph():
    builder = StateGraph(SearchState)
    builder.add_node("search", NodeRegistry.get("vector_search"))
    builder.add_node("rerank", NodeRegistry.get("rerank"))
    return builder.compile()

# agents/prebuilt/research_agent/agent.py - Specific composition
def build_research_agent():
    builder = StateGraph(ResearchState)
    builder.add_node("search", build_search_graph())  # Reuse subgraph
    builder.add_node("analyze", build_analysis_graph())  # Reuse subgraph
    return builder.compile()
```

### 4. Explicit Over Implicit

**Principle**: Make behavior visible and predictable.

**Applications**:
- **State schemas**: Use typed models (Pydantic/msgspec), not plain dicts
- **Node registration**: Explicit registry, not magic discovery
- **Data flow**: State reducers with clear merge logic
- **Tracing**: Explicit observability hooks

**Example**:
```python
# ❌ BAD: Implicit, hard to debug
def my_node(state):
    state["result"] = do_something()
    return state

# ✅ GOOD: Explicit return type, clear data flow
def my_node(state: MyState) -> dict:
    """Process query and return results."""
    result = do_something(state["query"])
    return {"result": result}  # Clear what's being updated
```

### 5. Testability First

**Principle**: Every component must be independently testable.

**Testing Strategy**:
- **Unit Tests**: Each node in isolation (mock state, mock services)
- **Integration Tests**: Each subgraph end-to-end
- **Contract Tests**: State schema compatibility across versions
- **System Tests**: Full agent workflows

**Example**:
```python
# tests/lib/nodes/test_retrieval.py - Unit test
def test_vector_search_node():
    state = {"query": "test query"}
    result = vector_search_node(state)
    assert "results" in result
    assert len(result["results"]) > 0

# tests/subgraphs/search/test_builder.py - Integration test
def test_search_graph_flow():
    graph = build_search_graph()
    result = graph.invoke({"query": "test"})
    assert result["results"] is not None
    assert result["reranked"] is True

# tests/contract/test_state_compatibility.py - Contract test
def test_search_state_v2_compatible_with_v1():
    v1_state = SearchStateV1(query="test")
    v2_state = SearchStateV2(**v1_state.dict())
    assert v2_state.query == v1_state.query
```

### 6. Observability by Design

**Principle**: Complex multi-agent systems are impossible to debug without observability.

**Requirements**:
- Every node must be traceable (name, inputs, outputs, duration)
- State transitions must be logged
- Errors must include context (which node, what state)
- Performance metrics must be collectible

**Implementation**:
```python
# core/tracing.py
@contextmanager
def trace_node(node_name: str, state: dict):
    span = start_trace(node_name, state)
    start_time = time.time()
    try:
        yield span
        span.log_success(duration=time.time() - start_time)
    except Exception as e:
        span.log_error(e, state=state)
        raise

# Usage in every node
def my_node(state: State) -> dict:
    with trace_node("my_node", state):
        # Implementation
        return {"result": result}
```

---

## 🏗️ Architecture Overview

### Directory Structure

```
langgraph_toolbox/
├── agents/prebuilt/           # Agent orchestration layer
│   ├── research_agent/
│   │   ├── agent.py           # Main graph assembly
│   │   ├── config.py          # Agent-specific configuration
│   │   └── tests/
│   └── code_reviewer/
│       └── ...
│
├── subgraphs/                 # Reusable workflow layer
│   ├── search/
│   │   ├── builder.py         # Graph builder
│   │   ├── state.py           # SearchState schema
│   │   ├── nodes.py           # Search-specific nodes
│   │   └── tests/
│   ├── analysis/
│   │   └── ...
│   └── __init__.py
│
├── lib/                       # Shared capabilities layer
│   ├── nodes/                 # Generic, reusable nodes
│   │   ├── retrieval.py       # Vector search nodes
│   │   ├── routing.py         # Conditional routing nodes
│   │   ├── llm_nodes.py       # LLM interaction nodes
│   │   └── tests/
│   └── services/              # External service adapters
│       ├── vectorstore.py     # Vectorstore abstraction
│       ├── llm_client.py      # LLM client abstraction
│       └── tests/
│
├── core/                      # Foundation layer
│   ├── state_base.py          # Base state classes
│   ├── registry.py            # Node factory registry
│   ├── patterns.py            # State reducers, common patterns
│   ├── tracing.py             # Observability hooks
│   └── tests/
│
├── configs/                   # Configuration layer (optional)
│   ├── research_agent.yaml
│   └── templates/
│
└── tests/
    ├── integration/           # Cross-component tests
    ├── contract/              # Schema compatibility tests
    └── fixtures/              # Shared test data
```

### Layer Responsibilities

#### `agents/prebuilt/` - Orchestration Layer

**Purpose**: Compose subgraphs and nodes into complete, user-facing agents.

**Responsibilities**:
- Define agent-level state (root state)
- Wire subgraphs together
- Handle agent-specific configuration
- Provide three execution modes (import, Studio, CLI)

**Does NOT**:
- Implement business logic (delegate to subgraphs/nodes)
- Directly interact with external services (use lib/services)

**Example**:
```python
# agents/prebuilt/research_agent/agent.py
class ResearchAgent:
    def __init__(self, model: str = "gpt-4o"):
        self.model = ChatOpenAI(model=model)
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        builder = StateGraph(ResearchState)

        # Compose reusable subgraphs
        builder.add_node("search", build_search_graph())
        builder.add_node("analyze", build_analysis_graph())
        builder.add_node("summarize", NodeRegistry.get("summarize"))

        # Define agent-specific routing
        builder.add_edge(START, "search")
        builder.add_conditional_edges("search", route_search_results)
        builder.add_edge("analyze", "summarize")
        builder.add_edge("summarize", END)

        return builder.compile()
```

#### `subgraphs/` - Reusable Workflow Layer

**Purpose**: Encapsulate domain-specific workflows that can be reused across agents.

**Responsibilities**:
- Define subgraph-specific state schemas
- Implement domain logic (search, analysis, etc.)
- Compose lib/nodes into workflows
- Provide builder functions for graph assembly

**Does NOT**:
- Know about specific agents (agent-agnostic)
- Directly access config (accept parameters)

**Characteristics**:
- **Domain cohesion**: Related state/nodes/builder live together
- **Self-contained**: Can be tested independently
- **Composable**: Can be nested in other graphs

**Example**:
```python
# subgraphs/search/state.py
class SearchState(BaseState):
    query: str
    results: list[dict]
    reranked: bool = False

# subgraphs/search/nodes.py
def search_node(state: SearchState) -> dict:
    results = search_service.query(state["query"])
    return {"results": results}

def rerank_node(state: SearchState) -> dict:
    reranked = rerank_service.rerank(state["results"], state["query"])
    return {"results": reranked, "reranked": True}

# subgraphs/search/builder.py
def build_search_graph() -> CompiledGraph:
    builder = StateGraph(SearchState)
    builder.add_node("search", search_node)
    builder.add_node("rerank", rerank_node)
    builder.add_edge(START, "search")
    builder.add_edge("search", "rerank")
    builder.add_edge("rerank", END)
    return builder.compile()
```

#### `lib/` - Shared Capabilities Layer

**Purpose**: Provide generic, reusable building blocks.

**Responsibilities**:
- Implement atomic, single-purpose nodes
- Abstract external service integrations
- Provide common utilities

**Does NOT**:
- Know about domains (search, analysis, etc.)
- Make assumptions about state schemas (use generics/protocols)

**Characteristics**:
- **Generic**: Works with any state schema
- **Stateless**: No internal state, pure functions
- **Testable**: Easy to mock dependencies

**Example**:
```python
# lib/nodes/retrieval.py
from typing import Protocol

class RetrievableState(Protocol):
    """Protocol for states that support retrieval."""
    query: str

@NodeRegistry.register("vector_search")
def vector_search_node(state: RetrievableState) -> dict:
    """Generic vector search node."""
    results = vectorstore_service.search(state.query, top_k=10)
    return {"results": results}

# lib/services/vectorstore.py
class VectorStoreService:
    """Abstract vectorstore operations."""
    def __init__(self, provider: str = "pinecone"):
        self.provider = provider
        self._client = self._init_client()

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        # Implementation
        pass
```

#### `core/` - Foundation Layer

**Purpose**: Provide foundational infrastructure for the entire library.

**Responsibilities**:
- Define base state classes
- Implement node registry
- Provide state manipulation patterns
- Handle observability (tracing, logging)

**Does NOT**:
- Implement business logic
- Know about specific domains/agents

**Example**:
```python
# core/state_base.py
from pydantic import BaseModel

class BaseState(BaseModel):
    """Base state all other states inherit from."""
    messages: list[dict] = []
    metadata: dict = {}

# core/registry.py
class NodeRegistry:
    """Central registry for all nodes."""
    _nodes: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func):
            cls._nodes[name] = func
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Callable:
        if name not in cls._nodes:
            raise KeyError(f"Node '{name}' not registered")
        return cls._nodes[name]

# core/patterns.py
def merge_subgraph_state(parent: dict, child: dict, mapping: dict) -> dict:
    """Merge child subgraph state into parent."""
    return {
        **parent,
        **{parent_key: child[child_key] for parent_key, child_key in mapping.items()}
    }
```

---

## 🔄 Key Patterns

### Pattern 1: State Composition

**Problem**: Multiple states need common fields (messages, metadata).

**Solution**: Use inheritance from BaseState.

```python
# core/state_base.py
class BaseState(BaseModel):
    messages: list[dict] = []
    metadata: dict = {}

# subgraphs/search/state.py
class SearchState(BaseState):
    query: str
    results: list[dict] = []

# subgraphs/analysis/state.py
class AnalysisState(BaseState):
    search_results: list[dict]
    insights: list[str] = []
```

**Benefits**:
- Type safety
- DRY (Don't Repeat Yourself)
- IDE autocomplete

### Pattern 2: State Reducers

**Problem**: Need to merge subgraph results into parent state.

**Solution**: Explicit merge functions.

```python
# core/patterns.py
def merge_search_results(parent: ResearchState, child: SearchState) -> dict:
    """Merge search subgraph results into research state."""
    return {
        "search_results": child.results,
        "metadata": {
            **parent.metadata,
            "search_completed": True,
            "result_count": len(child.results)
        }
    }

# Usage in agent
def research_node(state: ResearchState) -> dict:
    # Run search subgraph
    search_result = search_graph.invoke({"query": state.query})

    # Explicitly merge
    merged = merge_search_results(state, search_result)
    return merged
```

**Benefits**:
- Clear data flow
- Easy to debug
- Testable in isolation

### Pattern 3: Node Registry

**Problem**: Need consistent way to discover and use nodes.

**Solution**: Central registry with decorator-based registration.

```python
# core/registry.py
class NodeRegistry:
    _nodes: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, category: str = "general"):
        def decorator(func):
            cls._nodes[name] = {
                "func": func,
                "category": category,
                "metadata": getattr(func, "__doc__", "")
            }
            return func
        return decorator

# lib/nodes/retrieval.py
@NodeRegistry.register("vector_search", category="retrieval")
def vector_search_node(state: SearchState) -> dict:
    """Perform vector similarity search."""
    # Implementation
    pass

# Usage
search_node = NodeRegistry.get("vector_search")["func"]
builder.add_node("search", search_node)
```

**Benefits**:
- Discoverable (list all nodes)
- Consistent interface
- Metadata for documentation

### Pattern 4: Observability Hooks

**Problem**: Debugging complex multi-agent systems is hard.

**Solution**: Tracing context manager for every node.

```python
# core/tracing.py
from contextlib import contextmanager
import time
from typing import Optional

@contextmanager
def trace_node(node_name: str, state: dict, tracer: Optional[Tracer] = None):
    """Trace node execution with LangSmith or custom tracer."""
    tracer = tracer or get_default_tracer()
    span = tracer.start_span(node_name)
    span.log_input(state)

    start_time = time.time()
    error = None
    result = None

    try:
        yield span
    except Exception as e:
        error = e
        span.log_error(e)
        raise
    finally:
        duration = time.time() - start_time
        span.log_metrics({"duration_ms": duration * 1000})
        span.end()

# Usage in every node
def my_node(state: State) -> dict:
    with trace_node("my_node", state):
        result = do_work(state)
        return {"result": result}
```

**Benefits**:
- Uniform tracing across all nodes
- Easy to integrate with LangSmith, OpenTelemetry, etc.
- Performance metrics included

---

## 🧪 Testing Strategy

### Test Pyramid

```
        /\
       /  \      E2E Tests (Few)
      /____\     - Full agent workflows
     /      \    - Real services (optional)
    /________\   Integration Tests (Some)
   /          \  - Subgraph workflows
  /____________\ - Mock external services
 /              \ Unit Tests (Many)
/______________\ - Individual nodes
                 - Pure functions
                 - Mock everything
```

### Test Organization

```
tests/
├── unit/
│   ├── test_nodes.py          # lib/nodes/ tests
│   ├── test_services.py       # lib/services/ tests
│   └── test_patterns.py       # core/patterns.py tests
│
├── integration/
│   ├── test_search_subgraph.py    # subgraphs/search/ tests
│   └── test_analysis_subgraph.py  # subgraphs/analysis/ tests
│
├── contract/
│   ├── test_state_compatibility.py  # Version compatibility
│   └── test_node_contracts.py       # Node interface tests
│
├── e2e/
│   ├── test_research_agent.py   # Full agent tests
│   └── test_code_reviewer.py    # Full agent tests
│
└── fixtures/
    ├── states.py                # Mock states
    ├── responses.py             # Mock LLM responses
    └── data.py                  # Test data
```

### Testing Guidelines

**Unit Tests**:
- Test ONE function/node
- Mock ALL external dependencies
- Fast (<10ms per test)
- High coverage (>90%)

**Integration Tests**:
- Test ONE subgraph end-to-end
- Mock external services only
- Medium speed (<100ms per test)
- Focus on data flow

**Contract Tests**:
- Test state schema compatibility
- Test node interface contracts
- Ensure backward compatibility

**E2E Tests**:
- Test FULL agent workflows
- Use real or mock services
- Slow (<5s per test)
- Focus on user scenarios

---

## 📊 Decision Log

### Why Strict Layered Architecture?

**Decision**: Use agents → subgraphs → lib → core layering.

**Alternatives Considered**:
1. Flat structure (all code in one folder)
2. Domain-driven (search/, analysis/ at top level)
3. Hybrid (current choice)

**Rationale**:
- **For**: Clear dependency direction, testability, reusability
- **Against**: More boilerplate, learning curve
- **Winner**: Long-term maintainability outweighs initial complexity

**Trade-offs**:
- 📈 Gains: Reusability (+40%), testability (+50%), onboarding (-30% time)
- 📉 Costs: Boilerplate (+20%), initial setup time (+2 hours)

### Why Typed State Models (Pydantic)?

**Decision**: Use Pydantic for all state schemas.

**Alternatives Considered**:
1. Plain TypedDict
2. dataclasses
3. Pydantic (chosen)
4. msgspec

**Rationale**:
- **For**: Runtime validation, serialization, IDE support, ecosystem
- **Against**: Performance overhead, dependency weight
- **Winner**: Developer experience and safety > performance for most use cases

**Trade-offs**:
- 📈 Gains: Type safety, validation, documentation
- 📉 Costs: ~10-15% performance overhead, heavier dependency

### Why Node Registry Over Dynamic Discovery?

**Decision**: Explicit registry with decorator-based registration.

**Alternatives Considered**:
1. Auto-discovery via entrypoints
2. Explicit registry (chosen)
3. Config-based registration

**Rationale**:
- **For**: Explicit, predictable, IDE-friendly
- **Against**: Manual registration required
- **Winner**: Explicitness and control > magic discovery

**Trade-offs**:
- 📈 Gains: Predictability, static analysis, no surprises
- 📉 Costs: Must remember to register, more boilerplate

---

## 🚀 Extension Points

### Adding a New Agent

```python
# 1. Create agent folder
agents/prebuilt/my_agent/
├── agent.py
├── config.py
└── tests/

# 2. Define state (inherit from BaseState)
from core.state_base import BaseState

class MyAgentState(BaseState):
    # Add agent-specific fields
    pass

# 3. Compose from subgraphs/nodes
def build_my_agent():
    builder = StateGraph(MyAgentState)
    builder.add_node("step1", build_existing_subgraph())
    builder.add_node("step2", NodeRegistry.get("existing_node"))
    return builder.compile()

# 4. Register in langgraph.json
{
  "graphs": {
    "my_agent": "./src/langgraph_toolbox/agents/prebuilt/my_agent/agent.py:graph"
  }
}
```

### Adding a New Subgraph

```python
# 1. Create subgraph folder
subgraphs/my_workflow/
├── builder.py
├── state.py
├── nodes.py
└── tests/

# 2. Define state
class MyWorkflowState(BaseState):
    # Add workflow-specific fields
    pass

# 3. Implement nodes (or reuse from lib/nodes/)
def my_node(state: MyWorkflowState) -> dict:
    # Implementation
    pass

# 4. Build graph
def build_my_workflow() -> CompiledGraph:
    builder = StateGraph(MyWorkflowState)
    builder.add_node("node1", my_node)
    return builder.compile()

# 5. Use in agents
builder.add_node("my_step", build_my_workflow())
```

### Adding a New Generic Node

```python
# 1. Implement in lib/nodes/
# lib/nodes/my_capability.py

from typing import Protocol

class MyCapabilityState(Protocol):
    """Protocol for states that support this capability."""
    required_field: str

@NodeRegistry.register("my_capability", category="processing")
def my_capability_node(state: MyCapabilityState) -> dict:
    """Generic reusable node."""
    result = process(state.required_field)
    return {"result": result}

# 2. Use anywhere
builder.add_node("process", NodeRegistry.get("my_capability"))
```

---

## 📚 Further Reading

- [Prebuilt Agent Standard](../standards/prebuilt-agent-standard.md)
- [How to Create an Agent](../standards/HOW-TO-CREATE-AGENT.md)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Testing Guidelines](../../docs/python/testing_guidelines.md)

---

**Contributors**: AI Collaborative Solver (Claude + Codex)
**Review Status**: Draft - Awaiting team review
**Next Review**: After first 3 agents implemented
