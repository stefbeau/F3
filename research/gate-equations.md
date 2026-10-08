# GATE: equations, default parameters and what the playground can export (M1, test A1.1)

**Status:** written 2026-10-08 for step 1 of M1 (`docs/phase-2-plan.md`, A1.1), under D-005 as approved with its amendment. **This is an extraction and an inventory. No code was written and no comparison was run.** The comparison tests A1.3 to A1.6 have not started.

**Sources and how they were read.**
- The paper: Erdil et al., *GATE: An Integrated Assessment Model for AI Automation*, arXiv:2503.04941 **v2** (12 March 2025), licence CC BY 4.0. Its HTML text was downloaded to a scratch folder outside the repository (sha256 `deb9c636f078c75cdb4ab685bd3de24766b3c94a50b80072d5238a7d11ee8a6e`, 732,052 bytes) and read directly, equations 1 to 37 and Appendix D included. Equations are paraphrased in plain text here, with their paper numbers; **the exact forms must be taken from the paper**, not from this file.
- The playground page https://epoch.ai/gate and the script bundle it loads (https://epoch.ai/generated/gate.js, 3,167,570 bytes, sha256 `3afe8e4df5260ee062d987ce38a984fc37b488b6dcb5596a317b1fde106c55bf`, fetched 2026-10-08). Epoch states that its work is "free to use, distribute, and reproduce" with credit, "under the Creative Commons Attribution license"; **no software licence is stated for the bundle, so no code from it is copied or reused** (the bundle includes a compiled solver, which F3 does not use). What was read from it is *data the page embeds*: its parameter table, and three precomputed runs. These are Epoch's figures (credit: Epoch AI, CC BY) and are **not stored in the repository**; `audit/t0/gate_playground_probe.py` prints them from a copy of the bundle.
- Epoch's two posts (announcing GATE, and "AI and explosive growth redux"), read earlier for the D-005 amendment.

## 1. Answer to A1.1 in one paragraph

**The playground can be inspected by fetch, and it cannot export what A1.3 needs.** It can *show* any run the user sets (a compiled solver runs in the browser), and it can **download the parameter set** as a JSON file (`epoch-gate-parameters.json`), **upload** one, and **download a chart as a PNG image**. **It has no CSV or series download: the script contains no code that writes the result series to a file.** The only machine-readable result series that can be obtained are the **three precomputed runs embedded in the page's script** (the playground's default, "conservative" and "aggressive" presets), each with 80 yearly states and the series A1.3 compares, stored to about 16 significant digits. Any other parameter setting, including the approved **Settings 1 and 2** (T = 1e41 with λ = 0.25; T = 1e33 with λ = 1), **can be run in the browser but only read off charts or PNGs, which cannot support the ±2% at three significant figures that the amendment requires**. Consequences are in section 6. **I cannot run the playground's interactive part by fetch** (it needs a browser); everything below about the three shipped runs was read from the data in the script.

## 2. The model as the paper states it

Time is continuous in the equations and discretised at one year in the solver (Appendix C: "discretize time at a resolution of 1 year"; planning horizon "typically set at 80 periods"; optimisation horizon a multiple of it). Initial conditions are "at the start of 2025" (Appendix D). The solution is the optimum of a social planner (equations 19 to 24, gradient descent); **D-005's behavioural rule replaces that optimisation, so equations 19 to 24 and Appendix C are not ported.**

### 2.1 AI development module (Section 3)

