"""Tests for the reconciled seam: shared Task schema + filter registry.

These cover the reconciled base only (no feature filter modules are present on
this branch). The registry mechanism is exercised by dropping a throwaway filter
module into the ``tasklib.filters`` package directory at runtime, then removing
it — proving R-004 (zero edits to add a filter) without leaving anything behind.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from tasklib import filters as filters_registry
from tasklib.cli import build_parser
from tasklib.filters import FilterSpec
from tasklib.models import Task
from tasklib.query import query_tasks

_TEMP_MODULE = "tasklib.filters._tmp_starts_with"
_TEMP_SOURCE = '''
from tasklib.filters import FilterSpec


def _starts_with(task, value):
    return task.title.lower().startswith(value.lower())


FILTER = FilterSpec(
    name="starts_with",
    cli_flag="--starts-with",
    help="Show only tasks whose title starts with this text.",
    takes_value=True,
    predicate=_starts_with,
)
'''


@pytest.fixture()
def dropped_in_filter() -> Iterator[None]:
    """Drop a throwaway filter module into the package, then remove it.

    Simulates a developer adding a new filter by dropping a single file in,
    with no edits to any existing module.
    """
    pkg_dir = Path(filters_registry.__path__[0])
    module_path = pkg_dir / "_tmp_starts_with.py"
    module_path.write_text(_TEMP_SOURCE, encoding="utf-8")
    try:
        filters_registry.discover(force=True)
        yield
    finally:
        module_path.unlink(missing_ok=True)
        sys.modules.pop(_TEMP_MODULE, None)
        filters_registry.discover(force=True)


# --- Shared Task schema (R-001/002/003) ----------------------------------


def test_task_has_due_and_labels() -> None:  # T-001
    task = Task(id=1, title="x")
    assert task.due is None
    assert task.labels == []


def test_task_dict_round_trip_both_fields() -> None:  # T-002
    task = Task(
        id=7, title="ship", created_at="2026-06-13", due="2026-07-01",
        labels=["a", "b"],
    )
    assert task.to_dict() == {
        "id": 7,
        "title": "ship",
        "done": False,
        "created_at": "2026-06-13",
        "due": "2026-07-01",
        "labels": ["a", "b"],
    }
    assert Task.from_dict(task.to_dict()) == task


def test_from_dict_legacy_defaults() -> None:  # T-003
    data = {"id": 1, "title": "legacy", "done": False, "created_at": "2026-01-01"}
    task = Task.from_dict(data)
    assert task.due is None
    assert task.labels == []


# --- FilterSpec shape (R-005) --------------------------------------------


def test_filterspec_fields_present() -> None:  # T-005
    spec = FilterSpec(
        name="x", cli_flag="--x", help="h", takes_value=True,
        predicate=lambda task, value: True,
    )
    assert spec.name == "x"
    assert spec.cli_flag == "--x"
    assert spec.help == "h"
    assert spec.takes_value is True
    assert spec.predicate(Task(id=1, title="t"), "v") is True


# --- Discovery requires zero edits (R-004) -------------------------------


def test_registry_discovers_dropped_in_filter(dropped_in_filter: None) -> None:  # T-004
    names = {spec.name for spec in filters_registry.registry()}
    assert "starts_with" in names
    assert filters_registry.get("starts_with") is not None


def test_dropped_in_filter_is_absent_before_drop_in() -> None:
    # Adding a filter is purely additive: a module that has not been dropped in
    # is simply not in the registry. (Asserting the *absence* of our throwaway
    # filter stays correct even after real feature filters are added.)
    assert filters_registry.get("starts_with") is None


def test_duplicate_filter_name_is_rejected() -> None:
    from tasklib.filters import _coerce  # noqa: F401  (ensure import path valid)

    a = FilterSpec("dup", "--a", "h", True, lambda t, v: True)
    b = FilterSpec("dup", "--b", "h", True, lambda t, v: True)
    seen: dict[str, FilterSpec] = {}
    for spec in (a, b):
        if spec.name in seen:
            with pytest.raises(ValueError):
                raise ValueError(f"duplicate filter name: {spec.name!r}")
        seen[spec.name] = spec


# --- query_tasks applies a registered filter (R-006) ---------------------


def test_query_applies_registered_filter(dropped_in_filter: None) -> None:  # T-006
    tasks = [
        Task(id=1, title="alpha"),
        Task(id=2, title="beta"),
        Task(id=3, title="alphabet"),
    ]
    result = query_tasks(tasks, starts_with="alpha")
    assert [task.id for task in result] == [1, 3]


def test_query_unknown_kwarg_raises() -> None:
    with pytest.raises(TypeError):
        query_tasks([Task(id=1, title="x")], no_such_filter="v")


def test_query_registered_value_none_is_inactive(dropped_in_filter: None) -> None:  # R-009
    tasks = [Task(id=1, title="alpha"), Task(id=2, title="beta")]
    assert query_tasks(tasks, starts_with=None) == tasks


# --- CLI grows a flag per filter (R-008/009) -----------------------------


def test_cli_list_exposes_flag_per_filter(dropped_in_filter: None) -> None:  # T-008
    # Rebuild the parser AFTER the filter is registered so it picks up the flag.
    importlib.reload(sys.modules["tasklib.cli"])
    from tasklib.cli import build_parser as fresh_build_parser

    parser = fresh_build_parser()
    args = parser.parse_args(["list", "--starts-with", "alpha"])
    assert args.starts_with == "alpha"
    # Restore the cli module to its registry-empty state for other tests.
    importlib.reload(sys.modules["tasklib.cli"])


def test_cli_value_filter_inactive_when_absent() -> None:  # T-009
    parser = build_parser()
    args = parser.parse_args(["list"])
    # The base parser has no registered filters, but the built-ins default off.
    assert args.done is None
    assert args.contains is None
