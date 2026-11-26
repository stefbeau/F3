# Unlocking the weaknesses of links 3, 4, 6 and 7: sources found, readings written before the code

Written 2026-11-26. The editor wrote: "I want you to unlock the weaknesses for each by doing an extensive search for each. And if you can't expand, just report to me." Everything below is **Provisional (delegated)** and off by default. Readings are fixed here before any result is computed; where a number had already been seen, that is said.

## Sources found (2026-11-26) and how each was read
| Link | Source | Read how | Used for |
|---|---|---|---|
| 3 health | Bressler (2021), "The mortality cost of carbon", Nature Communications 12, 4467 | Publisher page and PDF through a parsing tool; **not read by eye**. Fig. 6 table of the increase in the global mortality rate at 1 to 5 degC above pre-industrial, low / central / high | A mortality function of global mean temperature |
| 3 yield | Hultgren et al. (2025), Nature 642, 644 | Abstract (eScholarship) and two university releases | A cross-check **with** adaptation; no coefficient taken |
| 4 | Acemoglu (2024) 0.07 points a year (US, 10 years), via a secondary table (Pictet); Filippucci et al. (OECD, 2024) 0.25 to 0.6 points a year of total factor productivity (publisher page); Goldman Sachs (2023) 1.25 points a year, world, via the same secondary table | Publisher page for the OECD; **secondary** for the two others | Sourced growth caps in place of hand-typed ones |
| 6 | IEA, Energy and AI (2025): 415 TWh in 2024, about 945 TWh in 2030, about 1,200 TWh in 2035, growth about 15% a year 2024 to 2030; CO2 from electricity for data centres about 180 Mt today, peak about 320 Mt by 2030, about 300 Mt by 2035. IEA, Key questions on energy and AI: 485 TWh in 2025, 950 TWh in 2030 | Publisher pages (search extracts) | An independent comparison for electricity and emissions |
| 7 | Nebel et al. (2023), Journal of Industrial Ecology, "Recalibration of limits to growth" (CC BY 4.0): Table 2, 21 of the 35 recalibrated parameters | One machine extraction of a PDF copy that has since gone offline; **not cross-checked**. The authors' repository does not contain the values. The text gives 111.8 for one parameter where the table gives 116.38 | A reference World3 run calibrated by others against data |

Not found: the coefficients beta1 and beta2 of Bressler's function (in the supplement); the 14 other recalibrated parameters; any measured bound on S3's own output.

## Link 3, health: mortality multiplier (L3H)
From 2025 the mortality of all four World3 age groups is multiplied by `(1 + d(T(t))) / (1 + d(T(2025)))`, where `d` is Bressler's increase in the mortality rate, linearly interpolated between the tabulated degrees: central 0.001, 0.002, 0.013, 0.037, 0.070 at 1 to 5 degC; high 0.003, 0.013, 0.045, 0.101, 0.180; low 0.000, -0.003, -0.007, -0.012, -0.018 (zero at 0 degC; held at the 5 degC value above). Counted from 2025 because World3's mortality already contains the warming to date. Left out and said so: age structure (the burden falls mostly on the old; here it is spread evenly), everything that is not temperature-related mortality, income effects.
- **L3H-T1** off: all 29 states equal the group alone to 1e-9. **L3H-T2** flat warming: no effect (1e-9).
- **L3H-T3** on a path stepping from 2 to 4 K the multiplier is `(1 + d(4)) / (1 + d(2))` for each option (1e-12).
- **L3H-T4** with the recorded warming, population in 2100 is lower for high than for central, and lower for central than with the link off; for **low** it is not lower than off (the low estimate is a net fall in mortality). Control: multiplier forced to 1 makes the comparison fail.
- **L3H-T5** nothing changes before 2025 (1e-9). **L3H-T6** with yield and output damage on as well: finite, non-negative.

