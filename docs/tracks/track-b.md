# Track B log: M3, complete World3 in Python

Branch `track-b`, worktree `C:\Users\sbeau\dev\F3-tracks\track-b`, started 2026-10-17 from main at 32e9732. Rules: `track_rules.md` (common to all tracks) and `CLAUDE.md`, including the Standing delegation section. Nothing in `DECISIONS.md`, `docs/STATUS.md`, `README.md`, `MODEL_SPEC.md` or `CLAUDE.md` is edited by this track.

## Plan and readings, written before any result (commit 1)

**Scope.** Port agriculture, capital (industry, services, jobs), non-renewable resources and persistent pollution from WorldDynamics.jl v1.0.0 (pinned environment `audit/env`, MIT) to Python as Sectors of the coupling loop, for both parameter sets (`World3` 1974, `World3_03.scenario1` 2004; D-015). Modules: `f3/sectors/w3_agriculture.py`, `w3_capital.py`, `w3_resources.py`, `w3_pollution.py` (common code `w3_common.py`). Names are a Provisional choice (P1 below). Time convention D-022 (`t = Y` is 1 January) and D-019 (start from the model's own 1900 state; restart in 1970 from the model's own state) apply.

**Method.** RK4 inside `advance`, loop step 0.25 year (D-003), explicit coupling at step boundaries (D-022). Start-of-step values are held for coupled inputs; a `ReplaySector` serves recorded series at any time inside a step (the S1 method). Variables compared by name. Error metric: `|port - reference| / max(|reference|, 1e-30)` at every 0.5-year point of 1900-2100 (401 points); mean, max and year of max reported. Reference: default solver options (D-017) and, beside every figure, the reference's own default-versus-tight difference (tight = reltol = abstol = 1e-8). Fixtures: `audit/t0/world3_m3_export.jl` (pinned run, names matched by name), files `tests/fixtures/w3_*.csv`.

**Acceptance tests and how each is read (fixed now).**
- A3.1 each sector alone, recorded inputs (the sector's cross-sector inputs from the reference run on a 1/16-year grid, linearly interpolated), the reference's own initial state, 1900-2100: every state of that sector within 2% of the default reference, both sets. Algebraic outputs the sector publishes are compared too (same 2%, reported as secondary). States per sector: agriculture 6 (al, pal, ai, uil, lfert, pfr), capital 3 (ic, sc, lufd), resources 1 (nr), pollution 4 (ppapr1, ppapr2, ppapr3, ppol). Population's 15 states were done in step 1.4.
- A3.2 full coupled run, S1 plus the four sectors in the loop, dt = 0.25: all 29 states within 2% of the default reference at every 0.5-year point of 1900-2100, both sets. A state above 2% is reported with its size and first year; if the reference's own solver explains it, the comparison against the tight reference is also reported; the criterion is not relaxed. As a diagnostic only, the same run at dt = 0.125 and 0.0625 is reported (explicit coupling is first order, D-022).
- A3.3 second check: PyWorld3 1.1 unmodified at dt = 0.05; the twelve main stocks (p1, p2, p3, p4, ic, sc, al, pal, uil, lfert, ppol, nr) of the full coupled port within 2% of PyWorld3, with PyWorld3's pollution Delay3 start value matched to WorldDynamics.jl's as a labelled runtime diagnostic (override on the instance, as in `audit/t0/pyworld3_t0.py`); the as-shipped comparison is reported beside it. 2004: diagnostic as in S1 (PyWorld3 does not ship the variant; parameters and tables overridden on the instance).
- A3.4 (a) all existing tests pass; (b) S1's 15 states inside the full run equal S1's 15 states run alone with the recorded inputs (the A3.1-style S1 run) within 0.25%, both sets, over 1900-2100. Read literally. D-022 measured start-of-step coupling error for S1 at 0.25 year as 1.04% (1974) and 0.93% (2004) on the worst state (`fcfpc1`); that predicts (b) fails for that state. This is a prediction written before the run, not a relaxation.
- A3.5 wall-clock time of one full World3 run, 1900-2100, dt = 0.25, measured (median of 5 runs on this machine, one core, after one warm-up) and for 1970-2100.

**Test lists, per sector, written before each port (committed ahead of the module).** Common to the four sector files: (1) initial state equals the reference row at 1900 (1e-8); (2) published algebraic outputs at the start equal the reference's 1900 values (1e-8); (3) A3.1 states; (4) A3.1 published outputs; (5) the sector's parameter set carries the documented 1974/2004 differences; (6) restart in 1970 from the reference's 1970 state stays within 2% (D-019 mechanics); (7) wiring: inputs and outputs with units accepted by `Model`. The coupling tests (A3.2 to A3.5) are listed before step 5 is coded.

## Log
- 2026-10-17 agriculture: test list committed first (`tests/test_w3_agriculture.py`, 13 tests), then `f3/sectors/w3_common.py` and `w3_agriculture.py`. A3.1 measured: all six states within 0.13% of the default reference, both sets (largest `ai` 2004 0.124%, reference default vs tight 0.121% on the same state); published outputs within 0.13%. First test run: 2 failures of the 1970-restart tests, caused by the test helper comparing a 1970 restart against the 1900 reference grid (helper bug, fixed in `tests/w3_helpers.py`, not a model change).
- 2026-10-17 capital: test list committed first (`tests/test_w3_capital.py`, 13 tests), then `w3_capital.py`. A3.1 measured: ic, sc, lufd within 0.11% of the default reference (largest `lufd` 2004 0.101%, which is the reference's own default-vs-tight 0.099%; 1974 `lufd` 0.047% while the reference's own is 0.306%); published outputs within 0.04%. One collection error on first run (missing unit strings in `w3_common.UNITS`, fixed).
- 2026-10-17 resources and pollution: test lists committed first (`tests/test_w3_resources.py` 13 tests, `tests/test_w3_pollution.py` 13 tests), then `w3_resources.py` and `w3_pollution.py`. A3.1 measured: nr within 0.015% (both sets); pollution states within 0.031% (both sets); published outputs within 0.04%. The 1974 pollution states differ from the reference's tight run by 0.19% (the reference's own default-vs-tight is 0.19%), the port matches the default run, as the plan reads. One collection error on first run (missing unit strings, fixed).

