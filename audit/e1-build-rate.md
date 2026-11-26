# Step E1 of the electricity module: results (2026-11-26)

Readings and tests: `docs/e1-build-rate-tests.md`, committed before the code (52652ea). Code: `f3/sectors/s4_datacentre.py` (two new parameters, `g_max` and `outer_share`; one new state, powered capacity). Tests: `tests/test_dc_build_rate.py`. Runs: S3 under R3 at its defaults (composite P), electricity limit on, recorded Earth4All supply (TLTL), no climate damage, 2025 to 2100, step 0.25 year. Provisional settings approved by the editor on 2026-11-26: build rates 15%, 30%, 50% a year; outer share 25%.

## Outcome of each reading
| Reading | Result |
|---|---|
| E-T1 off equals recorded | **Met.** With the defaults the module agrees with the module without the new parameters to 1e-9 on every output. The existing slice and M6 tests pass unchanged (106 passed, 3 expected failures that were already recorded). |
| E-T2 conservation | **Met** on the 16 grid points: use never exceeds powered capacity nor the outer share of supply; powered capacity never falls; all outputs finite and not negative. |
| E-T3 extremes | **Met.** A build rate of zero holds use at 485 TWh; an infinite build rate with a 5% outer share equals today's module to 1e-9. |
| E-T4 sign (the B1 reading) | **FAILED as written.** With the slower build rate, S3's usable compute is higher in 4 of 75 years (15% against 30%; largest +11.8% in 2038), in 5 years (30% against 50%; +8.4% in 2037), and with half the supply in 3 years (+3.8% in 2038). The control behaves as required (the reverse claim is false: 67 of 75 years). Recorded as a strict expected failure. |
| E-T5 step halving | **FAILED.** Largest difference 0.504% in 2098 against 0.1%. A2.6 had failed at 0.565% with the share cap. Recorded as a strict expected failure. |

One correction to a test after it was committed: E-T2 compared use with the supply at the wrong end of the step (an alignment error in the test). It is commented in the test file. No criterion was changed.

## E-T6 and E-T7: report only (no tolerance, never a target)
Data-centre electricity used, TWh a year:

| Build rate | 2026 | 2030 | 2035 | 2040 | 2060 | Share of supply in 2030 | Demand / use in 2040 |
|---|---|---|---|---|---|---|---|
| 15% a year | 558 | 976 | 1,962 | 3,946 | 11,695 | 2.8% | 153 |
| 30% a year | 631 | 1,801 | 6,686 | 10,440 | 11,695 | 5.1% | 52 |
| 50% a year | 727 | 3,683 | 9,975 | 10,440 | 11,695 | 10.5% | 52 |

For comparison only: the IEA's April 2026 report gives 485 TWh for 2025 (F3's calibration point) and 950 TWh for 2030; its World Energy Outlook 2026 gives about 1,000 TWh for 2030 (read in the IEA's overview page) and about 1,500 TWh for 2035 (read in a news report only).

## What this shows and what it does not
- **Measured:** electricity used is now bounded by something physical. At 15% a year the 2030 value (976 TWh) is of the size the IEA projects; at 30% and 50% it is two to four times larger. From about 2040 the outer share of supply binds in the two faster cases.
- **Measured:** S3 still asks for far more than can be powered: 52 to 153 times the electricity used in 2040. The investment rule keeps buying compute it cannot run. That is what step E2 addresses.
- **Inferred, not tested:** the E-T4 failure has the same cause as the B1 failure of Track A (less power, lower output, a different split of investment, more compute a few years later). No experiment isolating the cause was run.
- **Not shown by this:** that 15% a year is the right build rate. It is a provisional setting; the range is still to be justified from capacity histories (D-066).
- **Unchanged:** every label. Compute and electricity outputs stay withheld on the site. S3's long-run output was not examined here.
