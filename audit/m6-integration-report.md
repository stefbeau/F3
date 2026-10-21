# M6 minimal integration report (2026-10-21; D-051, `docs/m6-minimal-plan.md`, `docs/m6-tests.md`)

**What was built.** One loop (step 0.25 year, 1900-2100) with the World3 group (D-031), the recorded FaIR replay (D-021 A: emissions prescribed), S3 under R3 with the data-centre module and the Earth4All supply series (held at initial values before 2025 by `DelayedStart`), and S7 output-only (`s7_feed` adapter, `s7_given` constants: unemployment 0, redistribution 0, both illustrative). One real coupling added by D-051: climate damage to World3 industrial output, `io = io_gross x (1 - Omega(T))`, D-007 central by default, from 2025, **default OFF**, level-of-output effect, no new coefficient. Code: `f3/sectors/m6_integrated.py`, `world3_group.py`, `world3.py`, `w3_capital.py`. S3's economy and World3's are two models of the same world and are **not reconciled**. All results are conditional scenarios, not forecasts.

## Tests (readings and windows fixed in `docs/m6-tests.md` and the test files before the code; nothing adjusted after a result)

Suite on the merged result, run from the main checkout with `F3_FAIR_DATA` and `F3_GATE_BUNDLE` set, nothing else running: **406 passed, 0 failed, 45 xfailed (all strict, all recorded failures), 0 skipped, 0 XPASS** (500 s).

| Group | Result |
|---|---|
| Damage coupling (`tests/test_m6_damage_coupling.py`, 43) | all pass: OFF equals the pre-change snapshot to 1e-9 (both sets, 29 states, 1900-2100); zero warming equals OFF; multiplier 1 before 2025; sign test on `ic` and `io` in 2050 and 2100 (ON < OFF, doubled warming < recorded-like) with a control and a mutation that fail as required; low > central > high; finite and non-negative over the full grid |
| A6.1 (World3 in the loop) | pass: 29 states equal the group alone to 1e-9, both sets; within 2% of WorldDynamics.jl |
| A6.3 invariance | pass: damage OFF, S3 alone (1e-9), S7 alone on the same inputs (1e-9), live 20-member S6 against its recording to 2030 (1e-9) |
| A6.4 extremes | pass: zero AI share (`Q[k] = Q[k-1] exp(-0.3)` to 1e-9, demand non-increasing), unlimited electricity (supply ratio 1), zero investment, finiteness over World3 x S3 damage grid |
| A6.2 sign tests | pass: R1 (`frac_automated` 2029-2031, race > low), B1 (`usable_compute` 2027-2035, half <= base, strict at least once), B2 (S3 `gwp` and World3 `ic` in 2100, high < low), R2 via S3 (S7 inequality change in 2060 positive; zero for a constant labour share); every control fails as required |
| A6.6 initialisation, labels | pass |

**Failures recorded.** One, in a test I wrote: the first R2-via-S3 control kept the real warming input and gave an inequality change of 5.8e-4 in 2060 instead of 0 (warming raises tension, tension triggers the delayed policy response, the response lowers inequality). The mistake was in the test's construction; the reading meant to isolate the labour-share driver, so the control now holds warming at 0 as S7's own R2 test does. The failing version is in commit `a39237d`; the correction is a dated note in `docs/m6-tests.md`. No threshold changed and the positive assertion was untouched. No model test failed.

**xfail and skip accounting.** Main had 45 strict xfails before the merge; the merged run has 45 (none gone, none passing). The earlier branch-only run (399 passed, 15 skipped, 36 xfailed) was made in the worktree without `F3_GATE_BUNDLE`; the 15 skips are tests that need the GATE bundle or the FaIR files, and with both caches set they ran: 9 became the strict xfails above and the rest pass. I inferred the split from the counts (399 + 15 + 36 + 1 deselected = 451 = 406 + 45) and did not diff the two skip lists.

## A6.5 run time
- Integrated run with the recorded climate replay, 1900-2100: 2.2 s and 3.3 s (two repeats, measured alongside nothing else).
- **Live 841-member S6 inside the integrated loop: not measured in M6.** The attempt was stopped by the system for low memory and the editor decided not to re-run it. The D-021 measurement stands: 1,451 s per 1980-2100 loop, so a thousand runs with exact 841-member re-runs would take about 500-570 h on one core (`audit/m2-d021-measurement.md`). D-021 is to be revisited before Phase 3 Monte Carlo and is not decided here.
- The replay makes one integrated scenario cheap while emissions stay prescribed; once any F3 sector feeds emissions, the replay is no longer exact.

## Not done, by instruction
`docs/phase-2-review.md` is not written. S7 stays output-only. The Explorer site is unchanged.
