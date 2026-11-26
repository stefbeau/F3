# Step E2 of the electricity module (D-066): readings and tests, written before the code

Written 2026-11-26, after step E1 and before `f3/sectors/s3_rule_r3.py` is changed. The editor asked on 2026-11-26 to proceed "in proper order" (E1, then E2, then the links).

**What was already seen.** The prototype of 2026-11-25 showed that this form of E2 cut the unpowered overhang in 2040 by a factor of 6 to 13 and that long-run output stayed implausible (and rose). E1's results are in `audit/e1-build-rate.md`. The tests below are not blind to those figures; none uses them as a target.

## What E2 is (first form of the proposal)
- A new lever of the investment rule R3, `power_aware`, **default off**. R3 is the editor's rule (D-028): this is a labelled variant, not a change of the rule.
- When on: the share of output spent on compute is multiplied by the share of installed compute that can be powered (`supply_ratio`, the signal the data-centre module already sends to S3). The freed share goes to consumption. Nothing else in R3 or in S3 changes.
- The second form of the proposal (the freed share builds power capacity) is not built: it needs a cost of power capacity, a parameter with no source yet.

## Readings and tests (`tests/test_r3_power_aware.py`)
- **E2-T1, off equals recorded.** With the lever off, the shares equal those of the rule before the change to 1e-12 over a grid of states, whatever power ratio is passed; the existing S3, slice and M6 tests pass unchanged.
- **E2-T2, shares stay valid.** With the lever on, over a grid of states and power ratios from 0 to 1: every share is at least 0, the first five sum to 1, a ratio of 1 changes nothing, a ratio of 0 gives a compute share of 0, and only the compute and consumption shares differ from the lever-off shares.
- **E2-T3, sign (E-T4 with E2 on).** At an outer share of 25%: a slower build rate (15% against 30%, 30% against 50%) or half the supply never raises S3's usable compute, and never raises its compute stock, in any year. Controls: each reverse claim must be false.
- **E2-T4, overhang.** At each build rate, electricity demanded divided by electricity used in 2040 is lower with E2 on than off.
- **E2-T5, finite.** Every S3 and data-centre output is finite over the three build rates with E2 on.
- **Report only:** electricity used, the overhang and S3's output in 2030, 2040 and 2060 with E2 on and off, in `audit/e2-power-aware.md`. No tolerance.

## What E2 does not do
It lifts no label and makes no claim that S3's output becomes plausible. If output stays outside plausible ranges, the report says so.
