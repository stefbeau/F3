"""Renders the five static pages of the F3 Explorer v0 (English only). Shared CSS tokens, nav and footer on every page.

Every statement about a test or a decision is taken from the repository records (DECISIONS.md, audit/*.md, docs/tracks/*.md, STATUS);
nothing here is stronger than what those records show.
"""
from __future__ import annotations

import json
from pathlib import Path

NAV = [("index.html", "Explorer"), ("methods.html", "Methods"), ("limitations.html", "Limitations"), ("sources.html", "Sources"), ("about.html", "About")]
REPO_URL = "https://github.com/stefbeau/F3"

SCROLL_FIX = ""


def head(title: str, css: str) -> str:
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{title}</title>\n<style>\n{css}\n</style>\n</head>\n<body>\n')


def nav(current: str, cls: str = "site") -> str:
    parts = []
    for h, label in NAV:
        cur = ' aria-current="page"' if h == current else ""
        parts.append('<a href="' + h + '"' + cur + ">" + label + "</a>")
    return '<nav class="' + cls + '" aria-label="Site"><span class="brand">F3 Explorer v0</span>' + "".join(parts) + "</nav>\n"


def footer(current: str, stamp: dict) -> str:
    links = "".join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    return (f'<footer class="site"><nav aria-label="Footer">{links}<a href="{REPO_URL}">Source code on GitHub</a></nav>'
            f'<div>Conditional scenarios, not forecasts. Local draft, not published. Built {stamp["date"]} from source commit <code>{stamp["commit"]}</code>.</div></footer>\n')


def page(title: str, current: str, body: str, css: str, stamp: dict, script: str = "") -> str:
    return (head(title, css) + nav(current) + "<main>\n" + body + "\n</main>\n" + footer(current, stamp) + script + "</body>\n</html>\n")


BANNER = ('<div class="banner" role="note"><strong class="big">Conditional scenarios, not forecasts.</strong>'
          'Every curve in the Explorer is the output of a model run under stated assumptions. None is a prediction, none has a likelihood, '
          'and this page is a local draft that has not been approved for publication (plan test A2.7).</div>')


