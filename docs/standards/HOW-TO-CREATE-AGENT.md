# How to Create a New Prebuilt Agent

**Quick Guide**: Step-by-step instructions for creating a new prebuilt agent in `langgraph-toolbox`.

---

## 📋 Prerequisites

1. Read [prebuilt-agent-standard.md](./prebuilt-agent-standard.md)
2. Have `langgraph-toolbox` cloned locally
3. Understand basic LangGraph concepts

---

## 🚀 Quick Start

### Step 1: Copy Template

```bash
cd langgraph-toolbox/main
cp -r ../../templates/prebuilt_agent_template src/langgraph_toolbox/agents/prebuilt/my_agent
```

### Step 2: Replace Placeholders

In all copied files, replace:
- `{AgentName}` → Your agent class name (PascalCase, e.g., `ResearchAgent`)
- `{agent_name}` → Folder/module name (snake_case, e.g., `research_agent`)
- `{Brief Description}` → One-line description
- `{Detailed description}` → Full description

**Files to update:**
- `agent.py`
- `__init__.py`
- `README.md`

### Step 3: Implement Logic

Edit `agent.py`:

```python
def _process_handler(self, state: MyAgentState) -> dict:
    """Your implementation here"""
    messages = state["messages"]

    # TODO: Add your logic
    response = self.model.invoke(messages)

    return {"messages": [response]}
```

### Step 4: Register in langgraph.json

Add to root `langgraph.json`:

```json
{
  "graphs": {
    "my_agent": "./src/langgraph_toolbox/agents/prebuilt/my_agent/agent.py:graph"
  }
}
```

### Step 5: Export in __init__.py

```python
# src/langgraph_toolbox/agents/prebuilt/__init__.py
from langgraph_toolbox.agents.prebuilt.my_agent import MyAgent

__all__ = [..., "MyAgent"]
```

```python
# src/langgraph_toolbox/agents/__init__.py
from langgraph_toolbox.agents.prebuilt import MyAgent

__all__ = [..., "MyAgent"]
```

### Step 6: Test

```bash
# Test with LangGraph Studio
langgraph dev

# Test with Python
python -c "
from langgraph_toolbox.agents import MyAgent
agent = MyAgent()
result = agent.invoke({'messages': [{'role': 'user', 'content': 'test'}]})
print(result)
"

# Test CLI
python -m langgraph_toolbox.agents.prebuilt.my_agent.agent
```

---

## 📝 Detailed Example

Let's create a **SummarizerAgent** step by step.

### 1. Copy Template

```bash
cp -r templates/prebuilt_agent_template src/langgraph_toolbox/agents/prebuilt/summarizer
```

### 2. Update `agent.py`

```python
"""
SummarizerAgent - Text summarization with customizable length

Can be used both as library import and standalone with langgraph dev.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI


class SummarizerState(TypedDict):
    """State schema for SummarizerAgent."""
    messages: Annotated[list, add_messages]
    text: str  # Text to summarize
    summary: str  # Generated summary
    length: Literal["short", "medium", "long"]  # Summary length


class SummarizerAgent:
    """
    Summarize long texts into concise summaries.

    Features:
        - Multiple summary lengths (short/medium/long)
        - Preserves key points
        - Maintains context

    Args:
        model: LLM model to use (default: "gpt-4o")
        default_length: Default summary length (default: "medium")
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        default_length: Literal["short", "medium", "long"] = "medium",
    ):
        self.model = ChatOpenAI(model=model)
        self.default_length = default_length
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        builder = StateGraph(SummarizerState)
        builder.add_node("summarize", self._summarize_handler)
        builder.add_edge(START, "summarize")
        builder.add_edge("summarize", END)
        return builder.compile()

    def _summarize_handler(self, state: SummarizerState) -> dict:
        """Generate summary based on text and length."""
        text = state["text"]
        length = state.get("length", self.default_length)

        # Create prompt based on length
        length_instructions = {
            "short": "in 2-3 sentences",
            "medium": "in 1 paragraph (5-7 sentences)",
            "long": "in 2-3 paragraphs, preserving all key details",
        }

        prompt = f"Summarize the following text {length_instructions[length]}:\n\n{text}"

        response = self.model.invoke([{"role": "user", "content": prompt}])

        return {
            "summary": response.content,
            "messages": [{"role": "assistant", "content": response.content}],
        }

    def invoke(self, input_data: dict) -> dict:
        return self.graph.invoke(input_data)

    async def ainvoke(self, input_data: dict) -> dict:
        return await self.graph.ainvoke(input_data)


# Standalone graph export
_default_agent = SummarizerAgent()
graph = _default_agent.graph


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = {
            "messages": [{"role": "user", "content": "Summarize this"}],
            "text": "Long text here...",
            "length": "medium",
        }

    agent = SummarizerAgent()
    result = agent.invoke(input_data)
    print(json.dumps(result, indent=2, default=str))
```

