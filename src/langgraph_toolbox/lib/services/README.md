# Service Adapters

**Layer**: Shared Capabilities - Services
**Purpose**: Abstract external service integrations

---

## 📋 Overview

Service adapters provide a clean abstraction layer between nodes and external services (vectorstores, LLMs, APIs, databases, etc.). This layer handles authentication, error handling, retries, and provider-specific logic.

---

## 🎯 Responsibilities

**This layer SHOULD**:
- ✅ Abstract external service APIs
- ✅ Handle authentication and credentials
- ✅ Implement retry logic and error handling
- ✅ Provide consistent interfaces across providers
- ✅ Cache responses when appropriate

**This layer SHOULD NOT**:
- ❌ Implement business logic
- ❌ Know about state schemas
- ❌ Know about agents or subgraphs
- ❌ Directly modify state

---

## 📁 Structure

```
lib/services/
├── __init__.py
├── vectorstore.py        # Vectorstore abstractions (Pinecone, Weaviate, etc.)
├── llm_client.py         # LLM client abstractions (OpenAI, Anthropic, etc.)
├── search_api.py         # Search API integrations (Google, Bing, etc.)
└── tests/
    ├── test_vectorstore.py
    └── test_llm_client.py
```

---

## 🚀 Creating a Service Adapter

### Step 1: Define Abstract Interface

```python
# lib/services/vectorstore.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class VectorStoreBase(ABC):
    """Abstract base class for vectorstore services."""

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Search for similar vectors.

        Args:
            query: Search query
            top_k: Number of results
            threshold: Minimum similarity score

        Returns:
            List of result dicts with 'id', 'text', 'score'
        """
        pass

    @abstractmethod
    def insert(self, documents: List[Dict]) -> bool:
        """Insert documents into vectorstore."""
        pass
```

### Step 2: Implement Provider-Specific Adapters

```python
# lib/services/vectorstore.py (continued)
import os
from typing import Optional

class PineconeAdapter(VectorStoreBase):
    """Pinecone vectorstore adapter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: str = "default"
    ):
        api_key = api_key or os.getenv("PINECONE_API_KEY")
        environment = environment or os.getenv("PINECONE_ENVIRONMENT")

        if not api_key:
            raise ValueError("PINECONE_API_KEY not provided")

        import pinecone
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(index_name)

    def search(self, query: str, top_k: int = 10, threshold: float = 0.7) -> List[Dict]:
        # Embed query
        embedding = self._embed(query)

        # Search
        results = self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Filter by threshold and format
        return [
            {
                "id": match.id,
                "text": match.metadata.get("text", ""),
                "score": match.score
            }
            for match in results.matches
            if match.score >= threshold
        ]

    def insert(self, documents: List[Dict]) -> bool:
        # Implementation
        pass

    def _embed(self, text: str) -> List[float]:
        # Use OpenAI or other embedding service
        pass
```

### Step 3: Factory Pattern

```python
# lib/services/vectorstore.py (continued)
class VectorStoreService:
    """
    Factory for creating vectorstore clients.

    Auto-selects provider based on environment variables or explicit choice.
    """

    @staticmethod
    def create(provider: str = "auto", **kwargs) -> VectorStoreBase:
        """
        Create vectorstore client.

        Args:
            provider: "pinecone", "weaviate", "auto" (detect from env)
            **kwargs: Provider-specific arguments

        Returns:
            VectorStore instance
        """
        if provider == "auto":
            if os.getenv("PINECONE_API_KEY"):
                provider = "pinecone"
            elif os.getenv("WEAVIATE_URL"):
                provider = "weaviate"
            else:
                raise ValueError("No vectorstore credentials found")

        if provider == "pinecone":
            return PineconeAdapter(**kwargs)
        elif provider == "weaviate":
            return WeaviateAdapter(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

**Usage in Nodes**:
```python
# lib/nodes/retrieval.py
from langgraph_toolbox.lib.services.vectorstore import VectorStoreService

@NodeRegistry.register("vector_search")
def vector_search_node(state: SearchableState, top_k: int = 10) -> dict:
    # Create service (auto-detects provider)
    service = VectorStoreService.create()

    # Use service
    results = service.search(state.query, top_k=top_k)

    return {"results": results}
```

---

## 🎨 Design Patterns

### Pattern 1: Retry with Exponential Backoff

```python
import time
from functools import wraps