## Coupling test list (written before `f3/sectors/world3.py` was run)
`tests/test_w3_full.py`: 29 states by name; A3.2 (29 states within 2% of the default reference, both sets, with the tight-reference figure and the reference's own default-vs-tight beside each; failures reported with size and first year, not adjusted); A3.4(b) (S1 in the full run vs S1 alone with recorded inputs within 0.25%; **prediction written now: fails for the 1974 set on a delay stage, because D-022 measured the start-of-step coupling error of S1 at 1.04% (1974) and 0.93% (2004) at step 0.25 year**); A3.5 (run time, median of 3 after a warm-up, 1900-2100 and 1970-2100); wiring complete and unit-checked; 1970 restart as a diagnostic. `tests/test_w3_pyworld3.py`: A3.3 as read above, 1974 asserted with the matched pollution start-up, 2004 diagnostic.

## Results of the coupling (run 2026-10-20, after an API stop; no test, tolerance or criterion changed after the results)
Report: `audit/m3-world3-port-report.md` (generated by `audit/t0/m3_report.py`). Suite: 112 passed, 21 skipped (pre-existing, not from this track), 5 strict xfail (A3.2 both sets, A3.4(b) both sets, A3.3 1974).
- **A3.1 met**: 14 states of the four sectors within 0.124% (1974: 0.091%), both sets; published outputs within 0.13%.
- **A3.2 FAILED at the plan's step 0.25 year, both sets.** 1974: worst `lufd` 6.90%, 15 of 29 states above 2%, first failure 2023.5 (`fcfpc1`). 2004: worst `lufd` 7.96%, 16 of 29 above 2%, first failure 2023.0 (`fcfpc1`). Not the reference's solver: default-vs-tight is at most 1.61% (1974, `fcfpc1`) and 0.26% (2004), and the port against the tight reference is as far off as against the default. Cause, from a post-hoc step scan (not a criterion): first-order start-of-step coupling (D-022). Worst state by loop step, 1974 / 2004: 0.25 -> 6.90 / 7.96%; 0.125 -> 3.24 / 3.89%; 0.0625 -> 1.62 / 1.91% (no state above 2%); 0.03125 -> 1.63 / 0.93%.
- **A3.3**: 1974 with the pollution start-up matched (labelled diagnostic): ten stocks within 2%, `ic` 3.39% and `sc` 2.42% (2100): **FAILED** (strict xfail). As shipped `ppol` 373.49% (1906). 2004 diagnostic: all twelve within 2.4%, nothing asserted. Post-hoc: at loop step 0.0625 the 1974 worst is 0.91%.
- **A3.4(a)** existing tests pass. **A3.4(b) FAILED, as predicted before the run**: worst 4.36% (1974, `aiopc`, 2100) and 3.69% (2004, `fcfpc1`, 2072); above 0.25% from 1900.5.
- **A3.5**: one full run (1900-2100, step 0.25, five sectors, one core) median 0.59 s (2004), 0.68 s (1974); 1970-2100 0.38 s; 2.3 s at step 0.0625. The plan's guess of 5-10 s was an order of magnitude high.
- 1970 restart from the reference's state inside the loop (diagnostic): worst 0.74% (1974), 0.68% (2004) over 1970-2010.
- Corrections to my own work: a test-helper bug (restart compared on the 1900 grid) and a missing-fixture bug in the report and the A3.4(b) test (S1 inputs live in `s1_inputs_*.csv`); both were fixed before any result from those lines was read; no criterion touched.

## Status
Sectors built; each passes A3.1. The full run fails A3.2, A3.3 (1974) and A3.4(b) at the plan's loop step, with a measured cause. Not merged. M4, M5, S3 coupling and Phase 3 not started.

## Provisional decisions (paste-ready)

### D-0xx (P1): module names and structure of the four World3 sectors
- **Status:** Provisional (delegated)
- **Date:** 2026-10-20
- **Recommendation followed:** `f3/sectors/w3_agriculture.py`, `w3_capital.py`, `w3_resources.py`, `w3_pollution.py`, common code in `w3_common.py`, wiring in `world3.py`; each sector is a `Sector` with RK4 inside `advance`, algebraic outputs published at the end of `advance`.
- **Alternatives considered:** `s2_`/`s5_` names from the spec's sector map (rejected: World3 capital and resources are not the spec's S2/S5, which M4 and M5 rebuild); one monolithic World3 module (rejected: A3.1 needs per-sector tests).
- **Cost of reversing:** renaming files and imports; no equation changes.

