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
4. **A1.5(d) (corrected criterion).** *Correction of 2026-10-09: the first version of this item said that `physical_best_training_run` is "the one capped by the physical limit". That was an inference from the field name and was wrong.* Checked against the shipped runs: `physical_best_training_run` is the **cumulative raw training compute** (the initial run plus the sum of the stored `training_compute`, deviation 0 in all three runs), and `best_training_run` is the same sum weighted by the previous period's software efficiency. **Neither is capped by `C_L`**: the raw sum reaches 1.55 times `C_L` (3.1e38 against 2e38) in the conservative run, and stays below it in the default and aggressive runs (0.77 and 0.69 times), within the 80 shipped periods. **Neither is usable compute `g(Q)` or the raw stock `Q`**, and neither can be used to check A1.5(d); that check has to be made on S3's own variables. A related observation: the stored `compute` divided by the stored `software` (which would equal usable compute `g(Q)` if `compute` were `g(Q) S`, eq. 11) exceeds `C_L` by a factor of 31 at k = 30 and about 500 to 900 at k = 75 in the default run (6 to 600 in the other two). Since `g(Q)` cannot exceed `C_L`, **either the stored `compute` is not `g(Q) S`, or the playground does not cap effective compute as equations 9 to 11 and footnote 11 describe. This cannot be decided from the stored fields**, and it is a question for the comparison of effective compute (A1.3), not a settled fact. The usable-compute proxy `compute/software` first exceeds `C_L/11` (the point where `Q` would exceed 10% of `C_L` if `compute = g(Q) S`) at k = 24 (year 2049), 33 (2058) and 20 (2045) in the default, conservative and aggressive runs; this is a proxy under that unverified assumption.
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

## 9. S3 implementation choices (M1 step 2; written 2026-10-12, before any S3 code exists and before any comparison has been run)

**What this section is.** Section 5 identified what some stored fields mean. This section does the same for more of them, using **only the stored series** (no S3 code existed; nothing here is a comparison of F3 with GATE), and then fixes every choice S3 makes where the paper is silent. Pinned inputs: the bundle with sha256 `3afe8e4d…c55bf` (3,167,570 bytes, checked 2026-10-12) and the paper's HTML (v2, sha256 `deb9c636…8a6e`, re-read for equations 7 to 12 and footnote 11).

### 9.1 Measured identities on the stored fields (all three shipped runs; deviations are the largest relative difference over the 80 stored periods unless stated)

Notation: stored index `k` is the end of period `k` (section 5); `X[k-1]` is the previous stored value, and for `k = 0` it is the initial value from the run's parameter block.

