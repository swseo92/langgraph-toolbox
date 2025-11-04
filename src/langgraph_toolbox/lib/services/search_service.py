"""
Web search service for research operations.

Provides abstraction over web search APIs (Tavily, Google, Bing, etc.)
with unified interface for research agents.
"""

import os
from typing import Optional
from abc import ABC, abstractmethod


class SearchResult:
    """
    Structured search result.

    Attributes:
        title: Result title
        url: Source URL
        snippet: Text snippet/summary
        score: Relevance score (0-1)
        published_date: Publication date (optional)
    """

    def __init__(
        self,
        title: str,
        url: str,
        snippet: str,
        score: float = 1.0,
        published_date: Optional[str] = None,
    ):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.score = score
        self.published_date = published_date

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "score": self.score,
            "published_date": self.published_date,
        }

    def __repr__(self) -> str:
        return f"SearchResult(title={self.title!r}, url={self.url!r}, score={self.score})"


class SearchServiceBase(ABC):
    """Abstract base for search services."""

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> list[SearchResult]:
        """
        Search the web.

        Args:
            query: Search query
            max_results: Maximum number of results
            **kwargs: Provider-specific options

        Returns:
            List of SearchResult objects
        """
        pass


class TavilySearchService(SearchServiceBase):
    """
    Tavily AI search service.

    Tavily provides AI-optimized search specifically designed for
    research and LLM applications.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily search.

        Args:
            api_key: Tavily API key (or use TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Tavily API key not provided. "
                "Set TAVILY_API_KEY environment variable or pass api_key parameter."
            )

    def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        **kwargs
    ) -> list[SearchResult]:
        """
        Search using Tavily.

        Args:
            query: Search query
            max_results: Maximum results (default: 10)
            search_depth: "basic" or "advanced" (default: "advanced")
            **kwargs: Additional Tavily options

        Returns:
            List of SearchResult objects
        """
        try:
            from tavily import TavilyClient
        except ImportError:
            raise ImportError(
                "Tavily package not installed. "
                "Install with: pip install tavily-python"
            )

        client = TavilyClient(api_key=self.api_key)

        response = client.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            **kwargs
        )

        results = []
        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    score=item.get("score", 1.0),
                )
            )

        return results


class MockSearchService(SearchServiceBase):
    """
    Mock search service for testing.

    Returns predefined results without making actual API calls.
    """

    def __init__(self, mock_results: Optional[list[SearchResult]] = None):
        """
        Initialize mock search.

        Args:
            mock_results: Predefined results to return
        """
        self.mock_results = mock_results or []

    def search(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> list[SearchResult]:
        """
        Return mock results.

        Args:
            query: Search query (ignored)
            max_results: Maximum results
            **kwargs: Ignored

        Returns:
            Mock search results
        """
        return self.mock_results[:max_results]


class SearchService:
    """
    Factory for creating search service instances.

    Auto-selects provider based on available API keys.
    """

    @staticmethod
    def create(provider: str = "auto", **kwargs) -> SearchServiceBase:
        """
        Create a search service.

        Args:
            provider: "tavily", "mock", or "auto" (auto-detect from env)
            **kwargs: Provider-specific arguments

        Returns:
            SearchService instance

        Example:
            >>> # Auto-detect provider
            >>> service = SearchService.create()
            >>> results = service.search("LangGraph tutorial")
            >>>
            >>> # Explicit provider
            >>> service = SearchService.create(provider="tavily")
            >>>
            >>> # Mock for testing
            >>> mock_results = [SearchResult("Test", "http://test.com", "snippet")]
            >>> service = SearchService.create(provider="mock", mock_results=mock_results)
        """
        if provider == "auto":
            # Auto-detect based on API keys
            if os.getenv("TAVILY_API_KEY"):
                provider = "tavily"
            else:
                raise ValueError(
                    "No search API keys found. "
                    "Set TAVILY_API_KEY or use provider='mock' for testing."
                )

        if provider == "tavily":
            return TavilySearchService(**kwargs)
        elif provider == "mock":
            return MockSearchService(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")
