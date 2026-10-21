# Track A plan: rest of M2 (data-centre module, damage function, coupled slice) and the Demo 0 generator

**Status:** written 2026-10-17 before any code and before any result. Branch `track-a`, from main at 0eea404. Tests and readings below are fixed now. Provisional decisions are drafted in `docs/tracks/track-a.md`, not in `DECISIONS.md`.

## 0. IEA verification (what was read, 2026-10-17)

| Item | Read | Where |
|---|---|---|
| 2024: "around 415 TWh", about 1.5% of global electricity consumption | yes, verbatim | iea.org/reports/energy-and-ai/energy-demand-from-ai (fetched page) and Key Questions text (Base Case sentence, "around 415 TWh in 2024") |
| 2025: "485 TWh in 2025" | yes, verbatim, twice in the PDF text | Key Questions on Energy and AI (2026), PDF, local copy outside the repo `C:\Users\sbeau\dev\_iea_sources\KeyQuestionsonEnergyandAI.pdf`, sha256 `a3a47f07b35420e74b243878f631192b04788110db3c75275feb0fbdee7f4858`, text extracted with pdftotext |
| Same PDF, Q1 answer | "grew by more than 15% between 2024 and 2025, adding around 70 TWh ... taking the sector's annual consumption to almost 500 TWh" (the executive summary says 17%); 415 + 70 = 485, so these are consistent with 485 but "almost 500" is looser wording | PDF text |
| 2030: 950 TWh (Key Questions), 945 TWh (Energy and AI Base Case) | yes; report-only, a projection under IEA assumptions | both |
| Licence | CC BY 4.0, printed in the citation line of both reports | both |
| Boundary of "data centre" | **only partly.** Energy and AI describes a data centre as "facilities used to house servers, storage systems, networking equipment and associated components", with shares (servers about 60%, storage about 5%, networking up to 5%, cooling 7% to over 30%, plus UPS, generators, lighting). Neither document read states a formal accounting boundary. **Whether crypto-mining load is excluded was not found in any IEA text I read** (a secondary source, Our World in Data via a search summary, says it is excluded; not verified). PUE: Key Questions gives 1.1 to 1.2 for best-in-class hyperscale and 1.5 to 1.7 for older or enterprise sites; Energy and AI has no PUE. How the 415 TWh baseline was built is not on the page read |
| Not read | Energy and AI full PDF; the Key Questions Annex B text (grep found no data-centre definition in it); the IEA data-centre electricity series before 2024 |

**Consequence (STOP condition of this track):** the numbers and the licence are verified; the boundary is not verified well enough to claim the module's E_dc and the IEA figure are like for like. No module code is written until the editor accepts the descriptive boundary above (and the unverified crypto point) or supplies the IEA methodology.

## 1. Design (fixed before code)

- **Data-centre module (spec S4):** `E_dc [TWh/yr] = C_hw_operating [FLOP/yr] / eta_hw [FLOP/J] * PUE`, with `C_hw_operating` = S3 `compute_stock` (raw Q), `eta_hw` = `eta_0 * H(t)/H0` (S3 hardware efficiency drives energy efficiency; the proportionality is an assumption), PUE a constant. `eta_0` is calibrated once so that E_dc(2025) = 485 TWh; PUE = 1.4 (between the IEA ranges above); both are inputs, labelled. Starts 2025 (D-020); 2024 = 415 TWh is an input.
- **Electricity supply:** taken from recorded Earth4All.jl scenario series (pinned clone `C:\Users\sbeau\dev\Earth4All.jl` at 16f37d0, env `audit/env-earth4all`), by variable name; no Vensim files. The data-centre share of supply is a cap: if `E_dc` demand exceeds the available supply allocated to data centres, S3's usable compute is scaled by supply/demand (B1).
- **S3 to module:** S3 `compute_stock` and `hardware` to the module; the module's `supply_ratio` (min(1, supply/demand)) back to S3 as a multiplier on compute investment's effect (unit "1").
- **Emissions:** prescribed per D-021; the only coupling is an optional, labelled CO2 term for data-centre electricity at a fixed carbon intensity, off in the published grid unless the plan names it.
- **Damage function:** `damages.py`, level of output, `Omega = c * T^2` with c = 0.236% (low), 0.344% (central, derived), (0.595*1.25+0.260)% = 1.00375% (high); default central; T = FaIR warming above 1850-1900, no offset; applied to S3 gwp as a multiplier (1 - Omega). The growth-effect case is not represented.
- **Coupled slice:** S3 (R3 rule) + data-centre module + S6 (all 841 members for published runs; the 20-member subset, every 42nd member, for tests and development, stated wherever used). S1 exogenous. Loop step 0.25 year, t=Y is 1 January, results from 2025.
- **Grid (Demo 0):** R3 settings low/central/race x damage options low/central/high; climate computed once per distinct emissions path and reused where exact; run once in the background with output to a file.

## 2. Acceptance tests (as the plan states them; fixed now)

- **A2.2 (plan 14.2a reading):** consistency check of the 2025 initial value of E_dc against 485 TWh within +-10% (436.5 to 533.5 TWh). 2024 (415) is an input. No independent test of modelled data-centre electricity exists before 2025. The IEA 2030 figure (950) is reported, never a target.
- **A2.3 loop signs (no magnitudes pre-set):** R1: raising the AI investment share (`initial_ai_share`) raises compute and automation. B1: lowering electricity supply lowers compute growth in the following years. B2: the high damage option gives lower output by 2100 than the low option, all else equal.
- **A2.4 invariance:** coupling off reproduces standalone S3 (with R3) to 1e-9 relative on every output; damages off likewise.
- **A2.5 extreme conditions:** zero compute growth keeps E_dc constant; unlimited electricity makes B1 inactive (supply_ratio = 1 throughout, outputs equal to the uncoupled run).
- **A2.6 step:** halving the loop step 0.25 to 0.125 year changes the slice outputs by at most 0.1% (outputs: gwp, compute_stock, frac_automated, E_dc, warming), at every reported year from 2025; the annual FaIR coupling is part of it.
- **A2.7:** editor approval of Demo 0 before any publication (not done by this track).
Failures are recorded with size and first year, never adjusted.

## 3. Labels the Demo 0 page must carry
"conditional scenarios, not forecasts"; D-029 text via `S3AI.validation_status`; GATE re-implemented from the paper, not its code; Epoch's warning near full automation; D-030/D-021 text via `S6Climate.validation_status` and "non-CO2 emissions are prescribed, not modelled"; D-007 level-of-output and "high is not the upper end of the literature"; D-028 with the A1.4 numbers; what is not shown; plan section 10 caveats; data hashes and attributions (HadCRUT5 OGL v3.0 text, GCB 2025 CC BY 4.0, IEA CC BY 4.0, FaIR Apache 2.0).
