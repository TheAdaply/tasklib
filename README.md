# tasklib

A tiny, dependency-free Python task manager: a small core library plus an `argparse`
CLI (standard library only, 3.11+; the only dev dependency is `pytest`). It is also a
**live, reproducible demo of [re-forge](https://re-forge.vercel.app) Team Sync** — what
happens when two developers add overlapping features in parallel, with and without a
shared spec + memory layer.

> **Watch the 50-second demo:** https://re-forge.vercel.app/team-sync.html

## The demo: two parallel features, one shared file

Two developers branch from `main` at the same moment, neither aware of the other:

| Developer | Branch | Feature | Touches |
|---|---|---|---|
| **Akash** | `akash/due-dates` | due dates + `overdue` / `due_before` filters | `Task`, `query_tasks()` |
| **Shine** | `shine/labels` | labels + filter by `label` | `Task`, `query_tasks()` |

Both independently extend the **same** `Task` dataclass and the **same**
`query_tasks()` function.

### Path A — the naive merge (what usually happens)

```bash
git checkout akash/due-dates
git merge shine/labels        # CONFLICT
```

Measured result (see [`runs/naive-merge.txt`](runs/naive-merge.txt)):

| naive merge | |
|---|---|
| conflicted files | **4** (`models.py`, `query.py`, `cli.py`, `tests/test_models.py`) |
| conflict hunks | **13** |
| conflicting lines | **102** |

A human now hand-resolves 13 hunks, reconciles the `Task` schema and the `query_tasks`
signature by hand, rebases, and re-runs the suite.

### Path B — re-forge reconciles the contract first

re-forge's shared spec + memory layer sees that **both** intents target `Task` and
`query_tasks`, and reconciles them *before* code is written: one agreed `Task` schema
(carrying both `due` and `labels`) plus a **filter registry**, so each feature becomes a
single isolated new file. The frozen contract is in
[`specs/F-001-parallel-filters/`](specs/F-001-parallel-filters/).

```bash
git checkout akash/due-dates-reforged
git merge shine/labels-reforged   # clean
python -m pytest -q               # 53 passed
```

Measured result (see [`runs/reforged-merge.txt`](runs/reforged-merge.txt) and
[`runs/MEASUREMENT.md`](runs/MEASUREMENT.md)):

| re-forge reconciled | |
|---|---|
| conflicts | **0** |
| tests passing | **53** |
| rebase / debug cycles | **0** |

The eliminated resolve-rebase-retest loop is, conservatively, **~25-45 minutes per
overlapping feature pair** (*modeled*, not measured). Across a team merging many such
pairs a week, it compounds.

### Branch map

```
main ...................... base tasklib (where both devs start)
 |- akash/due-dates ....... naive feature A  -.  merge -> CONFLICT
 \- shine/labels .......... naive feature B  -'
reforge/reconciled-base ... shared Task schema + filter registry (re-forge's seam)
 |- akash/due-dates-reforged  feature A as one isolated file  -.  merge -> CLEAN
 \- shine/labels-reforged .. feature B as one isolated file  -'
```

### Honest notes

- The conflict counts and the 53 passing tests are **measured** from real `git merge`
  runs in this repo. The minutes-saved figure is a **conservative model**, labeled as
  such.
- re-forge is **non-blocking**: it surfaces the overlap and proposes reconciled
  contracts. It does not forcibly block a merge or claim runtime authority.

---

## Using tasklib

### Install

```bash
pip install -e .[dev]
```

### Library

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

### CLI

State persists to `~/.tasklib.json` by default (override with `--store`):

```bash
tasklib add "write report"
tasklib list --undone
tasklib list --contains report
tasklib done 1
tasklib rm 2
```

### Tests

```bash
python -m pytest -q
```

---

Built with [re-forge](https://github.com/Akasxh/re-forge) — the model- and
tool-agnostic memory, skill, and audit layer for AI coding agents.
