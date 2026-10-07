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
| D-013 | WorldDynamics.jl solver configuration | Proposed — to be superseded by D-017 on approval | 1 |
| D-014 | Use of the Vensim output shipped with Earth4All.jl | Approved | 1 |
| D-017 | World3 reference environment: dated registry snapshot (supersedes D-013 if approved) | Proposed | 1 |

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

- **Status:** Proposed. **Run #6 result: the original acceptance condition (item 3 of the proposal) was NOT met**; a revised proposal follows the result and awaits the editor-in-chief's decision.
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

## D-017 — World3 reference environment: dated registry snapshot, default solver options (supersedes D-013 if approved)

- **Status:** Proposed
- **Context:** The editor-in-chief asked for "a version that works" (2026-10-05). A search over Julia registry snapshots (`audit/T0-FINDINGS.md`, "Registry-snapshot search #1") found that WorldDynamics.jl v1.0.0 solves World3 with default solver options in the dependency sets of 2024-04-25 (ModelingToolkit 9.12.1, SciMLBase 2.35.0, OrdinaryDiffEq 6.74.1) and 2024-07-01 (9.22.0, 2.42.0, 6.85.0), and not in later ones. In the working stacks the PyWorld3 cross-check numbers equal those obtained with `NoInit()` on the newest stack.
- **Proposal:**
  1. F3's World3 reference environment is Julia 1.10 with the packages resolved from the General registry as of **2024-04-25** (registry commit `ec06aa53f5a2d5c46f7d70440c86911050375882`), the one closest to the package's release (2024-04-18).
  2. WorldDynamics.jl is run with **default solver options**. `NoInit()` is not used.
  3. The environment is pinned by committing the `Project.toml` and `Manifest.toml` of that job (artifact `world3-snap-2024-04-25`) to `audit/env/`; later audit runs install from them with `Pkg.instantiate()`.
  4. **Acceptance conditions, fixed before the follow-up checks:** (a) in a fresh run that uses only the committed Manifest, the default-option solve returns `Success` with at least 401 saved points (saveat 0.5); (b) its twelve main stocks agree with the `NoInit()` solution of the newest stack within 0.1% at every saved time (this tests whether the earlier workaround changed the solution); (c) against fine-step PyWorld3 with the diagnostic start-up, all twelve stocks stay within ±2% (already seen: worst 1.70%), and the as-shipped comparison is reported alongside (`ppol` 373.7%, explained by the start-up difference).
  5. With the editor-in-chief's agreement, the evidence (working until the 2024-07-01 snapshot; a different error at 2024-10-01; `InitialFailure` from 2025-01-15) is reported to the WorldDynamics.jl maintainers as an issue.
  6. D-013 is withdrawn in favour of this decision.
- **Check results (2026-10-06, from the artifact of the 2024-04-25 job):** (a) not yet testable; the Manifest is committed and the T0 workflow installs from it, so the next run tests it; (b) **met**, worst 0.0143% over the twelve stocks (default vs `NoInit()` on the same stack: identical); (c) **met**, worst 1.70% with the diagnostic start-up. Details in `audit/T0-FINDINGS.md`. If (a) fails in the next run, this decision is reopened.
- **Known limitations:** the start-up difference between WorldDynamics.jl and PyWorld3 in the pollution delay is unchanged (WorldDynamics.jl starts 8.9% above steady state, see D-013's run #6 result) and is handled in step 1.4 by testing the Python port from the same initial state as the reference. The cause of the break between July and October 2024 was not investigated. An environment from 2024 will age; the committed Manifest keeps it reproducible but not maintained.
- **Alternatives considered:** `NoInit()` on the newest stack (D-013), set aside by the editor-in-chief's direction; the 2024-07-01 snapshot (also works; newer, but further from the package's release); porting World3 from the book's equations without the package (highest error risk).
- **Sources:** snapshot search run #1 (2026-10-06), `audit/T0-FINDINGS.md`.
- **Proposed by:** Claude (Validator agent role)
- **Decision:** —
- **Date:** —

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
