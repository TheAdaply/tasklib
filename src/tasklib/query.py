"""Filtering for tasks.

``query_tasks`` is the single place where task filters live. It is written as a
linear sequence of independent ``if <param> is not None:`` steps over a running
``result`` list so that adding a new filter is an obvious, isolated change.
"""

from __future__ import annotations

from tasklib.models import Task


def query_tasks(
    tasks: list[Task],
    *,
    done: bool | None = None,
    contains: str | None = None,
) -> list[Task]:
    """Filter ``tasks`` by completion status and/or a title substring.

    Filters are applied independently and combine with AND. Any parameter left
    as ``None`` is ignored; when all are ``None`` every task is returned.

    Args:
        tasks: The tasks to filter (not mutated).
        done: If set, keep only tasks whose ``done`` matches this value.
        contains: If set, keep only tasks whose title contains this text,
            compared case-insensitively.

    Returns:
        A new list of matching tasks, preserving input order.
    """
    result = list(tasks)

    if done is not None:
        result = [task for task in result if task.done == done]

    if contains is not None:
        needle = contains.lower()
        result = [task for task in result if needle in task.title.lower()]

    # add new filters above this line
    return result
