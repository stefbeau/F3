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

Action item: record the final palette hex codes in this file once chosen.

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
