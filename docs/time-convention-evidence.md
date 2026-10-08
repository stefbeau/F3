# F3 — Time convention: the evidence (M0, review item 16)

**Question.** In World3, what does `t = 1970.0` mean on a calendar: 1 January 1970, the middle of 1970, or something else? It matters when model values are compared with data, because population statistics are stock values at a stated date (the UN publishes both 1 January and 1 July values) and flow statistics are totals over a calendar year.

**This page states evidence only. It proposes no convention.** The proposal is a separate Proposed decision (N3), written after this page, so that the evidence can be read first.

## 1. What the references say about it

| Source | Finding | How it was checked |
|---|---|---|
| WorldDynamics.jl v1.0.0 (source, README, docs) | **No statement** about what a time value means on a calendar | Searched `src`, `README.md` and `docs` for "January", "mid-year", "start of year", "beginning of year", "end of year", "calendar": no hit. A search by keywords cannot rule out other wording, so this is "none found", not "none exists" |
| PyWorld3 1.1 (source) | **No statement** | Same search over `pyworld3/*.py`: no hit |
| *Dynamics of Growth in a Finite World* (1974), Appendix A | **Not read in this review** | The book is not in the repository and was not opened; whatever it says about the time axis (for example the model's start and step) is unverified |

## 2. How time enters the equations (read from the Julia source)

World3 is a continuous-time model solved at a time step. `t` is a continuous variable; states are stocks at the instant `t` and flows are rates per year at that instant. The places where a calendar value of `t` matters are:

- **Switches** `clip(a, b, t, threshold)` take the value `a` when `t >= threshold`. The population sector has four (1940 for health-service technology, and 4000 three times). Other sectors have switches at 1975 (`pyear`) and, in the pollution and agriculture sectors, other thresholds. A switch at 1940 fires at the instant `t = 1940.0`, so a stock "at 1940" is the value just after the switch for flows but before it for stocks: the convention decides which side of the switch a labelled year falls on.
- **Exogenous exponentials anchored at 1900**: `0.7e11 * exp((t - 1900) * 0.037)` and similar (used only when a sector is run alone with its own placeholder inputs).
- **Initial values** are set at `t = 1900` (`t0 => 1900`); the initial population of 1.61 billion is a 1900 stock with no stated date within 1900.
- **Tables over time** exist only in the stand-alone pollution sector: its placeholder series of population, industrial output per capita and arable land are tabulated every 20 years from 1900 to 2100 (eleven points), without a stated date within the year.

Nothing in the equations distinguishes the start of a year from its middle: shifting the labelling of `t` by half a year changes no equation except where the integer thresholds sit, and those thresholds are themselves given as integers without a date.

## 3. What a half-year shift would change in comparisons (measured)

Model population from the WorldDynamics.jl reference (default options) against the UN World Population Prospects 2024 world total. UN values: 1 January from the age-group file `WPP2024_Population1JanuaryByAge5GroupSex_Medium.csv.gz`; mid-year approximated by the mean of the 1 January values of years Y and Y+1 (an approximation: it equals the UN's own mid-year spreadsheet value to the digits compared in 1970, 2000 and 2025). Values after 2023 are projections.

Four readings, percent (model minus observed, over observed):

| set | year | A: t=Y is 1 Jan, vs UN 1 Jan | B: t=Y is 1 Jan, vs UN mid-year | C: t=Y is mid-year, vs UN 1 Jan | D: t=Y is mid-year, vs UN mid-year | spread |
|---|---|---|---|---|---|---|
| 1974 | 1970 | +0.00 | -1.03 | +0.83 | -0.21 | 1.85 |
| 1974 | 2000 | -7.13 | -7.76 | -6.55 | -7.18 | 1.21 |
| 1974 | 2025 | -13.91 | -14.27 | -13.88 | -14.25 | 0.39 |
| 2004 | 1970 | +3.71 | +2.65 | +4.59 | +3.52 | 1.95 |
| 2004 | 2000 | -0.62 | -1.29 | +0.03 | -0.64 | 1.33 |
| 2004 | 2025 | -8.22 | -8.61 | -8.18 | -8.57 | 0.42 |

Readings A and D pair like with like (both on the same date); B and C mix a model date with a different observed date. **The population gaps quoted in D-015 (Finding 3) and D-019 correspond to reading B**, that is, the model value at `t = Y` against a mid-year observation. Under a start-of-year convention the matching comparison is A, which is 1.0 point higher in 1970 for both sets (1974: -1.0% becomes +0.0%; 2004: +2.6% becomes +3.7%) and 0.4 to 0.6 points higher in 2000 and 2025. Under a mid-year convention the matching comparison is D, which differs from B by at most 0.8 points. In no reading does the choice change which parameter set is nearer observed total population.

**Flows.** Model births per year at `t = Y` against the mean over `[Y, Y+1]` (what a calendar-year total would be) differ by 0.1% to 0.5% for 1970 and 2000, and by -0.5% (1974 set) and -1.0% (2004 set) in 2025.

**Age cohorts.** Not recomputed here. The cohort shares in the D-015 outcome note moved by at most 0.2 points between the 1 January and mid-year UN values, so the cohort conclusions are unaffected by the date basis.

## 4. One more observation, not discriminating

The model starts in 1900 with 1.6 billion people (its cohorts sum to 1.6e9 in the 1900 row of both runs). The UN historical-plot spreadsheet lists 1.65 billion for 1900 (a rounded figure from a historical source; the date basis within 1900 and the source's uncertainty were not checked). The gap of about 3% is larger than the half-year growth of the time, about 0.4%, so it cannot say which convention the model used.

## 5. What the evidence supports

- The equations and both reference implementations are silent on the date within the year; the convention cannot be derived from them. It is a labelling choice.
- The labelling choice moves total-population comparisons by up to about 2 points around 1970, about 1.3 points in 2000 and about 0.4 points in 2025, and calendar-year flow comparisons by up to about 1%. The 2.0% tolerance of D-004 applies to comparisons between F3 and its references run on the same time axis, where the convention cancels; it does not apply to comparisons with data, where it does not cancel.
- What remains unknown: what the 1974 book says about the time axis; whether either reference's authors intended a convention.

## 6. Method

`audit/t0/time_convention.py` (committed) reads `tests/fixtures/s1_reference_*_default.csv` and the UN age-group file (downloaded to a scratch folder outside the repository, not committed; its path is the script's argument), interpolates the model population linearly in time and forms the four readings above. Run: `uv run python audit/t0/time_convention.py <path to the UN .csv.gz>`.
