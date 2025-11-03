# Prebuilt Agents

**Layer**: Orchestration
**Purpose**: Complete, user-facing agents composed from reusable subgraphs and nodes

---

## 📋 Overview

This directory contains production-ready LangGraph agents that users can import and use directly. Each agent is a complete workflow assembled from reusable components in `subgraphs/` and `lib/`.

---

## 🎯 Responsibilities

**This layer SHOULD**:
- ✅ Define agent-level state (root state)
- ✅ Compose subgraphs and nodes into workflows
- ✅ Handle agent-specific configuration
- ✅ Provide three execution modes:
  - Library import (`from langgraph_toolbox.agents import MyAgent`)
  - LangGraph Studio (`langgraph dev`)
  - CLI execution (`python -m langgraph_toolbox.agents.prebuilt.my_agent.agent`)

**This layer SHOULD NOT**:
- ❌ Implement business logic (delegate to subgraphs/nodes)
- ❌ Directly interact with external services (use `lib/services/`)
- ❌ Duplicate code across agents (extract to `subgraphs/` or `lib/`)

---

## 📁 Structure

Each agent follows this structure:

```
prebuilt/
└── my_agent/
    ├── __init__.py           # Public exports
    ├── agent.py              # Main agent implementation
    ├── config.py             # Agent configuration (optional)
    ├── README.md             # Agent documentation
    └── tests/
        └── test_agent.py     # Agent-specific tests
```

---

## 🚀 Creating a New Agent

### Step 1: Use the Template

```bash
cp -r templates/prebuilt_agent_template src/langgraph_toolbox/agents/prebuilt/my_agent
```

### Step 2: Define Agent State

```python
# agents/prebuilt/my_agent/agent.py
from core.state_base import BaseState

class MyAgentState(BaseState):
    """Agent-level state schema."""
    # Add agent-specific fields
    query: str
    final_result: str
```

### Step 3: Compose from Subgraphs

```python
from subgraphs.search.builder import build_search_graph
from subgraphs.analysis.builder import build_analysis_graph
from core.registry import NodeRegistry

class MyAgent:
    def _create_graph(self) -> StateGraph:
        builder = StateGraph(MyAgentState)

        # Reuse existing subgraphs
        builder.add_node("search", build_search_graph())
        builder.add_node("analyze", build_analysis_graph())

        # Use registered generic nodes
        builder.add_node("summarize", NodeRegistry.get("summarize"))

        # Define workflow
        builder.add_edge(START, "search")
        builder.add_edge("search", "analyze")
        builder.add_edge("analyze", "summarize")
        builder.add_edge("summarize", END)

        return builder.compile()
```

### Step 4: Register in langgraph.json

```json
{
  "graphs": {
    "my_agent": "./src/langgraph_toolbox/agents/prebuilt/my_agent/agent.py:graph"
  }
}
```

### Step 5: Export

```python
# agents/prebuilt/__init__.py
from langgraph_toolbox.agents.prebuilt.my_agent import MyAgent

__all__ = ["MyAgent"]
```

---

## 📝 Agent Checklist

Before committing a new agent:

- [ ] **Structure**: Follows standard template
- [ ] **State**: Typed state schema (Pydantic/TypedDict)
- [ ] **Composition**: Reuses subgraphs/nodes (minimal custom logic)
- [ ] **Three Modes**: Works as import, Studio, and CLI
- [ ] **Tests**: Unit + integration tests
- [ ] **Documentation**: README with examples
- [ ] **Registration**: Added to `langgraph.json` and `__init__.py`

---

## 🧪 Testing

```bash
# Test specific agent
pytest tests/agents/prebuilt/test_my_agent.py

# Test all agents
pytest tests/agents/prebuilt/

# Test with LangGraph Studio
langgraph dev
```

---

## 📚 Examples

### Example 1: Simple Agent (2 subgraphs)

```python
class SimpleAgent:
    def _create_graph(self):
        builder = StateGraph(SimpleState)
        builder.add_node("step1", build_search_graph())
        builder.add_node("step2", build_analysis_graph())
        builder.add_edge(START, "step1")
        builder.add_edge("step1", "step2")
        builder.add_edge("step2", END)
        return builder.compile()
```

### Example 2: Complex Agent (conditional routing)

```python
class ComplexAgent:
    def _create_graph(self):
        builder = StateGraph(ComplexState)

        builder.add_node("search", build_search_graph())
        builder.add_node("deep_analysis", build_deep_analysis_graph())
        builder.add_node("quick_summary", NodeRegistry.get("quick_summary"))

        builder.add_edge(START, "search")
        builder.add_conditional_edges(
            "search",
            self._route_by_result_count,
            {
                "deep": "deep_analysis",
                "quick": "quick_summary"
            }
        )
        builder.add_edge("deep_analysis", END)
        builder.add_edge("quick_summary", END)

        return builder.compile()

    def _route_by_result_count(self, state: ComplexState) -> str:
        return "deep" if len(state.search_results) > 10 else "quick"
```

---

## 🔗 See Also

- [Design Philosophy](../../../docs/architecture/design-philosophy.md)
- [Prebuilt Agent Standard](../../../docs/standards/prebuilt-agent-standard.md)
- [How to Create an Agent](../../../docs/standards/HOW-TO-CREATE-AGENT.md)
