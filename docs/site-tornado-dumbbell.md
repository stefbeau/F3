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

## 4. Results (2026-11-27, after the build)

**Tests.** `tests/test_site_tornado_dumbbell.py`: 22 passed. All site tests: 218 passed (196 before this change). The full suite was not run: no model code was touched. All readings R-T1 to R-T6 and R-D1 to R-D4 are met; none was changed after the code was written.

**What the range chart shows for the standard run, damage off, in 2100** (printed by the page functions from the data file; each line is lowest to highest, widest first):

| Measure | Setting | Lowest | at | Highest | at |
|---|---|---|---|---|---|
| Population | Land yield factor after 1975 | 369 million | 2.0 | 3.5 billion | standard (1.0) |
| Population | Non-renewable resources at the start | 2.51 billion | half | 3.5 billion | standard |
| Population | Pollution generation factor after 1975 | 3.33 billion | 0.25 | 3.5 billion | standard (1.0) |
| Population | Climate damage to industrial output | 3.45 billion | high | 3.5 billion | off |
| Industrial output | Non-renewable resources at the start | 6.3 billion | half | 342 billion | double |
| Persistent pollution | Non-renewable resources at the start | 0.108 | half | 6.56 | double |

Read with care: a higher land yield factor gives a much LOWER 2100 population in these runs, and the standard value is the highest of the three for population. That is what the published runs contain (runs with changed parameters are not compared with WorldDynamics.jl); the chart only makes it visible. It is not a finding about the world.

**What the dumbbell shows for the default pair** (A: Standard, central damage; B: Combined, central damage; 2100, change against the standard run): industrial output -2.8% against +238.1% (240.8 points apart), persistent pollution -1.3% against +162.8%, resources remaining +1.2% against +103.8%, population -0.5% against -72.5%. The same numbers as the bars and the delta table.

**Checked live** (headless Chrome through the DevTools protocol, `file://`, 390 and 1280 px, dark and light): no page-level horizontal overflow; no chart text below 13 px and none outside its SVG; no console or script errors; the measure selector redraws the range chart; the chart follows the rail (tested at levers 2.1.1 with central damage); the data table opens; the CSV carries raw numbers and the caveats; A equal to B equal to the baseline shows the "nothing to draw" card. Screenshots: `docs/img/explorer-v03-explorer-range-*.png`, `explorer-v03-compare-dumbbell-*.png`.

**Not checked:** a physical phone, a screen reader, a colour-blindness simulation, the PNG download, any browser other than headless Chrome.

**Two display choices made on the way** (no reading touched): the range chart prints fractions with three significant figures, so the two ends of a narrow range do not print as the same number; grid lines and the reference mark are drawn across each bar or pair only, so no line runs through a label.
