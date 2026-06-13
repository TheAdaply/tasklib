"""Tests for the Task data model."""

from __future__ import annotations

from tasklib.models import Task


def test_defaults() -> None:
    task = Task(id=1, title="write report")
    assert task.id == 1
    assert task.title == "write report"
    assert task.done is False
    assert task.created_at == ""


def test_to_dict_lists_every_field() -> None:
    task = Task(id=7, title="ship", done=True, created_at="2026-06-13")
    assert task.to_dict() == {
        "id": 7,
        "title": "ship",
        "done": True,
        "created_at": "2026-06-13",
        "due": None,
    }


def test_from_dict_rebuilds_task() -> None:
    data = {"id": 3, "title": "review", "done": False, "created_at": "2026-01-01"}
    task = Task.from_dict(data)
    assert task == Task(id=3, title="review", done=False, created_at="2026-01-01")


def test_round_trip_is_identity() -> None:
    task = Task(id=42, title="round trip", done=True, created_at="2026-06-13")
    assert Task.from_dict(task.to_dict()) == task
