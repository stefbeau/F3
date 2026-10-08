# F3 — Phase 2 Plan: Couple (PROPOSAL)

**Status: Approved by the editor-in-chief on 2026-10-08, order B.** · **Depends on:** Phase 1 (done, `docs/phase-1-review.md`) · **Governing decisions so far:** D-001, D-003, D-004, D-010 to D-012, D-014 to D-019 · **Decisions this plan needs:** D-005 to D-009 and six new ones (section 8). No approved decision is changed by this document.

---

## 1. Goal

Couple the seven sectors of `MODEL_SPEC.md` into its feedback loops (R1–R3, B1–B6, spec section 5) so that F3 can run conditional scenarios from 1970 to 2100 (spec sections 5 and 6). Phase 1 left one ported sector (S1), a verdict on Earth4All (D-016), two pinned environments and a method that worked: feed the reference's recorded inputs by name, compare within ±2% (D-004), report the reference's own error beside every figure. Phase 2 adds the rest of World3, the reused Earth4All sectors, and the parts no reference model has (section 3). Calibration and Monte Carlo are Phase 3; the dashboard is Phase 4.

**Phase 2 is done when** every milestone's acceptance tests (section 6) have been run and their results published, passed or failed; all loops of spec section 5 are active; and the four reference scenarios of spec section 6 run from 1970 to 2100.

## 2. Where we start

| Component | State at the start of Phase 2 |
|---|---|
| S1 population | Ported, both World3 parameter sets, 22 tests pass locally and in CI (`f3/sectors/s1_population.py`) |
| World3 agriculture, capital, non-renewable resources, pollution | Not ported. 147 equations in WorldDynamics.jl (occurrences of ` ~ ` in the four subsystem files: 55, 42, 15, 35), against 54 for S1 (its death-rate, birth-rate and population blocks), so about 2.7 times S1 |
| Earth4All sectors to reuse (output, inventory, finance, demand, public, energy, labour market; "other" not assessed) | Not ported. 379 equations and delay helpers by a grep count (output 64, demand 89, inventory 24, finance 20, public 39, energy 90, labour market 53), 397 with "other" (18), so about 7 times S1. The count is rough: it counts ` ~ ` plus calls of the smoothing and delay helpers. Earth4All.jl solves with Euler at 1/64 year, not at F3's 0.25 year (D-003) |
| S3 AI sector, S6 climate, S7 social module, minerals and water modules | Do not exist |
| FaIR | Not installed in the project environment, never run |
| Speed | One S1 run (1970–2100, step 0.25 year, derived variables included) takes 0.24 s, measured. The cost of a full model is not measured |
| Sources | `research/SOURCES.md`: several primary documents could not be read (LBNL, TSMC, WID terms, ILOSTAT licence) |

## 3. What F3 must add that no reference model has

