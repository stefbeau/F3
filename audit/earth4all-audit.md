# F3 — Earth4All.jl audit (D-010 tests T1–T4)

**Status:** T1–T4 run 2026-10-07. **Object audited:** Earth4All.jl at commit `16f37d013a2f68135f03e7815bf861dbf47311f2` (MIT), environment resolved by `Pkg.instantiate()` against the package's own `Project.toml` on Julia 1.10.12 (the package ships no Manifest; resolved versions: ModelingToolkit 9.84.0, OrdinaryDiffEq 6.105.0, SciMLBase 2.153.1, DifferentialEquations 7.17.0, WorldDynamics 1.0.0). DataFrames and CSV were added to the clone's environment for export, as in the T0 workflow; the model code is unmodified. **Basis:** D-011 (Earth4All.jl is the reference), D-018 (it is audited as a reference implementation in its own right), D-014 (Vensim output is used only through the package's own comparison; `vensim_source/` is not used). Equations are quoted from Earth4All.jl (MIT, © World Dynamics) for audit purposes.

This file states facts and evidence. It does not judge the model's authors or its critics. Definitions that D-010 leaves open are stated where they are used, and flagged where a different definition could change the answer.

**Scripts:** `audit/t0/earth4all_audit.jl` (T1b, T2, T3 counterfactual, T4; run inside the clone's environment), `audit/t0/earth4all_explore.jl` (name discovery). **Stored results** (small CSVs, no Vensim values): `audit/data/earth4all_t1b_cohort_minima.csv`, `earth4all_t2_summary.csv`, `earth4all_t2_yearly_{TLTL,GL}.csv`, `earth4all_t3_counterfactual.csv`, `earth4all_t4_offenders_{TLTL,GL}.csv`.

**Environment note (2026-10-08).** The audit environment is now pinned: `audit/env-earth4all/Project.toml` (the package's own at the commit above) and `Manifest.toml`, resolved once with DataFrames and CSV added; the scripts and the T0 workflow install from it instead of resolving at run time. The first audit run (2026-10-07) had resolved its own environment; the pinned one differs from it in 4 of 348 packages, all patch releases (ArrayLayouts 1.13.1 to 1.14.0, LazyArrays 2.14.3 to 2.14.4, Roots 3.0.10 to 3.0.11, SparseConnectivityTracer 1.2.3 to 1.2.4). The T0 error statistics and the T1b, T2, T3 counterfactual and T4 scripts were re-run in the pinned environment: every stored result is identical, except that the per-variable error statistics differ by at most 1.8e-15 relative (floating-point rounding in one mean-error cell), and the report text is identical. The results below are therefore unchanged and reproducible from the committed Manifest.

## Summary of results

| Test | Result | Verdict against D-010's pass criterion |
|---|---|---|
| T1 mortality | No death flow out of the cohorts below 60, by design (static reading) | **Not met as written** (a modelling simplification, not a numerical accident) |
| T1b stocks non-negative | All four cohort stocks stay positive over 1980–2100 in both scenarios (smallest value 617.7 Mp) | **Met** |
| T2 employed ≤ working-age | Workforce ≤ working-age population in all 121 years, both scenarios (maximum ratio 0.825). Workforce exceeds the *available* workforce (working-age × participation) by at most 0.59% in 4 (TLTL) and 9 (GL) years | **Met** under the definition below; see the caveat |
| T3 forcing audit | 40 explicit time-driven equations: 9 behaviour forcing, 18 policy inputs, 7 feedback switches, 3 historical-then-goal paths, 2 reporting-only, 1 no-effect. **No behaviour forcing in output, demand, inventory, finance, public or energy** | **Met** for the sectors named in D-010; behaviour forcing exists in climate, foodland and population |
| T4 past 2100 | Too Little Too Late runs to 2200 without a non-finite value; Giant Leap becomes unstable (solver `Unstable` at 2197.3; NaN in 19 variables) | Informational |

## T1 — population mortality (static reading)

`src/population/subsystems.jl` defines four cohorts and their flows:

- `D(A0020) ~ BIRTHS - PASS20`
- `D(A2040) ~ PASS20 - PASS40`
- `D(A4060) ~ PASS40 - PASS60`
- `D(A60PL) ~ PASS60 - DEATHS`

`PASS20`, `PASS40` and `PASS60` are delays of `BIRTHS` over 20 years each; `DEATHS` is a delay of `PASS60` whose length is `LE60 = LE - 60` (life expectancy minus 60). So the model has **no death flow out of the cohorts younger than 60**: everyone reaches 60, and dies a delay of (life expectancy − 60) years later. Claim 1 of the March 2024 review (cohorts below 60 have no mortality) is therefore **confirmed as a property of the model as published** (a design simplification).
**For F3:** S1 is based on World3's population sector (D-010), in which every cohort has mortality, so this simplification does not enter F3's population. It matters for any Earth4All component whose behaviour depends on the Earth4All population.

### T1b — minimum of each cohort stock, 1980–2100 (run)

| scenario | stock | minimum (Mp) | year of minimum | 1980 | 2100 |
|---|---|---|---|---|---|
| TLTL | aged 0–20 | 1123.6 | 2100 | 2170.0 | 1123.6 |
| TLTL | aged 20–40 | 1058.2 | 2100 | 1100.0 | 1058.2 |
| TLTL | aged 40–60 | 768.0 | 1980 | 768.0 | 1610.0 |
| TLTL | aged 60+ | 382.0 | 1980 | 382.0 | 3490.7 |
| GL | aged 0–20 | 671.7 | 2100 | 2170.0 | 671.7 |
| GL | aged 20–40 | 617.7 | 2100 | 1100.0 | 617.7 |
| GL | aged 40–60 | 768.0 | 1980 | 768.0 | 1257.2 |
| GL | aged 60+ | 382.0 | 1980 | 382.0 | 3437.8 |

No cohort stock is negative before 2100 in either scenario. (Beyond 2100 see T4: in Giant Leap the aged 20–40 stock turns negative in 2154.6.)

## T2 — employed versus working-age population (run)

**Definitions (read from `src/labourmarket/subsystems.jl`):** `WF` ("WorkForce", Mp) is the stock of employed people: `D(WF) ~ CHWO`, with `UNEM ~ max(0, AVWO - WF)`, so unemployment is whatever the available workforce has that the workforce stock does not. `WAP` ("Working Age Population") is `A20PA = A2040 + A4060 + A60PL − OP` (`OP` = on pension). `AVWO ~ WAP * LPR` is the available workforce (`LPR` = labour participation rate). We take **employed = `WF`** and **working-age = `WAP`**. The review's wording ("employed people", "working-age population") does not name variables; if the review meant a different pair (for example employed = `WF` against `AVWO`, or population aged 20–60), the answer could differ, and we flag that rather than guess.

| scenario | years with WF > WAP | max WF/WAP (year) | min WF/WAP | years with WF > AVWO | max WF/AVWO | participation rate range |
|---|---|---|---|---|---|---|
| TLTL | 0 of 121 | 0.8144 (2004) | 0.7439 | 4 | 1.0059 | 0.789–0.819 |
| GL | 0 of 121 | 0.8248 (2095) | 0.7401 | 9 | 1.0059 | 0.798–0.832 |

Under the definition above the pass criterion of the plan (employed ≤ working-age population in every year) holds. The workforce stock can exceed the available workforce by up to 0.59% for a few years (the stock adjusts to the optimal workforce with a delay `HFD`, while available workforce moves with participation), and then `UNEM` is zero. We found no year, in either scenario, in which the employed stock exceeds working-age population. Per-year values are in `audit/data/earth4all_t2_yearly_*.csv`.

## T3 — time-driven equations

The full model composes twelve sector systems (`src/earth4all/scenarios.jl`: demand, climate, energy, finance, foodland, inventory, labour market, other, output, population, public, wellbeing). Each sector file also contains `*_support` helper systems that stand in for other sectors when a sector is run alone; they use time tables (e.g. `GDP ~ interpolate(t, tables[:GDP], …)`) and are **not** part of the composed model. A first scan that counted them gave 184 time-driven equations; that figure was wrong for the full model and is corrected here.

Within the twelve main systems (465 equations), **40 equations are explicit functions of time**: 19 ramps, 2 steps and 19 switches of the form `ifelse(t > …)`. There are no live time-table lookups in the main systems (two are commented out in the output sector).

| sector | equations | ramp | step | switch on t |
|---|---|---|---|---|
| climate | 54 | 1 | 0 | 3 |
| demand | 66 | 2 | 1 | 3 |
| energy | 80 | 3 | 1 | 1 |
| finance | 10 | 0 | 0 | 0 |
| foodland | 87 | 7 | 0 | 3 |
| inventory | 16 | 0 | 0 | 1 |
| labour market | 37 | 1 | 0 | 0 |
| other | 7 | 0 | 0 | 0 |
| output | 38 | 0 | 0 | 4 |
| population | 34 | 4 | 0 | 1 |
| public | 20 | 1 | 0 | 3 |
| wellbeing | 16 | 0 | 0 | 0 |
| **total** | **465** | **19** | **2** | **19** |

### Classification (all 40 read, consumers found by searching the source)

Classes, defined before reading the results: **policy input** — a lever whose value is a parameter and which the scenarios set (acceptable if documented); **historical path, then policy goal** — a calibrated 1980–2022 path followed by a policy ramp; **feedback switch** — a factor that is 1 before 2022 and an endogenous function (of warming or other state) afterwards, so the time term only switches a feedback on; **behaviour forcing** — an exogenous trend that changes an outcome with no policy lever of the user's and no feedback (red flag in D-010's sense); plus **no effect** and **reporting only**. The per-equation table, with consumers and notes, is `audit/earth4all-time-driven-equations.csv` (the original candidate class is kept in its own column; the confirmed class is a new column).

| class | count | where |
|---|---|---|
| policy input | 17 | demand 5; foodland 3; energy 2; output 2; population 2; climate 1; labour market 1; public 1 |
| policy input, non-zero at defaults | 1 | public `DRTA`: `EDROTA2022 = 0.003` is added from 2022 in both scenarios |
| historical path, then policy goal | 3 | demand `BITRO`; energy `FNE`, `DRES` |
| feedback switch | 7 | foodland 2, output 2, climate 1, population 1, public 1 |
| **behaviour forcing** | **9** | climate 2 (`KN2OEKF`, `KCH4EKC`: exogenous 1%/y decline of N2O per kg fertiliser and CH4 per kg crop from 1980); foodland 5 (`CEM`, `FAM`, `LERM`, `OGRRM`: the SSP2 land-management ramps, `SSP2LMA = 1`; `FSPI`: exogenous food productivity growth, 0.2%/y); population 2 (`FM`, `LEM`: the SSP2 family-action ramps, `SSP2FA2022F = 1`) |
| no effect | 1 | inventory `DEL`: `PNIS` is the constant 1 (a pink-noise placeholder), so the 1984 switch changes nothing |
| reporting only | 2 | energy `ECETSGDP`, public `XECTAGDP`: no other equation reads them |

**Behaviour forcing does not appear in output, demand, inventory, finance, public or energy**, the sectors D-010 names for possible reuse. It appears in climate, foodland and population. The caveat on scope: this inventory covers explicit functions of time; a variable that is forced through a parameter that is itself a constant trend, or through a lookup on an endogenous variable, is not counted, and neither is the effect of the equations on outcomes beyond what the counterfactual below measured.

### What the time-driven forcing does to the headline outcomes (counterfactual, run)

TLTL with the package's own parameters changed, one at a time (`audit/data/earth4all_t3_counterfactual.csv`); difference at 2100 against the unchanged run:

| variable | `SSP2FA2022F` 1 → 0 (fertility and life-expectancy ramps off) | `SSP2LMA` 1 → 0 (land-management ramps off) |
|---|---|---|
| population | 7283 → 5218 Mp (**−28.4%**) | 0.01% |
| life expectancy | 95.2 → 86.7 y (−8.9%) | 0.03% |
| average well-being index | 0.72 → 0.94 (**+30.1%**; max 32.4% in 2096) | 0.72 → 0.69 (−4.2%) |
| inequality index | 1.27 → 1.12 (−11.6%) | 0.25% |
| social tension | 1.30 → 1.24 (−4.8%) | +1.3% |
| GDP per person | +3.4% | 0.14% |
| observed warming | −1.1% | +0.6% |

So the two exogenous 2022–2100 ramps in the population sector move 2100 population by about 28% and the well-being index by about 30%; the land-management ramps move the well-being index by 4%. These are the effects of Earth4All's built-in SSP2 assumptions in the scenarios as published; they say nothing about whether the assumptions are reasonable.

### Latent observations (not tested)

- `src/population/subsystems.jl:92` reads `EPA ~ ramp(t, (GEPA - inits[:EPA]) / IPP, 2022, 22022 + IPP)`. The ramp end `22022 + IPP` looks like a typo for `2022 + IPP`. With the default parameters (`GEPA = 0`, initial `EPA = 0`) the slope is zero and the equation has no effect; Julia and Vensim agree exactly on this variable ("Extra Pension Age": error 0 in both scenarios). It would matter only if the extra-pension-age lever were set. Whether Vensim has the same expression was not checked (`vensim_source/` is not used, D-014).
- Two other ramps end at `2020 + IPP` instead of `2022 + IPP` (demand `IC2022` line 159, foodland `FRA` line 192), so they stop two years before the policy-introduction period is over. Whether this is intended, or matches Vensim, was not checked. Both levers are zero in TLTL.

## T4 — running past 2100 (run)

Both scenarios were run to 2200 with the package's own solver settings (Euler, `dt = 0.015625`, `CheckInit()`). **"Plausible range" is not defined in D-010; this audit defines three criteria and reports them separately:** (a) a value is NaN or infinite; (b) a variable that is ≥ 0 at every point of 1980–2100 becomes negative; (c) a variable's absolute value exceeds 10 times its maximum absolute value over 1980–2100. Every variable of the twelve main systems was checked; the offenders are listed in `audit/data/earth4all_t4_offenders_*.csv`.

| | Too Little Too Late | Giant Leap |
|---|---|---|
| solver return code | `Success`, to 2200 | **`Unstable`**, stops at 2197.30 |
| (a) non-finite | none | 19 variables, first at 2197.28 (rate of technological advance, public sector; then well-being and others) |
| (b) turns negative | 5 variables; first *Rate of Growth in GDP per Person* in 2117.1, then inflation rate and price-index change (2121.1), CO2 emissions and CO2 per GDP (2187.3) | 49 variables; first *Inflation Rate* and *Change in Price Index* in 2117.2, then crop supply and yield (2117.5), CO2 absorption (2126.7), **births and birth rate (2154.6)**, **aged 20–40 stock (2154.6)** |
| (c) beyond 10× | none | 8 variables; first *Dependency Ratio* in 2175.3 (21.9, against a 1980–2100 maximum of 2.19), then owner tax rate (2179.7), price-index change (2182.8), and others up to 2197 |

Headline variables at 2100 / 2150 / 2200:

| variable | TLTL | GL |
|---|---|---|
| population (Mp) | 7283 / 4333 / 2059 | 5984 / 2480 / 632 |
| GDP per person (kDollar/p/y) | 46.5 / 85.0 / 113.4 | 55.9 / 96.7 / 141.3 |
| well-being index | 0.72 / 1.53 / 2.56 | 3.12 / 7.91 / NaN |
| social tension | 1.30 / 1.09 / 1.19 | 1.09 / 1.06 / NaN |
| inequality index | 1.27 / 1.03 / 0.81 | 0.60 / 0.27 / −0.36 |
| observed warming (deg C) | 2.35 / 2.46 / 2.36 | 2.01 / 1.89 / 1.74 |

The Earth4All team states that the model should not be run beyond 2100 (D-010); these results show what happens when it is. F3 stops at 2100, so this is informational. Note, as an observation only: the Giant Leap well-being index is 3.12 in 2100, while the T0 headline table gives 0.62–1.44 as the Vensim range for TLTL (a different scenario, so this is not a like-for-like range).

## What the audit does not show

- The tests run Earth4All.jl, which T0 shows is a close numerical copy of the Vensim run for most variables, with the deviations listed in `audit/T0-FINDINGS.md` and D-018. They say nothing about whether the structure is sound where all of Earth4All and Vensim agree.
- T3's classification is the Validator's reading of 40 equations and the parameters' defaults. The counterfactual measures two switches only; it does not measure the other policy inputs, the 1980 baseline trends (climate N2O and CH4, food productivity) or the feedback switches.
- T2 uses one reading of "employed" and "working age". T4's plausible-range criteria are this audit's own.

## Next steps

1. Draft D-016 (done, Proposed in `DECISIONS.md`); the editor-in-chief decides.
2. If wanted: measure the effect of the remaining behaviour-forcing equations (climate, food productivity), and re-run T2 with the editor-in-chief's preferred definition of "employed".
