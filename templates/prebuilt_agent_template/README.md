# {AgentName}

**Category**: {Research / Code / Data / Utility}
**Status**: Alpha
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

```bash
pip install langgraph-toolbox
# or
uv add langgraph-toolbox
```

---

## Usage

### As Library

```python
from langgraph_toolbox.agents import {AgentName}

# Basic usage
agent = {AgentName}(model="gpt-4o")
result = agent.invoke({
    "messages": [{"role": "user", "content": "..."}]
})

print(result)
```

### With LangGraph Studio

```bash
cd langgraph-toolbox
langgraph dev

# Open Studio and select "{agent_name}" from dropdown
```

### CLI Execution

```bash
python -m langgraph_toolbox.agents.prebuilt.{agent_name}.agent '{"messages": [...]}'
```

---

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...          # or ANTHROPIC_API_KEY
LANGSMITH_API_KEY=lsv2_...     # For tracing
```

### Agent Parameters

- **model** (str): LLM model to use (default: "gpt-4o")

---

## State Schema

```python
class {AgentName}State(TypedDict):
    messages: Annotated[list, add_messages]  # Required
```

---

## Graph Structure

```
START → [Process] → END
```

**Nodes:**
- **process**: Main processing node

---

## Examples

### Example 1: Basic Usage

```python
from langgraph_toolbox.agents import {AgentName}

agent = {AgentName}()
result = agent.invoke({
    "messages": [{"role": "user", "content": "Hello"}]
})

print(result["messages"])
```

---

## Development

### Testing

```bash
pytest tests/agents/test_{agent_name}.py
```

### Local Development

```bash
# Run in development mode
langgraph dev

# Test with curl
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{"assistant_id": "{agent_name}", "input": {"messages": [...]}}'
```

---

## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3

---

## References

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
