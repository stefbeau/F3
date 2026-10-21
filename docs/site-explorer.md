# F3 Explorer v0 (branch `site`): what it is, and the choices made

**Status:** built 2026-10-21 on branch `site`; **not merged into main, not published, Pages not enabled, the workflow has not been run.** The editor reviews it in the browser (`site/index.html`, one self-contained file, opens from disk).

**What it is.** A static page (D-009: precomputed scenario grids, no backend) with a title, one plain-English line, the scenario controls first, then three panels that are **not coupled to each other** (a banner says so): (1) World3 scenarios, (2) Climate (FaIR, 841 members), (3) AI race (S3 under R3, data-centre electricity, damage options, loop signs). Each panel has a one-line persistent notice visible without clicking; every caveat that was on Demo 0 is kept, moved into a collapsed `<details>` under the panel (nothing removed), and the "conditional scenarios, not forecasts" banner is kept.

**Layout fix, as measured.** The provenance string, which made the old page about 5,500 px wide, is now in a collapsed `<details>` with wrapping. Measured in Edge through its debugging protocol, reading the page's own scroll width: at 390 px the content width is 390 px and at 1200 px it is 1185 px (the scrollbar), in light and dark, with no element wider than the viewport, no script or console errors, and the World3 lever changing the curves. Screenshots of the top of the page and of each panel at 390 px were looked at in light and dark.

**Generator and data.** `site/generate.py` (needs the 841-member climate recording; see `dashboard/demo0/record_climate.py`), `site/template.html`, `site/data/explorer.json`, `site/index.html`. The AI-race and climate panels reuse the Demo 0 grid code unchanged.

## Provisional (delegated) decision: the World3 levers and runs (recorded as D-046 on this branch)

- **Status:** Provisional (delegated). **Date:** 2026-10-21.
- **Decision:** the World3 panel is a precomputed grid of **3 levers x 3 values = 27 runs**, 1900-2100, **2004 parameter set** (the provisional default of D-015), run with the **D-031 group** (0.0625-year sub-steps inside the 0.25-year loop). Levers, all existing World3 parameters in the ported sectors: **initial non-renewable resources** `nri` (0.5e12, **1e12 standard**, 2e12), **land yield factor after the 1975 policy year** `lyf2` (**1.0 standard**, 1.5, 2.0), **persistent-pollution generation factor after 1975** `ppgf21` (**1.0 standard**, 0.5, 0.25). Shown: population, remaining resources as a fraction of the chosen starting stock, and the persistent-pollution index (ppol / 1.36e8, 1 = the 1970 level).
- **Why these three:** they are the classic scenario levers of the Limits to Growth runs (resources, agricultural technology, pollution control), each acts on a different sector, and each had a measurable effect in a trial run before the choice was frozen (2100 population from 0.37 to 6.8 billion across the probed values). `ppgf22` was probed and has no effect in this model because the technology switch is off (`swat = 0`), so `ppgf21` is used.
- **What was and was not checked:** only the **standard** parameters have been compared with WorldDynamics.jl (A3.1 met, A3.2 met after D-031, A3.4(b) failed). **Runs with changed parameters have not been compared with anything**; the page says so. The 2100 outcomes of the extreme values (for example population of 0.37 billion with `lyf2 = 2`) are properties of the ported equations under those inputs, and the page makes no claim that they are right.
- **Alternatives considered:** other levers (`icor`, `alic`, policy-year timing, `dcfsn`); the 1974 set; more values per lever. **Cost of reversing:** low (edit `LEVERS` in `site/generate.py`, regenerate; about 70 s plus the 841-member climate recording).

## Known issues in this draft (not fixed)
- In the charts the y-axis unit label overlaps the top tick label, and axis text is small at 390 px (the SVG scales down).
- The compute chart shows all three AI settings by design, so it does not change with the AI-setting selector (only the electricity chart does); the controls text does not say this.
- The AI-race panel's recorded test results (three failed slice tests) are inside the collapsed caveats, not in the one-line notice.
- The generated page and data are about 0.5 MB each and are committed on this branch.
- I did not run the Explorer on a physical phone or in browsers other than Edge.
