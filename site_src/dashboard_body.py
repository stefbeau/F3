"""Markup of the Explorer dashboard (explorer.html), D-056 stage 3. Left rail (choose), one main chart (result), details and tests (reliability).
Nothing here holds a model number; dashboard.js writes headlines, tiles and charts from the data. Caveat text is the verbatim v0.1 text (dash_blocks.py)."""
import dash_blocks as B
import ig
import index_body

PUBLIC = index_body.PUBLIC
S3, R3, FAIR, GATE, W3 = B.S3, B.R3, B.FAIR, B.GATE, B.W3

# (id, what it checked, result word, status class, anchor on the Limitations page). Wording follows docs/tracks and the Limitations page; nothing stronger.
TESTS = [
    ("A3.1", "World3 ported sectors against WorldDynamics.jl, standard run (14 states)", "Met: all within 0.124%", "met", "status-world3"),
    ("A3.2", "All 29 World3 states against WorldDynamics.jl, standard run, after D-031", "Met: worst 1.906% (limit 2%)", "met", "status-world3"),
    ("A3.4(b)", "Population sector inside the full run equals the same sector alone with recorded inputs, within 0.25%", "Failed: up to 0.931% (2004 set)", "failed", "status-world3"),
    ("M6", "Damage coupling: off equals stand-alone World3 to 1e-9; zero warming equals baseline; more warming lowers output; no NaN or negative values", "Met (these runs are not compared with WorldDynamics.jl)", "met", "status-world3"),
    ("A2.1", "FaIR ensemble-mean warming 2015-2024 against HadCRUT5", "Failed: 0.037 K below the interval", "failed", "status-climate"),
    ("A1.3", "S3 against GATE's three runs within 2% at every year", "Failed: levels unvalidated after about 2027", "failed", "status-ai"),
    ("A1.4", "Investment rule R3 against GATE's investment path (report only)", "Poor agreement", "failed", "status-ai"),
    ("A2.6", "Halving the loop step changes the slice's outputs by at most 0.1%", "Failed: 0.565% (data-centre electricity)", "failed", "status-ai"),
    ("B1 sign", "Lowering electricity supply lowers compute growth", "Failed as written", "failed", "status-ai"),
    ("R1 sign", "Raising AI investment raises compute and automation", "Failed on automation (saturation at 1.0)", "failed", "status-ai"),
    ("B2 sign", "More damage, lower output", "Met", "met", "status-ai"),
]



HISTORY_PANEL = """<section class="panel" id="p_history" role="tabpanel" aria-labelledby="tab_history" tabindex="-1">
<h1 class="headline">Model versus reality: how far is each model from observed history?</h1>
<p class="badges"><a href="limitations.html#status-history" class="badge amber"><span aria-hidden="true">&#9650;</span> Amber: a comparison with history, not a validation; tests A2.1 and A3.4(b) failed</a></p>
<div class="notice" role="note"><strong>This is not a validation.</strong> World3 (here the 2004 parameter set, a model of the 1970s) and FaIR were not fitted to these series, and nothing was tuned to improve the match. The charts show the distance. The World3 curves follow the settings chosen in the rail, with climate damage off, because damage starts in 2025.</div>
<h2>Population</h2>
<div id="ch_hpop"></div>
<p class="gap" id="gap_pop" aria-live="polite"></p>
<p class="note">Observed: United Nations, World Population Prospects 2024, medium variant, 1 July (CC BY 3.0 IGO). The UN gives estimates to 2023; the hollow dots for 2024 and 2025 are the UN's own projection and are not used in the gap. World3 values are calendar-year means. <strong>Test A3.4(b) FAILED:</strong> World3's population sector inside the full model differs from the same sector run alone by up to 0.93% (0.25% required); runs with changed parameters have not been compared with WorldDynamics.jl.</p>
<h2>Temperature</h2>
<div id="ch_htemp"></div>
<p class="gap" id="gap_temp" aria-live="polite"></p>
<p class="note"><strong>Test A2.1 FAILED</strong> (the FaIR mean for 2015-2024 is 0.037 K below HadCRUT5's interval). The ensemble was constrained to temperatures up to 2022, so 1850-2022 is in sample and 2023-2025 is out of sample; this chart is not an independent test of FaIR. Emissions are prescribed (non-CO2 is not modelled). Observed: HadCRUT.5.2.0.0 (Met Office, Open Government Licence v3.0), re-based to 1850-1900, the same baseline as every temperature on this page and as the warming stripes. NASA GISTEMP was used as a cross-check only (<span id="gis_x"></span>); none of its values is shown.</p>
<details class="secondary" id="hist_sec"><summary>Secondary comparison: World3 industrial output against world GDP. Not the same quantity, so read the gap as a distance, not an error.</summary>
<div id="ch_hio"></div>
<p class="note">Both curves are indexed to 1990 = 1 and nothing else is done to them: no fitting, no rescaling. World3 industrial output is in model dollars per year (World3's own constant dollars, industry only); observed GDP is the World Bank's world total in constant 2015 US dollars, all sectors. They are not the same quantity. Observed: World Bank, World Development Indicators NY.GDP.MKTP.KD (CC BY 4.0).</p>
</details>
<p class="gap secgap" id="gap_io" aria-live="polite"></p>
<details><summary>How the comparison is made</summary>
<ul>
<li>The readings (which year is compared, the 5% and 25% bands, the A2.1 form of the temperature test) were written before the numbers were seen: <code>docs/history-comparison.md</code>. The bands are plain-language aids set by the project, not acceptance criteria of the plan.</li>
<li>Every sentence under a chart is computed by the page from the data of that chart. World3 sits at 1 January, so a calendar-year value is the mean of the model values at the start and end of the year; the UN figure is for 1 July.</li>
<li>Sources, versions, licences and checksums: <a href="sources.html">Sources</a>. Caveats: <a href="limitations.html#status-history">Limitations</a>.</li>
</ul></details>
</section>"""

