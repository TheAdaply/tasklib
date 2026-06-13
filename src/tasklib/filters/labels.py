"""Label filter (Shine) — registered, isolated, zero edits elsewhere.

Dropping this file into ``tasklib.filters`` is the entire feature: the registry
discovers ``FILTER`` automatically, ``query_tasks`` applies it by name, and the
CLI grows a ``--label`` flag. No shared file is touched.
"""

from __future__ import annotations

from tasklib.filters import FilterSpec
from tasklib.labels import normalize_label
from tasklib.models import Task


def _has_label(task: Task, value: object) -> bool:
    """Keep tasks carrying ``value`` as a label (compared in normalized form)."""
    wanted = normalize_label(str(value))
    return wanted in {normalize_label(label) for label in task.labels}


FILTER = FilterSpec(
    name="label",
    cli_flag="--label",
    help="Show only tasks carrying this label.",
    takes_value=True,
    predicate=_has_label,
)
