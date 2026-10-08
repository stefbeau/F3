# F3 — Phase 1 review (Reproduce & audit)

**Written 2026-10-08**, step 1.5 of `docs/phase-1-plan.md`. The first commit in the repository is dated 2026-10-05 and the earliest dated T0 run in `audit/T0-FINDINGS.md` is run #3 on 2026-10-05 (earlier work is in the chat archive, not in the repository); the five steps of Phase 1 are now done. This page states what was done, what the evidence says, which decisions were taken, what is carried into Phase 2 and where each item is tracked, and what the work taught us. Numbers are quoted from the files named next to them; where something was inferred or not checked, it says so.

## 1. What was done

| Step | Result | Where |
|---|---|---|
| 1.0 Reference environment | WorldDynamics.jl v1.0.0 pinned in a Julia 1.10 environment resolved from the General registry as of 2024-04-25 (273 packages); Earth4All.jl audited at commit `16f37d0`; PyWorld3 1.1 pinned in `pyproject.toml`/`uv.lock` | `audit/env/`, `audit/REFERENCES.md`, D-017 |
| 1.1 T0 sanity check | World3 reproduced in the pinned environment with default solver options; the package's own test suite passes there. Earth4All.jl compared with the Vensim output through the package's own metric, with deviations reported | `audit/T0-FINDINGS.md`, D-017, D-018 |
| 1.2 Earth4All audit T1–T4 | All four tests run on both scenarios | `audit/earth4all-audit.md` |
| 1.3 Audit verdict | Per-sector verdict approved | D-016 |
| 1.4 World3 population sector in Python (S1) | Port of both parameter sets (1974, 2004); 22 tests pass locally and in CI | `f3/sectors/s1_population.py`, `audit/s1-port-report.md`, D-015, D-019 |
| 1.5 Phase review | This page; the UN age-cohort check left open in D-015 | D-015 outcome note |

## 2. The evidence in one page

**World3 reproduces, but only in a dated environment.** WorldDynamics.jl solves World3 with default options with the April and July 2024 dependency sets, and fails from October 2024 (`InitialFailure` from January 2025). In the pinned environment the twelve main stocks are within 1.70% of fine-step PyWorld3 once PyWorld3's pollution-delay start-up is matched (worst: persistent pollution in 2100). As shipped, PyWorld3 differs by 373.7% in pollution in 1906; the cause, confirmed by changing only that start value, is its delay start-up (`Delay3` starts at `input × 3 / delay`). The cause of the break between ModelingToolkit 9.22 and 9.41 was not investigated.

**Earth4All.jl is a close numerical copy of Vensim for most variables, not all.** Typical error about 1e-4 by the package's own metric (487 variables); 21% (Too Little Too Late) and 13% (Giant Leap) of variables have a 95th-percentile error above 1%, mostly demand, energy and labour-market flows. Of the six headline variables, the **well-being index misses D-004's ±2%** (4.37% TLTL, 2.77% GL) and inequality is borderline (1.96%; worst-case bound 2.4%). Reported openly, as D-018 requires.

