# F3 — Foundation for Earth: briefing for Claude Code

Read this first, then `docs/STATUS.md`. It is the project's memory: earlier work was done in a long chat, and everything that matters from it is in this repository.

## What this project is
F3 is an open global simulation model that puts two families of models into one set of feedback loops:
- **planetary-limits models**: World3 (*The Limits to Growth*, 1972; the 1974 version is what we use), Earth4All;
- **AI-transition models**: GATE (Epoch AI) and compute-based takeoff models.

It asks how a fast AI race interacts with energy, materials, water, climate and social stability, and which policy levers change the outcome. Output: **conditional scenarios with uncertainty bands, never forecasts**. End product: a public dashboard where anyone can run scenarios. The value is showing which levers and feedback loops matter. Specification: `MODEL_SPEC.md`. Plan: `docs/phase-1-plan.md`. Source register: `research/SOURCES.md`.

## People and authority
- **Editor-in-chief: Stéphane Beau** (GitHub `stefbeau`). He is a technical writer, not a programmer; he reads English (his app language is French) and works on Windows; the shell on his machine is PowerShell, not Command Prompt.
- **Only he approves, rejects or supersedes decisions** in `DECISIONS.md`. You draft decisions with status `Proposed`. Mark one `Approved` only after he has said so in the session, and record the date and what he approved. **Never edit an approved decision**: supersede it with a new one. Approved decisions may receive appended, dated outcome notes (for example the result of a condition, or a pointer to the decision that supersedes them). Their wording and status never change.
- He dislikes repeated manual steps. **Commit and push yourself**; never ask him to upload, paste or edit files by hand.

## How we work (rules that have already mattered)
1. **Facts, not spin.** Say what was measured, what was inferred and what is unverified. Check the evidence before writing a cause. Correct earlier mistakes openly with a visible note in the log; never delete them.
2. **Do not relax a pre-set acceptance condition after seeing the data.** If a condition fails, record the failure; a revised condition is a new, labelled post-hoc proposal for the editor.
3. **Pin everything.** External models are never copied into this repo. Julia: `audit/env/Manifest.toml` (World3, D-017) and `audit/env-earth4all/Manifest.toml` (Earth4All audit). Others: `audit/REFERENCES.md`. Do not run `Pkg.update` or add packages to either environment without a decision.
4. **Licences (D-001, D-011, D-012, D-014).** F3 code is Apache 2.0; docs and processed data CC BY 4.0.
   - PyWorld3 is CeCILL 2.1 (copyleft): use it unmodified from PyPI. Never copy or edit its code into F3. A runtime override on an instance, for diagnosis only, is allowed and must be labelled.
   - WorldDynamics.jl and Earth4All.jl are MIT: ports need attribution (`NOTICE` plus the licence text under `licenses/`).
   - **Vensim files are never copied or stored. `vensim_source/` is never used.** `VensimOutput/` may be read from a clone made at run time, only to run the package's own comparison; store only variable names and error figures.
5. **Do not overclaim.** Never write that Earth4All.jl "reproduces Vensim" without the caveat (D-018).
6. **Communication.** Answer first, concisely, plain English. At most one question per message. Say plainly when something failed or is untested. Summaries of at most ~15 lines unless asked.
7. **Git.** Small commits with clear messages, no force-push, no secrets, ask before deleting anything that is not obviously stale.

