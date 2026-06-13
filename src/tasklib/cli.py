"""Command-line interface for tasklib.

Subcommands:

- ``add <title>``                       create a task
- ``list [--done/--undone] [--contains TEXT]``  list tasks, optionally filtered
- ``done <id>``                         mark a task complete
- ``rm <id>``                           delete a task

State is persisted as JSON. The path defaults to ``~/.tasklib.json`` and can be
overridden with ``--store``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tasklib import __version__
from tasklib.errors import TaskNotFound
from tasklib.models import Task
from tasklib.query import query_tasks
from tasklib.store import TaskStore

DEFAULT_STORE = Path.home() / ".tasklib.json"


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="tasklib",
        description="A tiny task manager.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=DEFAULT_STORE,
        help=f"Path to the JSON store (default: {DEFAULT_STORE}).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    add_cmd = sub.add_parser("add", help="Add a new task.")
    add_cmd.add_argument("title", help="Title of the task.")

    list_cmd = sub.add_parser("list", help="List tasks.")
    status = list_cmd.add_mutually_exclusive_group()
    status.add_argument(
        "--done",
        dest="done",
        action="store_const",
        const=True,
        default=None,
        help="Show only completed tasks.",
    )
    status.add_argument(
        "--undone",
        dest="done",
        action="store_const",
        const=False,
        help="Show only tasks that are not done.",
    )
    list_cmd.add_argument(
        "--contains",
        default=None,
        help="Show only tasks whose title contains this text.",
    )

    done_cmd = sub.add_parser("done", help="Mark a task as complete.")
    done_cmd.add_argument("id", type=int, help="Id of the task to complete.")

    rm_cmd = sub.add_parser("rm", help="Delete a task.")
    rm_cmd.add_argument("id", type=int, help="Id of the task to delete.")

    return parser


def _format_task(task: Task) -> str:
    """Render a single task as a one-line string for the CLI."""
    mark = "x" if task.done else " "
    return f"[{mark}] {task.id}: {task.title}"


def main(argv: list[str] | None = None) -> int:
    """Run the CLI.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]`` when ``None``).

    Returns:
        Process exit code: ``0`` on success, ``1`` on a known user error.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    store = TaskStore.load(args.store)

    if args.command == "add":
        task = store.add(args.title)
        store.save(args.store)
        print(f"Added {_format_task(task)}")
        return 0

    if args.command == "list":
        tasks = query_tasks(store.all(), done=args.done, contains=args.contains)
        for task in tasks:
            print(_format_task(task))
        return 0

    if args.command == "done":
        try:
            task = store.complete(args.id)
        except TaskNotFound as exc:
            print(exc, flush=True)
            return 1
        store.save(args.store)
        print(f"Completed {_format_task(task)}")
        return 0

    if args.command == "rm":
        try:
            store.delete(args.id)
        except TaskNotFound as exc:
            print(exc, flush=True)
            return 1
        store.save(args.store)
        print(f"Removed task {args.id}")
        return 0

    # argparse enforces a valid subcommand, so this is unreachable.
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
