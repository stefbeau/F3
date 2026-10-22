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

## 5. Results, cap OFF (run 2026-10-22; 12 runs; figures in `audit/data/s3-supply-limited.json`)

Sections 1 to 4 were not changed after the run. The module is as committed (no efficiency cap; see D-055 and section 6). Values are at 1 January of the year (loop boundary). Damage option central is shown; off, low and high are in the JSON (the damage options change `gwp` by 1.0, 0.97, 0.956 and 0.874 of the off run in 2100 for B0, and move nothing else visibly).

| | 2025 | 2030 | 2040 | 2050 | 2070 | 2100 |
|---|---|---|---|---|---|---|
| **B0 default** output `gwp` (USD/year) | 1.10e14 | 1.90e14 | 4.00e14 | 8.92e14 | 2.51e15 | 5.92e15 |
| compute stock `Q` (FLOP/year) | 1.01e28 | 5.57e30 | 8.31e32 | 1.11e34 | 3.44e35 | 5.17e36 |
| effective compute (eFLOP/year) | 1.00e28 | 3.62e32 | 3.17e35 | 9.71e36 | 7.76e38 | 2.30e40 |
| electricity **demand** (TWh/year) | 485 | 2.00e4 | 4.14e5 | 9.80e5 | 4.80e6 | 1.37e7 |
| electricity **used** (TWh/year) | 485 | 1,748 | 2,090 | 2,231 | 2,350 | 1,763 |
| `supply_ratio` | 1 | 0.087 | 0.0051 | 0.0023 | 0.00049 | 0.00013 |
| **B1 conservative** `gwp` | 1.10e14 | 1.58e14 | 2.00e14 | 2.60e14 | 5.69e14 | 1.12e15 |
| `Q` | 1.01e28 | 4.53e30 | 3.22e32 | 1.51e33 | 5.37e33 | 1.30e34 |
| effective compute | 1.00e28 | 2.15e32 | 7.15e34 | 7.07e35 | 5.79e36 | 2.78e37 |
| demand | 485 | 2.28e4 | 6.38e5 | 1.48e6 | 2.02e6 | 1.93e6 |
| `supply_ratio` | 1 | 0.077 | 0.0033 | 0.0015 | 0.0012 | 0.00091 |
| **B2 aggressive** `gwp` | 1.10e14 | 3.46e14 | 5.58e14 | 9.99e14 | 2.84e15 | 7.14e15 |
| `Q` | 1.01e28 | 6.82e30 | 1.61e33 | 2.05e34 | 4.83e35 | 8.55e36 |
| effective compute | 1.00e28 | 7.74e32 | 1.74e36 | 5.60e37 | 2.96e39 | 7.34e40 |
| demand | 485 | 2.46e4 | 8.03e5 | 1.98e6 | 5.01e6 | 1.58e7 |
| `supply_ratio` | 1 | 0.071 | 0.0026 | 0.0011 | 0.00047 | 0.00011 |

Electricity **used** is the same in all 12 runs (1,748 TWh in 2030, 2,231 in 2050, 1,763 in 2100): it is 5% of the Earth4All TLTL supply, whatever S3 does.

### 5.1 Verdicts by the pre-registered table (all 12 runs, every decade)

| quantity | bound | verdict | detail |
|---|---|---|---|
| usable compute `g(Q)` | `<= C_L` | **INSIDE** (by construction) | 12 of 12 |
| raw stock `Q` | `<= C_L` | **INSIDE, through the throttle** | max `Q / C_L` is 0.027 (B0), 7e-5 (B1), 0.045 (B2). *Reading beyond the pre-registered wording, labelled so:* the unlimited R1 run of `docs/s3-diagnostic.md` reached `Q / C_L` of 76 (B0), so `Q` is inside **only because the supply limit throttles S3** |
| effective compute | none | **NO VERDICT** | as a ratio to `C_L` (units differ: eFLOP against FLOP) it is 0.15 (B1), 121 (B0) and 385 (B2) at its maximum |
| electricity **used** | (a) 5% of supply; (b) today's world energy use, 1.39e5 TWh; (c) IEA 2030 within a factor of 3 | **INSIDE on all three, and CAP-DETERMINED** (12 of 12 runs: used equals 5% of supply to 1e-9 wherever the limit binds) | used 2030 is 1,748 TWh, 1.84 times the IEA's 950 TWh projection, inside the factor-3 band **only because it equals the assumed cap**; it measures the 5% assumption (D-033), not S3 or the module |
| electricity **demand** | not above today's world energy use | **OUTSIDE** | demand passes the available electricity in **2027** and today's world energy use in **2032 to 2034**; its maximum is 15 (B1), 103 (B0) and 118 (B2) times today's world energy use; 2030 demand is 21 to 26 times the IEA's 950 TWh |
| output `gwp` | within a factor of 10 of Earth4All GDP in every decade | **OUTSIDE in 8 of 12 runs** | B1 stays inside in every decade (ratio 0.85 to 3.5); B0 first leaves in 2080 (18.3 times in 2100) and B2 in 2070 (22.1 times in 2100). The reference is another model's recording, so this verdict is weak |
| `supply_ratio` | in [0, 1] | reported | below 0.5 from **2027**, below 0.1 from **2029**, below 0.01 by 2040 in all three settings; minimum 1.1e-4 to 8.7e-4 |
| finiteness | no NaN | all 12 runs finite | |

