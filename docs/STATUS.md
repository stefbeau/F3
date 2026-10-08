# F3 — Status

**As of 2026-10-08.** `DECISIONS.md` is authoritative for decisions; this page summarises. Keep it current: update it in the same commit as any change of status.

## Phases
| Phase | Goal | Status |
|---|---|---|
| 0 Setup | repo, specification, decision log | Done |
| 1 Reproduce and audit | trust the reference models; World3 population sector in Python | **Done 2026-10-08** (`docs/phase-1-review.md`) |
| 2 Couple | AI sector, energy, materials, water, social stability, climate, linked by feedback loops | **In progress** (plan approved 2026-10-08, order B; M0 starting) |
| 3 Calibrate | backtest 1970–2025, Monte Carlo, sensitivity, validation report | Not started |
| 4 Publish | public scenario dashboard, methodology | Not started |

## Phase 2 milestones (`docs/phase-2-plan.md`, approved 2026-10-08, order B: thin slice first)
| Milestone | Sessions (estimate) | Status |
|---|---|---|
| M0 Carry-over, interfaces, first decisions (N1-N6 drafted) | 1-2 | **Closed 2026-10-08**: A0.1 (S1 in the loop bit-identical to stand-alone), A0.2 (equations untouched), A0.3 (time convention in `MODEL_SPEC.md`, D-022), A0.4 (D-020 to D-025 drafted, then approved by the editor), A0.5 (repository map matches) all met |
| M1 S3 AI sector, GATE-like, standalone | 4-6 | **Not started.** Needs D-005 amended and approved (amendment drafted as Proposed; parameter settings for A1.3 await the editor's confirmation) |
| M2 Slice: AI, electricity, climate; Demo 0 | 3-5 (+1-2 demo) | Not started |
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
- **Approved:** D-001 licensing · D-003 time step 0.25 y · D-004 ±2% tolerance (for ports against their reference) · D-010 Earth4All is a reference and component library, audited · D-011 Earth4All.jl is the reference, audit before porting · D-012 WorldDynamics.jl is the World3 reference, PyWorld3 the second check · D-014 Vensim output read at run time only · D-015 World3 variant for S1: both parameter sets carried, 2004 provisional default, confirmed at the Phase 3 backtest · D-019 1970 initialisation: Option C (World3-based sectors start from the model's own state until the Phase 3 calibration) · D-016 Earth4All audit verdict (replace population, climate, foodland, wellbeing; reuse the rest, with changes for demand, public, energy) · D-017 World3 environment: registry snapshot 2024-04-25, default solver options · D-018 Earth4All.jl is the reference; deviations from Vensim reported. · D-020 start years (S3 and data centres from 2025, Earth4All sectors from 1980) · D-021 FaIR re-run each year, non-CO2 emissions prescribed · D-022 explicit coupling at 0.25 y, t = Y is 1 January · D-023 replay then adapters for the replaced sectors' signals · D-024 backtest criteria as a framework, thresholds set by the editor before the M5 hindcast · D-025 Phase 3 entry conditions
- **Superseded:** D-002 (by D-011), D-013 (by D-017).
- **Open (Proposed, to be taken when needed):** D-005 AI-sector integration (an amendment with numeric criteria is drafted, Proposed) · D-006 critical-minerals granularity · D-007 climate damage function (sources note: `research/damage-functions.md`) · D-008 social-tension proxy · D-009 dashboard stack.

## Evidence in one page
- **World3.** WorldDynamics.jl v1.0.0 solves World3 (1974 model) with default options in the pinned environment (ModelingToolkit 9.12.1, SciMLBase 2.35.0, OrdinaryDiffEq 6.74.1). Against fine-step PyWorld3 with the diagnostic start-up, all twelve main stocks are within 1.7% (worst: persistent pollution in 2100). As shipped, PyWorld3 differs by 373.7% in pollution in 1906, explained by its delay start-up. Default and `NoInit()` solutions are identical in that environment; they agree with the newest-stack `NoInit()` solution to 0.014%.
- **Earth4All.jl vs Vensim** (package's own metric, 487 variables): typical error about 1e-4; 21% (TLTL) and 13% (GL) of variables have a 95th-percentile error above 1%, mostly demand, energy and labour-market flows. Headline variables, true relative error at the worst point: population 0.24%, GDP per person 1.2%, social tension 1.3%, warming 0.03%, inequality 1.96% (worst-case bound 2.4%), **well-being 4.37% (TLTL) and 2.77% (GL)**. Reported openly (D-018).
- **Dependency search.** First attempt pinned ModelingToolkit only: flawed and inconclusive. Registry-snapshot search: works with defaults for the 2024-04-25 and 2024-07-01 snapshots, fails from 2024-10-01. Full record in `audit/T0-FINDINGS.md`.

## Open questions for the editor
1. **D-005 amendment** (drafted, Proposed): confirm or change the two GATE parameter settings proposed for test A1.3 before any run, and the numeric criteria of A1.2 to A1.6.
2. **D-024:** you set the backtest thresholds before the M5 hindcast; the age-structure numbers were already seen when the framework was approved, and each criterion must say what a failure triggers.
3. **Plan amendment, section 14.2** (consequences of D-020 that touch approved tests and documents; not applied): A2.2's reading, the GATE-versus-Earth4All economy from 2025, the `MODEL_SPEC.md` time horizon wording, the hindcast window for variables from the Earth4All sectors.
4. Whether to report the WorldDynamics.jl break (ModelingToolkit 9.22 to 9.41) upstream.
5. Reading tasks the editor may do faster than automated access (publisher sites refused): the damage-function sections of Nordhaus, Howard and Sterner and Burke et al.; Herrington's Supporting Information; the LBNL and TSMC reports; the WID and ILOSTAT licences.

## Next tasks
M1 (the S3 AI sector) is next and does not start until you confirm the D-005 amendment. After it: M2 (the slice and Demo 0), which needs D-007 (damage function) decided. `docs/HANDOVER.md` has the Phase 2 prompts; Prompt 5 (automation of reports and CI) is open. The open issues carried into Phase 2 are in `docs/phase-1-review.md`, section 4.