MAP_PANEL = """<section class="panel" id="p_map" role="tabpanel" aria-labelledby="tab_map" tabindex="-1">
<h1 class="headline">Warming map: where the global FaIR warming would be larger or smaller, illustratively</h1>
<p class="badges"><a href="limitations.html#status-map" class="badge amber"><span aria-hidden="true">&#9650;</span> Amber: illustrative scaling of the global result, not a regional projection</a></p>
<div class="notice" role="note"><strong>Illustrative downscaling of the global FaIR result. Not a regional climate projection. Pattern-scaling ignores regional feedbacks, aerosols, ocean dynamics.</strong> <a href="methods.html#warming-map">How the map is made (Methods)</a>.</div>
<div class="mapctl"><label for="map_year">Year: <strong id="map_year_out">2100</strong></label><input type="range" id="map_year" min="2025" max="2100" step="1" value="2100" aria-describedby="map_note"></div>
<div class="mapbox">
<div id="ch_map"></div>
<div class="tiles mapglobal" aria-label="Global warming in the chosen year">
<div class="tile"><span class="tk_k">Global mean (FaIR)</span><strong class="tk_v" id="map_g_mean"></strong></div>
<div class="tile"><span class="tk_k">Global 5th percentile</span><strong class="tk_v" id="map_g_lo"></strong></div>
<div class="tile"><span class="tk_k">Global 95th percentile</span><strong class="tk_v" id="map_g_hi"></strong></div>
</div>
</div>
<p class="note" id="map_note">Regional warming = global warming (the FaIR run of the Climate chart under Details, above 1850-1900) x a fixed coefficient for each of the 58 IPCC AR6 reference regions. The uncertainty beside the map is the global one. <strong>Pattern uncertainty is not shown</strong> (the spread of the coefficients across 32 CMIP6 models is stored in the data file and not drawn). The map follows the climate run only: climate damage does not change warming, so it is the same for every scenario and every setting in the rail. No country-level, damage or population map is shown.</p>
<details><summary>Method and sources in brief</summary>
<ul>
<li>Coefficient = how many kelvin a region warms per kelvin of global warming, the multi-model mean of 32 CMIP6 models (regression of regional on global annual means, historical plus SSP1-2.6, SSP2-4.5 and SSP5-8.5). Source: the IPCC AR6 WGI Atlas regional aggregates (CC BY 4.0). The coefficients are derived by F3; the Atlas does not publish them.</li>
<li>Land regions use land values, ocean regions sea values. The area-weighted mean coefficient is checked to be 1 within 2%; the recorded value is on the Methods page.</li>
<li>Coastlines: Natural Earth (public domain). Colour scale: ColorBrewer OrRd, sequential and colour-blind safe, the same scale in every year.</li>
<li>The climate run starts about 0.04 to 0.07 K below observed (test A2.1 failed) and emissions are prescribed; the map inherits both.</li>
</ul></details>
</section>"""

TABS = """<div class="dtabs" id="dtabs" role="tablist" aria-label="Explorer views">
<button type="button" role="tab" id="tab_scenario" data-tab="scenario" aria-controls="result" aria-selected="true">Scenario</button>
<button type="button" role="tab" id="tab_history" data-tab="history" aria-controls="p_history" aria-selected="false" tabindex="-1">Model versus reality</button>
<button type="button" role="tab" id="tab_map" data-tab="map" aria-controls="p_map" aria-selected="false" tabindex="-1">Warming map</button>
</div>"""


def tests_table() -> str:
    rows = "".join(f'<tr class="t{c}"><th scope="row">{n}</th><td>{w}</td><td><a href="limitations.html#{a}"><span class="res {c}">{r}</span></a></td></tr>'
                   for n, w, r, c, a in TESTS)
    return ('<table class="tests" id="tb_tests"><caption class="sr">Recorded tests and their results</caption>'
            '<tr><th scope="col">Test</th><th scope="col">What it checked</th><th scope="col">Result</th></tr>' + rows + '</table>')


