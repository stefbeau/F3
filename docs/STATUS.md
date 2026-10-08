# F3 — Status

**As of 2026-10-08.** `DECISIONS.md` is authoritative for decisions; this page summarises. Keep it current: update it in the same commit as any change of status.

## Phases
| Phase | Goal | Status |
|---|---|---|
| 0 Setup | repo, specification, decision log | Done |
| 1 Reproduce and audit | trust the reference models; World3 population sector in Python | **Done 2026-10-08** (`docs/phase-1-review.md`) |
| 2 Couple | AI sector, energy, materials, water, social stability, climate, linked by feedback loops | **Next**: not started; no Phase 2 plan written yet |
| 3 Calibrate | backtest 1970–2025, Monte Carlo, sensitivity, validation report | Not started |
| 4 Publish | public scenario dashboard, methodology | Not started |

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
- **Approved:** D-001 licensing · D-003 time step 0.25 y · D-004 ±2% tolerance (for ports against their reference) · D-010 Earth4All is a reference and component library, audited · D-011 Earth4All.jl is the reference, audit before porting · D-012 WorldDynamics.jl is the World3 reference, PyWorld3 the second check · D-014 Vensim output read at run time only · D-015 World3 variant for S1: both parameter sets carried, 2004 provisional default, confirmed at the Phase 3 backtest · D-019 1970 initialisation: Option C (World3-based sectors start from the model's own state until the Phase 3 calibration) · D-016 Earth4All audit verdict (replace population, climate, foodland, wellbeing; reuse the rest, with changes for demand, public, energy) · D-017 World3 environment: registry snapshot 2024-04-25, default solver options · D-018 Earth4All.jl is the reference; deviations from Vensim reported.
- **Superseded:** D-002 (by D-011), D-013 (by D-017).
- **Open (Proposed, to be taken when needed):** D-005 AI-sector integration · D-006 critical-minerals granularity · D-007 climate damage function · D-008 social-tension proxy · D-009 dashboard stack.

## Evidence in one page
- **World3.** WorldDynamics.jl v1.0.0 solves World3 (1974 model) with default options in the pinned environment (ModelingToolkit 9.12.1, SciMLBase 2.35.0, OrdinaryDiffEq 6.74.1). Against fine-step PyWorld3 with the diagnostic start-up, all twelve main stocks are within 1.7% (worst: persistent pollution in 2100). As shipped, PyWorld3 differs by 373.7% in pollution in 1906, explained by its delay start-up. Default and `NoInit()` solutions are identical in that environment; they agree with the newest-stack `NoInit()` solution to 0.014%.
- **Earth4All.jl vs Vensim** (package's own metric, 487 variables): typical error about 1e-4; 21% (TLTL) and 13% (GL) of variables have a 95th-percentile error above 1%, mostly demand, energy and labour-market flows. Headline variables, true relative error at the worst point: population 0.24%, GDP per person 1.2%, social tension 1.3%, warming 0.03%, inequality 1.96% (worst-case bound 2.4%), **well-being 4.37% (TLTL) and 2.77% (GL)**. Reported openly (D-018).
- **Dependency search.** First attempt pinned ModelingToolkit only: flawed and inconclusive. Registry-snapshot search: works with defaults for the 2024-04-25 and 2024-07-01 snapshots, fails from 2024-10-01. Full record in `audit/T0-FINDINGS.md`.

## Open questions for the editor
1. D-015: the 2004 set is closer on total population but worse on age structure (65+ share 8.5% in 1970 against 5.3% observed; 16.8% in 2025 against 10.3% projected; the 1974 set is 7.1% and 12.8%). Should age structure be a named criterion of the Phase 3 backtest? (Recommended in the D-015 outcome note; the Decision text is unchanged.) The book's tables and Herrington's Supporting Information are still unread.
2. Whether to report the WorldDynamics.jl break (between ModelingToolkit 9.22 and 9.41) upstream.
3. Item 12 of the Phase 1 review (Earth4All environment not pinned) is resolved (2026-10-08). Item 11 (only the population sector is ported, so F3 cannot run World3 end to end) is carried into the Phase 2 plan, which is a proposal for your decision.

## Next tasks
**Decision for the editor:** `docs/phase-2-plan.md` is a **proposal** (drafted 2026-10-08, nothing approved): seven milestones with acceptance tests stated beforehand, a recommended order (a thin slice with the AI sector first, a public demo after about 9–15 sessions) and one alternative (complete World3 first). Phase 2 starts only when you approve a plan. Remaining from `docs/HANDOVER.md`: Prompt 5 (automation of reports and CI). The open issues carried into Phase 2 are in `docs/phase-1-review.md`, section 4.
