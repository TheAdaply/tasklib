"""Tests for query_tasks filtering."""

from __future__ import annotations

from tasklib.models import Task
from tasklib.query import query_tasks


def _sample() -> list[Task]:
    return [
        Task(id=1, title="Write report", done=False),
        Task(id=2, title="Review PR", done=True),
        Task(id=3, title="write tests", done=False),
        Task(id=4, title="Deploy release", done=True),
    ]


def _ids(tasks: list[Task]) -> list[int]:
    return [task.id for task in tasks]


def test_no_filters_returns_all() -> None:
    tasks = _sample()
    assert query_tasks(tasks) == tasks


def test_no_filters_returns_a_new_list() -> None:
    tasks = _sample()
    result = query_tasks(tasks)
    assert result is not tasks
    result.clear()
    assert len(tasks) == 4


def test_filter_done_true() -> None:
    assert _ids(query_tasks(_sample(), done=True)) == [2, 4]


def test_filter_done_false() -> None:
    assert _ids(query_tasks(_sample(), done=False)) == [1, 3]


def test_filter_contains_is_case_insensitive() -> None:
    assert _ids(query_tasks(_sample(), contains="WRITE")) == [1, 3]


def test_filter_contains_matches_substring() -> None:
    assert _ids(query_tasks(_sample(), contains="re")) == [1, 2, 4]


def test_combined_filters_use_and() -> None:
    result = query_tasks(_sample(), done=False, contains="write")
    assert _ids(result) == [1, 3]


def test_combined_filters_can_be_empty() -> None:
    assert query_tasks(_sample(), done=True, contains="write") == []


def test_preserves_input_order() -> None:
    assert _ids(query_tasks(_sample(), contains="e")) == [1, 2, 3, 4]
