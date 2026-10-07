# F3 — Audit

This folder holds everything needed to **rerun F3's audits of external models** and get the same results. It implements Phase 1, steps 1.0 and 1.1, of [the Phase 1 plan](../docs/phase-1-plan.md).

## How audits run

Audits run on **GitHub Actions**, not on anyone's personal machine, so every run is public, logged and reproducible.

To run T0: open the repository's **Actions** tab, select **Audit T0 — reference sanity check**, click **Run workflow**, leave the ref box empty (Earth4All.jl's default branch is `master`) and confirm. A run takes roughly 20–60 minutes; most of that time is Julia installing and compiling packages.

Results appear in two places:

- **The run page summary:** the reports, readable directly in the browser.
- **The `audit-t0-results` artifact:** a zip with all data files (CSV), figures (HTML/PNG) and the exact package versions used. Kept for 90 days; results from approved runs are archived in the repository.

## What T0 does

| Step | Reference | Checks |
|---|---|---|
| T0.1 | WorldDynamics.jl v1.0.0 (MIT) | Solves the World3 standard run (1900–2100), exports its states, regenerates the book's Figure 7.7 |
| T0.2 | Earth4All.jl (MIT), as published | Solves "Too Little Too Late" and "Giant Leap", exports states, regenerates the comparison figures against Vensim |
| T0.3 | PyWorld3 (CeCILL 2.1), installed unmodified | Solves the World3 standard run as an independent second check |
| T0.4 | — | Compares World3 population between WorldDynamics.jl and PyWorld3 (informational) |

Each step is isolated: if one fails, the others still run and the report shows ❌ with the error. **A green run does not mean every check passed; read the report.**

T0 is also a **discovery run**. It records the variable and function names each reference model exposes. Tests T1–T4 will be written against those real names.

## Rules (from DECISIONS.md)

- External models are **never copied into this repository**. They are installed or cloned during the run (D-001, D-011).
- Earth4All.jl's `vensim_source` folder is never used or copied (D-011).
- Every reference is pinned to an exact version or commit, recorded in [REFERENCES.md](REFERENCES.md).

## Contents

```
audit/
├── README.md          this file
├── REFERENCES.md      pinned versions of every external model
├── t0/
│   ├── world3_t0.jl       T0.1
│   ├── earth4all_t0.jl    T0.2
│   ├── pyworld3_t0.py     T0.3
│   └── compare_world3.py  T0.4
└── env/               Pinned Julia environment for WorldDynamics.jl (Project.toml and Manifest.toml from the 2024-04-25 registry snapshot, D-017); the T0 workflow installs from it with Pkg.instantiate()
```

The workflows are in [`.github/workflows/`](../.github/workflows/): `audit-t0.yml` (reference sanity checks) and `audit-world3-pins.yml` (first search: pins ModelingToolkit only; inconclusive, kept for the record) and `audit-world3-snapshot.yml` (second search: resolves the whole dependency stack from the Julia registry as of six dates; merged table on the run page, built by `audit/t0/snapshot_table.py`).