## Link 3, yield: correction of an earlier statement
`audit/link3-link4.md` called the loss "an upper reading". Hultgren et al. measure losses **with** observed adaptation and report, for a high-emissions path, calories from staple crops 24% lower in 2100; that is not smaller than link 3's central option. The statement is corrected in the report, visibly. No test: no coefficient is taken from that paper (its per-degree figure is a share of recommended consumption, not of yield).

## Link 4: sourced caps (L4S)
`SOURCED_CAPS = {acemoglu_2024: 0.0007, oecd_low: 0.0025, oecd_high: 0.006, goldman_world: 0.0125}` (a year). These are 10-year estimates of productivity growth for the US, the G7 or the world, **extended here to 2100 and applied to World3 industrial output: an extrapolation**. 
- **L4S-T1** the four values are the published ones. **L4S-T2** cap respected for each. **L4S-T3** industrial output in 2040 rises in the order acemoglu, oecd_low, oecd_high, goldman.
- **Report, and the test of whether the weakness is removed:** the number of years in which the cap binds. Seen already: S3's uplift is about 1.9 in 2030, so every one of these caps is expected to bind from the start. If so, the weakness is **not** removed: the result is the sourced cap, and S3 still contributes nothing.

## Link 6: comparison with the IEA (L6V)
Setting: build rate 15% a year (the IEA's own growth rate 2024 to 2030), outer share 25%, standard supply.
- **L6V-T1 (number already seen: 976 TWh)** modelled electricity in 2030 within 10% of 945 TWh.
- **L6V-T2 (not seen)** modelled electricity in 2035 within 25% of 1,200 TWh.
- **L6V-T3 (not seen)** modelled CO2 of data centres (electricity used x the link's carbon intensity) within 30% of 320 Mt in 2030 and within 30% of 300 Mt in 2035.
- **L6V-T4** the baseline of 485 TWh equals the IEA's 2025 figure.
Tolerances are mine, set now. A failure is recorded, not adjusted.

## Link 7: a reference run calibrated by others (L7N)
World3 is run with the 21 extracted values (18 exist in F3's port under the same name; `pptd` is applied to `pptd1` and `pptd2`, `alic1` to `alic1` and `alic2`, `faipm` to `fipm`; `pl` is unchanged at 0.10). It is **a partial and unverified copy** of Recalibration23, named `nebel_partial`.
- **L7N-T1** its industrial output is closer to observed world GDP 1970 to 2024 than the standard run's (rms log distance below 0.1775).
- **L7N-T2** with the intensity fitted on it, the hindcast of fossil CO2 1970 to 2024 is within 10% in every year.
- **L7N-T3** the step from the prescribed 2025 value to the computed 2026 value is within 5%.
If T1 fails, the run is not used as a reference and T2 and T3 are reported only.

## Link 6, added after the first run (POST-HOC, labelled): a build rate that follows the IEA
Seen before writing this: with 15% a year throughout, electricity is 926 TWh in 2030 (L6V-T1 met) but 1,863 TWh in 2035 against the IEA's 1,200 (L6V-T2 FAILED), and CO2 is 347 Mt in 2030 and 637 Mt in 2035 against 320 and 300 (L6V-T3 FAILED on 2035). Those failures stand. Proposal: `IEA_BASE_SCHEDULE` = 15% a year from 2025, then 4.9% a year from 2030 (my arithmetic: (1200 / 945)^(1/5) - 1), kept after 2035 for want of any later figure. **This is a calibration to the IEA Base Case, not a validation against it.**
- **L6C-T1** a schedule with the single entry (2025, 15%) gives the same electricity as the plain 15% setting (1e-12); no schedule is the committed behaviour.
- **L6C-T2** with the schedule, electricity is within 10% of 945 TWh in 2030 and of 1,200 TWh in 2035 (near to true by construction).
- **L6C-T3** CO2 within 30% of 300 Mt in 2035. My arithmetic before running says about +35%, so I expect this to fail: the link's intensity is the world average of the Earth4All path (0.34 kg/kWh in 2035), and the IEA's implied figure for data centres is 0.25.
