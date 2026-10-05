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
