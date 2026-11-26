# Step E2 of the electricity module: results (2026-11-26)

Readings and tests: `docs/e2-power-aware-tests.md`, committed before the code. Code: the lever `power_aware` of `R3Levers` (`f3/sectors/s3_rule_r3.py`, default off) and one line in `f3/sectors/s3_ai.py` that passes the power ratio to the rule when the lever is on. Tests: `tests/test_r3_power_aware.py`. Runs as in `audit/e1-build-rate.md` (S3 under R3, composite P, electricity limit on, recorded supply, no damage, outer share 25%).

## Outcome of each reading
| Reading | Result |
|---|---|
| E2-T1 off equals recorded | **Met.** Lever off: shares equal to 1e-12 whatever ratio is passed. Existing tests of S3, R3, the slice and M6 pass unchanged (98 passed, 21 skipped, 5 expected failures already recorded; the R3 file separately). |
| E2-T2 shares valid | **Met** over the grid: no negative share, the first five sum to 1, only the compute and consumption shares change. |
| E2-T3 sign, with E2 on | **Met** for usable compute and for the compute stock: a slower build rate or half the supply never raises either, in any year. Both controls behave as required. (Without E2 the same reading on usable compute fails: E-T4, still recorded as failed.) |
| E2-T4 overhang | **Met** at the three build rates. |
| E2-T5 finite | **Met.** |

## Report only (no tolerance)
| Build rate | E2 | Used in 2030 / 2040 / 2060 (TWh) | Demand / use in 2030 / 2040 / 2060 | Output in 2030 / 2040 / 2060 / 2099 (trillion USD) | All tasks automated |
|---|---|---|---|---|---|
| 15% | off | 976 / 3,946 / 11,695 | 38 / 153 / 7,150 | 222 / 873 / 278,000 / 24.4 million | 2046 |
| 15% | on | 976 / 3,946 / 11,695 | 14 / 12 / 268 | 212 / 838 / 1.33 million / 287 million | 2045 |
| 30% | off | 1,801 / 10,440 / 11,695 | 21 / 52 / 8,820 | 233 / 1,330 / 335,000 / 24.4 million | 2043 |
| 30% | on | 1,801 / 10,440 / 11,695 | 8.7 / 8.0 / 303 | 224 / 1,300 / 1.71 million / 292 million | 2043 |
| 50% | off | 3,683 / 10,440 / 11,695 | 10 / 52 / 9,090 | 249 / 1,460 / 344,000 / 24.4 million | 2042 |
| 50% | on | 3,683 / 10,440 / 11,695 | 5.0 / 8.3 / 309 | 239 / 1,400 / 1.78 million / 293 million | 2043 |

## What this shows and what it does not
- **Measured:** with E2 the sign reading that failed in Track A (B1) and again in E1 (E-T4) holds. The unpowered overhang in 2040 falls from 52 to 153 times to 8 to 12 times.
- **Measured:** electricity used is the same with E2 on and off at the dates shown. E2 changes what S3 buys, not what can be powered.
- **Measured, and against the purpose:** S3's output stays outside any plausible range (world output is about 110 trillion USD in 2025) and is **higher** in the long run with E2 on: about 290 million trillion USD in 2099 against 24 million. Until about 2040 it is slightly lower.
- **Not investigated:** why long-run output rises with E2. The freed share goes to consumption in the rule; which stock grows instead was not traced. No cause is claimed.
- **Still unpowered:** demand remains 5 to 14 times use in 2030 with E2 on.
- **Unchanged:** every label. R3 as approved in D-028 is untouched when the lever is off.
