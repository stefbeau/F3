# F3 — Decision Log

Every assumption, parameter choice and design choice in F3 is recorded here. Nothing enters the model without an entry.

**Rules**

1. Any agent or contributor can **propose** a decision.
2. Only the editor-in-chief (Stéphane Beau) can **approve**, **reject** or **supersede** one.
3. Approved decisions are never edited. To change one, add a new entry that supersedes it and link both.
4. Each entry cites its sources. "Seems reasonable" is not a source.

**Status values:** `Proposed` · `Approved` · `Rejected` · `Superseded by D-xxx`

---

## Summary

| ID | Title | Status | Phase |
|---|---|---|---|
| D-001 | Licensing | Approved | 0 |
| D-002 | Earth4All integration route | Superseded by D-011 | 0 |
| D-003 | Internal time step | Approved | 0 |
| D-004 | Reproduction tolerance | Approved | 0 |
| D-005 | AI sector integration approach | Proposed | 2 |
| D-006 | Critical minerals granularity in v0.1 | Proposed | 2 |
| D-007 | Climate damage function | Proposed | 2 |
| D-008 | Social tension historical proxy | Proposed (research needed) | 3 |
| D-009 | Dashboard stack | Proposed (deferred) | 4 |
| D-010 | Scientific robustness of Earth4All as a baseline | Approved | 1 |
| D-011 | Earth4All reference implementation (supersedes D-002) | Approved | 0 |
| D-012 | World3 reference implementation | Approved | 1 |
| D-013 | WorldDynamics.jl solver configuration | Superseded by D-017 | 1 |
| D-014 | Use of the Vensim output shipped with Earth4All.jl | Approved | 1 |
| D-015 | World3 variant for F3's population sector: 1974 or 2004 parameter set | Approved with amendment | 1 |
| D-016 | Earth4All audit verdict: which components F3 reuses, changes or replaces | Approved | 1 |
| D-017 | World3 reference environment: dated registry snapshot, default solver options | Approved; condition (a) met 2026-10-07 | 1 |
| D-018 | Earth4All.jl is the Earth4All reference implementation; deviations from Vensim reported | Approved | 1 |
| D-019 | How F3 initialises its stocks in 1970 | Proposed | 1 |

---

## D-001 — Licensing

