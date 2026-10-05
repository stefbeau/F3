# F3 — T0 findings (running log)

Factual record of what each T0 run showed. Updated after every run; nothing is deleted, only superseded.

## Run #6 (2026-10-05, F3 commit 4c33274)

### World3: WorldDynamics.jl (`NoInit()`, tight tolerance) vs PyWorld3 fine step (dt=0.05), max / mean gap
p1 0.95 / 0.45 % · p2 0.70 / 0.32 % · p3 0.67 / 0.23 % · p4 0.63 / 0.28 % · ic 1.95 / 0.82 % · sc 1.55 / 0.84 % · al 0.22 / 0.09 % · pal 0.53 / 0.19 % · uil 0.62 / 0.17 % · lfert 0.71 / 0.21 % · nr 1.15 / 0.33 % · pop (sum) 0.66 / 0.31 % · **ppol 373.70 / 22.65 % (max in 1906)**.
Eleven of the twelve stocks are within ±2% (ic at 1.95% is only just inside). **Persistent pollution (`ppol`) is not.** The three solver variants agree with each other, so this is not a solver-tolerance effect.

**D-013 acceptance condition (all twelve stocks within ±2% of fine-step PyWorld3) was NOT met.** D-013 therefore cannot be approved as written.

### Likely cause of the `ppol` gap (checked locally, hypothesis not yet confirmed on the WorldDynamics.jl data)
- PyWorld3 1.1 (`specials.py`) initializes its third-order delay `Delay3` at `input × 3 / delay`; its sibling `Dlinf3` initializes at the input (steady state). For the pollution-appearance delay (PPGR, delay 20 years) PyWorld3's delay output therefore starts at 15% of its input (1.57e6 vs 1.05e7 in 1900, ratio 0.150 = 3/20). Pollution then falls from 2.5e7 to a minimum of 5.0e6 (1906) before rising.
- WorldDynamics.jl starts the same delay chain at steady state (`ppapr3 = pptd × ppgr / 3`, cited as Line 141, Appendix A), so its pollution does not dip. The value implied by the run #6 gap for 1906 is about 2.43e7.
- **Diagnostic (not a reference):** a local PyWorld3 run (dt=0.05) with only that delay initialized at steady state gives `ppol` 2.22e7 in 1906 and no dip. Its gap to the unpatched run is 339.6% max / 20.2% mean, close to the 373.7% / 22.7% measured against WorldDynamics.jl. Effect of this single change on other stocks (max / mean): pop 0.19 / 0.11 %, ic 0.53 / 0.33 %, sc 0.43 / 0.32 %, lfert 0.64 / 0.13 %, nr 0.44 / 0.10 %.
- **What this does and does not explain:** most of the `ppol` gap; part of the 0.5–1% residuals elsewhere (the patched run moves them by 0.1–0.6%, the measured gaps are 0.2–1.95%). A remaining difference of roughly 9% in early `ppol` (2.43e7 vs 2.22e7) is not explained. Which initialization is faithful to the 1974 book has not been checked against the book itself.
- The comparison must be redone directly on the WorldDynamics.jl data (all stocks, early decades) before any conclusion is drawn.

### Offline analysis of the WorldDynamics.jl export (after run #6)
The `world3_worlddynamics_states_noinit_tight.csv` file from run #6 was compared with PyWorld3 (dt=0.05) run in three ways, changing only how PyWorld3's pollution-appearance delay is started (max % gap, in brackets the mean):

| stock | PyWorld3 as shipped | delay at steady state of its own ppgr(1900) | delay started at the WorldDynamics.jl value |
|---|---|---|---|
| p1 | 0.95 (0.45) | 0.81 (0.49) | 0.79 (0.50) |
| p2 | 0.70 (0.32) | 0.60 (0.37) | 0.59 (0.38) |
| p3 | 0.67 (0.23) | 0.53 (0.27) | 0.51 (0.27) |
| p4 | 0.63 (0.28) | 0.42 (0.15) | 0.39 (0.14) |
| ic | 1.95 (0.82) | 1.42 (0.49) | 1.36 (0.46) |
| sc | 1.55 (0.84) | 1.18 (0.52) | 1.14 (0.49) |
| al | 0.22 (0.09) | 0.09 (0.04) | 0.07 (0.04) |
| pal | 0.53 (0.19) | 0.26 (0.13) | 0.26 (0.13) |
| uil | 0.62 (0.17) | 0.32 (0.12) | 0.29 (0.11) |
| lfert | 0.71 (0.21) | 0.27 (0.09) | 0.26 (0.07) |
| **ppol** | **373.70 (22.65)** | **7.94 (1.26)** | **1.69 (0.54)** |
| nr | 1.15 (0.33) | 0.71 (0.23) | 0.67 (0.22) |
| pop (sum) | 0.66 (0.31) | 0.56 (0.37) | 0.55 (0.37) |

