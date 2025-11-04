"""
Base state classes for all LangGraph agents and subgraphs.

All states should inherit from BaseState to ensure consistency
and common functionality across the library.
"""

from typing import Any
from pydantic import BaseModel, Field


class BaseState(BaseModel):
    """
    Base state class for all LangGraph workflows.

    Provides common fields that all agents and subgraphs can use:
    - messages: Conversation history
    - metadata: Arbitrary workflow metadata (timing, status, etc.)

    Attributes:
        messages: List of message dicts (role, content, etc.)
        metadata: Dictionary for arbitrary metadata

    Example:
        >>> from langgraph_toolbox.core.state_base import BaseState
        >>>
        >>> class MyAgentState(BaseState):
        ...     query: str
        ...     results: list[dict] = []
        >>>
        >>> state = MyAgentState(query="test", messages=[])
        >>> print(state.query)
        test
    """

    messages: list[dict] = Field(
        default_factory=list,
        description="Conversation history with role/content structure"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata (timing, status, version, etc.)"
    )

    class Config:
        """Pydantic configuration."""
        # Allow arbitrary types (for complex objects)
        arbitrary_types_allowed = True
        # Allow extra fields at runtime for flexibility
        extra = "allow"
        # Use enum values instead of enum instances
        use_enum_values = True


class ErrorState(BaseState):
    """
    State extension for tracking errors.

    Use this when you need explicit error tracking in your workflow.

    Attributes:
        error: Error message (None if no error)
        error_type: Type of error (None if no error)
        error_stack: Full stack trace (None if no error)
    """

    error: str | None = Field(
        default=None,
        description="Error message if workflow failed"
    )
    error_type: str | None = Field(
        default=None,
        description="Type of error (ValueError, RuntimeError, etc.)"
    )
    error_stack: str | None = Field(
        default=None,
        description="Full stack trace"
    )

    def has_error(self) -> bool:
        """Check if state has an error."""
        return self.error is not None


class TimestampedState(BaseState):
    """
    State extension with automatic timestamp tracking.

    Useful for performance monitoring and debugging.

    Attributes:
        created_at: Unix timestamp when state was created
        updated_at: Unix timestamp when state was last updated
    """

    created_at: float = Field(
        default_factory=lambda: __import__("time").time(),
        description="Unix timestamp when state was created"
    )
    updated_at: float = Field(
        default_factory=lambda: __import__("time").time(),
        description="Unix timestamp when state was last updated"
    )

    def touch(self) -> None:
        """Update the updated_at timestamp to current time."""
        import time
        self.updated_at = time.time()

    def age_seconds(self) -> float:
        """Get age of state in seconds."""
        import time
        return time.time() - self.created_at
