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
<div class="dash" id="dash" data-step="result">
<aside class="rail" id="choose" aria-labelledby="choose_h">
<h2 id="choose_h">Choose a story</h2>
<div class="presetlist" id="presets" role="group" aria-label="Scenario presets"></div>
<div class="ctlrow col"><span class="ctllab" id="dmg_lab">Climate damage to industrial output <span class="note">(default off)</span></span><div class="seg" id="dmg_seg" role="group" aria-labelledby="dmg_lab"></div></div>
<div class="notice damage" id="w3_damage_notice" role="note" aria-live="polite"></div>
<details id="custom"><summary>Custom parameters</summary><div class="ctl col" id="w3ctl"></div></details>
<button type="button" class="reset" id="reset">Reset to standard</button>
</aside>
<div class="stage">
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
{ig.STRIPES}
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
<p class="note">Solid arrows are links that are built and tested today. Dashed arrows are links that are not built. Nothing in the Explorer depends on a dashed arrow.</p>
{ig.LOOPS}
{ig.LOOPS_KEY}
<h4>Roadmap</h4>
{ig.ROADMAP}
{ig.ROADMAP_KEY}
</section>
{B.NOT_SHOWN}
{B.SOURCES}
</section>
</div>
<nav class="actionbar" id="actionbar" aria-label="Steps"><button type="button" data-step="choose">Choose story</button><button type="button" data-step="result" aria-current="step">Result</button><button type="button" data-step="reliability">Reliability</button></nav>
</div>
"""
