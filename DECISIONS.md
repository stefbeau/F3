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
| D-005 | AI sector integration approach | Approved, with the amendment of 2026-10-08 (numeric criteria A1.2 to A1.6); amendment B (the three A1.3 settings replaced by the playground's shipped runs, with the addition on equation-10 years) approved 2026-10-09 | 2 |
| D-006 | Critical minerals granularity in v0.1 | Approved 2026-10-21 (aggregate index in v0.1; named minerals in v0.2) | 2 |
| D-007 | Climate damage function | Approved 2026-10-12 (three level-effect options, default central) | 2 |
| D-008 | Social tension historical proxy | Approved 2026-10-21 (option 3: no event-data backtest; tension labelled not validated) | 3 |
| D-009 | Dashboard stack | Approved 2026-10-12 (static site, precomputed scenario grids) | 4 |
| D-010 | Scientific robustness of Earth4All as a baseline | Approved | 1 |
| D-011 | Earth4All reference implementation (supersedes D-002) | Approved | 0 |
| D-012 | World3 reference implementation | Approved | 1 |
| D-013 | WorldDynamics.jl solver configuration | Superseded by D-017 | 1 |
| D-014 | Use of the Vensim output shipped with Earth4All.jl | Approved | 1 |
| D-015 | World3 variant for F3's population sector: 1974 or 2004 parameter set | Approved with amendment | 1 |
| D-016 | Earth4All audit verdict: which components F3 reuses, changes or replaces | Approved | 1 |
| D-017 | World3 reference environment: dated registry snapshot, default solver options | Approved; condition (a) met 2026-10-07 | 1 |
| D-018 | Earth4All.jl is the Earth4All reference implementation; deviations from Vensim reported | Approved | 1 |
| D-019 | How F3 initialises its stocks in 1970 | Approved (Option C) | 1 |
| D-020 | Start years and initial states of the non-World3 sectors (plan N1) | Approved (question 1 option A, question 2 option (i)) | 2 |
| D-021 | How FaIR is coupled; source of non-CO2 emissions (plan N2) | Approved (re-run each year; emissions prescribed) | 2 |
| D-022 | Sector interface and time convention (plan N3) | Approved (explicit coupling; t = Y is 1 January) | 2 |
| D-023 | Inputs to the reused Earth4All sectors from replaced sectors (plan N4) | Approved (option C) | 2 |
| D-024 | Phase 3 backtest criteria (plan N5) | Approved as a framework; thresholds set by the editor before the M5 hindcast | 2 |
| D-025 | Phase 3 entry conditions (plan N6, optional) | Approved | 2 |
| D-026 | Handling of Epoch AI's GATE playground data (the shipped runs) | Approved | 2 |
| D-027 | S3 production composite: footnote-38 task grids as a labelled variant | Approved 2026-10-12 | 1 |
| D-028 | S3 investment rule: R3 (AI-race budget) calibrated with R1 curves | Approved 2026-10-12 | 1 |
| D-029 | M1 closed with A1.3 failed; S3's composite is a known open difference | Approved 2026-10-12 | 1 |
| D-030 | M2 step 1 closes with A2.1 failed; climate output labelled | Approved 2026-10-12 | 2 |
| D-031 | World3 sector group advanced with internal sub-steps of 0.0625 year inside the 0.25-year loop | Approved 2026-10-20 | 2 |
| D-032 | Data-centre boundary for the F3 data-centre module (IEA Energy and AI, descriptive) | Provisional (delegated) | 2 |
| D-033 | Data-centre module form, calibration, supply and coupling (Track A) | Provisional (delegated) | 2 |
| D-034 | Damage function action on S3 (Track A) | Provisional (delegated) | 2 |
| D-035 | Reuse of one exact climate recording (Track A) | Provisional (delegated) | 2 |
| D-036 | Demo 0 grid and levers (Track A) | Provisional (delegated) | 2 |
| D-037 | Module names and structure of the four World3 sectors | Approved 2026-10-21 | 2 |
| D-038 | The A3.2 failure at loop step 0.25 is recorded, not repaired (superseded in effect by D-031) | Superseded in effect by D-031 | 2 |
| D-039 | Initial outputs of the coupled World3 sectors | Approved 2026-10-21 | 2 |
| D-040 | The World3 group is one Sector wrapping the five sectors (the form D-031 takes) | Approved 2026-10-21 | 2 |
| D-041 | A3.4(b) is recorded as failed and not repaired | Approved 2026-10-21 | 2 |
| D-042 | N4: inputs to the reused Earth4All sectors in M4 (D-023 option C) | Approved for M4 2026-10-21 (revisit at M6) | 2 |
| D-043 | Euler with a 1/64-year internal sub-step for the reused Earth4All sectors | Approved 2026-10-21 | 2 |
| D-044 | Correction of the M4 recorded-input fixture grid (1/16 to 1/64 year), made after a result was seen | Approved 2026-10-21 | 2 |
| D-045 | Fixture correction: S1 and World3 recorded inputs re-exported on the 1/64-year grid (no change) | Provisional (delegated) | 2 |

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

- **Status:** Approved (2026-10-08)
- **Context:** GATE determines investment through an optimization step that does not fit naturally into a system dynamics model.
- **Proposal:** Re-implement GATE's three modules (AI development, automation, growth) in simplified form, replacing the optimization with a behavioral investment rule. Check against GATE sandbox presets (MODEL_SPEC §7.3).
- **Alternatives considered:** Coupling to GATE's own code (harder to integrate and maintain).
- **Decision:** Approved by Stéphane Beau: re-implement GATE's three modules in simplified form with a behavioural investment rule (the Proposal above), with the amendment below approved with the fix recorded in its approval note (A1.5(d) corrected; criteria for A1.2 to A1.6; the two settings and the Setting 2 replacement rule; the rule for the λ ambiguity).
- **Date:** 2026-10-08

- **Amendment proposal A (2026-10-08, Proposed; the editor's confirmation is needed before any comparison run).** The entry above is the approved-for-drafting text and is not changed. This amendment fixes the numeric criteria that plan tests A1.2 to A1.6 call for. It is written before any code, so the criteria cannot be shaped by results. **Nothing here is approved.** When approved, this block becomes the record and D-005's Status, Decision and Date lines are filled.

  **Why the entry above is not enough.** It says "check against GATE sandbox presets (MODEL_SPEC §7.3)" with no tolerance and, as the evidence below shows, presets whose values are not published in a readable form.

  **Evidence read for this amendment (2026-10-08).** The full text of arXiv:2503.04941v2 (CC BY 4.0), downloaded to a scratch folder and searched directly, Appendix D tables included; Epoch's announcement post; Epoch's follow-up post on explosive growth; the playground page.
  1. *The paper has no sensitivity analysis.* Section 8 says "one could conduct sensitivity analyses across plausible parameter ranges"; the conclusion encourages "parameter sweeps, and sensitivity testing". No figure or table reports a run under varied parameters with numbers; Figure 5 is "illustrative outputs" under unspecified "different assumptions"; Figure 3 is a conceptual schematic. **So there are no published GATE results to reproduce numerically from the paper alone.** What the paper does give, as its own explorations: Section 7's themes (rapid versus gradual automation by lowering the FLOP gap or the compute requirement; hardware and software progress by changing the R&D returns and efficiency caps; investment aggressiveness through the discount rate and risk aversion; bottlenecks through the adjustment-cost exponent and the substitution parameter; policy through the R&D wedge and caps on training runs), the three add-ons, and Appendix D's ranges.
  2. *Presets exist in the playground but are not documented in the paper:* the paper says users can "select from pre-specified bundles of parameters or scenarios (e.g., median, 5th or 95th percentile values ...)"; Appendix D gives **ranges with defaults** (low, default, high) and does not list preset values. A search summary (secondary) says the playground presets move only the AGI training requirement and the hardware and software R&D returns; the playground page fetched shows no preset names or values. **Preset names and values are therefore unverified**, and whether results can be exported is stated in the paper ("visualize and export these outputs") but not verified in the tool.
  3. *Published numbers exist only in Epoch's posts, for the default (and one add-on) configuration:* "GATE A" (default): with about 30% of tasks automated growth "may exceed 20%"; strict explosive growth (above 30%) needs roughly 50 to 70% of tasks automated; "23%/year" in 2027; optimal 2025 AI investment "$25 trillion", with the initial AI investment "24% of GWP" (footnote 9). The announcement post says the default "assigns 20% of the world economic output (nearly $20T/year)" to AI development and calls this unrealistic. "GATE B" (R&D wedge 10, investor uncertainty with 50% chance that at most 30% automation is attainable and 50% that at most 100% is attainable, and labour reallocation frictions): at 40% of tasks automated "12% GWP growth rates"; initial AI investment about 15% of GWP with wedge and uncertainty together. **These are the only numeric results found. The sources disagree among themselves on the default's initial AI investment (20% in one post, 24% in a footnote of another; $20T against $25T).** They are figures read from blog text, with unknown solver settings and version.
  4. *Unresolved:* GATE has no published source code (arXiv page; the playground and posts mention none), so a re-implementation can be compared only with these figures and with the sandbox if it can be driven; **whether the sandbox can be driven or its outputs exported at the numbers' precision was not established** (A1.1).

  **A1.1 precondition (unchanged from the plan):** before any comparison, record what the sandbox can export. If it cannot give series at a precision that supports A1.3, the fallback (A1.6) applies and the editor decides before any comparison.

  **Numeric criteria (proposed).**

  | Test | Criterion | Reasoning |
  |---|---|---|
  | **A1.3** same equations, GATE's investment path supplied as input | For the **three settings** below (the default and the two proposed by the Validator), S3's effective compute, algorithmic and hardware efficiency, automation fraction and output match the sandbox within **±2%** at every year of 2025 to 2100, **provided** the sandbox's series can be exported to at least three significant figures. | This part of S3 re-implements the same equations, so D-004's ±2% is the natural bar. It is stated before any run; a failure is reported, not relaxed, and a revised criterion would be a new labelled proposal. If the export is coarser than three significant figures, the criterion becomes ±2% plus the export's rounding, stated in the report. |
  | **A1.4** behavioural rule against GATE's optimised path | **Report only, no pass or fail.** For each setting: the largest and mean relative difference of the investment shares, of effective compute and of output, and the first year each exceeds 5% and 10%. | D-005 deliberately replaces the optimisation; a pass/fail would test the replacement against the thing it replaces. |
  | **A1.5** extreme conditions | **Pass if all hold, 2025 to 2100, on each setting:** (a) hardware efficiency and software efficiency growth set to zero (R&D productivity zero): effective compute grows only through compute stock and the automation fraction never falls; (b) zero investment in compute and R&D: compute stock falls by depreciation and no stock turns negative; (c) the automation fraction is non-decreasing in effective compute at every year; (d) no NaN and no negative stock; and **usable compute `g(Q)`, which the paper's equation 10 defines as `g(Q) = Q / (Q/C_L + 1)`, never exceeds `C_L`** (2e38 FLOP/year by default). **`C_L` bounds usable compute only: the raw compute stock `Q` and effective compute (usable compute times software efficiency `S`, equation 11, `C(0) = g(Q(0)) S(0)`) are not capped by `C_L` and may exceed it.** The report states the criterion on `g(Q)` and reports the raw stock `Q` and the effective compute beside it, so that nobody reads a value of `Q` or of effective compute above `C_L` as a violation. (Corrected 2026-10-08 at the editor's instruction; the first wording said "no stock that exceeds the paper's physical compute limit", which would have wrongly applied the cap to `Q` and to effective compute. Checked against equations 9 to 11 of arXiv:2503.04941v2.) | These are the plan's extreme-condition tests made concrete. Each is a property of the equations, not of a reference. Whether (a) holds exactly depends on a reading of the paper's law of motion for the largest training run that was not completed here; the criterion is therefore stated as a property and the Modeler states, before running, the exact equation it applies to. |
  | **A1.6** fallback (only if A1.1 shows nothing can be exported) | The default setting reproduces the **published figures of the posts** within **±10%**: the investment share in 2025 (20% or 24%, whichever the editor accepts as the reference; the two posts disagree), the growth rate of 23% in 2027, and the automation fraction at which growth first exceeds 20% (about 30%) and exceeds 30% (50 to 70%). The ±10% is looser because these are blog figures of unknown precision and version, not series. **It is a fallback, labelled so everywhere it is reported, and the editor decides whether it is enough to proceed.** | Without a series the comparison is against statements, which carry less information. |
  | **A1.2** | This amendment, once approved, **is** A1.2. | |

  **Two parameter settings for A1.3, proposed for the editor to confirm (they are tested together with the default, Setting 0).** Chosen from the parameter ranges of the paper's own Appendix D (which are the paper's "permissible ranges", read directly), not from a published sensitivity analysis, because the paper has none. Each setting changes **one named group of parameters** to a range endpoint that the paper itself lists, keeps everything else at default, and exercises a different part of the S3 equations:

  | | **Setting 0: default** | **Setting 1: slow, pessimistic automation** | **Setting 2: fast, optimistic automation** |
  |---|---|---|---|
  | Parameters changed | none | AGI training requirement `T` = 1e41 eFLOP; returns to hardware and software R&D `λ_H` = `λ_S` = 0.25 | `T` = 1e33 eFLOP; `λ_H` = `λ_S` = 1 |
  | Source of each value | all Appendix D defaults | `T`: the high end of the paper's range (1e33 to 1e41, default 1e36.5). `λ`: **the paper's text** gives 0.25 as the lower value of both (its "range" sentence for `λ_H` and for `λ_S`: "a lower value of 0.25"); the paper's **tables** print different lows (0.0625 for `λ_H`, 0.14 for `λ_S`), see the inconsistency below | `T`: the low end of the paper's range. `λ`: the upper value 1 that both the text and the tables give |
  | What it tests | the main case, and the only one with published numbers (Epoch's posts) | the long path to full automation: the automation function's tail, slow efficiency growth | an abrupt automation threshold, explosive efficiency growth, the compute limit `C_L`, the solver near its edge |
  | Why it matters for S3 | reference for A1.4 and A1.6 | stresses the stocks and R&D laws with little growth | stresses numerical stability and the physical limit |

  **Reasons for choosing these.** (1) The paper's own Section 7 names these groups as the main explorations (rapid versus gradual automation via the FLOP gap and the total compute `T`; hardware and software progress via `λ_H`, `λ_S`). (2) They are the parameters the paper itself flags as the most uncertain: Epoch's post says "even under conservative assumptions—such as modest returns to hardware and software R&D" automation within two decades results, so low `λ` is the paper's own "conservative" case, and the paper says `T` "is highly uncertain" with "several OOMs of uncertainty". (3) Each value is one the paper lists (in its text for the low `λ`, in its ranges for `T`), so no setting is invented. (4) A search summary says the playground's presets move "only the AGI training requirements and the hardware and software R&D returns", which is the same set; **that statement is unverified**, so these settings may or may not coincide with the playground's named presets, and the editor is asked not to assume they do.

  **Caveats the editor should weigh before confirming.**
  - **The paper's tables are internally inconsistent in places** (found while reading its text directly): for the returns to R&D, the **table for hardware** gives the range "0.0625 to 1" with default 0.14, and the **table for software** gives "0.14 to 1" with default **0.0625**, a default below its own low bound; the paper's **text** says, for both, that the central value is 0.14 (0.4 times an elasticity of 0.35) and that the range runs from 0.25 to 1. The tables look as if the two parameters' default and low values were swapped. Other inconsistencies: initial output is "$105T" in a bullet and "110 trillion" in the table; initial software R&D is "$10B/year" in a heading and "$5B" in the reasoning; the FLOP gap default is 0.55 in the table and 0.52 in the bullet heading; the risk-aversion default is 1.45 in the table and 1.5 in the text; and the software efficiency cap is `1e4` in the table and `1e5` in the bullet. **The default `λ_S` is therefore ambiguous (0.14 in the text, 0.0625 in the table), and the lows of both ranges differ between text and tables.** Consequences: (1) the default setting depends on which reading is taken, and a re-implementation fitted to the sandbox must use whatever the sandbox uses; (2) Setting 1 above uses the text's 0.25, which is inside every reading; (3) **the editor is asked which reading is the default**: the text's (default 0.14 for both) or the tables' (default 0.14 for hardware and 0.0625 for software). Until then the Modeler runs both and reports the difference; if the sandbox shows its parameter values, those decide.
  - The paper marks three parameters as needing "extra caution": the substitution parameter `ρ`, the risk aversion `η` and the FLOP gap; the proposed settings leave all three at default, so they stay inside the paper's recommended region.
  - **Setting 2 may not converge in the sandbox** ("for extreme parameter values our solution algorithm may not converge, in which case our model playground will typically deliver an error warning"). If the sandbox refuses it, the setting is replaced by one with `λ` = 0.5 for both and `T` = 1e34.5 (about half the range in log terms) and the report says so. This replacement rule is fixed now so it is not chosen after seeing the failure.
  - Time axis: the paper's initial conditions are "at the start of 2025"; it discretises time at 1 year, solves with a planning horizon "typically set at 80 periods" and simulates over a longer optimisation horizon (about twice that, from the paper's appendix as summarised earlier; not re-read for this amendment). A 2025 to 2100 run is 75 annual steps, inside the 80-period planning horizon. S3 runs on F3's 0.25-year loop (D-022) while GATE solves annually, so the comparison is at annual points and the step difference is reported separately.

  **What this amendment does not do.** It does not choose the behavioural investment rule (the Modeler proposes it in M1 and it is reported by A1.4); it does not settle which economy drives output from 2025 (D-020, plan amendment 14.2); it does not claim the settings coincide with the playground's presets.