| # | Identity | Deviation | Reading |
|---|---|---|---|
| 1 | **Stored `compute` is the raw compute stock `Q`, not effective compute `g(Q)·S`.** `Q[k] = Q[k-1]·exp(-δ_Q) + I_q[k]·H[k-1]`, with `I_q` the stored `effective_compute_investment` | 2e-16 | depreciation as an exponential over the year, the investment flow added in full and not depreciated within the year; `H` at the **start** of the period |
| 2 | Eq. 7 inverted: `I_Q[k] = Q[k-1]/(χ a_Q H[k-1]) · ((a_Q I_q[k] H[k-1]/Q[k-1] + 1)^χ − 1)`, with `I_Q[k] = q_compute[k]·gwp[k]` | 1e-15 | `I_q` follows from the dollars `I_Q`, with `Q` and `H` at the start of the period |
| 3 | **Usable compute is split between training and runtime:** `training_compute[k] + runtime_compute[k] = g(Q[k-1])`, with `Q(0)` such that `g(Q(0)) = C_T(0) + C_I(0) = 1.005e28` (eq. 11 with `S(0) = 1`); `training_compute[k] = q_training_compute[k]·g(Q[k-1])` | 5e-11 | **the apportionment of compute is an input (the stored share `q_training_compute`), the cap `g` acts on `Q`, and from the first period `Q` runs above `0.1·C_L` only late** |
| 4 | Capital: `I_K[k] = q_capital[k]·gwp[k]`; `I_K = I_k + a_K I_k²/(2 K[k-1])` (eq. 29), `K[k] = K[k-1]·exp(-δ_K) + I_k` (eq. 30 discretised like 1) | 3e-16 | |
| 5 | Hardware and software: `X[k] = X[k-1]·exp( θ_X · X[k-1]^(−φ_X) · I_X[k]^(λ_X) · Λ_X(X[k-1]) )`, `I_X[k] = q_X_rnd[k]·gwp[k]`, `θ_X = g_X(0) X(0)^(φ_X) I_X(0)^(−λ_X)`, `φ_X = (λ_X/γ_X)/r_X`; `Λ` of eq. 6 | 3e-16 until `X` is within 0.2% of its cap; then up to **1.8e-4 (H) and 5.6e-4 (S)** in the periods approaching the cap | growth rate held constant over the period, from the start-of-period state and the period's investment; the small gap near the cap is not explained |
| 6 | Output: `gwp[k] = A · T[k]^(1−α) · K[k-1]^α` with `T` the stored `cognitive_ces_term` and **`A = Y(0) / (L(0)^(1−α) K(0)^α) = 502.5412085…`** | 1e-15 | capital at the **start** of the period, labour at its stored period-end value `L(0) e^{g_L (k+1)}`; `A` is the value that makes `T = L` and output `Y(0)` with no automation. `μ = 0`, so `F` does not enter |
| 7 | `labor_share + capital_share + runtime_compute_share = 1`, `capital_share = α`, `q_training_compute = training/(training+runtime)` | 2e-16 | |
| 8 | Not identified: the composite `T` (the stored `cognitive_ces_term`) from `L`, `f`, the runtime compute and the largest training run. A reconstruction from the **stored per-task allocation** (`compute_allocation`, 101 entries per period; its sum is **not** the stored `runtime_compute`, ratio 1082 at k = 0 and 59 at k = 1) reproduces `T` to 3e-4 in the first two periods and drifts to a few percent after that | up to ~15% by k = 11 | I could not tell whether the drift is the grid the solver uses (the paper's footnote 38: 20 grid points for digital workers, 100 for humans and the CES integral, in an Appendix C passage that does not match the 101-entry stored grid), the stored allocation being a different iterate, or my reading. **Unresolved; reported, not tuned** |

### 9.2 Consequences for earlier statements (corrections, appended; the text above is not edited)

1. **Correction to section 6, item 4 and to the open point (2) of D-005 amendment B.** Item 4 said that stored `compute / software` exceeding `C_L` by 31 to 900 times late in the runs meant either that `compute` is not `g(Q)·S` or that the playground does not cap as eq. 10 describes, and that this could not be decided from the stored fields. **It can: identity 1 shows stored `compute` is the raw stock `Q`**, and `Q` is not capped by `C_L` (eq. 10 caps `g(Q)`, which identity 3 shows the playground applies to `Q` when it splits compute between training and runtime). So **that observation is not evidence that the playground contradicts eq. 10**, and the premise of the sentence the editor added to B ("the shipped series contradicts the paper's equation 10 (stored compute divided by software exceeds C_L)") **is not supported**. I have no evidence of the playground differing from the paper on eq. 10. The classification clause will therefore not be applied to anything that rests on that premise; if the comparison fails for another reason, the report says so. This is a finding for the editor, not a change of any approved text.
2. **B's quantity pairing "S3's effective compute against the stored `compute`" is not like for like.** The stored `compute` is `Q`. S3 therefore reports both its raw stock `Q` (`compute_stock`) and its effective compute `g(Q)·S` (`effective_compute`), and the comparison report shows **two rows against the stored `compute`**: (i) `compute_stock` (the identified pairing; labelled as such) and (ii) `effective_compute`, the pairing as B words it, which differs from `Q` by the factor `g(Q)·S/Q` (up to the order of `S_max = 1e4`) and cannot pass. Which row counts for the criterion is the editor's decision; **neither is relaxed**, both are reported.
3. **The timing, discretisation and calibration choices of 9.3 were identified from the very series S3 is then compared with.** For hardware, software, capital, compute stock, automation and output given `T`, a match is therefore close to **in-sample by construction** (it shows the pieces fit together over 76 periods, not that the paper alone determines them). The comparison is an independent test only of the production composite `T` (identity 8) and of the chain over 76 periods. The report says this next to its results.

### 9.3 Choices S3 makes (fixed now)

1. **One period is one year, advanced as a block** in the way identities 1 to 6 show. S3 runs inside the 0.25-year loop with `period = 1.0` (the interface's slow-sector mechanism, advanced every fourth step); the published value at `t = 2025 + k + 1` is the end of period `k` (stored index `k`). Stocks published at `t` are the values on that date; **flows (`gwp`, `training_compute`, `runtime_compute`) published at `t` are the totals rates over the period that just ended**, which is GATE's own annual convention and a labelling difference from D-022's "rate at that instant", recorded here and to be settled at M2 when S3 is coupled.
2. **Order inside a period `k`:** (a) automation `f_k = f(C_{T+ι}[k-1])`, with `C_{T+ι} = C_T·ι^(1/m)`, `ι = ι_max`; **the one-period lag of B**; (b) output from `L[k]`, `K[k-1]`, and the runtime compute `(1 − q_training)·g(Q[k-1])`; (c) investments from that output and the supplied shares; (d) `Q`, `H`, `S`, `K`, then the largest training run `C_T[k] = C_T[k-1] + training_compute[k]·S[k-1]` and the physical one `C_T,phys[k] = C_T,phys[k-1] + training_compute[k]`.
3. **Eq. 13: `Δ_FLOP = Δf · (log10 T − log10 C_T(0))` (in OOM).** The paper gives `Δ_FLOP` and the table gives `Δf` without stating the relation; this one reproduces the stored `frac_automated` to 1e-15 (section 5, item 2). Identified from the data, not stated in the paper.
4. **The law of motion near `C_L` (footnote 11), literally:** S3 does not integrate eq. 12. It evolves the raw stock `Q` with eq. 8 and takes **effective compute as `C = g(Q)·S`** (footnote 11's `Ċ = g(Q) × S` plus product-rule terms is what differentiating this gives); `g(Q) = Q/(Q/C_L + 1)` is evaluated as `C_L/(1 + C_L/Q)` (the same function; it cannot exceed `C_L` in floating point). **The cap acts on `g(Q)` only: `Q`, `S`, `C` and the largest training run are not capped** (D-005 A1.5(d), as corrected). `Q(0) = C(0)/(1 − C(0)/C_L)` with `C(0) = C_T(0) + C_I(0)`, `S(0) = 1` (eq. 11, identity 3).
5. **Hardware and software efficiency are capped at `H_max`, `S_max`** by `min(·, max)` after the update (the paper says efficiency "approaches" a maximum and that `Λ` stays between 0 and 1; an overshoot would make `Λ` negative, which the paper excludes). A choice; identity 5's small gap near the cap is not explained by it.
6. **Production block (identity 8 is the open point):** the continuous task space of eqs. 25 to 28 with the efficient allocation the paper's footnote 39 describes: given `L`, `f`, runtime compute `C_I` and `R_i` (eqs. 15, 16), labour and runtime compute are allocated across tasks to maximise `T = (∫ T_i^ρ di)^(1/ρ)`, `T_i = L_i + C_i/R_i` for `i ≤ f`, `T_i = L_i` for `i > f`. The solution has a threshold task `i*` below which tasks use compute only and above which labour only; `i* = f` with leftover compute when compute is abundant. Integrals are evaluated on **20,000 midpoints** (converged to better than 1e-4 in the quantities used). `R_i` uses `C_T[k-1]` (largest training run at the start of the period, with `C_T(0)` for `k = 0`) in `max(1, f⁻¹(i)/C_T)^m`. **S3 does not use the solver's grids** (20 and 100 points, footnote 38): that is a possible cause of a difference and is the first thing to try if the output comparison fails, but it is not done unless the editor decides, because it would be an equation change after seeing the data.
7. **`μ = 0` only** (`F` unspecified in the paper; section 2.5, item 5); S3 raises an error for `μ ≠ 0`. `A` as in identity 6. Labour is `L(0) e^{g_L t}` (eq. 17, perfect reallocation); the no-reallocation case (eq. 18) and the add-ons of Section 6 are not implemented.
8. **Inputs.** The investment path is supplied: six shares in `[0, 1]` per period (`q_consumption`, `q_compute`, `q_capital`, `q_hardware_rnd`, `q_software_rnd`, and the training share of usable compute `q_training_compute`); the first five must sum to 1. S3 has **no investment rule** (D-005; the editor chooses one after `docs/s3-investment-rule.md`). Consumption is carried only as the remainder of the output.
9. **Parameters:** the playground's defaults (`λ_H = λ_S = 0.14`; sections 3 and 3.1), with the three shipped settings of D-005 amendment B (`T`, `r_H`, `r_S`) and, for the two report-only stress settings, `λ` changed directly with `r_H = 5.2`, `r_S = 1.25` kept (so `φ = (λ/γ)/r` and `θ` are recomputed from the initial growth rates). The stress settings use a **placeholder** investment path: constant shares equal to the shipped default run's period-0 shares, with the training share held at 0.5; it is labelled as a placeholder everywhere, is **not** a behavioural rule, and the capital share it implies is small, so capital falls by depreciation in those runs.
10. **What is compared and how it is reported** (D-005 B, D-026): `gwp`, `capital`, `labor`, `hardware`, `software`, `frac_automated` by name; the two `compute` rows of 9.2, item 2; labour share and runtime-compute share as extra, report-only rows; the shares themselves are inputs and equal the stored ones by construction. ±2% relative at indices 0 to 75; two year groups by S3's own `Q` against `0.1·C_L`; largest differences and first year each criterion is exceeded; the sha256 and 'read at test time' wording of D-026. Only comparison figures are stored (`audit/data/s3-gate-comparison.json`); nothing from the bundle is committed.

## 10. Variant B of the production block (D-027, approved 2026-10-12; written before variant B code exists and before any variant B run)

**What B is.** The same problem as variant A (9.3, item 6): maximise `T = (∫ T_i^ρ di)^(1/ρ)` with `T_i = L_i + C_i/R_i` on automated tasks, `T_i = L_i` on the others, given labour `L` and runtime compute `C_I`, with `R_i` from eqs. 15 and 16 evaluated at `C_T[k-1]`. Only the discretisation changes, as the paper's footnote 38 states it: **20 grid points for the allocation of digital workers, 100 for the allocation of human workers and for the CES integral.** The footnote does not say how the two grids relate, so the scheme below is my reading; it is fixed now and is not tuned.

**Scheme.**
1. *Fine grid (humans and the CES integral):* 100 midpoints `x_j = (j + 0.5)/100`, `j = 0..99`, each with weight `w_j = 1/100` (midpoint rule). A fine task is *automated* iff `x_j ≤ f`.
2. *Coarse grid (digital workers):* 20 cells, cell `c` holding the 5 fine tasks `5c..5c+4`, cell weight `W_c = 1/20`. Compute is allocated per cell, as a density `C_c`, spread equally over the cell's fine tasks; `R_c` is eq. 15 at the cell midpoint `(c + 0.5)/20`. Digital workers per automated fine task in the cell: `N_c = C_c / R_c`. Compute used is `Σ_c W_c C_c = C_I`. Non-automated fine tasks in a cell get no compute.
3. *Humans:* free to move across the 100 fine tasks (perfect reallocation, eq. 17), `Σ_j w_j L_j = L`.
4. *Solution (exact for the discrete problem; no iteration, no tolerance):* let `A_c` = the weight of automated fine tasks in cell `c` and `R_eff,c = R_c W_c / A_c`; cells with `A_c = 0` get nothing. With `e = 1/(ρ − 1)`, optimal compute cells have `N_c = N* (R_eff,c / R_eff,m)^e`, labour on a task is `Th − N` where positive. Humans and compute are perfect substitutes within a task, so one *marginal* cell `m` (the sorted-by-`R_eff` position where compute runs out) may be partly filled, `0 ≤ N_m ≤ Th`. For the cheapest `k` cells in the set `S`, `a = Σ_S W_c R_c (R_eff,c/R_eff,m)^e`, `sA = Σ_S A_c`: `Th = (C_I + R_eff,m L)/(a + R_eff,m (1 − sA))`, `N_m = (Th (1 − sA) − L)/A_m`. The first `k` with `0 ≤ N_m ≤ Th` is taken. If compute is abundant (all cells `N_c = a0 R_eff,c^e` with `Σ W_c R_c N_c = C_I` and `Th = L/(1 − Σ A_c)`, and every `N_c ≥ Th`), that case is taken first. If no task is automated, `T = L`.
5. *Output:* `T = (Σ_j w_j T_j^ρ)^(1/ρ)` over the 100 fine tasks, with `T_j = max(Th, N_c)` on automated tasks in compute cells (`Th` for the marginal cell), `T_j = Th` elsewhere.
6. *Price ratio* (for the report-only income shares): `p/w = 1/R_eff,m`, or in the abundant case `(N_c/Th)^(ρ−1)/R_eff,c` at the dearest cell.

**The single named case of outcome (iii)** (tried only if B fails, once): one grid of 101 points `x_j = j/100`, `j = 0..100` (the size of the stored `compute_allocation`), trapezoid weights (0.005 at the two ends, 0.01 elsewhere), each point its own cell (`W_c = w_j`, `R_c` at `x_j`), the same solution method as above. No other grid size is tried.

**Implementation.** `GateParams.composite` = `"A"` (default; 20,000 midpoints; recorded as failed) or `"B"` (this section); `"C101"` exists only if outcome (iii) is reached. Nothing else in S3 changes. The A1.3 re-run uses the same criterion (±2%, indices 0 to 75, same quantities) and is added as a second labelled row in `audit/s3-gate-comparison.md` and `audit/data/s3-gate-comparison.json`.

**Correction to section 10, step 2 and step 4 (2026-10-12, before any variant B code or run).** Step 4 defined `R_eff,c = R_c W_c / A_c`. That was a slip: compute allocated to a cell is delivered equally to the cell's *automated* fine tasks, so per automated task the compute is `X_c / A_c` and `N_c = X_c / (A_c R_c)`; the cell weight cancels and **`R_eff = R_c`**. The solution therefore is: groups (one per coarse cell, or per point in the 101 case) with automated weight `A_c` (= number of automated fine tasks in the cell / 100) and cost `R_c`, sorted by `R_c` ascending; humans `L` free across all tasks. With `e = 1/(ρ − 1)`: cheaper groups than the marginal group `m` use compute only, `T_c = Th (R_c/R_m)^e`; the marginal group is mixed, `T = Th`, `N_m ≥ 0`; dearer groups and non-automated tasks use humans only, `T = Th`. With `s = Σ_{c<m} A_c` and `B = Σ_{c<m} A_c R_c (R_c/R_m)^e`: `Th = (C_I + R_m L)/(B + R_m (1 − s))`, `N_m = (Th (1 − s) − L)/A_m`, accepted for the first `m` with `0 ≤ N_m ≤ Th`. If compute is abundant (no marginal group: `T_c = κ R_c^e` for all automated groups, `Th = L/(1 − Σ A_c)`, `κ` from `Σ A_c R_c T_c = C_I`, and `κ R_c^e ≥ Th` for the dearest group) that case is taken first. `T = (Σ weights × T^ρ)^(1/ρ)` over the 100 fine tasks (or the 101 trapezoid points). Price ratio `p/w = 1/R_m` (abundant: `(κ/Th)^(1/e)`). Everything else in section 10 stands.

**Second correction to section 10 (2026-10-12; found when the first variant B run raised "no marginal group found"; no variant B comparison has been produced yet).** With finite-weight groups the solution can also be a **corner**: the `k` cheapest automated groups are compute-only, `T_c = κ R_c^e` with `κ = C_I / Σ_{c≤k} A_c R_c^(1+e)` (the budget), humans only on everything else (`Th = L/(1 − Σ_{c≤k} A_c)`), valid when `κ R_k^e ≥ Th` (group `k` really is compute-only) and `κ R_{k+1}^e ≤ Th` (buying compute for group `k+1` is not worth it: its price `λ R_{k+1}` is at least the human value). The compute price ratio is `p/w = (κ/Th)^(ρ−1)`. The abundant case is `k = n` with only the first condition. The mixed (marginal-group) case stays as written. The solver tries, in this order: abundant, then for `k = 1..n−1` the corner, then for `m = 0..n−1` the mixed case; the conditions are the first-order conditions of the same problem, so at most one case is valid (up to ties), and nothing is tuned.

**Third correction to section 10 (2026-10-12; degenerate case found in the first variant B run: `f = 1`, which gave `Th = L/(1 − ΣA)` = NaN; still no variant B comparison produced).** When every task is automated (`1 − ΣA ≤ 1e-12`) there is no human-only task, so the abundant case and the corner cases (which assume humans only on non-automated or dearer tasks) are not valid; only the mixed case applies, with the dearest group as a candidate marginal group (humans and compute then share it, `T = Th`). The solver skips the abundant case and the corner cases when `1 − cumA ≤ 1e-12` and goes to the mixed case. `ΣA` is clipped at 1. No equation or parameter changes.
