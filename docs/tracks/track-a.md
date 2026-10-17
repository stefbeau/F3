# Track A log

## 2026-10-17 IEA boundary: stop, then editor decision (option a)
Plan committed first (`docs/tracks/track-a-plan.md`, aa40a45). IEA numbers and licence verified (see plan section 0); the formal accounting boundary was not. The track stopped and reported; the editor decided option (a) on 2026-10-17 (relayed by the orchestrator). Work continues from step 2. 485 TWh (2025) is a CALIBRATION point and 415 TWh (2024) a reference; neither is validation anywhere. 950 TWh (2030) is a report-only comparison. The crypto-mining exclusion is [unverified] and is labelled so on the page and in the report.

## Provisional decisions (paste-ready blocks)

### P-A1 — Data-centre boundary for the F3 data-centre module (IEA Energy and AI, descriptive)
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** "Data centre" means a facility housing servers, storage systems, networking equipment and associated components (cooling, power distribution, UPS, lighting), as the IEA's Energy and AI describes it. The module's `E_dc` is compared with the IEA's totals on that descriptive boundary only. Whether crypto-mining load is excluded from the IEA totals is [unverified] (no IEA text read states it; a secondary source says it is). 485 TWh (2025) is a calibration point, 415 TWh (2024) a reference value, 950 TWh (2030) a report-only comparison; none is called validation.
- **Recommendation followed:** the editor's option (a), 2026-10-17, after the track reported that the formal boundary could not be verified.
- **Alternatives considered:** (b) wait for the IEA methodology or the full Energy and AI PDF before any module code.
- **Cost of reversing it:** low. The boundary only fixes the calibration constant `eta_0` and the labels; a different boundary re-calibrates one constant, re-runs the grid (about 30 to 34 minutes per loop run with 841 members) and changes label text.

### P-A2 — Data-centre module form, calibration, supply and coupling (Track A)
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** `E_dc = compute_stock / eta_hw * PUE` (spec S4), with `compute_stock` = S3's raw compute stock Q, `eta_hw = eta_0 * H(t)/H(2025)` (S3's hardware price-performance drives energy efficiency; an assumption), PUE = 1.4 (between the IEA's ranges 1.1-1.2 and 1.5-1.7, Key Questions), `eta_0` calibrated once so E_dc(2025) = 485 TWh (calibration point, not validation). Supply = recorded Earth4All.jl electricity production `ene.EP` (pinned 16f37d0, scenario TLTL, exported by `audit/t0/earth4all_supply_export.jl` to `f3/data/earth4all_electricity_supply.csv`; no Vensim file). Data centres may use 5% of that supply (`dc_share_cap`, an assumption; 485 TWh is about 1.5% of the series' 2025 value of about 32,600 TWh). `supply_ratio = min(1, available/demand)` multiplies S3's usable compute (not the stocks), lagging by one year under explicit coupling. Emissions: prescribed (D-021); no electricity-to-emissions coupling is implemented (the plan names none beyond D-021).
- **Recommendation followed:** the plan's M2 deliverable form; simplest reading of spec S4.
- **Alternatives considered:** a larger or smaller share cap; GL scenario supply; scaling investment instead of usable compute; coupling emissions to electricity at a fixed carbon intensity.
- **Cost of reversing it:** low to medium; constants and one wiring line, then re-run the grid (about 30 to 34 minutes for the 841-member climate recording only if the climate changes; the nine slice runs take seconds because climate is recorded once and replayed exactly).

### P-A3 — Damage function action on S3 (Track A)
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** D-007 options as level-of-output multipliers on S3 gross output: `gwp = gwp_gross * (1 - c T^2)`, c = 0.236% (low), 0.344% (central, derived from printed anchors), 1.00375% (high, (0.595 x 1.25 + 0.260)%); T = FaIR ensemble-mean warming above 1850-1900 on 1 January, no offset; damage cap 0.99; default central. The damaged output is what feeds investment (damages lower investment in dollars). Growth-effect case not represented; "high" is not the upper end of the literature.
- **Recommendation followed:** D-007 as approved and its appended text.
- **Alternatives considered:** damage applied to output after investment is computed; a damage on TFP or capital; an offset for FaIR's low start (D-030 leaves it open).
- **Cost of reversing it:** low (one function and one line in S3), plus a re-run of the grid.

### P-A4 — Reuse of one exact climate recording (Track A)
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** Because emissions are prescribed, S6 has no inputs in this slice and its output is identical for every lever. The Demo 0 grid records `S6Climate` once with all 841 members (D-021 option a: exact re-run each year) and replays it in each run; S3 reads warming only at the start of each year, where the replayed value equals the sector's published value. Tests and development use the first 20 members and say so. Not valid once any sector feeds S6.
- **Recommendation followed:** the editor's instruction to reuse climate where exact.
- **Alternatives considered:** a live S6 in each of the 11 runs (about 6 hours with 841 members).
- **Cost of reversing it:** none for results; the replay stops being exact the moment an emissions coupling is added.

### P-A5 — Demo 0 grid and levers (Track A)
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** AI settings: low = initial_ai_share 0.5 x fitted, central = R3 defaults, race = 1.5 x fitted with decay_speed 0.5; damage low/central/high; plus supply 0.5 x and unlimited for central/central. 11 runs, 2025-2100. Chosen before any result was seen.
- **Recommendation followed:** the briefing (small documented set).
- **Alternatives considered:** varying split, capital_scale, training_scale as well.
- **Cost of reversing it:** low; edit `SETTINGS` in `dashboard/demo0/generate.py` and regenerate.

## 2026-10-17 Results (tests/test_m2_slice.py, 20-member development climate; `audit/data/m2-slice-results-dev20.json`)
Pass (6 of 9): A2.2 consistency (E_dc 2025 = 485, by construction), A2.4 invariance (both readings, 1e-9), A2.5 both, B2, damage anchors.
**Failures, recorded as they are; no criterion or test changed:**
1. **A2.6 step halving FAILS.** Largest relative difference between the 0.25 and 0.125 year runs: data-centre electricity used 0.565% (2036; first above 0.1% in 2028), gwp 0.197% (2099; first above 0.1% in 2080), compute stock 0.108% (2049), automation 0.025%, warming 0.0 (recording). Cause not isolated; the loop has first-order coupling (D-022) and the cap `min(1, avail/demand)` is a kink; this is inference.
2. **B1 sign FAILS as written** ("compute never higher with lower supply"): with half the supply, compute stock is up to 17.8% higher than the base case in 2038-2045 (first 2038). Mean log growth 2026-2040 is also not lower (0.7582 against 0.7548). In the five years after the half-supply cap binds (2027) growth is lower (0.956 against 0.971). Inference: with R3 the investment path depends on usable compute (via u), so a lower cap changes the shares and can raise later compute; this is a property of the R3 feedback, not shown further.
3. **R1 sign FAILS on automation at 2065** (both runs at exactly 1.0, so "higher" is false); compute is higher (5.2e34 more). Automation is higher at 2035 and 2045. First year with equality: 2050.
4. Supply binds from 2027-2028 in every case: E_dc demand is 20,010 TWh in 2030 and 413,839 TWh in 2040 against a cap of about 1,750 to 2,100 TWh used. This is S3's own compute path (D-029, unvalidated) meeting the cap; the module's demand leaves any plausible range, and the page says so.
Not done: the full-suite run (see the review file for the final count).
