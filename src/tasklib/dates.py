"""Date helpers for tasklib.

Dates are ISO date strings (``YYYY-MM-DD``). Lexicographic comparison of two
well-formed ISO dates matches chronological order, so comparisons here are plain
string comparisons against today's date.
"""

from __future__ import annotations

from datetime import date


def is_overdue(due: str | None, today: str | None = None) -> bool:
    """Return ``True`` if ``due`` is strictly before ``today``.

    Args:
        due: An ISO date string (``YYYY-MM-DD``), or ``None`` for no due date.
        today: ISO date string to compare against; defaults to the current date.

    Returns:
        ``True`` when ``due`` is set and falls before ``today``; otherwise
        ``False`` (a task with no due date is never overdue).
    """
    if due is None:
        return False
    reference = today if today is not None else date.today().isoformat()
    return due < reference