### D-0xx (P2): the A3.2 failure at step 0.25 is recorded, not repaired
- **Status:** Provisional (delegated)
- **Date:** 2026-10-20
- **Recommendation followed:** no change to the loop step, coupling scheme or criterion; strict xfails document A3.2 (both sets), A3.3 (1974) and A3.4(b) (both sets).
- **Alternatives considered:** (a) loop step 0.0625 (A3.2 would pass both sets; 2.3 s per run); (b) predictor-corrector coupling (D-022 alternative, needs state save and restore); (c) sub-stepping inside the World3 sectors. Each changes D-003 or D-022 and needs the editor.
- **Cost of reversing:** none (nothing applied).

### D-0xx (P3): initial outputs of the coupled sectors
- **Status:** Provisional (delegated)
- **Date:** 2026-10-20
- **Recommendation followed:** the start-time inputs of the four sectors are computed from their initial states by iterating the wiring, which is acyclic at t0 (`f3/sectors/world3.py`), not seeded from recorded data. Initial state is the reference's own (D-019 Option C; pollution delay stages start at `pptd*ppgr0/3` from the sector's own 1900 tables, as the reference does).
- **Alternatives considered:** seeding from recorded values (rejected: the full run would depend on fixtures).
- **Cost of reversing:** small, one function.


## Re-run under D-031 (2026-10-20)
- Rule and predictions committed first (D-031, `b953b31` on main). Implementation `f3/sectors/world3_group.py`; `run_world3` now returns the sub-stepped group by default, `substep=None` keeps the first version. No Sector interface change.
- **A3.2 MET** both sets: worst 1.621% (1974, `fcfpc1`) and 1.906% (2004, `lufd`). **A3.3 (1974, matched start-up) MET**, worst 0.91% (`ppol`). **A3.4(b) FAILED**: worst 1.019% (1974 `aiopc`), 0.931% (2004 `fcfpc1`) against 0.25%; D-031's 'borderline' prediction was wrong. Suite: 115 passed, 21 skipped, 4 strict xfail (A3.4(b) both sets; the recorded un-sub-stepped A3.2 failure both sets).
- Test edits (the criteria and thresholds are unchanged; only the xfail markers changed with the results): the A3.2 and A3.3 strict xfails were removed because they now pass; the A3.4(b) reason was updated to the new sizes; a test recording the old failure (`substep=None`) was added as a strict xfail.
- **Provisional (delegated) P4:** the World3 group is one Sector wrapping the five sectors (alternative: a global 0.0625 step for World3-only runs, rejected because it was not needed; reversal cost: low). **P5:** A3.4(b) is recorded as failed and not repaired (alternatives: restate to a looser number, a labelled post-hoc proposal, not applied; reversal cost: none).

## Fixture regrid, 2026-10-21 (orchestrator)
See `audit/m3-world3-port-report.md` section 8 and `docs/m3-fixture-regrid-reading.md`: re-export on the 1/64-year grid changed nothing (by construction); A3.4(b) still fails with the same sizes.
