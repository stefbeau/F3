# Link 7, variant B: a POST-HOC proposal, written after the first form failed its hindcast

Written 2026-11-26, **after** `audit/link7-world3-emissions.md`. The editor wrote: "I want this one to work alongside with the rest. Try and find additional data to make it work and unblock anything else. All links need to work properly." The first form's hindcast (L7-T1) **stays failed and recorded**. Nothing below changes that test, its tolerance or its result. This is a new form with its own readings, fixed here before it is run.

## What I had seen when writing this (so the reader can discount it)
- The first form's errors by year: within 10% until 1993, up to +14% around 2000, then -27% in 2024.
- That the standard World3 run's industrial output falls after about 2015, and that with double resources the computed emissions in 2026 are above the prescribed value.
- **Not seen:** any comparison of World3 runs with observed output; any fit on a run other than the standard one; any result of the form below.

## Why the first form failed, as far as the evidence goes
Measured: the standard run's industrial output leaves the observed path after about 2015. Inferred, not tested: an intensity fitted on a run that follows observed output more closely would follow observed emissions more closely.

## The additional data
World GDP at constant 2015 US dollars, 1960 to 2025, World Bank (already in the repository: `site/data/history.json`, built under D-057). It is **independent of the emissions series** the hindcast uses. GDP is not industrial output; it is the closest observed series the repository holds, and the difference is a stated limit.

## Variant B
1. **Reference run, chosen by a rule fixed here.** Among the 27 settings of the three World3 levers, the reference is the one whose industrial output, indexed to 1970, is closest to observed GDP indexed to 1970 over 1970 to 2024 (smallest root-mean-square difference of the logarithms). The emissions series plays no part in the choice.
2. **Intensity.** `k_B(t) = exp(a + b t)` fitted as before, but on the reference run.
3. **Join.** For any World3 run, fossil CO2 from 2026 is `io(t) x k_B(t) x h`, where `h` is the one constant that makes the run's 2025 value equal the prescribed 2025 value. So no run steps at the join; what a run carries into the future is the shape of its industrial output and the intensity trend. `h` is reported for every run shown: it says how far that run's present is from the observed present.
4. Everything else as in the first form: one-way, off by default, replaces fossil CO2 from 2026, nothing else touched, same labels.

## Readings and tests (`tests/test_link7_variant_b.py`), fixed before the run
- **L7B-T1, hindcast (the editor's 10%, unchanged).** On the reference run, `io(t) x k_B(t)` (without `h`) is within 10% of observed fossil CO2 in every year from 1970 to 2024. A failure is recorded.
- **L7B-T2, join.** For the reference run `h` is within 10% of 1. For every run, the value in 2026 is within 5% of the prescribed 2025 value.
- **L7B-T3, selection is reproducible** and does not read the emissions series: the stored reference equals a fresh selection.
- **L7B-T4, switch-off, history, mass conservation, sign with control:** as L7-T2 to L7-T5, for this form.
- **Report only:** the reference chosen and its distance from observed GDP; `h`, fossil CO2 and warming (841 members) for the five settings reported before.

## What this form gives up
With the join constant, the link no longer says anything about the **level** of a run's emissions today: every run starts from the observed level. It transmits only how each World3 run's industrial output moves from 2025 on. A run whose past differs from reality (all runs with changed resources differ from 1900) is treated as if it had arrived at today's emissions.

## If it fails
It is recorded, and link 7 stays a link whose validation failed.
