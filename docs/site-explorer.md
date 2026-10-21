# F3 Explorer v0 (branch `site`): what it is, and the choices made

**Status:** built 2026-10-21 on branch `site`; **not merged into main, not published, Pages not enabled, the workflow has not been run.** The editor reviews it in the browser: open `site/index.html` (the five pages link to each other and are self-contained; they open from disk).

## What it is
A static site (D-009: precomputed scenario grids, no backend). Five pages in `site/`: **index.html** (the Explorer), **methods.html**, **limitations.html**, **sources.html**, **about.html**, linked by a header and a footer navigation on every page, with the same CSS tokens, light and dark mode, English only. The Explorer has a title, one plain-English line, the scenario controls first, then three panels that are **not coupled to each other** (a banner says so): (1) World3 scenarios, (2) Climate (FaIR, 841 members), (3) AI race (automation and damage). Each panel has a one-line status visible without clicking; all caveat text is in a collapsed `<details>` under it. The "conditional scenarios, not forecasts" banner is on every page.

## Build
- Generator and templates are in `site_src/` (not in `site/`, so that what would be deployed is only pages and data): `generate.py`, `pages.py` (the five pages), `explorer.js` (charts and controls), `style.css`.
- Full build (about 2 minutes; needs the 841-member climate recording, `dashboard/demo0/record_climate.py`): `PYTHONPATH=. python site_src/generate.py <climate841.npz>`. Restamp only (date and commit hash): `... generate.py --reuse`.
- `site/data/explorer.json` holds everything the pages draw **and** the series that are withheld (S3 compute, data-centre electricity); `.github/workflows/pages.yml` deploys `site/` and is manual-only.

## What changed from Demo 0, and why (editor decision 2026-10-21, "fix all")
- **A. AI panel cut.** The S3 compute charts, the B1 compute chart and the data-centre electricity chart and table are **not rendered**: their values reach about 1.4e40 FLOP/year and 7.4e9 TWh/year. One visible note says they are withheld until the S3 compute path is validated (awaiting Epoch AI). Kept: the automation chart, the damage chart and table (shares of S3's unvalidated output; the "2100 output, USD/yr" column is dropped), and the loop-sign text without the large magnitudes. The series remain in `explorer.json` and the generator.
- **B. Charts.** Readable ticks ("2 billion", "0.5", "3.24 K"), unit label on its own line above the plot, text drawn at its real size (the SVG viewBox is the pixel size, measured minimum rendered font 13 px at 390 px width).
- **C. World3 and controls.** The grey dashed "standard" reference and its note appear only when a lever differs from standard. The AI controls say which chart each control changes. Each panel has its status line.
- **D. Pages.** Methods, Limitations, Sources, About (this page's statements are taken from the repository records).
- **E. Accessibility.** Colour-blind-safe palette (Okabe-Ito based), dash patterns on series with direct end labels, a `<title>`, `<desc>` and `aria-label` text summary on every chart, visible keyboard focus, selectors usable by keyboard.

## Checked (Edge, through its debugging protocol)
All five pages at 390 px and 1200 px, light and dark (20 measurements): horizontal scroll none (page scroll width equals client width; 1185 at 1200 px is the scrollbar), no element wider than the viewport, no script or console errors, every chart has a title and an aria-label, minimum rendered chart font 13 px. Interaction: a World3 lever changes the curves and shows the note and the dashed reference; the AI setting redraws the automation chart. Screenshots of the top of the page, the controls and each panel (light and dark, 390 px), the four other pages (light and dark, 390 px) and the AI panel at 1200 px were looked at. **Not checked:** a physical phone, browsers other than Edge, a screen reader (the summaries are in the markup but were not read aloud), colour-blindness simulation (the palette is a published colour-blind-safe set and every series also differs by dash pattern and end label).

## Caveat-text comparison with Demo 0
Sentence by sentence, the Demo 0 template's caveat text was compared with the five new pages (script `caveat_diff`, 31 specific caveat statements checked verbatim): **nothing was lost.** Intentional changes, all under A: (1) the withheld charts' own descriptions were kept but moved into the AI-race caveats in the past tense ("The IEA points were ..." instead of "Dots: ..."); (2) the table row "Model 2025 / Model 2030, demand / used" and the "2100 output, USD/yr" column are not rendered; (3) the heading "Demo 0" became "F3 Explorer v0" and the sentence "Every curve below ..." appears as "Every curve in the Explorer ..." on the subpages; (4) one wording was made more exact: the Epoch AI playground runs are no longer described as "(CC BY 4.0)" on the Explorer page, because Epoch's statement covers its work in general and no licence is stated for the playground's script bundle (Sources page).

## Provisional (delegated) decisions
- **D-046** (World3 levers and runs: 3 levers x 3 values, 27 runs, 2004 parameter set, D-031 group): see `DECISIONS.md` on this branch; only standard parameters are compared with WorldDynamics.jl.
- **D-047** (Explorer pages, withheld outputs and chart conventions, recorded on this branch): see `DECISIONS.md`.

## Known issues (not fixed)
- Dark-mode and light-mode charts are drawn when the page loads; if the colour scheme changes while the page is open the charts redraw, but a manual `data-theme` toggle does not exist (the CSS supports it, the page has no button).
- The Limitations table of failed tests is stacked blocks, not a table, on purpose (a table was unreadable at 390 px).
- The generated Explorer page and data are about 0.5 MB each and are committed on this branch.
- "Last updated" and the commit hash on the pages are those of the source commit at build time, so they name the commit before the one that contains the built pages; the About page says so.