| Eq. | Content (plain text) | Notes |
|---|---|---|
| 1 | The largest training run grows by the effective compute spent on training: `dC_T/dt = D(t)` | continuous training |
| 2 | Total capability with inference: `C_{T+ι} = C_T × ι^(1/m)`, with `ι` between its bounds and `ι_max` the maximum | `m` is the training-inference trade-off slope; "no downside to choosing ι = ι_max" |
| 3 | Cost per effective FLOP/year `= 1 / (H(t) S(t))` | `H` hardware efficiency (FLOP/year/$), `S` software efficiency (eFLOP/FLOP) |
| 4 | `Ḣ/H = θ_H H^(-φ_H) I_H^RD^(λ_H)`; `Ṡ/S = θ_S S^(-φ_S) I_S^RD^(λ_S)` | R&D laws; `θ` productivity, `φ` fishing-out exponent, `λ` returns to R&D investment |
| 5, 6 | With ceilings: `Ḣ/H = g_H(t) Λ_H(H)`, `Λ_H = (log H_max − log H)/(log H_max − log H(0))`, same for software | `g(t)` the underlying growth potential from eq. 4 |
| 7 | Adjustment cost of expanding the compute stock: `I_Q = (Q/(χ a_Q H)) · ((a_Q I_q H / Q + 1)^χ − 1)` | `χ` exponent (default 4), `a_Q` timescale (2 years) |
| 8 | Compute stock: `Q̇ = I_q H − δ_Q Q` | `δ_Q` depreciation, 0.3/year |
| 9, 10 | **Usable compute** `Q̃ = g(Q)`, with `g(Q) = Q / (Q/C_L + 1)` | `C_L` = 2e38 FLOP/year; **`g(Q)` saturates at `C_L`; the raw stock `Q` and effective compute are not capped** (the D-005 A1.5(d) correction) |
| 11 | Initial effective compute `C(0) = Q̃(0) S(0)`, with `S(0) = 1` | |
| 12 | `Ċ = C Ṡ/S − δ_Q C + I_q H S` | valid when `Q ≪ C_L`; footnote 11 says that near or above `C_L` "the law of motion must be adjusted to incorporate `Ċ = g(Q) × S` (plus appropriate product-rule terms)" and **does not give the adjusted law** |

### 2.2 Automation module (Section 4)

| Eq. | Content | Notes |
|---|---|---|
| 13 | Fraction of tasks automated: `f = f_init` if `C_{T+ι} ≤ T/10^Δ_FLOP`; `f = f_init + (1 − f_init)(log C_{T+ι} − log(T/10^Δ_FLOP)) / (log T − log(T/10^Δ_FLOP))` in between; `f = 1` if `C_{T+ι} > T` | `T` AGI training requirement; `Δ_FLOP` in OOMs |
| 14 | Digital workers on task `i`: `N_i = C_{I,i} / R_i` | `C_{I,i}` runtime compute allocated to task `i` |
| 15 | Runtime requirement: `R_i = max(1, f^{-1}(i)/C_T)^m × 10^(γ_0 + γ_1 i)` | task-specific multiplier times minimum runtime cost; `f^{-1}` inverse of `f` |
| 16 | `f^{-1}(i)` defined piecewise (0 below `f_init`, the infimum compute reaching `i`, infinity above the supremum) | |
| 17, 18 | Labour: `L(t) = L(0) e^{g_L t}` (perfect reallocation, the default) or per-task `L_i(t) = L_i(0) e^{g_L t}` (no reallocation) | |

### 2.3 Macroeconomics module (Section 5)

| Eq. | Content | Notes |
|---|---|---|
| 19 | Planner's objective: `max ∫ e^{−(β − g_L)t} (c^{1−η} − 1)/(1 − η) dt` | **replaced by a behavioural rule in F3 (D-005)** |
| 20 to 24 | Resource constraints: non-negativity; no runtime compute on non-automated tasks; labour adding up; `D + ∫ C_{I,i} ≤ C`; `L c + I_Q + I_H^RD + I_S^RD + I_K ≤ Y` | the last is the output allocation |
| 25 | Output `Y = A T^{1−α−μ} K^α F^μ`, `A` constant (no TFP growth) | `α` capital elasticity, `μ` non-accumulable factor elasticity |
| 26 | Task composite `T = (∫ T_i^ρ di)^{1/ρ}`, `ρ < 0` | CES, constant returns; `ρ` the substitution parameter |
| 27, 28 | `T_i = L_i + N_i` for automated tasks, `L_i` otherwise; output `Y = A ( ∫_0^f (L_i+N_i)^ρ di + ∫_f^1 L_i^ρ di )^{(1−α−μ)/ρ} K^α F^μ` | |
| 29, 30 | Capital: `I_K = I_k + a_K I_k² / (2K)`; `K̇ = I_k − δ_K K` | |