**Confirmed (causal test: only the start value of one delay was changed):** the `ppol` gap is a start-up difference of the pollution-appearance delay chain. With PyWorld3 started at the WorldDynamics.jl value, `ppol` is within 1.69% (largest in 2100) and all twelve stocks are within 1.4%.

**What the start values are** (PyWorld3 1.1 and WorldDynamics.jl v1.0.0 source and data):
- PyWorld3's own model value at 1900: ppgr = 1.0452e7. Its delay starts at 1.5679e6, which is 0.150 = 3/20 of that (code: `Delay3._init_out_arr` sets `input × 3 / delay`; the sibling `Dlinf3` sets `input`).
- WorldDynamics.jl starts the delay stages at ppapr3 = 7.5867e7, which implies ppgr = 1.1380e7. That equals the value computed from the **standalone pollution-sector tables** at 1900 (pcrum = 0.17, aiph = 6.6, population 1.6e9, arable land 9e8) rather than from the connected model (PyWorld3 gets pcrum = 0.1766 and aiph = 5.333 at 1900 from the other sectors). It is 8.9% above PyWorld3's own ppgr(1900).
- Neither start is the steady state of the model's own ppgr(1900): PyWorld3 is 85% below, WorldDynamics.jl is 8.9% above. With `NoInit()` the solver does not reconcile this (the consistency check it skips is the one that warned of an overdetermined initialization). Which start the 1974 book prescribes has not been checked against the book.

**Still unexplained:** residuals of up to about 0.8% in population cohorts, 1.4% in industrial capital and 1.1% in service capital remain with matching pollution start. They may come from similar start-up differences in other delay or smoothing chains (WorldDynamics.jl's `aiopc(1900)` is 41.30, PyWorld3's `iopc(1900)` is 41.56) but this was not tested.

