# F-001 Parallel Filters — Tasks

- Feature ID: F-001
- Status: approved

Each task lists the requirements it satisfies (R-) and the verification IDs
(T-) that check it. Tasks are ordered so the reconciled base lands first and the
two feature files land independently on top of it.

## Reconciled base (branch `reforge/reconciled-base`)

- TK-1 — Extend `Task` with `due` and `labels`; update `to_dict`/`from_dict`
  with backward-compatible reads. (R-001, R-002, R-003) → T-001, T-002, T-003
- TK-2 — Add `tasklib/filters/__init__.py`: `FilterSpec` value object plus
  `pkgutil`/`importlib` discovery and an ordered `registry()`. (R-004, R-005)
  → T-004, T-005
- TK-3 — Refactor `query_tasks` to keep `done`/`contains` and apply registered
  filters from `**kwargs`; preserve order and backward compatibility.
  (R-006, R-007) → T-006, T-007
- TK-4 — Make `list` auto-add a CLI flag per registered filter and forward the
  values to `query_tasks`. (R-008, R-009) → T-008, T-009
- TK-5 — Add `tests/test_registry.py`; keep all base tests green. (R-004..R-009)
  → T-004 .. T-009

## Akash feature (branch `akash/due-dates-reforged`, new files only)

- TK-6 — Add `tasklib/filters/due.py` exporting a `FILTER` for `overdue` and
  `due_before`, reusing `tasklib.dates.is_overdue`. Add
  `tests/test_filter_due.py`. Edit no existing file. (R-010) → T-010, T-006

## Shine feature (branch `shine/labels-reforged`, new files only)

- TK-7 — Add `tasklib/filters/labels.py` exporting a `FILTER` for `label`,
  reusing `tasklib.labels.normalize_label`. Add `tests/test_filter_labels.py`.
  Edit no existing file. (R-010) → T-010, T-006

## Merge demonstration

- TK-8 — Merge `shine/labels-reforged` into `akash/due-dates-reforged`; expect
  zero conflicts and all tests passing. (R-010) → verification.md
