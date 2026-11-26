# Links 3, 4, 6 and 7: what a search of the literature unlocked, and what it did not

Date: 2026-11-26. Readings and tests were committed before the code (ffc860a; the post-hoc link 6 readings in a second commit before their code): `docs/links-unlock-tests.md`, `tests/test_links_unlock.py`. Figures: `audit/data/links-unlock.json`. Everything is off by default and Provisional (delegated). World3 2004 set, standard levers; recorded FaIR warming (1.35 K in 2025, 2.86 K in 2100).

## Summary
| Link | Weakness | After the search | Status |
|---|---|---|---|
| 3 | Health not built | Built from Bressler (2021): mortality of all age groups scaled with global mean temperature | **Unlocked**, with caveats |
| 3 | Yield: one abstract, no adaptation | Cross-checked with Hultgren et al. (2025), which includes adaptation; an earlier statement of mine corrected | Improved; still no hindcast |
| 4 | The cap is hand-typed and decides the result | Caps now come from published estimates; they still bind in every year from 2027 | **Not unlocked** |
| 6 | No independent comparison | Compared with the IEA: agrees to 2030, fails in 2035; a build rate that follows the IEA then meets all three readings (post-hoc) | **Unlocked to 2035**, as a calibration |
| 7 | Reference run picked by me from six settings | A published recalibration of World3 tried as reference: worse than the standard run | **Not unlocked** |

## Link 3, health
Source: Bressler (2021), Nature Communications 12, 4467, Fig. 6: increase in the global mortality rate at 1 to 5 degC above pre-industrial, fitted by its author to three studies (WHO 2014, Climate Impact Lab 2019, Gasparrini et al. 2017). **The table was read through a parsing tool, not by eye; the coefficients of the underlying quadratic are in a supplement I could not open.** All six readings met.

| Option | Mortality multiplier in 2100 | Population 2050 | Population 2100 |
|---|---|---|---|
| low | 0.9946 | +0.03% | +0.21% |
| central | 1.0100 | -0.01% | -0.34% |
| high | 1.0336 | -0.09% | -1.19% |

Yield and health together (both central): population -0.43% in 2050, -3.98% in 2100. The health effect is small beside the yield effect. Left out: age structure (spread evenly here), all mortality that is not temperature-related, income. The low option is a net fall in mortality, as in the source.

## Link 3, yield: correction
**Correction (2026-11-26).** `audit/link3-link4.md` and the site text call link 3's loss "an upper reading" because Zhao et al. exclude adaptation. Hultgren et al. (2025, Nature 642, 644) measure losses with observed adaptation: 120 kcal per person per day per degree, 4.4% of recommended consumption, and for a high-emissions path staple-crop calories 24% lower in 2100 (11% with rapid cuts). That is not smaller than link 3's central option (-7.4% of land yield in 2100 on a path that warms 1.5 K after 2025). **"Upper reading" was not supported; the earlier text is wrong on this point.** No coefficient was taken from Hultgren: its per-degree figure is a share of consumption, not of yield. Still no hindcast.

## Link 4: sourced caps
| Cap | Source | Cap binds | Bounded uplift 2099 | Industrial output 2040 / 2100 | Population 2100 |
|---|---|---|---|---|---|
| 0.07% a year | Acemoglu (2024), US; secondary | every year from 2027 | 1.05 | +0.9% / +7% | +1.2% |
| 0.25% | OECD (Filippucci et al. 2024), low | every year from 2027 | 1.20 | +3.2% / +25% | +4.2% |
| 0.6% | OECD, high | every year from 2027 | 1.55 | +7.8% / +65% | +10.4% |
| 1.25% | Goldman Sachs (2023), world; secondary | every year from 2027 | 2.48 | +16.5% / +144% | +21.2% |

All three readings met. **The weakness is not removed.** The caps are now published numbers instead of mine, but each binds in all 73 years, so S3 still contributes nothing but the start year. The sources are 10-year estimates of productivity for the US, the G7 or the world; running them to 2100 on World3 industrial output is an extrapolation. What would remove the weakness is a bound on S3's own output from something measured (test A1.3), and the search found none.

## Link 6: comparison with the IEA
Setting: 15% a year (the IEA's own growth rate for 2024 to 2030), outer share 25%.

| Reading | Model | IEA | Result |
|---|---|---|---|
| L6V-T1 electricity 2030, 10% | 926 TWh | 945 | Met (-2%) |
| L6V-T2 electricity 2035, 25% | 1,863 TWh | 1,200 | **FAILED** (+55%) |
| L6V-T3 CO2 2030 and 2035, 30% | 347 and 637 Mt | 320 and 300 | **FAILED** on 2035 (+8%, +112%) |
| L6V-T4 baseline 485 TWh | 485 | 485 (2025) | Met |

Both failures are recorded as strict expected failures; tolerances unchanged. Cause, from the numbers: the IEA slows after 2030 and a constant rate does not. For 2025 the link gives 205 Mt against the IEA's "around 180 Mt today" (+14%).

**Post-hoc, labelled:** `IEA_BASE_SCHEDULE`, 15% a year to 2030 then 4.9%. This is a calibration to the IEA Base Case, not a validation.

| Reading | Model | IEA | Result |
|---|---|---|---|
| L6C-T1 single-entry schedule equals the plain setting | | | Met |
| L6C-T2 electricity 2030 and 2035, 10% | 874 and 1,110 TWh | 945 and 1,200 | Met (-7.5%, -7.5%) |
| L6C-T3 CO2 2035, 30% | 380 Mt | 300 | Met (+27%); **I had predicted a failure (+35%) and was wrong** |

With the schedule: 2,275 TWh in 2050 and 8,778 TWh in 2099 (the 4.9% is kept after 2035 with no source); extra CO2 0.15 Gt in 2030, 0.47 Gt in 2050, 1.31 Gt in 2099; **warming +0.022 K in 2100** (841 members; base 2.858 K). The electricity no longer depends on S3's unvalidated compute path before the cap, only on the schedule, because demand exceeds the cap throughout. So link 6 now says: "if data centres follow the IEA Base Case to 2035 and keep that pace, with the world-average carbon intensity of the Earth4All path".

## Link 7: a reference run calibrated by others
Nebel et al. (2023) recalibrated World3 against eight data series. 21 of their 35 values were applied (`NEBEL_PARTIAL`), from one unverified machine extraction.

| Reading | Result |
|---|---|
| L7N-T1 closer to observed GDP than the standard run | **FAILED**: rms log distance 0.2457 against 0.1775 |
| L7N-T2 hindcast within 10% | **FAILED**: largest 40.1% (2024), 35 of 55 years outside |
| L7N-T3 join step within 5% | **FAILED**: -5.6% |

Not used. I do not conclude anything about the published recalibration: 14 parameters are missing, one table value disagrees with the paper's own text, their industrial-output target was a production index and not GDP, and their model is World3-03 while F3's port follows the 1974 equations with the 2004 parameter set. Link 7 keeps variant B and its stated weaknesses: reference chosen by me from six settings, and a join step outside 5% for four of six runs.

## What I could not find
- Bressler's coefficients (supplement); the 14 other recalibrated parameters; any IEA figure after 2035.
- Any measured quantity that bounds S3's output. This is the one weakness that blocks link 4 and it is a model question, not a literature question.
- A hindcast for the yield link: by construction it is inactive before 2025.
