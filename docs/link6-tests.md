# Link 6, data-centre electricity to emissions: readings and tests, written before the code

Written 2026-11-26. The editor wrote "merge 21, 22 and 23, and link 6 with your recommendations": the carbon intensity is derived from the recorded Earth4All run, and the climate runs use all 841 members for six scenarios. Plan: `docs/links-3-4-6-7-plan.md`; literature note: `docs/links/L6.md`.

**What was already seen before these tests were written.** The intensity derived from the recorded Earth4All run (TLTL): 0.42 kg CO2 per kWh in 2025, 0.37 in 2030, 0.26 in 2050, 0.16 in 2100. The electricity paths of step E1 (`audit/e1-build-rate.md`). No warming result of this link.

## What the link is
- **Electricity:** data-centre electricity used, from S3 under R3 with the build-rate limit of step E1 (it must be on: without it the electricity is not bounded).
- **Intensity (the editor's choice):** CO2 from electricity divided by electricity produced, both from the recorded Earth4All.jl run, using Earth4All's own identities: fossil fuel for electricity x tonnes of CO2 per tonne of oil equivalent x (1 minus the captured share), over total electricity production.
- **Addition to emissions:** for each calendar year from 2026, extra fossil CO2 = (electricity used minus a baseline) x intensity, added to the prescribed "CO2 FFI" input of FaIR. Never negative.
- **Baseline (my assumption, Provisional, for the editor):** the 2025 level, 485 TWh a year, held constant. The prescribed emission path already contains some growth of data centres, of unknown size, so the addition is an **upper reading** of the extra emissions.
- **One-way.** Electricity is computed first, without the climate; the warming it adds does not feed back on the electricity. With the climate-damage switch on that return path would exist; it is not closed here.
- **Unchanged and still labelled:** non-CO2 emissions and land-use CO2 are prescribed (D-021); the climate starts about 0.04 to 0.07 K below observed (D-030).
- **Six scenarios (a change from the plan, stated here):** the plan said three AI settings by two supply cases. Step E1 showed that electricity used is set by the build rate, not by the AI setting (demand is 5 to 150 times use). The six scenarios are therefore the three provisional build rates (15%, 30%, 50% a year) by two supply cases (recorded supply, and half of it), with the central AI setting and an outer share of 25%.

## Readings and tests (`tests/test_link6_dc_emissions.py`)
- **L6-T1, switch-off invariance.** With no addition, the emissions table given to FaIR is identical to today's; with an addition of zero in every year, warming and concentration equal the stand-alone result to 1e-9 (small ensemble).
- **L6-T2, join and history.** The addition is zero up to and including 2025, so every emission up to 2025 is unchanged exactly, and warming up to 1 January 2026 is unchanged to 1e-9.
- **L6-T3, mass conservation.** The CO2 added to FaIR's input, summed over 2026 to 2099, equals the sum of (electricity used minus baseline) x intensity over the same years to 1e-9 relative.
- **L6-T4, sign.** A faster build rate gives at least as much cumulative extra CO2; warming on 1 January 2100 with the addition is not lower than without it, and not lower at 50% a year than at 15% (small ensemble). Control: a negative "addition" must lower warming, so the test can fail.
- **L6-T5, intensity.** Finite, positive and below 1 kg CO2 per kWh in every year from 2025 to 2100. (A bound, not a fit; the values were seen first, see above.)
- **L6-T6, one run equals yearly re-runs.** The sector re-runs FaIR from 1750 for every year (D-021). For this link one run to 2100 is read at every year. Reading: the two agree to 1e-9 on warming and concentration at 2030, 2050 and 2100 (small ensemble). If this fails, the six scenarios are run with yearly re-runs instead (about 22 minutes each).
- **Report only:** extra CO2 per year and cumulative, and the change in ensemble-mean warming in 2050 and 2100, for the six scenarios with 841 members, beside the 5 to 95% spread of the ensemble. In `audit/link6-dc-emissions.md`.

## What cannot be promised
That the added warming is larger than the ensemble's own spread. If it is not, that is the result.
