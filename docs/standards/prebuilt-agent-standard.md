# Prebuilt Agent Standard Structure

**Version**: 1.0.0
**Last Updated**: 2025-11-04

This document defines the standard structure for all prebuilt agents in `langgraph-toolbox`.

---

## 🎯 Design Goals

All prebuilt agents must support **three modes of operation**:

1. **LangGraph Studio**: Visual debugging with `langgraph dev`
2. **Library Import**: `from langgraph_toolbox.agents import AgentName`
3. **CLI Execution**: `python -m langgraph_toolbox.agents.prebuilt.agent_name`

---

## 📁 Directory Structure

```
src/langgraph_toolbox/agents/prebuilt/
└── {agent_name}/
    ├── __init__.py           # Public exports
    ├── agent.py              # Main agent implementation
    ├── state.py              # State definitions (optional)
    ├── tools.py              # Custom tools (optional)
    ├── prompts.py            # Prompt templates (optional)
    ├── config.py             # Configuration (optional)
    └── README.md             # Agent documentation
```

### File Naming Convention

- **Agent folder**: `snake_case` (e.g., `research_agent`, `code_review`)
- **Files**: Always `lowercase_with_underscores`
- **Classes**: `PascalCase` (e.g., `ResearchAgent`)
- **Functions/methods**: `snake_case`

---

## 📝 File Templates

### 1. `agent.py` - Main Implementation

**Required Structure:**

```python
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
        {other_fields}: Description
    """
    messages: Annotated[list, add_messages]
    # Add other fields as needed


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
        {other_args}: Description

    Examples:
        Basic usage:
            >>> agent = {AgentName}()
            >>> result = agent.invoke({"messages": [...]})

        Custom configuration:
            >>> agent = {AgentName}(model="claude-sonnet-4", {config}={value})
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
        builder.add_node("node1", self._node1_handler)
        builder.add_node("node2", self._node2_handler)

        # Add edges
        builder.add_edge(START, "node1")
        builder.add_edge("node1", "node2")
        builder.add_edge("node2", END)

        return builder.compile()

    def _node1_handler(self, state: {AgentName}State) -> dict:
        """
        Handle node1 logic.

        Args:
            state: Current agent state

        Returns:
            Updated state fields
        """
        # Implementation
        return {"messages": [...]}

    def _node2_handler(self, state: {AgentName}State) -> dict:
        """
        Handle node2 logic.

        Args:
            state: Current agent state

        Returns:
            Updated state fields
        """
        # Implementation
        return {"messages": [...]}

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
        input_data = {
            "messages": [{"role": "user", "content": "Hello"}]
        }

    # Run agent
    agent = {AgentName}()
    result = agent.invoke(input_data)

    # Print result
    print(json.dumps(result, indent=2))
```

---

### 2. `__init__.py` - Public Exports

```python
"""
{AgentName} - {Brief Description}

Usage:
    >>> from langgraph_toolbox.agents import {AgentName}
    >>> agent = {AgentName}()
    >>> result = agent.invoke({...})
"""

from langgraph_toolbox.agents.prebuilt.{agent_name}.agent import (
    {AgentName},
    {AgentName}State,
)

__all__ = ["{AgentName}", "{AgentName}State"]
```

---

### 3. `README.md` - Agent Documentation

```markdown
# {AgentName}

**Category**: {Research / Code / Data / Utility}
**Status**: {Alpha / Beta / Stable}
**Version**: 0.1.0

{Brief description of what this agent does}

---

## Features

- ✅ Feature 1
- ✅ Feature 2
- ✅ Feature 3

---

## Installation

This agent is included in `langgraph-toolbox`:

\`\`\`bash
pip install langgraph-toolbox
# or
uv add langgraph-toolbox
\`\`\`

---

## Usage

### As Library

\`\`\`python
from langgraph_toolbox.agents import {AgentName}

# Basic usage
agent = {AgentName}(model="gpt-4o")
result = agent.invoke({
    "messages": [{"role": "user", "content": "..."}]
})

print(result)
\`\`\`

### With LangGraph Studio

\`\`\`bash
cd langgraph-toolbox
langgraph dev

# Open Studio and select "{agent_name}" from dropdown
\`\`\`

### CLI Execution

\`\`\`bash
python -m langgraph_toolbox.agents.prebuilt.{agent_name}.agent '{"messages": [...]}'
\`\`\`

---

## Configuration

### Environment Variables

\`\`\`bash
# Required
OPENAI_API_KEY=sk-...          # or ANTHROPIC_API_KEY
LANGSMITH_API_KEY=lsv2_...     # For tracing

# Optional
{ENV_VAR_1}=value
{ENV_VAR_2}=value
\`\`\`

### Agent Parameters

- **model** (str): LLM model to use (default: "gpt-4o")
- **{param1}** (type): Description
- **{param2}** (type): Description

---

## State Schema

\`\`\`python
class {AgentName}State(TypedDict):
    messages: Annotated[list, add_messages]  # Required
    {field1}: {type}                          # Description
    {field2}: {type}                          # Description
\`\`\`

---

## Graph Structure

\`\`\`
START
  ↓
[Node 1] → [Node 2] → [Node 3]
  ↓
END
\`\`\`

**Nodes:**
- **{node1}**: Description
- **{node2}**: Description
- **{node3}**: Description

---

## Examples

### Example 1: {Use Case}

\`\`\`python
from langgraph_toolbox.agents import {AgentName}

agent = {AgentName}()
result = agent.invoke({
    "messages": [{"role": "user", "content": "..."}],
    "param": "value"
})

print(result["field"])
\`\`\`

### Example 2: {Use Case}

\`\`\`python
# Code example
\`\`\`

---

## Development

### Testing

\`\`\`bash
pytest tests/agents/test_{agent_name}.py
\`\`\`

### Local Development

\`\`\`bash
# Run in development mode
langgraph dev

# Test with curl
curl -X POST http://localhost:2024/runs/stream \\
  -H "Content-Type: application/json" \\
  -d '{"assistant_id": "{agent_name}", "input": {...}}'
\`\`\`

---

## Limitations

- Limitation 1
- Limitation 2

---

## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3

---

## References

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Related Documentation]
```

