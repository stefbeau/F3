# Link 7, variant B: a POST-HOC proposal, written after the first form's hindcast failed

Date: 2026-11-26. Proposal and tests: `docs/link7-variant-b.md` and `tests/test_link7_variant_b.py`, committed (299cf2a) before any variant-B result. **The first form's failure stands**: L7-T1 remains a recorded strict expected failure and its 10% tolerance is unchanged. Variant B is a different construction that the editor may accept or reject; it does not turn the earlier failure into a pass.

## What changed
1. **Reference run chosen against data, not by default.** Of the lever settings tried, the one whose World3 industrial output follows observed world GDP most closely over 1970 to 2024 (World Bank series already in `site/data/history.json`) is resources doubled with pollution 0.25: rms log distance 0.077 against 0.178 for the standard run. The intensity is fitted on that run.
2. **A join constant.** For any other run the computed series is multiplied by one constant so that its 2025 value meets the prescribed 2025 value. This gives up the absolute level of emissions for non-reference runs; only the change after 2025 comes from World3.

## Readings
| Reading | Result |
|---|---|
| L7B-T1 hindcast, reference run, 10% | **Met.** Largest error 9.4% (1998); 0 of 55 years outside 10%; rms 4.7% |
| L7B-T2a join factor of the reference run within 10% of 1 | **Met** (1.006) |
| L7B-T2b step from prescribed 2025 to computed 2026 within 5%, every run | **FAILED** for four of six: reference +0.7%, resources double +0.6%, standard -6.2%, pollution 0.25 -6.4%, resources half -6.7%, land yield 2.0 -7.3%. Recorded as a strict expected failure; the 5% is unchanged |
| L7B-T3, T4 (switch-off invariance, bounds) | Met |

The T2b failure has a plain cause: in those four runs World3's industrial output is already falling quickly in 2025, so one year of World3 moves emissions by more than 5%. It is a property of those runs, not of the join.

## Report (841 members, warming in 2100; prescribed pathway 2.86 K)
| Run | Join factor | Warming 2100 |
|---|---|---|
| Reference (resources double, pollution 0.25) | 1.006 | 2.20 K |
| Resources double | 1.043 | 2.19 K |
| Standard | 1.684 | 1.96 K |
| Pollution 0.25 | 1.698 | 1.97 K |
| Land yield 2.0 | 2.52 | 1.93 K |
| Resources half | 7.316 | 1.93 K |

## What this does and does not show
- Measured: on its reference run the link reproduces observed fossil CO2 for 1970 to 2024 within 10%.
- Inferred, not validated: everything after 2025. The lower warming is the consequence of World3's decline in industrial output; it is not a finding about the world and not a forecast.
- A join factor far from 1 (standard 1.68, resources half 7.3) means that run's World3 economy is far from the observed one in 2025; its emissions level is then set by the constant, not by World3.
- The reference run was selected from six settings, not from the 27 of the lever grid. One-way: emissions do not change World3 beyond links 1 and 3.