| Component | Nearest reference | What it lacks | Milestone |
|---|---|---|---|
| AI development and automation (S3) | GATE (Epoch AI), paper only: no source code found | It is an economic growth model with no energy, mineral or water limits, and its investment comes from an optimisation that does not fit a system dynamics model (D-005) | M1 |
| Data-centre electricity (S4) | IEA reports, Epoch data hub (data, not a model) | Earth4All's energy sector has no data-centre demand and no material limits (D-010) | M2, M4 |
| Data-centre and chip-fabrication water (S5) | none | No model; the source documents for the figures were not readable (SOURCES.md) | M5 |
| Seven warming-effect channels fed by FaIR | Earth4All.jl: seven equations that are 1 before 2022 and an effect of observed warming (six) or of CO2 concentration (one, `CO2ELY`) afterwards (`audit/earth4all-time-driven-equations.csv`) | Three are in sectors F3 reuses (output: cost and loss of capital; public: productivity), so they only need a warming input from FaIR. Four are in sectors F3 replaces, one each in climate (`OWLCO2`), population (`WELE`, life expectancy) and two in foodland (`CO2ELY` needs CO2 concentration, `WELY` warming): **whether F3 needs its own version of each depends on what replaces the sector**, and was not traced (the CSV marks their consumers "not traced"). `OWLCO2` is probably unnecessary because FaIR has its own carbon cycle (inference, not checked) | M2, M4, M5 |
| Non-CO2 greenhouse gases and land-use CO2 for FaIR | Earth4All's climate and foodland sectors computed them; F3 replaces both | **No F3 sector produces them.** World3 agriculture has no methane or nitrous oxide | M2 (decision N2) |
| Labour share and inequality (S7) | Earth4All has an inequality index inside the demand sector; Turchin-style theory | No explicit stocks; the long labour-share data are not found (ILOSTAT's SDG series starts in 2004) | M5 |
| Social tension (S7) | Earth4All's index | No open historical proxy found from 1970 (D-008 evidence note) | M5 |
| Minerals (S5) | World3 aggregate non-renewable resources | No critical-minerals module (D-006) | M5 |

## 4. Principles for this phase

The Phase 1 rules stay: acceptance tests are written before the work and are not relaxed after seeing results (a failure is recorded, and a revised test is a new, labelled proposal); everything is pinned; results state what was measured, inferred or unverified. Added for Phase 2:

1. **Reference by name, recorded inputs.** A ported sector is tested alone with the reference's recorded inputs, matched by variable name, started from the reference's own initial state; the reference's own error (default against tight tolerance) is reported next to each figure.
2. **Never test against a projection.** Observed estimates can be pass/fail targets; projections (the IEA's 2030 figure, UN values after 2023) are compared and reported only.
3. **Extensions are switchable.** Anything added to a ported sector (the warming channels) can be switched off, and with it off the sector must still pass its D-004 tests. Claude does not change an equation of a ported sector without asking (`CLAUDE.md`).
4. **New modules have no reference.** Their acceptance tests are documentation of equations and sources before coding, extreme-condition tests (spec section 7.5), balance checks, and backtest metrics fixed beforehand (decision N5); never a tolerance invented after the fact.
5. **Checkpoints.** ✋ marks a point where the editor-in-chief reviews before the next milestone starts.

---

## 5. Order: the recommendation and one alternative

Both orders do the same work; they differ in what is learned first. Section 6 lists the milestones in the recommended order (B). Section 7 gives the alternative (A).

**B (recommended): a thin slice first.** After M0, build the AI sector (M1), then couple it with a minimal data-centre electricity module and FaIR (M2): a three-sector slice that closes loops R1, B1 and B2 and can be shown (section 10). Then complete World3 (M3), port the Earth4All sectors (M4), add the new modules (M5), integrate (M6).

**A (alternative): complete World3 first.** After M0, port the four remaining World3 sectors and reproduce the full World3 run, then port the Earth4All sectors, then add FaIR and the warming channels, then S3, then S7 and the new modules, then integrate.

| | B: thin slice first | A: World3 first |
|---|---|---|
| What is learned first | Whether GATE can be re-implemented without its code, whether FaIR can be coupled inside a loop, whether the data-centre data exist: the three least-known things | Whether the whole World3 reproduces within ±2%, which is well specified and likely to work |
| Reference tests early | Thin: S3 against GATE only if the sandbox can export results (not checked); FaIR against observed warming | Strong: every step has a reference (WorldDynamics.jl, Earth4All.jl) |
| First public demo (section 10) | After M2: **9–15 sessions** | After the AI slice at the end of A's order: **21–34 sessions** |
| Main risk | Rework: the slice's economy is GATE's own growth module, to be replaced or extended by Earth4All's sectors in M4; the slice's interfaces may not fit the full model | The core novelty and the biggest unknown (S3, decision D-005) is reached last, so a failure there is found after most of the effort is spent |
| Cost if the biggest unknown fails | Found early, after about 4–6 sessions | Found late |

**Recommendation: B.** Three reasons: the three least-known items (D-005, FaIR coupling, data-centre data) can each change the plan, so learning them first is cheaper; World3 completion is mechanical and can wait without losing information; and B reaches an honest demo sooner, when external review is cheapest. The rework risk is reduced by M0, which fixes the sector interface before any sector is built on it, and by keeping the slice's economy to GATE's own growth module (already part of D-005) rather than a throw-away placeholder. **What would change my recommendation:** if M1's first precondition fails (GATE's results cannot be obtained in any form, see A1.1), the slice loses its test and A becomes the safer order. This is a recommendation, not a decision.

---

## 6. Milestones (recommended order B)

Sizes are in working sessions (section 11 says what a session is and what is uncertain). Acceptance tests are stated here, before the work. Numbers marked *proposed* are the Validator's proposals for the editor to confirm; where a number would be invented without data, the test says what must be fixed first.

### M0 — Carry-over, interfaces and first decisions (1–2 sessions)

**Goal.** Remove what would otherwise be found during coupling: the sector interface, the time convention, the open decisions that block M1 and M2, and the housekeeping.

**Deliverables.**
1. A sector interface and coupling loop: sectors declare inputs and outputs by name; a fixed step of 0.25 year (D-003); every exchanged series can be recorded to CSV (the test method of S1, built in). S1 runs inside it.
2. The time convention (review item 16): is `t = 1970` the start of the year or its middle? World3 is a continuous-time model, so this may not be answerable from its equations; if so, say so and propose a convention (state values at 1 January, flows per year) with its effect on comparisons (up to about one point of population against UN data).
3. Drafts, status Proposed, of decisions N1–N6 (section 8), each with options and evidence.
4. A research note listing published sources for the low, central and high damage functions of D-007 (none is in the register yet).
5. Housekeeping: the `CLAUDE.md` repository map, which said `f3/` and `tests/` were planned and omitted `licenses/`, `pyproject.toml`, `uv.lock` and the Phase 1 review, was corrected while drafting this plan (A0.5 re-checks it); `docs/HANDOVER.md` gets Phase 2 prompts; Prompt 5 of the handover (automation of audit reports and CI) can run in parallel.

**Acceptance tests (before the work).**
- A0.1 S1 inside the framework gives results identical to stand-alone S1 (relative difference at most 1e-9 on all 15 states, both parameter sets) and its 22 tests still pass.
- A0.2 The equations section of `s1_population.py` is unchanged (the diff shows only interface code).
- A0.3 The time convention is written in `MODEL_SPEC.md` with its evidence, or the file says it cannot be determined and a Proposed decision carries the choice.
- A0.4 N1–N6 exist as Proposed entries; none is marked Approved by Claude.
- A0.5 The `CLAUDE.md` repository map matches the repository (checked by listing).

**Data and sources.** None new. **Decisions.** N3 before M1 builds on the interface. **Risks.** Over-designing the interface: keep it to what S1, S3 and FaIR need and extend it later. **✋ Checkpoint:** the editor reviews the interface and drafts N1–N6.

### M1 — S3 AI sector, GATE-like, standalone (4–6 sessions)

**Goal.** Re-implement GATE's three modules (AI development, automation, growth) in simplified form with a behavioural investment rule, as D-005 proposes, and show where it reproduces GATE.

**Deliverables.** `f3/sectors/s3_ai.py`; a note in `research/` listing GATE's equations and default parameters with their locations in the paper; a comparison report; an amendment to D-005 fixing the tolerances below (as drafted it says to check against presets, with no tolerance).

**Acceptance tests (before the work).**
- A1.1 *Precondition.* Before any code, the equations and default parameters are extracted from the paper (arXiv:2503.04941, version 2), and what the sandbox at epoch.ai/gate can export is established (whether it offers named presets and downloadable results was not checked; the specification assumes presets). If nothing can be exported, the fallback is stated and the editor approves it before any comparison.
- A1.2 D-005 is amended to contain the numeric criteria below before the comparison runs.
- A1.3 *Same equations (proposed).* With GATE's own investment path supplied as an input, S3's effective compute, algorithmic efficiency, automation fraction and output match the sandbox within ±2% (the spirit of D-004: this part re-implements the same equations) for at least three parameter settings, the default and two chosen by the editor before the run.
- A1.4 *Behavioural rule (report only).* The departure of the behavioural investment path from GATE's optimised one is reported (largest and mean difference per setting, and the first year it exceeds 5% and 10%). No pass or fail: the rule is a deliberate departure (D-005).
- A1.5 *Extreme conditions.* Zero hardware and algorithmic growth leaves the automation fraction constant; no investment gives no capital growth; the automation fraction never decreases when effective compute rises; no NaN or negative stock to 2100.
- A1.6 *Fallback if nothing can be exported (proposed).* Reproduce the paper's published base-case figures within ±10%, labelled as digitised with a looser tolerance; the editor decides whether that is enough to proceed.

**Data and sources.** GATE paper (CC BY 4.0, verified); epoch.ai/gate (Epoch work "free to use, distribute, and reproduce" with credit under the Creative Commons Attribution licence; no software licence stated; no source code found, so S3 is written from the paper and cites it); Epoch data hub for initial values (attribution required).
**Decisions.** D-005 before M1 starts, amended as above.
**Risks.** (1) No code and an unknown export: the biggest risk in the plan; the size could double. (2) Epoch says GATE behaves poorly near full automation, so claims must be limited to where it is reliable. (3) The behavioural rule changes the dynamics; the A1.3/A1.4 split is meant to separate that from errors. (4) The start year of GATE's calibration and of Epoch's compute series was not checked, which bears on N1.
**✋ Checkpoint:** the editor approves the comparison report before M2.

### M2 — Slice: AI, electricity, climate (S3 + minimal S4 + S6), and Demo 0 (3–5 sessions, plus 1–2 for the demo page)

**Goal.** Close R1 (AI growth engine), B1 (electricity limit) and B2 (climate damage) in a thin slice: S3 with its own growth module, a data-centre electricity module with electricity supply taken from recorded Earth4All.jl scenario series, and FaIR for temperature; S1 population exogenous.

**Deliverables.** The data-centre electricity module (`E_dc = C_hw_operating / η_hw · PUE`, spec S4); `f3/sectors/s6_climate.py` coupling FaIR; the damage function with three switchable options (D-007); the coupled slice; the Demo 0 page (section 10).

**Acceptance tests (before the work).**
- A2.1 *FaIR alone, first.* With recorded historical emissions (Global Carbon Budget 2025 for CO2; the source chosen in N2 for the rest), FaIR's mean warming for 2015–2024 lies within the observational uncertainty of the observed series chosen (HadCRUT or NOAA, to be added to `SOURCES.md` and verified before the test; the uncertainty is read from the dataset). FaIR's configuration is taken as published, with its calibration source recorded.
- A2.2 *Data-centre electricity (proposed).* The module reproduces the IEA estimates for 2024 (about 415 TWh, *Energy and AI*) and 2025 (485 TWh, *Key Questions*) within ±10%, since the IEA gives no uncertainty. The IEA's 2030 figure (950 TWh) is a projection under the IEA's assumptions: it is compared and reported, never a target.
- A2.3 *Loop signs, no magnitudes pre-set.* B1: lowering electricity supply lowers compute growth in the following years. R1: raising the AI investment share raises compute and automation. B2: the high damage option gives lower output by 2100 than the low option, all else equal.
- A2.4 *Invariance.* With the S3–S4 coupling off, S3 reproduces its M1 results to 1e-9; with damages off, likewise.
- A2.5 *Extreme conditions.* Zero compute growth keeps data-centre electricity constant; unlimited electricity makes B1 inactive.
- A2.6 *Step.* Halving the loop step (0.25 to 0.125 year) changes the slice's outputs by at most 0.1% (proposed); this tests the annual FaIR coupling.
- A2.7 The Demo 0 content is approved by the editor before publication.

**Data and sources.** IEA *Key Questions* and *Energy and AI* (CC BY 4.0, verified); Epoch data hub (AI data centers, ML hardware, chip sales; licence wording verified, version not stated); Global Carbon Budget 2025 (CC BY 4.0, verified); FaIR 2.2.4 (Apache 2.0; its calibration constraints still to be checked); an observed-warming dataset (to be added); Earth4All.jl pinned runs for supply paths. Water is deferred to M5.
**Decisions.** D-007 before the damage part; N1 and N2 before coding; N3 from M0; a minimal format decision for Demo 0 (section 10), without settling D-009.
**Risks.** (1) Whether FaIR can be advanced year by year inside a feedback loop was **not checked**: it is designed to run a whole emissions series in one call; the options are to re-run it each year (costly), to use a simplified response model of FaIR, or to couple with a one-year lag. (2) Non-CO2 emissions have no source (N2). (3) The IEA's data-centre figures define "data centre" in their own way, so the module's boundary must match. (4) The slice's economy is GATE's own and will be replaced or extended in M4.
**✋ Checkpoint:** the editor approves Demo 0 before it is published.

### M3 — Complete World3 in Python: agriculture, capital, resources, pollution (5–8 sessions)

**Goal.** Port the four remaining World3 sectors so that F3 runs the full World3 end to end (review item 11) and reproduces WorldDynamics.jl, the same way S1 was done.

**Deliverables.** One module per sector under `f3/sectors/` (names set in M0), each with the attribution header, the source line number of every equation (Appendix A where the package cites them), a `NOTICE` entry, fixtures exported from the pinned Julia run by name, and a comparison report like `audit/s1-port-report.md`.

**Acceptance tests (before the work).**
- A3.1 *Each sector alone.* With the recorded inputs, every state within ±2% of WorldDynamics.jl (D-004) for both parameter sets, started from the reference's own initial state; the reference's own default-against-tight difference reported beside each figure.
- A3.2 *Full coupled run.* All 29 World3 states within ±2% of WorldDynamics.jl, 1900–2100, both parameter sets. If a state exceeds 2% because of the reference's own solver (as `fcfpc1` did in S1), that is reported and the comparison is also made against the tight-tolerance reference; the criterion is **not** relaxed, and a revised criterion would be a new labelled proposal.
- A3.3 *Second check.* Against unmodified PyWorld3 at dt = 0.05, the twelve main stocks within 2% with PyWorld3's pollution-delay start-up matched (diagnostic, labelled as in CLAUDE.md); the 2004 comparison is diagnostic as in S1.
- A3.4 All existing tests still pass; the S1 results inside the full run equal the S1 results with recorded inputs within 0.25% (the largest gap measured for S1 with the 2004 set).
- A3.5 *Time.* The full World3 run time is measured and reported (it sets the Monte Carlo budget in Phase 3).

**Data and sources.** WorldDynamics.jl v1.0.0 pinned environment (MIT, D-017); PyWorld3 1.1 unmodified. **Decisions.** None new; D-015 and D-019 apply (both parameter sets; 1970 start per D-019 Option C). **Risks.** (1) The four sectors together are about 2.7 times S1 by equation count, and their delay and switch content was not counted. (2) The pollution start-up difference between the two references (373.7% for as-shipped PyWorld3) makes the second check weaker. (3) The 2004 set has no independent second implementation. (4) The reference's own solver error may grow in longer chains.

### M4 — Port the reused Earth4All sectors (S2 economy, S4 energy) (6–10 sessions)

**Goal.** Port the Earth4All.jl sectors that D-016 keeps: output, inventory, finance (reuse); demand, public, energy (reuse with changes); labour market (provisional); and decide what "other" is for.

**Deliverables.** One module per sector under `f3/sectors/`, attribution and `NOTICE` entries (Earth4All.jl is MIT), fixtures from pinned runs of Earth4All.jl in both scenarios, a comparison report per sector; the demand component-level comparison with Vensim that D-016 requires; `EDROTA2022` exposed as a documented parameter; the warming channels in these sectors as switchable inputs (principle 3).

**Acceptance tests (before the work).** Earth4All.jl is itself only an approximation of Vensim (D-018), so the reference for the port is Earth4All.jl, as D-011 and D-018 say.
- A4.1 *Each sector alone, ±2% of Earth4All.jl* for every state variable and for the headline variables of that sector, in both scenarios, with recorded inputs by name. Earth4All.jl solves with Euler at 1/64 year and F3 uses 0.25 year (D-003): the step effect is measured first (the port at 1/64 year against Earth4All.jl, then at 0.25 year) and reported; if the 0.25-year result exceeds 2%, the sector runs at a smaller internal step and the reason is recorded. This is a stated rule, not a relaxation.
- A4.2 *Switches.* With the warming channels off the sector still passes A4.1; with them on and warming held at the 2022 value, results equal the off case.
- A4.3 *Demand.* The component comparison with Vensim (through the package's own mechanism, D-014) is reported per variable with true relative error, median and 95th percentile (the T0 method); D-004 is not relaxed.
- A4.4 *Labour market.* Re-test T2 (employed at most working-age population) on the ported sector, under the definition accepted in D-016 (employed = `WF`, working-age = `WAP`), and record the effect of the automation input from S3 when it is connected (M6).
- A4.5 *Coupled economy.* All reused sectors together reproduce Earth4All.jl's economy variables (GDP, GDP per person, inequality index, public spending, energy mix) within ±2% in both scenarios, with the replaced sectors (population, climate, foodland, wellbeing) supplied as recorded inputs.
- A4.6 *Known deviations.* Where Earth4All.jl itself deviates from Vensim by more than 2% (D-018: the well-being index, inequality), F3 reports the deviation and does not claim the port reproduces Vensim.

**Data and sources.** Earth4All.jl pinned (MIT; commit `16f37d0`; `audit/env-earth4all`); Vensim output only through the package's own comparison, never stored (D-014); IEA and Epoch data for the energy extension. **Decisions.** D-016 applies; N4 before the first sector; D-006 before the materials link. **Risks.** (1) Size: 379 equations and delay helpers by a rough count (excluding "other"), about 7 times S1, and the sectors are tightly interlinked, so "each sector alone" needs recorded inputs for many series. (2) The step mismatch above. (3) The `22022 + IPP` and the two `2020 + IPP` ramp ends: whether Vensim has them was not checked, so a port could copy a typo; the port records its choice. (4) Demand deviates most from Vensim, so A4.3 may report more than the sector can fix.

### M5 — New modules: S7 social, S5 minerals and water, and the warming channels in replaced sectors (6–10 sessions)

**Goal.** Build what has no reference: an explicit-stock social module, an aggregate critical-minerals index, a data-centre and chip-fabrication water module, labour share and inequality, and whichever of the four warming channels in replaced sectors F3 decides it needs (to be traced in M0; see section 3).

**Deliverables.** `s7_social`, `s5_minerals`, `s5_water` modules; for each, before any code, a one-page document with the equations, the source of every parameter and the units (the substitute for "tested against a reference" for a module with none); data cards under `data/` for each dataset used (D-001); a decision for each parameter that has no source.

**Acceptance tests (before the work).**
- A5.1 *Documentation first.* Each module has its equations and sources documented and the editor-in-chief has seen them before the code is merged.
- A5.2 *Balance and bounds.* Mineral stocks never go negative; water use never exceeds the supply declared; social stocks stay inside their declared bounds, in every scenario; no NaN.
- A5.3 *Extreme conditions (spec 7.5).* Zero compute: data-centre water and mineral demand fall to the baseline; infinite supply: B3 and B4 are inactive; no automation: the labour share is constant.
- A5.4 *Hindcast: metrics fixed now, thresholds fixed when the data are loaded and before the first run.* Labour share and top-10% income share are compared with observed series for 1970–2024; the editor sets the pass thresholds on the day the series are loaded, before the first run (a number invented now would be a guess, since the series are not in hand).
- A5.5 *Sign tests for B3, B4, B5 and R2*, as in A2.3.
- A5.6 *Open terms.* No dataset is committed or redistributed until its licence is read from its own page (WID and ILOSTAT are still unknown).

**Data and sources.** WID (terms **unknown**), ILOSTAT labour share (SDG series starts 2004, terms unknown), USGS Mineral Commodity Summaries 2026 (public domain; the report PDF was not read), LBNL and TSMC water documents (**could not be read**; figures unverified), UCDP (CC BY 4.0, armed conflict only). **Decisions.** D-006 (minerals) and D-008 (social-tension proxy) before S7; N5 (backtest criteria) before A5.4. **Risks.** (1) The least verified data are here; some modules may have to start with parameters clearly labelled illustrative. (2) No long labour-share series was found. (3) No open proxy for social tension from 1970. (4) Water: only US figures were found, none verified.

### M6 — Integration and Phase 2 review (4–7 sessions)

**Goal.** Connect all sectors, run the four reference scenarios (spec section 6) from 1970 to 2100, and review.

**Deliverables.** The coupled model; the four scenarios; `docs/phase-2-review.md`; a sign test for each loop of spec section 5; updated `MODEL_SPEC.md`, `README.md`, `STATUS.md`.

**Acceptance tests (before the work).**
- A6.1 *Baseline scenario.* With the AI sector switched off, population, resources, agriculture, capital and pollution reproduce the full World3 run within ±2% (D-004), as spec 6.1 already requires; comparison with Earth4All "Too Little Too Late" is information only.
- A6.2 *All loops.* R1, R2, B1–B6 each have a sign test showing the intended direction of effect on an output named before the test (R3 is optional in the specification and is tested if built).
- A6.3 *Invariance.* Each coupling can be switched off and the sector then returns its stand-alone result (to 1e-9 for S3 and S1, within each sector's own recorded tolerance for the others).
- A6.4 *Extreme conditions* for the whole model (spec 7.5): zero compute growth, infinite energy, zero investment: plausible behaviour, no NaN, no negative stock.
- A6.5 *Run time measured.* One full run's time is reported, and an upper bound for a thousand-run Monte Carlo derived from it.
- A6.6 *Initialisation.* The 1970 state follows D-019 Option C; the Phase 3 question (observed 1970 start) stays open, as D-019 says.
- A6.7 The Phase 2 review states which tests passed, which failed and which were not run.

**Data and sources.** All of the above. **Decisions.** N6 (Phase 3 entry conditions, optional). **Risks.** (1) Integration surprises: sectors run at different steps and the coupling can be unstable. (2) The warming input reaches the reused sectors only after M2 and M5. (3) Whatever is unverified in the data sources travels forward.
**✋ Checkpoint:** the editor reviews the Phase 2 review before Phase 3.

---

## 7. Alternative order A (World3 first), in brief

M0, then **M3** (World3 complete), **M4** (Earth4All sectors), **M2′** (FaIR and the warming channels in the reused sectors, 4–6 sessions), **M1** (S3, with the economy now available, 4–6 sessions), **M5** (new modules), **M6**. Acceptance tests are those of section 6 (M2′ is M2 without S3 and the data-centre module; M1 then has the full economy to attach to, so A1.3 is unchanged and A2.3 is split between M2′ and M1). **Sizes:** the same milestones, so the same total (29–48 sessions); the first demo comes after M1 in this order, at about 21–34 sessions. **What B costs relative to A:** the slice's economy is replaced in M4, and its loop step and interface may need rework (the M0 interface work and the use of GATE's own growth module limit this). **What A costs relative to B:** the largest unknown (S3) is reached last, and nothing public exists for many sessions.

---

## 8. Decisions needed, and when

D-005 to D-009 are existing Proposed entries; N1 to N6 are new and would be drafted in M0 (Proposed). **None is decided here.**

| ID | Decision | Needed before | Why then |
|---|---|---|---|
| D-005 | AI-sector integration approach (as drafted: re-implement GATE's three modules, behavioural investment rule) | M1, amended with the numeric criteria of A1.2 | M1 is the re-implementation |
| D-006 | Critical minerals granularity (aggregate index in v0.1) | M5 (the minerals part) | M5 builds the module; the data are public domain (USGS) |
| D-007 | Climate damage function (three options as a lever) | M2 (the damage part) | A2.3 tests it; it also decides how warming reaches the reused sectors |
| D-008 | Social tension proxy | M5 (before S7), and by Phase 3 for the backtest | No open source found; options (1)–(3) in the D-008 evidence note |
| D-009 | Dashboard stack | Phase 4; a minimal format for Demo 0 is a separate small choice (section 10) | Phase 4 |
| N1 | Start year and initial state of S3 and the data-centre module (GATE and Epoch data have their own calibration years) | M1 | F3 starts in 1970; AI compute data begin much later (the start years of Epoch's series were not checked) |
| N2 | Source of non-CO2 greenhouse gases and land-use CO2 for FaIR (no F3 sector produces them): prescribed from observed and scenario series, from recorded Earth4All outputs, or from a simplified agriculture module | M2 | A2.1 needs them |
| N3 | Sector interface: step, units, naming, how exchanged series are recorded | M0 | Everything after builds on it |
| N4 | How reused Earth4All sectors receive inputs from sectors F3 replaces (population, climate, foodland, wellbeing): recorded Earth4All series, or F3's own sectors from the start | M4 | A4.1 and A4.5 test each choice differently |
| N5 | Phase 3 backtest criteria fixed now: variables, error metrics, out-of-sample period (2000–2025 per D-015), and age structure as a named criterion (the finding of the D-015 outcome note) | M5 (hindcast thresholds) and before Phase 3 | Fixes what "good" means before the data are seen |
| N6 | Phase 3 entry conditions (what Phase 2 must show) | M6 | Optional |

## 9. Research tasks inside the milestones

Done in M0–M2 by the Research role, since the plan depends on them: (1) what the GATE sandbox can export (A1.1); (2) the start years of Epoch's AI compute and data-centre series and of the IEA historical series (N1); (3) an observed warming dataset and its uncertainty (A2.1); (4) published sources for the three damage functions (M0 deliverable 4); (5) the licences of WID and ILOSTAT, read from the files or asked of the organisations (A5.6); (6) the primary LBNL and TSMC documents, opened by hand since automated access was refused; (7) the CNTS licence terms if option (2) of D-008 is considered.

## 10. The earliest honest public demo

**Demo 0, after M2** (about 9–15 sessions from the start of Phase 2 in order B). A static page with precomputed runs: no live model, so no hosting decision beyond a static site, and D-009 is not pre-empted. Everything on it is labelled **"conditional scenarios, not forecasts"**.

**What it would show:** three AI-investment settings (low, central, race) run through the slice (AI, electricity, climate) from 1970 to 2100: compute, automation fraction, data-centre electricity demand shown beside the IEA's published 2024 and 2025 values (the IEA's 2030 projection shown separately and labelled as its projection, not as a target the model was tuned to), and temperature under the three damage options. It would also show the loop signs (more investment, more compute, more electricity, slower growth when supply binds).

**What it would not show, and says so on the page:** population, inequality, social stability, minerals, water or the full economy (these arrive in M3–M5); any uncertainty band (Phase 3); any calibration to observed data beyond the data-centre check and the warming check; any claim about likelihood. It would carry the open caveats: GATE is re-implemented from its paper and not from its code; Epoch states that GATE behaves poorly near full automation; FaIR is used as published; nothing has been validated against an independent reference beyond the tests A1 and A2.

**Condition for publishing:** the editor-in-chief approves the content (A2.7). Spec section 7.6 asks for external review before the public launch; whether a short review of Demo 0 is wanted is the editor's choice.

**Under order A,** the earliest demo is the same page, available only after S3 and the slice are built at the end (about 21–34 sessions).

## 11. Sizes, and what is uncertain

| Milestone | Sessions | Main uncertainty |
|---|---|---|
| M0 | 1–2 | Whether the time convention can be settled from the equations |
| M1 | 4–6 | **Large**: no GATE code; unknown export; could double if fallback A1.6 is needed |
| M2 | 3–5 (+1–2 for the demo page) | **Large**: FaIR has not been used in a loop; non-CO2 inputs |
| M3 | 5–8 | Moderate: mechanical, about 2.7 times S1, more delays |
| M4 | 6–10 | **Large**: about 7 times S1, many cross-links, a step mismatch |
| M5 | 6–10 | **Large**: data not verified; three modules with no reference |
| M6 | 4–7 | Integration surprises |
| **Total** | **29–48** (order B: demo at 9–15) | |

**What a session is.** One focused working session of Claude with the editor's decisions in between. The only yardstick is Phase 1, which is not a clean one: it ran over four calendar days (2026-10-05 to 2026-10-08) and 57 commits, and I did not count its sessions. So these sizes are estimates built from relative size against S1 (the one sector actually ported), not from a measured rate. **The ranges are wide for that reason.** They also rest on rough counts of equations (147 for the four World3 sectors against 54 for S1; 379 for the seven reused Earth4All sectors, 397 with "other") and on guesses where no reference exists (S3, S7, water). Review waits are not counted; each ✋ can add time. **The estimate most likely to be wrong is M1**, then M2 and M5.

**Speed.** One S1 run takes 0.24 s (measured, 1970–2100, step 0.25 year). If the full model is 20 to 40 times heavier (a guess), one run takes 5–10 s and a thousand-run Monte Carlo 1.5–3 hours on one core; this is an order of magnitude, to be replaced by A3.5 and A6.5.

## 12. Risks across the phase

| Risk | Effect | Mitigation |
|---|---|---|
| The GATE sandbox cannot be exported | M1 has no reference; the claim "S3 reproduces GATE" weakens | A1.1 first; fallback A1.6 with the editor's approval; order A if it fails |
| FaIR cannot run year by year | M2 stalls | decide the three coupling options in M0 (research note); test with a lag in the slice |
| Unverified data become model inputs | Wrong baselines presented as sourced | A5.6; labels "illustrative"; data cards; verified/unverified column in `SOURCES.md` |
| Earth4All sectors deviate from Vensim (D-018) | Ported sectors inherit deviations; a port can pass ±2% against Earth4All.jl while not matching Vensim | A4.6 and the reporting rule of D-018 |
| Step mismatch (Earth4All.jl at 1/64 year, F3 at 0.25) | Sector tests fail for numerical reasons | A4.1 measures it first |
| Scope growth | Six milestones and six new decisions | The editor can drop M5 modules (water, minerals) from a first release and label them absent; Demo 0 does not depend on them |
| Review capacity | ✋ checkpoints queue | Decisions batched per milestone; N1–N6 drafted together in M0 |

## 13. What this plan does not do

It does not approve a decision, choose between the damage functions, select a social-tension proxy, set a dashboard stack, or settle the initialisation of any sector other than World3's (D-019). It does not claim any number is a forecast. Numbers marked *proposed* are the Validator's and are not accepted until the editor accepts them. Anything outside the milestones above (regional disaggregation, a live dashboard, Monte Carlo) belongs to later phases.


---

## 14. Amendment of 2026-10-08, after the approval of D-020 to D-025

The sections above are the plan as approved on 2026-10-08 and are not rewritten. This section records what the decisions taken at the M0 checkpoint change. It applies to the milestones from M1 on. The wording of the decisions is in `DECISIONS.md`; where this section and a decision differ, the decision governs.

### 14.1 What D-020 changes (the editor asked for these two to be recorded)

D-020 (question 1 option A, question 2 option (i)) fixes when each part of the model starts:

| Part | Starts | Before that |
|---|---|---|
| World3-based sectors (S1, and M3's agriculture, capital, resources, pollution) | 1970, from the model's own state (D-019 Option C) | not applicable |
| Reused Earth4All sectors (M4) | **1980**, from their own initial state | undefined or prescribed; from 1970 to 1980 only the World3-based sectors run |
| S3 AI sector and the data-centre module (M1, M2) | **2025**, from GATE's initial values | the automation fraction is held at GATE's initial value; data-centre electricity is prescribed from IEA estimates where available |
| FaIR (S6) | its own history: it is re-run from the start each year (D-021) with prescribed historical emissions | not applicable |

**A6.6 (initialisation)**, as approved, read: "The 1970 state follows D-019 Option C; the Phase 3 question (observed 1970 start) stays open, as D-019 says." It now reads, in addition: the World3-based sectors start in 1970, the Earth4All sectors in 1980 and S3 in 2025, each from the starting point D-020 fixes; **nothing is coupled before 1980**, so a coupled run reports from 1980, and 1970 to 1980 is reported from the World3-based sectors alone.

**Demo 0 (section 10)**, as approved, shows "three AI-investment settings ... from 1970 to 2100". Under D-020 it shows the AI sector (compute, automation fraction, data-centre electricity) **from 2025 to 2100**; the slice's climate part (temperature under the three damage options) can still be shown from 1970 because FaIR runs from its own history with prescribed emissions (D-021). Data-centre electricity before 2025 appears only as prescribed IEA values, labelled as inputs, not as model output; the only values read so far are 415 TWh for 2024 and 485 TWh for 2025, and the IEA's earlier series was not read. The page also carries the label D-021 requires: **"non-CO2 emissions are prescribed, not modelled"**.

### 14.2 Other consequences noticed while recording the decisions (listed for the editor's confirmation; **not applied**)

These follow from the approved decisions but touch acceptance tests or documents that were approved earlier. None has been changed.

1. **A2.2 cannot be an independent test of the data-centre module for 2024 or 2025.** Under D-020 the module is switched on in 2025 from GATE's initial values, and the 2024 value is prescribed; the 2025 value is an initial condition, so comparing it with the IEA's 485 TWh checks the initialisation, not the model's dynamics. As written, A2.2 also asks the module to "reproduce" 2024. Proposed reading, for confirmation: A2.2 becomes a consistency check of the 2025 initial value against 485 TWh within the stated ±10%, the 2024 value is an input, and the plan states that **no independent test of modelled data-centre electricity against estimates exists before 2025**; the IEA's 2030 figure stays report-only. This is a consequence of the decision, not a relaxation after seeing a result, but it changes an approved test and so waits for the editor.
2. **GATE's economy and Earth4All's economy are two models of the same world** (GATE: output 110 trillion USD/year and capital 450 trillion USD at the start of 2025, as read from its Appendix D). From 2025 the coupled model needs a rule saying which one drives output, or how they are reconciled. This does not arise in M1 or in the slice (whose economy is GATE's own); it must be settled before M4 couples the Earth4All economy to S3, and D-020's text names it as open.
3. **A4.5 and the Earth4All sector tests** are already on a 1980 horizon (the package solves 1980 to 2100); no change.
4. **A5.4 (hindcast, 1970 to 2024)**: variables produced by the Earth4All sectors (labour share in its labour market, the inequality index) exist only from 1980; the hindcast window for them starts in 1980, and for a variable from outside those sectors (for example observed WID series used only as data) it can start earlier. The editor sets the window when the thresholds are set (D-024).
5. **`MODEL_SPEC.md`** still says "Time horizon 1970-2100" (section 3) and its sector text assumes a 1970 start for every sector. It has not been changed; it should say that the horizon is 1970 to 2100 for the World3-based sectors, 1980 to 2100 for the Earth4All sectors and 2025 to 2100 for S3, and that the coupled run reports from 1980. Wording to be agreed with the editor.
6. **`docs/phase-1-review.md`**, section 2 ("Starting in 1970"), still says the rescaling helped the 1974 set by about one point; D-019's dated outcome note of 2026-10-08 corrects that statement and the review has not been edited.

### 14.2a Confirmation of consequences 1, 5 and 6 (2026-10-08)

Stéphane Beau confirmed three of the six consequences listed in 14.2. The text of 14.2 above is unchanged; this note records what became effective.

- **Consequence 1 is confirmed as proposed.** A2.2 now reads as a consistency check, not an independent test: the 2025 initial value of data-centre electricity is checked against the IEA's 485 TWh within the stated ±10%; the 2024 value is an input; the plan states that **no independent test of modelled data-centre electricity against estimates exists before 2025**; the IEA's 2030 figure stays report-only and is never a target.
- **Consequence 5 is confirmed as proposed and applied** to `MODEL_SPEC.md` (the horizon row of section 3): 1970 to 2100 for the World3-based sectors, 1980 to 2100 for the Earth4All sectors, 2025 to 2100 for S3, and the coupled run reports from 1980.
- **Consequence 6 is confirmed**: `docs/phase-1-review.md`, section 2, has received a dated note correcting the "about one point" sentence (a note, not a rewrite).
- **Consequences 2, 3 and 4 are acknowledged and stay open as listed**: the GATE-versus-Earth4All economy from 2025 (to be settled before M4 couples them); the Earth4All sector tests on a 1980 horizon (no change needed); the hindcast window for variables from the Earth4All sectors (the editor sets it when the D-024 thresholds are set).

### 14.3 What the other approvals change in the plan

| Decision | Effect on the milestones |
|---|---|
| D-021: FaIR re-run from the start each year; non-CO2 emissions prescribed | M2's FaIR coupling is the re-run; options (b) and (c) are re-tested once a real configuration exists and the editor then decides; Demo 0 carries the label above. Cost per full run is not yet measured with a real configuration (the toy case was 24 s for 130 annual re-runs) |
| D-022: explicit coupling at 0.25 year; t = Y is 1 January | A2.6 tests the loop step with live partners; observed 1 January values are compared with the model at t = Y (written into `MODEL_SPEC.md` as A0.3) |
| D-023: option C | M4 tests each sector against replayed Earth4All series first and builds adapters for the coupled model afterwards, reporting the adapters' effect; the warming baseline of `OW` and the working-age mapping are settled before M4's output, public and labour-market tests |
| D-024: framework approved, thresholds set by the editor before the series are loaded | Before the M5 hindcast the editor sets thresholds; the age-structure numbers were already seen at approval and any age-structure threshold must say so; each criterion states what a failure triggers (D-024 Decision) |
| D-025: Phase 3 entry conditions as drafted | M6 closes against the six conditions in D-025 |
| M0 | Closed on 2026-10-08 (A0.1 to A0.5 met; see `docs/STATUS.md`) |
