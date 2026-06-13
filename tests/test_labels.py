"""Tests for Shine's labels feature: model field, helper, query, CLI."""

from __future__ import annotations

from pathlib import Path

from tasklib.labels import normalize_label
from tasklib.models import Task
from tasklib.query import query_tasks


def _sample() -> list[Task]:
    return [
        Task(id=1, title="write report", labels=["work", "urgent"]),
        Task(id=2, title="review PR", labels=["work"]),
        Task(id=3, title="buy milk", labels=["home"]),
        Task(id=4, title="no labels", labels=[]),
    ]


def _ids(tasks: list[Task]) -> list[int]:
    return [task.id for task in tasks]


def test_task_labels_default_to_empty_list() -> None:
    assert Task(id=1, title="x").labels == []


def test_task_labels_are_independent_per_instance() -> None:
    a = Task(id=1, title="a")
    b = Task(id=2, title="b")
    a.labels.append("work")
    assert b.labels == []


def test_labels_round_trip_through_dict() -> None:
    task = Task(id=9, title="ship", created_at="2026-06-13", labels=["a", "b"])
    assert task.to_dict()["labels"] == ["a", "b"]
    assert Task.from_dict(task.to_dict()) == task


def test_from_dict_without_labels_defaults_to_empty() -> None:
    data = {"id": 1, "title": "legacy", "done": False, "created_at": "2026-01-01"}
    assert Task.from_dict(data).labels == []


def test_normalize_label_trims_and_lowercases() -> None:
    assert normalize_label("  Work  ") == "work"
    assert normalize_label("URGENT") == "urgent"


def test_query_label_matches() -> None:
    assert _ids(query_tasks(_sample(), label="work")) == [1, 2]


def test_query_label_is_normalized() -> None:
    assert _ids(query_tasks(_sample(), label="  WORK ")) == [1, 2]


def test_query_label_no_match_is_empty() -> None:
    assert query_tasks(_sample(), label="missing") == []


def test_cli_add_with_labels_and_list_by_label(tmp_path: Path) -> None:
    from tasklib.cli import main

    store = tmp_path / "tasks.json"
    code = main(
        ["--store", str(store), "add", "report", "--label", "work", "--label", "urgent"]
    )
    assert code == 0
    assert main(["--store", str(store), "add", "milk", "--label", "home"]) == 0

    loaded = __import__("tasklib.store", fromlist=["TaskStore"]).TaskStore.load(store)
    by_title = {task.title: task.labels for task in loaded.all()}
    assert by_title == {"report": ["work", "urgent"], "milk": ["home"]}

    result = query_tasks(loaded.all(), label="work")
    assert [task.title for task in result] == ["report"]
