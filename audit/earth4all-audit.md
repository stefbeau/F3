# F3 — Earth4All.jl audit (D-010 tests T1–T4)

**Status:** started 2026-10-07; static reading only so far. **Object audited:** Earth4All.jl at commit `16f37d013a2f68135f03e7815bf861dbf47311f2` (MIT). **Basis:** D-011 (Earth4All.jl is the reference), D-018 (it is audited as a reference implementation in its own right), D-014 (Vensim output is used only through the package's own comparison; `vensim_source/` is not used). Equations are quoted from Earth4All.jl (MIT, © World Dynamics) for audit purposes.

This file states facts and evidence. It does not judge the model's authors or its critics.

## What has been done and what has not

| Test | Question | Done so far | Still to do |
|---|---|---|---|
| T1 | Do all population cohorts have mortality, and do cohort stocks stay non-negative? | Static reading of the population equations (below) | Minimum value of each cohort stock over 1980–2100 (needs a Julia run) |
| T2 | Can more people be employed than are of working age? | Nothing yet | Compare employed with working-age population every year, both scenarios (Julia run) |
| T3 | Which outcomes are driven by time-based inputs instead of feedback? | Static inventory of explicitly time-driven equations (below, and `earth4all-time-driven-equations.csv`) | Classify each equation as policy input or behaviour forcing; check what those inputs drive |
| T4 | What breaks if the model runs past 2100? | Nothing yet | Run to 2200 and record the first variable that leaves a plausible range |

## T1 — population mortality (static reading, preliminary)

`src/population/subsystems.jl` defines four cohorts and their flows:

- `D(A0020) ~ BIRTHS - PASS20`
- `D(A2040) ~ PASS20 - PASS40`
- `D(A4060) ~ PASS40 - PASS60`
- `D(A60PL) ~ PASS60 - DEATHS`

`PASS20`, `PASS40` and `PASS60` are delays of `BIRTHS` over 20 years each; `DEATHS` is a delay of `PASS60` whose length is `LE60 = LE - 60` (life expectancy minus 60). So the model has **no death flow out of the cohorts younger than 60**: everyone reaches 60, and dies a delay of (life expectancy − 60) years later. Claim 1 of the March 2024 review (cohorts below 60 have no mortality) is therefore **confirmed as a property of the model as published** (a design simplification, not a numerical accident). The second half of T1 (can a cohort stock go negative?) is not answered by reading: every inflow is a delayed copy of a non-negative flow, which argues against it, but the run is needed.
**For F3:** S1 is based on World3's population sector (D-010), in which every cohort has mortality, so this simplification does not enter F3's population. It matters for any Earth4All component whose behaviour depends on the Earth4All population.

## T3 — inventory of explicitly time-driven equations (static, preliminary)

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

The years appearing in these equations are 1980, 2020, 2022 and 2100 (and one anomaly below). Most are anchored in 2022, where the scenarios' policy levers (the "turnarounds") start; a few are baselines anchored in 1980 (for example the climate decay trends `exp(-RD·(t − 1980))` and the demand-sector ramp from 1980 to 2022). `earth4all-time-driven-equations.csv` lists every one of the 40 with a **candidate** class ("policy input starting 2022", "baseline trend anchored in 1980", or "to classify"). These classes are a first guess from the years in the equation and are to be confirmed by reading each equation; T3's question (does a time-based input drive an outcome that should be endogenous?) is not answered by the inventory.

**Observation (latent):** `src/population/subsystems.jl:92` reads `EPA ~ ramp(t, (GEPA - inits[:EPA]) / IPP, 2022, 22022 + IPP)`. The ramp end `22022 + IPP` looks like a typo for `2022 + IPP`. With the default parameters (`GEPA = 0`, initial `EPA = 0`) the slope is zero and the equation has no effect; Julia and Vensim agree exactly on this variable ("Extra Pension Age": error 0 in both scenarios). It would matter only if the extra-pension-age lever were set. Whether Vensim has the same expression was not checked (`vensim_source/` is not used, D-014).

## Next steps

1. Run T1b (minimum cohort stocks), T2 and T4 on Earth4All.jl in CI (needs Julia code written against the package's variable names).
2. Classify the 40 time-driven equations (T3) and trace what each drives.
3. Write the audit verdict as a decision entry (D-016 in the Phase 1 plan): for each Earth4All component, reuse, reuse with changes, or replace.
