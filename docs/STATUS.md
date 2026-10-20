# F3 — Status

**As of 2026-10-20 (Track A held; Track B stopped by an API budget error part-way; Track C stopped).** `DECISIONS.md` is authoritative for decisions; this page summarises. Keep it current: update it in the same commit as any change of status.

## Phases
| Phase | Goal | Status |
|---|---|---|
| 0 Setup | repo, specification, decision log | Done |
| 1 Reproduce and audit | trust the reference models; World3 population sector in Python | **Done 2026-10-08** (`docs/phase-1-review.md`) |
| 2 Couple | AI sector, energy, materials, water, social stability, climate, linked by feedback loops | **In progress** (plan approved 2026-10-08, order B; M0 and M1 closed, M1 with A1.3 failed per D-029; M2 not started) |
| 3 Calibrate | backtest 1970–2025, Monte Carlo, sensitivity, validation report | Not started |
| 4 Publish | public scenario dashboard, methodology | Not started |

## Phase 2 milestones (`docs/phase-2-plan.md`, approved 2026-10-08, order B: thin slice first)
| Milestone | Sessions (estimate) | Status |
|---|---|---|
| M0 Carry-over, interfaces, first decisions (N1-N6 drafted) | 1-2 | **Closed 2026-10-08**: A0.1 (S1 in the loop bit-identical to stand-alone), A0.2 (equations untouched), A0.3 (time convention in `MODEL_SPEC.md`, D-022), A0.4 (D-020 to D-025 drafted, then approved by the editor), A0.5 (repository map matches) all met |
| M1 S3 AI sector, GATE-like, standalone | 4-6 | **Closed 2026-10-12 with A1.3 FAILED (D-029).** S3 (`f3/sectors/s3_ai.py`) fails A1.3 on all three shipped runs under variant A, variant B (footnote-38 grids) and the 101-point case (D-027 outcome ii); with Epoch's own composite supplied everything matches, so the gap is the task-allocation step, cause unresolved, grid ruled out. **S3's absolute output (gwp, capital, effective compute) is unvalidated against GATE after about 2027; nothing may say the model reproduces GATE; every output that uses S3 carries that notice** (in `s3_ai.py`, `README.md`, `MODEL_SPEC.md`). A1.5 and finiteness pass. R3 (D-028) is a scenario-lever rule, not a GATE replica (A1.4 poor, `audit/s3-r3-a1.4.md`). Tests: 56 passed, 9 strict xfail. Route to resolve the composite: Epoch's answer to `docs/drafts/epoch-gate-email.md` (**unsent, the editor sends it**); no further composite variants without a new decision |
| M2 Slice: AI, electricity, climate; Demo 0 | 3-5 (+1-2 demo) | **Step 1 done 2026-10-12: FaIR alone and `s6_climate`; A2.1 FAILED.** Plan `docs/m2-step1-fair.md` (fixed before code); sector `f3/sectors/s6_climate.py` (FaIR 2.2.4 unmodified, published fair-calibrate v1.4.1 ensemble of 841 members, D-021 re-run rule; tests S1-S5 pass). **A2.1: ensemble-mean 2015-2024 warming 1.196 K above 1850-1900 against HadCRUT5's mean 95% interval [1.234, 1.305] K: 0.037 K below the lower edge** (0.073 K below the best estimate); not an artefact of the CO2 source or the non-CO2 scenario; the ensemble was constrained to 2022, so only 2023-2024 are out of sample (0.16-0.20 K low). Report `audit/m2-fair-report.md`; labelled post-hoc options listed there, none applied. Measured cost of D-021: 1.06 s per annual re-run with 20 members (about 2 min per 1980-2100 loop) and 19.4 s with 841 members (about 39 min); clarified 2026-10-12, projection about 4% low (`audit/m2-fair-report.md` section 6). Data: HadCRUT5 (OGL v3.0) and the FaIR files pinned and never committed; GCB 2025 extract (CC BY 4.0) committed. **D-030 drafted (Proposed): close the step with A2.1 failed and label climate output.** D-021 measurement (b)/(c) vs (a) with the real configuration and the 20-member representativeness check: done 2026-10-12 (`audit/m2-d021-measurement.md`; readings fixed first): ensemble-mean error at most 0.002 K from 2025 for both (b) and (c), single members up to 0.27 K; carried segments cost about as much as exact re-runs; 20-member mean within 0.054 K of the 841-member mean but the 5th-95th band is poorly represented (up to 0.32 K). **Editor chose (a) on 2026-10-12: exact re-run, all 841 members for precomputed published runs; the 20-member subset is not used for published bands** (D-021 note). **D-007 drafted (Proposed, not approved):** damage-function sources read (`research/damage-functions-verified.md`): Nordhaus 2017 (2.1% of output at 3 C), Barrage-Nordhaus 2024 (3.1% at 3 C), Howard-Sterner 2017 (6.7% at 3 C, 9.0% with the catastrophic term, derived); Burke et al. 2015 not offered as a level option (growth-rate, local temperature; its numbers unreadable here); Hsiang et al. 2017 blocked. **Not started:** data-centre module, damage function implementation (D-007 not approved), coupled slice, Demo 0 |
| M3 Complete World3 in Python (agriculture, capital, resources, pollution) | 5-8 | Not started |
| M4 Port the reused Earth4All sectors | 6-10 | Not started |
| M5 New modules: S7 social, S5 minerals and water, warming channels in replaced sectors | 6-10 | Not started |
| M6 Integration and Phase 2 review | 4-7 | Not started |

