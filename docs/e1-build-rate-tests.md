# Step E1 of the electricity module (D-066): readings and tests, written before the code

Written 2026-11-26, before `f3/sectors/s4_datacentre.py` is changed. The editor answered "Yes" on 2026-11-26 to starting E1 with the prototype's values as provisional settings: build rates of 15%, 30% and 50% a year and an outer share of 25%.

**What was already seen.** The exploratory prototype of 2026-11-25 (`audit/t0/dc_build_rate_prototype.py`) gave data-centre use of about 980 to 3,700 TWh in 2030 for these build rates. The tests below are therefore not blind to those figures. None of them uses a figure from the prototype as a target.

## What E1 is
- A new state, powered capacity `P` (TWh a year), starting at the 2025 calibration point (485 TWh).
- When demand exceeds `P`, `P` grows towards demand by at most `g_max` a year. `P` never falls.
- Electricity available = the smaller of `P` and `outer_share` x total supply.
- Two new parameters of `DCParams`: `g_max` (default infinite) and `outer_share` (default none, meaning the existing 5% cap). At the defaults the module is today's module.
- Nothing else changes: the interface to S3 (`supply_ratio`) and the outputs keep their names.

## Readings and tests (`tests/test_dc_build_rate.py`)
- **E-T1, off equals recorded.** With the defaults, every existing test of the slice and of M6 passes unchanged (`test_m2_slice`, `test_m6_*`, `test_dc_eta_cap`), and a direct comparison of the module with and without the new parameters at their neutral values agrees to 1e-9 on every output.
- **E-T2, conservation.** Over the grid `g_max` in {0, 15%, 30%, 50%}, `outer_share` in {5%, 25%}, supply x {1, 0.5}: electricity used never exceeds `P` nor `outer_share` x supply; `P` never falls; every output is finite and not negative.
- **E-T3, extremes.** `g_max` = 0 holds use at the 2025 level whenever demand is above it. `g_max` infinite with `outer_share` = 5% equals today's module to 1e-9.
- **E-T4, sign (the B1 reading).** Halving the build rate, or halving supply, never raises S3's usable compute in any year. Control: the reverse claim (a higher build rate never raises usable compute) must be false.
- **E-T5, step halving.** The A2.6 reading: halving the loop step changes data-centre electricity used by at most 0.1% at whole years, at `g_max` = 30% and `outer_share` = 25%. Reported; a failure is recorded as a strict expected failure with its size, not adjusted.
- **E-T6 and E-T7, report only.** Modelled use in 2026, 2030 and 2035 beside the IEA figures, in `audit/e1-build-rate.md`. No tolerance, never a target.

## What E1 does not do
- It does not make S3's output plausible in the long run (the prototype showed that).
- It does not change the investment rule (that is E2), the efficiency path (E3), or add water and land outputs (E4).
- It lifts no label. Compute and electricity outputs stay withheld on the site until the editor decides otherwise.
