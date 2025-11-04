"""
Common state manipulation patterns for LangGraph workflows.

Provides utilities for merging states, updating metadata, and
managing data flow between parent and child graphs.
"""

from typing import TypeVar, Callable, Any

T = TypeVar('T')


def merge_subgraph_state(
    parent: dict,
    child: dict,
    field_mapping: dict[str, str]
) -> dict:
    """
    Merge child subgraph state into parent state.

    Useful when a parent graph runs a subgraph and needs to merge
    the results back into its own state.

    Args:
        parent: Parent state dict
        child: Child subgraph result state
        field_mapping: Map child fields to parent fields
                      {"parent_field": "child_field"}

    Returns:
        Merged state dict (does not modify parent in-place)

    Example:
        >>> parent = {"query": "test", "results": []}
        >>> child = {"search_results": [1, 2, 3], "count": 3}
        >>> mapping = {"results": "search_results", "result_count": "count"}
        >>>
        >>> merged = merge_subgraph_state(parent, child, mapping)
        >>> print(merged)
        {'query': 'test', 'results': [1, 2, 3], 'result_count': 3}
    """
    merged = dict(parent)

    for parent_key, child_key in field_mapping.items():
        if child_key in child:
            merged[parent_key] = child[child_key]

    return merged


def update_metadata(
    state: dict,
    updates: dict[str, Any],
    merge: bool = True
) -> dict:
    """
    Update metadata without overwriting entire dict.

    Args:
        state: Current state (must have 'metadata' field)
        updates: Metadata fields to update
        merge: If True, merge with existing metadata.
               If False, replace metadata entirely.

    Returns:
        State dict with updated metadata

    Example:
        >>> state = {"metadata": {"step": 1}}
        >>> updated = update_metadata(state, {"status": "processing"})
        >>> print(updated["metadata"])
        {'step': 1, 'status': 'processing'}
        >>>
        >>> # Replace entirely
        >>> replaced = update_metadata(state, {"new": "data"}, merge=False)
        >>> print(replaced["metadata"])
        {'new': 'data'}
    """
    if merge:
        metadata = state.get("metadata", {}).copy()
        metadata.update(updates)
    else:
        metadata = updates

    return {"metadata": metadata}


def increment_metadata_counter(
    state: dict,
    counter_name: str,
    increment: int = 1
) -> dict:
    """
    Increment a counter in metadata.

    Useful for tracking iterations, attempts, etc.

    Args:
        state: Current state
        counter_name: Name of the counter field
        increment: Amount to increment (default: 1)

    Returns:
        State dict with updated metadata

    Example:
        >>> state = {"metadata": {"attempts": 0}}
        >>> updated = increment_metadata_counter(state, "attempts")
        >>> print(updated["metadata"]["attempts"])
        1
        >>>
        >>> # Increment by custom amount
        >>> updated = increment_metadata_counter(state, "items_processed", 5)
    """
    metadata = state.get("metadata", {}).copy()
    current = metadata.get(counter_name, 0)
    metadata[counter_name] = current + increment

    return {"metadata": metadata}


def append_to_metadata_list(
    state: dict,
    list_name: str,
    item: Any
) -> dict:
    """
    Append an item to a list in metadata.

    Useful for tracking history, steps taken, etc.

    Args:
        state: Current state
        list_name: Name of the list field in metadata
        item: Item to append

    Returns:
        State dict with updated metadata

    Example:
        >>> state = {"metadata": {"steps": ["start"]}}
        >>> updated = append_to_metadata_list(state, "steps", "search")
        >>> print(updated["metadata"]["steps"])
        ['start', 'search']
    """
    metadata = state.get("metadata", {}).copy()
    items = metadata.get(list_name, []).copy()
    items.append(item)
    metadata[list_name] = items

    return {"metadata": metadata}


def create_state_reducer(
    reducer_func: Callable[[Any, Any], Any]
) -> Callable:
    """
    Create a state reducer function for use with Annotated types.

    State reducers control how LangGraph merges updates into state fields.

    Args:
        reducer_func: Function that takes (existing, new) and returns merged value

    Returns:
        Reducer function for use with Annotated[type, reducer]

    Example:
        >>> from typing import Annotated
        >>> from langgraph.graph.message import add_messages
        >>>
        >>> # Built-in reducer
        >>> messages: Annotated[list, add_messages]
        >>>
        >>> # Custom reducer
        >>> def merge_scores(existing: list, new: list) -> list:
        ...     return existing + new
        >>>
        >>> score_reducer = create_state_reducer(merge_scores)
        >>> scores: Annotated[list, score_reducer]
    """
    def reducer(existing: Any, new: Any) -> Any:
        return reducer_func(existing, new)

    return reducer


def merge_lists_unique(existing: list, new: list) -> list:
    """
    Merge two lists, removing duplicates.

    Useful as a state reducer for list fields.

    Args:
        existing: Existing list in state
        new: New list to merge

    Returns:
        Merged list with unique elements (preserves order)

    Example:
        >>> merge_lists_unique([1, 2, 3], [3, 4, 5])
        [1, 2, 3, 4, 5]
    """
    seen = set(existing)
    result = list(existing)

    for item in new:
        if item not in seen:
            result.append(item)
            seen.add(item)

    return result


def merge_dicts_deep(existing: dict, new: dict) -> dict:
    """
    Deep merge two dictionaries.

    Nested dicts are merged recursively. Lists are concatenated.

    Args:
        existing: Existing dict in state
        new: New dict to merge

    Returns:
        Deep-merged dictionary

    Example:
        >>> existing = {"a": 1, "b": {"c": 2}}
        >>> new = {"b": {"d": 3}, "e": 4}
        >>> merge_dicts_deep(existing, new)
        {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}
    """
    result = dict(existing)

    for key, value in new.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_deep(result[key], value)
        elif key in result and isinstance(result[key], list) and isinstance(value, list):
            result[key] = result[key] + value
        else:
            result[key] = value

    return result


def extract_fields(state: dict, fields: list[str]) -> dict:
    """
    Extract specific fields from state.

    Useful for passing only required fields to subgraphs.

    Args:
        state: Full state
        fields: List of field names to extract

    Returns:
        New dict with only the specified fields

    Example:
        >>> state = {"query": "test", "results": [], "metadata": {}}
        >>> extract_fields(state, ["query"])
        {'query': 'test'}
    """
    return {field: state[field] for field in fields if field in state}