**The Earth4All audit (D-010's tests).** T1: no death flow below age 60, by design; no cohort stock goes negative before 2100. T2: workforce never exceeds working-age population in any of 121 years, under one reading of "employed" and "working age". T3: of 40 explicit time-driven equations, 9 are behaviour forcing (climate 2, foodland 5, population 2) and none is in output, demand, inventory, finance, public or energy; switching off the two SSP2 population ramps changes 2100 population by 28%. T4: Too Little Too Late runs to 2200; Giant Leap becomes unstable at 2197.3.

**The two World3 parameter sets share the same equations.** The 2004 variant differs in one parameter, five population tables or parameters, one agriculture parameter and table, and one resource table (D-015, finding 1). Total population: the 2004 set is nearer observed (2025: 7.52 bn against 8.23 bn at 1 July, −8.6%; the 1974 set 7.06 bn, −14.3%). **Age structure points the other way**: the 2004 set has 8.5% aged 65+ in 1970 (observed 5.3%) and 16.8% in 2025 (projected 10.3%); the 1974 set is 7.1% and 12.8%. The 2025 UN values are medium-variant projections, not counts.

**The port reproduces the reference.** Against WorldDynamics.jl (default options): all 15 states within 0.25% (2004 set) and 1.57% (1974 set; that figure is in a delay stage, where the reference's own solver differs from its tight-tolerance run by 1.61%). Key variables (cohorts, life expectancy, births, deaths, fertility) within 0.21%. Against unmodified PyWorld3 from the same start: cohorts within 0.1%. Started from WorldDynamics.jl's own state, the total differs by up to 0.74% (1974) and 1.75% (2004, diagnostic override), a start-up effect, not an equation difference. No equation was changed.

**Starting in 1970.** Restarting from the 1900 run's 1970 state reproduces the full run to within 0.11% (1974) and 0.006% (2004). Rescaling the cohorts to the observed 1970 total did not improve the 2004 set's later fit (2025: −8.6% → −11.0%); it improved the 1974 set by about one point.

> **Note, 2026-10-08 (correction; the sentence above is unchanged).** "It improved the 1974 set by about one point" does not hold under the time convention adopted in D-022 (`t = Y` is 1 January). The 1974 set's 1970 total (3.657 bn) already equals the UN 1 January total (3.657 bn), so rescaling the cohorts changes nothing for it; the one-point gain came from comparing with the UN 1 July value. For the 2004 set the finding stands and is slightly stronger (2025: −8.2% becomes −11.5%, against −8.6% and −11.0% in the sentence above). The figures in this paragraph for the 2004 set (−8.6% → −11.0%) are on the 1 July basis. See the outcome note on D-019 for the table and `docs/time-convention-evidence.md` for the date bases. The conclusion of the paragraph and the decision it supports (D-019 Option C) are unchanged.

## 3. Decisions taken in Phase 1

Twelve approved (D-001, D-003, D-004, D-010, D-011, D-012, D-014, D-015, D-016, D-017, D-018, D-019; D-015 with an amendment), two superseded (D-002 by D-011, D-013 by D-017), five still Proposed for later phases (D-005 to D-009). In the order they bear on the work: **D-017** pinned dated environment, default options, with acceptance conditions fixed before the checks; **D-018** Earth4All.jl is the reference and deviations from Vensim are reported, not tolerated away; **D-016** replace population, climate, foodland and wellbeing; reuse output, inventory, finance; reuse demand, public and energy with changes; labour market provisionally; **D-015** both World3 parameter sets in one codebase, the 2004 set provisional default, confirmed at the Phase 3 backtest on 2000–2025; **D-019** World3-based sectors start from the model's own state until the Phase 3 calibration (Option C). All entries are in `DECISIONS.md`.

## 4. Open issues carried into Phase 2

| # | Issue | Where tracked |
|---|---|---|
| 1 | AI-sector integration approach (S3) | D-005 (Proposed), `MODEL_SPEC.md` S3 |
| 2 | Critical-minerals granularity | D-006 (Proposed) |
| 3 | Climate damage function, which also decides how warming reaches the reused Earth4All sectors (seven warming-effect feedback switches need a FaIR warming input) | D-007 (Proposed), `MODEL_SPEC.md` note under the sector map |
| 4 | Historical proxy for social tension | D-008 (Proposed), research in `research/SOURCES.md` |
| 5 | Dashboard stack | D-009 (Proposed, Phase 4) |
| 6 | Demand sector: a component-level comparison with Vensim before it is relied on (half its variables deviate at the 95th percentile) | D-016, `MODEL_SPEC.md` S2 |
| 7 | Public sector: expose `EDROTA2022` (non-zero in both scenarios) as a documented parameter | D-016, `MODEL_SPEC.md` S2 |
| 8 | Labour market is reused provisionally; reconsider when S3 is specified | D-016, `MODEL_SPEC.md` S2 |
| 9 | Age structure must be a backtest criterion, not only total population: the 2004 set's total is nearer but its 65+ share is too high | D-015 outcome note (2026-10-08) |
| 10 | D-015's other open check: the book's tables and Herrington's Supporting Information are unread | D-015 amended Decision, `docs/STATUS.md` |
| 11 | Only the population sector is ported. Agriculture, capital, non-renewable resources and pollution exist in Python only as recorded inputs from a Julia run, so F3 cannot yet run World3 end to end | `MODEL_SPEC.md` S1 and S5. **Not yet tracked in a decision or a handover prompt** |
| 12 | **Resolved 2026-10-08.** The Earth4All.jl audit environment is pinned in `audit/env-earth4all/` (Project.toml and Manifest.toml); the scripts and the T0 workflow install from it. Re-run of the error statistics and of T1b, T2, T3 counterfactual and T4: results identical (largest difference 1.8e-15 relative) | `audit/env-earth4all/`, `audit/REFERENCES.md`, `audit/earth4all-audit.md` (environment note) |
| 13 | Earth4All: whether Vensim has the same `22022 + IPP` ramp end and the two `2020 + IPP` ramp ends was not checked (`vensim_source/` is not used, D-014) | `audit/earth4all-audit.md`, latent observations |
| 14 | The other 18 policy inputs of the T3 classification were not re-read; T2's definition and T4's plausible-range criteria are the audit's own | D-016 outcome note; `audit/earth4all-audit.md` |
| 15 | Whether to report the WorldDynamics.jl break (ModelingToolkit 9.22 → 9.41) to its maintainers | `docs/STATUS.md`, open question 2 |
| 16 | World3's time convention within a year (is `t = 1970` the start or the middle?) was not checked; it moves population gaps by up to about one point | D-015 outcome note |
| 17 | Automation of audit reports and CI, and deletion of the superseded `audit-world3-pins.yml` | `docs/HANDOVER.md`, Prompt 5 |
| 18 | **Refreshed 2026-10-08 (Prompt 6 has run).** *Verified* against primary pages: GATE paper versions and licence (arXiv), IEA *Key Questions on Energy and AI* (date, CC BY 4.0, executive-summary figures), Global Carbon Budget 2025 (published paper, CC BY 4.0), Epoch data hub (licence wording), USGS data-release metadata (public domain), UCDP (CC BY 4.0, coverage). Two earlier register entries were corrected (the IEA "465 TWh" AI-focused figure is withdrawn; the carbon-budget row now uses the published paper). WPP 2026 is postponed to 2027 (found by search; the UN document was not opened). *Blocked*, automated access refused (HTTP 403, 404 or empty): the LBNL data-centre water report, the TSMC 2024 sustainability report, the WID terms of use, the ILOSTAT licence; so the water figures are unverified and WID and ILOSTAT terms are unknown (do not assume CC BY). *Still open*: the UN WPP licence is not stated on the pages read; the GCB paper was read only to its first 100,000 characters (the 1.36 °C and 42.4 GtCO2 figures are unverified); the USGS report PDF was not read; the Epoch June 2026 data-centre insight, the FaIR version and the WPP 2026 postponement document were not re-checked; no sector-wide water-per-wafer figure and no open historical social-tension proxy from 1970 were found; Epoch's GitHub organisation was not browsed for a GATE repository. | `research/SOURCES.md`; `DECISIONS.md` D-008 evidence note |

Items 11 and 12 had no home before this review; item 12 has since been resolved (see its row), and item 11 is carried into the Phase 2 plan as milestone 0.

## 5. Lessons learned

1. **Check the first reading of a number.** Four of our own early statements were wrong and were corrected in the log rather than deleted: the first dependency search pinned only ModelingToolkit and tested nothing about dependency eras; the first Earth4All scan counted test-scaffolding systems (184 time-driven equations; the real figure is 40); the UN population file's "1 January" note was repeated for values that are mid-year (caught by the editor-in-chief); and the 2025 population values were called "observed" although they are projections.
2. **Fix the acceptance conditions before looking.** D-017's three conditions were written before the follow-up checks and were then reported as met or not met; D-004's ±2% was reported as missed for well-being rather than relaxed.
3. **The package's own error metric can hide errors.** `all_mre` divides by `|vensim| + 1`, which hides relative errors of variables of order 1; maxima are dominated by isolated timing spikes. Always convert to true relative error and report median and 95th percentile.
4. **Compare by name, never by position.** The two Julia environments list the 29 World3 states in different orders.
5. **A reference has its own error.** WorldDynamics.jl's default solve differs from its tight-tolerance solve by up to 1.61% in one delay stage; PyWorld3 at its default step has errors of up to 11.6% for early pollution. Quote the yardstick's own error beside every comparison.
6. **Separate start-up conventions from equation differences.** Both the PyWorld3 pollution delay and the port's initial state came down to start values, not equations; the port starts from the reference's own initial state and says so.
7. **A pass on one criterion can hide a failure on another.** The 2004 parameter set is closer on total population and worse on age structure. Total population alone would have chosen it without showing that.
8. **Read primary documents in full.** Abstracts and search summaries were not enough for Herrington (2021) (scenario definitions, data sources); reading the article text answered what the summaries could not. The Supporting Information and Turner's papers are still unread.
9. **Practicalities.** Julia package installs on a new environment take 15–30 minutes, so local runs are preferable to CI for development. Scripts passed through shell quoting broke repeatedly; writing them to files first avoided it. A Windows installer lock (`juliaup add 1.10`) needed one retry.