def with_retry(max_retries: int = 3, backoff: float = 2.0):
    """Decorator for retrying failed service calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait = backoff ** attempt
                    logger.warning(f"Retry {attempt+1}/{max_retries} after {wait}s: {e}")
                    time.sleep(wait)
        return wrapper
    return decorator

class RobustVectorStore(VectorStoreBase):
    @with_retry(max_retries=3)
    def search(self, query: str, **kwargs) -> List[Dict]:
        # Implementation that may fail
        pass
```

### Pattern 2: Response Caching

```python
from functools import lru_cache
import hashlib

class CachedVectorStore(VectorStoreBase):
    def __init__(self, base_store: VectorStoreBase):
        self.base_store = base_store
        self._cache = {}

    def search(self, query: str, top_k: int = 10, **kwargs) -> List[Dict]:
        # Create cache key
        cache_key = hashlib.md5(f"{query}:{top_k}".encode()).hexdigest()

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Query base store
        results = self.base_store.search(query, top_k=top_k, **kwargs)

        # Cache results
        self._cache[cache_key] = results
        return results
```

### Pattern 3: Rate Limiting

```python
import time
from threading import Lock

class RateLimitedService:
    """Rate-limited service wrapper."""

    def __init__(self, service, calls_per_second: float = 10.0):
        self.service = service
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
        self.lock = Lock()

    def __getattr__(self, name):
        """Wrap all service methods with rate limiting."""
        attr = getattr(self.service, name)
        if callable(attr):
            def rate_limited_method(*args, **kwargs):
                with self.lock:
                    elapsed = time.time() - self.last_call
                    if elapsed < self.min_interval:
                        time.sleep(self.min_interval - elapsed)
                    self.last_call = time.time()
                return attr(*args, **kwargs)
            return rate_limited_method
        return attr
```

---

## 🧪 Testing Strategy

### Mock Services for Testing

```python
# lib/services/tests/test_vectorstore.py
from langgraph_toolbox.lib.services.vectorstore import VectorStoreBase

class MockVectorStore(VectorStoreBase):
    """Mock vectorstore for testing."""

    def __init__(self):
        self.documents = []

    def search(self, query: str, top_k: int = 10, threshold: float = 0.7) -> List[Dict]:
        # Return mock results
        return [
            {"id": "1", "text": "mock result 1", "score": 0.9},
            {"id": "2", "text": "mock result 2", "score": 0.8}
        ][:top_k]

    def insert(self, documents: List[Dict]) -> bool:
        self.documents.extend(documents)
        return True

# Usage in tests
def test_search_node():
    from langgraph_toolbox.lib.nodes.retrieval import vector_search_node

    # Inject mock service
    with patch('langgraph_toolbox.lib.services.vectorstore.VectorStoreService.create') as mock:
        mock.return_value = MockVectorStore()

        state = MockState(query="test")
        result = vector_search_node(state)

        assert len(result["results"]) == 2
```

---

## 📚 Common Services

### LLM Client Service

```python
# lib/services/llm_client.py
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class LLMService:
    """Unified LLM client interface."""

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self._client = self._init_client()

    def _init_client(self):
        if self.model.startswith("gpt"):
            return ChatOpenAI(model=self.model, temperature=self.temperature)
        elif self.model.startswith("claude"):
            return ChatAnthropic(model=self.model, temperature=self.temperature)
        else:
            raise ValueError(f"Unsupported model: {self.model}")

    def generate(self, messages: List[Dict]) -> str:
        """Generate text from messages."""
        response = self._client.invoke(messages)
        return response.content

    def stream(self, messages: List[Dict]):
        """Stream text generation."""
        for chunk in self._client.stream(messages):
            yield chunk.content
```

### Search API Service

```python
# lib/services/search_api.py
import os
import requests

class SearchAPIService:
    """Web search API integration."""

    def __init__(self, provider: str = "google"):
        self.provider = provider
        self.api_key = os.getenv(f"{provider.upper()}_API_KEY")

    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Perform web search.

        Returns:
            List of dicts with 'title', 'url', 'snippet'
        """
        if self.provider == "google":
            return self._google_search(query, num_results)
        elif self.provider == "bing":
            return self._bing_search(query, num_results)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _google_search(self, query: str, num_results: int) -> List[Dict]:
        # Google Custom Search API implementation
        pass

    def _bing_search(self, query: str, num_results: int) -> List[Dict]:
        # Bing Search API implementation
        pass
```

---

## 🔗 See Also

- [Design Philosophy](../../../../docs/architecture/design-philosophy.md)
- [Lib Nodes](../nodes/README.md) - Using services in nodes
- [Testing Guidelines](../../../../docs/python/testing_guidelines.md)