### 3. Update `__init__.py`

```python
"""
SummarizerAgent - Text summarization with customizable length
"""

from langgraph_toolbox.agents.prebuilt.summarizer.agent import (
    SummarizerAgent,
    SummarizerState,
)

__all__ = ["SummarizerAgent", "SummarizerState"]
```

### 4. Update `README.md`

```markdown
# SummarizerAgent

**Category**: Utility
**Status**: Alpha
**Version**: 0.1.0

Intelligent text summarization with customizable length options.

## Features

- ✅ Three summary lengths (short/medium/long)
- ✅ Preserves key information
- ✅ Context-aware summarization

## Usage

\`\`\`python
from langgraph_toolbox.agents import SummarizerAgent

agent = SummarizerAgent()
result = agent.invoke({
    "text": "Your long text here...",
    "length": "medium"
})

print(result["summary"])
\`\`\`
```

### 5. Register in `langgraph.json`

```json
{
  "graphs": {
    "summarizer": "./src/langgraph_toolbox/agents/prebuilt/summarizer/agent.py:graph"
  }
}
```

### 6. Export

```python
# src/langgraph_toolbox/agents/prebuilt/__init__.py
from langgraph_toolbox.agents.prebuilt.summarizer import SummarizerAgent

__all__ = ["SummarizerAgent"]
```

### 7. Test

```bash
# Studio
langgraph dev

# Python
python -c "
from langgraph_toolbox.agents import SummarizerAgent
agent = SummarizerAgent()
result = agent.invoke({
    'text': 'Long text...',
    'length': 'short'
})
print(result['summary'])
"
```

---

## ✅ Pre-Submission Checklist

Before committing your agent:

- [ ] Follows standard structure
- [ ] All three modes work (import/studio/cli)
- [ ] Comprehensive docstrings
- [ ] README complete
- [ ] Tests written
- [ ] Registered in `langgraph.json`
- [ ] Exported in all `__init__.py` files

---

## 🎯 Tips

1. **Start simple**: Get basic version working first
2. **Test early**: Use `langgraph dev` frequently
3. **Document as you go**: Update README while coding
4. **Use patterns**: Import from `langgraph_toolbox.patterns` for common logic
5. **Follow conventions**: Match existing agents' style

---

## 🐛 Troubleshooting

### Agent not showing in Studio

- Check `langgraph.json` path is correct
- Ensure `graph` variable is exported
- Restart `langgraph dev`

### Import not working

- Check all `__init__.py` exports
- Verify class name matches exports
- Run `uv sync` after changes

### CLI execution fails

- Check `if __name__ == "__main__"` block
- Verify JSON parsing
- Test with simple input first

---

## 📚 Resources

- [Standard Structure](./prebuilt-agent-standard.md)
- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [Existing Agents](../../src/langgraph_toolbox/agents/prebuilt/)

---

Happy agent building! 🚀