### 2.4 Add-ons (Section 6) and their parameters

R&D externalities (eqs. 31, 32: the planner sees `I/ξ`, with `ξ` the wedge); uncertainty over automation functions (eqs. 33 to 36); labour reallocation frictions (eq. 18). The approved scope of S3 does not include the add-ons unless M1's report says so; their defaults are listed in section 3 for completeness.

### 2.5 What the paper does not give (needed before any code)

1. The **adjusted law of motion for effective compute when `Q` approaches `C_L`** (footnote 11 says one is needed and does not state it).
2. The **mapping from the planner's choices to the series the playground stores** (for example `compute` and `oom_compute` are stored; usable compute `g(Q)` and the raw stock `Q` are **not** stored under any name).
3. How **effective compute `C` is split** between training `D` and runtime `C_I,i` is a planner choice; S3's behavioural rule must supply it.
4. **TFP `A`** is "constant"; its value is not stated (it scales output; the stored first-year output is 1.19 times the parameter `Y(0)`).
5. The value of **`F(0)`** (non-accumulable factor): 1 trillion in the text, 11 trillion in one table.
6. **`a_Q` versus the playground's "adjustment timescale"** and the exact definition of `a_K`, `a_Q` in code units.

## 3. Default parameters (paper's Appendix D, and the playground's own table)

Two sources give defaults: the paper's tables and the playground's embedded table (which also gives the two presets and its own limits). They agree on most and disagree on a few; where they disagree both are given. "Soft" limits are the playground's recommended range; "hard" limits are what it accepts.

