# F-001 Parallel Filters — Requirements

- Feature ID: F-001
- Title: Parallel, conflict-free task filters (due dates + labels)
- Status: approved
- Owners: Akash (due dates), Shine (labels)
- Reconciled by: re-forge spec-sync

## Problem

Two developers add overlapping features to `tasklib` in parallel:

- Akash adds **due dates**: a `due` field on `Task` plus `overdue` and
  `due_before` filtering.
- Shine adds **labels**: a `labels` field on `Task` plus filtering by `label`.

Both target the same two shared symbols — the `Task` dataclass and the
`query_tasks` function (and the `list` CLI command that calls it). Edited in
place, their changes collide on a git merge. re-forge's spec-sync observed both
contracts up front and reconciled them into one shared schema plus an extensible
filter seam, so each feature becomes an isolated new file.

## EARS requirements

R-001 (ubiquitous): The `Task` record SHALL carry both a `due` field
(ISO date string `YYYY-MM-DD`, default `None`) and a `labels` field
(list of strings, default empty), in one agreed schema.

R-002 (ubiquitous): `Task.to_dict` and `Task.from_dict` SHALL round-trip both
`due` and `labels` without loss.

R-003 (event-driven): WHEN a JSON record produced before a field existed is
loaded, the system SHALL default the missing `due` to `None` and the missing
`labels` to an empty list (backward-compatible reads).

R-004 (ubiquitous): The system SHALL provide a filter registry that discovers
filters from modules dropped into the `tasklib.filters` package, requiring ZERO
edits to existing modules to add a new filter.

R-005 (ubiquitous): Each registered filter SHALL declare a stable name, a CLI
flag, help text, whether it takes a value, and a predicate
`predicate(task, value) -> bool`.

R-006 (event-driven): WHEN `query_tasks` is called with a registered filter's
name as a keyword argument, the system SHALL apply that filter's predicate,
combined with the existing filters using AND.

R-007 (ubiquitous): `query_tasks` SHALL preserve its existing `done` and
`contains` behavior and its input order, and SHALL remain backward compatible so
all pre-existing tests pass unchanged.

R-008 (event-driven): WHEN the `list` CLI command runs, the system SHALL expose
one CLI flag per registered filter (discovered from the registry) and forward
provided values to `query_tasks`.

R-009 (state-driven): WHILE no value is supplied for a value-taking filter, the
system SHALL treat that filter as inactive (it does not remove any task).

R-010 (ubiquitous): Adding the **due** feature and the **labels** feature SHALL
each be achievable by adding exactly one new file under `tasklib/filters/`
(plus its test), touching no shared file — so two such features merge with zero
conflicts.

## Acceptance criteria

- AC-1 → R-001/R-002/R-003: `Task` exposes `due` and `labels`; dict round-trip
  is identity; legacy dicts load with defaults.
- AC-2 → R-004/R-005: dropping a `*.py` file exporting a `FILTER` into
  `tasklib/filters/` registers it with no other edit.
- AC-3 → R-006/R-007: `query_tasks(**{name: value})` applies the named filter;
  all 24 base tests stay green.
- AC-4 → R-008/R-009: `tasklib list` gains a flag per filter and forwards it.
- AC-5 → R-010: `due.py` and `labels.py` are added independently and their
  branches merge with zero conflicts and all tests passing.

## Out of scope

- Sorting, due-date arithmetic beyond a strict before-comparison, label
  management commands (rename/delete), and persistence format changes beyond the
  two additive fields.
