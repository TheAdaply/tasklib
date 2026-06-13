# Measurement — NAIVE vs RE-FORGE (tasklib parallel-filters demo)

Two developers add overlapping features to `tasklib` in parallel:

- **Akash** — due dates: `Task.due` + `overdue` / `due_before` filtering.
- **Shine** — labels: `Task.labels` + `label` filtering.

Both target the same shared symbols (`Task`, `query_tasks`, the `list` CLI). The
demo runs the same two features two ways and measures the merge.

All numbers below are hard counts taken from real git merges in this repo. No
time figures are modeled here. Base repo: commit `cf854e8`, 24 passing tests.

## Methodology (reproducible)

- **NAIVE.** Branch `akash/due-dates` and `shine/labels` both fork from `main`
  (`cf854e8`) and edit the shared files in place. Merge captured verbatim in
  `runs/naive-merge.txt` via:
  `git checkout akash/due-dates && git merge --no-ff --no-commit shine/labels`.
  - Conflicted files = `git diff --name-only --diff-filter=U | wc -l`.
  - Conflict hunks = total count of `^<<<<<<<` markers across the conflicted
    files (each `<<<<<<<` is balanced by one `=======` and one `>>>>>>>`;
    counts verified equal at 13/13/13).
  - Conflicted lines = lines inside conflict regions, counted from each
    `<<<<<<<` through its matching `>>>>>>>` inclusive, summed across files.
  - The merge was then aborted (`git merge --abort`); nothing was committed.

- **RE-FORGE.** re-forge's spec-sync reconciles the two contracts first
  (`specs/F-001-parallel-filters/`): one shared `Task` schema carrying both
  fields, plus a filter **registry** (`tasklib/filters/`) so each new filter is
  an isolated new file. The reconciled seam lands once on
  `reforge/reconciled-base`. Each feature is then a single new file added on its
  own branch (`akash/due-dates-reforged`, `shine/labels-reforged`), forked
  independently from the reconciled base. Merge captured verbatim in
  `runs/reforged-merge.txt` via:
  `git checkout akash/due-dates-reforged && git merge --no-ff shine/labels-reforged`,
  then `pytest -q` on the merged branch.

## Results

| Metric | NAIVE | RE-FORGE |
|---|---|---|
| Branch fork point | `main` (`cf854e8`) | `reforge/reconciled-base` (`98a50d0`) |
| Files each feature edits | shared files, in place | one new file under `tasklib/filters/` |
| Merge command exit code | `1` (failed) | `0` (clean) |
| Conflicted files | **4** | **0** |
| Conflict hunks (`<<<<<<<` count) | **13** | **0** |
| Conflicted lines (in markers) | **102** | **0** |
| Human must resolve by hand | **Yes** | No |
| Re-test required after manual fixup | **Yes** | (merge is already green) |
| Tests passing on the merged branch | n/a — merge aborted, never integrated | **53** |

### NAIVE — per-file conflict breakdown

| File | Conflict hunks | Conflicted lines |
|---|---|---|
| `src/tasklib/cli.py` | 4 | 37 |
| `src/tasklib/models.py` | 4 | 20 |
| `src/tasklib/query.py` | 4 | 40 |
| `tests/test_models.py` | 1 | 5 |
| **Total** | **13** | **102** |

The naive merge leaves the tree in an unmerged state: the two features collide
on every shared symbol they both touched (the `Task` field list, `to_dict` /
`from_dict`, the `query_tasks` signature and filter block, the CLI flags, and the
`to_dict` model test). A human must hand-resolve all 13 hunks and then re-run the
suite before anything is mergeable.

### RE-FORGE — clean integration

The reconciled features land on disjoint files
(`tasklib/filters/due.py` vs `tasklib/filters/labels.py`, plus their separate
test files), so git merges them with zero conflicts. The merged branch
(`ff2eed2`) carries both features and the full suite is green:

- `git merge` exit `0`, "Merge made by the 'ort' strategy", 0 conflicts.
- `pytest -q` → **53 passed** on the merged branch.
- All three filters (`due_before`, `label`, `overdue`) are registered and
  combine with AND, verified end-to-end through the CLI.

## Test-count trail (for reference)

| Branch | Tests |
|---|---|
| `main` (base) | 24 |
| `akash/due-dates` (naive) | 34 |
| `shine/labels` (naive) | 33 |
| `reforge/reconciled-base` | 36 |
| merged reforged (`ff2eed2`) | 53 |

## Artifacts

- `runs/naive-merge.txt` — verbatim naive merge: conflict messages, `git status`,
  conflicted file list, and full `git diff --diff-filter=U` conflict markers.
- `runs/reforged-merge.txt` — verbatim clean merge + `pytest -q` (53 passed).
- `specs/F-001-parallel-filters/` — the reconciling spec (requirements, design +
  ADR-001, tasks, verification).