## Lessons already paid for (do not repeat)
- WorldDynamics.jl v1.0.0 fails with dependencies newer than about mid-2024 (default solve returns `InitialFailure`, later other errors). Use the pinned environment. With `initializealg = NoInit()` it also works, but D-017 chose the pinned environment with default options.
- The two Julia environments list the 29 World3 states **in a different order**. Compare by name, never by position.
- PyWorld3's `Delay3` starts its delay at `input × 3 / delay`, not at steady state; its pollution stock then differs from WorldDynamics.jl by 374% in 1906. Overriding that one start value on the instance (diagnostic only) brings the worst gap to 1.7%. PyWorld3 at its default step (dt=0.5) has its own error (up to 3.5% for some stocks, 11.6% for early pollution): compare with dt=0.05.
- Earth4All.jl's own error metric (`all_mre`) is |julia − vensim| / (|vensim| + 1): it hides relative errors of variables of order 1. Convert to true relative error. The maximum over time is dominated by isolated timing spikes; report median and 95th percentile too.
- In Earth4All.jl the `*_support` systems inside sector files are test scaffolding, not part of the composed model. Exclude them from audits (a first scan that included them was wrong).
- CI runs take 10–30 minutes. Prefer local runs; keep CI for public, repeatable evidence.

## Repository map
```
CLAUDE.md                 this file
DECISIONS.md              decision register (authoritative)
MODEL_SPEC.md             model specification v0.1
README.md  LICENSE  NOTICE
docs/STATUS.md            where we stand (keep current)
docs/HANDOVER.md          prompts for the next tasks, in order
docs/phase-1-plan.md      Phase 1 plan (done)
docs/phase-1-review.md    Phase 1 review: evidence, decisions, open issues carried into Phase 2
docs/phase-2-plan.md      Phase 2 plan: a PROPOSAL until the editor approves it
research/SOURCES.md       latest verified information per topic
audit/                    audits of reference models (README.md, T0-FINDINGS.md, earth4all-audit.md, REFERENCES.md)
audit/env/                pinned Julia environment for WorldDynamics.jl (D-017)
audit/env-earth4all/      pinned Julia environment for the Earth4All.jl audit (commit 16f37d0 plus DataFrames and CSV)
audit/t0/                 audit scripts (world3_t0.jl, earth4all_t0.jl, pyworld3_t0.py, compare_world3.py, snapshot_table.py)
audit/data/               stored error statistics (variable names and error figures only)
.github/workflows/        audit-t0.yml (current), audit-world3-snapshot.yml and audit-world3-pins.yml (records of the dependency search)
```
Model code: `f3/sectors/s1_population.py` (S1, both World3 parameter sets), tests in `tests/` (fixtures exported from the pinned Julia run in `tests/fixtures/`), `pyproject.toml` and `uv.lock` (Python environment, `uv sync --group dev`), `licenses/` (MIT text of ported code). Planned, not yet created: `dashboard/`, `data/`.

## Running things on Stéphane's machine (Windows)
- Set `PYTHONUTF8=1` (the scripts print Unicode such as `₊` and `✅`).
- Julia 1.10 via juliaup: `winget install --id Julialang.juliaup -e --source winget` (without `--source winget` it finds no package), then `juliaup add 1.10`; run as `julia +1.10 …`. The first `juliaup add 1.10` can fail with a file-lock error ("Accès refusé"); a retry works.
- World3 audit: `julia +1.10 --project=audit/env -e "using Pkg; Pkg.instantiate()"`, then `julia +1.10 --project=audit/env audit/t0/world3_t0.jl` with `F3_OUT` set; then `python audit/t0/pyworld3_t0.py` and `python audit/t0/compare_world3.py` (`pip install pyworld3 pandas matplotlib`).
- Earth4All audit: clone `https://github.com/worlddynamics/Earth4All.jl` **outside** this repo and check out `16f37d013a2f68135f03e7815bf861dbf47311f2` (its sources and `VensimOutput/` are only read). Packages come from the committed Manifest, not from the clone's own `Project.toml`: `julia +1.10 --project=audit/env-earth4all -e "using Pkg; Pkg.instantiate()"`, then `julia +1.10 --project=audit/env-earth4all audit/t0/earth4all_t0.jl <clone path>` and `audit/t0/earth4all_audit.jl <clone path>`, with `F3_OUT` set. `.github/workflows/audit-t0.yml` is the executable recipe.

## Next
`docs/STATUS.md` says where we stand; `docs/HANDOVER.md` lists the next tasks as ready-to-run prompts.
