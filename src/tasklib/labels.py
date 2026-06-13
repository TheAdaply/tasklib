"""Label helpers for tasklib.

Labels are short free-form strings. ``normalize_label`` defines the single
canonical form (trimmed, lower-cased) so that lookups and equality checks are
consistent regardless of how a label was typed.
"""

from __future__ import annotations


def normalize_label(s: str) -> str:
    """Return the canonical form of a label.

    Args:
        s: A raw label as typed by a user.

    Returns:
        The label with surrounding whitespace stripped and folded to lower case.
    """
    return s.strip().lower()
