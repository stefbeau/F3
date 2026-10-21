"""Body of the Explorer page (index.html), v0.1 (D-052). Pure markup; the numbers in the takeaway cards and charts are drawn by explorer.js from the data."""
import ig

PUBLIC = "Public draft, published 2026-10-21. Conditional scenarios, not forecasts."


def tip(term, text):
    return f'<abbr title="{text}">{term}</abbr>'


S3, R3 = (tip("S3", "S3 is this project's AI-economy model: a re-implementation of the GATE equations for output, automation and compute, driven by a scenario investment rule. Its levels are unvalidated."),
          tip("R3", "R3 is the scenario-lever rule that sets how much S3 invests in compute, hardware research and software research. It is a lever, not a replica of GATE."))
FAIR = tip("FaIR", "FaIR is the open climate model used here, with the published 841-member calibrated ensemble. Emissions are prescribed, so every scenario has the same climate.")
GATE = tip("GATE", "GATE is Epoch AI's model of the economy under AI automation. F3 re-implemented its equations from the paper; the re-implementation does not reproduce GATE after about 2027.")
W3 = tip("World3", "World3 is the system-dynamics model behind The Limits to Growth: population, food, industry, resources and pollution, 1900 to 2100.")

BODY = f"""
<h1>F3 Explorer v0.1</h1>
<p class="lead">Three model pieces to explore: a {W3} scenario grid, a {FAIR} climate run, and an AI-race run ({S3}). One link between them is built: climate damage to World3 industrial output (off by default).</p>
<div class="banner" role="note"><strong class="big">{PUBLIC}</strong>Every curve in the Explorer is the output of a model run under stated assumptions. None is a prediction, none has a likelihood. Recorded test failures are shown with the panels and on the <a href="limitations.html">Limitations</a> page.</div>

<section class="card" id="readfirst" aria-labelledby="rf_h">
<h2 id="rf_h">Read this first</h2>
<ul class="rfl">
<li class="rf"><strong>Scenarios, not forecasts.</strong> Each curve is one model run under stated assumptions. It has no probability and says nothing about what will happen.</li>
<li class="rf"><strong>Only one link between the pieces is built:</strong> warming lowers World3 industrial output, through a damage function, switched off by default. The AI model and World3 are two models of the same world and are not connected or reconciled.</li>
<li class="rf"><strong>Check the status badges.</strong> The climate run missed its test against observations by a small margin, the AI model's levels are unvalidated, and World3 was compared with its reference only for the standard run. Compute and electricity outputs are withheld.</li>
</ul>
</section>

<nav class="tabs" aria-label="Panels"><a href="#p_w3">World3</a><a href="#p_climate">Climate</a><a href="#p_ai">AI race</a><a href="#connected">What is connected</a><a href="#notshown">Not shown</a></nav>

<section class="card" id="connected">
<h2>What is connected</h2>
<p class="note">Solid arrows are links that are built and tested today. Dashed arrows are links that are not built. Nothing in the Explorer depends on a dashed arrow.</p>
<h3>Feedback loops</h3>
{ig.LOOPS}
{ig.LOOPS_KEY}
<h3>Roadmap</h3>
{ig.ROADMAP}
{ig.ROADMAP_KEY}
</section>

<!-- ========================= PANEL 1: WORLD3 ========================= -->
<section class="card" id="p_w3">
<h2>1. {W3} scenarios <a class="badge amber" href="limitations.html#status-world3"><span aria-hidden="true">&#9650;</span> Amber: standard run matches its reference; A3.4(b) failed; changed runs not compared</a></h2>
<div class="take" id="tk_w3" aria-live="polite"></div>
<div class="notice" role="note"><strong>Status:</strong> the standard run with climate damage off matches WorldDynamics.jl (tests A3.1 and A3.2 met); test A3.4(b) failed; runs with changed parameters, and all runs with climate damage on, are not compared with anything (WorldDynamics.jl has no climate damage). Population, industrial output, resources and pollution, 1900-2100; precomputed grid, 3 levers x 3 values x 4 damage states. <strong>No health or yield effect of warming</strong> is modelled.</div>
<div class="grp">Scenario</div>
<div class="presets" id="w3_presets" role="group" aria-label="Scenario presets"></div>
<div class="ctl one"><label>Climate damage to industrial output <span class="note">(default off)</span><br><select id="w3_damage"></select></label></div>
<div class="notice damage" id="w3_damage_notice" role="note" aria-live="polite"></div>
<details id="w3_custom"><summary>Custom: set each World3 parameter</summary><div class="ctl" id="w3ctl"></div></details>
<div class="chips" id="w3_chips" aria-label="Changes against the standard run"></div>
<div class="note" id="w3_text"></div>
<figure><div id="ch_w3pop"></div><div class="leg" id="lg_w3pop"></div></figure>
<figure><div id="ch_w3io"></div><div class="leg" id="lg_w3io"></div></figure>
<figure><div id="ch_w3nr"></div><div class="leg" id="lg_w3nr"></div></figure>
<figure><div id="ch_w3pol"></div><div class="leg" id="lg_w3pol"></div></figure>
<details><summary>What this panel is, and its test status</summary>
<ul id="w3status"></ul>
<ul>
<li>The levers are World3 parameters chosen as a <strong>Provisional (delegated)</strong> decision, not an approved one (D-046, docs/site-explorer.md). They are not forecasts of anything; they show how the 1900-2100 World3 run changes when one parameter changes.</li>
<li><strong>Climate damage (D-051, D-052).</strong> When switched on, World3's industrial output is multiplied by (1 minus the damage fraction) from 2025. The damage fraction is c x T^2 with T the {FAIR} ensemble-mean warming above 1850-1900 from the recorded run (no new climate run per scenario) and c from the chosen D-007 option. It is a <strong>level-of-output effect, not the upper end of the literature</strong>: growth-effect estimates are larger and are not represented. No new coefficient was introduced. The change flows through every link industrial output has in World3 (investment, agriculture, resources, population), so it is not a health or yield effect of warming. With damage on, the run is not compared with WorldDynamics.jl; the M6 tests check that switching damage off returns the stand-alone World3 to 1e-9, that zero warming changes nothing, that more warming lowers industrial output, and that nothing is NaN or negative over the whole grid.</li>
<li>World3 is run as the D-031 group: its five sectors take 0.0625-year sub-steps inside the model's 0.25-year loop.</li>
<li>The 2004 parameter set is the provisional default (D-015); the 1974 set exists in the code and is not shown.</li>
<li>Resources are shown as the fraction of the starting stock that remains (the starting stock is the chosen lever value); pollution as the persistent-pollution index (1 = the 1970 level); industrial output in dollars a year as World3 defines it.</li>
<li>World3 is a single run per setting: there is no band and no uncertainty analysis.</li>
<li><strong>No health or yield effect of warming.</strong> World3's population and food sectors have no warming term, and the four warming effects of Earth4All that would act on them (life expectancy, land yield, CO2 fertilisation and the CO2 lifetime) are deliberately omitted (D-049).</li>
<li>S3's economy and World3's are not reconciled: they are two models of the same world, and the AI-race panel does not change anything in this panel.</li>
</ul></details>
</section>

<!-- ========================= PANEL 2: CLIMATE ========================= -->
<section class="card" id="p_climate">
<h2>2. Climate ({FAIR}) <a class="badge amber" href="limitations.html#status-climate"><span aria-hidden="true">&#9650;</span> Amber: test A2.1 failed by 0.037 K</a></h2>
<div class="take" id="tk_climate" aria-live="polite"></div>
<div class="notice" role="note"><strong>Status:</strong> test A2.1 failed. FaIR climate starts about 0.04 to 0.07 K below observed for the current decade, and non-CO2 emissions are prescribed, not modelled (D-030, D-021). The FaIR test against HadCRUT5 for 2015-2024 failed.</div>
<figure><div id="ch_temp"></div><div class="leg" id="lg_temp"></div></figure>
<h3>Warming stripes</h3>
{ig.STRIPES}
{ig.STRIPES_CAP}
<details><summary>Caveats and details for the climate panel</summary>
<div class="note">FaIR warming above 1850-1900, ensemble of 841 members: mean (line) and 5th-95th percentile (band). Prescribed emissions do not respond to any lever here, so the temperature path is the same for every setting and damage option: the damage options change output, not temperature. The band is the FaIR ensemble band only (not an uncertainty analysis of the whole model). FaIR starts about 0.04 to 0.07 K below observed for the current decade. This same recorded mean drives the climate damage in the World3 panel and in the AI-race panel.</div>
<ul>
<li><strong>Climate (FaIR).</strong> FaIR climate starts about 0.04 to 0.07 K below observed for the current decade (D-030); non-CO2 emissions are prescribed, not modelled (D-021). The test of FaIR against HadCRUT5 for 2015-2024 failed (ensemble mean 0.037 K below the interval). <span id="s6status"></span></li>
</ul></details>
</section>

<!-- ========================= PANEL 3: AI RACE ========================= -->
<section class="card" id="p_ai">
<h2>3. AI race: automation and damage <a class="badge red" href="limitations.html#status-ai"><span aria-hidden="true">&#9632;</span> Red: S3 failed its test against GATE; levels unvalidated</a></h2>
<div class="take" id="tk_ai" aria-live="polite"></div>
<div class="notice" role="note"><strong>Status:</strong> the AI sector ({S3}) failed its test against {GATE} (A1.3): its absolute output is unvalidated after about 2027, and it does not reproduce GATE. Shapes are more reliable than levels. Not a forecast.</div>
<div class="withheld" role="note">Compute and electricity outputs are withheld until the S3 compute path is validated (awaiting Epoch AI); they currently leave any plausible range.</div>
<div class="ctl">
<label>AI investment setting ({R3} rule) <select id="sel_s"><option value="low">low</option><option value="central" selected>central</option><option value="race">race</option></select></label>
<label>Damage option <select id="sel_d"><option value="low">low (Nordhaus 2017)</option><option value="central" selected>central (Barrage and Nordhaus 2024)</option><option value="high">high (Howard and Sterner 2017; not the upper end)</option></select></label>
</div>
<div class="note">The automation chart changes with the AI setting; the damage chart changes with the damage option. The climate panel has no controls: emissions are prescribed.</div>
<div class="note" id="setting_text"></div>
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

<section class="card" id="notshown">
<h2>What is not shown</h2>
<ul>
<li>Inequality, social stability, minerals, water and the full economy (these come in later milestones). The AI-race slice's economy is GATE's own, with population exogenous.</li>
<li>Uncertainty bands beyond the FaIR ensemble band; any calibration beyond the stated checks (the 2025 data-centre calibration point and the warming check, which failed); any claim about likelihood.</li>
<li>The growth-effect damage case. Climate emissions are prescribed; neither World3 nor AI electricity feeds back into emissions.</li>
<li>Any coupling other than climate damage to World3 industrial output and to S3 output (the dashed arrows in "What is connected").</li>
<li>S3 compute and data-centre electricity outputs (withheld, see the AI-race panel).</li>
<li>Open caveats: GATE is re-implemented from its paper and not from its code; Epoch states GATE behaves poorly near full automation; FaIR is used as published; nothing has been validated against an independent reference beyond the tests A1, A2 and A3 and their recorded failures.</li>
</ul></section>

<section class="card small"><h2>Sources, licences, data versions</h2>
<ul>
<li>HadCRUT.5.2.0.0 data were obtained from http://www.metoffice.gov.uk/hadobs/hadcrut5 on 2026-10-12 and are (c) British Crown Copyright, Met Office, provided under an Open Government License, http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ (used for the FaIR warming check, not drawn here).</li>
<li>Global Carbon Budget 2025 (ICOS, doi 10.18160/GCP-2025), CC BY 4.0: CO2 emissions for 2023-2024.</li>
<li>IEA (2025), Energy and AI; IEA (2026), Key Questions on Energy and AI, Licence CC BY 4.0: 415, 485 and 950 TWh.</li>
<li>FaIR 2.2.4 and the fair-calibrate v1.4.1 ensemble (Smith et al., GMD 17, 8569, 2024), Apache 2.0.</li>
<li>World3: ported from WorldDynamics.jl v1.0.0 (MIT), Python port in this project; the standard run is compared with WorldDynamics.jl (tests A3.1, A3.2).</li>
<li>GATE: Erdil et al., arXiv:2503.04941 v2, CC BY 4.0 (equations only; no code used). Epoch AI playground reference runs used to test S3 and to fit R3: Epoch states its work is free to use with credit under a Creative Commons Attribution licence, but no licence is stated for the playground's script bundle itself (see the Sources page); the series are not redistributed.</li>
<li>Earth4All.jl (MIT) pinned run, electricity production series (<code>ene.EP</code>, scenario TLTL), commit 16f37d0.</li>
<li>Damage functions: Nordhaus (2017); Barrage and Nordhaus (2024); Howard and Sterner (2017). Coefficients and which numbers are printed or derived: research/damage-functions-verified.md. The central coefficient (0.344) is derived from printed anchors.</li>
</ul>
<p>Full list with licences: <a href="sources.html">Sources</a>.</p>
<details><summary>Data provenance (hashes and versions)</summary><pre id="prov"></pre></details>
</section>
"""
