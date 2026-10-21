# S3 / World3 reconciliation: what is shared, how far apart, and the options (D-053 C; written 2026-10-21)

**Status:** section 1 (method) is committed **before** the measurement script was run; sections 2 onward are added after it, by dated sections, and nothing in section 1 is edited afterwards. **Nothing is built, no sector, test or label is changed.** Script: `audit/t0/s3_world3_measure.py`; figures: `audit/data/s3-world3-measure.json`.

## 1. What is measured (fixed before the run)

**Runs.** (i) S3 under R3 at its fitted defaults (the "standard R3 central" run), damage off, electricity limit off, from 2025 to 2100, alone. (ii) S3 under R3 with AI investment switched off (`R3Levers(initial_ai_share=0.0)`, capital investment kept), the "S3 with automation and AI investment off" baseline for a relative uplift. (iii) World3, 2004 parameter set, standard parameters, damage off, D-031 group, 1900 to 2100. (iv) For a third comparison only, the **recorded Earth4All.jl TLTL run** (committed fixture `tests/fixtures/e4a_reference_tltl.csv`, MIT, a recording, not a run of ours): `inventory.GDP` (Gdollar/year), `population.POP` and `labourmarket.WF` (Mp).

**Samples.** Values at 1 January of 2025, 2030, 2040, 2050, 2075, 2100 (loop boundaries). S3's flows (`gwp`) at a boundary are the total for the year that just ended; its stocks are values on that date. World3 population is `p1 + p2 + p3 + p4` (persons); World3 labour force is `lf = (p2 + p3) x lfpf` with `lfpf = 0.75` (the model's own Line 80, as the capital sector computes it); World3 industrial output `io` and service output `so` are the capital sector's published outputs (model dollars per year, World3's own constant dollars); "World3 output" is reported as `io`, `so` and `io + so`. World3 has **no total economic output** and no valued agricultural output: food is in vegetable-equivalent kilograms, and agricultural inputs are a use of `io` and `so`, not an addition to them, so `io + so` is the closest dollar total and is **not** a GDP.

**Quantities and ratios.** S3 `labor` / World3 population, and / World3 labour force, and / Earth4All `WF`; S3 `gwp` / World3 `io`, `so`, `io + so`, and / Earth4All GDP; compound annual growth rates 2025 to 2050 and 2050 to 2100 of each; and the **relative uplift** `gwp(R3 central) / gwp(AI investment off)` at the same dates.

**What this can and cannot say.** The two models start from different bases (S3: 110 trillion USD in 2025 with 3.6 billion workers; World3: its own constant dollars from a 1900 start), so levels are expected to differ; what matters for any coupling is the **ratio at 2025 and how it moves**. S3's levels are unvalidated after about 2027 (D-029) and the diagnostic (`docs/s3-diagnostic.md`) shows its absolute output leaves any plausible range, so ratios beyond about 2030 describe S3's internal trajectory, not the world.

## 2. Measurement

(to be added after the run, in a dated section)

## 3. Options, tests, risks, cost, recommendation

(to be added after section 2)