### 5.2 What this says

1. **With the supply limit on, S3 is throttled to a fraction of its installed compute from 2027** and to under 1% by 2040: what S3 actually computes is `supply_ratio` times the stock. The "compute stock" is **installed** compute, 99% or more idle after 2040; it is not used compute.
2. **The one quantity the module reports as an output, electricity used, is the assumed cap, not a result.** The module's own physical information is in the **demand**, and demand is outside every bound.
3. **S3's output is still outside the Earth4All range in two of the three settings** (18 and 22 times Earth4All's GDP in 2100), mainly through effective compute (software and hardware efficiency), which the supply limit does not throttle in the same way: effective compute is `g(Q) x S` with `S` up to 1e4.
4. **The hand check of D-055 holds in this data:** nothing here required the efficiency cap to be on; see section 6.

### 5.3 What could be shown on the Explorer (rule of section 3, applied after the results; the site is not changed)

- **Not shown (OUTSIDE or no verdict):** electricity demand; effective compute; output `gwp` (inside only in the conservative setting).
- **Quantities that satisfy the rule only as "cap-determined / throttle-determined":** electricity **used** (flat at the assumed share of supply), raw stock `Q`, and `supply_ratio`. If any is shown it must carry that label and the cap's assumptions (5% share, D-033; tie of efficiency to S3's hardware curve) and the S3 label (unvalidated against GATE after about 2027, D-029). **My recommendation: do not show electricity used or `Q` as curves**, because each would present an assumption or a throttle as a result; the single honest quantity is `supply_ratio` (how hard the assumed cap throttles S3: 0.09 in 2030, below 0.01 by 2040), and only as a labelled diagnostic of the cap. This is a recommendation; the editor decides.
- **Proposed replacement for the withheld note** (instead of "awaiting Epoch AI"; the editor already wrote to Epoch on 2026-10-17 and F3 is not waiting for it): *"Compute and electricity outputs are withheld. Without a supply limit they leave any physical range, as Epoch's own GATE run does; with the supply limit on, electricity used is simply the assumed 5% share of supply, and S3 runs on under 10% of its installed compute from 2029 and under 1% by 2040. They would be shown only with those labels, and S3's output is unvalidated against GATE after about 2027."* Proposed text only; no site file was changed.

### 5.4 Limits

One electricity supply scenario (Earth4All TLTL); one cap share (5%, an assumption, D-033); the damage options barely differ because the climate is replayed and the damage fraction is small until late; S3's output verdict rests on another model's recording as reference; the bounds are mine (fixed before the run), not the paper's, except `C_L` and the 5e20 J figures. Nothing was adjusted after seeing a result.

## 6. Results with the efficiency cap (D-055; run 2026-10-22; figures in `audit/data/s3-supply-limited-cap.json`)

The same 12 runs (three settings, four damage options) with `DCParams(eta_cap = 4e15 FLOP/J)`, the paper's value. **The result is identical to section 5**: the maximum relative difference over 12 runs x 9 decades x every reported quantity is exactly 0, and every check of the table in section 3 has the same verdict. **The paper's cap never binds in this configuration.**

Why (hand check, written in D-055 before the run, and confirmed by it): `eta_0` is 8.06e9 FLOP/J (485 TWh in 2025 at 1e28 FLOP/year, PUE 1.4). `eta` scales with S3's hardware efficiency, which S3 caps at `H_max = 1e23`, 1e5 times its starting value, so `eta` cannot exceed 8.06e14 FLOP/J, a factor 5 below the cap. The tests (`tests/test_dc_eta_cap.py`) confirm the cap is respected when it is set low enough to bind, and that it then **raises** demand (demand is compute divided by `eta`); a cap at the paper's value would bind only if hardware efficiency were allowed to pass about 5e5 times its 2025 value.

**What this means.** The cap is a correct, switchable physical bound and it is in place, but **it removes none of the implausibility**: the implausible electricity demand does not come from the module's `eta` running above the physical limit. It comes from the compute stock `Q` (up to 5e36 FLOP/year in 2100 for B0, a factor of 3e5 above its 2025 value) divided by an `eta` that has already risen 1e5-fold with S3's hardware efficiency: demand of 1.4e7 TWh a year in 2100 is the product of those two S3 outputs. The cap would matter only if S3's hardware efficiency were allowed beyond `H_max`. So the earlier arithmetic note of `docs/s3-diagnostic.md` 3.4 (capping the input does not bound electricity) has a companion: **capping `eta` at the paper's value does not bound it either**; electricity demand stays outside the bounds of section 3 in the same years, and only the supply limit (5% of supply, an assumption) holds the electricity **used**.

Nothing was tuned. A tighter cap (a value below the paper's) would be a new coefficient and an editor decision.
