"""Tests for TaskStore: CRUD, errors, and JSON persistence."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tasklib.errors import TaskNotFound
from tasklib.store import TaskStore


def test_add_assigns_incrementing_ids_and_today() -> None:
    store = TaskStore()
    first = store.add("write report")
    second = store.add("review PR")

    assert first.id == 1
    assert second.id == 2
    assert first.done is False
    assert first.created_at == date.today().isoformat()


def test_get_returns_matching_task() -> None:
    store = TaskStore()
    task = store.add("write report")
    assert store.get(task.id) is task


def test_get_missing_raises_with_id() -> None:
    store = TaskStore()
    with pytest.raises(TaskNotFound) as excinfo:
        store.get(99)
    assert excinfo.value.task_id == 99
    assert "99" in str(excinfo.value)


def test_all_returns_a_copy_in_insertion_order() -> None:
    store = TaskStore()
    store.add("a")
    store.add("b")

    tasks = store.all()
    assert [task.title for task in tasks] == ["a", "b"]

    # Mutating the returned list must not affect the store.
    tasks.clear()
    assert len(store.all()) == 2


def test_complete_marks_done() -> None:
    store = TaskStore()
    task = store.add("write report")
    assert task.done is False

    returned = store.complete(task.id)
    assert returned is task
    assert task.done is True


def test_complete_missing_raises() -> None:
    store = TaskStore()
    with pytest.raises(TaskNotFound):
        store.complete(1)


def test_delete_removes_task() -> None:
    store = TaskStore()
    task = store.add("write report")
    store.delete(task.id)

    assert store.all() == []
    with pytest.raises(TaskNotFound):
        store.get(task.id)


def test_delete_missing_raises() -> None:
    store = TaskStore()
    with pytest.raises(TaskNotFound):
        store.delete(1)


def test_save_load_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    store = TaskStore()
    store.add("write report")
    completed = store.add("review PR")
    store.complete(completed.id)
    store.save(path)

    loaded = TaskStore.load(path)
    assert loaded.all() == store.all()


def test_load_missing_file_returns_empty_store(tmp_path: Path) -> None:
    loaded = TaskStore.load(tmp_path / "does-not-exist.json")
    assert loaded.all() == []


def test_load_continues_id_sequence(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    store = TaskStore()
    store.add("a")
    store.add("b")  # highest id == 2
    store.save(path)

    loaded = TaskStore.load(path)
    new_task = loaded.add("c")
    assert new_task.id == 3
