# tasklib

A tiny, dependency-free task manager: a small core library plus an `argparse`
command-line interface. Pure Python standard library (3.11+); the only dev
dependency is `pytest`.

## Install

```bash
pip install -e .[dev]
```

## Library

```python
from tasklib import Task, TaskStore, query_tasks

store = TaskStore()
store.add("write report")
store.add("review PR")
store.complete(1)

# Filter: completion status and/or case-insensitive title substring.
open_tasks = query_tasks(store.all(), done=False)
review = query_tasks(store.all(), contains="review")
```

## CLI

State is persisted to `~/.tasklib.json` by default; override it with `--store`.

```bash
# Add tasks
tasklib add "write report"
tasklib add "review PR"

# List (optionally filter by status and/or title substring)
tasklib list
tasklib list --undone
tasklib list --done
tasklib list --contains report

# Complete and remove by id
tasklib done 1
tasklib rm 2

# Use a custom store file
tasklib --store ./mytasks.json add "buy milk"
```

Each `list` row is rendered as `[ ] <id>: <title>`, where `x` marks a completed
task.

## Roadmap

The following features are **planned but not yet implemented**:

- **Due dates** — an optional deadline per task, with filtering for overdue and
  upcoming items.
- **Labels** — free-form tags on tasks, with filtering by label.

Both will extend the existing model and `query_tasks` filters.

## Development

```bash
pip install -e .[dev]
pytest -q
```
