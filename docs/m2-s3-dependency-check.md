# M2: which deliverables depend on S3's absolute output matching GATE (dependency check)

**Status:** note, 2026-10-12. Not code. Basis: `docs/phase-2-plan.md` section M2 and section 10, D-029 (A1.3 failed; S3's absolute output unvalidated against GATE after about 2027; with Epoch's own composite supplied everything matches), D-028 (R3 is a scenario-lever rule, A1.4 poor). "Depends" means: would the deliverable be wrong, or would a test or claim be hollow, if S3's `gwp`, capital and effective compute are off by large factors after 2027.

| M2 deliverable or test | Depends on S3 absolute output matching GATE? | Why, and what to do |
|---|---|---|
| **A2.1** FaIR alone (warming 2015 to 2024 against observations, recorded emissions) | **No** | S3 is not involved. Safe to start. |
| **S6 climate sector** (`s6_climate.py`, FaIR re-run each year, D-021) | **No** (for building it) | Takes emissions and gives temperature. Non-CO2 emissions need N2 (decided: prescribed). |
| **Data-centre electricity module** `E_dc = C_hw_operating / η_hw · PUE` | **Partly** | Its inputs are compute quantities from S3: the raw compute stock `Q`, hardware efficiency `H` and usable compute `g(Q)`. In 2025 to 2027 they match GATE (the first periods match within 0.1% to 0.3%); later, the compute path inherits the composite error through output and investment dollars. **Do:** build and test the module on given compute paths; label every post-2027 electricity figure per D-029; prefer reporting composite-independent shapes (growth rates of compute, timing of the cap) over absolute TWh. |
| **A2.2** module vs IEA 2024 and 2025 (±10%) | **No** (in effect) | Already read as a consistency check of the 2025 initial value (plan 14.2a); 2025 is an initial condition, where S3 matches. The IEA 2030 figure stays report-only. |
| **Damage function, three options** (D-007) | **Partly** | The damage acts on S3's output; the A2.3 B2 test is a sign test (high damage gives lower output by 2100 than low, all else equal), which survives a wrong level. Absolute output losses in dollars do not. **Do:** test signs only; show damages as percentages of S3's own output, labelled per D-029; D-007 itself is still open. |
| **A2.3** loop signs (B1, R1, B2) | **No** | Sign tests, "no magnitudes pre-set". R1 (raise the AI investment share, raise compute and automation) is already tested in `tests/test_s3_r3.py` for the R3 lever. |
| **A2.4** invariance (coupling off reproduces M1 results to 1e-9) | **No** | Compares S3 with itself. Note that the "M1 results" it refers to are S3's, which failed A1.3. |
| **A2.5** extreme conditions | **No** | Properties of the equations (A1.5-style), which pass. |
| **A2.6** step halving (≤ 0.1%) | **No** | Self-consistency of the loop. |
| **The coupled slice** (S3 + data-centre + FaIR, S1 exogenous) | **Partly** | Runs fine; its absolute outputs (output, compute, electricity, then temperature through emissions) after 2027 carry the S3 caveat. Loop structure and signs do not. |
| **Demo 0 page** (three AI-investment settings 2025 to 2100: compute, automation fraction, data-centre electricity, temperature under three damage options) | **Yes for absolute levels; no for shapes and the climate part** | The automation fraction matches GATE closely (within 2.3% at worst in the conservative run, 0.01% to 1.1% elsewhere) and is the safest AI quantity to show. Compute, electricity and anything in dollars after about 2027 are unvalidated. **Do:** put the D-029 notice on the page next to every S3-derived chart; say "the model does not reproduce GATE"; show the R3 investment settings as scenario levers, not as GATE paths; no statement of the form "GATE says" about S3's outputs. The temperature curves for 1970 to 2025 do not depend on S3. |
| **A2.7** editor approves Demo 0 | n/a | The approval should include the D-029 labelling. |

## Headline

- **Safe to start now, independent of S3's open difference:** FaIR alone (A2.1) and the `s6_climate` sector, and the loop-structure tests (A2.3 signs, A2.4 to A2.6).
- **Buildable, but outputs must be labelled per D-029:** the data-centre electricity module, the damage function, the coupled slice and Demo 0.
- **Blocked:** nothing is blocked outright. Two things are blocked on other decisions, not on S3: the damage part waits for **D-007**, and Demo 0's format needs the small format decision in plan section 10.
- **What would change this:** an answer from Epoch (email sent by the editor on 2026-10-17, no reply as of 2026-10-22) that resolves the composite would turn the "partly" rows into "no" and allow absolute S3 numbers to be shown after a re-run of A1.3. Until then, D-029 governs.

## Recommendation for the first M2 step

**Start with FaIR alone (A2.1) and the climate sector.** It does not touch S3, it is the plan's named M2 risk (FaIR in a loop, re-run each year, D-021 cost not yet measured with a real configuration), and it needs two small inputs the plan already lists: an observed warming series (HadCRUT or NOAA, to be added to `research/SOURCES.md` and verified) and the historical emissions sources (Global Carbon Budget 2025 for CO2, prescribed non-CO2 per N2/D-021). Doing it first also gives the editor something to decide on D-007 with a real temperature path. The data-centre module can follow on given compute paths.
