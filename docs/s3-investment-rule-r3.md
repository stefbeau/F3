# S3 investment rule R3 (D-028): method and choices

**Status:** written 2026-10-12, **before** the curves were fitted and **before** any A1.4 run. D-028 (approved 2026-10-12) chose R3 with R1's fitted curves as the default calibration. S3's equations are untouched; the rule only generates the six shares per period. Evidence for the shape of the curves: `docs/s3-investment-rule.md` section 1.

## 1. What the rule is

`f3/sectors/s3_rule_r3.py` provides `R3Rule`, which S3 accepts as `S3AI(params, rule=R3Rule(...))` in place of the supplied path. At the start of period `k` S3 gives the rule two state variables it already has: the automated fraction of that period, `f_k` (from the largest training run at the end of the previous period, the one-period lag), and usable compute relative to the limit, `u = g(Q[k-1]) / C_L`. The rule returns the six shares: `q_compute`, `q_hardware_rnd`, `q_software_rnd`, `q_capital`, `q_training_compute`, and `q_consumption` as the remainder. If the five non-consumption shares sum to more than 1 they are scaled down together so consumption is 0; so the six shares are in [0, 1] and the first five sum to 1.

## 2. Default calibration: R1 curves fitted once to the three shipped runs

Fitted by `audit/t0/s3_r3_fit.py` from the shipped runs read at test time under D-026 (pinned bundle, hash checked). **Only the fitted curve tables are stored** (`f3/sectors/r3_curves.json`: a few knots per share, no series). The fit uses only stored fields, by name: `frac_automated`, `compute` (the raw stock `Q`, per `research/gate-equations.md` 9.1), and the six `q_*` shares; `u` for period `k` is `g(Q[k-1])/C_L` with `g` from eq. 10 and `Q[-1]` from eq. 11 (`C(0) = C_T(0) + C_I(0)`).

Fixed choices (nothing tuned afterwards):
1. **Indices 0 to 75** (2025 to 2100), the A1 window. The three shipped runs are pooled with equal weight.
2. **Two regimes.** *Automation regime*, `f_k < 0.999`: each share is a piecewise-linear function of `f` with knots at `f = 0.1, 0.3, 0.5, 0.7, 0.9`; the value at a knot is the equal-weight mean over runs of that run's mean share over its periods with `|f − knot| < 0.1` (a knot with no data in a run uses the other runs). *Full-automation regime*, `f_k ≥ 0.999`: each share is a piecewise-linear function of `log10 u` with knots at `log10 u = −5, −4, −3, −2, −1.5, −1, −0.5, −0.2`; the value at a knot is the equal-weight mean over runs of that run's mean share over its periods whose `log10 u` is nearest to that knot (bins split at the midpoints between knots; knots with no data in any run take the nearest filled knot's value). Outside the knots the end value is held.
3. **Joining the regimes.** For `0.9 < f < 1` the share is the linear blend between the `f = 0.9` knot value and the `u`-curve value at the current `u`, with weight `(f − 0.9)/0.1` on the `u`-curve; for `f ≥ 1` (within 1e-9 of it) the `u`-curve alone. This removes a jump; it is a choice, not a fitted feature.
4. **Shares fitted:** `q_compute`, `q_hardware_rnd`, `q_software_rnd`, `q_capital`, `q_training_compute`. Consumption is never fitted.
5. **In-sample.** The curves are fitted to the same three runs A1.4 compares with, so A1.4 shows how well three curves of `f` and `u` can represent these paths, **not** how well the rule predicts anything else.

## 3. Levers (scenario parameters; defaults reproduce the fitted curves exactly)

| lever | default | effect |
|---|---|---|
| `initial_ai_share` | fitted value of (compute + hardware R&D + software R&D) at `f = f_init` | rescales all three AI shares at every period by `initial_ai_share / fitted initial total`; `0` switches AI investment off |
| `decay_speed` | 1.0 | multiplies the three AI shares by `exp(−(decay_speed − 1) · 3 · p)`, `p = (f − f_init)/(1 − f_init)` clipped to [0, 1]: above 1 the AI share falls faster as automation proceeds |
| `split` (compute, hardware R&D, software R&D) | (1, 1, 1) | multiplies the three AI shares, then rescales them so their total is unchanged |
| `capital_scale` | 1.0 | multiplies the capital share |
| `training_scale` | 1.0 | multiplies the training share, clipped to [0, 1] |

The form of `decay_speed` (the constant 3, the dependence on `f`) is a design choice made now; the levers are meant for scenarios, not for improving agreement with the shipped runs.

## 4. A1.4 (report only, `audit/s3-r3-a1.4.md`)

Run 2025 to 2100 (indices 0 to 75) for the three shipped parameter settings, S3 variant A (the default D-027 leaves), driven by R3 with default levers. Per run and per quantity: the largest and the mean relative difference, and the first year each exceeds 5% and 10%. Quantities: the six shares (relative difference and, because several shipped shares are near zero, also the absolute difference in percentage points), S3's effective compute `g(Q)·S` against the reference `g(stored compute)·stored software` (**derived** from the stored fields with eq. 10, since effective compute is not stored; labelled so), the raw stock `Q` against stored `compute`, and output `gwp`. **Two row sets:** (a) the full chain with S3's own production composite (open difference, A1.3 failed); (b) the composite-independent quantities, with Epoch's stored composite `T` supplied to S3 period by period (a labelled diagnostic input, `stored_T`): compute stock, hardware, software, automation (and the shares). The report says which differences come from the rule and which from the open composite. **R3 is not tuned after seeing these numbers**; if they are poor they are reported as they are.

## 5. Other tests

R3 shares in [0, 1] and summing to 1 over a grid of states and extreme lever values; finiteness over 2025 to 2100; A1.5 on S3 driven by R3 for the three shipped parameter settings and the two stress settings (slow `T = 1e41, λ = 0.25`; fast `T = 1e33, λ = 1`), where R3 **replaces the placeholder path** used in `audit/s3-gate-comparison.md` section 5; a lever test (a higher `initial_ai_share` brings automation to 50% earlier).