# --------------------------------------------------------------------------------------------------------------------
INDEX_BODY = """
<h1>F3 Explorer v0</h1>
<p class="lead">Three separate model pieces you can explore: a World3 scenario grid, a climate run, and an AI-race run. They are not connected to each other yet.</p>
""" + BANNER + """
<div class="banner" role="note"><strong>The three panels are NOT yet coupled.</strong> Changing a control in one panel does not change any other panel: World3 does not know about the AI race, the climate path does not respond to either, and the AI-race run does not feed back into World3. Coupling them is later work (milestone M6). See <a href="methods.html">Methods</a> and <a href="limitations.html">Limitations</a>.</div>

<section class="card" id="controls">
<h2>Choose scenarios</h2>
<div class="grp">World3 panel (World3 parameters; Provisional choice of levers)</div>
<div class="ctl" id="w3ctl"></div>
<div class="note" id="w3_text"></div>
<div class="grp">AI-race panel (investment setting and damage option)</div>
<div class="ctl">
<label>AI investment setting <select id="sel_s"><option value="low">low</option><option value="central" selected>central</option><option value="race">race</option></select></label>
<label>Damage option <select id="sel_d"><option value="low">low (Nordhaus 2017)</option><option value="central" selected>central (Barrage and Nordhaus 2024)</option><option value="high">high (Howard and Sterner 2017; not the upper end)</option></select></label>
</div>
<div class="note">The automation chart changes with the AI setting; the damage chart changes with the damage option.</div>
<div class="note" id="setting_text"></div>
<div class="note">The climate panel has no controls: emissions are prescribed, so the temperature path is the same for every choice above.</div>
</section>

<!-- ========================= PANEL 1: WORLD3 ========================= -->
<section class="card" id="p_w3">
<h2>1. World3 scenarios</h2>
<div class="notice" role="note"><strong>Status:</strong> the standard run matches WorldDynamics.jl (tests A3.1 and A3.2 met); test A3.4(b) failed; runs with changed parameters are not compared with anything. Population, capital, land, resources and pollution, 1900-2100; precomputed grid, 3 levers x 3 values. <strong>No health or yield effect of warming</strong> is modelled.</div>
<figure><div id="ch_w3pop"></div><div class="leg" id="lg_w3pop"></div></figure>
<figure><div id="ch_w3nr"></div><div class="leg" id="lg_w3nr"></div></figure>
<figure><div id="ch_w3pol"></div><div class="leg" id="lg_w3pol"></div></figure>
<details><summary>What this panel is, and its test status</summary>
<ul id="w3status"></ul>
<ul>
<li>The levers are World3 parameters chosen as a <strong>Provisional (delegated)</strong> decision, not an approved one (D-046, docs/site-explorer.md). They are not forecasts of anything; they show how the 1900-2100 World3 run changes when one parameter changes.</li>
<li>World3 is run as the D-031 group: its five sectors take 0.0625-year sub-steps inside the model's 0.25-year loop.</li>
<li>The 2004 parameter set is the provisional default (D-015); the 1974 set exists in the code and is not shown.</li>
<li>Resources are shown as the fraction of the starting stock that remains (the starting stock is the chosen lever value); pollution as the persistent-pollution index (1 = the 1970 level).</li>
<li>World3 is a single run per setting: there is no band and no uncertainty analysis.</li>
<li><strong>No health or yield effect of warming.</strong> World3's population and food sectors have no warming term, and the four warming effects of Earth4All that would act on them (life expectancy, land yield, CO2 fertilisation and the CO2 lifetime) are deliberately omitted (D-049). The panel therefore shows no feedback from warming to population or food.</li>
</ul></details>
</section>

<!-- ========================= PANEL 2: CLIMATE ========================= -->
<section class="card" id="p_climate">
<h2>2. Climate (FaIR)</h2>
<div class="notice" role="note"><strong>Status:</strong> test A2.1 failed. FaIR climate starts about 0.04 to 0.07 K below observed for the current decade, and non-CO2 emissions are prescribed, not modelled (D-030, D-021). The FaIR test against HadCRUT5 for 2015-2024 failed.</div>
<figure><div id="ch_temp"></div><div class="leg" id="lg_temp"></div></figure>
<details><summary>Caveats and details for the climate panel</summary>
<div class="note">FaIR warming above 1850-1900, ensemble of 841 members: mean (line) and 5th-95th percentile (band). Prescribed emissions do not respond to any lever here, so the temperature path is the same for every setting and damage option: the damage options change output, not temperature, in this slice. The band is the FaIR ensemble band only (not an uncertainty analysis of the whole model). FaIR starts about 0.04 to 0.07 K below observed for the current decade.</div>
<ul>
<li><strong>Climate (FaIR).</strong> FaIR climate starts about 0.04 to 0.07 K below observed for the current decade (D-030); non-CO2 emissions are prescribed, not modelled (D-021). The test of FaIR against HadCRUT5 for 2015-2024 failed (ensemble mean 0.037 K below the interval). <span id="s6status"></span></li>
</ul></details>
</section>

<!-- ========================= PANEL 3: AI RACE ========================= -->
<section class="card" id="p_ai">
<h2>3. AI race: automation and damage</h2>
<div class="notice" role="note"><strong>Status:</strong> the AI sector (S3) failed its test against GATE (A1.3): its absolute output is unvalidated after about 2027, and it does not reproduce GATE. Shapes are more reliable than levels. Not a forecast.</div>
<div class="withheld" role="note">Compute and electricity outputs are withheld until the S3 compute path is validated (awaiting Epoch AI); they currently leave any plausible range.</div>
<h3>Automation (S3)</h3>
<figure><div id="ch_auto"></div><div class="leg" id="lg_auto"></div></figure>
<div class="note" id="auto_note"></div>
<h3>Damage to output, three level-effect options</h3>
<div class="notice" role="note"><strong>The "high" damage option is NOT the upper end of the literature.</strong> All three options are level-of-output effects; growth-effect estimates are larger and are not represented (D-007). Shares are of S3's own output, whose level is unvalidated.</div>
<figure><div id="ch_dmg"></div><div class="leg" id="lg_dmg"></div></figure>
<div class="note">Damage fraction = c x T^2 (c per option below). Output losses are shown as shares of S3's own output, whose level is unvalidated.</div>
<table id="tb_dmg"></table>
<h3>The loop signs</h3>
<div class="note">Signs tested in tests/test_m2_slice.py (written before the results). Magnitudes are not claims.</div>
<div id="signs"></div>
<details><summary>All caveats for the AI-race panel, including those for the withheld charts</summary>
<ul>
<li><strong>AI sector (S3).</strong> <span id="s3status"></span> It does not reproduce GATE. GATE was re-implemented from the paper, not from its code. Epoch states that GATE behaves poorly near full automation.</li>
<li><strong>Damage options.</strong> All three are level-of-output effects. The "high" option is NOT the upper end of the literature: growth-effect estimates are larger and are not represented (D-007).</li>
<li><strong>Investment rule R3</strong> is a scenario-lever rule, not a GATE replica (D-028). Against the three shipped GATE runs, with default levers and Epoch's stored composite supplied, effective compute is 43% to 72% off at worst, output 13% to 20% off, hardware up to 35% off, and the share errors reach 24 percentage points (capital) and 55 (training share) (A1.4, report only, audit/s3-r3-a1.4.md).</li>
<li><strong>Data-centre electricity.</strong> 485 TWh (2025) is a calibration point and 415 TWh (2024) a reference value; neither validates the module, and no independent test of modelled data-centre electricity against estimates exists before 2025. The IEA 2030 figure (950 TWh) is the IEA's projection under its own assumptions, shown for comparison only. Boundary: a data centre is a facility housing servers, storage, networking equipment and associated components (IEA, Energy and AI); whether crypto-mining load is excluded from the IEA totals is <strong>[unverified]</strong>.</li>
<li><strong>Assumptions to state (D-033, D-034):</strong> the 5% data-centre supply cap and the tie of energy efficiency to S3's hardware curve are assumptions; the central and high damage coefficients are <strong>derived</strong> from published anchors, not read as printed coefficients.</li>
</ul>
<h4>About the withheld compute and electricity charts (text kept from the earlier Demo 0 page)</h4>
<ul>
<li>Raw compute stock (FLOP/year, log scale) and automated fraction of tasks, for the three AI settings at the chosen damage option. Absolute compute is unvalidated against GATE after about 2027; shapes are more reliable than levels.</li>
<li>Data-centre electricity, TWh per year, chosen AI setting, central damage. "Demand" is what the installed compute would draw; "used" is capped by the share of electricity supply available to data centres (5% of the recorded Earth4All.jl TLTL electricity production, a provisional assumption). The IEA points were 2024 (415, reference) and 2025 (485, calibration point); the 2030 point (950) is the IEA's projection, not a target. Values after about 2027 inherit S3's unvalidated output; the demand curve leaves any plausible range quickly, which is a property of S3's compute path, not a finding about the world.</li>
<li>Supply binds from about 2027-2028 in this slice. The half-supply curve is not below the base curve in every year (see the recorded B1 failure below); the sign holds for the unlimited case.</li>
<li>The series are kept in <code>data/explorer.json</code> and in the generator; they are not drawn.</li>
</ul>
<h4>Recorded test results (development ensemble, 20 members)</h4>
<ul>
<li>A2.4 invariance, A2.5 extreme conditions, A2.2 consistency check, R1 and B2 signs: see tests/test_m2_slice.py outcomes in docs/tracks/track-a.md.</li>
<li>A2.6 step test (0.25 vs 0.125 year, limit 0.1%): <strong>failed</strong> (largest difference 0.56% in data-centre electricity, first above 0.1% in 2028).</li>
<li>B1 sign: <strong>failed</strong> as written (a lower supply case had up to 17.8% more compute in 2038-2045).</li>
<li>R1 sign: <strong>failed</strong> on automation at 2065 (both runs at 1.0); compute is higher.</li>
</ul>
<div class="note">Details and exact sizes: docs/tracks/track-a.md and audit/data/m2-slice-results-dev20.json. This page uses all 841 FaIR members for the climate.</div>
<table id="tb_coef"></table>
</details>
</section>

<section class="card">
<h2>What is not shown</h2>
<ul>
<li>Population, inequality, social stability, minerals, water and the full economy (these come in later milestones). The slice's economy is GATE's own, with population exogenous.</li>
<li>Uncertainty bands beyond the FaIR ensemble band; any calibration beyond the stated checks (the 2025 data-centre calibration point and the warming check, which failed); any claim about likelihood.</li>
<li>The growth-effect damage case. Climate emissions are prescribed; AI electricity does not feed back into emissions in this slice.</li>
<li>Any coupling between the three panels (World3, climate, AI race).</li>
<li>S3 compute and data-centre electricity outputs (withheld, see the AI-race panel).</li>
<li>Open caveats: GATE is re-implemented from its paper and not from its code; Epoch states GATE behaves poorly near full automation; FaIR is used as published; nothing has been validated against an independent reference beyond the tests A1 and A2 and their recorded failures.</li>
</ul></section>

<section class="card small"><h2>Sources, licences, data versions</h2>
<ul>
<li>HadCRUT.5.2.0.0 data were obtained from http://www.metoffice.gov.uk/hadobs/hadcrut5 on 2026-10-12 and are (c) British Crown Copyright, Met Office, provided under an Open Government License, http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ (used for the FaIR warming check, not drawn here).</li>
<li>Global Carbon Budget 2025 (ICOS, doi 10.18160/GCP-2025), CC BY 4.0: CO2 emissions for 2023-2024.</li>
<li>IEA (2025), Energy and AI; IEA (2026), Key Questions on Energy and AI, Licence CC BY 4.0: 415, 485 and 950 TWh.</li>
<li>FaIR 2.2.4 and the fair-calibrate v1.4.1 ensemble (Smith et al., GMD 17, 8569, 2024), Apache 2.0.</li>
<li>World3: ported from WorldDynamics.jl v1.0.0 (MIT), Python port in this project; compared with WorldDynamics.jl (tests A3.1, A3.2).</li>
<li>GATE: Erdil et al., arXiv:2503.04941 v2, CC BY 4.0 (equations only; no code used). Epoch AI playground reference runs used to test S3 and to fit R3: Epoch states its work is free to use with credit under a Creative Commons Attribution licence, but no licence is stated for the playground's script bundle itself (see the Sources page); the series are not redistributed.</li>
<li>Earth4All.jl (MIT) pinned run, electricity production series (<code>ene.EP</code>, scenario TLTL), commit 16f37d0.</li>
<li>Damage functions: Nordhaus (2017); Barrage and Nordhaus (2024); Howard and Sterner (2017). Coefficients and which numbers are printed or derived: research/damage-functions-verified.md. The central coefficient (0.344) is derived from printed anchors.</li>
</ul>
<p>Full list with licences: <a href="sources.html">Sources</a>.</p>
<details><summary>Data provenance (hashes and versions)</summary><pre id="prov"></pre></details>
</section>
"""