| Parameter | Symbol | Paper default (range) | Playground default | Playground soft range | Playground "conservative" / "aggressive" | Units |
|---|---|---|---|---|---|---|
| AGI training requirement | `T` | 1e36.5 (1e33 to 1e41) | 36.5 (OOM) | 31 to 41 | **38 / 33** | eFLOP |
| FLOP gap fraction | `Δf` | 0.55 table, 0.52 in heading (0.4 to 0.8) | 55 (%) | 40 to 80 | 55 / 55 | |
| Initial automated fraction | `f_init` | 0.1 (0.05 to 0.2) | 0.1 (hidden) | 0.05 to 0.2 | same | |
| Max inference multiplier | `ι_max` | 1e5 (1e3 to 1e7) | 5 (OOM) | 2 to 6 | same | |
| Inference-training slope | `m` | 2 (1 to 4) | 2 | 1 to 4 | same | |
| Runtime compute requirement | `10^γ_0` | 1e15 (1e13 to 1e17) | 15 (OOM) | 13 to 17 | same | FLOP/year |
| Task-level slope | `γ_1` | 9 (7 to 11) | 9 | 7 to 11 | same | |
| Initial runtime compute | `C_I(0)` | 1e28 (1e27 to 1e29) | 1e28 | 1e27 to 1e29 | same | eFLOP/year |
| Compute adjustment exponent | `χ` | 4 (3 to 5) | 4 | 3 to 5 | same | |
| Compute adjustment timescale | `α_Q` | 2 (1 to 4) | 2 | 1 to 4 | same | years |
| Compute depreciation | `δ_Q` | 0.3/year (bullet only) | 30 (%/year) | 20 to 50 | same | |
| Physical compute limit | `C_L` | 2e38 (8.6e34 to 5e41) | 2e38 | 8.6e34 to 5e41 | same | FLOP/year |
| Initial largest training run | `C_T(0)` | 5e25 (2e25 to 2e26) | 5e25 | 2e25 to 2e26 | same | eFLOP |
| Initial compute investment | `I_Q(0)` | 2e11 (5e10 to 8e11) | 2e11 | 5e10 to 8e11 | same | USD/year |
| **Hardware R&D returns** (ratio `λ_H/φ_H` as the playground names it) | `r_H` | 5.2 | 5.2 | 0.12 to 7.1 | **1 / 7.1** | |
| Returns to scale in hardware R&D | `λ_H` | **0.14** (table range 0.0625 to 1; text range 0.25 to 1) | 0.14 | 0.0625 to 1 | same (0.14 / 0.14) | |
| Hardware R&D elasticity | `γ_H` | 0.35 | 0.35 | 0.1 to 1 | same | |
| Maximum hardware efficiency | `H_max` | 1e23 (1e21 to 1e25) | 1e23 | 1e21 to 1e25 | same | FLOP/year/$ |
| Initial hardware efficiency | `H(0)` | 1e18 (1e17 to 1e19) | 1e18 | 1e17 to 1e19 | same | |
| Initial hardware R&D input | `I_H(0)` | 1e11 (1e10 to 1e12) | 1e11 | 1e10 to 1e12 | same | USD/year |
| Initial hardware growth | `g_H(0)` | 27.5%/year | 27.5 | 17.5 to 45 | same | |
| **Software R&D returns** | `r_S` | 1.25 | 1.25 | 0.5 to 6 | **1 / 2** | |
| Returns to scale in software R&D | `λ_S` | **text 0.14; table "0.14 to 1 (0.0625)"** | **0.14** | 0.0625 to 1 | same (0.14 / 0.14) | |
| Software R&D elasticity | `γ_S` | 0.35 | 0.35 | 0.35 | same | |
| Maximum software efficiency | `S_max` | 1e4 table, 1e5 bullet (50 to 1e8) | 1e4 | 1e2 to 1e12 | same | eFLOP/FLOP |
| Initial software R&D input | `I_S(0)` | 5e9 table, 1e10 heading (1e9 to 2.5e10) | 5e9 | 1e9 to 2.5e10 | same | USD/year |
| Initial software growth | `g_S(0)` | 70%/year | 70 | 25 to 100 | same | |
| Substitution parameter | `ρ` | -0.65 (-5 to -0.2) | -0.65 | -5 to -0.2 | same | |
| Capital elasticity | `α` | 0.35 (0.2 to 0.6) | 0.35 | 0.2 to 0.6 | same | |
| Non-accumulable elasticity | `μ` | 0 (0 to 0.3) | 0 | 0 to 1 | same | |
| Consumption discount rate | `β` | 5% (3% to 7%) | 5 | 3 to 7 | same | |
| Relative risk aversion | `η` | 1.45 table, 1.5 text (1 to 6) | 1.45 | 1 to 6 | same | |
| Initial GWP | `Y(0)` | 110 trillion table, 105 trillion in a bullet (105 to 115) | 110 | 105 to 115 | same | USD/year |
| Initial labour force | `L(0)` | 3.6 billion (3.4 to 3.8) | 3.6 | 3.4 to 3.8 | same | |
| Population growth | `g_L` | 0.25% (-1% to 2%) | 0.25 | -1 to 2 | same | |
| Initial capital | `K_0` | 450 trillion (200 trillion to 1 quadrillion) | 450 | 200 to 1000 | same | USD |
| Capital adjustment timescale | `α_K` | 1 (0.5 to 2) | 1 | 0.5 to 2 | same | years |
| Capital depreciation | `δ_K` | 6.5% (0.3% to 20%) | 6.5 | 0.3 to 20 | same | |
| R&D wedge (add-on) | `ξ` | 8 (2 to 20) | 8 | 1 to 20 | same (the shipped runs use 1: wedge off) | |

