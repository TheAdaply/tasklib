"""Tests for the registered due-date filters (Akash)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tasklib import filters as filters_registry
from tasklib.cli import build_parser, main
from tasklib.models import Task
from tasklib.query import query_tasks


def _sample() -> list[Task]:
    # Use unambiguous past / far-future dates so "today" never changes the
    # expected result.
    return [
        Task(id=1, title="ancient", due="2000-01-01"),
        Task(id=2, title="far future", due="2999-12-31"),
        Task(id=3, title="no due", due=None),
        Task(id=4, title="also past", due="2001-02-03"),
    ]


def _ids(tasks: list[Task]) -> list[int]:
    return [task.id for task in tasks]


def test_due_filters_are_registered() -> None:
    names = {spec.name for spec in filters_registry.registry()}
    assert {"overdue", "due_before"} <= names


def test_overdue_is_a_boolean_filter() -> None:
    spec = filters_registry.get("overdue")
    assert spec is not None and spec.takes_value is False


def test_due_before_is_a_value_filter() -> None:
    spec = filters_registry.get("due_before")
    assert spec is not None and spec.takes_value is True


def test_query_overdue() -> None:
    # Both year-2000 and year-2001 dates are before any realistic "today".
    assert _ids(query_tasks(_sample(), overdue=True)) == [1, 4]


def test_query_overdue_excludes_far_future_and_undated() -> None:
    result_ids = _ids(query_tasks(_sample(), overdue=True))
    assert 2 not in result_ids  # far future
    assert 3 not in result_ids  # no due date


def test_query_overdue_false_is_inactive() -> None:
    assert query_tasks(_sample(), overdue=False) == _sample()


def test_query_due_before() -> None:
    assert _ids(query_tasks(_sample(), due_before="2001-01-01")) == [1]


def test_query_due_before_skips_tasks_without_due() -> None:
    assert 3 not in _ids(query_tasks(_sample(), due_before="2999-01-01"))


def test_cli_list_has_due_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(["list", "--overdue", "--due-before", "2026-06-13"])
    assert args.overdue is True
    assert args.due_before == "2026-06-13"


def test_cli_list_filters_overdue(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    store = tmp_path / "tasks.json"
    from tasklib.store import TaskStore

    s = TaskStore()
    s.add("old").due = "2000-01-01"
    s.add("new").due = "2999-12-31"
    s.save(store)

    assert main(["--store", str(store), "list", "--overdue"]) == 0
    out = capsys.readouterr().out
    assert "old" in out
    assert "new" not in out
