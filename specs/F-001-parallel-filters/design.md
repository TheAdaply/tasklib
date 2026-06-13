# F-001 Parallel Filters — Design

- Feature ID: F-001
- Status: approved
- Traces: R-001 .. R-010

## Reconciliation summary (what spec-sync produced)

spec-sync diffed the two in-flight contracts and found both Akash and Shine
targeting the **same two shared symbols**: the `Task` dataclass and the
`query_tasks` function (plus the `list` CLI that calls it). Editing those in
place guarantees a merge collision. The reconciliation has two moves:

1. **One agreed `Task` schema** carrying BOTH new fields. Instead of two
   competing single-field edits to the same lines, the reconciled base adds
   `due` and `labels` together, once. Both developers build on this schema; the
   shared symbol is touched exactly once, by the reconciled base, not by either
   feature branch.

2. **A filter registry** so `query_tasks` and the CLI auto-discover filters from
   a `tasklib/filters/` package. After the reconciled base lands, a new filter
   is an ISOLATED new file dropped into `tasklib/filters/`. Neither
   `query_tasks` nor `cli.py` is edited again to add a filter, so two new
   filters land on disjoint files and merge cleanly.

## Components

### Shared `Task` schema (models.py) — R-001, R-002, R-003

`Task` gains `due: str | None = None` and
`labels: list[str] = field(default_factory=list)`. `to_dict` emits both keys;
`from_dict` reads them with defaults (`d.get("due")`, `d.get("labels", [])`) so
records written before a field existed still load (R-003).

### Filter registry (tasklib/filters/__init__.py) — R-004, R-005

A tiny value object describes a filter:

```text
FilterSpec(
    name: str,                  # keyword used in query_tasks(**{name: value})
    cli_flag: str,              # e.g. "--label"
    help: str,
    takes_value: bool,          # value flag vs boolean store_true flag
    predicate: Callable[[Task, value], bool],
)
```

Each filter module exports a module-level `FILTER` (a `FilterSpec`, or an
iterable of them for modules that ship more than one — e.g. due ships
`overdue` + `due_before`). The package walks its own directory with
`pkgutil.iter_modules`, imports each sibling module with `importlib`, and
collects every `FILTER` it finds into an ordered registry keyed by `name`.
`discover()` is idempotent and memoized; `registry()` returns the specs in a
stable (sorted-by-name) order so CLI flags and query application are
deterministic. **Adding a filter requires zero edits here** (R-004): the walk
finds any new module automatically.

### query_tasks application (query.py) — R-006, R-007

`query_tasks` keeps its literal `done` and `contains` blocks (so existing tests
are untouched) and then, for any extra `**kwargs`, looks each key up in the
registry by `name` and applies its predicate. A value-taking filter is inactive
when its value is `None`; a boolean filter is inactive when falsy (R-009).
Unknown kwargs raise `TypeError`, matching normal Python call semantics.

### CLI integration (cli.py) — R-008, R-009

`build_parser` iterates `registry()` and adds one argument per filter to the
`list` subcommand: `store_true` when `takes_value` is false, else a value
option. `main` collects those values back out of the parsed args (by each
filter's `name`) and forwards them to `query_tasks`. New filters appear on the
CLI automatically.

### Feature files (added on top of the reconciled base) — R-010

- `tasklib/filters/due.py`: exports a `FILTER` list of two specs — `overdue`
  (boolean) and `due_before` (value) — reusing `tasklib.dates.is_overdue`.
- `tasklib/filters/labels.py`: exports a `FILTER` for `label` (value), reusing
  `tasklib.labels.normalize_label`.

Each is a brand-new file. Two such files share no lines, so their branches
merge with zero conflicts (R-010).

## ADR-001: filter registry over inline `if` chain

- **Context.** The base `query_tasks` is a linear `if param is not None:` chain
  and the CLI hand-declares each flag. Both are shared edit points; every new
  filter touches them, so parallel features collide there.
- **Decision.** Invert the dependency: make filters self-describing modules and
  have `query_tasks`/CLI *discover* them. The shared code iterates the registry
  instead of naming each filter.
- **Consequences.** (+) New filters are isolated new files — parallel work no
  longer collides; the CLI and query layer never change to add a filter.
  (+) The seam is explicit and testable (`tests/test_registry.py`).
  (-) One indirection (registry lookup) and a small import-time directory walk.
  (-) Discovery is dynamic, so a malformed filter module fails at import — an
  acceptable, loud trade for a stdlib-only plugin seam.
- **Alternatives rejected.** Keep the inline chain (rejected: the collision is
  the problem we are removing). An external entry-point/plugin system (rejected:
  pulls in packaging machinery; `tasklib` is deliberately dependency-free and
  the in-package `pkgutil` walk is enough).

## Traceability

| Requirement | Design element | Verified by |
|-------------|----------------|-------------|
| R-001/002/003 | Shared `Task` schema | T-001, T-002, T-003 |
| R-004/005 | `FilterSpec` + discovery | T-004, T-005 |
| R-006/007 | `query_tasks` registry application | T-006, T-007 |
| R-008/009 | CLI flag-per-filter | T-008, T-009 |
| R-010 | One-file feature modules | T-010 |