def index_page(data: dict, stamp: dict, css: str, js: str) -> str:
    script = "<script>\n" + js.replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))) + "\n</script>\n"
    return page("F3 Explorer v0", "index.html", INDEX_BODY, css, stamp, script)


# --------------------------------------------------------------------------------------------------------------------
def methods_page(data: dict, stamp: dict, css: str) -> str:
    prov = data["meta"]["provenance"]
    body = f"""
<h1>Methods</h1>
<p class="lead">What is run, how it is stepped, and how to read what you see. For what is wrong or unvalidated, read <a href="limitations.html">Limitations</a>.</p>
{BANNER}
<section class="card"><h2>The three model pieces</h2>
<ul>
<li><strong>World3</strong> (<em>The Limits to Growth</em>, 1974 version and its 2004 update). F3 contains a Python port of five World3 sectors (population, agriculture, capital, non-renewable resources, persistent pollution), ported from WorldDynamics.jl v1.0.0 (MIT). The Explorer shows the <strong>2004 parameter set</strong>, the provisional default (D-015). The reference environment is a pinned registry snapshot of 2024-04-25 with default solver options (D-017). The standard run was compared with WorldDynamics.jl: every state of the four ported sectors within 0.124% (A3.1) and all 29 states within 2% (A3.2, worst 1.906%).</li>
<li><strong>Climate</strong>: FaIR 2.2.4 (Apache 2.0), unmodified, with the published fair-calibrate v1.4.1 constrained ensemble of <strong>841 members</strong> (Smith et al., 2024). Emissions are prescribed: CO2 from the Global Carbon Budget 2025 for 2023-2024, and all other gases and later years from a scenario file of the ensemble's own; no F3 sector produces them (D-021).</li>
<li><strong>AI race</strong>: S3, a re-implementation of the laws of motion, automation and production of GATE (Erdil et al., arXiv:2503.04941) written from the paper, not from Epoch's code, driven by an investment rule R3 (D-028), plus a data-centre electricity module and a damage function (D-007). Withheld outputs are described on the page.</li>
</ul></section>

<section class="card"><h2>Time and coupling</h2>
<ul>
<li>The model loop steps by <strong>0.25 year</strong> (D-003). Sectors exchange values at step boundaries; each sector reads the other sectors' values at the <em>start</em> of the step and holds them across it (explicit coupling, D-022). <code>t = Y</code> is 1 January of year Y; stocks are values on that date.</li>
<li><strong>World3 sub-steps (D-031).</strong> The five World3 sectors are advanced together as one group in <strong>0.0625-year sub-steps</strong> inside each 0.25-year loop step, with the same start-of-sub-step coupling among them. With plain 0.25-year coupling the full-run test A3.2 failed (worst state 6.90% for the 1974 set and 7.96% for the 2004 set, against 2%); at 0.0625 year no state exceeded 2%. The Sector interface and D-003 and D-022 are unchanged.</li>
<li>The AI sector advances in whole-year periods (GATE's own convention); the climate sector is re-run <strong>from 1750 every year with all 841 members</strong> and nothing carried between years (D-021 option a, chosen by the editor after measuring the alternatives).</li>
<li><strong>The three panels are not coupled.</strong> In this version World3 runs alone, the climate path is a single recorded run replayed (exact, because emissions are prescribed and no lever changes them), and the AI-race run takes the warming from that recording.</li>
</ul></section>

<section class="card"><h2>Scenario grids</h2>
<ul>
<li>The Explorer is a <strong>static page of precomputed runs</strong> (D-009): no model runs in your browser and nothing is sent anywhere.</li>
<li>World3: 3 levers x 3 values = 27 runs (D-046, Provisional): initial non-renewable resources (0.5e12, <strong>1e12 standard</strong>, 2e12), land yield factor after 1975 (<strong>1.0 standard</strong>, 1.5, 2.0), persistent-pollution generation factor after 1975 (<strong>1.0 standard</strong>, 0.5, 0.25).</li>
<li>AI race: 3 investment settings (low, central, race; levers of the R3 rule) x 3 damage options = 9 runs, plus two electricity-supply cases kept in the data for the sign test.</li>
</ul></section>

<section class="card"><h2>How to read a band</h2>
<ul>
<li>The <strong>shaded band on the climate chart</strong> is the 5th to 95th percentile across the 841 members of the published constrained ensemble; the line is their mean. Each member has its own climate parameters and its own seeded internal variability. It describes the spread of that ensemble under the prescribed emissions. It is <strong>not</strong> a probability statement about the real climate and not an uncertainty analysis of the whole model.</li>
<li><strong>World3 and S3 are single runs with no band</strong>: each curve is one run under the stated settings. A different parameter, or a different version of the model, gives a different curve, and the Explorer does not say how likely any curve is.</li>
<li>Where a curve is dashed grey (World3 panel) it is the standard run, shown for comparison when you change a lever.</li>
</ul></section>

<section class="card"><h2>Pins and versions</h2>
<ul>
<li>FaIR 2.2.4; fair-calibrate v1.4.1 ensemble files at FaIR repository commit <code>{prov["fair_commit"]}</code>.</li>
<li>WorldDynamics.jl v1.0.0 (pinned environment); Earth4All.jl commit <code>16f37d013a2f68135f03e7815bf861dbf47311f2</code> (electricity supply series only).</li>
<li>HadCRUT.5.2.0.0 (used for the FaIR warming check, not drawn); Global Carbon Budget 2025 v1.0.</li>
<li>All hashes are on the <a href="index.html">Explorer</a> page under "Data provenance".</li>
</ul></section>
"""
    return page("Methods - F3 Explorer v0", "methods.html", body, css, stamp)