---

## 🧪 Testing Standards

### Test File Structure

```
tests/agents/prebuilt/
└── test_{agent_name}.py
```

### Test Template

```python
"""Tests for {AgentName}"""

import pytest
from langgraph_toolbox.agents import {AgentName}


class Test{AgentName}:
    """Test suite for {AgentName}"""

    def test_initialization(self):
        """Test agent initialization"""
        agent = {AgentName}()
        assert agent.model is not None
        assert agent.graph is not None

    def test_invoke_basic(self):
        """Test basic invocation"""
        agent = {AgentName}()
        result = agent.invoke({
            "messages": [{"role": "user", "content": "test"}]
        })
        assert "messages" in result
        assert len(result["messages"]) > 0

    @pytest.mark.asyncio
    async def test_ainvoke(self):
        """Test async invocation"""
        agent = {AgentName}()
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": "test"}]
        })
        assert "messages" in result

    def test_custom_model(self):
        """Test with custom model"""
        agent = {AgentName}(model="gpt-4o-mini")
        assert agent.model.model_name == "gpt-4o-mini"
```

---

## 📋 Checklist for New Agent

Before submitting a new prebuilt agent, ensure:

- [ ] **Structure**
  - [ ] Follows directory structure standard
  - [ ] All required files present (`agent.py`, `__init__.py`, `README.md`)
  - [ ] Proper file naming (snake_case)

- [ ] **Code Quality**
  - [ ] Type hints on all functions
  - [ ] Comprehensive docstrings
  - [ ] State schema documented
  - [ ] Error handling implemented

- [ ] **Three Modes Working**
  - [ ] Library import: `from langgraph_toolbox.agents import AgentName`
  - [ ] LangGraph Studio: Listed in `langgraph.json`, works in Studio
  - [ ] CLI execution: `python -m ...` works

- [ ] **Documentation**
  - [ ] README.md complete with examples
  - [ ] Usage examples for all three modes
  - [ ] Configuration documented
  - [ ] State schema explained

- [ ] **Testing**
  - [ ] Test file created
  - [ ] Basic tests pass
  - [ ] Async tests (if applicable)

- [ ] **Integration**
  - [ ] Added to `langgraph.json`
  - [ ] Exported in `prebuilt/__init__.py`
  - [ ] Exported in `agents/__init__.py`
  - [ ] Added to root `__init__.py`

---

## 🎨 Code Style Guidelines

### Docstrings

- Use Google-style docstrings
- Include `Args`, `Returns`, `Raises` sections
- Provide usage examples

### Type Hints

- All function parameters must have type hints
- Return types must be specified
- Use `TypedDict` for complex state schemas

### Naming

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Imports

```python
# Standard library
import sys
import json
from typing import TypedDict, Annotated

# Third-party
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# Local
from langgraph_toolbox.patterns import with_retry
```

---

## 🔄 Version Control

### Commit Messages

When adding a new agent:
```
feat(agents): Add {AgentName}

- Implement core {AgentName} functionality
- Add comprehensive tests
- Include usage examples in README
- Support all three execution modes
```

When updating an agent:
```
fix(agents/{agent_name}): Fix {issue}

- Detailed description of the fix
```

---

## 📦 Integration Checklist

### Update `langgraph.json`

```json
{
  "graphs": {
    "{agent_name}": "./src/langgraph_toolbox/agents/prebuilt/{agent_name}/agent.py:graph"
  }
}
```

### Update Package Exports

```python
# src/langgraph_toolbox/agents/prebuilt/__init__.py
from langgraph_toolbox.agents.prebuilt.{agent_name} import {AgentName}

__all__ = [..., "{AgentName}"]
```

### Update Root __init__.py

```python
# src/langgraph_toolbox/__init__.py
from langgraph_toolbox.agents import {AgentName}

__all__ = [..., "{AgentName}"]
```

---

## 🚀 Example: Minimal Agent

See `src/langgraph_toolbox/agents/prebuilt/example_minimal/` for a minimal working example following this standard.

---

**Questions or suggestions?** Open an issue or PR!
