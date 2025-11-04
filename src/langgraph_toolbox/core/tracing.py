"""
Observability infrastructure for debugging and monitoring LangGraph workflows.

Provides tracing context managers and utilities for tracking node execution,
performance metrics, and errors across complex multi-agent systems.
"""

from contextlib import contextmanager
from typing import Optional, Any
import time
import logging

logger = logging.getLogger(__name__)


class Span:
    """
    Represents a traced operation (node execution).

    Tracks timing, success/failure, and arbitrary metrics.

    Attributes:
        name: Name of the operation (node name)
        state: Current state snapshot
        start_time: Unix timestamp when operation started
        error: Exception if operation failed
        metrics: Dictionary of arbitrary metrics
    """

    def __init__(self, name: str, state: dict):
        """
        Initialize a span.

        Args:
            name: Operation name
            state: Current state dict
        """
        self.name = name
        self.state = state
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.error: Optional[Exception] = None
        self.metrics: dict[str, Any] = {}

    def log_success(self, **metrics: Any) -> None:
        """
        Log successful completion with optional metrics.

        Args:
            **metrics: Arbitrary key-value metrics

        Example:
            >>> span.log_success(items_processed=10, cache_hit=True)
        """
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.metrics = {"duration_ms": duration * 1000, **metrics}

        logger.info(
            f"✓ {self.name} completed in {duration*1000:.2f}ms",
            extra={"metrics": self.metrics}
        )

    def log_error(self, error: Exception) -> None:
        """
        Log operation failure.

        Args:
            error: Exception that occurred

        Example:
            >>> try:
            ...     risky_operation()
            ... except Exception as e:
            ...     span.log_error(e)
        """
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.error = error
        self.metrics = {"duration_ms": duration * 1000}

        logger.error(
            f"✗ {self.name} failed after {duration*1000:.2f}ms: {error}",
            extra={"error": str(error), "error_type": type(error).__name__}
        )

    def end(self) -> None:
        """
        End span.

        Hook for integrating with external tracing systems
        (LangSmith, OpenTelemetry, etc.)
        """
        # Future: Send to LangSmith, OpenTelemetry, etc.
        pass


@contextmanager
def trace_node(node_name: str, state: dict):
    """
    Trace node execution with automatic timing and error handling.

    This context manager should wrap every node execution to provide
    uniform observability across the entire workflow.

    Args:
        node_name: Name of the node being executed
        state: Current state dict

    Yields:
        Span object for logging additional metrics

    Example:
        >>> def my_node(state: State) -> dict:
        ...     with trace_node("my_node", state) as span:
        ...         result = do_work(state)
        ...         span.log_success(items_processed=len(result))
        ...         return {"result": result}
    """
    span = Span(node_name, state)
    logger.info(f"→ {node_name} starting")

    try:
        yield span
        # If user didn't call log_success, call it automatically
        if span.end_time is None:
            span.log_success()
    except Exception as e:
        span.log_error(e)
        raise
    finally:
        span.end()


def get_default_tracer():
    """
    Get default tracer (LangSmith if available).

    Returns:
        LangSmith client if available, None otherwise

    Example:
        >>> tracer = get_default_tracer()
        >>> if tracer:
        ...     tracer.create_run(...)
    """
    try:
        from langsmith import Client
        return Client()
    except ImportError:
        logger.debug("LangSmith not available, tracing to logs only")
        return None


def configure_logging(
    level: str = "INFO",
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> None:
    """
    Configure logging for tracing.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format: Log format string

    Example:
        >>> from langgraph_toolbox.core.tracing import configure_logging
        >>> configure_logging(level="DEBUG")
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format
    )


class MetricsCollector:
    """
    Collect and aggregate metrics from multiple spans.

    Useful for performance analysis and monitoring.

    Example:
        >>> collector = MetricsCollector()
        >>>
        >>> with trace_node("node1", state) as span:
        ...     # work
        ...     collector.add_span(span)
        >>>
        >>> stats = collector.get_stats()
        >>> print(stats["total_duration_ms"])
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.spans: list[Span] = []

    def add_span(self, span: Span) -> None:
        """
        Add a span to the collector.

        Args:
            span: Span to add
        """
        self.spans.append(span)

    def get_stats(self) -> dict[str, Any]:
        """
        Get aggregated statistics.

        Returns:
            Dictionary with total_duration_ms, success_count, error_count, etc.

        Example:
            >>> stats = collector.get_stats()
            >>> print(f"Total duration: {stats['total_duration_ms']:.2f}ms")
            >>> print(f"Success rate: {stats['success_rate']:.1%}")
        """
        if not self.spans:
            return {
                "total_duration_ms": 0,
                "success_count": 0,
                "error_count": 0,
                "success_rate": 0.0
            }

        total_duration = sum(
            span.metrics.get("duration_ms", 0)
            for span in self.spans
        )
        success_count = sum(1 for span in self.spans if span.error is None)
        error_count = len(self.spans) - success_count

        return {
            "total_duration_ms": total_duration,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_count / len(self.spans) if self.spans else 0.0,
            "avg_duration_ms": total_duration / len(self.spans) if self.spans else 0.0
        }

    def get_slowest_spans(self, n: int = 5) -> list[tuple[str, float]]:
        """
        Get the N slowest spans.

        Args:
            n: Number of spans to return

        Returns:
            List of (span_name, duration_ms) tuples

        Example:
            >>> slowest = collector.get_slowest_spans(3)
            >>> for name, duration in slowest:
            ...     print(f"{name}: {duration:.2f}ms")
        """
        spans_with_duration = [
            (span.name, span.metrics.get("duration_ms", 0))
            for span in self.spans
        ]
        return sorted(spans_with_duration, key=lambda x: x[1], reverse=True)[:n]

    def clear(self) -> None:
        """Clear all collected spans."""
        self.spans.clear()
