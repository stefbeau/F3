# S3 / World3 reconciliation: what is shared, how far apart, and the options (D-053 C; written 2026-10-21)

**Status:** section 1 (method) is committed **before** the measurement script was run; sections 2 onward are added after it, by dated sections, and nothing in section 1 is edited afterwards. **Nothing is built, no sector, test or label is changed.** Script: `audit/t0/s3_world3_measure.py`; figures: `audit/data/s3-world3-measure.json`.

## 1. What is measured (fixed before the run)

**Runs.** (i) S3 under R3 at its fitted defaults (the "standard R3 central" run), damage off, electricity limit off, from 2025 to 2100, alone. (ii) S3 under R3 with AI investment switched off (`R3Levers(initial_ai_share=0.0)`, capital investment kept), the "S3 with automation and AI investment off" baseline for a relative uplift. (iii) World3, 2004 parameter set, standard parameters, damage off, D-031 group, 1900 to 2100. (iv) For a third comparison only, the **recorded Earth4All.jl TLTL run** (committed fixture `tests/fixtures/e4a_reference_tltl.csv`, MIT, a recording, not a run of ours): `inventory.GDP` (Gdollar/year), `population.POP` and `labourmarket.WF` (Mp).

**Samples.** Values at 1 January of 2025, 2030, 2040, 2050, 2075, 2100 (loop boundaries). S3's flows (`gwp`) at a boundary are the total for the year that just ended; its stocks are values on that date. World3 population is `p1 + p2 + p3 + p4` (persons); World3 labour force is `lf = (p2 + p3) x lfpf` with `lfpf = 0.75` (the model's own Line 80, as the capital sector computes it); World3 industrial output `io` and service output `so` are the capital sector's published outputs (model dollars per year, World3's own constant dollars); "World3 output" is reported as `io`, `so` and `io + so`. World3 has **no total economic output** and no valued agricultural output: food is in vegetable-equivalent kilograms, and agricultural inputs are a use of `io` and `so`, not an addition to them, so `io + so` is the closest dollar total and is **not** a GDP.

**Quantities and ratios.** S3 `labor` / World3 population, and / World3 labour force, and / Earth4All `WF`; S3 `gwp` / World3 `io`, `so`, `io + so`, and / Earth4All GDP; compound annual growth rates 2025 to 2050 and 2050 to 2100 of each; and the **relative uplift** `gwp(R3 central) / gwp(AI investment off)` at the same dates.

**What this can and cannot say.** The two models start from different bases (S3: 110 trillion USD in 2025 with 3.6 billion workers; World3: its own constant dollars from a 1900 start), so levels are expected to differ; what matters for any coupling is the **ratio at 2025 and how it moves**. S3's levels are unvalidated after about 2027 (D-029) and the diagnostic (`docs/s3-diagnostic.md`) shows its absolute output leaves any plausible range, so ratios beyond about 2030 describe S3's internal trajectory, not the world.

## 2. Measurement (run 2026-10-21; figures in `audit/data/s3-world3-measure.json`)

Nothing in section 1 was changed after the run (one fix to the script before it produced any output: the Earth4All series were first read from the wrong fixture file, which has no population column; they are read from `tests/fixtures/e4a_signals_tltl.csv`, the recorded Earth4All.jl TLTL run).

### 2.1 Labour and population (persons)

| | 2025 | 2030 | 2040 | 2050 | 2075 | 2100 |
|---|---|---|---|---|---|---|
| S3 labour (grows 0.25%/year, exogenous) | 3.60e9 | 3.65e9 | 3.74e9 | 3.83e9 | 4.08e9 | 4.34e9 |
| World3 population (p1 to p4) | 7.52e9 | 7.49e9 | 7.11e9 | 6.49e9 | 4.64e9 | 3.50e9 |
| World3 labour force, (p2 + p3) x 0.75 | 3.44e9 | 3.47e9 | 3.34e9 | 3.07e9 | 2.19e9 | 1.61e9 |
| Earth4All workforce (recorded, TLTL) | 3.99e9 | 3.90e9 | 4.25e9 | 4.44e9 | 4.46e9 | 3.73e9 |
| **S3 labour / World3 population** | 0.48 | 0.49 | 0.53 | 0.59 | 0.88 | 1.24 |
| **S3 labour / World3 labour force** | **1.05** | 1.05 | 1.12 | 1.25 | 1.86 | 2.70 |
| S3 labour / Earth4All workforce | 0.90 | 0.93 | 0.88 | 0.86 | 0.92 | 1.16 |