- **Approval of the amendment (recorded 2026-10-08).** Stéphane Beau approved the D-005 amendment above **with the following fix and decisions**:
  1. **A1.5(d) is corrected** as written in the table above: the physical limit applies to usable compute `g(Q)` (equation 10), not to the raw stock `Q` or to effective compute; the report gives the criterion on `g(Q)` and reports `Q` and effective compute beside it.
  2. **The numeric criteria of A1.2 to A1.6 are approved as proposed** (A1.3 within ±2% at every year of 2025 to 2100 for three settings, provided the sandbox exports at least three significant figures; A1.4 report only; A1.5 as corrected; A1.6, the ±10% fallback, only if nothing can be exported and only with the editor's decision before any comparison).
  3. **The two parameter settings for A1.3 are approved**, together with the default (Setting 0): **Setting 1 (slow):** `T` = 1e41 eFLOP, `λ_H` = `λ_S` = 0.25. **Setting 2 (fast):** `T` = 1e33 eFLOP, `λ_H` = `λ_S` = 1, with the **replacement rule for Setting 2** as written above (if the sandbox refuses Setting 2, it is replaced by `λ` = 0.5 for both and `T` = 1e34.5, and the report says so).
  4. **Rule for the `λ` ambiguity** (the paper's tables and text disagree on the defaults and lows of `λ_H` and `λ_S`): the Modeler **runs both readings and reports the difference**; **if the playground shows its parameter values, those decide**; the **working default is the text's reading, 0.14 for both** `λ_H` and `λ_S`.
  Nothing else in the amendment changed.

- **Amendment proposal B (2026-10-09, Proposed; nothing here is approved; it changes nothing above, and A1.3, A1.4 and A1.6 as approved stay in force until the editor approves this block).** Written before any comparison code exists and before any comparison has been run.

  **What B changes, in one sentence.** It replaces the three settings that A1.3 is tested on, **D-005 Settings 0, 1 and 2, with the three runs the GATE playground ships** (default, conservative, aggressive), and keeps the approved slow and fast settings as report-only stress runs.

  **Why (the reason is data availability, not a result).** The approved A1.3 needs a reference series for each setting at three significant figures. `research/gate-equations.md` (A1.1, 2026-10-08) found that the playground ships exactly three runs as series, each with 80 yearly states stored to about 16 significant digits, and has no way to export any other run: it downloads a parameter file and chart images only. The approved Settings 1 and 2 (T = 1e41 with λ = 0.25; T = 1e33 with λ = 1) are **not among the shipped runs** and therefore have **no reference series at all**; they could not be tested to ±2% by any means available. Of the approved three settings, only the default has a series. **This is a change of the reference, forced by what exists; it is not a change of the standard.** It is written before any S3 code exists, so it cannot have been chosen to make a test pass, and the pass bar (±2%) and the rule that a failure is reported and not relaxed are kept unchanged. What it gives up is the coverage that Settings 1 and 2 would have given of parameters that change λ directly (the shipped presets change `T` and the returns ratios, not λ), and that loss is stated, not hidden.

  **The three A1.3 settings under B** (parameters as read in the playground's own table and in the parameter blocks of the shipped runs; all other parameters at the playground's defaults, which for λ_H and λ_S are 0.14 for both):

  | | **B0: default** | **B1: conservative** | **B2: aggressive** |
  |---|---|---|---|
  | AGI training requirement `T` | 1e36.5 eFLOP | 1e38 | 1e33 |
  | Hardware R&D returns ratio `r_H` | 5.2 | 1 | 7.1 |
  | Software R&D returns ratio `r_S` | 1.25 | 1 | 2 |
  | Implied fishing-out exponents `φ_H = (λ_H/γ_H)/r_H`, `φ_S = (λ_S/γ_S)/r_S` (λ/γ = 0.4) | 0.0769, 0.32 | 0.4, 0.4 | 0.0563, 0.2 |
  | Everything else | default | default | default |

  (The `φ` values are derived, and they were checked: at stored index 0 the hardware and software efficiencies of all three shipped runs equal the paper's equation 4 evaluated with these `φ`, ratio 1.000000. The names "conservative" and "aggressive" are the playground's.)

  **Numeric criteria under B (A1.3 only; A1.2, A1.4, A1.5 and A1.6 stay as approved, except as stated under "Report-only stress runs").**

  | Item | Criterion |
  |---|---|
  | **Compared quantities** | S3's effective compute, hardware efficiency, software efficiency, automation fraction and output, against the stored `compute`, `hardware`, `software`, `frac_automated` and `gwp`, and S3's capital stock, labour and the output-allocation shares against `capital`, `labor` and the stored shares. The shipped series are the reference **with GATE's own investment path supplied to S3 as input** (the stored investment shares), as A1.3 already says |
  | **Tolerance** | **±2% relative, at every annual period end, 2025 to 2100**, for each compared quantity and each of the three settings |
  | **Alignment in time (fixed now, from `research/gate-equations.md` section 5)** | The stored index `k` is the **end of period k, 0-based**, so index 0 is the end of 2025 and index 79 the end of 2104; comparisons are made at those period ends (an annual grid), not at `t = 0`. The initial conditions are the start of 2025. **Automation lags by one period:** the stored `frac_automated[k]` is equations 13 and 2 evaluated on the largest training run stored at index `k − 1` (the initial run at `k = 0`); S3 reproduces that lag explicitly, and a comparison without the lag is not a valid comparison. Effective training compute is accumulated at the **previous** period's software efficiency (`best_training_run[k] = best[k−1] + training_compute[k] × S[k−1]`). The comparison window **2025 to 2100 is indices 0 to 75** (the shipped series run to index 79, which is the end of 2104, and are not used beyond index 75) |
  | **F3's own step** | S3 runs inside the 0.25-year loop (D-022); the comparison is at the annual period ends only; the effect of the loop step on S3 is reported separately (plan A2.6), not folded into this criterion |
  | **What a failure means** | **Reported, not relaxed.** A failure of any quantity at any year in any setting is recorded with its size and first year; a revised criterion would be a new labelled proposal for the editor. No year or setting is dropped because it fails |
  | **Years where the raw stock `Q` exceeds 10% of `C_L`** | **Reported separately and not excluded from the criterion.** The paper does not state the law of motion for effective compute once `Q` approaches or exceeds `C_L` (footnote 11 says it "must be adjusted" and does not give the adjustment), so S3 will have to supply one there and the comparison in those years tests that choice as much as the paper. The report therefore gives, for each setting, the largest and mean difference **in two groups of years**: those where `Q ≤ 0.1 C_L` and those where `Q > 0.1 C_L`, and the first year of the second group. **How the second group is identified** is limited by what the playground stores: the raw stock `Q` and usable compute `g(Q)` are **not stored** in the shipped series. The report therefore identifies those years from **S3's own `Q`** (fed GATE's investment path) and states that it did so; as a cross-check it also gives the years where the stored `compute / software` exceeds `C_L/11`, which equals the same condition **only if** the stored `compute` is `g(Q) S` (unverified: that ratio exceeds `C_L` by factors of 30 to 900 late in the shipped runs, which is impossible if it is `g(Q)`, so the stored `compute` may not be `g(Q) S`, see `research/gate-equations.md`, section 6, item 4). Both groups are in the criterion |
  | **Precision of the reference** | The shipped runs came from a solver with tolerance 0.02 and at most 40 iterations (`research/gate-equations.md`, section 4). With GATE's investment path supplied as input, S3's equations are deterministic given that path, so the solver's tolerance affects only whether the stored investment path is the optimum, not S3's response to it; the ±2% is applied to S3's response. If the comparison nevertheless shows differences that look like solver noise rather than equations, the report says so and does not change the criterion |

  **Report-only stress runs (the approved slow and fast settings).** Approved Settings 1 (slow: `T` = 1e41, λ_H = λ_S = 0.25) and 2 (fast: `T` = 1e33, λ_H = λ_S = 1, with the replacement rule for Setting 2 as already approved) are **kept**, with these changes only: they are **report-only** and have **no reference series**. They are run for A1.5 (the extreme-condition properties, including the corrected (d) on usable compute `g(Q)`) and for **finiteness** (no NaN, no negative stock, no overflow, all stocks finite to 2100). For these two runs S3 uses a behavioural investment path of its own (no GATE path exists), and the report states that. **They become A1.3 settings, with the ±2% criterion above, only if Epoch supplies the series** (for example in answer to a request to `info@epoch.ai`, the address the playground gives for questions), and then by a further dated note, not by this amendment.

  **Not changed by B.** The Proposal and the Decision of D-005 (the behavioural investment rule replaces the planner's optimisation); A1.4 (report only, for each of the three B settings); A1.6 (the ±10% fallback, now less likely to be needed since series exist for the three B settings, but still the fallback if the series prove unusable); the corrected A1.5(d); the λ rule (the playground shows 0.14 for both, which decides); the ±2% tolerance; the rule that failures are reported and not relaxed.

  **Open points B does not settle.** (1) The adjusted law for effective compute near `C_L` (above). (2) Whether the stored `compute` is `g(Q) S`. (3) The licence status of the shipped series: see D-026. B uses the three runs as reference values only under D-026's pattern; **if D-026 is not approved, B cannot be run as written** (the comparison needs the reference values at test time).

- **Approval of amendment B (recorded 2026-10-09).** Stéphane Beau approved amendment B above, **with one addition**, which is part of the approved text:
  > "If a failure is confined to years where the shipped series contradicts the paper's equation 10 (stored compute divided by software exceeds C_L), the report classifies it as 'playground differs from the paper'; S3 keeps the paper's equation; the criterion is still recorded as failed."

  So, as approved: the three A1.3 settings are the playground's shipped runs (default; conservative, `T` = 38 with `r_H`, `r_S` = 1, 1; aggressive, `T` = 33 with `r_H`, `r_S` = 7.1, 2); the criterion is ±2% at every annual period end 2025 to 2100 with the one-period automation lag; a failure is reported and not relaxed; the years where `Q` exceeds 10% of `C_L` are reported separately and not excluded; the approved slow and fast settings are report-only stress runs; and the addition above governs how a failure that coincides with the stored-compute-above-`C_L` years is classified (the classification does not turn a recorded failure into a pass). Amendment B depends on D-026, which was approved the same day. The wording of this entry's earlier Status, Decision and Date lines is unchanged; they were approved on 2026-10-08 and this record is appended to them.

- **Outcome note (2026-10-12, appended; no earlier line of D-005 is changed).** From the M1 step 2 work (`research/gate-equations.md` section 9, `audit/s3-gate-comparison.md`):
  (a) The stored `compute` field of the shipped runs is the **raw compute stock Q**, not effective compute (section 9.1, identity 1: `Q[k] = Q[k-1] exp(-delta_Q) + I_q[k] H[k-1]`, deviation 2e-16).
  (b) The premise of the equation-10 clause added in amendment B (stored compute divided by software exceeds C_L) is therefore **not supported**: that ratio is Q/S, and Q is not capped by C_L (eq. 10 caps g(Q), which the playground applies when it splits usable compute between training and runtime). The "playground differs from the paper" classification is **not applied to anything**.
  (c) The observation behind the clause came from an earlier misreading by the strategist (`research/gate-equations.md` section 6, item 4, which read the stored field as possibly g(Q) S); this work corrected it.
  (d) Which of the two compute rows counts for the A1.3 criterion (S3's raw stock Q, or effective compute g(Q) S, each against the stored `compute`) is left to the editor. It has no effect on the current result, because every compared row fails from the production composite onward (first failures 2026 to 2027). A1.3 is recorded as failed on all three shipped runs.

## D-006 — Critical minerals granularity in v0.1

- **Status:** Approved (2026-10-21)
- **Proposal:** One aggregate critical-minerals index in v0.1. Split into named minerals (candidates: copper, lithium, gallium, rare earths) in v0.2.
- **Decision:** Approved by the editor ("approve all", 2026-10-21): one aggregate critical-minerals index in v0.1; named minerals (copper, lithium, gallium, rare earths) in v0.2.
- **Date:** 2026-10-21
- **Outcome note (2026-10-21, appended).** The index is built from USGS data (public domain per the plan). **The USGS report PDF has not been read, so every figure taken from it stays [unverified] until it is read.** M5 is unblocked on this decision but has not been started.

## D-007 — Climate damage function

- **Status:** Approved (2026-10-12)
- **Context:** Estimates of economic damage from warming differ widely across the literature, and the choice strongly shapes results.
- **Proposal:** Do not pick one. Offer three options (low / central / high) as a scenario lever, each traced to a published source.
- **Decision:** Approved by Stéphane Beau ("fast-track", 2026-10-12): three switchable level-of-output damage options, low = Nordhaus (2017), central = Barrage and Nordhaus (2024), high = Howard and Sterner (2017) with the catastrophic term; default = central; temperature baselines aligned as the draft below states.
- **Date:** 2026-10-12

- **Draft for decision (2026-10-12, Proposed; appended; the lines above are unchanged and the status stays Proposed).** Evidence: `research/damage-functions-verified.md` (every number marked read, derived or unverified; copies held outside the repository). Nothing here is approved.

  **Context.** F3 needs one lever for how warming reduces output. Three functional forms exist in the sources read: level-effect quadratics (DICE) and a meta-regression (Howard and Sterner), and a growth-effect function (Burke et al.). The sources disagree by a factor of three to four at 3 degrees C among level forms, and by orders of magnitude between level and growth forms (Newell, Prest and Sexton: 2100 GDP impact 95% interval -84% to +359% for growth models, -8.5% to +1.8% for levels models). **Kotz et al. (2024) is retracted and not used.**

  **Options, each traced to a document read** (% of output, level effect, temperature above pre-industrial; **[read]** printed, **[derived]** computed from printed numbers):

  | Option | Source | 1.5 C | 2 C | 3 C | 4 C | Status of the numbers |
  |---|---|---|---|---|---|---|
  | **Low** | Nordhaus (2017), DICE-2016R, `0.236 T^2` | 0.53 | 0.94 | 2.1 [read] | 3.8 | coefficient and 3 C and 6 C anchors read; others derived |
  | **Central** | Barrage and Nordhaus (2024), DICE-2023 | 0.77 | 1.38 | 3.1 [read] | 5.5 | 3 C and 4.5 C anchors read (7.0%); coefficient not obtained, derived as 0.344 from the anchors; stated valid to 4 C |
  | **High** | Howard and Sterner (2017), preferred regression (4), non-catastrophic x 1.25 (and with the catastrophic term) | 1.67 (2.26) | 2.97 (4.01) | 6.69 (9.03) | 11.90 (16.06) | coefficients 0.595, 0.260 and the 1.25 factor read; damages derived; Barrage and Nordhaus read "9% at 3 C" for their preferred version |

  **Not offered as an option:** Burke, Hsiang and Miguel (2015) as a level function. It is a **growth-rate** function of each country's local temperature, its damages compound over time and have no horizon-free value at 3 C; its temperature-specific numbers and coefficient table were not readable from the copy obtained (marked unverified). Its headline (-23% of global income by 2100, RCP8.5, read) is a different kind of quantity. Hsiang et al. (2017) could not be read (blocked).

  **Questions for the editor (choices, not recommendations):**
  1. **Replace or add.** After D-016 F3 keeps three warming channels in the reused sectors: cost of capacity (+20% per unit of OW/OW2022 - 1), loss of capital (-10%), and TFP (-10%) (`research/damage-functions-verified.md` section 8, read from Earth4All.jl at `16f37d0`). Should the damage function **replace** them (switch their coefficients to zero) or **add** to them? Adding counts part of the damage twice; its size is unknown until M4 runs the reused sectors. Until M4 the slice's economy (S3) has no warming channel, so the question bites from M4.
  2. **Level or growth.** Level effects (the three options above) are the well-documented, comparable ones; a growth effect (Burke) may have far larger long-run impact and the sources disagree about whether the data can identify it at all. Should F3 offer a growth-effect option in a later release as a labelled stress case, or not?
  3. **Which temperature.** The options use warming above pre-industrial (DICE-2023 states 1765; Howard and Sterner convert to pre-industrial; DICE-2016R does not state its baseline in the text read). FaIR's anomaly here is above 1850-1900 and starts 0.04 to 0.07 K below observed (D-030, Proposed). Whether to add an offset is open.
  4. **Validity range.** The DICE-2023 function is stated valid to 4 C; the table's 4 C values and above are extrapolation for the other two.

  **Recommendation (the Validator's, separate from the above; the decision is the editor's):** offer **Nordhaus 2017 / Barrage and Nordhaus 2024 / Howard and Sterner (non-catastrophic x 1.25)** as low / central / high **level-effect** quadratics, labelled with their sources and their validity range, with the damage function **replacing** the three Earth4All warming channels once M4 brings them in (so damages are counted once), and with Burke-type growth effects **not offered in v0.1**. Reason: these are the ones I could read and recompute; the high option is about three times the central at 3 C, which spans most of the level-effect literature read; replacing avoids double counting without needing a measurement first. Weaker points: the DICE-2023 coefficient and the DICE-2016R baseline are not verified; the high option rests on a meta-regression whose appendix was not read.

  **What cannot be verified:** DICE-2023's `psi1`, `psi2` (SI not obtained); DICE-2016R's temperature baseline year; Howard and Sterner's online appendix; Burke et al.'s Extended Data Table 1 and 3 values and Fig. 5d; Hsiang et al. (2017); the size of the double counting.

- **Two points added to the draft (2026-10-12, appended; nothing above is changed or deleted; the status stays Proposed).**
  1. **The three options are all level-of-output effects and do not include the growth-effect case.** Nordhaus (2017), Barrage and Nordhaus (2024) and Howard and Sterner (2017, with and without the catastrophic term) lower the **level** of output by a share that grows with warming. The growth-effect case, Burke, Hsiang and Miguel (2015), whose abstract reports average global incomes about 23% lower by 2100 under unmitigated warming (read in the abstract), is **not** among them. **So the "high" option is not the upper end of the literature**, and **any dashboard or report text that uses it must say so** (for example: "high damage option: the highest of three level-effect functions; growth-effect estimates in the literature are larger and are not offered"). The Burke coefficients are **[unverified]**: the regression table in our copy was an image, so the coefficients and the table of projections were not read; the full paper's Supplementary Information has not been read either. The only Burke facts used are those printed in the text layer of the copy obtained (the 23% headline, the maximum near 13 C, the approximately linear global losses). Newell, Prest and Sexton, read in abstract only, report that growth and level models can differ by orders of magnitude, so the gap above the "high" option is not small.
  2. **Temperature baseline (what each function and FaIR use).** The warming each damage function takes, **as read in the documents**: Barrage and Nordhaus (2024): "global temperature increase since preindustrial times (1765)" [read]. Howard and Sterner (2017): warming "relative to the pre-industrial or current time", with each study's reference period converted to pre-industrial [read]. Nordhaus (2017): "global mean surface temperature", **reference year not stated in the main text** (searched for the words pre-industrial, preindustrial, 1765, 1750 and 1900; none appears) **[unverified]**. Burke et al. (2015): each country's own **annual mean temperature in degrees C**, not an anomaly against any baseline [read]; it is a different kind of input. **FaIR** here gives warming above the **1850-1900** mean (`docs/m2-step1-fair.md`). **Alignment, if the editor adopts level-effect options:** pre-industrial warming from FaIR (1850-1900) is used as the damage function's temperature without an offset, which treats 1765 and 1850-1900 as the same reference; the difference between those periods is **not measured here and is not read from the documents** [unverified]. A further, measured offset: FaIR's decadal warming starts 0.04 to 0.07 K below observed (D-030, approved), which would lower damages slightly at the current decade. Whether to apply an offset is open (question 3 above).
- **Outcome note (2026-10-12, appended; no earlier line changed).** Approved as stated in the Decision line. **Default option: central.** **The growth-effect case (Burke, Hsiang and Miguel 2015) is not represented, and every output that uses the "high" option must say that it is not the upper end of the literature** (growth-effect estimates are larger and are not offered). The three options are level-of-output effects; the damage function replaces or adds to the three Earth4All warming channels (replace-versus-add) is **not decided by this approval**: it bites from M4 and is delegated as a routine decision under the standing delegation in `CLAUDE.md`, to be recorded as Provisional. Until M4, the slice's economy has no warming channel and the damage function is the only one.

## D-008 — Social tension historical proxy

- **Status:** Approved (2026-10-21)
- **Context:** The Social Tension Index needs observed data to backtest against.
- **Proposal:** Research agent compares candidate datasets (political instability indices, protest-event data) on coverage since 1970, global scope and licensing, then proposes one.
- **Decision:** Approved by the editor ("approve all", 2026-10-21), option 3 of the evidence note: no backtest of the social-tension index against event data. S7 is calibrated on its drivers (inequality, labour share) and tension is reported as a model-internal index.
- **Date:** 2026-10-21

- **Evidence note (2026-10-08, Research agent role; the entry above is unchanged and the decision is still open).** Candidates compared on coverage since 1970, global scope and terms. The full rows and what was verified are in `research/SOURCES.md` (section "Research for the missing rows"). Only the UCDP row was checked against a primary page; the others rest on library-guide summaries and are unverified.

  | Candidate | Content | Coverage | Global from 1970? | Terms |
  |---|---|---|---|---|
  | UCDP/PRIO Armed Conflict | state-based armed conflict | 1946-2025 (verified) | yes, but armed conflict only | CC BY 4.0 (verified) |
  | UCDP One-sided Violence, Non-State Conflict | violence against civilians; conflict between non-state groups | 1989-2025 (verified) | no, starts 1989 | CC BY 4.0 (verified) |
  | Cross-National Time-Series Archive (Banks) | riots, strikes, demonstrations, assassinations, government crises, revolutions | 1815-2023 (unverified) | yes | paid licence; redistribution restricted (unverified) |
  | Global Terrorism Database | terrorist events | from 1970 (unverified) | yes, terrorism only | not checked |
  | GDELT | automated news-event coding, including protest | from 1979 (unverified) | from 1979 | not checked |
  | ACLED | political violence and protest | modern; start date not given | no | not checked |
  | SCAD | social conflict | 1990-2017, Africa and parts of the Americas (unverified) | no | not checked |

  **Findings.** No candidate found combines global coverage, protest-type events and open terms from 1970. The only one with protest-type events before 1990 (CNTS) is paid, and its terms probably forbid publishing the underlying series, which conflicts with D-001's requirement to publish processed data under CC BY 4.0. UCDP is open and verified but measures armed conflict, not social tension, and has a coverage break at 1989 for two of its three datasets. Whether any of these measures "social tension" as Earth4All's index defines it (a smoothed index of inequality and well-being effects, not event counts) is not established: a proxy built from conflict events would be a different concept.

  **Options for the editor-in-chief (not recommendations to adopt without a check of the terms):** (1) build a composite from open sources only (UCDP armed conflict from 1970, GTD from 1970 if its terms allow, GDELT from 1979), accepting uneven coverage and that it measures violence, not tension; (2) obtain a CNTS licence and publish only derived, non-reversible indices if its terms permit; (3) do not backtest the social-tension index against events, and calibrate S7 on its drivers instead (inequality from WID and labour share from ILOSTAT, both with terms still unverified), reporting tension as a model-internal index. **Not done:** the terms of GTD, GDELT, ACLED, WID and ILOSTAT were not read from their own pages, so no option is yet cleared for publication.
- **Outcome note (2026-10-21, appended).** Rules that follow from the approval: (1) **wherever the tension index is shown it is labelled "not validated against history"**; (2) **UCDP armed conflict (CC BY 4.0, 1946 onward) may be shown only as a labelled plausibility overlay, never as a calibration target**; (3) **the tension index is excluded from the D-024 backtest framework**; (4) **the terms of WID and ILOSTAT are still unverified, so reading their terms is a STOP-and-ask item before any use of either**; (5) **the long labour-share series starts only in 2004**. M5 is unblocked on this decision but has not been started.

## D-009 — Dashboard stack

- **Status:** Approved (2026-10-12)
- **Candidates:** Streamlit (live runs, simplest); static site with precomputed scenario runs (cheapest to host, fastest for users).
- **Decision:** Approved by Stéphane Beau ("fast-track", 2026-10-12): the dashboard is a static site that plays precomputed scenario grids, no backend.
- **Date:** 2026-10-12
- **Outcome note (2026-10-12, appended; no earlier line changed).** Scope as approved: **static site, precomputed scenario grids, no backend.** Live runs (for example Streamlit) are a later option and are **not part of Phase 2 or of Phase 4's first release.** Publishing anything remains the editor's decision (plan A2.7 for Demo 0).

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

- **Outcome note (2026-10-08): the age-cohort check left open above.** Data: UN World Population Prospects 2024, file `WPP2024_Population1JanuaryByAge5GroupSex_Medium.csv.gz` (1 January, World, Medium variant, 5-year age groups; downloaded 2026-10-08 into a scratch folder outside the repository; https://population.un.org/wpp/). The 0-14, 15-44, 45-64 and 65+ cohorts of World3 are formed from the 5-year groups at exactly those boundaries. Model values are the 1900 runs of the port's reference (WorldDynamics.jl), taken at t equal to the calendar year, unscaled. The file is labelled Medium variant, and the WPP 2024 Summary of Results lists 2024 among its projections ("estimates for 1995 and projections (medium scenario), 2024, 2054 and 2100"): the 2025 values are therefore **medium-variant projections, not counts**, and earlier entries that call them "observed" should be read that way (1970 and 2000 are estimates). The mid-year (1 July) shares differ from the 1 January shares by at most 0.2 points.

  | | 0-14 | 15-44 | 45-64 | 65+ |
  |---|---|---|---|---|
  | **1970 observed share** | 37.8% | 42.3% | 14.7% | 5.3% |
  | 1970, 1974 set (model minus observed, points) | 36.7% (-1.1) | 41.0% (-1.3) | 15.2% (+0.5) | 7.1% (+1.9) |
  | 1970, 2004 set | 34.5% (-3.3) | 40.9% (-1.3) | 16.1% (+1.4) | 8.5% (+3.2) |
  | **2025 observed share** | 24.6% | 44.1% | 21.0% | 10.3% |
  | 2025, 1974 set | 25.6% (+1.0) | 42.0% (-2.1) | 19.6% (-1.4) | 12.8% (+2.5) |
  | 2025, 2004 set | 22.2% (-2.3) | 40.5% (-3.7) | 20.6% (-0.5) | 16.8% (+6.4) |

  The 65+ group in millions, model against observed: 1970, 261 (1974 set) and 322 (2004 set) against 192, that is +35% and +67%; 2025, 905 and 1260 against 845, that is +7% and +49%. For 2025 the other groups are also below observed in the 2004 set: 0-14 by 17%, 15-44 by 16%, 45-64 by 10% (1974 set: by 10%, 18% and 20%).

  **What this shows.** The 2004 parameter set's closer total population (Finding 3) comes with a **worse age structure**: it has too many people aged 65 and over from the start (8.5% against 5.3% in 1970) and, by 2025, 16.8% against 10.3% projected, while its working-age and young groups fall short. The 1974 set is closer in age structure at both dates (largest share gap: 1.9 points in 1970 and 2.5 in 2025, against 3.3 and 6.4 for the 2004 set). The two criteria point in opposite directions, so the 2004 set's lead on the total does not establish that it is the better set for population as a whole. This bears on the amended Decision (2004 provisional default, confirmed at the Phase 3 backtest) and is a reason to include age structure, not only total population, among the backtest criteria; it does not change the Decision.

  **Date basis (additional correction).** Against the 1 January totals in this file, the model's 1970 population is 3.657 bn for the 1974 set (observed 3.657 bn, +0.0%) and 3.792 bn for the 2004 set (+3.7%); in 2000 the gaps are -7.1% and -0.6%, and in 2025 -13.9% and -8.2%. Finding 3 above compares the same model values with 1 July totals (-1.0% / +2.6% in 1970, -7.8% / -1.3% in 2000, -14.3% / -8.6% in 2025). Which date matches the model's t is not established (World3's time convention within a year was not checked), so the true gap lies within about one point of either table; the conclusions of Finding 3 do not depend on it. The same applies to the evidence table in D-019, which uses the 1 July values.

  **Not done:** the book's tables and Herrington's Supporting Information remain unread (the other check named in the amended Decision). Only the world total was used; no regional comparison.

- **Outcome note (2026-10-08, after D-022): date basis of Finding 3.** The gaps in Finding 3 compare the model value at `t = Y` with the UN **1 July** value: that is reading B of `docs/time-convention-evidence.md`. D-022 adopts `t = Y` as 1 January of year Y, so the matching comparison is reading A: the model at `t = Y` against the UN **1 January** value (file `WPP2024_Population1JanuaryByAge5GroupSex_Medium.csv.gz`, world total as the sum of the age groups; values after 2023 are medium-variant projections). Finding 3's table under reading A:

  | year | UN 1 January (bn) | 1974 model | 2004 variant |
  |---|---|---|---|
  | 1970 | 3.657 | 3.657 (+0.0%) | 3.792 (+3.7%) |
  | 1980 | 4.408 | 4.294 (-2.6%) | 4.486 (+1.8%) |
  | 2000 | 6.130 | 5.693 (-7.1%) | 6.092 (-0.6%) |
  | 2010 | 6.977 | 6.396 (-8.3%) | 6.852 (-1.8%) |
  | 2020 | 7.851 | 6.961 (-11.3%) | 7.402 (-5.7%) |
  | 2025 | 8.197 | 7.057 (-13.9%) | 7.523 (-8.2%) |

  Every gap moves by 0.4 to 1.0 point. The conclusions of Finding 3 are unchanged: the 1974 model is nearer in 1970 only, the 2004 variant is nearer from 1980 on, and neither stays within 2% to 2025. The earlier date-basis note above (which gave both date bases) is consistent with this one. The Decision (2004 set as provisional default) is unaffected.
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

- **Status:** Approved (2026-10-08)
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
- **Decision:** Approved: Option C. Applies to the World3-based sectors; other F3 sectors define their own 1970 starting data in their own decisions. (Approved by Stéphane Beau, as drafted.)
- **Date:** 2026-10-08

- **Outcome note (2026-10-08, after D-022): date basis and one correction.** The population gaps in evidence items 2 and 3 compare the model at `t = Y` with the UN **1 July** value (reading B of `docs/time-convention-evidence.md`). D-022 adopts `t = Y` as 1 January, so the matching reading is A (UN 1 January values; see the outcome note on D-015). Under reading A, item 2 becomes: model total population in 1970 is 3.657 bn for the 1974 set (UN 1 January 3.657 bn, +0.0%) and 3.792 bn for the 2004 set (+3.7%). Item 3's experiment, re-run with the cohorts scaled to the UN 1 January 1970 total (3.6567 bn):

  | parameter set | start | 2000 vs observed | 2025 vs observed |
  |---|---|---|---|
  | 1974 | 1970 state from the 1900 run | -7.1% | -13.9% |
  | 1974 | cohorts scaled to the UN 1 January 1970 total | -7.1% | -13.9% |
  | 2004 | 1970 state from the 1900 run | -0.6% | -8.2% |
  | 2004 | cohorts scaled to the UN 1 January 1970 total | -4.2% | -11.5% |

  **Correction to item 3.** The sentence "for the 1974 set it helps by about one point" does **not** hold under reading A. The 1974 set's 1970 total already equals the UN 1 January total (scale factor 1.0000), so the scaling changes nothing for it; the one-point gain in the table above came from comparing with the 1 July value. For the 2004 set the finding holds and is slightly stronger (2000: -0.6% becomes -4.2%; 2025: -8.2% becomes -11.5%, against -3.8% and -11.0% before). So the conclusion drawn from item 3, that matching the 1970 total does not by itself improve the later fit, stands, and the Decision (Option C) is unaffected. `docs/phase-1-review.md`, section 2 ("Starting in 1970"), repeats the 1974 sentence and has not been edited.
---

## D-020 — Start years and initial states of the sectors that are not World3-based (plan item N1)

- **Status:** Approved (2026-10-08)
- **Context:** D-019 (Option C) fixes the 1970 start for the World3-based sectors and says other sectors define their own starting data in their own decisions. This is that decision for S3, the data-centre module, the reused Earth4All sectors and FaIR. The plan (`docs/phase-2-plan.md`, N1) named only S3 and the data-centre module; the Earth4All start year turned up while gathering the evidence and is included here because it has the same cause. Needed before M1.
- **Evidence** (read 2026-10-08; where a figure comes through a summarising fetch tool rather than verbatim it is said):
  1. *World3 sectors:* start 1900, reported from 1970 (D-019).
  2. *Reused Earth4All sectors:* the package solves **1980 to 2100** (`src/earth4all/solutions.jl`: `WorldDynamics.solve(run_tltl(), (1980, 2100), ...)`), and its initial values are 1980 values. It has no 1970 state, so F3's 1970 start (MODEL_SPEC) is not available from it. The audit exports have 7,681 points, 120 years at 1/64 year.
  3. *GATE* (arXiv:2503.04941 v2, whole HTML text read through a summarising tool, Appendices C and D included): initial conditions are "at the start of 2025" (labour force, capital, hardware R&D, software efficiency, largest training run, runtime compute); global output is "produced globally in 2024". Defaults: output 110 trillion USD/year, capital 450 trillion USD, labour 3.6 billion, hardware efficiency 1e18 FLOP/year/USD, software efficiency 1, largest training run 5e25 effective FLOP, runtime compute 1e28 effective FLOP/year, compute investment 2e11 USD/year, hardware R&D 1e11, software R&D 5e9. Time step 1 year; the planner's horizon is typically 80 periods (optimisation horizon 160 years); solved by gradient descent. The paper has internal inconsistencies (output "$105T" in text against 110 trillion in the table; software R&D "$10B/year" in a heading against $5B in the reasoning). It states no calibration period and no source for initial capital and output beyond a World Bank figure. Section 3.7 says the compute module "maps any given path of investment" into effective compute, which suggests an investment path can be supplied; no exogenous-path mode is described.
  4. *Epoch AI data* (pages opened): the AI-models dataset covers "from 1950 to today"; the AI-data-centers dataset covers sites operational "in 2024 or later, with some exceptions", with a timeline axis from Q1 2023.
  5. *IEA:* data-centre electricity about 415 TWh in 2024 (*Energy and AI*) and 485 TWh in 2025 (*Key Questions*). The historical series before 2024 was not read.
  6. *FaIR:* needs an emissions history; the calibrated versions use historical emissions that start long before 1970 (see D-021).
- **Consequence to settle:** GATE's economy (output 110 trillion, capital 450 trillion in 2025) and Earth4All's economy in 2025 are two different models of the same world; they will not agree, and which one the coupled model uses from 2025 has to be decided (see option A).
- **Proposal** (options, mutually exclusive for each question; the decision is the editor-in-chief's):
  - **Question 1, S3 and the data-centre module.**
    - **A. Switch on in 2025** from GATE's initial values. Before 2025 the automation fraction is held at GATE's initial value and data-centre electricity is prescribed from IEA estimates where available. Uses GATE as published; no S3 backtest before 2025; needs a rule for reconciling GATE's economy with Earth4All's in 2025.
    - **B. Start in 1970** with back-cast values. No data for the AI sector that far back (data centres 2023 on, GATE not calibrated before 2025); the back-cast would be invented.
    - **C. Start earlier than 2025 (for example 2010)** using Epoch's training-compute series as a hindcast of compute only, with the automation fraction and GATE's economy from 2025. Gives a partial backtest of compute; adds a second start rule.
  - **Question 2, the reused Earth4All sectors.**
    - **(i)** They enter in 1980 from their own initial state; from 1970 to 1980 only the World3-based sectors run and the Earth4All variables are undefined (or prescribed).
    - **(ii)** F3's coupled run starts in 1980 and 1970 to 1980 is reported from World3 alone.
    - **(iii)** Back-cast Earth4All's 1980 state to 1970 (no method exists in the package; the cost is not known).
  - **Validator's recommendation: A for question 1 and (i) for question 2.** Reasons: they use each reference as published and do not invent data; the price is that nothing coupled is reported before 1980 and nothing from S3 before 2025. This is a recommendation, not a decision.
- **What each choice does to the plan:** A and (i) change A6.6 (the 1970 state) to "World3-based sectors from 1970, Earth4All sectors from 1980, S3 from 2025", and make the backtest of the coupled economy start in 1980; a 1970 backtest then applies to population only. B and (iii) keep a 1970 backtest of everything, at the cost of invented starting values.
- **Alternatives considered:** a single common start year for all sectors (2025, losing the historical comparison; or 1980, losing 1970 to 1980).
- **Sources:** `src/earth4all/solutions.jl` in Earth4All.jl at `16f37d0`; arXiv:2503.04941 v2 (CC BY 4.0); https://epoch.ai/data (licence wording verified); IEA reports (CC BY 4.0); D-019.
- **Proposed by:** Claude (Research and Validator roles)
- **Decision:** Approved by Stéphane Beau: question 1 option A (S3 and the data-centre module switch on in 2025 from GATE's initial values; before 2025 the automation fraction is held at GATE's initial value and data-centre electricity is prescribed from IEA estimates where available); question 2 option (i) (the reused Earth4All sectors enter in 1980 from their own initial state; from 1970 to 1980 only the World3-based sectors run, and the Earth4All variables are undefined or prescribed). The Validator's recommendation was adopted as drafted.
- **Date:** 2026-10-08

---

## D-021 — How FaIR is coupled, and the source of non-CO2 emissions (plan item N2)

- **Status:** Approved (2026-10-08)
- **Context:** S6 uses FaIR (D-010, MODEL_SPEC). Two things are open: how an annual climate model with memory is advanced inside a feedback loop (the M2 risk the plan names), and where emissions of non-CO2 gases and land-use CO2 come from, since D-016 replaces the Earth4All climate and foodland sectors that produced them and World3 agriculture has none. Needed before M2.
- **Evidence:**
  1. *FaIR 2.2.4 documentation* (docs.fairmodel.net, "Introduction" and "Basic example", read 2026-10-08): time is defined once with `define_time(start, end, step)` and need not be integer years; a run is one `f.run()` over that horizon; initial conditions at the first time bound are set with `initialise(...)`; temperature and the other states sit on time bounds, emissions on time points at step centres. **The pages do not describe running in segments or restarting from a previous state.** A search found no documented restart method.
  2. *Probe, run here* (`audit/t0/fair_segment_probe.py`, FaIR 2.2.4 in a scratch environment; **toy case**: CO2 only, one scenario, one configuration, **illustrative climate parameters, not a calibrated configuration**; a real configuration has about 61 species). Carrying the last-time-bound state (concentration, forcing, temperature, cumulative and airborne emissions, ocean heat content, gas-box partitions) into the next segment:

| segmentation, 2000 to 2040 or 2020 | result against one run |
|---|---|
| one run 2000-2020, step 1.0 / 0.5 / 0.25 year | T(2020) 0.109351 / 0.109410 / 0.109435 K (the step effect inside one run) |
| 20 annual segments, 2000-2020 | T(2020) 0.109797 K, **+4.5e-4 K (0.41% of the warming)** |
| 1 restart (2 segments), 2000-2040 | +7.7e-6 K (0.003%) |
| 3 restarts | +2.9e-5 K (0.01%) |
| 39 annual restarts | +5.2e-4 K (0.20%) |
| **re-run from the start every year** (1750 to y, 130 runs) | **0.0 K difference** |

     So carrying state works mechanically but is **not equivalent** to one run (the error grows with the number of restarts; carrying the unreported state variables I tried gave no improvement; the cause was not found). Re-running from the start is exact. Cost in the toy: 0.25 s for a 350-year run, 24 s for 130 annual re-runs; with about 61 species the cost is **not measured** and is probably much higher.
  3. *Emissions inputs:* the AR6-consistent FaIR calibration takes historical emissions of CO2 and the short-lived species from RCMIP v5.1.0 (from search results on fair-calibrate and its documentation, secondary; some versions replace CO2 with Global Carbon Project estimates). The Community Emissions Data System covers BC, OC, SO2, NOx, NH3, CH4, CO, NMVOC, CO2 and N2O, with CH4 and N2O only from 1970 in its main system (search summary, secondary; licence **not verified**). The licence of RCMIP was not checked.
  4. *Earth4All's own producers:* methane and nitrous oxide emissions come from the climate sector (`MMCH4E`, `MMN2OE`) via the exogenous 1%-per-year intensity declines classed as behaviour forcing (D-016); land-use CO2 from foodland. Both sectors are replaced.
- **Proposal:**
  - **Coupling question.**
    - **(a) Re-run from the start each year**: exact, simple, cost unknown with a real configuration and multiplied by the Monte Carlo count in Phase 3 (the toy figure of 24 s per full run would be about 6.7 hours for 1,000 runs on one core, for FaIR alone).
    - **(b) Carry state between annual segments**: fast; the toy error is 0.2% to 0.4% of the warming and unexplained; acceptable only if its size with a real configuration is measured and accepted by the editor.
    - **(c) Restart rarely** (for example every 10 or 20 years, with the state carried and one-year steps in between by re-running only the last window): error between the two above; not tested beyond the toy's 1 and 3 restarts.
    - **(d) Run FaIR once per scenario outside the loop** with prescribed emissions: no feedback from temperature to the economy, so loop B2 and every warming channel would be open-loop. Listed for completeness; it does not meet the plan's A2.3.
  - **Emissions question.**
    - **(A) Prescribe non-CO2 emissions and land-use CO2** from RCMIP historical series and a chosen SSP scenario for the future, independent of F3: simple; they do not respond to F3's economy, so F3 would say nothing about methane or land-use policy.
    - **(B) Recorded Earth4All series**: tied to its scenarios and to 1980 on.
    - **(C) A simplified F3 module** producing methane, nitrous oxide and land-use CO2: responsive, but new and unreferenced (M5 scale work).
  - **Validator's recommendation: (a) for the slice and for M2's acceptance tests, with (b) and (c) tested once a real configuration exists and the editor decides; and (A) for M2, labelled on the demo as "non-CO2 emissions are prescribed, not modelled".** A calibrated configuration (fair-calibrate's published ensemble or a single configuration from it) was not tried. This is a recommendation.
- **Not done:** a real FaIR configuration; a check that FaIR's temperature baseline (pre-industrial) matches Earth4All's observed-warming baseline `OW2022` (see D-023, warming baseline); the licences of RCMIP and CEDS.
- **Alternatives considered:** a simplified FaIR-like response model written by F3 (more control, new unreferenced code, D-010's choice of FaIR would be reopened).
- **Sources:** FaIR 2.2.4 documentation and code (Apache 2.0); `audit/t0/fair_segment_probe.py`; fair-calibrate (GMD 17, 8569, 2024); Global Carbon Budget 2025 (CC BY 4.0, verified).
- **Proposed by:** Claude (Research role)
- **Decision:** Approved by Stéphane Beau: coupling option (a), FaIR is re-run from the start each year, for the slice and for M2's acceptance tests; options (b) and (c) are to be re-tested once a real FaIR configuration exists, and the editor then decides. Emissions option (A): non-CO2 emissions and land-use CO2 are prescribed, and every use of F3 results that depends on them is labelled "non-CO2 emissions are prescribed, not modelled".
- **Date:** 2026-10-08

- **Outcome note (2026-10-12, appended; no earlier line changed).** The cost of the re-run rule was measured with a real configuration in M2 step 1 (`audit/m2-fair-report.md`, section 6): the published fair-calibrate v1.4.1 constrained ensemble, annual re-runs from 1750. About 19 s per annual re-run with all 841 members (about 39 minutes for a 120-year loop, 1980 to 2100) and about 1 s with 20 members (about 2 minutes). Options (b) and (c) have not been re-tested; the editor decides per the entry above. Also: A2.1 failed in that step (ensemble-mean 2015-2024 warming 1.196 K, 0.037 K below HadCRUT5's mean 95% interval); see the report.

- **Outcome note (2026-10-12, later, appended; no earlier line changed).** The state-carrying options were measured with the real configuration (`audit/m2-d021-measurement.md`; readings fixed first in `docs/m2-d021-measurement.md`): (b) carry state between annual segments and (c) restart every 10 years, each against (a) re-run from the start, 841 members, to 2100. Headline numbers, absolute K, chains started at 2025 (the realistic coupling window), errors 2025 to 2100: **ensemble-mean error at most 0.0021 K for (b) and 0.0018 K for (c)** with internal variability matched, and 0.0010 K and 0.0009 K without it; **the largest error of any single member 0.265 K for (b) and 0.223 K for (c)** with variability, 0.036 K and 0.023 K without. Chains from 1980 reach about 0.025 K in the ensemble mean, almost all before 2025. As a share of the warming since 1850, the ensemble-mean error at 2100 is at most 0.04%. **Cost:** a carried one-year segment takes 10.8 to 12.2 s with 841 members, about as long as an exact re-run (14.7 to 17.1 s), so (b) and (c) save little time with unmodified FaIR; a 120-year loop of exact re-runs takes about 30 to 34 minutes. **Correction:** the earlier note above that the projection was 4% low was wrong (see the report). **20-member subset** (every 42nd member, rule fixed beforehand), 2025 to 2100: mean within 0.054 K of the 841-member mean at every year; 5th and 95th percentiles up to 0.176 K and 0.321 K different (95th percentile 0.321 K low at 2100). **The editor chooses among (a), (b) and (c); nothing is chosen here.**

- **Editor decision note (2026-10-12, appended; no earlier line changed).** Stéphane Beau chose **option (a)** for the re-run rule: FaIR is re-run from the start each year (exact), **with all 841 members for precomputed published runs**. **The 20-member subset is not used for published bands** (the measurement showed its 5th-95th percentile band is poorly represented, `audit/m2-d021-measurement.md` section 5). Options (b) and (c) are not adopted. Whether a smaller ensemble may be used for development or testing runs is not decided by this note. Cost to expect, measured: about 30 to 34 minutes for one 1980-2100 loop of exact re-runs with 841 members on this machine.

---

## D-022 — Sector interface and time convention (plan item N3)

- **Status:** Approved (2026-10-08)
- **Context:** M0 built the interface (`docs/coupling-interface.md`, `f3/core/`) and ran S1 inside it. This decision records its rules and settles the time convention (review item 16). Needed before M1 builds on it. **The evidence for the time convention is in `docs/time-convention-evidence.md`, which should be read first.**
- **Interface evidence:** S1 inside the loop equals stand-alone S1 bit for bit (worst relative difference 0.0 on all 15 states, both parameter sets; criterion 1e-9). The first-order error of start-of-step coupling, measured with S1 and recorded inputs (`audit/t0/coupling_error.py`, held against exact):

| loop step | 1974 set, worst state (fcfpc1) | 1974 total population | 2004 set, worst state | 2004 total population |
|---|---|---|---|---|
| 0.5 year | 2.15% | 0.38% | 1.87% | 0.49% |
| **0.25 year (D-003)** | **1.04%** | **0.19%** | **0.93%** | **0.24%** |
| 0.125 year | 0.51% | 0.09% | 0.46% | 0.12% |
| 0.0625 year | 0.25% | 0.05% | 0.23% | 0.06% |

  The error halves when the step halves (first order). It is for S1 with recorded partners; the error with live partners is unknown and is tested in M2 (A2.6).
- **Time convention evidence, summarised:** neither reference nor the equations say what a time value means on a calendar. A half-year shift moves population comparisons by up to about 2 points around 1970 and about 0.4 points in 2025, and calendar-year flow comparisons by up to about 1%. FaIR's own documented convention is that temperature and other states are on time bounds (step boundaries) and emissions on time points at step centres.
- **Proposal:**
  - **Interface (as built):** fixed step 0.25 year (D-003); explicit coupling at step boundaries (each sector reads the start-of-step values of the others); units checked, never converted; a sector with a longer period (FaIR, annual) advances every fourth step; every exchanged series recorded with units; a coupling is refused if a switch time would fall inside a step. **Alternative:** add a predictor-corrector (implicit coupling) now: halves the error order at the cost of two sector advances per step and a state save/restore the interface does not have. **Validator's recommendation:** keep explicit coupling; revisit only if A2.6 shows the step matters.
  - **Time convention.** **(1)** `t = Y` is 1 January of year Y: stocks are values on that date, flows are rates per year at that instant, and a calendar-year total is the integral over `[Y, Y+1]`. **(2)** `t = Y` is mid-year. **(3)** No convention is adopted; every comparison states its date basis and compares like with like. **Validator's recommendation: (1)**, because it matches FaIR's boundary-and-centre convention (states on boundaries), puts F3's yearly reporting on the same grid as the UN's 1 January file and the 1970 start of D-019, and costs nothing in the equations. The evidence does **not** show that the World3 authors intended it; it is a labelling choice, and the 2% tolerance of D-004 between F3 and a reference on the same time axis is unaffected by it.
- **What this changes:** under (1), earlier comparisons with mid-year data (D-015 Finding 3, D-019) are re-read as reading B of the evidence page; the matching comparison is reading A (differences of 0.4 to 1.0 point). No approved decision is edited; an outcome note would be added.
- **Not covered:** parallel advance, state save and restore, sub-stepping, regional vectors (listed in `docs/coupling-interface.md`, "Not in this interface").
- **Sources:** `docs/coupling-interface.md`; `docs/time-convention-evidence.md`; `audit/t0/coupling_error.py`; FaIR documentation.
- **Proposed by:** Claude (Modeler and Validator roles)
- **Decision:** Approved by Stéphane Beau: explicit coupling at step boundaries with the 0.25-year step (as built, no predictor-corrector); time convention (1): t = Y is 1 January of year Y, stocks are values on that date, flows are rates per year at that instant, and a calendar-year total is the integral over [Y, Y+1].
- **Date:** 2026-10-08

---

## D-023 — Inputs to the reused Earth4All sectors from the sectors F3 replaces (plan item N4)

- **Status:** Approved (2026-10-08)
- **Context:** D-016 replaces Earth4All's population, climate, foodland and wellbeing sectors and reuses the others. The reused sectors read variables the replaced sectors compute, and the replaced sectors read some of theirs. Needed before M4.
- **Evidence** (`audit/t0/earth4all_links.jl`, from the composed TLTL system; `audit/data/earth4all_cross_sector_links.csv`): the composed model has 71 cross-sector connections: 45 within the same group, **18 from replaced to reused**, 8 from reused to replaced. The 18 carry **eight distinct signals**:

| signal | computed by (replaced) | read by (reused) | what F3 would use instead |
|---|---|---|---|
| `POP` population | population | demand, energy, other, public | S1 total population (persons against Earth4All's Mp: a unit adapter) |
| `GDPP` GDP per person | population | energy, labour market, other, output, public | S2's GDP divided by S1 population: **new equation, not in S1** |
| `EGDPP` effective GDP per person (a smoothed variable) | population | demand | a smoothing of `GDPP` with Earth4All's own time constant: **new equation** |
| `A20PA` aged 20 to pension age | population | labour market | from World3's cohorts, **whose age bands differ** (see below) |
| `OW` observed warming | climate | output, public | FaIR temperature anomaly; **baseline not checked** |
| `CAC` cost of air capture | climate | energy | `DACCO2` times a capture cost: **new equation** (zero when direct air capture is zero, as in Too Little Too Late) |
| `COFO` cost of food | foodland | other | World3 agriculture has no equivalent; "other" is not assessed in D-016 |
| `IPP` policy introduction period | wellbeing | demand, energy, labour market | a scenario constant (it is `EIP` or `RD` depending on a flag), not a state |

  The 8 reused-to-replaced connections carry `GDP` (inventory to climate, foodland, population), `INEQ` and `WDI` (demand to wellbeing), `LPR` (labour market to wellbeing), `PSP` (public to wellbeing) and `CO2EI` (energy to climate).
  **Age bands.** Earth4All's cohorts are 0-20, 20-40, 40-60 and 60+; World3's are 0-14, 15-44, 45-64 and 65+; Earth4All's working-age population is 20 to pension age (`A20PA = A2040 + A4060 + A60PL - OP`) and the labour market reads it. Measured shares for comparison (not an error measure, since the definitions differ): Earth4All TLTL working-age share 44.7% (1980), 54.8% (2000), 61.0% (2020); World3 ages 15-64 share 56.9% / 58.4% / 60.5% (1974 set) and 57.4% / 58.7% / 60.3% (2004 set). The gap in 1980 is 12 points, in 2020 under 1 point. **The labour market's T2 result (D-016) was obtained with Earth4All's own population; with World3's cohorts the working-age series would differ, so T2 has to be re-run on the coupled model.**
- **Proposal:**
  - **A. Replay Earth4All's recorded series for these signals** in every test and in a first coupled version: exact, tied to its scenarios and to 1980, no adapters to validate. It cannot represent F3's own population or climate.
  - **B. F3's own sectors from the start**, through adapters for the eight signals: the coupled model F3 wants; each adapter is new code that needs a test, and the working-age and warming-baseline mappings are open questions.
  - **C. Both, in sequence** (the plan's A4.1 and A4.5 already test the sectors against recorded inputs first): replay for the sector tests, adapters for the coupled model, with the difference between the two runs reported as the adapters' effect.
  - **Validator's recommendation: C.** The interface is small (eight signals), so the adapters are cheap relative to the sectors; the working-age mapping and the warming baseline must be settled before M4's labour-market and output tests, not after.
- **Warming baseline, evidence (read from the code):** the reused sectors divide the observed warming by a **fixed constant**: `OW / OW2022` with `OW2022 = 1.35` (a parameter, 1.35 degrees C, stated in the parameter files of output, population, foodland and climate as "observed warming in 2022"). Earth4All's own `OW` is `WA1980 + (EHS - EH1980) * WFEH` in the climate sector, that is a warming relative to a 1980 anchor plus a response to ocean heat; its reference period relative to pre-industrial was not read. FaIR reports temperature relative to its own pre-industrial reference. If F3 feeds FaIR's anomaly into `OW`, the ratio `OW / 1.35` is meaningful only if both are on the same baseline; **this was not checked**, and an offset of a few tenths of a degree would change the size of the three warming channels in output and public. It has to be settled before the M4 tests of those two sectors.
- **Open before M4:** the warming baseline above; which pension-age rule applies when the cohorts are World3's.
- **Sources:** `audit/data/earth4all_cross_sector_links.csv`; `audit/t0/earth4all_links.jl`; `src/*/subsystems.jl` in Earth4All.jl; `audit/earth4all-audit.md` (T2).
- **Proposed by:** Claude (Modeler role)
- **Decision:** Approved by Stéphane Beau: option C. Recorded Earth4All series are replayed for the sector tests, and adapters from F3's own sectors are used for the coupled model, with the difference between the two runs reported as the adapters' effect. The warming baseline and the working-age mapping stay open before M4, as the entry says.
- **Date:** 2026-10-08

---

## D-024 — Phase 3 backtest criteria, fixed before the data are used (plan item N5)

- **Status:** Approved as a framework (2026-10-08)
- **Context:** Phase 3 backtests F3 against observed data. D-015's amendment fixes 2000 to 2025 as the out-of-sample period for the choice of World3 parameter set; the plan asks for the criteria to be fixed now so that "good" is defined before the data are seen, in the way D-004 and D-017 were. This entry proposes a framework and leaves numerical thresholds to the editor, to be set before the series are loaded (plan A5.4). Needed before the M5 hindcast and before Phase 3.
- **Evidence** (computed with the port's reference runs and the UN WPP 2024 age-group file, 1 January values; `/tmp` script not committed, reproducible with `audit/t0/time_convention.py`'s data):
  1. *The out-of-sample window.* The UN file's estimates end in 2023; 2024 and 2025 are medium-variant projections. A test over "2000 to 2025" therefore ends with two projected years. **Proposal: test on 2000 to 2023 and report 2024 and 2025 separately as comparisons with projections.**
  2. *Naive benchmarks.* A model has to beat a trivial forecast to claim skill. Fitted on data before 2000 only, total population 2000 to 2023, mean absolute relative error: **World3 1974 set 9.4%; World3 2004 set 3.3%; log-linear trend 1970 to 1999: 8.6%; the 1989 to 1999 growth rate held: 3.8%.** The 2004 set beats the second naive benchmark by 0.5 points, which is small; the 1974 set does not beat the first.
  3. *Age structure* (D-015 outcome note): the 65+ share is too high in both sets, by 27% to 41% (1974 set) and 66% to 81% (2004 set) relative to observed, 2000 to 2023 (observed 6.8% in 2000, 9.9% in 2023; 2004 set 11.8% and 16.4%). A total-population criterion alone hides this.
  4. *The literature's own yardstick.* Herrington (2021) and Turner use a value-difference range of 20%, 50% for the rate of change and 20% for the normalised RMSD. Both sets are inside 20% for total population in 2020 and 2023 (1974 set -11.3% and -12.7%, 2004 set -5.7% and -7.0%). These are the references' ranges, not targets F3 adopts.
- **Proposal** (framework):
  - **Out-of-sample period:** 2000 to 2023 for estimates; 2024 to 2025 reported separately.
  - **Variables:** total population and the four cohort shares; GDP; primary energy and electricity; CO2 emissions; warming; data-centre electricity against the IEA's 2024 and 2025 values (an estimate and a projection respectively, reported separately).
  - **Metrics:** relative error at stated years; mean absolute relative error over the window; normalised RMSD as in Herrington; each against the naive benchmarks of the same variable.
  - **Rules:** every criterion lists its observed series and its date basis before the run; a variable fails if it does not beat the naive benchmark, whatever its error; failures are reported, not relaxed (plan principle 4).
  - **Thresholds:** **left blank for the editor**, to be set before the series are loaded, as the plan's A5.4 says. The 20% figure is the literature's, not a proposal.
  - **Age structure is a named criterion**, as the D-015 note recommends.
- **Alternatives considered:** only a total-population criterion (simplest; hides the age-structure failure); thresholds set now (would be guesses).
- **Not done:** series for GDP, energy, CO2 and warming are not yet in `research/SOURCES.md` with verified terms; the naive benchmarks for those variables are not computed.
- **Sources:** UN WPP 2024 age-group file (licence terms not stated on the pages read); D-015 and its outcome note; Herrington (2021) as read for D-015.
- **Proposed by:** Claude (Validator role)
- **Decision:** Approved by Stéphane Beau as a framework. The numerical thresholds are to be set by the editor-in-chief before the series are loaded, that is before the M5 hindcast (plan A5.4); they are not set by this approval. Two conditions recorded at approval: (1) the age-structure numbers in this entry (65+ share too high by 27% to 41% for the 1974 set and 66% to 81% for the 2004 set, 2000 to 2023) were already seen when the framework was approved, so any threshold set for age structure is not blind to them and must say so; (2) each criterion must state what a failure triggers (for example: a variable that fails is reported and its sector is flagged, or the parameter-set choice is reopened, or Phase 3 does not start), written when the threshold is set; a criterion without a stated consequence is incomplete.
- **Date:** 2026-10-08

---

## D-025 — Phase 3 entry conditions (plan item N6, optional)

- **Status:** Approved (2026-10-08)
- **Context:** The plan lists this as optional and needed before M6. Drafted now so that the editor can see what "Phase 2 done" would have to show before the work is spent.
- **Evidence for the speed condition:** one S1 run (1970 to 2100, step 0.25 year) takes 0.24 s; a full model's run time is **not measured** (plan tests A3.5 and A6.5 measure it); the FaIR re-run option of D-021 costs 24 s per run in a toy configuration, which would be about 6.7 hours for a 1,000-run Monte Carlo on one core for FaIR alone.
- **Proposal:** Phase 3 starts when all of the following hold:
  1. Every acceptance test of M0 to M6 has been run and its result published, passed or failed; failures each have a written disposition approved by the editor.
  2. The baseline scenario (A6.1) reproduces the full World3 run within ±2% (D-004).
  3. D-005 to D-009 and D-020 to D-024 are decided (or the editor records why one is deferred).
  4. The full run time is measured, and a Monte Carlo budget derived from it is acceptable (D-021 chooses the FaIR coupling with this in view).
  5. Every dataset to be published has its licence read from its own page (WID and ILOSTAT are unknown today).
  6. The Phase 2 review is written.
- **Alternatives:** *strict* (all tests pass before Phase 3; may block on a single hard test); *lenient* (start Phase 3 with documented failures; the risk is calibrating around a known fault). The list above is the middle: failures are allowed if each has a disposition.
- **Sources:** `docs/phase-2-plan.md` (A3.5, A6.1 to A6.7).
- **Proposed by:** Claude (Validator role)
- **Decision:** Approved by Stéphane Beau, as drafted.
- **Date:** 2026-10-08

---

## D-026 — Handling of Epoch AI's GATE playground data (the shipped runs)

- **Status:** Approved (2026-10-09)
- **Context:** D-005's amendment B needs reference series to test S3 against. The only series available are three precomputed runs (default, conservative, aggressive) that Epoch AI's playground page (https://epoch.ai/gate) ships inside its script bundle (https://epoch.ai/generated/gate.js): 80 yearly states each, stored to about 16 significant digits. They are Epoch's output numbers. **What Epoch states about use** (read 2026-10-08 and 2026-10-09): the playground and data pages say its work is "free to use, distribute, and reproduce" with the source and authors credited, "under the Creative Commons Attribution license" (the playground footer links CC BY 4.0). **No licence is stated for the script bundle or for the data inside it**, and the bundle also contains a compiled solver that F3 does not use and does not reuse. Whether the sentence about "Epoch's work" covers numbers embedded in a script file is not settled by the page: that is a reading, not a statement. A request for permission has **not** been sent (an unsent draft is in `docs/drafts/epoch-gate-email.md`); this entry treats permission as **not yet requested**. The same situation was met for Vensim output in D-014, which this entry follows.
- **Evidence:**
  1. *The bundle's identity.* Fetched on 2026-10-08 and again on 2026-10-09: the same 3,167,570 bytes, sha256 `3afe8e4df5260ee062d987ce38a984fc37b488b6dcb5596a317b1fde106c55bf`, byte for byte (the server answers `Cache-Control: public, max-age=0, must-revalidate`, an ETag `735017e30aa343030d708382921dece0`, no stated last-modified date). **A file at a fixed URL that the owner may change at any time**, so a pin by hash is meaningful and will break when Epoch updates the page.
  2. *What the three runs are, structurally* (`audit/t0/gate_playground_probe.py`, `research/gate-equations.md`): they sit as a JSON array in the script (`legacy/one-offs/gate/backend/cache.json` in the bundle's source map comments), keyed by their parameter blocks; they were produced by the page's own solver (C++, double precision, one-year step, tolerance 0.02, at most 40 iterations).
  3. *Size of what would be stored:* three runs of 80 states with 31 fields come to 767,428 bytes (about 750 KB) as stored in the script; the comparison in amendment B needs about 17 of the 31 fields from each run (output, capital, labour, hardware, software, effective compute, automation, and the output shares).
  4. *D-014's pattern, as approved:* the audit may read the reference data from a clone made at run time; nothing from it is copied into the repository or into stored results; stored results hold only variable names and error figures.
- **Proposal** (the D-014 pattern, adapted):
  1. **Nothing from the bundle is committed to the F3 repository**: no series, no part of the script, no copy of the bundle, and none of its code. The bundle's solver is not used.
  2. **Reference values are read at test time from a local copy of the public bundle**, downloaded from `https://epoch.ai/generated/gate.js` into a folder outside the repository (an environment variable names the path; the default is a git-ignored cache folder). **The copy is pinned by sha256**: before any test uses it, the test checks the hash against the one recorded in the repository (above) and **fails with a clear message if it differs**: "The GATE playground bundle has changed since the hash recorded in D-026 (expected …, got …). The reference runs may have changed. Re-read `research/gate-equations.md` sections 3 to 5, compare the three runs' parameter blocks and timing, and record the new hash by a dated note on D-026 before running comparisons." A changed hash is a stop, not an automatic update.
  3. **CI fetches the bundle** in a step of its own (`curl` to the pinned URL), checks the hash, and runs the comparison; if the download fails or the hash differs the comparison step **fails visibly** and is not silently skipped. The existing `python-tests` workflow stays green without it: the GATE comparison tests are marked so that they are skipped, with a stated reason, when no local copy is configured, and run when one is (locally or in the dedicated CI job). **A skip is reported as a skip**, never as a pass.
  4. **Only comparison figures and parameter names are stored** in the repository: per setting and per compared quantity, the largest and mean relative differences, the first year a tolerance is exceeded, and the year groups of amendment B; the names of the parameters and of the stored fields; the sha256 of the bundle; and the parameter values of the three runs **only as far as they are the playground's published parameter table** (names and default values are a description of the model, also in the paper's Appendix D and credited to it). No stored figure allows the series to be reconstructed.
  5. **Permission.** If Epoch AI grants permission in writing (for example in reply to the draft email, which asks for it), the three series **may then be committed as test fixtures with attribution** ("Epoch AI, GATE playground, CC BY 4.0, accessed [date]") and a dated note on this entry records the reply, and the sha256 test becomes a check that the fixtures match the live page. **Silence is not permission**; a reply that declines means the pattern above stays.
  6. **Attribution** in any report or figure that uses the comparison: "Reference values: Epoch AI, GATE playground (https://epoch.ai/gate), CC BY 4.0, read from the public page on [date], sha256 …".
- **Alternatives considered:**
  - **Store the three series now as fixtures** (the simplest and fastest for tests, CI and the reader: no network access, no hash drift). **Not recommended** because: (a) the page says Epoch's work is free to use with credit, which probably allows it, but it does not state a licence for the bundle or the data inside it, and "probably allows it" is the situation D-014 chose not to rely on for Vensim output; (b) CC BY lets others reuse the data with credit, but it is the owner's licence to give, and what the owner has licensed is not clear from what was read; (c) publishing the series in a public repository cannot be undone (they would remain in the history after deletion); (d) the cost of waiting is small: a download and a hash check at test time; (e) a request for permission costs one email and, if granted, removes the objection. If the editor judges that the CC BY sentence plainly covers the data, this alternative is a one-step change later, and the Validator's recommendation does not exclude it.
  - **Store only a hash of each series** (so a fixture could be verified but not read): not usable for a comparison.
  - **Ask permission first and wait:** correct in principle; the plan does not depend on a reply (the comparison can run from the local copy), so waiting would hold up nothing, but it would also hold up nothing if the pattern above is used meanwhile, which is why both are proposed together: use the pattern now, ask when the editor chooses.
  - **Re-run GATE ourselves** (to produce our own reference series): not possible, since no source code is published and the solver in the bundle has no licence stated.
- **What this does not settle:** whether Epoch's CC BY sentence covers the bundle's data (left open; the proposal does not depend on the answer); the terms for the compiled solver in the bundle (not used); the rights to Epoch's two posts (their figures are quoted in D-005's amendment with attribution, short quotes only).
- **Sources:** https://epoch.ai/gate and https://epoch.ai/data (licence sentences, read 2026-10-08/09); the bundle at https://epoch.ai/generated/gate.js (sha256 above); D-014; `research/gate-equations.md`; `audit/t0/gate_playground_probe.py`; `docs/drafts/epoch-gate-email.md`.
- **Proposed by:** Claude (Research and Validator roles)
- **Decision:** Approved by Stéphane Beau, as drafted.
- **Date:** 2026-10-09

## D-027 — S3 production composite: test the paper's footnote-38 task grids as a labelled variant

- **Status:** Approved (2026-10-12)
- **Context:** D-005 amendment B (approved) sets A1.3: S3 within ±2% of the three shipped GATE runs at every annual period end, 2025 to 2100, with GATE's investment path as input. A1.3 was run on 2026-10-12 and **failed on all three runs** (`audit/s3-gate-comparison.md`). **This proposal is post-hoc: it is made after seeing the A1.3 data.** It changes no tolerance and no criterion.
- **Problem (measured):** with Epoch's stored composite task input `T` (`cognitive_ces_term`) supplied to S3 period by period, all three runs pass A1.3 at every year (output 3e-16 to 2e-16, hardware up to 1.8e-4, software up to 1.5e-3, compute stock up to 1.4e-4, automation 3e-15). With S3's own composite they fail from 2026 to 2027 (output 5.7% low in 2027, compounding through the investment feedback). The gap is entirely the task-allocation step (`research/gate-equations.md` section 9.1, identity 8). Its cause is **not established**; candidates are the solver's task discretisation, the stored allocation being a different iterate, and my reading of eqs. 14 to 16 and footnote 39.
- **Proposal:**
  1. Add **variant B** of the production block that uses the discretisation the paper states in footnote 38: **20 grid points for the allocation of digital workers, 100 for human workers and for the CES integral**. Variant B is a separate, named option of `f3/sectors/s3_ai.py`.
  2. **Variant A** (current: 20,000 midpoints) **stays the default and stays recorded as failed.**
  3. A1.3 is re-run for variant B with the same ±2% criterion, same indices, same quantities, and reported as a **second, labelled row**. Nothing is removed from the existing report.
- **Outcomes pre-registered (written before any variant B run):**
  - **(i) B passes:** A1.3 is recorded "**failed under A, passed under B (paper's own grids)**". The default stays A unless the editor decides otherwise.
  - **(ii) B fails:** the failure is recorded with its size and first year, and work on the composite **stops**; no further variant is tried without a new decision.
  - **(iii) Only a 101-point grid passes** (the size of the stored `compute_allocation`, which does not match the paper's footnote): reported as "**matches the playground, not the paper**", and the choice between them is left to the editor. A 101-point variant is tried **only** if B fails, and only as this one named case, not as a search over grid sizes.
- **What this does not do:** no tolerance changes; no criterion is relaxed; no other equation is touched; variants are not tuned to the data (grid sizes are the paper's, or the stored allocation's, nothing else). The in-sample caveat of `research/gate-equations.md` section 9.2, item 3 applies.
- **Alternatives considered:** (a) accept S3 as is, with the composite as a known open difference (A1.3 stays failed; cheapest, leaves S3's output unusable for comparison after 2027); (b) ask Epoch for the allocation convention (draft email updated, unsent; no deadline); (c) both: run B while waiting for a reply.
- **Sources:** `audit/s3-gate-comparison.md`; `research/gate-equations.md` sections 9.1 and 9.3; arXiv:2503.04941 v2 footnotes 38 and 39; D-005 amendment B and its outcome note of 2026-10-12.
- **Proposed by:** Claude (Modeler and Validator roles)
- **Decision:** Approved by Stéphane Beau, as written.
- **Date:** 2026-10-12

- **Outcome note (2026-10-12, appended; no earlier line changed).** Variant B (the paper's footnote-38 grids; implementation in `research/gate-equations.md` section 10) was run on the three shipped runs with the same criterion, indices and quantities. **Outcome (ii): B fails A1.3** on all three runs, with the same first failure years as variant A (output 2027, 2027, 2026; capital 2031, 2032, 2030; hardware 2030, 2033, 2029; software 2030, 2032, 2028; compute stock 2028, 2028, 2027; automation only in the conservative run, 2039). As pre-registered, the single named 101-point case was then tried once and **also fails**, in the same years; so "matches the playground, not the paper" does not apply. No other grid size was tried. A1.3 stays recorded as failed under variants A, B and the 101-point case; the default stays A. Measured: three discretisations give the same output to within a fraction of a percent, so the task grid is not the cause. The cause remains unresolved; composite work stops here until a new decision or a reply from Epoch. Figures: `audit/s3-gate-comparison.md` section 7. Both variants were run only after their implementation was written down; four dated corrections to the written implementation (a wrong formula, a corner case, two `f = 1` handlings) were made before any variant B comparison existed.

- **Pointer note (2026-10-12, appended).** The disposition of this outcome is recorded in D-029: M1 closes with A1.3 failed and accepted as a known open difference; no further composite variants without a new decision.

## D-028 — S3 investment rule: R3 (AI-race budget) calibrated with R1 curves

- **Status:** Approved (2026-10-12)
- **Context:** D-005 replaces GATE's planner with a behavioural investment rule and says the editor chooses the rule after the note `docs/s3-investment-rule.md`; **this is that choice.** S3 (`f3/sectors/s3_ai.py`) takes six shares per year as input; the rule generates them.
- **Decision (content from `docs/s3-investment-rule.md`, sections 2 and 3):**
  1. **R3, the AI-race budget, with R1's fitted curves as its default calibration.** S3's equations are untouched; the rule only generates the six shares (`q_consumption`, `q_compute`, `q_capital`, `q_hardware_rnd`, `q_software_rnd`, and the training share of usable compute). The first five lie in [0, 1] and sum to 1; consumption is the remainder.
  2. **Levers, exposed as named scenario parameters:** the initial overall AI share of output, its decay speed, the split into compute, hardware R&D and software R&D, the capital share rising with the automated fraction `f`, and the training share falling with `f`.
  3. **Default calibration:** fitted once to the three shipped runs, each share as a piecewise-linear function of `f` and of `g(Q)/C_L` (R1 curves). Fitted parameters and comparison figures are stored; no bundle series (D-026).
  4. **A1.4 is report only:** the largest and mean relative difference of the shares, of effective compute and of output against each shipped run, and the first year each exceeds 5% and 10%. R3 is not tuned after seeing these numbers.
- **Caveats (as in the note):** only three solver paths exist and none is a converged optimum (tolerance 0.02, at most 40 iterations), so calibrating to them calibrates to Epoch's playground, not to a truth about investment behaviour; A1.4 differences mix the rule's error with the open production-composite difference (A1.3, D-027) unless the composite is settled, so A1.4 is reported with and without it.
- **Alternatives considered:** R1 alone (no lever), R2 return-driven allocation (marginal-return formulas unverified).
- **Sources:** `docs/s3-investment-rule.md`; D-005; D-027.
- **Proposed by:** Claude (Modeler role)
- **Decision:** Approved by Stéphane Beau: R3 with R1's fitted curves as its default calibration.
- **Date:** 2026-10-12

- **Outcome note (2026-10-12, appended; no earlier line changed).** R3 was built (`f3/sectors/s3_rule_r3.py`; method in `docs/s3-investment-rule-r3.md`, written before the fit) and A1.4 was run, report only (`audit/s3-r3-a1.4.md`). With default levers and the curves fitted once to the three shipped runs: automation fraction within 9.5% at worst once Epoch's stored composite is supplied, but effective compute 43% to 72% off at worst, output 13% to 20% off, hardware up to 35% off; share errors up to 24 percentage points (capital) and 55 (training share). Most of the full-chain output error is the open composite (D-027), the rest is the rule. R3 was not tuned after seeing the numbers; any better fit would be a new labelled post-hoc proposal. A1.5 passes with S3 driven by R3 on the three shipped settings and the two stress settings.

- **Pointer note (2026-10-12, appended).** D-029 records that R3 is a scenario-lever rule, not a GATE replica, and that a better fit is to be considered only after the composite is settled, because A1.4 mixes the rule's error with the composite's.

## D-029 — M1 closed with A1.3 failed; S3's composite is a known open difference

- **Status:** Approved (2026-10-12)
- **Context:** M1 step 2 (S3 built and compared, `audit/s3-gate-comparison.md`) and the D-027 and D-028 follow-ups are done. A1.3 (D-005 amendment B) failed. This entry records the disposition.
- **Facts (measured):**
  1. A1.3 failed on all three shipped GATE runs under variant A (20,000 midpoints), variant B (the paper's footnote-38 grids) and the single named 101-point case (D-027 outcome ii), with the same first failure years (output 2026 to 2027).
  2. With Epoch's stored composite `T` (`cognitive_ces_term`) supplied, every compared quantity passes at every year in all three runs. The gap is entirely the composite (the task-allocation step). **The cause is unresolved; the task grid is ruled out.**
  3. A1.5 and finiteness pass; R3 (D-028) was built and A1.4 reported (`audit/s3-r3-a1.4.md`).
- **Decision:**
  1. **M1 closes with A1.3 recorded as failed**, and the failure is accepted as a known open difference. The criterion, its thresholds and the failed record stay as they are; **nothing is relaxed.**
  2. **S3's absolute output (`gwp`, capital, effective compute) is UNVALIDATED against GATE after about 2027.** No further composite variants are tried without a new decision. The route to resolve it is Epoch's answer to the email in `docs/drafts/epoch-gate-email.md` (unsent; sending it is the editor's call).
  3. **Labelling rule.** Every document, report or dashboard output that uses S3 must say that S3 failed A1.3 and that its absolute output is unvalidated against GATE. **Nothing may say the model "reproduces GATE".** The notice is carried in `f3/sectors/s3_ai.py`, `README.md` and `MODEL_SPEC.md`.
  4. **R3 (D-028) is a scenario-lever rule, not a GATE replica.** The A1.4 numbers (effective compute 43% to 72% off at worst with the stored composite supplied; training share up to 55 percentage points off) are published as they are. A better fit would be a new, labelled post-hoc proposal, to be considered only after the composite is settled, because A1.4 mixes the rule's error with the composite's.
- **Alternatives considered:** keep trying composite variants (open-ended, post-hoc, and the grid is already ruled out); relax A1.3 (not allowed); block M2 until Epoch replies (no deadline for a reply).
- **Sources:** `audit/s3-gate-comparison.md`; `audit/s3-r3-a1.4.md`; D-005 (outcome note), D-027, D-028.
- **Proposed by:** Claude (Validator role)
- **Decision:** Approved by Stéphane Beau in session, as drafted.
- **Date:** 2026-10-12

## D-030 — M2 step 1 closes with A2.1 failed; climate output labelled

- **Status:** Approved (2026-10-12)
- **Context:** M2 step 1 (FaIR alone and `s6_climate`, `docs/m2-step1-fair.md`) ran A2.1 as fixed before any comparison. The report is `audit/m2-fair-report.md`.
- **Facts (measured):**
  1. **A2.1 failed.** FaIR's ensemble-mean warming for 2015 to 2024 is 1.196 K above 1850-1900; the mean HadCRUT5 95% interval is [1.234, 1.305] K. FaIR is **0.037 K below the lower edge** and **0.073 K below the best estimate** (1.269 K).
  2. 2023 and 2024 are the only out-of-sample years (the ensemble was constrained to data through 2022) and run **0.16 to 0.20 K low**; the cause is untested.
  3. Neither the CO2 source (GCB 2025 against the file's history) nor the non-CO2 scenario moves the result by more than 0.001 K.
  4. The sector tests (equality with a single FaIR run to 1e-9 K, time convention, properties, sign, data integrity) pass.
- **Proposal:**
  1. **Leave A2.1 recorded as failed.** The criterion and its record stay as they are; nothing is relaxed.
  2. **The distributional criterion (post-hoc option 2 of the report) is NOT adopted**: it is a looser test chosen after the result.
  3. `s6_climate` is carried forward with its validation status stated (in its docstring, as `S6Climate.validation_status`, in `README.md` and `MODEL_SPEC.md`).
  4. **Labelling rule:** every output that uses FaIR warming says that scenario warming starts about 0.04 to 0.07 K below observed for the current decade (HadCRUT5), and that non-CO2 emissions are prescribed, not modelled (D-021).
  5. Whether the offset matters for the coupled slice is decided at the first coupled test, not now.
- **Alternatives considered:** adopt the distributional criterion (rejected above); a second reading against the calibration's four-dataset mean (needs three more datasets with terms checked, asks a different question); re-base FaIR to HadCRUT5 by an offset (would hide the finding).
- **Sources:** `audit/m2-fair-report.md`; `docs/m2-step1-fair.md`; D-021; D-029 for the parallel S3 case.
- **Proposed by:** Claude (Validator role)
- **Decision:** Approved by Stéphane Beau, as drafted.
- **Date:** 2026-10-12

## D-031 — World3 sector group advanced with internal sub-steps of 0.0625 year inside the 0.25-year loop

- **Status:** Approved (2026-10-20)
- **Context:** M3 (Track B) ported the four remaining World3 sectors. A3.1 was met (all 14 states within 0.124%). **A3.2 failed at the loop step 0.25 year**, both parameter sets: worst state `lufd` 6.90% (1974 set) and 7.96% (2004 set), 15 and 16 of 29 states above 2%, first failure in 2023. The reference's own solver error is not the cause (default against tight at most 1.61% and 0.26%). A post-hoc scan by the track found the cause to be the first-order error of start-of-step coupling (D-022): the worst state is **6.9% / 3.2% / 1.6%** (1974 set) and **8.0% / 3.9% / 1.9%** (2004 set) at loop steps **0.25 / 0.125 / 0.0625 year**, and at 0.0625 no state exceeds 2%. The editor decided on 2026-10-20 how to meet A3.2 (below). D-003 and D-022 are **not edited**.
- **Decision:** Approved by the editor, 2026-10-20: **the World3 sector group (S1 population, agriculture, capital, resources, pollution) is advanced with internal sub-steps of 0.0625 year while the model loop stays at 0.25 year** (D-003 and D-022 unchanged for coupling with all other sectors).
- **The rule, written before any re-run:**
  1. The five World3 sectors are wrapped in one `Sector` of the coupling loop (`f3/sectors/world3_group.py`). Inside each 0.25-year loop step it takes **four sub-steps of 0.0625 year** with the **same explicit start-of-sub-step coupling** among the five sectors (each reads the others' values at the start of the sub-step, held across it). Every sector's own integration (RK4) and equations are unchanged.
  2. What the group publishes to the loop, at each 0.25-year boundary, are the values at that boundary; any other sector sees them at the loop's start-of-step convention (D-022). The group has no inputs from other sectors in M3; coupling of the World3 group to other sectors is later work and uses the loop's 0.25-year convention.
  3. The Sector interface is not changed. (If it could not be done without changing it, the fallback was a global step of 0.0625 for World3-only runs; **this was not needed**: the group is a Sector.)
  4. **Pre-registered criteria, unchanged:** A3.2 (all 29 states within 2% of the default WorldDynamics.jl reference at every 0.5-year point of 1900-2100, both sets), A3.3 (twelve main stocks within 2% of unmodified PyWorld3 at dt = 0.05 with the pollution start-up matched, labelled diagnostic; the 2004 set diagnostic), A3.4(b) (S1's 15 states inside the full run within 0.25% of S1 alone with recorded inputs, both sets). **Written predictions before the run:** A3.2 is expected to pass (the track's scan: worst 1.6% and 1.9% at 0.0625); A3.4(b) is expected to be **borderline**: D-022's measurement of S1 with recorded partners gives about 0.25% (1974) and 0.23% (2004) at 0.0625, against a 0.25% criterion; A3.3 for the 1974 set is expected to improve but not certainly to pass (`ic` 3.39% and `sc` 2.42% at 0.25 are the largest).
  5. **Any criterion that still fails is recorded with its size and first year; nothing is adjusted.**
- **Cost, measured by the track:** one full World3 run takes about 0.6 s at step 0.25 and 2.3 s at 0.0625 (median), so the sub-stepped group costs roughly 2.3 s per run.
- **Reversal cost:** low: removing the group wrapper restores the 0.25-year behaviour and A3.2 fails again as recorded (strict xfails remain in the history).
- **Alternatives considered (editor chose the one above):** predictor-corrector coupling (more code, changes the interface, not needed to meet 2%); a labelled post-hoc restatement of the criterion (would relax a pre-registered criterion).
- **Sources:** `audit/m3-world3-port-report.md`, `docs/tracks/track-b.md`, D-003, D-004, D-022.
- **Proposed by:** Claude (Modeler role), on the track's recommendation.
- **Decision:** Approved by the editor, 2026-10-20.
- **Date:** 2026-10-20

- **Outcome note (2026-10-20, appended; no earlier line changed).** Re-run with the criteria unchanged (`audit/m3-world3-port-report.md` section 7). **A3.2 met**, both sets: worst state `fcfpc1` 1.621% (1974) and `lufd` 1.906% (2004), 0 of 29 above 2% (predicted). **A3.3 (1974, pollution start-up matched, labelled diagnostic) met:** worst `ppol` 0.91%. **A3.4(b) failed:** S1 inside the full run against S1 alone with recorded inputs, worst 1.019% (1974, `aiopc`) and 0.931% (2004, `fcfpc1`) against 0.25%; the prediction written here that it would be "borderline" **was wrong** (measured 4 to 5 times the criterion). The track's reading, inferred and not tested, is that this gap is S1's response to small differences in the other four sectors' outputs and not an error of S1's equations. The criterion is not relaxed. The Sector interface was not changed (the group is a Sector), so the global-step fallback was not used. One full run takes 2.3 s (2004 set) to 3.2 s (1974 set).

---

# Provisional (delegated) decisions

Entered 2026-10-21 under the standing delegation of 2026-10-12 (`CLAUDE.md`). **Provisional is not Approved.** D-032 to D-036 describe Track A's work, which is on branch `track-a` and **not merged into main** (Demo 0 is held); they stay Provisional and unused until the editor decides on that track. The editor reviews them in one batch at each milestone and may reverse any; the reversal cost is stated in each.

## D-032 — Data-centre boundary for the F3 data-centre module (IEA Energy and AI, descriptive)

- **Source:** Track A, `docs/tracks/track-a.md` on branch `track-a` (not merged into main; Demo 0 held), block P-A1. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** "Data centre" means a facility housing servers, storage systems, networking equipment and associated components (cooling, power distribution, UPS, lighting), as the IEA's Energy and AI describes it. The module's `E_dc` is compared with the IEA's totals on that descriptive boundary only. Whether crypto-mining load is excluded from the IEA totals is [unverified] (no IEA text read states it; a secondary source says it is). 485 TWh (2025) is a calibration point, 415 TWh (2024) a reference value, 950 TWh (2030) a report-only comparison; none is called validation.
- **Recommendation followed:** the editor's option (a), 2026-10-17, after the track reported that the formal boundary could not be verified.
- **Alternatives considered:** (b) wait for the IEA methodology or the full Energy and AI PDF before any module code.
- **Cost of reversing it:** low. The boundary only fixes the calibration constant `eta_0` and the labels; a different boundary re-calibrates one constant, re-runs the grid (about 30 to 34 minutes per loop run with 841 members) and changes label text.
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Provisional (delegated); not approved. The editor reviews all Provisional decisions in one batch at each milestone and may reverse any.

## D-033 — Data-centre module form, calibration, supply and coupling (Track A)

- **Source:** Track A, `docs/tracks/track-a.md` on branch `track-a` (not merged into main; Demo 0 held), block P-A2. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** `E_dc = compute_stock / eta_hw * PUE` (spec S4), with `compute_stock` = S3's raw compute stock Q, `eta_hw = eta_0 * H(t)/H(2025)` (S3's hardware price-performance drives energy efficiency; an assumption), PUE = 1.4 (between the IEA's ranges 1.1-1.2 and 1.5-1.7, Key Questions), `eta_0` calibrated once so E_dc(2025) = 485 TWh (calibration point, not validation). Supply = recorded Earth4All.jl electricity production `ene.EP` (pinned 16f37d0, scenario TLTL, exported by `audit/t0/earth4all_supply_export.jl` to `f3/data/earth4all_electricity_supply.csv`; no Vensim file). Data centres may use 5% of that supply (`dc_share_cap`, an assumption; 485 TWh is about 1.5% of the series' 2025 value of about 32,600 TWh). `supply_ratio = min(1, available/demand)` multiplies S3's usable compute (not the stocks), lagging by one year under explicit coupling. Emissions: prescribed (D-021); no electricity-to-emissions coupling is implemented (the plan names none beyond D-021).
- **Recommendation followed:** the plan's M2 deliverable form; simplest reading of spec S4.
- **Alternatives considered:** a larger or smaller share cap; GL scenario supply; scaling investment instead of usable compute; coupling emissions to electricity at a fixed carbon intensity.
- **Cost of reversing it:** low to medium; constants and one wiring line, then re-run the grid (about 30 to 34 minutes for the 841-member climate recording only if the climate changes; the nine slice runs take seconds because climate is recorded once and replayed exactly).
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Provisional (delegated); not approved. The editor reviews all Provisional decisions in one batch at each milestone and may reverse any.
- **Review note (2026-10-21, appended; status stays Provisional).** The 5% data-centre supply cap and the tie of energy efficiency to S3's hardware curve are **assumptions and must be stated on the page** (and wherever the module's output is shown).

## D-034 — Damage function action on S3 (Track A)

- **Source:** Track A, `docs/tracks/track-a.md` on branch `track-a` (not merged into main; Demo 0 held), block P-A3. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** D-007 options as level-of-output multipliers on S3 gross output: `gwp = gwp_gross * (1 - c T^2)`, c = 0.236% (low), 0.344% (central, derived from printed anchors), 1.00375% (high, (0.595 x 1.25 + 0.260)%); T = FaIR ensemble-mean warming above 1850-1900 on 1 January, no offset; damage cap 0.99; default central. The damaged output is what feeds investment (damages lower investment in dollars). Growth-effect case not represented; "high" is not the upper end of the literature.
- **Recommendation followed:** D-007 as approved and its appended text.
- **Alternatives considered:** damage applied to output after investment is computed; a damage on TFP or capital; an offset for FaIR's low start (D-030 leaves it open).
- **Cost of reversing it:** low (one function and one line in S3), plus a re-run of the grid.
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Provisional (delegated); not approved. The editor reviews all Provisional decisions in one batch at each milestone and may reverse any.
- **Review note (2026-10-21, appended; status stays Provisional).** The central and high damage coefficients are **derived** from published anchors (central 0.344% from the printed 3.1% at 3 C; high from the Howard and Sterner coefficients), not read as printed coefficients; **mark them "derived"** wherever they are shown.

## D-035 — Reuse of one exact climate recording (Track A)

- **Source:** Track A, `docs/tracks/track-a.md` on branch `track-a` (not merged into main; Demo 0 held), block P-A4. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** Because emissions are prescribed, S6 has no inputs in this slice and its output is identical for every lever. The Demo 0 grid records `S6Climate` once with all 841 members (D-021 option a: exact re-run each year) and replays it in each run; S3 reads warming only at the start of each year, where the replayed value equals the sector's published value. Tests and development use the first 20 members and say so. Not valid once any sector feeds S6.
- **Recommendation followed:** the editor's instruction to reuse climate where exact.
- **Alternatives considered:** a live S6 in each of the 11 runs (about 6 hours with 841 members).
- **Cost of reversing it:** none for results; the replay stops being exact the moment an emissions coupling is added.
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Provisional (delegated); not approved. The editor reviews all Provisional decisions in one batch at each milestone and may reverse any.
- **Review note (2026-10-21, appended; status stays Provisional).** **Add a test that fails if any sector feeds S6**: the replay of one recorded climate is exact only while S6 has no inputs.

## D-036 — Demo 0 grid and levers (Track A)

- **Source:** Track A, `docs/tracks/track-a.md` on branch `track-a` (not merged into main; Demo 0 held), block P-A5. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** AI settings: low = initial_ai_share 0.5 x fitted, central = R3 defaults, race = 1.5 x fitted with decay_speed 0.5; damage low/central/high; plus supply 0.5 x and unlimited for central/central. 11 runs, 2025-2100. Chosen before any result was seen.
- **Recommendation followed:** the briefing (small documented set).
- **Alternatives considered:** varying split, capital_scale, training_scale as well.
- **Cost of reversing it:** low; edit `SETTINGS` in `dashboard/demo0/generate.py` and regenerate.
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Provisional (delegated); not approved. The editor reviews all Provisional decisions in one batch at each milestone and may reverse any.

## D-037 — Module names and structure of the four World3 sectors

- **Source:** Track B, `docs/tracks/track-b.md`, P1. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Approved (2026-10-21)
- **Date:** 2026-10-21
- **Recommendation followed:** `f3/sectors/w3_agriculture.py`, `w3_capital.py`, `w3_resources.py`, `w3_pollution.py`, common code in `w3_common.py`, wiring in `world3.py`; each sector is a `Sector` with RK4 inside `advance`, algebraic outputs published at the end of `advance`.
- **Alternatives considered:** `s2_`/`s5_` names from the spec's sector map (rejected: World3 capital and resources are not the spec's S2/S5, which M4 and M5 rebuild); one monolithic World3 module (rejected: A3.1 needs per-sector tests).
- **Cost of reversing it:** renaming files and imports; no equation changes.
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Approved by the editor ("approve all", 2026-10-21).

## D-038 — The A3.2 failure at loop step 0.25 is recorded, not repaired (superseded in effect by D-031)

- **Source:** Track B, `docs/tracks/track-b.md`, P2. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Superseded in effect by D-031
- **Date:** 2026-10-20
- **Note (orchestrator, 2026-10-21):** at the time of the first result nothing was applied; the editor then approved D-031 (World3 group with 0.0625-year sub-steps), under which A3.2 is met. This block records the first disposition and is superseded in effect by D-031; it is kept for the record.
- **Recommendation followed:** no change to the loop step, coupling scheme or criterion; strict xfails documented A3.2 (both sets), A3.3 (1974) and A3.4(b) (both sets).
- **Alternatives considered:** (a) loop step 0.0625 (A3.2 would pass both sets; 2.3 s per run); (b) predictor-corrector coupling (D-022 alternative, needs state save and restore); (c) sub-stepping inside the World3 sectors. Each changes D-003 or D-022 and needs the editor.
- **Cost of reversing it:** none (nothing was applied).
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Provisional (delegated); not approved. The editor reviews all Provisional decisions in one batch at each milestone and may reverse any.

## D-039 — Initial outputs of the coupled World3 sectors

- **Source:** Track B, `docs/tracks/track-b.md`, P3. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Approved (2026-10-21)
- **Date:** 2026-10-21
- **Recommendation followed:** the start-time inputs of the four sectors are computed from their initial states by iterating the wiring, which is acyclic at t0 (`f3/sectors/world3.py`), not seeded from recorded data. Initial state is the reference's own (D-019 Option C; pollution delay stages start at `pptd*ppgr0/3` from the sector's own 1900 tables, as the reference does).
- **Alternatives considered:** seeding from recorded values (rejected: the full run would depend on fixtures).
- **Cost of reversing it:** small, one function.
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Approved by the editor ("approve all", 2026-10-21).

## D-040 — The World3 group is one Sector wrapping the five sectors (the form D-031 takes)

- **Source:** Track B, `docs/tracks/track-b.md`, P4. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Approved (2026-10-21)
- **Date:** 2026-10-21
- **Recommendation followed:** `f3/sectors/world3_group.py`: one `Sector` wraps S1 and the four World3 sectors and advances them with 0.0625-year sub-steps inside each 0.25-year loop step (the rule itself is D-031, approved by the editor); the Sector interface is unchanged.
- **Alternatives considered:** a global 0.0625 step for World3-only runs (rejected: not needed).
- **Cost of reversing it:** low; `run_world3(..., substep=None)` runs the sectors directly at the loop step (A3.2 then fails as recorded).
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Approved by the editor ("approve all", 2026-10-21).

## D-041 — A3.4(b) is recorded as failed and not repaired

- **Source:** Track B, `docs/tracks/track-b.md`, P5. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Approved (2026-10-21)
- **Date:** 2026-10-21
- **Recommendation followed:** S1 inside the full run differs from S1 alone with recorded inputs by up to 1.019% (1974, `aiopc`) and 0.931% (2004, `fcfpc1`) against 0.25%; the criterion is not changed and the test stays a strict xfail. The track's reading (S1 responding to small differences in the other four sectors) is inferred, not tested.
- **Alternatives considered:** restating the criterion to a looser number (a labelled post-hoc proposal; not applied).
- **Cost of reversing it:** none (nothing applied).
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Approved by the editor ("approve all", 2026-10-21).

## D-042 — N4: inputs to the reused Earth4All sectors in M4 (D-023 option C)

- **Source:** Track C, `docs/tracks/track-c.md`, N4 (plan decision N4, delegated). Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Approved for M4 (2026-10-21)
- **Date:** 2026-10-21
- **Recommendation followed:** D-023 option C. Sector tests and the A4.5 group use the recorded Earth4All.jl series of the eight signals (`POP`, `GDPP`, `EGDPP`, `A20PA`, `OW`, `CAC`, `COFO`, `IPP`) through `ReplaySector`; no adapter was built (A4.5 needs none).
- **Alternatives considered:** (A) recorded series only (no F3 population or climate in the economy); (B) adapters from the start (rejected: the working-age mapping and warming baseline of D-023 are open, and sector tests need exact inputs).
- **Cost of reversing it:** low. Sectors read inputs by name through the loop context; switching means wiring other sectors' outputs to the same names and writing unit adapters (persons to Mp, S1 age bands to `A20PA`, FaIR temperature to `OW`); no sector code changes.
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Approved by the editor ("approve all", 2026-10-21).
- **Note (2026-10-21, appended).** Revisit at M6 (adapters for population and climate).

## D-043 — Euler with a 1/64-year internal sub-step for the reused Earth4All sectors

- **Source:** Track C, `docs/tracks/track-c.md` and `docs/tracks/track-c-plan.md`. Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Approved (2026-10-21)
- **Date:** 2026-10-21
- **Rule (written in `docs/tracks/track-c-plan.md` before any run):** if a sector alone exceeds 2% at the loop step, use the largest rung of {RK4 0.125, 0.0625, 0.03125; Euler 1/64} at which every state and headline variable is within 2% in both scenarios.
- **Measured:** RK4 exceeds 2% in seven of eight sectors (report section 1); no RK4 rung meets 2%; Euler 1/64 does (0.0000% with recorded inputs). D-003 and D-022 are not edited; loop step and interface unchanged. **Meaning:** the reused sectors reproduce the reference's own Euler discretisation (1/64-year sub-step), not a better integration of the same equations.
- **Why:** the reference is Euler at 1/64 year and its own Euler error exceeds 2% near zero crossings and kinks, so only its own scheme reproduces it.
- **Alternatives considered:** a labelled post-hoc restatement of A4.1 (relaxes a criterion); a global 1/64 loop step (changes D-003).
- **Cost of reversing it:** low (class default `SUBSTEP`). Cost of keeping: 7681 sub-steps per run in pure Python.
- **Not decided here:** A4.5 failed under this rule (group coupling lag); the editor accepted that failure as recorded on 2026-10-21 (no criterion changed).
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Approved by the editor ("approve all", 2026-10-21).

## D-044 — Correction of the M4 recorded-input fixture grid (1/16 to 1/64 year), made after a result was seen

- **Source:** Track C, `docs/tracks/track-c.md`, log (correction of the first reading). Moved into this register by the orchestrator on 2026-10-21 at the editor's instruction; text as drafted by the track (the track did not edit this file).
- **Status:** Approved (2026-10-21)
- **Date:** 2026-10-21
- **What happened (the track's own account):** the first S0 run (sector alone, recorded inputs) used inputs exported on a 1/16-year grid and linearly interpolated, as the S1 and World3 fixtures are. It failed in output (TLTL), finance (both scenarios) and labour market (both) with errors that vanish when the inputs are the reference's own: `OGR` 2.56%, `UR`/`UNEM` 11.5%, `CFWB` 0.34% and others. Measured cause: the Euler reference reads its inputs at every 1/64-year step; a 1/16 grid carries them only every fourth step, so quantities that are differences of near-equal numbers (`OGR`, `ISR`, `UNEM`) move by the interpolation error.
- **Recommendation followed:** the export (`audit/t0/earth4all_m4_export.jl`) was amended after the result was seen so that signals are on the full 1/64-year grid at 12 significant digits. **This is an amendment of a fixture after seeing a result, labelled as such.** The 2% tolerance, the criterion sets and the rule were not changed. With 1/64 signals the sector-alone run is 0.0000% for every state and headline variable of all eight sectors, both scenarios (the port reproduces the package's equations to rounding when fed its inputs).
- **Alternatives considered:** keeping the 1/16 grid and reporting the failures (would have measured the interpolation, not the equations); relaxing the S0 tolerance (not allowed).
- **Cost of reversing it:** none for the equations; re-exporting at a coarser grid reproduces the failures. Bears on how the earlier S1 and World3 fixtures (1/16 grid) should be read: not examined here.
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Approved by the editor ("approve all", 2026-10-21).
- **Follow-up note (2026-10-21, appended).** The same correction was applied to the S1 and World3 recorded-input fixtures (D-045); it changed nothing, because those tests query their inputs only at points that were already on the old grid.

## D-045 — Fixture correction: S1 and World3 recorded inputs re-exported on the 1/64-year grid

- **Status:** Provisional (delegated)
- **Date:** 2026-10-21
- **Decision:** At the editor's instruction (2026-10-21, "fixture correction, no criterion change"), `tests/fixtures/s1_inputs_world3_{1974,2004}.csv` and `w3_signals_world3_{1974,2004}.csv` were re-exported from the same pinned solve (`audit/env`, D-017, default options) with `saveat = 1/64` and 12 significant digits (`audit/t0/world3_regrid_export.jl`); the reference files were not touched. Reading, outcome categories and prediction were written first (`docs/m3-fixture-regrid-reading.md`, commit `50b5bda`).
- **Outcome:** **no change.** A3.1, A3.2, A3.3, A3.4(a), A3.4(b) and the S1 step-1.4 comparisons give textually identical results before and after (96 passed, 17 strict xfail); A3.4(b) still fails (1.019% and 0.931% against 0.25%). **No criterion, tolerance or rule was changed.**
- **Why nothing changed (and a correction of the proposal's premise):** sector-alone runs at the 0.25-year loop step query inputs at multiples of 0.125 year, which are grid points of the old 1/16-year files, so no interpolation took place. Unlike the Earth4All case (D-044), where the reference reads its inputs every 1/64 year, this correction could not have had an effect.
- **Alternatives considered:** leaving the fixtures as they were (they were already exact at every point the tests use).
- **Cost of reversing it:** none for results; the four files grew from about 1.4 MB to about 8.5 MB, and reverting the commit restores the old files.
- **Proposed by:** Claude (delegated, standing delegation of 2026-10-12)
- **Decision:** Provisional (delegated); not approved. The editor reviews all Provisional decisions in one batch at each milestone and may reverse any.
- **Revert note (2026-10-21, appended; status unchanged).** At the editor's instruction the four re-exported fixture files were reverted to their previous versions (a new commit, history not rewritten) because the re-export changed no result and added about 7 MB. This entry, `docs/m3-fixture-regrid-reading.md` and the export script `audit/t0/world3_regrid_export.jl` are kept as the record of the negative result.

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