The external review of Demo 0 is deferred until Demo 0 is ready (editor's decision, 2026-10-08).

## Phase 1 steps
| Step | Status |
|---|---|
| 1.0 reference environment | Done: pinned Julia environment in `audit/env` (D-017); Earth4All.jl audited at commit `16f37d0` |
| 1.1 T0 sanity check | Earth4All part closed (D-018). World3 part: closed 2026-10-07. D-017 conditions (a), (b) and (c) all met; condition (a) confirmed by a local run from the pinned environment alone, and the package's own test suite passes there |
| 1.2 Earth4All audit T1–T4 | Done 2026-10-07 (`audit/earth4all-audit.md`): T1 no mortality below 60 by design; T1b no negative cohort stock; T2 workforce never above working-age population (under the stated definition); T3 40 equations classified, 9 behaviour forcing (climate, foodland, population), none in output, demand, inventory, finance, public, energy; T4 Giant Leap unstable at 2197 |
| 1.3 audit verdict (D-016) | Done: D-016 approved 2026-10-07; MODEL_SPEC updated 2026-10-08 |
| 1.4 Python port of World3 population sector (S1) | **Done 2026-10-08**. Port (`f3/sectors/s1_population.py`, both parameter sets): all 15 states within 0.25% (2004 set) and 1.57% (1974 set, a delay stage; the reference's own solver gap there is 1.61%) of WorldDynamics.jl, key variables within 0.21%; PyWorld3 second check within 0.1% for the cohorts from the same start (`audit/s1-port-report.md`). 22 tests pass locally and in CI (workflow `python-tests`, commit `cc9f791`). Done: D-019 (1970 initialisation, Option C) approved 2026-10-08 |
| 1.5 phase review | Done 2026-10-08: `docs/phase-1-review.md`; the UN age-cohort check of D-015 is done (outcome note in D-015) |

## Decisions
- **Approved:** D-001 licensing · D-003 time step 0.25 y · D-004 ±2% tolerance (for ports against their reference) · D-010 Earth4All is a reference and component library, audited · D-011 Earth4All.jl is the reference, audit before porting · D-012 WorldDynamics.jl is the World3 reference, PyWorld3 the second check · D-014 Vensim output read at run time only · D-015 World3 variant for S1: both parameter sets carried, 2004 provisional default, confirmed at the Phase 3 backtest · D-019 1970 initialisation: Option C (World3-based sectors start from the model's own state until the Phase 3 calibration) · D-016 Earth4All audit verdict (replace population, climate, foodland, wellbeing; reuse the rest, with changes for demand, public, energy) · D-017 World3 environment: registry snapshot 2024-04-25, default solver options · D-018 Earth4All.jl is the reference; deviations from Vensim reported. · D-005 amendments A (2026-10-08) and B (2026-10-09, shipped runs as the A1.3 settings, plus the eq.-10 clause) · D-026 handling of the Epoch playground data (2026-10-09) · D-027 footnote-38 task grids as a labelled variant (approved 2026-10-12; outcome ii: fails) · D-028 S3 investment rule R3 with R1 curves (approved 2026-10-12; built, A1.4 poor) · D-029 M1 closed with A1.3 failed; composite a known open difference (approved 2026-10-12) · D-030 M2 step 1 closes with A2.1 failed, climate output labelled (approved 2026-10-12) · D-007 climate damage function: three level-effect options, default central, growth case not represented (approved 2026-10-12) · D-009 dashboard: static site, precomputed scenario grids (approved 2026-10-12) · D-020 start years (S3 and data centres from 2025, Earth4All sectors from 1980) · D-021 FaIR re-run each year, non-CO2 emissions prescribed · D-022 explicit coupling at 0.25 y, t = Y is 1 January · D-023 replay then adapters for the replaced sectors' signals · D-024 backtest criteria as a framework, thresholds set by the editor before the M5 hindcast · D-025 Phase 3 entry conditions
- **Superseded:** D-002 (by D-011), D-013 (by D-017).
- **Open (Proposed, to be taken when needed):** D-006 critical-minerals granularity · D-008 social-tension proxy.

## Evidence in one page
- **World3.** WorldDynamics.jl v1.0.0 solves World3 (1974 model) with default options in the pinned environment (ModelingToolkit 9.12.1, SciMLBase 2.35.0, OrdinaryDiffEq 6.74.1). Against fine-step PyWorld3 with the diagnostic start-up, all twelve main stocks are within 1.7% (worst: persistent pollution in 2100). As shipped, PyWorld3 differs by 373.7% in pollution in 1906, explained by its delay start-up. Default and `NoInit()` solutions are identical in that environment; they agree with the newest-stack `NoInit()` solution to 0.014%.
- **Earth4All.jl vs Vensim** (package's own metric, 487 variables): typical error about 1e-4; 21% (TLTL) and 13% (GL) of variables have a 95th-percentile error above 1%, mostly demand, energy and labour-market flows. Headline variables, true relative error at the worst point: population 0.24%, GDP per person 1.2%, social tension 1.3%, warming 0.03%, inequality 1.96% (worst-case bound 2.4%), **well-being 4.37% (TLTL) and 2.77% (GL)**. Reported openly (D-018).
- **Dependency search.** First attempt pinned ModelingToolkit only: flawed and inconclusive. Registry-snapshot search: works with defaults for the 2024-04-25 and 2024-07-01 snapshots, fails from 2024-10-01. Full record in `audit/T0-FINDINGS.md`.

## Open questions for the editor
1. **Epoch email** (`docs/drafts/epoch-gate-email.md`): finalised, **unsent**; you send it. Its reply is the only route to resolve the composite (D-029). A better R3 fit waits until then (D-029). Which `compute` pairing counts is yours and changes nothing (D-005 outcome note).
2. **D-024:** you set the backtest thresholds before the M5 hindcast; the age-structure numbers were already seen when the framework was approved, and each criterion must say what a failure triggers.
3. **Plan amendment, section 14.2** (consequences of D-020 that touch approved tests and documents; not applied): A2.2's reading, the GATE-versus-Earth4All economy from 2025, the `MODEL_SPEC.md` time horizon wording, the hindcast window for variables from the Earth4All sectors.
4. Whether to report the WorldDynamics.jl break (ModelingToolkit 9.22 to 9.41) upstream.
5. Reading tasks the editor may do faster than automated access (publisher sites refused): the damage-function sections of Nordhaus, Howard and Sterner and Burke et al.; Herrington's Supporting Information; the LBNL and TSMC reports; the WID and ILOSTAT licences.
6. Optional, pending, **still unsent** (question 4 on task grids and stored `compute` added 2026-10-12): email to Epoch AI (docs/drafts/epoch-gate-email.md) asking permission to use the shipped playground runs as test references and for result series for the two stress settings. Not sent. The plan does not depend on a reply; D-026 treats permission as not yet requested.

## Parallel tracks (launched 2026-10-12, then stopped by the editor the same day; standing delegation in CLAUDE.md)
Each track works in its own git worktree and branch and writes `docs/tracks/<track>.md`; the orchestrator merges. Routine decisions are recorded as Provisional (delegated) and reviewed by the editor in one batch per milestone.
| Track | Scope | Branch | Status |
|---|---|---|---|
| A | M2 remainder: data-centre electricity, damage function (D-007), coupled slice, tests A2.2-A2.6, Demo 0 page generator (local only; **not published**, editor approves per A2.7) | `track-a` | **stopped by the editor 2026-10-12, no work produced** (branch at main, nothing to merge) |
| B | M3: agriculture, capital, resources, pollution ports of World3 (A3.1-A3.5) | `track-b` (wip commit 612d16f, pushed) | **relaunched 2026-10-17, then stopped 2026-10-20 by an API budget error (key limit 150.0 reached), not a code failure.** Per the track's log: agriculture, capital, resources and pollution ported, A3.1 within 0.13%, 0.11% and 0.04% (both sets); the coupling module, report script and test edits are written but **never run**, so A3.2 to A3.5 have no results. Not merged into main |
| C | M4: reused Earth4All sectors (A4.1-A4.6); N4 delegated per D-023 | `track-c` | **stopped by the editor 2026-10-12, no work produced** (branch at main, nothing to merge) |
The D-021 measurement finished (see the M2 row); its report and D-021 outcome note are on main. Not started: M5 (water, minerals), Phase 3.

### Track A result (2026-10-17): three slice tests FAILED, recorded, no test changed
Tests written before results (`docs/tracks/track-a-plan.md`); 20-member development climate for tests. Six of nine pass (A2.2 consistency, A2.4 invariance to 1e-9, A2.5, B2 sign, damage anchors). **Failures:**
- **A2.6 step halving (0.25 to 0.125 year): FAILED.** Largest difference 0.565% in data-centre electricity used (2036; first above 0.1% in 2028); output 0.197%; compute 0.108%; the bar is 0.1%.
- **B1 sign: FAILED.** Halving electricity supply gives up to 17.8% MORE compute in 2038-2045 (first 2038), the opposite of the expected direction. The track's explanation (R3's shares depend on usable compute) is an inference, not tested.
- **R1 sign: FAILED** on automation: both runs are at 1.0 at 2065, so no increase can be seen (compute is higher).
- **Finding:** modelled data-centre demand is about 20,000 TWh in 2030 and 414,000 TWh in 2040, because S3's unvalidated compute path (D-029) leaves any plausible range; supply binds from 2027-28.
- **Checked on this side:** my re-run of the slice tests gives 6 passed, 3 failed as above. The 33-line change to `f3/sectors/s3_ai.py` on the branch leaves S3 unchanged: the A1.3 and A1.5 figures (all settings, the stored-T diagnostic, the stress settings, the variants) and the R3 A1.4 figures regenerate bit-identical to `audit/data/s3-gate-comparison.json` and `s3-r3-a1.4.json`; the S3 and R3 tests give 28 passed, 9 strict xfail.
- **Not verified here:** the five Provisional decisions and the review checklist (`docs/tracks/track-a.md`, `track-a-review.md`); the 841-member climate run; the page has not been viewed in a browser (phone width, dark mode).

### To revisit after the Epoch reply
1. **R3 design:** the counter-loop under supply limits (B1 sign failure).
2. **A better R1 test** (automation saturates at 1.0 by 2065), only as a labelled post-hoc addition; the failed test stays recorded.
3. **A2.6 step convergence** (0.565% against 0.1%).
4. **The implausible 2030+ electricity demand** (about 20,000 TWh in 2030) caused by S3's unvalidated compute path.

## Next tasks
Waiting for the editor. Demo 0 is held (A2.7 not approved); Track A's branch is kept, not merged; Tracks B and C are stopped. Open for the editor: send the Epoch email (S3). D-021 is settled: option (a). Only the editor's STOP list in `CLAUDE.md` applies to anything further. `docs/HANDOVER.md` has the Phase 2 prompts; Prompt 5 is open. Open issues carried into Phase 2: `docs/phase-1-review.md`, section 4.
