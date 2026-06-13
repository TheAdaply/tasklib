# F-001 Parallel Filters — Verification

- Feature ID: F-001
- Status: approved

Evidence that each requirement is met. Test IDs (T-) map to concrete tests in
the suite. The merge demonstration is the load-bearing claim: two filter
features land on disjoint files and merge with zero conflicts.

## Test traceability

| Test | Requirement | Where |
|------|-------------|-------|
| T-001 | R-001 | `tests/test_registry.py::test_task_has_due_and_labels` |
| T-002 | R-002 | `tests/test_registry.py::test_task_dict_round_trip_both_fields` |
| T-003 | R-003 | `tests/test_registry.py::test_from_dict_legacy_defaults` |
| T-004 | R-004 | `tests/test_registry.py::test_registry_discovers_dropped_in_filter` |
| T-005 | R-005 | `tests/test_registry.py::test_filterspec_fields_present` |
| T-006 | R-006 | `tests/test_registry.py::test_query_applies_registered_filter` and the per-feature filter tests |
| T-007 | R-007 | the 24 pre-existing base tests, unchanged |
| T-008 | R-008 | `tests/test_registry.py::test_cli_list_exposes_flag_per_filter` |
| T-009 | R-009 | `tests/test_registry.py::test_cli_value_filter_inactive_when_absent` |
| T-010 | R-010 | merge demonstration below + `tests/test_filter_due.py`, `tests/test_filter_labels.py` |

## Backward compatibility (R-007)

The reconciled base keeps the literal `done` and `contains` blocks in
`query_tasks` and only adds registry application afterward. The 24 base tests in
`test_models.py`, `test_query.py`, and `test_store.py` pass unchanged on
`reforge/reconciled-base`.

## Merge demonstration (R-010) — primary evidence

Procedure (captured verbatim in `runs/reforged-merge.txt`):

```
git checkout akash/due-dates-reforged
git merge --no-ff shine/labels-reforged   ; echo "exit=$?"
git status
uv run --with pytest --python 3.11 python -m pytest -q
```

Result: merge exit `0`, zero conflicted files, clean working tree, and the full
suite green on the merged branch. Contrast: the naive in-place approach
(`runs/naive-merge.txt`) collides on 4 files / 13 hunks. Hard counts are
recorded in `runs/MEASUREMENT.md`.

Because `tasklib/filters/due.py` and `tasklib/filters/labels.py` are each
brand-new files that share no lines and touch no shared module, git merges them
without conflict — satisfying R-010.
