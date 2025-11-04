"""
Central node registry for discovering and using nodes across the library.

The registry provides a decorator-based pattern for registering nodes,
making them discoverable and reusable across all agents and subgraphs.
"""

from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class NodeMetadata:
    """
    Metadata about a registered node.

    Attributes:
        name: Unique node identifier
        func: The actual node function
        category: Category for organization (retrieval, routing, llm, etc.)
        description: Human-readable description (from docstring)
    """

    name: str
    func: Callable
    category: str
    description: str


class NodeRegistry:
    """
    Central registry for all nodes in the library.

    Nodes register themselves using the @NodeRegistry.register decorator.
    Agents and subgraphs look up nodes using NodeRegistry.get().

    Example:
        >>> from langgraph_toolbox.core.registry import NodeRegistry
        >>>
        >>> @NodeRegistry.register("my_node", category="processing")
        ... def my_node(state: State) -> dict:
        ...     '''Process the state.'''
        ...     return {"processed": True}
        >>>
        >>> # Later, in an agent or subgraph
        >>> node_func = NodeRegistry.get("my_node")
        >>> builder.add_node("process", node_func)
    """

    _nodes: dict[str, NodeMetadata] = {}

    @classmethod
    def register(
        cls,
        name: str,
        category: str = "general"
    ) -> Callable:
        """
        Decorator to register a node.

        Args:
            name: Unique node identifier
            category: Category for organization (retrieval, routing, llm, etc.)

        Returns:
            Decorator function

        Example:
            >>> @NodeRegistry.register("vector_search", category="retrieval")
            ... def vector_search_node(state: State) -> dict:
            ...     return {"results": [...]}
        """
        def decorator(func: Callable) -> Callable:
            # Check for duplicates
            if name in cls._nodes:
                raise ValueError(
                    f"Node '{name}' is already registered. "
                    f"Choose a different name or unregister the existing node."
                )

            # Register node
            cls._nodes[name] = NodeMetadata(
                name=name,
                func=func,
                category=category,
                description=func.__doc__ or ""
            )

            return func

        return decorator

    @classmethod
    def get(cls, name: str) -> Callable:
        """
        Get a registered node by name.

        Args:
            name: Node identifier

        Returns:
            Node function

        Raises:
            KeyError: If node not found

        Example:
            >>> search_node = NodeRegistry.get("vector_search")
            >>> builder.add_node("search", search_node)
        """
        if name not in cls._nodes:
            available = ", ".join(sorted(cls._nodes.keys()))
            raise KeyError(
                f"Node '{name}' not registered.\n"
                f"Available nodes: {available}"
            )

        return cls._nodes[name].func

    @classmethod
    def list_nodes(cls, category: Optional[str] = None) -> list[NodeMetadata]:
        """
        List all registered nodes, optionally filtered by category.

        Args:
            category: Filter by category (optional)

        Returns:
            List of node metadata

        Example:
            >>> # List all nodes
            >>> all_nodes = NodeRegistry.list_nodes()
            >>>
            >>> # List only retrieval nodes
            >>> retrieval_nodes = NodeRegistry.list_nodes(category="retrieval")
            >>> for node in retrieval_nodes:
            ...     print(f"{node.name}: {node.description}")
        """
        nodes = list(cls._nodes.values())

        if category:
            nodes = [n for n in nodes if n.category == category]

        return sorted(nodes, key=lambda n: n.name)

    @classmethod
    def list_categories(cls) -> list[str]:
        """
        List all available categories.

        Returns:
            Sorted list of unique categories

        Example:
            >>> categories = NodeRegistry.list_categories()
            >>> print(categories)
            ['general', 'llm', 'retrieval', 'routing']
        """
        categories = {node.category for node in cls._nodes.values()}
        return sorted(categories)

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregister a node.

        Useful for testing or dynamic node replacement.

        Args:
            name: Node identifier

        Example:
            >>> NodeRegistry.unregister("my_node")
        """
        if name in cls._nodes:
            del cls._nodes[name]

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered nodes.

        WARNING: This removes ALL nodes from the registry.
        Primarily useful for testing.

        Example:
            >>> NodeRegistry.clear()  # Remove all nodes
        """
        cls._nodes.clear()

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if a node is registered.

        Args:
            name: Node identifier

        Returns:
            True if registered, False otherwise

        Example:
            >>> if NodeRegistry.is_registered("vector_search"):
            ...     node = NodeRegistry.get("vector_search")
        """
        return name in cls._nodes

    @classmethod
    def get_metadata(cls, name: str) -> NodeMetadata:
        """
        Get full metadata for a node.

        Args:
            name: Node identifier

        Returns:
            NodeMetadata with name, func, category, description

        Raises:
            KeyError: If node not found

        Example:
            >>> metadata = NodeRegistry.get_metadata("vector_search")
            >>> print(f"Category: {metadata.category}")
            >>> print(f"Description: {metadata.description}")
        """
        if name not in cls._nodes:
            raise KeyError(f"Node '{name}' not registered")

        return cls._nodes[name]
