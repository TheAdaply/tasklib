"""Tests for the registered label filter (Shine)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tasklib import filters as filters_registry
from tasklib.cli import build_parser, main
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


def test_label_filter_is_registered() -> None:
    spec = filters_registry.get("label")
    assert spec is not None
    assert spec.takes_value is True
    assert spec.cli_flag == "--label"


def test_query_label_matches() -> None:
    assert _ids(query_tasks(_sample(), label="work")) == [1, 2]


def test_query_label_is_normalized() -> None:
    assert _ids(query_tasks(_sample(), label="  WORK ")) == [1, 2]


def test_query_label_no_match_is_empty() -> None:
    assert query_tasks(_sample(), label="missing") == []


def test_query_label_none_is_inactive() -> None:
    assert query_tasks(_sample(), label=None) == _sample()


def test_cli_list_has_label_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["list", "--label", "work"])
    assert args.label == "work"


def test_cli_list_filters_by_label(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    store = tmp_path / "tasks.json"
    from tasklib.store import TaskStore

    s = TaskStore()
    s.add("report").labels = ["work"]
    s.add("milk").labels = ["home"]
    s.save(store)

    assert main(["--store", str(store), "list", "--label", "work"]) == 0
    out = capsys.readouterr().out
    assert "report" in out
    assert "milk" not in out
