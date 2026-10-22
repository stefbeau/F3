# S3 with the supply limit on: which outputs stay inside stated bounds? (D-054 item 3; written 2026-10-22)

**Status:** method and pre-registered criteria, **committed before the script was run**. Results are added by dated sections; nothing above is edited afterwards. **Documents and a script only: no sector, test, label or site change.** Script: `audit/t0/s3_supply_limited.py`; figures: `audit/data/s3-supply-limited.json` (comparison figures; nothing from Epoch's bundle is read here).

## 1. Question

The earlier diagnostic (`docs/s3-diagnostic.md`) ran S3 and the data-centre module **without** the supply limit and found the unlimited quantities leave any bounded range, on GATE's own path too. The coupled slice has the limit on: the module computes `supply_ratio = min(1, available / demand)` with `available` = 5% of the Earth4All TLTL electricity supply (D-033), and S3 multiplies its usable compute by it (loop B1). **Which of S3's quantities stay inside stated bounds in that coupled, supply-limited configuration, and which do not?** And therefore which could be shown on the Explorer as supply-limited runs, with labels, and what should the withheld-note say instead of "awaiting Epoch AI"?

## 2. Runs (fixed before the run)

The M2 slice (`f3/sectors/slice_m2.py`): S3 under R3 (fitted defaults) + data-centre module + supply limit on + damage, with the recorded 841-member FaIR replay (`climate841.npz`), step 0.25 year, 2025 to 2100. **Three settings** = the three shipped GATE parameter sets of D-005 amendment B (B0 default, B1 conservative, B2 aggressive: `T_oom`, `r_H`, `r_S`; `tests/s3_checks.SETTINGS_B`), **four damage options** (off, low, central, high): 12 runs. Module parameters as committed (PUE 1.4, 5% supply cap, calibration 485 TWh in 2025). After D-055 is implemented the same 12 runs are repeated with the efficiency cap ON (`--cap`, 4e15 FLOP/J) and the two sets of results are reported side by side.

**Quantities, by decade** (2025, 2030, then every decade to 2100; values at 1 January of the year, loop boundary `t = Y`; S3's flows at a boundary are the year just ended): output `gwp` (USD/year), compute stock `Q` (FLOP/year), effective compute `g(Q) x S` (eFLOP/year), electricity used `e_dc` and demand `e_dc_demand` (TWh/year), `supply_ratio`, available electricity `dc_available`.

## 3. Bounds and rules, written before any result

| quantity | bound (source) | "inside" means | note |
|---|---|---|---|
| usable compute `g(Q)` | `C_L = 2e38` FLOP/year (paper, D.3.2) | `g(Q) <= C_L` in every year | true by construction of eq. 10; reported |
| raw compute stock `Q` | `C_L` (the physical limit on a flow of FLOP/year) | `Q <= C_L` in every year | `Q` is not capped by the model (GATE's own stored run exceeds it by seven orders) |
| effective compute | none given by the paper | reported as ratio to `C_L`; no verdict | it is in eFLOP and carries the software factor `S` (up to 1e4) |
| electricity used `e_dc` | (a) 5% of supply (the module's own cap, D-033); (b) today's world energy use, 5e20 J = about 1.39e5 TWh/year (paper, D.3.2); (c) the IEA 2030 projection of 950 TWh | (a) and (b) in every year; (c) in 2030 within a **factor of 3** of 950 (317 to 2,850 TWh) | (c) is a **reading band, not a validation**: the 950 TWh is the IEA's projection under its own assumptions, and I did not verify the IEA's other scenarios, so the width is my choice, fixed here |
| electricity demand `e_dc_demand` | the available electricity `dc_available` | reported: first year demand exceeds available (the limit binds) | demand is unlimited by design; a verdict "outside" only if it exceeds 5e20 J |
| output `gwp` | **none in the paper.** Reference: Earth4All.jl TLTL recorded GDP (`tests/fixtures/e4a_signals_tltl.csv`, a different model, not truth) | `gwp` within a **factor of 10** of the Earth4All GDP of the same year, in every decade | factor and reference fixed here; the reference is another model's recording, not an observation |
| `supply_ratio` | in [0, 1] by construction | reported: first year below 0.5 and below 0.1 | diagnostic of how far the limit throttles S3 |

**Verdict classes per quantity** (across all 12 runs and all decades): **INSIDE** (every decade, every run); **OUTSIDE** (with the first year, run and size); **CAP-DETERMINED** (inside its bound only because the supply cap binds: used electricity equal to 5% of supply from the first binding year on, to 1e-9; in that case the quantity measures the cap, not the model).

**Rule for the Explorer** (applied to the results afterwards, not chosen after seeing them): a quantity **could be shown as a supply-limited run, with labels,** only if it is INSIDE in every run and every decade **and** not CAP-DETERMINED. A quantity that is INSIDE only through the cap **could be shown only as "cap-determined"**, with that label and the cap's assumptions (5% share, tie to S3's hardware curve). Anything OUTSIDE stays withheld. Whatever is shown keeps the S3 label (unvalidated against GATE after about 2027, D-029) and the shape-only notice. **The site is not changed in this step**; this section only states what could be shown and proposes the wording of the withheld note.

## 4. What this cannot say

That any bound is a prediction or a limit the world respects; that "inside" means "validated" (S3's level is unvalidated, D-029; the supply series is Earth4All's TLTL, one scenario); that the 5% share is right (an assumption, D-033, P-A2). It says only which numbers stay inside which stated bounds when the module's own limit is on.

## 5. Results

(to be added after the run, in a dated section)
