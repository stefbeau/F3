# Link 6, data-centre electricity to emissions: results (2026-11-26)

Readings and tests: `docs/link6-tests.md`, committed before the code (7b80466). Code: `f3/sectors/link6_dc_emissions.py` and one optional field of `ClimateSetup` (`co2_ffi_extra`, default none). Tests: `tests/test_link6_dc_emissions.py`. Figures: `audit/data/link6-dc-emissions.json`. The editor's choices of 2026-11-26: intensity from the recorded Earth4All run; all 841 members; six scenarios.

## Outcome of each reading
| Reading | Result |
|---|---|
| L6-T1 switch-off invariance | **Met.** No addition: the emissions table is identical. An addition of zero: warming and concentration equal to 1e-9. Existing climate, slice and M6 tests pass unchanged (70 passed, 2 skipped, 5 expected failures already recorded). |
| L6-T2 join and history | **Met.** Nothing is added up to and including 2025; warming up to 1 January 2026 unchanged to 1e-9. |
| L6-T3 mass conservation | **Met** to 1e-9 relative; no other species touched. |
| L6-T4 sign | **Met**, and the control (a negative addition) cools as required. |
| L6-T5 intensity | **Met:** between 0.16 and 0.42 kg CO2 per kWh over 2025 to 2100 (values seen before the bound was written). |
| L6-T6 one run equals yearly re-runs | **Met** to 1e-9 at 2030, 2050 and 2100. The six scenarios were therefore computed with one FaIR run each (about 19 seconds for 841 members), not with yearly re-runs. |

## Report only: six scenarios, 841 members
Without the link: ensemble-mean warming 1.92 K in 2050 and 2.86 K in 2100 (5 to 95%: 2.04 to 3.85 K in 2100).

| Build rate | Supply | Electricity used, 2030 / 2050 / 2099 (TWh in the year) | Extra CO2, 2030 / 2050 / 2099 (Gt a year) | Cumulative 2026 to 2099 (Gt CO2) | Added warming 2050 | Added warming 2100 |
|---|---|---|---|---|---|---|
| 15% | recorded | 926 / 11,222 / 8,778 | 0.17 / 2.81 / 1.31 | 127 | +0.008 K | +0.043 K |
| 30% | recorded | 1,636 / 11,222 / 8,778 | 0.43 / 2.81 / 1.31 | 151 | +0.017 K | +0.051 K |
| 50% | recorded | 3,184 / 11,222 / 8,778 | 1.01 / 2.81 / 1.31 | 160 | +0.021 K | +0.055 K |
| 15% | half | 926 / 5,611 / 4,389 | 0.17 / 1.34 / 0.62 | 67 | +0.006 K | +0.023 K |
| 30% | half | 1,636 / 5,611 / 4,389 | 0.43 / 1.34 / 0.62 | 76 | +0.010 K | +0.026 K |
| 50% | half | 3,184 / 5,611 / 4,389 | 1.01 / 1.34 / 0.62 | 79 | +0.011 K | +0.027 K |

Electricity here is the mean over the calendar year; `audit/e1-build-rate.md` gives the value on 1 January of the following year (976 against 926 for 2030 at 15%).

## What this shows and what it does not
- **Measured:** in these scenarios data-centre electricity adds 0.02 to 0.05 K to ensemble-mean warming in 2100. The ensemble's own 5 to 95% range in 2100 is 1.8 K wide. **The added warming is about one fortieth of that spread.**
- **Measured:** from about 2045 the electricity used is set by the outer share of supply (25%), not by the build rate, so the three build rates differ only until then. A quarter of world electricity for data centres is a provisional lever, not a finding.
- **Upper reading:** the baseline is the 2025 level held constant; the prescribed emissions already contain some data-centre growth. The true addition is smaller by an unknown amount.
- **Not included:** emissions from building data centres and chips; any effect of data centres on the rest of the electricity system (the intensity is the system average of the Earth4All run, and adding demand of this size would change it); non-CO2 gases; the return path from warming to electricity.
- **Not a statement about the world:** the electricity comes from S3 under F3's own investment rule, whose demand exceeds what is powered many times over; the result describes what the build-rate and supply limits allow.
- **Unchanged:** every label, and the site. The Explorer's warming panel does not use this link.