# --------------------------------------------------------------------------------------------------------------------
def limitations_page(data: dict, stamp: dict, css: str) -> str:
    body = f"""
<h1>Limitations</h1>
<p class="lead">Every caveat in one place, with the failed tests stated plainly. Nothing on this page has been softened; sizes are the recorded ones.</p>
{BANNER}

<section class="card"><h2>Tests that failed (recorded, not relaxed)</h2>
<div class="failblock"><h3 class="fail">A1.3</h3><p class="note"><strong>What it checked:</strong> The AI sector (S3) against the three runs shipped by Epoch AI's GATE playground, within 2% at every year, with GATE's own investment path supplied</p><p><strong>Result:</strong> <strong>Failed</strong> for all three runs. Output first exceeds 2% in 2026-27; capital, hardware, software and compute from 2027-33. With Epoch's own task-composite supplied, every quantity matches, so the gap is S3's task-allocation step; its cause is unresolved. Three different discretisations of that step gave the same failure. S3's absolute output (output, capital, effective compute) is <strong>unvalidated after about 2027</strong>. S3 does <strong>not</strong> reproduce GATE.</p></div>
<div class="failblock"><h3 class="fail">A1.4</h3><p class="note"><strong>What it checked:</strong> The investment rule R3 against GATE's own investment path (report only, no pass or fail)</p><p><strong>Result:</strong> <strong>Poor agreement.</strong> With Epoch's stored composite supplied, effective compute is 43% to 72% off at worst and output 13% to 20% off; hardware up to 35% off; investment shares up to 24 percentage points off (capital) and 55 (training share). R3 is a scenario-lever rule, not a GATE replica; it was fitted to the same three runs.</p></div>
<div class="failblock"><h3 class="fail">A2.1</h3><p class="note"><strong>What it checked:</strong> FaIR's ensemble-mean warming for 2015-2024 against HadCRUT5's mean 95% interval</p><p><strong>Result:</strong> <strong>Failed.</strong> FaIR gives 1.196 K above 1850-1900; the HadCRUT5 interval is 1.234 to 1.305 K. FaIR is 0.037 K below the lower edge and 0.073 K below the best estimate. 2023 and 2024 (outside the ensemble's calibration window) run 0.16 to 0.20 K low; the cause is untested. Scenario warming therefore starts about 0.04 to 0.07 K below observed for the current decade.</p></div>
<div class="failblock"><h3 class="fail">A2.6</h3><p class="note"><strong>What it checked:</strong> Halving the loop step (0.25 to 0.125 year) changes the slice's outputs by at most 0.1%</p><p><strong>Result:</strong> <strong>Failed.</strong> Largest difference 0.565% in data-centre electricity (first above 0.1% in 2028); output 0.197%; compute 0.108%.</p></div>
<div class="failblock"><h3 class="fail">B1 sign</h3><p class="note"><strong>What it checked:</strong> Lowering electricity supply lowers compute growth afterwards</p><p><strong>Result:</strong> <strong>Failed as written.</strong> Halving supply gave up to 17.8% <em>more</em> compute in 2038-2045. The suspected cause (the investment rule depends on usable compute) is inferred, not tested.</p></div>
<div class="failblock"><h3 class="fail">R1 sign</h3><p class="note"><strong>What it checked:</strong> Raising the AI investment share raises compute and automation</p><p><strong>Result:</strong> <strong>Failed on automation:</strong> both runs are at 1.0 by 2065, so no increase can be seen (compute is higher).</p></div>
<div class="failblock"><h3 class="fail">A3.4(b)</h3><p class="note"><strong>What it checked:</strong> World3's population sector inside the full model equals the same sector run alone with recorded inputs, within 0.25%</p><p><strong>Result:</strong> <strong>Failed.</strong> Up to 1.019% (1974 parameter set) and 0.931% (2004 set). The reading that it reflects small differences in the other four sectors, not an error in the population equations, is inferred, not tested.</p></div>
<div class="failblock"><h3 class="fail">A4.5</h3><p class="note"><strong>What it checked:</strong> (Not shown in the Explorer.) The ported Earth4All economy sectors together reproduce the Earth4All.jl economy within 2%</p><p><strong>Result:</strong> <strong>Failed</strong> in both scenarios from about 2076 (GDP up to 2.5%, inequality up to 3.2%); accepted as recorded by the editor.</p></div>
</section>

<section class="card"><h2>What is, and is not, compared with anything</h2>
<ul>
<li><strong>World3:</strong> only the <em>standard</em> parameters were compared with WorldDynamics.jl. The Explorer's runs with changed parameters have not been compared with any reference. Extreme settings (for example a land yield factor of 2.0, which ends with a population of about 0.4 billion) show what the ported equations do under that input; nothing says it is right.</li>
<li><strong>AI race:</strong> unvalidated against GATE after about 2027 (above). Compute and data-centre electricity outputs are withheld because they leave any plausible range (in the recorded runs modelled data-centre demand reaches about 7 billion TWh a year by 2100, against about 485 TWh in 2025; the earlier recorded figures were about 20,000 TWh in 2030 and 414,000 TWh in 2040); that is a property of S3's compute path, not a finding about the world.</li>
<li><strong>Data-centre module:</strong> 485 TWh (2025) is a <em>calibration point</em>, 415 TWh (2024) a reference value; neither validates the module, and no independent test of modelled data-centre electricity against estimates exists before 2025. The IEA's 950 TWh for 2030 is the IEA's projection under its own assumptions. The IEA's formal definition of a data centre could not be verified: whether crypto-mining load is excluded from its totals is <strong>[unverified]</strong>. The 5% cap on the share of electricity supply available to data centres and the tie of energy efficiency to S3's hardware curve are assumptions.</li>
<li><strong>Climate:</strong> FaIR is used as published. Non-CO2 emissions and land-use CO2 are prescribed, not modelled. The ensemble was constrained to data through 2022. The band is the ensemble band only.</li>
<li><strong>Damages:</strong> the three options are level-of-output effects (Nordhaus 2017, Barrage and Nordhaus 2024, Howard and Sterner 2017). <strong>"High" is not the upper end of the literature:</strong> growth-effect estimates (for example Burke, Hsiang and Miguel 2015, whose abstract reports about 23% lower average global incomes by 2100) are larger and are not represented; their coefficients were not readable in the copy obtained and are <strong>[unverified]</strong>. The central and high coefficients are <strong>derived</strong> from printed anchors, not read as printed coefficients. The temperature baseline of Nordhaus (2017) is not stated in the text read <strong>[unverified]</strong>; FaIR's baseline is 1850-1900 and no offset is applied. Shares are of S3's own output, whose level is unvalidated.</li>
<li><strong>The panels are not coupled</strong> to each other.</li>
<li><strong>No health or yield effect of warming:</strong> the warming effects on life expectancy and on land yield (and the CO2 effect on yield and on the CO2 lifetime) that Earth4All has are omitted by decision (D-049); World3's population and food have no warming term, so warming does not reach them. To be revisited.</li>
<li><strong>Not shown at all:</strong> population (beyond World3's own), inequality, social stability, minerals, water, the full economy, uncertainty bands beyond the FaIR ensemble band, any likelihood.</li>
</ul></section>

<section class="card"><h2>Provenance of choices</h2>
<ul>
<li>GATE was re-implemented from the paper (arXiv:2503.04941 v2), not from Epoch's code. Epoch states that GATE behaves poorly near full automation.</li>
<li>Some design choices are <strong>Provisional (delegated)</strong>, not approved by the editor (for example the World3 levers, D-046, and the data-centre module, D-032 to D-036). They are listed in the project's decision register.</li>
<li>The Explorer is a local draft; it has not been approved for publication.</li>
</ul></section>
"""
    return page("Limitations - F3 Explorer v0", "limitations.html", body, css, stamp)