BADGES = (
    '<p class="badges"><a class="badge amber" href="limitations.html#status-world3"><span aria-hidden="true">&#9650;</span> World3: standard run matches its reference; A3.4(b) failed; changed runs not compared</a> '
    '<a class="badge amber" href="limitations.html#status-climate"><span aria-hidden="true">&#9650;</span> Climate: A2.1 failed by 0.037 K</a> '
    '<a class="badge red" href="limitations.html#status-ai"><span aria-hidden="true">&#9632;</span> AI race: A1.3 failed, levels unvalidated</a></p>'
)


def body() -> str:
    return f"""
<div class="banner compact" role="note"><strong class="big">{PUBLIC}</strong>Every curve is the output of a model run under stated assumptions. None is a prediction, none has a likelihood. See <a href="limitations.html">Limitations</a>.</div>
<div class="dash" id="dash" data-step="result" data-tab="scenario">
<aside class="rail" id="choose" aria-labelledby="choose_h">
<h2 id="choose_h">Choose a story</h2>
<div class="presetlist" id="presets" role="group" aria-label="Scenario presets"></div>
<div class="ctlrow col"><span class="ctllab" id="dmg_lab">Climate damage to industrial output <span class="note">(default off)</span></span><div class="seg" id="dmg_seg" role="group" aria-labelledby="dmg_lab"></div></div>
<div class="notice damage" id="w3_damage_notice" role="note" aria-live="polite"></div>
<details id="custom"><summary>Custom parameters</summary><div class="ctl col" id="w3ctl"></div></details>
<button type="button" class="reset" id="reset">Reset to standard</button>
</aside>
<div class="stage">
{TABS}
<section id="result" aria-labelledby="headline">
<h1 class="headline" id="headline">The standard world turns down</h1>
<div class="chips" id="w3_chips" aria-label="Changes against the standard run"></div>
<div class="kpis" id="kpis" aria-label="Key numbers"></div>
<div id="ch_main"></div>
<p class="note" id="w3_text"></p>
</section>
<section id="reliability" aria-labelledby="rel_h">
<h2 id="rel_h">How reliable is this?</h2>
{BADGES}
<details id="details"><summary>Details: more charts, the climate and AI-race runs, tests and caveats</summary>
<h3>More World3 charts</h3>
<div id="ch_io"></div><div id="ch_nr"></div><div id="ch_pol"></div>
{B.W3_STATUS}
{B.W3_DETAILS}
<h3>Climate ({FAIR})</h3>
{B.CLIMATE_STATUS}
<div id="ch_temp"></div>
<h4>Warming stripes</h4>
<div id="ch_stripes">{ig.STRIPES}</div>
{ig.STRIPES_CAP}
{B.CLIMATE_DETAILS}
<h3>AI race: automation and damage</h3>
{B.AI_STATUS}
{B.AI_WITHHELD}
<div class="ctl">
<label>AI investment setting ({R3} rule) <select id="sel_s"><option value="low">low</option><option value="central" selected>central</option><option value="race">race</option></select></label>
<label>Damage option <select id="sel_d"><option value="low">low (Nordhaus 2017)</option><option value="central" selected>central (Barrage and Nordhaus 2024)</option><option value="high">high (Howard and Sterner 2017; not the upper end)</option></select></label>
</div>
<div class="note">The automation chart changes with the AI setting; the damage chart changes with the damage option. The climate chart has no controls: emissions are prescribed.</div>
<div class="note" id="setting_text"></div>
<div id="ch_auto"></div>
<div class="note" id="auto_note"></div>
{B.AI_DAMAGE_NOTICE}
<div id="ch_dmg"></div>
<div class="note">Damage fraction = c x T^2 (c per option below). Output losses are shown as shares of S3's own output, whose level is unvalidated.</div>
<table id="tb_dmg"></table>
<h4>The loop signs</h4>
<div class="note">Signs tested in tests/test_m2_slice.py (written before the results). Magnitudes are not claims.</div>
<div id="signs"></div>
{B.AI_DETAILS}
<h3>Tests and their results</h3>
<p class="note">Recorded results, not relaxed. Each row links to the full statement on the Limitations page.</p>
{tests_table()}
</details>
<section class="connected" id="connected"><h3>What is connected</h3>
<p>Only two links are built and tested: warming lowers World3 industrial output (off by default) and warming lowers S3's own output. One more is built with its outputs withheld; four are not built. Solid, dotted and dashed lines say which. <a href="connections.html">Open the connections map</a> to inspect each of the seven links.</p>
</section>
{B.NOT_SHOWN}
{B.SOURCES}
</section>
{HISTORY_PANEL}
{MAP_PANEL}
</div>
<nav class="actionbar" id="actionbar" aria-label="Steps"><button type="button" data-step="choose">Choose story</button><button type="button" data-step="result" aria-current="step">Result</button><button type="button" data-step="reliability">Reliability</button></nav>
</div>
"""
