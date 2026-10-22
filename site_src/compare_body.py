"""Markup of the Compare page (compare.html), D-056 stage 4: baseline (standard run, damage off) against scenario A and scenario B, each a preset plus a damage option.
Nothing here holds a model number; compare.js writes the headline, charts and delta table from the data."""
import dash_blocks as B
import index_body

PUBLIC = index_body.PUBLIC


def picker(k: str, letter: str) -> str:
    return (f'<fieldset class="pick {k}"><legend><span class="badgeletter {k}" aria-hidden="true">{letter}</span> Scenario {letter}</legend>'
            f'<label for="sel_{k}">Story</label><select id="sel_{k}"></select>'
            f'<span class="ctllab" id="dmg_{k}_lab">Climate damage</span><div class="seg" id="seg_{k}" role="group" aria-labelledby="dmg_{k}_lab"></div></fieldset>')


def body() -> str:
    return f"""
<div class="banner compact" role="note"><strong class="big">{PUBLIC}</strong>Every curve is the output of a model run under stated assumptions. None is a prediction, none has a likelihood. See <a href="limitations.html">Limitations</a>.</div>
<div class="dash" id="dash" data-step="result">
<aside class="rail" id="choose" aria-labelledby="choose_h">
<h2 id="choose_h">Pick two scenarios</h2>
<p class="note">The baseline is fixed: the standard run with climate damage off (grey, dashed). Each scenario is a story plus a climate-damage option.</p>
{picker("a", "A")}
{picker("b", "B")}
<button type="button" id="swap">Swap A and B</button>
<button type="button" class="reset" id="reset">Reset to the default pair</button>
</aside>
<div class="stage">
<section id="result" aria-labelledby="headline">
<h1 class="headline" id="headline">Compare two scenarios with the standard run</h1>
<p class="note" id="names"></p>
<div class="ctlrow"><span class="ctllab" id="metric_lab">Overlay chart shows</span><div class="seg" id="metric_seg" role="group" aria-labelledby="metric_lab"></div></div>
<div id="ch_over"></div>
<div id="ch_bars"></div>
<div class="notice" id="identical_note" role="note"></div>
<h2 class="h2s">Table: scenario values and differences in <span id="tbl_year">2100</span></h2>
<div class="tblwrap" tabindex="0" role="region" aria-label="Delta table, scrolls sideways on a narrow screen"><table class="delta" id="tb_delta"></table></div>
<p class="dl"><button type="button" id="delta_csv">Download table as CSV</button></p>
</section>
<section id="reliability" aria-labelledby="rel_h">
<h2 id="rel_h">How reliable is this?</h2>
<div class="notice damage" id="cmp_damage_notice" role="note" aria-live="polite"></div>
<p class="badges"><a class="badge amber" href="limitations.html#status-world3"><span aria-hidden="true">&#9650;</span> World3: standard run matches its reference; A3.4(b) failed; changed runs not compared</a>
<a class="badge amber" href="limitations.html#status-climate"><span aria-hidden="true">&#9650;</span> Climate: A2.1 failed by 0.037 K</a></p>
<ul>
<li>Each curve is one model run under stated assumptions: no band, no probability, a conditional scenario and not a forecast. The AI-race run is not part of this comparison (it is not connected to World3: S3's economy and World3's are not reconciled).</li>
<li>Only the standard parameters with climate damage off were compared with WorldDynamics.jl. Damage-on runs are not compared with WorldDynamics.jl (it has no climate damage), and scenario runs with changed parameters are not compared with anything. <strong>High is not the upper end of the literature.</strong></li>
<li>No health or yield effect of warming is modelled; warming is the same in the baseline and in both scenarios because emissions are prescribed.</li>
<li>The recorded tests and their results are in the table under Details on the <a href="explorer.html#reliability">Explorer</a> page and on <a href="limitations.html">Limitations</a>.</li>
</ul>
</section>
</div>
<nav class="actionbar" id="actionbar" aria-label="Steps"><button type="button" data-step="choose">Choose story</button><button type="button" data-step="result" aria-current="step">Result</button><button type="button" data-step="reliability">Reliability</button></nav>
</div>
"""
