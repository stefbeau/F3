# F3 — Design guidelines for the public Explorer

Status: draft v0.1. Purpose: one reference for every visualization and layout decision in the public Explorer (https://stefbeau.github.io/F3/). Reviewed and approved by the editor-in-chief (Stéphane).

Sources of the principles: From Data to Viz (chart choice and caveats), Dashboard Design Patterns (layout and genres), ColorBrewer (palettes), Storytelling with Data (message and decluttering), Dataviz Inspiration (reference gallery).

## 1. Audience and genre

The Explorer serves the general public first, specialists second. It combines two dashboard genres:

- Narrative layer: preset scenarios with a clear message, readable without touching any control.
- Analytical layer: parameter controls and custom runs, available on demand.

Rule: a first-time visitor must understand something within 10 seconds without changing any parameter.

## 2. Page structure (top to bottom)

1. Headline: one sentence stating the message of the current scenario.
2. Key indicators: 3 to 5 numbers at most (end-of-period value and change vs. baseline).
3. Main chart: the one chart that carries the message.
4. Controls: parameters grouped by theme, with sensible defaults and a reset button.
5. Details: secondary charts, assumptions, data sources and model notes, collapsed by default.

Do not show every output at once. Anything not needed for the message goes in Details.

## 3. Choosing the chart (by data shape)

| Data shape | Default chart | Notes |
|---|---|---|
| Variable over time, one scenario | Line | Show uncertainty as a band or fan, never as many overlapping lines |
| Variable over time, several scenarios | Line, one color per scenario | Max 5 scenarios; highlight one, grey the rest |
| Scenario comparison at one date | Horizontal bar or dumbbell | Sort by value |
| Two variables against each other | Scatter or connected scatter | Label start and end points |
| Difference vs. baseline | Diverging bar or line around zero | Zero line always visible |
| Composition over time | Stacked area, only with 2–5 parts | Otherwise use small multiples |
| Many variables, same scale | Small multiples | Same axes across panels |

Avoid: pie and donut charts, 3D effects, dual y-axes, truncated bar axes, spaghetti charts with more than 5 lines. Check each new chart against the From Data to Viz caveats gallery before shipping.

## 4. Color

- Use ColorBrewer palettes, filtered to colorblind-safe.
- Scenarios: one qualitative palette, 3–5 colors. A scenario keeps the same color on every chart and every page.
- Intensity (heatmaps, maps): sequential palette.
- Difference from baseline: diverging palette, centered on zero.
- Never rely on color alone: add direct labels, line styles or markers.
- Grey is for context and non-highlighted series. Accent color is reserved for the message.

### 4.1 Palette as built in Explorer v0.2 (D-056, Provisional until the editor approves)

Source of truth: the two theme blocks at the top of `site_src/style.css`; `tests/test_site_tokens.py` reads them, checks the hex codes below and verifies WCAG AA programmatically (text 4.5:1 on page, card and raised surfaces; lines and bars 3:1 on the card).

Scenario colours (ColorBrewer Paired blue and Dark2 orange, plus a neutral grey). Same line colours in both themes; text variants differ where needed for contrast.

| Role | Line / fill | Text on light | Text on dark |
|---|---|---|---|
| Baseline (standard run, damage off), dashed | #6B7280 | #5B6270 | #9AA3B2 |
| Scenario A, or the single chosen scenario in the Explorer | #1F78B4 | #1A6CA1 | #6DB3E6 |
| Scenario B | #D95F02 | #B34E00 | #F08A3C |

Accents (not scenarios; used for other variables, never for A or B): light theme teal #0F766E, violet #5B4FB8, magenta #B0206A, heat red #B2182B; dark theme teal #35C2A1, violet #A9A3F0, magenta #F07FB6, heat red #FF7F73.

Surfaces: light (reading) theme page #FAFAF7, card #FFFFFF, text #1C1C1A; dark (dashboard) theme page #0E1420, card #151D2C, text #E6EAF2. Status badges: amber and red, each with a text label and an icon; no panel is green.

Themes: the dashboard pages (Explorer, Compare, Connections) open in the dark theme; story and text pages open in the light "reading" theme and follow `prefers-color-scheme` (dark if the system asks for it). Every page has a toggle; the choice is kept in the browser only.

Type: Work Sans (SIL OFL 1.1) is embedded in the stylesheet as a base64 woff2, so the static site makes no font request and works offline; headings on reading pages use a serif system stack (Iowan Old Style, Palatino, Georgia). Minimum text size 13 px (tested on the stylesheet and on chart text).

## 5. Titles and annotations

- Chart titles state the finding, not the topic ("Under rapid AI growth, X peaks in 2060", not "X over time").
- Label lines directly at their end point instead of using a legend where possible.
- Annotate key moments (peaks, crossings, tipping points) with a short note.
- Axis labels carry units. Time axes show the model's start and end years.
- Every chart says whether it shows a simulation output and links to the assumptions behind it.

## 6. Honesty rules for a simulation tool

- Label outputs as simulated projections, not forecasts.
- Show uncertainty or ranges where the model produces them.
- State the baseline clearly and show it on comparison charts.
- Keep a visible link to model documentation, parameters and data sources.

## 7. Preset scenarios

- Provide 3 to 5 named presets, each with a one-sentence story and a pre-written chart title.
- A preset loads instantly and can be modified, with a "back to preset" option.

## 8. Accessibility and performance

- Minimum contrast per WCAG AA; test palettes in a colorblind simulator.
- Charts have text alternatives and a data table view.
- Controls are usable on mobile.
- Do not block the first view on a model run: load a precomputed preset first.

## 9. Review checklist (before each release)

- [ ] Message visible in 10 seconds, no interaction needed
- [ ] Max 5 key indicators, max 5 scenario lines per chart
- [ ] Chart type matches the data shape (section 3)
- [ ] Palette colorblind-safe, colors consistent per scenario
- [ ] Titles state the finding; direct labels used
- [ ] Baseline and uncertainty shown where relevant
- [ ] Assumptions and sources one click away
- [ ] Checked on a phone

## 10. References

- From Data to Viz: https://www.data-to-viz.com
- Dashboard Design Patterns: https://dashboarddesignpatterns.github.io
- ColorBrewer: https://colorbrewer2.org
- Storytelling with Data: https://www.storytellingwithdata.com
- Dataviz Inspiration: https://www.dataviz-inspiration.com

## 11. Guidelines not met in Explorer v0.2 (D-056, reported honestly)

- 3 "Scenario comparison at one date: horizontal bar, sorted by value": the Compare bars are in a fixed order of measures (the measures have different units, so there is no meaningful value order).
- 4 "test palettes in a colorblind simulator" and 8 (same): not done. The scenario colours come from ColorBrewer sets and every series also differs by dash pattern, direct label and line weight, but no simulator was run.
- 5 "Annotate key moments": the main chart marks the peak and the AI automation chart marks the half-way year; the secondary World3 charts carry no annotation.
- 5 "Every chart says whether it shows a simulation output and links to the assumptions behind it": each chart's text alternative, PNG and CSV say it is a model run and carry the caveat; the chart card itself has no assumptions link (the page banner and the reliability section do).
- 7 "pre-written chart title" and "back to preset": titles are generated from the data (as the editor's brief asked) and Reset returns to the standard run, not to the last chosen preset.
- 8 "Checked on a phone": checked in an emulated 390 px viewport only; no physical phone, no screen reader.
- The warming stripes are an infographic with a text alternative, without a data table, PNG or CSV.

Update, v0.2b (2026-10-22): the last point above is now met: every chart card carries an assumptions link (World3, the climate-damage coupling, FaIR, the AI race, the damage options, the history comparison, the warming map), and the warming stripes are a chart card with a data table, PNG and CSV. Not changed: the fixed order of the Compare bars, the missing colour-blindness simulator run, and the annotation of secondary charts. The warming map follows the sequential-palette rule (ColorBrewer OrRd, one scale for every year); the Model-versus-reality charts use the scenario-A blue for the model, the FaIR heat colour for FaIR and the text colour for observations (points).

