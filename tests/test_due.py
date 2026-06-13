"""Tests for Akash's due-date feature: model field, helper, query, CLI."""

from __future__ import annotations

from pathlib import Path

from tasklib.dates import is_overdue
from tasklib.models import Task
from tasklib.query import query_tasks


def _sample() -> list[Task]:
    return [
        Task(id=1, title="write report", due="2026-01-01"),
        Task(id=2, title="review PR", due="2026-12-31"),
        Task(id=3, title="no due date", due=None),
        Task(id=4, title="ship release", due="2026-06-01"),
    ]


def _ids(tasks: list[Task]) -> list[int]:
    return [task.id for task in tasks]


def test_task_due_defaults_to_none() -> None:
    assert Task(id=1, title="x").due is None


def test_due_round_trips_through_dict() -> None:
    task = Task(id=9, title="ship", created_at="2026-06-13", due="2026-07-01")
    assert task.to_dict()["due"] == "2026-07-01"
    assert Task.from_dict(task.to_dict()) == task


def test_from_dict_without_due_defaults_to_none() -> None:
    data = {"id": 1, "title": "legacy", "done": False, "created_at": "2026-01-01"}
    assert Task.from_dict(data).due is None


def test_is_overdue_compares_against_reference() -> None:
    assert is_overdue("2026-01-01", today="2026-06-13") is True
    assert is_overdue("2026-12-31", today="2026-06-13") is False


def test_is_overdue_is_strict() -> None:
    assert is_overdue("2026-06-13", today="2026-06-13") is False


def test_is_overdue_none_is_never_overdue() -> None:
    assert is_overdue(None, today="2026-06-13") is False


def test_query_due_before() -> None:
    assert _ids(query_tasks(_sample(), due_before="2026-06-13")) == [1, 4]


def test_query_overdue_uses_today() -> None:
    tasks = [
        Task(id=1, title="past", due="2000-01-01"),
        Task(id=2, title="future", due="2999-01-01"),
        Task(id=3, title="none", due=None),
    ]
    assert _ids(query_tasks(tasks, overdue=True)) == [1]


def test_query_due_filters_skip_tasks_without_due() -> None:
    assert 3 not in _ids(query_tasks(_sample(), due_before="2026-06-13"))


def test_cli_add_with_due_and_list_due_before(tmp_path: Path) -> None:
    from tasklib.cli import main

    store = tmp_path / "tasks.json"
    assert main(["--store", str(store), "add", "early", "--due", "2026-01-01"]) == 0
    assert main(["--store", str(store), "add", "late", "--due", "2026-12-31"]) == 0

    loaded = __import__("tasklib.store", fromlist=["TaskStore"]).TaskStore.load(store)
    dues = {task.title: task.due for task in loaded.all()}
    assert dues == {"early": "2026-01-01", "late": "2026-12-31"}

    result = query_tasks(loaded.all(), due_before="2026-06-13")
    assert [task.title for task in result] == ["early"]