# --------------------------------------------------------------------------------------------------------------------
def sources_page(data: dict, stamp: dict, css: str) -> str:
    body = f"""
<h1>Sources and licences</h1>
<p class="lead">References, what each is used for, and its licence. Licences are stated as read from the providers' own pages unless marked otherwise; this is a practical reading, not legal advice.</p>
{BANNER}

<section class="card"><h2>F3's own licences</h2>
<ul>
<li><strong>Code: Apache License 2.0.</strong> <strong>Documentation and processed data: CC BY 4.0.</strong> Third-party data keeps its original licence (D-001).</li>
<li>Source code and records: <a href="{REPO_URL}">{REPO_URL}</a>.</li>
</ul></section>

<section class="card"><h2>Models whose equations or code F3 uses</h2>
<table>
<tr><th>Source</th><th>Use in F3</th><th>Licence and attribution</th></tr>
<tr><td><strong>WorldDynamics.jl</strong> v1.0.0 (the WorldDynamics.jl contributors: Pierluigi Crescenzi, Emanuele Natale, Aurora Rossi, Paulo Bruno Serafim and others), github.com/worlddynamics/WorldDynamics.jl</td><td>World3 sectors ported to Python (population, agriculture, capital, non-renewable resources, persistent pollution); also the reference the port is compared with</td><td>MIT. The licence text is kept in the repository (<code>licenses/WorldDynamics.jl-MIT.txt</code>) with an attribution entry in <code>NOTICE</code>.</td></tr>
<tr><td><strong>Earth4All.jl</strong> (Copyright (c) 2023 World Dynamics), commit 16f37d013a2f68135f03e7815bf861dbf47311f2, github.com/worlddynamics/Earth4All.jl</td><td>Reused economy and energy sectors ported (not shown in the Explorer); one recorded electricity-production series (<code>ene.EP</code>, scenario Too Little Too Late) used as the electricity supply of the AI-race run</td><td>MIT; licence text in <code>licenses/Earth4All.jl-MIT.txt</code>, entry in <code>NOTICE</code>. Nothing from the package's Vensim sources or Vensim output is copied (D-014).</td></tr>
<tr><td><strong>PyWorld3</strong> 1.1</td><td>Used <em>unmodified</em> from PyPI as a second check in tests only</td><td>CeCILL 2.1 (copyleft). None of its code is copied into F3 (D-001, D-012).</td></tr>
<tr><td><strong>FaIR</strong> 2.2.4 and the fair-calibrate v1.4.1 constrained ensemble (Smith et al., Geoscientific Model Development 17, 8569, 2024)</td><td>Climate panel; used as published</td><td>Apache 2.0 (the repository and the package). The licences of the data underneath the ensemble's emissions file (CEDS, PRIMAP-hist, GFED, Global Carbon Project) were <strong>not verified</strong>; the calibration files are fetched by script and not redistributed here.</td></tr>
<tr><td><strong>GATE</strong>: Erdil et al., arXiv:2503.04941 v2</td><td>S3 re-implemented from the paper's equations (no code used)</td><td>CC BY 4.0 (the paper).</td></tr>
</table></section>

<section class="card"><h2>Data</h2>
<table>
<tr><th>Source</th><th>Use</th><th>Licence and required acknowledgement</th></tr>
<tr><td><strong>HadCRUT5</strong>, HadCRUT.5.2.0.0 analysis (Morice et al., 2021, doi 10.1029/2019JD032361)</td><td>The FaIR warming test (not drawn on the Explorer)</td><td>Open Government Licence v3.0. <em>HadCRUT.5.2.0.0 data were obtained from http://www.metoffice.gov.uk/hadobs/hadcrut5 on 2026-10-12 and are (c) British Crown Copyright, Met Office, provided under an Open Government License, http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/</em> The year of first publication was not stated on the pages read. Not redistributed here.</td></tr>
<tr><td><strong>Global Carbon Budget 2025</strong> v1.0 (Global Carbon Project, ICOS Carbon Portal, doi 10.18160/GCP-2025; Friedlingstein et al., 2026)</td><td>CO2 emissions for 2023-2024</td><td>CC BY 4.0 (ICOS data licence). A small extract is committed with attribution.</td></tr>
<tr><td><strong>IEA</strong>, Energy and AI (2025) and Key Questions on Energy and AI (2026)</td><td>Reference figures for data-centre electricity: 415 TWh (2024), 485 TWh (2025, used as a calibration point), 950 TWh (2030, the IEA's projection)</td><td>CC BY 4.0, as printed in the citation lines of the two documents.</td></tr>
<tr><td><strong>Epoch AI GATE playground</strong> (epoch.ai/gate), three precomputed runs</td><td>Test references for S3 and the data to which the investment rule R3 was fitted</td><td>Epoch states that its work is free to use with credit under a Creative Commons Attribution licence. <strong>No licence is stated for the playground's script bundle or the data inside it</strong>, so under D-026 the series are read at test time from a hash-pinned local copy and <strong>never committed or redistributed</strong>; only comparison figures and fitted curve parameters are stored. Permission has not been granted in writing.</td></tr>
<tr><td><strong>Damage-function sources</strong>: Nordhaus (2017); Barrage and Nordhaus (2024); Howard and Sterner (2017); context: Burke, Hsiang and Miguel (2015)</td><td>The three damage options; which numbers are printed and which derived is in the repository (<code>research/damage-functions-verified.md</code>)</td><td>Open-access texts read from PMC, Europe PMC and the publishers' open-access copies; the Burke copy was an author copy. Not redistributed. Hsiang et al. (2017) could not be read.</td></tr>
</table></section>

"""
    return page("Sources - F3 Explorer v0", "sources.html", body, css, stamp)