- **Status:** Approved
- **Context:** F3 is meant to be open and reusable, and it reuses existing models whose licenses must be respected.
- **Proposal:** Code under Apache 2.0. Documentation and processed data under CC BY 4.0. Raw third-party data keeps its original license, recorded in each data card.
- **Alternatives considered:** MIT for code (simpler, but without Apache's explicit patent grant); GPL (would restrict reuse by organizations).
- **License check (2026-10-04):**

  | Component | License found | Compatible with Apache 2.0 for F3? |
  |---|---|---|
  | PyWorld3 (World3, 1974 version) | CeCILL 2.1 (French copyleft, GPL-compatible) | **Only as an unmodified external dependency.** Copying or modifying its code inside F3 would likely pull F3 under copyleft terms. |
  | Earth4All.jl (Julia port, validated against Vensim) | MIT | Yes |
  | Earth4All original Vensim model | Described as open source by Earth4All; no explicit license found | **Unclear.** Ask the Earth4All team before redistributing the model files. |
  | GATE (Epoch AI) | No public source code found; model described in arXiv paper and online playground | Re-implementation from the paper (with citation) is the only route. |
  | Epoch AI datasets | CC BY | Yes, with attribution |
  | FaIR | Apache 2.0 | Yes |
  | PySD | Not yet checked | To confirm |

- **Consequences:**
  1. F3 does not copy PyWorld3 code. It either installs PyWorld3 unmodified for reproduction tests only, or re-implements World3 from the published equations.
  2. For Earth4All, the MIT-licensed Earth4All.jl is the cleaner reference (see D-002).
  3. This is a practical reading of the licenses, not legal advice. Confirm with a lawyer or the projects' maintainers before public launch.
- **Sources:** github.com/cvanwynsberghe/pyworld3; github.com/worlddynamics/Earth4All.jl; arXiv:2503.04941; epoch.ai data licensing pages; github.com/OMS-NetZero/FAIR.
- **Decision:** Approved by Stéphane Beau
- **Date:** 2026-10-04

## D-002 — Earth4All integration route

- **Status:** Superseded by D-011 (2026-10-04)
- **Context:** Earth4All is published as a Vensim model. Recoding it by hand risks introducing errors.
- **Proposal:** Run the published model in Python through PySD and treat it as the S1/S2/S4/S7 baseline.
- **Alternatives considered:**
  - Full manual re-implementation in Python from scratch (more control, much higher error risk and effort).
  - **Port from Earth4All.jl** (added after the D-001 license check): an MIT-licensed Julia implementation already validated against the Vensim runs. Porting it to Python avoids the unclear license of the original Vensim files and gives a tested reference.
- **Risk:** PySD may not support every Vensim function the model uses; any gap gets its own decision entry.
- **Decision:** Approved by Stéphane Beau
- **Date:** 2026-10-04

## D-003 — Internal time step

- **Status:** Approved
- **Proposal:** Integrate at 0.25 year and report results yearly.
- **Rationale:** Matches common practice in World3-family models and keeps fast loops (investment, compute growth) numerically stable.
- **Check:** Validator agent confirms that results do not change materially at 0.125 year.
- **Decision:** Approved by Stéphane Beau
- **Date:** 2026-10-04

## D-004 — Reproduction tolerance

- **Status:** Approved
- **Proposal:** A reproduction passes when key variables stay within ±2% of the published source run at every reported year.
- **Key variables:** Population, industrial output or GDP, resources, pollution or emissions, and well-being indices where the source model reports them.
- **Decision:** Approved by Stéphane Beau
- **Date:** 2026-10-04

## D-005 — AI sector integration approach

- **Status:** Proposed
- **Context:** GATE determines investment through an optimization step that does not fit naturally into a system dynamics model.
- **Proposal:** Re-implement GATE's three modules (AI development, automation, growth) in simplified form, replacing the optimization with a behavioral investment rule. Check against GATE sandbox presets (MODEL_SPEC §7.3).
- **Alternatives considered:** Coupling to GATE's own code (harder to integrate and maintain).
- **Decision:** —
- **Date:** —

## D-006 — Critical minerals granularity in v0.1

- **Status:** Proposed
- **Proposal:** One aggregate critical-minerals index in v0.1. Split into named minerals (candidates: copper, lithium, gallium, rare earths) in v0.2.
- **Decision:** —
- **Date:** —

## D-007 — Climate damage function

- **Status:** Proposed
- **Context:** Estimates of economic damage from warming differ widely across the literature, and the choice strongly shapes results.
- **Proposal:** Do not pick one. Offer three options (low / central / high) as a scenario lever, each traced to a published source.
- **Decision:** —
- **Date:** —

## D-008 — Social tension historical proxy

- **Status:** Proposed (research needed)
- **Context:** The Social Tension Index needs observed data to backtest against.
- **Proposal:** Research agent compares candidate datasets (political instability indices, protest-event data) on coverage since 1970, global scope and licensing, then proposes one.
- **Decision:** —
- **Date:** —

## D-009 — Dashboard stack

- **Status:** Proposed (deferred to Phase 4)
- **Candidates:** Streamlit (live runs, simplest); static site with precomputed scenario runs (cheapest to host, fastest for users).
- **Decision:** —
- **Date:** —

## D-010 — Scientific robustness of Earth4All as a baseline

- **Status:** Approved
- **Context:** Found during the D-001 check. A review of the Earth4All global model (E4A) by K. V. Ragnarsdóttir, H. Sverdrup, H. Haraldsson and B. Kopainsky (January 2024, revised March 2024) is hosted on the Earth4All website. Earth4All published a Science and Modelling FAQ (April 2024) plus separate responses from its modelling team and from Jørgen Randers. The scenarios were later published in *Global Sustainability* (Cambridge).

### Context on both sides

- The review is a letter to the Club of Rome co-presidents, not a peer-reviewed paper. One of its authors (Sverdrup) leads the competing WORLD7 model.
- The Earth4All team does not dispute that the model is highly aggregated. It argues the model was built to illustrate scenarios and improve structural understanding, not to forecast, and should not be run beyond its 2100 design horizon. It reports calibration on 1980–2020 data.
- Many of the review's claims are factual statements about model structure. They can be **tested directly** on Earth4All.jl, so F3 does not need to take either side on trust.

### Classification for F3

| # | Review claim | Assessment | Relevance to F3 | Action |
|---|---|---|---|---|
| 1 | Population cohorts below 60 have no mortality; cohort stocks can go negative | Testable; serious if true | High (S1) | Use **World3's population sector** for S1 instead of E4A's. Verify claim (test T1). |
| 2 | Energy sector has only two capacity stocks and no material limits on renewables | Consistent with E4A's own structure description | High (S4, S5) | Keep E4A energy as a starting point, but couple it to F3's materials sector (already planned). |
| 3 | No natural resources of any kind | Consistent with E4A's sector list | High (S5) | Already covered: F3 uses World3 resources plus new modules. |
| 4 | No carbon mass balance or real climate model | Plausible; testable | Neutralized | F3 uses **FaIR** for S6. |
| 5 | Agriculture lacks food supply, prices and nutrient balances | Partly testable; partly a scope disagreement | Medium (S1 food) | Use World3's agriculture sector in v0.1; revisit in v0.2. |
| 6 | Labor market shows more employed people than working-age population after 2040 | Testable; serious if true | **Critical** (automation → labor is F3's core link) | Verify (test T2). If confirmed, F3 builds its own labor module. |
| 7 | Many outcomes driven by time-based forcing functions rather than feedback | **Disputed.** E4A authors cite calibration and structural intent | **Critical** (F3's value is endogenous feedback) | Audit every time-driven or table-forced variable in sectors F3 would reuse (test T3). |
| 8 | Model becomes unstable after 2100 | Testable; E4A says not to run past 2100 | Low (F3 stops at 2100) | Keep as an extreme-condition test (T4). |
| 9 | Well-being and social trust lack stocks; definitions differ from literature | Partly modeling choice, partly literature dispute | High (S7) | Redesign S7 with explicit stocks; use E4A's Social Tension Index as inspiration only. |
| 10 | Book's five turnarounds and policy claims are not represented in the model | About the book, not the model's mechanics | Not relevant | None |

### Tests for the Validator agent (Phase 1, on Earth4All.jl)

- **T1:** Check mortality in each population cohort; run 1980–2100 and record the minimum value of each cohort stock.
- **T2:** Compare employed population with working-age population for 1980–2100 in both scenarios.
- **T3:** List every variable that depends directly on time or on a lookup table, by sector.
- **T4:** Run to 2200 and record where and when instability appears.

### Proposal

Demote Earth4All from "baseline for four sectors" to **"reference model and component library."** Revised sector origins:

| Sector | Was | Proposed |
|---|---|---|
| S1 Population & well-being | World3, Earth4All | **World3** population (+ well-being redesigned in S7) |
| S2 Economy & capital | Earth4All | Earth4All demand/output structure **only after T2 and T3 pass**; GATE production function for automation |
| S4 Energy | Earth4All, extended | Earth4All capacity structure, **coupled to S5 material limits** |
| S7 Social stability | Earth4All, Turchin | New F3 module with explicit stocks, informed by Earth4All and Turchin |

Also consider the **WORLD7** model (Sverdrup et al.) as a reference for S5 metals and materials, subject to availability and license.

- **Sources:** Ragnarsdóttir et al., *A scientific review of the Earth4All model* (earth4all.life, March 2024); Earth4All, *Science and Modelling FAQ* (April 2024); Crescenzi et al. (2024), *Journal of Industrial Ecology*; Earth4All scenarios article, *Global Sustainability* (Cambridge).
- **Decision:** Approved by Stéphane Beau
- **Date:** 2026-10-04

## D-011 — Earth4All reference implementation (supersedes D-002)

- **Status:** Approved
- **Context:** D-002 (approved) runs Earth4All's Vensim files through PySD. Two later findings conflict with it:
  1. The D-001 license check found no explicit license on the original Vensim files, while Earth4All.jl is MIT-licensed.
  2. D-010 demotes Earth4All to a reference library audited by tests T1–T4, so F3 no longer needs to run the whole Earth4All model in Python.
- **Proposal:**
  1. Use **Earth4All.jl** (MIT) as F3's only Earth4All reference. Its authors validated it against the Vensim version.
  2. Run the D-010 audit tests T1–T4 **in Julia, on Earth4All.jl as published**. No translation before auditing, so no translation errors can distort the audit.
  3. Port to Python **only the components that pass the audit**, one at a time. Each port must match Earth4All.jl outputs within ±2% (D-004) before use.
  4. Do not download, store or redistribute the original Vensim files in the F3 repository.
- **Consequences:**
  - Julia is added to the toolset for the Validator agent (audit only; F3 itself stays in Python).
  - PySD is no longer needed for Earth4All. It stays available for any future Vensim-format model with a clear license.
  - D-002 is superseded by this decision.
- **Alternatives considered:** Keep D-002 and ask the Earth4All team for an explicit license (slower, and still requires auditing a model F3 only partly reuses).
- **Sources:** D-001 license check; D-010 review; github.com/worlddynamics/Earth4All.jl.
- **Proposed by:** Claude (Research agent role)
- **Decision:** Approved by Stéphane Beau
- **Date:** 2026-10-04

## D-012 — World3 reference implementation

- **Status:** Approved
- **Context:** Found while preparing Phase 1. WorldDynamics.jl, from the same research group as Earth4All.jl (Université Côte d'Azur, Inria, CNRS), is **MIT-licensed**. It implements World3 and reproduces figures from *Dynamics of Growth in a Finite World*, and it also contains an Earth4All implementation. Under D-001, F3 can only use PyWorld3 (CeCILL 2.1) unmodified, which forces a re-implementation of World3 from the book's equations — the most error-prone route.
- **Proposal:**
  1. Use **WorldDynamics.jl** (pinned to v1.0.0) as F3's World3 reference.
  2. Port World3 sectors to Python **from WorldDynamics.jl code**, with MIT attribution in each ported file and in `NOTICE`.
  3. Keep PyWorld3, installed unmodified, as an **independent second check**: a port passes only if it matches WorldDynamics.jl within ±2% (D-004), and any gap with PyWorld3 is explained.
  4. Both Julia references (WorldDynamics.jl, Earth4All.jl) stay outside the F3 repository and are pinned by version or commit in `audit/`.
- **Consequences:** F3's whole reference toolchain is MIT; two independent implementations of World3 cross-check each other; the "re-implement from the book" route in MODEL_SPEC S1 is replaced by "port with attribution."
- **Risk:** WorldDynamics.jl's last release (v1.0.0) dates from April 2024; pinning the version protects reproducibility.
- **Alternatives considered:** Re-implement from the book (higher error risk); use PyWorld3 code (not allowed under D-001).
- **Sources:** github.com/worlddynamics/WorldDynamics.jl; Crescenzi et al. (2024), *Journal of Open Source Software* 9(95), 5772.
- **Proposed by:** Claude (Research agent role)
- **Decision:** Approved by Stéphane Beau
- **Date:** 2026-10-04

## D-013 — WorldDynamics.jl solver configuration

- **Status:** Superseded by D-017 (2026-10-07). Never approved; the `NoInit()` configuration is not used by F3.
- **Context:** With the dependency versions that install today (ModelingToolkit 9.84.0, DifferentialEquations 7.17.0, OrdinaryDiffEq 6.105.0, SciMLBase 2.153.1), `WorldDynamics.solve` on the World3 system returns `InitialFailure` and a single time point. The package's own warning says its initialization system is overdetermined (16 equations for 7 unknowns). With `initializealg = NoInit()` the same call returns `Success` over 1900–2100. Only a solver option changes; no equation, parameter or package file does. T0 run #5 population results: all solver variants within 0.5–0.7% (max) of PyWorld3 run at a fine time step; tightening the solver tolerance to 1e-8 did not bring the result closer (0.67% vs 0.53%), so the remaining gap is not a WorldDynamics.jl tolerance effect. Its cause is not yet explained.
- **Proposal:**
  1. F3 uses WorldDynamics.jl only with `initializealg = NoInit()` and saves the solution every 0.5 year. This is a documented deviation from the package defaults.
  2. The dependency versions of an approved audit run are pinned by committing `audit/env/Project.toml` and `Manifest.toml`.
  3. **Acceptance condition:** the decision is approved only if T0 run #6 shows all twelve main stocks within ±2% of the fine-step PyWorld3 run (dt=0.05), with the largest gaps explained in `audit/T0-FINDINGS.md`.
  4. With the editor-in-chief's agreement, the `InitialFailure` behaviour is reported to the WorldDynamics.jl maintainers as an issue.
- **Run #6 result (2026-10-05):** eleven of twelve stocks are within ±2% of the fine-step PyWorld3 run (largest: ic 1.95%). Persistent pollution `ppol` is not: 373.7% maximum, 22.7% mean, largest in 1906. Likely cause (checked only on PyWorld3 so far): PyWorld3's `Delay3` starts the pollution-appearance delay at 15% of its input, while WorldDynamics.jl starts it at steady state. Details and caveats in `audit/T0-FINDINGS.md`. The original condition is left unchanged above; any revised condition is a new proposal for the editor-in-chief, not a retroactive pass.
- **Revised proposal (2026-10-05, after the run #6 data was analysed; this is a post-hoc revision and is labelled as such):**
  1. *Finding:* the `ppol` gap is a start-up difference of the pollution-appearance delay between the two implementations, not a solver effect. Starting PyWorld3's delay at the WorldDynamics.jl value (one change, a documented diagnostic, PyWorld3 code untouched) brings `ppol` from 373.7% to 1.69% and keeps all twelve stocks within 1.4% (details in `audit/T0-FINDINGS.md`).
  2. *Revised acceptance condition:* WorldDynamics.jl with `NoInit()` is accepted as F3's World3 reference for the 1974 model if, against fine-step PyWorld3 with that diagnostic start-up, all twelve main stocks stay within ±2% (**met: worst 1.69%**), and the as-shipped PyWorld3 comparison is always reported alongside (**fails for `ppol`, explained above**).
  3. *Known limitation:* neither implementation starts the delay at the steady state of the model's own initial value; WorldDynamics.jl is 8.9% above it. This is to be handled in step 1.4 by testing the Python port from the same initial state as the reference.
  4. *Why this is weaker than the original condition:* the criterion was chosen after seeing the result, and it relies on a diagnostic modification of PyWorld3 that I designed. The editor-in-chief may therefore prefer to reject D-013 as written, or to approve it and require a further independent check (for example, comparison with the book's printed Figure 7.7).
- **Editor-in-chief's direction (2026-10-05):** "I want a version that works!" Read as: prefer a dependency set in which World3 solves with default options over the `NoInit()` workaround. A first pinned-dependency search (ModelingToolkit only) was inconclusive because it left all other packages at their newest versions; a registry-snapshot search (`.github/workflows/audit-world3-snapshot.yml`, whole dependency stack resolved as of a given date) replaces it. D-013 stays Proposed until its result is reviewed, then is approved, rejected or superseded explicitly.
- **Alternatives considered:** Pin older versions of the dependencies the package was built against (April 2024), which needs a separate experiment (now under way, see above); port World3 from the book's equations without the package (highest error risk).
- **Sources:** T0 runs #3–#5 (`audit/T0-FINDINGS.md`); WorldDynamics.jl v1.0.0 `src/solvesystems.jl`.
- **Proposed by:** Claude (Validator agent role)
- **Decision:** —
- **Date:** —

## D-014 — Use of the Vensim output shipped with Earth4All.jl

- **Status:** Approved
- **Context:** The Earth4All.jl repository (MIT-licensed, `LICENSE`: "Copyright (c) 2023 World Dynamics") contains `VensimOutput/{tltl,gl}/<sector>.txt` (twelve files per scenario) and `vensim_source/` (two `.mdl` model files). Its function `Earth4All.all_mre` compares the Julia solution with that Vensim output variable by variable (error metric |julia − vensim| / (|vensim| + 1)). It is not part of any test suite; the repository has no test folder. D-011 keeps the original Vensim files out of the F3 repository because their licence status is unclear.
- **Proposal:**
  1. The audit may read `VensimOutput/` from a clone made at run time, to run the package's own `all_mre`. This is the numeric check that Earth4All.jl matches Vensim.
  2. Nothing from `VensimOutput/` or `vensim_source/` is copied into the F3 repository or into stored results. Stored results contain only per-variable error figures and variable names.
  3. `vensim_source/` is not used at all.
- **Alternatives considered:** Ask the Earth4All team for explicit permission first (slower); skip the numeric check and rely on visual comparison only (weaker).
- **Sources:** `src/functions.jl` and `LICENSE` of Earth4All.jl at commit `16f37d0`.
- **Proposed by:** Claude (Research agent role)
- **Decision:** Approved by Stéphane Beau (run #6 had already executed the step; approval given afterwards, on 2026-10-05, after the results were reviewed)
- **Date:** 2026-10-05

## D-017 — World3 reference environment: dated registry snapshot, default solver options (supersedes D-013)

- **Status:** Approved (2026-10-07). Condition (a) is tested by the next T0 run; if it fails, this decision is reopened.
- **Context:** The editor-in-chief asked for "a version that works" (2026-10-05). A search over Julia registry snapshots (`audit/T0-FINDINGS.md`, "Registry-snapshot search #1") found that WorldDynamics.jl v1.0.0 solves World3 with default solver options in the dependency sets of 2024-04-25 (ModelingToolkit 9.12.1, SciMLBase 2.35.0, OrdinaryDiffEq 6.74.1) and 2024-07-01 (9.22.0, 2.42.0, 6.85.0), and not in later ones. In the working stacks the PyWorld3 cross-check numbers equal those obtained with `NoInit()` on the newest stack.
- **Proposal:**
  1. F3's World3 reference environment is Julia 1.10 with the packages resolved from the General registry as of **2024-04-25** (registry commit `ec06aa53f5a2d5c46f7d70440c86911050375882`), the one closest to the package's release (2024-04-18).
  2. WorldDynamics.jl is run with **default solver options**. `NoInit()` is not used.
  3. The environment is pinned by committing the `Project.toml` and `Manifest.toml` of that job (artifact `world3-snap-2024-04-25`) to `audit/env/`; later audit runs install from them with `Pkg.instantiate()`.
  4. **Acceptance conditions, fixed before the follow-up checks:** (a) in a fresh run that uses only the committed Manifest, the default-option solve returns `Success` with at least 401 saved points (saveat 0.5); (b) its twelve main stocks agree with the `NoInit()` solution of the newest stack within 0.1% at every saved time (this tests whether the earlier workaround changed the solution); (c) against fine-step PyWorld3 with the diagnostic start-up, all twelve stocks stay within ±2% (already seen: worst 1.70%), and the as-shipped comparison is reported alongside (`ppol` 373.7%, explained by the start-up difference).
  5. With the editor-in-chief's agreement, the evidence (working until the 2024-07-01 snapshot; a different error at 2024-10-01; `InitialFailure` from 2025-01-15) is reported to the WorldDynamics.jl maintainers as an issue.
  6. D-013 is withdrawn in favour of this decision.
- **Check results (2026-10-06, from the artifact of the 2024-04-25 job):** (a) not yet testable; the Manifest is committed and the T0 workflow installs from it, so the next run tests it; (b) **met**, worst 0.0143% over the twelve stocks (default vs `NoInit()` on the same stack: identical); (c) **met**, worst 1.70% with the diagnostic start-up. Details in `audit/T0-FINDINGS.md`. If (a) fails in the next run, this decision is reopened.
- **Condition (a) result (2026-10-07, local run on the editor-in-chief's machine, from the committed Manifest alone):** met. The default-option solve returns `Success` (73 saved points with no `saveat`; 401 with `saveat = 0.5`), the twelve main stocks are within 1.70% of fine-step PyWorld3 with the diagnostic start-up (as shipped: `ppol` 373.70%), and the package's own test suite passes in this environment. Details in `audit/T0-FINDINGS.md`, "Local verification". Status unchanged.
- **Known limitations:** the start-up difference between WorldDynamics.jl and PyWorld3 in the pollution delay is unchanged (WorldDynamics.jl starts 8.9% above steady state, see D-013's run #6 result) and is handled in step 1.4 by testing the Python port from the same initial state as the reference. The cause of the break between July and October 2024 was not investigated. An environment from 2024 will age; the committed Manifest keeps it reproducible but not maintained.
- **Alternatives considered:** `NoInit()` on the newest stack (D-013), set aside by the editor-in-chief's direction; the 2024-07-01 snapshot (also works; newer, but further from the package's release); porting World3 from the book's equations without the package (highest error risk).
- **Sources:** snapshot search run #1 (2026-10-06), `audit/T0-FINDINGS.md`.
- **Proposed by:** Claude (Validator agent role)
- **Decision:** Approved by Stéphane Beau. D-013 is superseded.
- **Date:** 2026-10-07

## D-018 — Earth4All.jl is F3's Earth4All reference implementation; deviations from Vensim are reported, not tolerated away

- **Status:** Approved (2026-10-07)
- **Context:** T0 showed that Earth4All.jl reproduces the Vensim output closely for most variables but not within D-004's ±2% for all headline variables. True relative error at the worst point: Average WellBeing Index 4.37% (Too Little Too Late, 2077) and 2.77% (Giant Leap, 2058), with a worst-case bound of 4.7% and 4.3%; inequality index 1.96% and 1.74% (bound 2.4% and 2.2%); population, GDP per person, social tension and warming are within 2%. About 21% (TLTL) and 13% (GL) of the 487 variables have a 95th-percentile error above 1e-2, concentrated in the demand, energy and labour-market flow variables. Details in `audit/T0-FINDINGS.md`. The well-being index oscillates, so small timing differences of the oscillations produce errors of a few percent at the peaks; whether that is the cause was not tested.
- **Decision (as proposed by Claude and approved by the editor-in-chief):** F3 treats Earth4All.jl (commit `16f37d013a2f68135f03e7815bf861dbf47311f2`, D-011) as a reference implementation in its own right, and reports its deviations from Vensim openly, instead of relaxing D-004 for oscillating variables.
- **Consequences:**
  1. D-004's ±2% criterion is not applied to Earth4All.jl against Vensim. The T0 audit of Earth4All.jl is closed with these deviations logged.
  2. Wherever F3 shows or describes results derived from Earth4All, it states that Earth4All.jl follows the Vensim output closely for most variables, and gives the headline deviations (the table in `audit/T0-FINDINGS.md`). It does not claim that it "reproduces Vensim" without that qualification.
  3. Clarification of D-004 (not a change to it): its ±2% criterion remains in force for F3's own ports, for example a Python port measured against its reference implementation (World3: WorldDynamics.jl, D-012 and D-017; Earth4All components: Earth4All.jl).
  4. The D-010 audit tests (T1–T4) run on Earth4All.jl as published, which T0 supports as a close numerical copy of the Vensim model; they say nothing about whether the model itself is sound.
- **Alternatives considered:** relax D-004 to a wider band for oscillating variables (rejected by the editor-in-chief's choice: it hides a 4% gap); re-implement from the Vensim source (excluded by D-011).
- **Sources:** `audit/T0-FINDINGS.md` (run #7 error statistics, headline-variable table); Earth4All.jl `src/functions.jl` (`all_mre`).
- **Proposed by:** Claude (Validator agent role)
- **Decision:** Approved by Stéphane Beau
- **Date:** 2026-10-07

---

## D-015 — World3 variant for F3's population sector: 1974 or 2004 parameter set

- **Status:** Approved with amendment (2026-10-07)
- **Context:** Step 1.4 ports the World3 population sector (D-012) and needs to know which variant it is based on. WorldDynamics.jl v1.0.0 ships `World3` (the 1974 model; the one all T0 cross-checks used), `World3_91` and `World3_03` (the 2004 variant, *The Limits to Growth: The 30-Year Update*). PyWorld3 implements the 1974 model only. Evidence below was produced in the pinned environment `audit/env` (D-017) with default solver options, by `audit/t0/world3_variants.jl`; both runs returned `Success` with 401 points.
- **Finding 1: the two variants share the same equations.** In WorldDynamics.jl, `World3_03.scenario1()` is `World3_91.scenario1()` (which calls `World3.historicalrun()` with overridden parameters and tables) plus one more table override (`sfsn`) and two added subsystems, a human welfare index and a human ecological footprint. The two added subsystems only read from the model (life expectancy, industrial output per capita, pollution, land); nothing reads from them (`src/World3_03/world3_03/scenarios.jl`). So for the population sector, the choice is a choice of **parameters and tables, not of equations**. The complete list of differences in the five modules F3 would use (1974 → 2004):
  - population: `dcfsn` 4 → 3.8; table `fm` (0, .2, .4, .6, .8, .9, 1, 1.05, 1.1) → (0, .2, .4, .6, .7, .75, .79, .84, .87); table `lmf` (0, 1, 1.2, 1.3, 1.35, 1.4) → (0, 1, 1.43, 1.5, 1.5, 1.5); table `lmhs2` (1, 1.4, 1.6, 1.8, 1.95, 2) → (1, 1.5, 1.9, 2, 2, 2); table `sfsn` (1.25, 1, .9, .8, .75) → (1.25, .94, .715, .59, .5)
  - agriculture: `alln` 6000 → 1000; table `lymc` (higher yield response to inputs in the 2004 set)
  - non-renewable resources: table `pcrum` (lower per-capita resource use at high output in the 2004 set: 7.0 → 5.0 at the top)
  - capital and pollution: no differences.

  I did **not** check this list against the book's Appendix A or against the 2004 book's own tables; it is what WorldDynamics.jl implements. I did not find out whether the 2004 book changes anything the package does not model.
- **Finding 2: the trajectories differ, mostly in age structure and agriculture.** Differences of the 29 common states, compared by name (`audit/data/world3_variants_state_differences.csv`):

| quantity | 1970 | 2000 | 2025 | 2100 | largest over 1900–2100 |
|---|---|---|---|---|---|
| population, age 0–14 (p1) | 2.4% | 1.6% | 7.3% | 15.8% | 16.2% (2088) |
| population, age 15–44 (p2) | 3.5% | 5.5% | 2.7% | 12.6% | 12.6% (2100) |
| population, age 45–64 (p3) | 9.7% | 12.9% | 11.7% | 9.0% | 13.5% (2009) |
| population, age 65+ (p4) | 23.5% | 32.1% | 39.3% | 4.2% | 40.0% (2018) |
| industrial capital | 6.2% | 3.8% | 1.8% | 13.7% | 13.7% (2100) |
| arable land | 6.5% | 14.2% | 21.6% | 28.8% | 28.8% (2100) |
| non-renewable resources | 0.5% | 4.3% | 10.3% | 3.6% | 11.6% (2020) |
| persistent pollution | 2.8% | 11.5% | 9.4% | 25.8% | 25.8% (2100) |

  Total population (billions): 1974 model 3.66 (1970), 5.69 (2000), 7.06 (2025), 4.00 (2100), peak 7.06 in 2026; 2004 variant 3.79, 6.09, 7.52, 3.51, peak 7.53 in 2026. The peak year is the same; the 2004 variant is about 6–7% higher around the peak and falls faster after 2050.
- **Finding 3: against observed world population (UN World Population Prospects 2024, 28th edition; values from `UN_2024_WorldPop-Historical-Plot.xlsx`, downloaded 2026-10-07 from population.un.org; they are 1 July (mid-year) values, see the date note below):**

| year | observed, 1 July (bn) | 1974 model | 2004 variant |
|---|---|---|---|
| 1970 | 3.695 | 3.657 (−1.0%) | 3.792 (+2.6%) |
| 1980 | 4.448 | 4.294 (−3.4%) | 4.486 (+0.9%) |
| 2000 | 6.172 | 5.693 (−7.8%) | 6.092 (−1.3%) |
| 2010 | 7.022 | 6.396 (−8.9%) | 6.852 (−2.4%) |
| 2020 | 7.887 | 6.961 (−11.7%) | 7.402 (−6.1%) |
| 2025 | 8.232 | 7.057 (−14.3%) | 7.523 (−8.6%) |

  The models run from 1900 with no recalibration and are not forecasts, so this is a check of how far each has drifted, not a fit. Neither variant stays within D-004's ±2% of the observed series to 2025 (D-004 was written for ports against their reference, so this is a different use of the number). The 2004 variant is nearer from 1980 on; the 1974 model is nearer in 1970 only. **This checks total population only.** I did not compare the age cohorts, food, industrial output, resources or pollution with observed data, and I did not find primary data for them in this task.

  *Date basis (corrected 2026-10-08).* The spreadsheet's own note says "populations on 1 January (0h)", but its values are mid-year (1 July) values. They exceed the 1 January figures in Table A2 of the WPP 2024 Summary of Results (which states "1 January", World, thousands) by about half a year's growth: 1995 5.759 bn in the file against 5.717 in Table A2; 2024 8.162 against 8.127; 2054 9.813 against 9.796; 2100 10.180 against 10.187 (population falling by then). The Summary of Results also says that "years given refer to 1 July" unless stated otherwise. An earlier version of this entry labelled the values 1 January; that was wrong, and the label is corrected. The percentages stand: they were computed against these same values. The model values are taken at t equal to the calendar year (World3's time convention within a year is not verified); taking the model at t + 0.5 instead moves each percentage by at most 0.9 points (for example 2000: 1974 model -7.2%, 2004 variant -0.6%; 2025: -14.2% and -8.6%).

  Since 2000 both variants fall behind observed population at a similar pace (1974: -7.8% to -14.3%, 6.5 points; 2004: -1.3% to -8.6%, 7.3 points); the 2004 set's advantage was already present in 2000 and may reflect calibration with data up to about 2000 (unverified: check against the book).
- **Finding 4: which variant is used in recent comparisons with data** (revised 2026-10-08). Read in full: the 13-page article text as posted at mahb.stanford.edu (footer "Journal of Industrial Ecology 2020;1-13"; DOI 10.1111/jiec.13084; published in 25(3), 614-626). **Not read:** the Supporting Information (per-variable graphs; data in S2) and the 100-page Harvard thesis version (Branderhorst, 2020).
  - *Model and scenarios.* Herrington uses the 2004 revision: "World3-03 (henceforth called 'World3')", with four scenarios: "BAU, BAU2, CT, and SW, correspond to scenarios 1, 2, 6, and 9 in the 2004 LtG book". They were made with "the original CD-ROM that came with the 2004 book" (Vensim), not with WorldDynamics.jl. BAU is the book's scenario 1. That is what the package's `World3_03.scenario1()` is documented to reproduce (its docstring cites Chapter 4, page 169 of the 30-Year Update, one of the pages her Figure 1 cites). So her BAU is the package's `scenario1` **by the book's numbering**; I did not compare the two numerically. The package defines a `scenario1` function only for `World3_03` (checked by listing the function names), so BAU2, CT and SW are not available from it as ready-made scenarios.
  - *Population data and her own comparison.* Population comes from UN DESA Population Division, WPP 2019, "Total population - Both sexes" (the World Bank "Population, total" series is mentioned as an alternative). Empirical series are "normalized to the 1990 scenario value, because that is the year World3 was recalibrated to last (Meadows et al., 1992)". Her measures are the value difference and the rate-of-change difference at the latest data year (2020 for population) and the normalised RMSD from 1990, with uncertainty ranges of 20% (value), 50% (rate of change) and 20% (NRMSD), the same as Turner's. Her Table 2 gives, for population, a value difference of -6% (BAU), -5% (BAU2), -5% (CT) and -11% (SW), and a rate-of-change difference of -42%, -28%, -25% and -52%. These come from the extracted table text, and the population column is identified by being first. The sign follows her formula (model minus observed, over observed), so the model is below observed. This is close to my own figure for the package's 2004 `scenario1` in 2020 (-6.1% against WPP 2024, Finding 3), although the methods differ (her data are WPP 2019 normalised to 1990; mine are WPP 2024, not normalised).
  - *Data for the other variables (her section 2.4).* Fertility and mortality: World Bank crude birth and death rates. Food per capita: FAOSTAT food-balance-sheet energy per person per day. Industrial output per capita: UNIDO index of industrial production (weighted by manufacturing value added) and World Bank gross fixed capital formation, both divided by population. Services per capita: UNDP Education Index, and World Bank government spending on education and on health (% of GDP). Pollution: NOAA atmospheric CO2 minus 297 ppm, and plastic production (Geyer et al. 2017). Non-renewable resources: two fossil-resource fractions (Turner's sources; Sverdrup and Ragnarsdottir 2014; BP and World Bank production data). Human welfare: UNDP HDI, scaled by 1.106 to match the scenario value in 2000. Ecological footprint: Global Footprint Network, scaled by 1.17.
  - *Her conclusions that bear on this decision.* The two scenarios closest to the data were BAU2 and CT, not BAU (closest-fit counts over ten variables: BAU 4, BAU2 6, CT 7, SW 3, none 2). She notes that scenarios "start to deviate later in World3-03 than was the case in the 1972 version", and that BAU2 and CT "do not deviate significantly before 2020", so these two fit equally well for several variables. In her discussion most value differences are within the 20% range "except for pollution and for fertility (i.e., birth rate) in SW"; the population value differences are within 20% for all four scenarios, while SW's population rate-of-change difference (-52%) is just outside her 50% range.
  - *Turner.* Per Herrington, Turner (2008, 2012, 2014) "compared global observed data for the LtG variables with 3 of the 12 scenarios from the first book: BAU, CT, and SW", that is, the 1972 model. Turner's own paper was not read in full: only its ScienceDirect abstract page and a search summary (Global Environmental Change 18(3), 397-411; data 1970-2000).
  - *Still unverified:* her Supporting Information; the other columns of her Table 2 (the extracted table text is garbled after the first four columns, so only population is quoted); whether the CD-ROM's BAU matches the package's `scenario1` numerically; Turner's paper beyond its abstract. Proposal step 3 asked for Herrington to be read in full; that is now done. The book's tables and the age-structure comparison with UN data are still open.
- **Finding 5: tests of the variants.** The package's own test suite covers `World3_03` only (5 tests, compared with Vensim solutions stored in the package) and passes in the pinned environment (`audit/T0-FINDINGS.md`, Local verification). The cross-check of D-017 (all twelve stocks within 1.70% of PyWorld3) is for the 1974 model; there is no independent second implementation of the 2004 variant, because PyWorld3 does not have it.
- **Proposal:**
  1. F3's population sector (S1) uses the **2004 parameter set** (`World3_03`) as its default.
  2. The port (step 1.4) carries **both parameter sets** in a single piece of code, since only parameters and tables differ. The 1974 set is a regression test: the port must match WorldDynamics.jl `World3` within ±2% (D-004) with PyWorld3 as second check, as planned. The 2004 set is checked against WorldDynamics.jl `World3_03` within ±2%; any second check of it (for example PyWorld3 with its tables overridden on the instance) is labelled diagnostic, per `CLAUDE.md`.
  3. Before relying on the 2004 variant for backtesting from 1970, someone reads Herrington (2021) in full and the book's tables to confirm what WorldDynamics.jl's `World3_03` leaves out or changes, and the age-structure data (UN WPP) are compared with the p1–p4 cohorts, where the variants differ most (65+: 23–39% apart in 1970–2025). Those two checks are cheap relative to step 1.4 and do not block starting it.
- **What each choice means:**
  - *2004 (proposed):* population is closer to observed values from 1980 to 2025 (−8.6% against −14.3% in 2025); matches the variant used in the most recent comparison with data (subject to the verification note); no second implementation to cross-check; the 1970 starting population is 2.6% above observed instead of 1% below.
  - *1974:* matches everything already cross-checked (T0, D-017 and PyWorld3), the book that the package's Figure 7.7 reproduces, and Turner's 1970–2000 comparison; drifts further from observed population (−14.3% in 2025), so a backtest from 1970 would start from a larger structural gap.
  - *Either choice:* F3 starts in 1970 from observed data (open question: the 1970 initialisation decision in the Phase 1 plan), so how the model reaches 1970 from 1900 matters less than how it behaves afterwards; and the effect on the equations to port is nil, only the parameter and table set differs.
- **Alternatives considered:** 1974 as default with 2004 as an option (lower cross-check risk, but the worse fit to observed population would carry into every backtest); port only one variant (smaller, but the choice cannot then be revisited without redoing the tests); decide after the two checks in proposal step 3 (cleanest evidence, delays step 1.4 for work that does not change the equations).
- **Sources:** `audit/t0/world3_variants.jl`; `audit/data/world3_variants_report.md`; `audit/data/world3_variants_state_differences.csv`; WorldDynamics.jl v1.0.0 source (`src/World3`, `src/World3_91`, `src/World3_03`); UN World Population Prospects 2024, https://population.un.org/wpp/ (file `UN_2024_WorldPop-Historical-Plot.xlsx`; licence and citation terms not checked); WPP 2024 Summary of Results, https://population.un.org/wpp/assets/Files/WPP2024_Summary-of-Results.pdf (Table A2; note on the reference date); Herrington (2021), DOI 10.1111/jiec.13084 (article text read in full, Supporting Information not read); Turner (2008), Global Environmental Change 18(3), 397–411 (abstract only).
- **Proposed by:** Claude (Research agent role)
- **Decision:** Approved with amendment: the port carries both parameter sets (1974 and 2004) in one codebase; the 2004 set is F3's provisional default; the final default is confirmed at the Phase 3 backtest on observed data, using 2000-2025 as the out-of-sample test. Before the 2004 set is relied on for backtests, the book's tables (and Herrington's Supporting Information) are read and the age cohorts are compared with UN WPP; these checks do not block step 1.4. (Approved by Stéphane Beau; this amends proposal item 1, whose text is kept as drafted.)
- **Date:** 2026-10-07

---

## D-016 — Earth4All audit verdict: reuse, reuse with changes, or replace, sector by sector

- **Status:** Approved (2026-10-07)
- **Context:** D-010 made Earth4All a reference model and component library, to be reused only after tests T1–T4. The tests have been run on Earth4All.jl at commit `16f37d0` (`audit/earth4all-audit.md`); D-018 fixes how its deviations from Vensim are reported. This entry turns the evidence into a per-sector verdict, so that MODEL_SPEC can be updated to match. It is a proposal: the evidence below is measured, the verdicts are the Validator's recommendation.
- **Evidence in one place** (details and caveats in `audit/earth4all-audit.md` and `audit/T0-FINDINGS.md`):
  - **T1:** no death flow out of the cohorts below 60 (by design). **T1b:** no cohort stock is negative before 2100 in either scenario (smallest 617.7 Mp).
  - **T2:** workforce never exceeds working-age population (121 of 121 years, both scenarios; maximum ratio 0.825), under the definition employed = `WF`, working-age = `WAP`. It exceeds the available workforce by at most 0.59% in a few years.
  - **T3:** of the 40 explicit time-driven equations, 9 are behaviour forcing, all in **climate (2), foodland (5) and population (2)**. None is in output, demand, inventory, finance, public, energy, labour market or well-being. The two population ramps (`SSP2FA2022F`) move 2100 population by 28% and the well-being index by 30% (TLTL counterfactual).
  - **T4:** Too Little Too Late runs to 2200 without a non-finite value; Giant Leap becomes unstable at 2197.3. Informational (F3 stops at 2100).
  - **Deviation from Vensim** (variables whose 95th-percentile error exceeds 1e-2, TLTL / GL, of total): demand 36 / 36 of 71, energy 23 / 12 of 80, wellbeing 8 / 3 of 20, inventory 8 / 0 of 20, foodland 7 / 3 of 87, output 6 / 3 of 40, labour market 5 / 4 of 41, public 4 / 1 of 21, population 2 / 0 of 30, other 2 / 1 of 8; climate 0 of 55, finance 0 of 14. Headline variables above D-004's ±2%: well-being index (4.37% TLTL, 2.77% GL).
- **Proposal** (verdict per Earth4All.jl sector; "reuse" means port or call the component in F3 after it is documented and tested against Earth4All.jl within D-004's tolerance, per D-011):

| Earth4All sector | Verdict | Reason from the evidence | F3 sector (MODEL_SPEC) |
|---|---|---|---|
| population | **Replace** | no mortality below 60 (T1); two exogenous ramps that move 2100 population by 28% (T3). D-010 already assigns S1 to World3's population sector | S1 (World3) |
| output | **Reuse** | no behaviour forcing; 6 / 3 of 40 variables deviate from Vensim at p95 | S2 |
| demand | **Reuse with changes** | no behaviour forcing; its policy levers are zero in TLTL; but it is the sector with the largest deviation from Vensim (half of its variables at p95 above 1e-2), so it needs a component-level comparison before it is relied on | S2 |
| inventory | **Reuse** | the single time switch (1984) has no effect (`PNIS = 1`); 8 / 0 of 20 deviate | S2 |
| finance | **Reuse** | no time-driven equation; 0 of 14 deviate | S2 |
| public | **Reuse with changes** | no behaviour forcing, but `EDROTA2022 = 0.003` is non-zero in both scenarios and was not measured; F3 should expose it as a documented parameter | S2 |
| labour market | **Reuse (provisional)** | T2 passes under the stated definition. Provisional because automation to labour is F3's core link and the AI sector (S3) is not yet coupled; reconsider when S3 is specified | S2 / S3 |
| energy | **Reuse with changes** | no behaviour forcing; D-010 already plans to extend it with data-center demand and material limits (S5). 23 / 12 of 80 deviate | S4 |
| climate | **Replace** | D-010 assigns S6 to FaIR; two exogenous 1%/y emission-intensity declines are behaviour forcing | S6 (FaIR) |
| foodland | **Replace** (v0.1) | five behaviour-forcing equations (SSP2 land-management ramps, food productivity trend); D-010 assigns v0.1 food to World3's agriculture, revisit in v0.2 | S1 food (World3) |
| wellbeing | **Replace** with F3's own S7, keeping Earth4All's indices as a comparison output | its indices are the deviating headline variables (4.37% / 2.77% against D-004) and oscillate; D-010 assigns S7 to a new module with explicit stocks | S7 |
| other | **Not assessed** | 8 variables, 7 equations, no time-driven equation; follows whichever sector needs it | — |

  Where F3 reuses Earth4All results or components it states the caveats of D-018. F3 does not run Earth4All past 2100.
- **Alternatives considered:** reuse every sector except population (simplest, but carries the climate and food forcing into F3's feedback loops, which is the property F3 is meant to show); replace all of Earth4All with new sectors (highest effort and error risk, and discards 6 sectors with no behaviour forcing); decide per sector later when each is needed (keeps options open but leaves MODEL_SPEC inconsistent).
- **Open points for the editor-in-chief:** (1) whether the T2 definition (employed = `WF`, working-age = `WAP`) is the one D-010 meant; (2) whether the nine behaviour-forcing equations are acceptable inside a reused sector if exposed as scenario switches (the SSP2 ramps can be switched off by package parameters), instead of replacing the sector; (3) the T3 classification is a reading of 40 equations and is open to challenge, equation by equation, in `audit/earth4all-time-driven-equations.csv`.
- **Sources:** `audit/earth4all-audit.md`; `audit/earth4all-time-driven-equations.csv`; `audit/T0-FINDINGS.md` (run #7); Earth4All.jl source at `16f37d0`.
- **Proposed by:** Claude (Validator and Research agent roles)
- **Decision:** Approved by Stéphane Beau, as drafted.
- **Date:** 2026-10-07

- **Outcome note (2026-10-08), answers of the editor-in-chief to the three open points above:**
  1. The T2 definition (employed = `WF`, working-age = `WAP`) is accepted. The caveat stays on record: a different pair of variables could give a different answer (`audit/earth4all-audit.md`, T2).
  2. No decision is needed on exposing the nine behaviour-forcing equations as switches inside a reused sector, because the three sectors concerned (population, climate, foodland) are replaced.
  3. The T3 classification stands. A second read of the 9 behaviour-forcing equations, the 3 historical-then-goal paths, the 7 feedback switches and the one non-zero policy input found nothing to reclassify. The other 18 policy inputs were not re-read.

---

## D-019 — How F3 initialises its stocks in 1970

- **Status:** Proposed
- **Context:** World3 runs from 1900; F3 is specified to start in 1970 (`MODEL_SPEC.md`), and `docs/phase-1-plan.md` (step 1.4) says the 1970 initialisation gets its own decision. The population-sector port (`f3/sectors/s1_population.py`) is finished and tested from 1900 against WorldDynamics.jl (`audit/s1-port-report.md`), so there is now evidence on what starting in 1970 does. **Scope of the evidence:** the S1 population sector only, with its four inputs (food, service output and industrial output per capita, pollution index) held at the series the 1900 WorldDynamics.jl run produced. Other sectors, and the feedbacks of a coupled model, are not tested.
- **Evidence** (measured with the port; `audit/t0/s1_report.py` and the checks below; observed population is UN World Population Prospects 2024, 1 July values):
  1. *Restarting at 1970 is mechanically sound.* Started in 1970 from the reference's own 1970 state, the port reproduces the same port run from 1900 to within 0.11% (1974 parameter set) and 0.006% (2004 set) on all 15 states, and the WorldDynamics.jl reference to within 0.039% and 0.025%.
  2. *The model's own 1970 state is not the observed one.* Total population in 1970: 3.657 bn (1974 set, −1.0% against observed 3.695) and 3.792 bn (2004 set, +2.6%). The model's 1970 age shares (0–14 / 15–44 / 45–64 / 65+) are 36.7 / 41.0 / 15.2 / 7.1% (1974 set) and 34.5 / 40.9 / 16.1 / 8.5% (2004 set). **They were not compared with the UN age structure** (the age-cohort check left open in D-015).
  3. *Matching the 1970 total does not by itself improve the later fit.* One experiment: scale the four cohorts by a common factor to the observed 1970 total, keep the other eleven states as they are in the 1900 run, run to 2025:

| parameter set | start | 2000 vs observed | 2025 vs observed |
|---|---|---|---|
| 1974 | 1970 state from the 1900 run | −7.8% | −14.3% |
| 1974 | cohorts scaled to observed 1970 total | −6.8% | −13.4% |
| 2004 | 1970 state from the 1900 run | −1.3% | −8.6% |
| 2004 | cohorts scaled to observed 1970 total | −3.8% | −11.0% |

     So for the 2004 set the better 1970 start leaves it further from observed population by 2000 and 2025; for the 1974 set it helps by about one point. The drift after 1970 is therefore mostly a property of the parameters and inputs, not of the 1970 start, and the experiment says nothing about how age cohorts, or the other eleven states, should be initialised. It is a single-variable experiment, not a calibration.
  4. *Eleven of the fifteen states are not observable.* The delayed and smoothed variables (health services, perceived life expectancy, delayed and average industrial output per capita, fertility-control facilities, with their delay stages) have no data series. A 1970 start needs a rule for them: take them from the 1900 run, or set them to the steady state of the 1970 inputs. The second rule was not tested.
- **Proposal** (the decision is the editor-in-chief's; the options are mutually exclusive):
  - **Option A — spin-up from 1900.** F3 keeps a 1900 start inside the model and reports 1970–2100. Every stock, in every sector, is the model's own; fully reproducible against the references; the 1970 state is not observed data.
  - **Option B — observed 1970 state.** Set every stock that has data to its observed 1970 value (cohorts from the UN age structure, others from their sources) and every other state to the steady state of the 1970 inputs. Starts from reality, but needs a data source per stock, the steady-state rule is untested, and item 3 shows no guarantee of a better 1970–2025 fit.
  - **Option C — A for Phases 1 and 2, B as a calibration choice in Phase 3.** Until the model is coupled and calibrated, F3 starts in 1970 from the model's own 1900-run state (A). Whether to initialise from observed values is then treated as a calibration choice and judged on the Phase 3 backtest, with 2000–2025 as the out-of-sample period (as the D-015 amendment already sets for the parameter-set choice).
  - **Recommendation (Validator): Option C.** It keeps the reproduction tests exact, does not commit to an untested steady-state rule, and puts the question where its answer can be measured. This is a recommendation, not a decision.
- **What each option means for the work already done:** none requires changing the port: its `run()` already accepts a start year and an initial state (`t0`, `y0`). Option B needs the UN age-cohort comparison (D-015's open check) and a data source for each stock of every sector.
- **Alternatives considered:** initialising from the 1900 run but rescaling cohorts to the observed 1970 total (evidence item 3 shows it moves the 2004 set the wrong way, and it mixes a data value with model-consistent delays); starting the whole model in 1900 and reporting from 1970 as the only horizon (that is Option A).
- **Sources:** `audit/s1-port-report.md`; `f3/sectors/s1_population.py`; `tests/fixtures/` (WorldDynamics.jl exports); UN World Population Prospects 2024 (`UN_2024_WorldPop-Historical-Plot.xlsx`); D-003, D-004, D-015.
- **Proposed by:** Claude (Modeler and Validator agent roles)
- **Decision:** Proposed. Not approved.
- **Date:** 2026-10-08

---

## Template for new entries

```
## D-xxx — Title

- **Status:** Proposed
- **Context:** Why this decision is needed.
- **Proposal:** What we would do.
- **Alternatives considered:** What else, and why not.
- **Sources:** Citations.
- **Proposed by:** Agent or person.
- **Decision:** Approved / Rejected / Superseded by D-xxx
- **Date:** YYYY-MM-DD
```