Growth, compound per year: S3 labour +0.25% (2025 to 2100); World3 population -0.59% (2025 to 2050) and -1.23% (2050 to 2100); World3 labour force -0.46% and -1.28%; Earth4All population +0.38% and -0.37%. **Reading:** S3's labour is a total number of workers, and World3's **labour force is derivable** (`lf`, with the model's own participation fraction 0.75) and starts within 5% of S3's 3.6 billion (ratio 1.05 in 2025). S3 labour against World3 **population** is not the same quantity (ratio 0.48: workers against people). Going forward the two diverge steadily because S3's labour grows and World3's collapses with the standard run (ratio 2.7 by 2100).

### 2.2 Output (USD per year for S3 and Earth4All; World3's own model dollars per year for World3)

| | 2025 | 2030 | 2040 | 2050 | 2075 | 2100 |
|---|---|---|---|---|---|---|
| S3 `gwp` (R3 central, unlimited) | 1.10e14 | 2.23e14 | 2.85e15 | 7.35e17 | 4.12e19 | 5.66e19 |
| S3 `gwp` with AI investment off | 1.10e14 | 1.20e14 | 9.21e13 | 7.36e13 | 4.04e13 | 2.54e13 |
| World3 `io` | 2.07e12 | 1.58e12 | 1.03e12 | 6.37e11 | 1.88e11 | 5.68e10 |
| World3 `so` | 4.20e12 | 3.72e12 | 2.65e12 | 1.82e12 | 6.83e11 | 2.71e11 |
| World3 `io + so` (not a GDP) | 6.27e12 | 5.30e12 | 3.68e12 | 2.46e12 | 8.72e11 | 3.28e11 |
| Earth4All GDP (recorded) | 1.30e14 | 1.38e14 | 1.74e14 | 2.02e14 | 2.81e14 | 3.39e14 |
| **S3 `gwp` / World3 `io`** | 53 | 141 | 2.8e3 | 1.2e6 | 2.2e8 | 1.0e9 |
| **S3 `gwp` / World3 `io + so`** | 17.5 | 42 | 775 | 3.0e5 | 4.7e7 | 1.7e8 |
| S3 `gwp` / Earth4All GDP | 0.85 | 1.61 | 16 | 3.6e3 | 1.5e5 | 1.7e5 |
| **relative uplift**, S3 central / S3 AI off | 1.00 | 1.86 | 31 | 1.0e4 | 1.0e6 | 2.2e6 |

Growth, compound per year, 2025 to 2050 and 2050 to 2100: S3 `gwp` **+42.2%** and +9.1%; S3 with AI off **-1.6%** and -2.1%; World3 `io` -4.6% and -4.7%; `so` -3.3% and -3.7%; `io + so` -3.7% and -4.0%; Earth4All GDP +1.8% and +1.0%.

### 2.3 What the numbers say

1. **Labour is reconcilable; output is not.** At 2025 the two labour measures agree within 5% (World3 labour force against S3 labour); the 2025 output ratio is 17.5 (S3 against `io + so`), because World3's model dollars are on a different base (its 1900 constant dollars and its own capital-output ratios; **World3 has no total output**, and food is in vegetable-equivalent kilograms). Earth4All's 2025 GDP is within 16% of S3's (0.85), the closest base.
2. **S3's output leaves World3's scale within five years and any plausible scale within fifteen:** 42 times `io + so` in 2030 and 775 times in 2040 (the diagnostic, `docs/s3-diagnostic.md`, shows the S3 level is not a quantity to carry across; Epoch's own run is equally extreme).
3. **The "AI off" baseline is not a no-AI economy.** With the R3 AI shares set to zero, S3's `gwp` falls 1.6% a year (110 trillion to 25 trillion by 2100), a path that is also not credible as "the world without AI"; I did not investigate why (the R3 capital share and depreciation are the first suspects). So the relative uplift (central over AI off) of 1.86 in 2030 and 2.2 million in 2100 contains both an AI effect and a baseline decline, and cannot be read as a growth multiplier.
4. **World3 is itself in decline in the standard run** (population -0.6% to -1.2% a year, `io` -4.6%), so any link that makes World3 follow S3's growth would not reconcile the models; it would replace World3's dynamics.

## 3. Options, tests, risks, cost, recommendation (nothing is built)

Common test discipline for any option: written and committed before the code; the A6.1 and invariance tests are the existing ones (`tests/test_m6_integration.py`, `tests/test_m6_damage_coupling.py`) and must pass unchanged; every new switch defaults OFF; failures recorded with size and first year, nothing adjusted.

### Option A: relative uplift as a multiplier on World3 `io`, default off

- **What it is:** `io = io_gross x U(t)` with `U(t) = S3 gwp(t) / S3 gwp(t) with automation and AI investment off`, switchable, from 2025 (the same slot as the climate-damage multiplier, `damage_mult`).
- **What it changes:** World3's industrial output, and through it investment, agriculture, resources and population. S3 does not change; the second S3 run (AI off) must run alongside, once per scenario.
- **Measured against section 2:** `U` is 1.86 in 2030, 31 in 2040, 10,000 in 2050 and 2.2 million by 2100. Applied as measured it multiplies World3's `io` by up to 2 million: not a reconciliation. A bounded form (cap, saturation, or applying only to 2025-2030) needs a **new coefficient** the sources do not give, which is an editor decision, not mine.
- **Tests:** (i) A6.1 untouched when off: 29 states equal the group alone to 1e-9 (existing); (ii) invariance: switch off equals stand-alone World3 to 1e-9 and S3 unchanged to 1e-9 (new test, named); (iii) `U = 1` gives the baseline (the multiplier of 1 changes nothing, 1e-9); (iv) sign test: named output `io` in 2030 and 2040, ON above OFF for the standard R3 central run, and ON-race above ON-low (the control is the AI-off S3 run, for which `U = 1` and the assertion must fail); (v) bounds and NaN over the lever grid.
- **Risks:** highest. The multiplier inherits S3's unvalidated level (D-029) and the baseline decline (2.3 item 3); a cap invents a coefficient; the result would read as "AI makes the world richer by X" from a model that failed its own validation. It also double counts: World3's `io` already carries a model of industry.
- **Token cost:** about 150,000 to 250,000 tokens (tests, a second S3 run in the loop, the switch, a report).

### Option B: World3 labour force drives S3 labour, default off (the reverse direction)

- **What it is:** S3's labour `L` follows a relative index of World3's labour force, `L(t) = L0 x lf(t) / lf(2025)`, replacing S3's exogenous 0.25% a year, switchable, default off. `lf` is derivable (section 2.1) and the two start within 5%, so the index removes the base mismatch.
- **What it changes:** S3's labour input (and with it S3's output, capital productivity and automation economics). **World3 does not change at all** (one-way), so A6.1 is untouched whatever the switch.
- **Measured:** World3's labour force falls to 0.47 of its 2025 value by 2100 in the standard run, so S3's labour would fall from 3.6 to about 1.7 billion rather than rise to 4.3 billion. S3's output is dominated by automation, not labour, after 2030 (`labor_share` 0.40 in 2040 and about 0 after 2050), so the effect on S3's level is small relative to its own error; the effect before 2035 is the interesting one.
- **Tests:** (i) A6.1 and the damage-coupling tests unchanged (the link does not touch World3); (ii) invariance: switch off equals stand-alone S3 under R3 to 1e-9 (existing A6.3 item 2) and with a constant index equal to 1, the same; (iii) sign test, named output S3 `gwp` and `labor` in 2040 and 2060: lower World3 labour force gives lower S3 labour and lower `gwp`, control = the same run with a constant index; (iv) bounds and NaN; (v) unit and base check: ratio 1.05 at 2025 is stated and tested to 1e-12 on the index.
- **Risks:** low. One direction, one existing quantity, no new coefficient (the index uses World3's own `lfpf`). Residual: it makes S3 respond to World3's collapse, which changes S3's labour path against Epoch's reference (a labelled, switchable departure from GATE); and S3's labour share outputs (and the social module, if ever shown) would then move.
- **Token cost:** about 60,000 to 120,000 tokens (a small S3 input, the adapter, tests, report). Needs a change to S3 (a new optional input), which is a sector change and needs the editor's approval of the first job's findings.

### Option C: Earth4All economy

- **What it is:** use the ported Earth4All economy (M4) for output and labour instead of S3's economy for the shared quantities, with population from World3 (or Earth4All's own) and warming through adapters (D-042 note: revisit at M6).
- **Measured:** the closest base (S3 `gwp` / Earth4All GDP 0.85 in 2025; labour 0.90) and the only one with plausible growth (+1.8% then +1.0%).
- **Tests:** A4.5 already failed (GDP 2.2% to 2.5% from about 2076); the integration tests would need new A4-style comparisons; invariance and sign tests as in A and B for each link.
- **Risks:** large. It is a new coupled model, not a switch; the Earth4All warming channels were omitted by decision (D-049); it replaces S3 in the one place S3 is the project's distinctive contribution (AI), so it does not reconcile S3 and World3, it sidelines S3; the A4.5 failure carries over.
- **Token cost:** about 400,000 to 800,000 tokens and several sessions.

### Recommendation

**Option B first, and defer Option A.** Reasons: (1) it is the only shared quantity the measurements show to be reconcilable (labour force, 1.05 at 2025, derivable without a new coefficient); (2) it is one-way into S3, so World3's validated baseline (A6.1) is untouched by construction; (3) Option A would feed S3's output level into World3, and the measurements (2.3 items 2 and 3) and the diagnostic show that level, and the AI-off baseline, are not usable; it should wait for the S3 validation job, and then needs the editor's decision on a bounded form (a new coefficient); (4) Option C is a model replacement and a separate project. Option B does not reconcile **output**; it states that outputs of the two models stay unreconciled, which is already the label on every output. The two dependencies are the editor's: approval to add one optional input to S3, and whether the result should be shown anywhere (it should not be shown on the Explorer until S3's levels are validated).