# --------------------------------------------------------------------------------------------------------------------
def about_page(data: dict, stamp: dict, css: str) -> str:
    dirty = "the working tree had uncommitted changes when this was built" if stamp.get("dirty") == "yes" else "the working tree was clean when this was built"
    body = f"""
<h1>About F3</h1>
{BANNER}
<section class="card"><h2>What F3 is</h2>
<p><strong>F3 (Foundation for Earth) is an open global model of how the AI race interacts with the planet's limits and society's stability.</strong> It puts planetary-limits models (World3, Earth4All) and an AI-transition model (GATE, by Epoch AI) into one set of feedback loops. It does not predict the future: it produces <strong>conditional scenarios</strong>, meaning <em>if</em> these assumptions hold, <em>then</em> these trajectories follow, to show which levers and feedback loops matter. The project is led by Stéphane Beau, who approves or rejects every decision in its register.</p>
<p>This Explorer is a first, partial version: three pieces that are not yet coupled, with several recorded test failures, shown with their labels. Its purpose at this stage is to make the state of the work visible, not to inform decisions about the world.</p>
</section>
<section class="card"><h2>Source code, records and errors</h2>
<ul>
<li>Source code, decision register, test reports and data cards: <a href="{REPO_URL}">{REPO_URL}</a>.</li>
<li><strong>To report an error</strong> (a wrong number, a missing caveat, a broken page, a licence concern): open an issue at <a href="{REPO_URL}/issues">{REPO_URL}/issues</a>. Please say which page and which chart or sentence.</li>
</ul></section>
<section class="card"><h2>How to cite</h2>
<p>Beau, S. (2026). <em>F3 (Foundation for Earth): an open global simulation model. Explorer v0 (draft).</em> {REPO_URL}, source commit {stamp["commit"]}, accessed {stamp["date"]}.</p>
<p class="note">There is no DOI and no published paper yet. If you cite a figure, please cite the date and commit, and state that it is a conditional scenario from a draft with recorded test failures.</p>
</section>
<section class="card"><h2>This version</h2>
<ul>
<li>Built <strong>{stamp["date"]}</strong> from source commit <code>{stamp["commit"]}</code>; {dirty}. (The page is committed after it is built, so the commit that contains this page is the next one on the branch.)</li>
<li>Status: local draft, not published; the editor has not approved publication.</li>
<li>Language: English only in this version.</li>
</ul></section>
"""
    return page("About - F3 Explorer v0", "about.html", body, css, stamp)


def render_all(data: dict, stamp: dict, here: Path) -> dict:
    css = (here / "style.css").read_text(encoding="utf-8")
    js = (here / "explorer.js").read_text(encoding="utf-8")
    return {
        "index.html": index_page(data, stamp, css, js),
        "methods.html": methods_page(data, stamp, css),
        "limitations.html": limitations_page(data, stamp, css),
        "sources.html": sources_page(data, stamp, css),
        "about.html": about_page(data, stamp, css),
    }
