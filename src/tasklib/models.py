"""Data model for a single task.

``Task`` is a deliberate future merge point: ``to_dict`` and ``from_dict``
list every field explicitly so that adding a field is an obvious, linear
change rather than hidden behind a loop or reflection.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Task:
    """A single task.

    Attributes:
        id: Stable, unique identifier assigned by the store.
        title: Human-readable description of the task.
        done: Whether the task has been completed.
        created_at: ISO date string (``YYYY-MM-DD``) for when it was created.
        due: Optional ISO date string (``YYYY-MM-DD``) the task is due on.
    """

    id: int
    title: str
    done: bool = False
    created_at: str = ""
    due: str | None = None

    def to_dict(self) -> dict:
        """Serialize this task to a plain JSON-compatible dict.

        Each field is listed explicitly so the mapping stays obvious.
        """
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "created_at": self.created_at,
            "due": self.due,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        """Build a :class:`Task` from a dict produced by :meth:`to_dict`.

        Each field is read explicitly so the mapping stays obvious.
        """
        return cls(
            id=d["id"],
            title=d["title"],
            done=d["done"],
            created_at=d["created_at"],
            due=d.get("due"),
        )
