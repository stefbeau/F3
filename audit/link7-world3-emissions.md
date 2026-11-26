# Link 7, World3 to emissions: results (2026-11-26)

Readings and tests: `docs/link7-tests.md`, committed before the code and before any fit (e6dbba5). Code: `f3/sectors/link7_world3_emissions.py` and one optional field of `ClimateSetup` (`co2_ffi_replace`, default none). Parameters: `f3/data/link7_intensity.json`. Tests: `tests/test_link7_world3_emissions.py`. Figures: `audit/data/link7-world3-emissions.json`. The editor's choices of 2026-11-26: fossil CO2 = World3 industrial output x an intensity fitted to 1970 to 2024 and extended at its trend; hindcast tolerance 10%.

## The fit (made once, in-sample)
`k(t) = exp(a + b t)` with `a` = -12.312757 and `b` = -0.006306: the CO2 per unit of World3 industrial output falls by 0.63% a year. Root-mean-square error over 1970 to 2024: 9.3%.

## Outcome of each reading
| Reading | Result |
|---|---|
| L7-T1 hindcast, 10% every year | **FAILED.** 14 of 55 years are outside 10%: 1973, 1994 to 2003, and 2022 to 2024. Largest difference **-27.2% in 2024**. Recorded as a strict expected failure; the tolerance was not changed and the form was not refitted. |
| L7-T2 switch-off invariance | **Met.** No replacement: identical table. Replacement by the prescribed values: warming and concentration equal to 1e-9. |
| L7-T3 history | **Met.** Nothing changes up to and including 2025; warming up to 1 January 2026 unchanged to 1e-9. |
| L7-T4 mass conservation | **Met** to 1e-9; no other species touched. |
| L7-T5 sign | **Met**, and the control fails as required. |
| L7-T6 stored parameters | **Met:** equal to a fresh fit to 1e-9. |
| L7-T7 with link 6 | **Met:** the two parts add. |

Existing climate, slice and link 6 tests pass unchanged with the link off.

## Report only (841 members)
Fossil CO2 given to FaIR, Gt a year, and ensemble-mean warming:

| Case | 2026 | 2050 | 2099 | Cumulative 2026 to 2099 | Warming 2050 | Warming 2100 (5 to 95%) |
|---|---|---|---|---|---|---|
| Prescribed path (link off) | 37.8 | 40.9 | 44.5 | 3,095 | 1.92 K | 2.86 K (2.04 to 3.85) |
| World3 standard run | 24.9 | 7.0 | 0.5 | 468 | 1.70 K | 1.91 K (1.31 to 2.63) |
| Resources half | 5.7 | 1.2 | 0.1 | 91 | 1.60 K | 1.76 K (1.20 to 2.43) |
| Resources double | 43.2 | 29.2 | 2.8 | 1,495 | 1.95 K | 2.29 K (1.58 to 3.14) |
| Land yield 2.0 | 16.5 | 3.7 | 0.2 | 272 | 1.65 K | 1.83 K (1.25 to 2.53) |
| Pollution factor 0.25 | 24.7 | 7.0 | 0.4 | 466 | 1.70 K | 1.91 K (1.31 to 2.63) |

Only five of the 27 lever settings were run.

## What this shows and what it does not
- **Measured:** the link works mechanically (six readings met) and, for the first time in F3, warming differs by World3 scenario: 1.76 to 2.29 K in 2100 across these five, against 2.86 K on the prescribed path.
- **Measured, and it decides how far the result can be used:** the hindcast fails, and it fails in the direction that matters. World3's standard industrial output falls after about 2015; observed emissions did not. By 2024 the computed emissions are 27% below observed, and **in 2026 the link steps fossil CO2 down from the prescribed 37.8 Gt to 24.9 Gt**, a drop of 34% in one year.
- **Therefore:** the lower warming in the table is the climate consequence of World3's collapse of industrial output, which reality has not followed so far. It is **not** a finding that warming will be lower, and it must not be shown without that statement.
- **Inferred, not tested:** that a fit to a World3 run with more resources would follow history better. "Resources double" starts 2026 at 43.2 Gt, above the prescribed value, but the intensity was fitted to the standard run only.
- **Not included:** non-CO2 gases and land-use CO2 (prescribed for every case, so the cases differ by fossil CO2 only); the return path from warming to World3; any harmonisation at the join.
- **Unchanged:** every label, and the site.