### 3.1 What the playground's table says about the λ ambiguity

**The playground's own code uses 0.14 as the default for both `λ_H` and `λ_S`**, which is the paper's text reading and the hardware table's, and not the software table's printed default of 0.0625. Its soft range for both is 0.0625 to 1, which equals the paper's hardware table range and the text's `0.25 × 0.25` low. This is the evidence the approved rule asks for ("if the playground shows its values, those decide"): **the working default 0.14 for both is the playground's value.** One more observation: the playground's presets do **not** change `λ`. They change **the returns ratios `r_H` and `r_S`** (hardware 5.2 to 1 or 7.1; software 1.25 to 1 or 2), which set the fishing-out exponents `φ = (λ/γ)/r` (with `λ/γ = 0.4`, `φ_H = 0.0769` at `r_H = 5.2` and `φ_S = 0.32` at `r_S = 1.25`, matching the paper's Appendix D), and `T`. This differs from the settings approved in D-005, which vary `λ` directly (see section 6).

## 4. The playground's inputs, outputs and actions

**Inputs.** 44 parameters in the embedded table (visibility: "Show", "Toggle" or "Hide"), with hard limits; the user may set any of them within the hard limits; solver behaviour at extreme values is not guaranteed (the paper says the "solution algorithm may not converge" and "our model playground will typically deliver an error warning"). Two presets are offered in the interface, named "conservative" and "aggressive" in the page's FAQ and parameter table. **The earlier search summary that the presets move only the AGI training requirement and the hardware and software R&D returns is now verified**: the three shipped runs differ only in `T`, `r_H` and `r_S` (section 3).

**Outputs shown.** Charts; the paper lists the variables in Section 7. The stored state per year has 31 fields (listed below).

**Actions.** (i) Download the parameter set (`epoch-gate-parameters.json`) and upload it; (ii) download a chart as a PNG (`epoch-gate-model-<chart>.png`); (iii) "Copy link"; (iv) compare two simulations side by side. **No action writes a result series to a file** (a text search of the 3.2 MB script found no CSV writer and three `new Blob(` sites: the JSON parameter download, the creation of the solver's web worker from an inline script, and no other; the chart download builds a PNG from the chart's SVG through a canvas data URL; an internal routine that regenerates the page's own results cache also uses the JSON download). The paper's Section 7 says users "can visualize and export these outputs"; **what "export" means there is the chart PNG and the parameter JSON, not the series, as far as the script shows.** This was not tried in a live browser.

**Solver as shipped.** In the three cached runs: `implementation` C++ (compiled, run in a web worker), `precision` fp64, `dt` = 1 year, `years_to_run` 80, `objective_horizon_multiplier` 2, solver method `sign_gradient_descent`, `maxiter` 40, `fun_tol` 0.02 (the stopping tolerance). **A tolerance of 0.02 on the objective, and a cap of 40 iterations, mean the shipped trajectories are not converged optima to machine precision;** that bears on how closely any re-implementation can be expected to match them (section 6).

**The shipped result series** (per run: 80 yearly states, index k = 0 to 79; fields): `time, consumption, gwp, q_hardware_rnd, q_software_rnd, capital, labor, training_compute, runtime_compute, compute, oom_compute, best_training_run, physical_best_training_run, hardware, software, frac_automated, compute_investment, effective_compute_investment, q_compute, q_capital, q_consumption, q_training_compute, q_runtime_compute, labor_share, capital_share, runtime_compute_share, ai_value, tobin_q_compute, compute_allocation, cognitive_ces_term, chip_fabrication_scale_up`. Stored precision: median 16 significant digits. **Not stored: the raw compute stock `Q`, usable compute `g(Q)`, hardware and software R&D spending in dollars (only their shares of output), and capital investment in dollars (only its share).**

## 5. What the shipped runs reveal about timing and about which equations the playground uses (identities tested)

These were tested **only to establish what the stored fields mean**; none is a comparison of F3 with GATE.

1. **Stored index k is the end of period k, 0-based.** Labour in the stored state k equals `L(0) e^{g_L (k+1)}` to 8e-15 in all 80 states (eq. 17 with elapsed time k + 1), and the stored index 0 is **not** the initial state: for example output at index 0 is 1.19 times the parameter `Y(0)`, hardware 1.60 times `H(0)`, software 8.4 times `S(0) = 1`, the largest training run 181 times `C_T(0)`. **So a comparison of S3 with the playground must compare at the end of each yearly period, after one period of dynamics, not at `t = 0`.** Hardware and software at index 0 were reproduced exactly (ratio 1.000000) from the paper's equation 4 with one period of constant growth at the rate implied by the first period's R&D share of output, which also confirms the equation form and the parameter reading `φ = (λ/γ)/r`.
2. **`frac_automated[k]` follows equations 13 and 2 evaluated on the largest training run stored at index k − 1**, to 1e-15 in all three runs (with the inference multiplier `10^(ι_oom/m) = 316` and `Δ_FLOP` taken as `Δf` times the OOM distance from the initial run to `T`). At k = 0 the initial run is used. So automation lags the training run by one period.
3. **The training-run recursions are exact:** `physical_best_training_run[k] = physical[k−1] + training_compute[k]` (deviation 0), and `best_training_run[k] = best[k−1] + training_compute[k] × S[k−1]` (deviation 0): effective training compute is accumulated at the *previous* period's software efficiency.
4. **Output shares sum to one** (2e-16); `q_training_compute = training/(training + runtime)` (3e-16).
5. **The default run is the run Epoch's posts describe:** the AI-related shares at index 0 (compute, hardware R&D and software R&D) total **24.0% of output** (matching the footnote "24% of GWP", not the blog's headline 20%); **growth 22.6% at k = 2** (the post's "23%/year" in 2027, so **k = 2 is 2027, which would make k = 0 the year 2025**, consistent with initial conditions at the start of 2025 and index k ending year 2025 + k) and automation of 0.318 at that point; growth first exceeds 20% at k = 2 with 31.8% automated (the post: "about 30%"); first exceeds 30% at k = 6 with 78% automated (the post: strict explosive growth "needs roughly 50-70% of tasks" automated: **this does not match** the shipped run, where growth is 28 to 30% at 46 to 69% automated and passes 30% only at 78%). So the shipped run matches Epoch's post figures in two respects (the 2027 growth rate and the 24% footnote share) and the 20% threshold in a third, and not the 30% threshold; the shipped run is a solver output with the tolerances above and may differ from what the live site shows.
6. **Not tied down by the paper or the identities:** equation 12 above `C_L` (section 2.5); the capital recursion (stored capital at index 0 is 0.9375 of `K_0`, which equals `K_0 (1 − δ_K)` plus a small investment, consistent with a period of depreciation and investment but not checked to precision); the allocation of effective compute between training and runtime.

## 6. What this means for the approved A1.3 to A1.6 (for the editor; nothing here changes an approved text)

1. **A1.3 can be run, on the data the playground ships, for the three shipped runs only.** They are the **default (Setting 0)** and the playground's two presets, which differ from the D-005 Settings 1 and 2 as follows:

   | | D-005 Setting 1 (slow) | Shipped "conservative" | D-005 Setting 2 (fast) | Shipped "aggressive" |
   |---|---|---|---|---|
   | `T` (OOM) | 41 | 38 | 33 | 33 |
   | `λ_H`, `λ_S` | 0.25, 0.25 | 0.14, 0.14 (unchanged) | 1, 1 | 0.14, 0.14 (unchanged) |
   | `r_H`, `r_S` (returns ratios) | 5.2, 1.25 (unchanged) | 1, 1 | 5.2, 1.25 (unchanged) | 7.1, 2 |

   **Setting 1 and Setting 2 as approved cannot be compared at three significant figures with anything the playground ships**, because the playground ships no run with `T` = 1e41 or with `λ` changed; the fast setting shares only `T` = 33 with the shipped aggressive run. They can be run in the playground in a browser (the playground accepts them: `T` 41 is the top of its soft range, `λ` 1 is the top of its soft range, 0.25 is inside it) but only charts and PNGs come out.
2. **What the editor may wish to decide** (not decided here): (a) accept the **three shipped runs** as the A1.3 settings (default, conservative, aggressive), which would be a change of the approved settings; (b) keep the approved Settings 1 and 2 and obtain their series by **running the playground in a browser and reading values** (precision limited by what the charts show; probably not three significant figures) or by asking Epoch for the series; (c) apply the **A1.6 fallback** (±10% against the published figures of the posts) for Settings 1 and 2, keeping A1.3 at ±2% for the default; (d) write to Epoch (info@epoch.ai, the address the playground gives for questions) asking for result series. **The approved rule for the λ ambiguity is already settled by the playground's own values (section 3.1).**
3. **Precision of the reference.** The shipped runs were produced with a solver tolerance of 0.02 and at most 40 iterations (section 4), and a one-period timing convention (section 5). The ±2% criterion of A1.3 applies to a re-implementation fed GATE's own investment path; with the path supplied the remaining differences are in the equations of the AI-development, automation and production blocks, which the identities of section 5 show can be matched closely for the pieces tested, but **whether ±2% is achievable for output and for effective compute near full automation (where the paper says GATE "behaves poorly") is unknown until tried.**
4. **A1.5(d) (corrected criterion).** The shipped runs include `physical_best_training_run`, which is the *physical* training run (the one capped by the physical limit) and `best_training_run` (effective). They diverge strongly (by k = 20 the effective run is 2e3 times the physical one), which is exactly the effective-versus-physical distinction the corrected A1.5(d) makes; **neither stored field is usable compute `g(Q)` or the raw stock `Q`**, so the A1.5(d) check on `g(Q)` has to be done on S3's own variables, not compared with stored GATE series.
5. **The behavioural investment rule** (D-005) can be fitted to the shipped investment shares (`q_consumption`, `q_compute`, `q_capital`, `q_hardware_rnd`, `q_software_rnd`, `q_training_compute`) for A1.4's report; those are stored for all three runs.

## 7. What was not done, and what is unverified

- **The playground was not operated in a browser.** Everything about its actions comes from reading its script; whether a "download" button for series is hidden behind a control, or whether the live site differs from the bundle read, was not checked. The editor may wish to confirm in a browser (see the checklist below).
- **The paper's Appendices B and C and Sections 6 and 8 to 9 were not read in full detail;** the add-on equations are listed by number only.
- The paper's remaining inconsistencies (section 3) are reported, not resolved.
- Epoch's posts disagree with each other and partly with the shipped run on the default's initial AI investment (20% against 24%) and on the automation level at which growth passes 30%.
- The licence of the playground code is not stated; no code was reused.

## 8. If the editor wishes to verify the playground in a browser (at most four things to look at)

1. Open https://epoch.ai/gate and run the **default** preset. Look for any control (button, menu, "..." or table view) that offers the **numbers** of a chart, a CSV, or a data download, and write down its name.
2. Set `T` to 41 (OOM) and both R&D returns ratios as they are; run, and look at whether the chart can show a **table of values** on hover or click, and to how many digits.
3. In the parameter panel, look at **"Returns to scale in hardware R&D"** and **"... software R&D"**: read their default values (the shipped table says 0.14 for both) and whether the panel lets you type exactly `0.25` and `1`.
4. Use the **download (↓) icon on the parameters panel** and check that `epoch-gate-parameters.json` contains the values you set; then try the **chart download icon** and confirm it gives an image, not data.
