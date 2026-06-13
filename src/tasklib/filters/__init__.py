"""Filter registry for tasklib.

This package is the reconciled seam that lets ``query_tasks`` and the CLI
*discover* filters instead of naming each one. A filter is a self-describing
module dropped into this package that exports a module-level ``FILTER``:

- a single :class:`FilterSpec`, or
- an iterable of :class:`FilterSpec` (for a module that ships more than one,
  e.g. ``due`` ships both ``overdue`` and ``due_before``).

Discovery walks this package's own directory with :func:`pkgutil.iter_modules`
and imports each sibling module with :mod:`importlib`. **Adding a filter
requires zero edits to any existing file** — dropping a new ``*.py`` here is
enough. See ``specs/F-001-parallel-filters`` (ADR-001) for the rationale.
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from tasklib.models import Task


@dataclass(frozen=True)
class FilterSpec:
    """A self-describing task filter.

    Attributes:
        name: Keyword used to invoke the filter, e.g.
            ``query_tasks(**{name: value})``. Must be unique across filters.
        cli_flag: The CLI flag that drives it, e.g. ``"--label"``.
        help: Help text shown on the CLI.
        takes_value: ``True`` if the flag carries a value; ``False`` for a
            boolean (``store_true``) flag.
        predicate: ``predicate(task, value) -> bool`` — keep the task when it
            returns ``True``. For a value flag, ``value`` is the supplied value;
            for a boolean flag the predicate is only consulted when the flag is
            set.
    """

    name: str
    cli_flag: str
    help: str
    takes_value: bool
    predicate: Callable[["Task", object], bool] = field(compare=False)


# Memoized discovery result: name -> FilterSpec.
_REGISTRY: dict[str, FilterSpec] | None = None


def _coerce(found: object) -> list[FilterSpec]:
    """Normalize a module's ``FILTER`` export to a list of specs."""
    if isinstance(found, FilterSpec):
        return [found]
    return list(found)  # any iterable of FilterSpec


def discover(*, force: bool = False) -> dict[str, FilterSpec]:
    """Discover and return all registered filters, keyed by name.

    The walk is memoized; pass ``force=True`` to re-scan (used by tests that
    drop a filter module in at runtime).

    Raises:
        ValueError: If two filters declare the same ``name``.
    """
    global _REGISTRY
    if _REGISTRY is not None and not force:
        return _REGISTRY

    found: dict[str, FilterSpec] = {}
    for info in pkgutil.iter_modules(__path__, prefix=f"{__name__}."):
        module = importlib.import_module(info.name)
        if not hasattr(module, "FILTER"):
            continue
        for spec in _coerce(module.FILTER):
            if spec.name in found:
                raise ValueError(f"duplicate filter name: {spec.name!r}")
            found[spec.name] = spec

    _REGISTRY = found
    return _REGISTRY


def registry() -> list[FilterSpec]:
    """Return all registered filter specs in a stable, name-sorted order."""
    return [discover()[name] for name in sorted(discover())]


def get(name: str) -> FilterSpec | None:
    """Return the filter named ``name``, or ``None`` if there is no such filter."""
    return discover().get(name)


__all__ = ["FilterSpec", "discover", "registry", "get"]
