# langgraph-toolbox

🛠️ **Community-driven** utilities and patterns for LangGraph development

> ⚠️ **This is an unofficial, community-maintained project.**
> Not affiliated with or endorsed by LangChain Inc.

---

## Overview

`langgraph-toolbox` is a collection of helper functions, reusable patterns, and utilities designed to make LangGraph development more efficient and enjoyable. This library provides:

- **State Management Helpers**: Utilities for working with TypedDict and State schemas
- **Node Patterns**: Reusable node templates with retry logic, error handling, and more
- **Conditional Edge Builders**: Simplified routing logic and conditional branching
- **Testing Utilities**: Mock states, test graph builders, and debugging tools
- **High-level Abstractions**: Common patterns for agent workflows and orchestration

---

## Installation

### Using pip

```bash
pip install langgraph-toolbox
```

### Using uv (recommended)

```bash
uv add langgraph-toolbox
```

### Development Installation

```bash
git clone https://github.com/swseo92/langgraph-toolbox.git
cd langgraph-toolbox
uv sync --dev
```

---

## Quick Start

Coming soon! This project is in early development.

```python
from langgraph_toolbox import ...

# Example usage will be added here
```

---

## 🎨 LangGraph Studio

This project includes LangGraph Studio support for visual development and debugging.

### Prerequisites

1. **LangSmith Account**: Sign up at https://smith.langchain.com
2. **Python 3.11+**: Required for LangGraph CLI
3. **Environment Variables**: Set up your `.env` file

### Setup

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Add your LangSmith API key to .env
LANGSMITH_API_KEY=lsv2_your_key_here

# 3. Start the local server
langgraph dev
```

### Using LangGraph Studio

Once the server is running, you'll see:

```
API: http://localhost:2024
Docs: http://localhost:2024/docs
Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

Open the Studio URL in your browser to:
- 📊 **Visualize** your agent graphs
- 🎮 **Interact** with agents in real-time
- 🐛 **Debug** execution flows step-by-step
- 📝 **Edit** prompts and configurations live

### Example Agent

Try the included example agent:

```bash
# Start the server
langgraph dev

# In another terminal, test the agent
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "example_agent",
    "input": {"messages": [{"role": "user", "content": "Hello!"}]}
  }'
```

---

## Features

### 🎯 State Management
- State schema validators
- State transformation utilities
- Type-safe state builders

### 🔄 Node Patterns
- Retry-enabled nodes
- Error handling wrappers
- Async node helpers

### 🔀 Conditional Routing
- Dynamic edge builders
- Condition validators
- Routing helpers

### 🧪 Testing & Debugging
- Mock state generators
- Test graph builders
- LangSmith integration helpers

---

## Roadmap

- [ ] Core state management utilities
- [ ] Node pattern templates
- [ ] Conditional edge builders
- [ ] Testing framework integration
- [ ] Documentation and examples
- [ ] PyPI publication

---

## Contributing

Contributions are welcome! This is a community project and we'd love your help.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and install dependencies
git clone https://github.com/swseo92/langgraph-toolbox.git
cd langgraph-toolbox
uv sync --dev

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built for the [LangGraph](https://github.com/langchain-ai/langgraph) community
- Inspired by common patterns from LangGraph projects
- Special thanks to all contributors

---

## Disclaimer

This project is not officially associated with LangChain Inc. or the LangGraph project. It is a community-driven effort to provide helpful utilities for LangGraph developers.

For official LangGraph resources, please visit:
- [LangGraph Official Docs](https://python.langchain.com/docs/langgraph)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)

---

**Made with ❤️ by the community, for the community**
