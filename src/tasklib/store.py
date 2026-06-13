"""In-memory task collection with JSON persistence.

``TaskStore`` owns a list of :class:`~tasklib.models.Task` objects and assigns
auto-incrementing ids. Persistence is plain JSON built from
``Task.to_dict`` / ``Task.from_dict``.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from tasklib.errors import TaskNotFound
from tasklib.models import Task


class TaskStore:
    """A mutable collection of tasks with stable, auto-incrementing ids."""

    def __init__(self) -> None:
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add(self, title: str) -> Task:
        """Create a new task with today's date and append it to the store.

        Args:
            title: Human-readable description of the task.

        Returns:
            The newly created :class:`Task`.
        """
        task = Task(
            id=self._next_id,
            title=title,
            done=False,
            created_at=date.today().isoformat(),
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task:
        """Return the task with ``task_id``.

        Raises:
            TaskNotFound: If no task has that id.
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise TaskNotFound(task_id)

    def all(self) -> list[Task]:
        """Return all tasks as a new list (insertion order)."""
        return list(self._tasks)

    def complete(self, task_id: int) -> Task:
        """Mark the task with ``task_id`` as done and return it.

        Raises:
            TaskNotFound: If no task has that id.
        """
        task = self.get(task_id)
        task.done = True
        return task

    def delete(self, task_id: int) -> None:
        """Remove the task with ``task_id`` from the store.

        Raises:
            TaskNotFound: If no task has that id.
        """
        task = self.get(task_id)
        self._tasks.remove(task)

    def save(self, path: str | Path) -> None:
        """Write all tasks to ``path`` as a JSON array.

        Args:
            path: Destination file path.
        """
        payload = [task.to_dict() for task in self._tasks]
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "TaskStore":
        """Load a store from a JSON file written by :meth:`save`.

        A missing file yields an empty store. The next id is set just past the
        highest id found so future adds never collide with loaded tasks.

        Args:
            path: Source file path.

        Returns:
            A populated :class:`TaskStore`.
        """
        store = cls()
        file_path = Path(path)
        if not file_path.exists():
            return store

        raw = json.loads(file_path.read_text(encoding="utf-8"))
        store._tasks = [Task.from_dict(item) for item in raw]
        store._next_id = max((task.id for task in store._tasks), default=0) + 1
        return store
