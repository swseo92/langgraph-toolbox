"""
Generic research nodes for web search and content analysis.

These nodes are domain-independent and can be used across
any research workflow or agent.
"""

from typing import Protocol, runtime_checkable
from langgraph_toolbox.core import NodeRegistry, trace_node
from langgraph_toolbox.lib.services import SearchService, FileSystemService


@runtime_checkable
class SearchableState(Protocol):
    """Protocol for states that support web search."""
    query: str


@runtime_checkable
class ResultsState(Protocol):
    """Protocol for states that have search results."""
    results: list[dict]


@NodeRegistry.register("web_search", category="research")
def web_search_node(
    state: SearchableState,
    max_results: int = 10,
    search_depth: str = "advanced"
) -> dict:
    """
    Perform web search using configured search service.

    Args:
        state: State with 'query' field
        max_results: Maximum number of results (default: 10)
        search_depth: "basic" or "advanced" (default: "advanced")

    Returns:
        dict with 'results' and 'result_count' fields

    Example:
        >>> builder.add_node("search", NodeRegistry.get("web_search"))
    """
    with trace_node("web_search", state) as span:
        search_service = SearchService.create()

        results = search_service.search(
            query=state.query,
            max_results=max_results,
            search_depth=search_depth
        )

        # Convert SearchResult objects to dicts
        results_dicts = [r.to_dict() for r in results]

        span.log_success(
            result_count=len(results_dicts),
            query_length=len(state.query)
        )

        return {
            "results": results_dicts,
            "result_count": len(results_dicts)
        }


@NodeRegistry.register("filter_results", category="research")
def filter_results_node(
    state: ResultsState,
    min_score: float = 0.5,
    max_results: int = 5
) -> dict:
    """
    Filter and rank search results.

    Args:
        state: State with 'results' field
        min_score: Minimum relevance score (0-1)
        max_results: Maximum results to keep

    Returns:
        dict with filtered 'results'

    Example:
        >>> builder.add_node("filter", NodeRegistry.get("filter_results"))
    """
    with trace_node("filter_results", state) as span:
        results = state.results

        # Filter by score
        filtered = [
            r for r in results
            if r.get("score", 1.0) >= min_score
        ]

        # Sort by score (descending)
        filtered = sorted(
            filtered,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        # Limit results
        filtered = filtered[:max_results]

        span.log_success(
            original_count=len(results),
            filtered_count=len(filtered),
            min_score=min_score
        )

        return {"results": filtered}


@NodeRegistry.register("save_results", category="research")
def save_results_node(
    state: ResultsState,
    filename: str = "search_results.json",
    subdirectory: str | None = None
) -> dict:
    """
    Save search results to file.

    Args:
        state: State with 'results' field
        filename: Output filename
        subdirectory: Optional subdirectory

    Returns:
        dict with 'file_path' and 'saved' status

    Example:
        >>> builder.add_node("save", NodeRegistry.get("save_results"))
    """
    with trace_node("save_results", state) as span:
        fs = FileSystemService()

        file_path = fs.write_json(
            filename=filename,
            data={"results": state.results},
            subdirectory=subdirectory
        )

        span.log_success(
            result_count=len(state.results),
            file_path=str(file_path)
        )

        return {
            "file_path": str(file_path),
            "saved": True
        }


@runtime_checkable
class SummarizableState(Protocol):
    """Protocol for states that can be summarized."""
    messages: list[dict]
    results: list[dict]


@NodeRegistry.register("summarize_findings", category="research")
def summarize_findings_node(
    state: SummarizableState,
    model: str = "gpt-4o-mini"
) -> dict:
    """
    Summarize research findings using LLM.

    Args:
        state: State with 'results' field
        model: LLM model to use

    Returns:
        dict with 'summary' and updated 'messages'

    Example:
        >>> builder.add_node("summarize", NodeRegistry.get("summarize_findings"))
    """
    with trace_node("summarize_findings", state) as span:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=model, temperature=0.3)

        # Prepare context from results
        context = "\\n\\n".join([
            f"**{r['title']}**\\n{r['snippet']}\\nSource: {r['url']}"
            for r in state.results
        ])

        # Create summarization prompt
        prompt = f"""Based on the following search results, provide a comprehensive summary of the key findings:

{context}

Please synthesize the information into:
1. Main themes and insights
2. Key facts and data points
3. Notable sources and references

Keep the summary concise but comprehensive."""

        messages = state.messages + [
            {"role": "user", "content": prompt}
        ]

        response = llm.invoke(messages)

        span.log_success(
            result_count=len(state.results),
            summary_length=len(response.content)
        )

        return {
            "summary": response.content,
            "messages": messages + [
                {"role": "assistant", "content": response.content}
            ]
        }
