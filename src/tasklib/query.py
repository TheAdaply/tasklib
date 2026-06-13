"""Filtering for tasks.

``query_tasks`` keeps the built-in ``done`` and ``contains`` behavior and then
applies any *registered* filters passed as keyword arguments. Registered filters
live as self-describing modules under :mod:`tasklib.filters`, so adding a new
filter never touches this file (see ``specs/F-001-parallel-filters``).
"""

from __future__ import annotations

from tasklib import filters as filters_registry
from tasklib.models import Task


def query_tasks(
    tasks: list[Task],
    *,
    done: bool | None = None,
    contains: str | None = None,
    **registered: object,
) -> list[Task]:
    """Filter ``tasks`` by completion status, a title substring, and/or any
    registered filter.

    Filters are applied independently and combine with AND. The built-in
    ``done`` and ``contains`` parameters keep their original behavior. Any other
    keyword argument is looked up by name in the filter registry
    (:mod:`tasklib.filters`); its predicate is applied unless the value is
    "inactive" (``None`` for a value filter, falsy for a boolean filter).

    Args:
        tasks: The tasks to filter (not mutated).
        done: If set, keep only tasks whose ``done`` matches this value.
        contains: If set, keep only tasks whose title contains this text,
            compared case-insensitively.
        **registered: Values for registered filters, keyed by their ``name``.

    Returns:
        A new list of matching tasks, preserving input order.

    Raises:
        TypeError: If a keyword argument is neither built in nor a registered
            filter name.
    """
    result = list(tasks)

    if done is not None:
        result = [task for task in result if task.done == done]

    if contains is not None:
        needle = contains.lower()
        result = [task for task in result if needle in task.title.lower()]

    # Apply any registered filters passed by name. Each new feature adds an
    # isolated module under tasklib/filters/, so this loop never changes.
    for name, value in registered.items():
        spec = filters_registry.get(name)
        if spec is None:
            raise TypeError(
                f"query_tasks() got an unexpected keyword argument {name!r}"
            )
        if spec.takes_value:
            if value is None:
                continue
        elif not value:
            continue
        result = [task for task in result if spec.predicate(task, value)]

    return result
