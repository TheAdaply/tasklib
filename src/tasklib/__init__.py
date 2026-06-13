"""tasklib: a tiny, dependency-free task manager core library and CLI.

The public API is intentionally small:

- :class:`Task` -- a single task record.
- :class:`TaskStore` -- an in-memory collection of tasks with JSON persistence.
- :func:`query_tasks` -- filter a list of tasks by completion status or title.
"""

from tasklib.models import Task
from tasklib.query import query_tasks
from tasklib.store import TaskStore

__version__ = "0.1.0"

__all__ = ["Task", "TaskStore", "query_tasks", "__version__"]
