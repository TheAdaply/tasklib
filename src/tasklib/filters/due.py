"""Due-date filters (Akash) — registered, isolated, zero edits elsewhere.

Dropping this file into ``tasklib.filters`` is the entire feature: the registry
discovers ``FILTER`` automatically, ``query_tasks`` applies it by name, and the
CLI grows ``--overdue`` and ``--due-before`` flags. No shared file is touched.
"""

from __future__ import annotations

from tasklib.dates import is_overdue
from tasklib.filters import FilterSpec
from tasklib.models import Task


def _overdue(task: Task, value: object) -> bool:
    """Keep tasks whose due date is before today."""
    return is_overdue(task.due)


def _due_before(task: Task, value: object) -> bool:
    """Keep tasks with a due date strictly before ``value`` (an ISO date)."""
    return task.due is not None and task.due < str(value)


FILTER = [
    FilterSpec(
        name="overdue",
        cli_flag="--overdue",
        help="Show only tasks whose due date is before today.",
        takes_value=False,
        predicate=_overdue,
    ),
    FilterSpec(
        name="due_before",
        cli_flag="--due-before",
        help="Show only tasks due strictly before this ISO date (YYYY-MM-DD).",
        takes_value=True,
        predicate=_due_before,
    ),
]
