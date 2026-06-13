"""Exceptions raised by tasklib."""

from __future__ import annotations


class TaskNotFound(Exception):
    """Raised when a task id does not exist in the store.

    The offending id is kept on the exception so callers can inspect it.
    """

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"No task with id {task_id}")