**Consequence for F3 (design, not yet a decision):** a 1900 start-up convention matters little for F3 (it starts in 1970 from observed data and the delay's memory is 20 years), but it does matter for how the Python port is *tested*. Comparing two implementations with different start states mixes equation differences with initialization differences. Step 1.4 should test the port by starting it from the same state as the reference (the WorldDynamics.jl 1900 state, taken from the export) and checking the trajectory against the reference, with start-up conventions documented separately.

### Earth4All.jl vs Vensim (package's own `all_mre`, error = |julia − vensim| / (|vensim| + 1), maximum over 7,681 points)
| | Too Little Too Late | Giant Leap |
|---|---|---|
| variables compared | 487 | 487 |
| maximum error | 26.0 (*Desired renewable el capacity change GW*) | 20.0 (*Bank Cash Inflow from Lending GDollar/y*) |
| variables with error > 1e-3 / 1e-2 / 1e-1 | 274 / 119 / 8 | 276 / 123 / 22 |

Largest errors are mostly finance and energy flows, plus *CHange in WOrkforce Mp/y* (3.01 TLTL, 4.08 GL) and, in Giant Leap, several fossil-energy variables near 1.0. **Caution:** the metric takes the maximum over all time points, so a one-step timing offset of a switched input can dominate it. It does not say how large the typical error is. Per-variable median and 95th-percentile errors, and the year of the maximum, are needed before any conclusion about D-010/T2 (labour market) is drawn.
The run included the `all_mre` step (D-014) before D-014 had been explicitly approved; D-014 was approved afterwards (2026-10-05). The stored results contain variable names and error figures only.

### Status of Phase 1 step 1.1 (T0)
Not passed. Open: decide how D-013 proceeds (revised proposal in DECISIONS.md); Earth4All error statistics beyond the maximum (run #7 adds them); residual 1–2% gaps in capital stocks. D-014 was approved on 2026-10-05.

## Run #5 (2026-10-05, F3 commit c04f249)

### Confirmed
- **Solver variants (WorldDynamics.jl, `World3`):** default options → `InitialFailure`, 1 point; `NoInit()` → `Success` with 50 points; `NoInit()` + `saveat = 0.5` → 401 points; `NoInit()` + `saveat = 0.5` + tolerance 1e-8 → 401 points.
- **Population cross-check, all three usable variants** (max / mean): vs PyWorld3 dt=0.5: 0.91 / 0.43 %, 0.91 / 0.50 %, 0.97 / 0.53 %; vs PyWorld3 dt=0.05: 0.53 / 0.24 %, 0.54 / 0.25 %, 0.67 / 0.31 %. All within the ±2% band of D-004.
- **Both implementations are the 1974 World3 model.** WorldDynamics.jl's `World3` module reproduces *Dynamics of Growth in a Finite World* (README, Figure 7.7); PyWorld3 documents the same book. (WorldDynamics.jl also contains `World3_91` and `World3_03`, the 2004 update.) The like-for-like question from run #4 is answered.
- **The package's failing tests are for a different variant.** Its test suite covers `World3_03`, not the `World3` module audited here. Their failure (`BoundsError` on a 1-element vector) is consistent with the same initialization problem but was not verified for that variant.
- **Earth4All.jl ships Vensim reference output** (`VensimOutput/tltl` and `VensimOutput/gl`, twelve sector files each) and the two Vensim `.mdl` sources (`vensim_source/`). The package has its own numeric comparison function `Earth4All.all_mre(scenario, solution)` (error |julia − vensim| / (|vensim| + 1)), which is not wired into any test. Its README validates by visual comparison of figures. The audited commit is `16f37d0` (21 Sep 2026), licence MIT.

### My prediction that did not hold
Run #4 notes predicted that a tight-tolerance WorldDynamics.jl run would land within a few hundredths of a percent of fine-step PyWorld3. It did not: the tight run is slightly *farther* away (0.67%) than the loose ones (0.53%). So the remaining gap of about 0.5–0.7% in population is **not** explained by PyWorld3's step size alone (that explained part of it: 0.9% → 0.5%) and **not** by WorldDynamics.jl's tolerance. Cause unknown. Candidates, none tested: small differences in how the two codes implement delays or smoothing, in table interpolation, or in the timing of the switched policy inputs.

### Local test of the yardstick (PyWorld3 1.1, run on the same code outside CI)
PyWorld3 at its default step is far from its own fine-step run for some stocks: maximum gap by stock (year): p1 1.45 % (2025), p2 0.96 % (2043), p3 1.14 % (2054), p4 1.62 % (1986), ic 2.54 % (2040), sc 3.42 % (2030), al 0.81 % (1994), pal 1.89 % (2006), uil 2.01 % (1992), lfert 2.41 % (2042), ppol 11.57 % (1904), nr 3.51 % (2018). **Consequence:** a ±2% test against PyWorld3 at dt=0.5 could fail a correct implementation. Comparisons must use the fine-step run (and D-012 already makes WorldDynamics.jl, not PyWorld3, the primary reference for the Python port).

### Still open
- All main stocks, not only population, still have to be compared with real data (run #6).
- The residual gap is unexplained (see above).
- Earth4All.jl has not yet been compared numerically with Vensim (run #6 runs the package's own `all_mre`; needs D-014).
- Which World3 variant (1974 or 2003) F3's population sector should be based on has to be decided before step 1.4. WorldDynamics.jl offers both; the 2003 variant is the one in *The Limits to Growth: The 30-Year Update*.

### Status of Phase 1 step 1.1 (T0)
Not passed. Population is within ±2% of the references; the rest of the T0 evidence is being collected in run #6.

## Run #4 (2026-10-05, F3 commit 78f260e)

### Confirmed
- **The World3 solver problem is a solver-initialization failure.** `WorldDynamics.solve` with default options returns `InitialFailure` and one time point (1900). With `initializealg = NoInit()` it returns `Success` over 1900–2100 (50 saved points). The package's own failure therefore comes from how the current dependency versions handle initialization, not from the World3 equations.
- **Versions in play:** ModelingToolkit 9.84.0 · DifferentialEquations 7.17.0 · OrdinaryDiffEq 6.105.0 · OrdinaryDiffEqCore 2.3.0 · DiffEqBase 6.213.0 · SciMLBase 2.153.1 (package v1.0.0 dates from April 2024).
- **First valid cross-check (population only):** WorldDynamics.jl with `NoInit()` vs PyWorld3 (dt=0.5): max 0.91% (1985), mean 0.43%, within the ±2% band of D-004, on 50 time points.

### Caveats (do not skip)
- **Population only.** One variable, not the full set of key variables in D-004.
- **Coarse.** 50 saved points (about 4 years apart) can hide short features.
- **`NoInit()` skips the solver's initialization consistency check.** It is a deviation from the package defaults and must be logged as a decision before F3 relies on it. The agreement with an independent implementation is the evidence for it, not a proof.
- **PyWorld3 is not an exact yardstick.** A local test (PyWorld3 1.1) shows its own population differs by up to ~0.9–1.0% between dt=0.5 (default) and dt=0.05, which is as large as the gap measured. **Hypothesis:** most of the gap is PyWorld3's fixed-step error, not a model difference. Run #5 tests this against a fine-step PyWorld3 run and a tight-tolerance WorldDynamics.jl run.
- **Which World3 version does each implement?** The package's test set is named `World3_03`; PyWorld3's documentation should be checked for the version it implements. Agreement within 1% suggests they are the same model, but this has to be confirmed from the documentation, not inferred.
- WorldDynamics.jl's own test suite still errors 5/5. It calls the solver with default options, so this is expected and adds no new information.
- Earth4All.jl: unchanged (see run #3, problem 4). Run #5 lists the repository layout to find out whether reference output ships with it.

### Status of Phase 1 step 1.1 (T0)
Not passed. Open: confirm the size of the numerical gap (run #5), log the solver-option decision, answer the World3-version question, and decide how Earth4All.jl is checked against Vensim.

## Run #3 (2026-10-05, F3 commit c4db929)

**Environment:** Julia 1.10.12 · WorldDynamics.jl v1.0.0 · Earth4All.jl `16f37d0` (branch `master`) · PyWorld3 1.1

> **Revision (after reading the package's test log and the Figure 7.7 image):** three statements in the first version of this entry were wrong and are corrected below. (a) Figure 7.7 did *not* regenerate: the saved image is empty (axes and legend, no curves). (b) The 1-row export was *not* an export problem: the solver itself returned a single time point. (c) The "workaround" therefore proved nothing about the model. All three symptoms below share one observed cause: the default `WorldDynamics.solve` returns a one-point solution in this environment.

### Confirmed
- **Earth4All.jl runs as published.** Both scenarios solve (7,681 time points, 106 variables each) and both figures regenerate. The figures show the Julia model's own run; they do not overlay Vensim output, so they show "runs and behaves plausibly", not "matches Vensim".
- **PyWorld3 runs unmodified.** Standard run 1900–2100; population peaks at 7.06 billion in 2027.
- **WorldDynamics.jl builds the World3 system** (`World3.historicalrun()` returns a ModelingToolkit `ODESystem`). Solving it does not yet work, see problem 1.

### Problems found
1. **`WorldDynamics.solve` returns a one-point solution** (time 1900 only) in this environment. Evidence: (i) the package's own test suite fails 5 of 5 with `BoundsError: attempt to access 1-element Vector{Float64} at index [2]`; (ii) our export had 1 row; (iii) the regenerated Figure 7.7 is empty. The test log also shows `Warning: Initialization system is overdetermined. 16 equations for 7 unknowns`, and dependencies much newer than the package (April 2024): ModelingToolkit v9.84.0, DifferentialEquations v7.17.0, OrdinaryDiffEq v6.105.0, DiffEqBase v6.213.0. **Working hypothesis, not yet confirmed:** the solver's initialization step fails and returns early (dependency drift). Run #4 records the return code and tries solver initialization options.
2. **`World3.fig_7()` fails with `UndefVarError: solve not defined`** (`plots.jl:6`). Possibly the same dependency drift. After making `solve` visible, it runs but draws nothing (see problem 1).
3. **The T0.4 cross-check result in run #3 is INVALID** (0.00% gap): only the shared 1900 starting value was compared, because the WorldDynamics.jl solution had one point. The comparison now refuses to run on fewer than 50 time points.
4. **Earth4All.jl has no test folder.** There is no automated check of its agreement with Vensim, and its figures show only the Julia run (no Vensim overlay). Any such check has to be built by F3 (see D-011 for the constraint on Vensim files).

### Status of Phase 1 step 1.1 (T0)
Not passed. Open: a working World3 solve and a valid cross-check against PyWorld3 (problems 1 and 3), and a way to check Earth4All.jl against Vensim output (problem 4).
