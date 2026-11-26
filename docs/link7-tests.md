# Link 7, World3 to emissions: readings and tests, written before the code

Written 2026-11-26. The editor wrote "merge 24, and link 7 with your recommendations": fossil CO2 = World3 industrial output x an intensity fitted to 1970 to 2024 and extended at its fitted trend; hindcast tolerance 10% on yearly fossil CO2 over 1970 to 2024, set before the fit is seen. Plan: `docs/links-3-4-6-7-plan.md`.

**What was seen before these tests were written.** World3's standard run (industrial output peaks about 2015 and falls). The results of link 6. **Not seen:** any fit of the intensity, any hindcast figure, any warming result of this link.

## What the link is
- **Activity:** World3 industrial output `io` (the model's own dollars a year), 2004 parameter set, D-031 group, for any setting of the three World3 levers.
- **Observed fossil CO2:** the "CO2 FFI" series that FaIR itself is given for 1970 to 2024 (the pinned emissions file, with Global Carbon Budget values for 2023 and 2024, as in `ClimateSetup`). Not committed; read from the FaIR cache.
- **Intensity:** `k(t) = exp(a + b t)`, Gt CO2 per model dollar, with `a` and `b` fitted by least squares on the logarithm of observed CO2 over the standard run's `io`, 1970 to 2024. Two parameters, stored in `f3/data/link7_intensity.json` with the fit's error figures. Extended after 2024 at the same trend.
- **Replacement, not addition:** from 2026 the prescribed fossil CO2 is replaced by `io(t) x k(t)` for the chosen World3 run. Up to and including 2025 nothing changes. No harmonisation at the join; the step at the join is reported.
- **One-way and off by default.** Warming does not feed back into this World3 run through the link (the climate-damage coupling is a separate switch).
- **Unchanged and still labelled:** non-CO2 emissions and land-use CO2 are prescribed (D-021); the climate starts about 0.04 to 0.07 K below observed (D-030).
- **With link 6 on as well:** link 6's addition is added on top of link 7's replacement, and the two are reported separately.

## Readings and tests (`tests/test_link7_world3_emissions.py`)
- **L7-T1, hindcast (the editor's tolerance).** `io(t) x k(t)` is within 10% of observed fossil CO2 in every year from 1970 to 2024. The fit is made on the same years (in-sample); that is stated in the report. A failure is recorded with its size and years, not adjusted.
- **L7-T2, switch-off invariance.** No replacement: the emissions table is identical. A replacement equal to the prescribed values: warming and concentration equal to 1e-9 (small ensemble).
- **L7-T3, history.** Every emission up to and including 2025 is unchanged exactly; warming up to 1 January 2026 unchanged to 1e-9.
- **L7-T4, mass conservation.** FaIR's fossil CO2 input for 2026 to 2099 equals `io x k` year by year to 1e-9 relative; no other species is touched.
- **L7-T5, sign.** A World3 path with half the industrial output from 2026 gives lower warming in 2100 than the standard path (small ensemble). Control: the same comparison with the paths swapped must fail.
- **L7-T6, stored parameters.** `a` and `b` in the stored file equal a fresh fit to 1e-9.
- **L7-T7, with link 6.** Fossil CO2 input = link 7's replacement + link 6's addition, to 1e-9.
- **Report only:** the step at the join (2025 prescribed against 2026 computed); fossil CO2 and warming in 2050 and 2100 for the standard run and the other lever settings, with 841 members; in `audit/link7-world3-emissions.md`.

## What cannot be promised
- That the hindcast passes. One exponential trend may not follow 55 years of history within 10%.
- That the result is a credible emissions scenario. World3's industrial output falls after about 2015 in its standard run; emissions computed from it will fall too. That is what the link says, and it will be reported as a property of World3.
