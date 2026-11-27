# Explorer: two new chart types, a range chart ("tornado") and a dumbbell (D-070, Provisional (delegated))

**Status:** readings and tests written 2026-11-27, before any chart code. Branch `site-tornado-dumbbell`. **Not merged, not deployed.** Display layer only: no model code, no parameter, no model run, no new number. Everything is drawn from `site/data/explorer.json` (the 108 World3 runs already published).

**Why.** The editor asked on 2026-11-27 for more kinds of visualization on the site, taken from an article on unusual charts, and agreed to start with these two. `docs/design-guidelines.md` section 3 already names the dumbbell for "scenario comparison at one date"; section 11 records that the Compare bars are in a fixed order, not sorted.

## 1. Range chart ("Which setting moves the result most?"), Explorer, under Details

- **What it draws.** For one measure in the last model year, one row per setting the rail offers: the three World3 levers and the climate-damage option. Each row is a horizontal bar from the lowest to the highest value that the measure takes when **that one setting** goes through all its values and **every other setting stays as chosen in the rail**. A vertical line marks the chosen run. Rows are sorted by the width of the bar, widest first.
- **Where the numbers come from.** For lever `i` with chosen levers `L` and damage `d`: the runs `L` with `L[i]` replaced by 0, 1, 2, damage `d`. For the damage row: levers `L`, damage off, low, central, high. No interpolation, no new run.
- **What it is not.** The settings are scenario choices of D-046 and the options of D-007. The bar is the range **among the settings the Explorer offers**. It is not an uncertainty range, not a likelihood, and not a sensitivity analysis of the model's parameters. Changing one setting at a time hides combined effects; the Compare page shows combinations. The chart must say all of this without a click.
- **Labels that must stay** (CLAUDE.md, standing delegation): high is not the upper end of the literature; damage is a level-of-output effect; damage-on runs and runs with changed parameters are not compared with WorldDynamics.jl; no health or yield effect of warming; a model run, not a forecast.

### Readings (fixed before the code)
- **R-T1** Every bar end equals the minimum or maximum, computed independently in Python from the data file, of the runs named above; the chosen run's value lies inside every bar.
- **R-T2** Rows are sorted by bar width, widest first; equal widths keep the order of the data file (levers, then damage). The title names the first row and its two end values.
- **R-T3** With a different chosen run the rows are recomputed around that run (tested at levers 2, 1, 1 with central damage).
- **R-T4** `null` is no value, never zero: a missing value is left out of the range; a row with fewer than two values has no width, is listed last and is drawn as "no value". A measure that no setting changes gives a title that says so.
- **R-T5** Synthetic data with different values gives a different title, and none of the real values appears in it.
- **R-T6** The caveat and the text alternative carry the sentences under "What it is not" and "Labels that must stay".

## 2. Dumbbell ("Where A and B part"), Compare page

- **What it draws.** One row per measure that differs from the baseline. On a shared axis of "change in the last model year against the standard run (%)": a marker for scenario A, a marker for scenario B, a line joining them, and a thick zero line (the baseline). Rows are sorted by the distance between A and B in percentage points, widest first.
- **Where the numbers come from.** `compareRows` (already tested): `dA` and `dB` times 100; the gap is their difference. Identical rows (warming) are not drawn, as for the bars.
- **It adds to the bars, it does not replace them.** The diverging bars, the table and their tests are unchanged.
- **Not by colour alone.** A is a circle and B is a square, each with its letter, in the scenario colours of design-guidelines 4.1.

### Readings (fixed before the code)
- **R-D1** Each marker equals `dA x 100` or `dB x 100` of `compareRows`; the gap equals B minus A in percentage points.
- **R-D2** Rows are sorted by the absolute gap, widest first; identical rows are left out. The title names the first row and its gap.
- **R-D3** A equal to B gives a title that says the two scenarios coincide; nothing is drawn as a zero-length line read as a result.
- **R-D4** `null` is no value: such a row has no gap, is listed last and is drawn as "no value".

## 3. Common to both
- Card tools as on every chart: finding title generated from the data, text alternative, data table, PNG, CSV with the caveats, assumptions link.
- Text at 13 px or more; scenario and accent colours from the stylesheet tokens only; no page script holds a model number (the existing scan in `tests/test_site_v02_core.py` covers the two page scripts).
- Tests: `tests/test_site_tornado_dumbbell.py`.

## 4. Results
*(Filled in after the build; see the end of this file.)*
