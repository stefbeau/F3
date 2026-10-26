"""Markup of the story front door (index.html), D-056 stage 2. Four chapters, each: a finding title (written by story.js from the data), one annotated chart,
one control. Nothing here holds a model number; the static text is the fallback shown before the script runs."""
import ig
import index_body
import links

S3, GATE, FAIR, W3 = index_body.S3, index_body.GATE, index_body.FAIR, index_body.W3
PUBLIC = index_body.PUBLIC

STEPS = [("ch1", "Standard world"), ("ch2", "Add the heat"), ("ch3", "The AI race"), ("ch4", "Connected?")]


def steps_nav() -> str:
    items = "".join(f'<li><a href="#{i}"><span class="stepn">{n}</span><span class="stept">{t}</span></a></li>' for n, (i, t) in enumerate(STEPS, 1))
    return f'<nav class="steps" id="steps" aria-label="Story steps, four chapters"><ol>{items}</ol></nav>'


def body() -> str:
    return f"""
<section class="hero">
<p class="kicker">F3 Explorer v0.2: a story in four steps</p>
<h1>The standard world turns down. Then we add the heat and the AI race.</h1>
<p class="lead" id="hero_line">Four short steps, each with one chart and one control. Nothing here is a forecast.</p>
<p class="cta"><a class="btn primary" href="#ch1">Start the story</a> <a class="btn" href="explorer.html">Skip to the Explorer</a></p>
</section>
<div class="banner" role="note"><strong class="big">{PUBLIC}</strong>Every curve is the output of a model run under stated assumptions. None is a prediction, none has a likelihood. Recorded test failures are shown next to the charts they affect and on the <a href="limitations.html">Limitations</a> page.</div>
{steps_nav()}

<section class="chapter card" id="ch1" aria-labelledby="ch1_h">
<p class="kicker">Step 1 of 4: the standard world</p>
<h2 id="ch1_h" class="finding">The standard world turns down</h2>
<p class="why">{W3} is the model behind <em>The Limits to Growth</em>. This is its standard run, 1900 to 2100, with the 2004 parameter set. Change one thing and see what moves.</p>
<div class="ctlrow"><span class="ctllab" id="c1_lab">Starting non-renewable resources</span><div class="seg" id="c1_seg" role="group" aria-labelledby="c1_lab"></div></div>
<div id="ch_s1"></div>
<p class="note histline"><span id="ch1_hist"></span> <a href="explorer.html#tab=history">Compare with history: Model versus reality</a></p>
<p class="status"><a class="badge amber" href="limitations.html#status-world3"><span aria-hidden="true">&#9650;</span> Amber: the standard run matches its reference; test A3.4(b) failed; changed runs are not compared</a></p>
<p class="next"><a href="#ch2">Next: add the heat</a></p>
</section>

<section class="chapter card" id="ch2" aria-labelledby="ch2_h">
<p class="kicker">Step 2 of 4: add the heat</p>
<h2 id="ch2_h" class="finding">Adding the heat lowers industrial output</h2>
<p class="why">The {FAIR} climate run warms the same way in every scenario here (emissions are prescribed). Switch the climate-damage option on and World3's industrial output is cut by a share that grows with warming squared.</p>
<div class="ctlrow"><span class="ctllab" id="c2_lab">Climate damage to industrial output</span><div class="seg" id="c2_seg" role="group" aria-labelledby="c2_lab"></div></div>
<div id="ch_stripes">{ig.STRIPES}</div>
<div id="ch_s2"></div>
<div class="notice damage" id="c2_notice" role="note" aria-live="polite"></div>
<p class="note">Stripes: FaIR mean, not observed; test A2.1 failed (FaIR starts about 0.04 to 0.07 K below observed). The three damage options are level-of-output effects; <strong>high is not the upper end of the literature</strong>. See <a href="limitations.html#status-climate">Limitations</a>.</p>
<p class="status"><a class="badge amber" href="limitations.html#status-climate"><span aria-hidden="true">&#9650;</span> Amber: test A2.1 failed by 0.037 K; damage-on runs are not compared with WorldDynamics.jl</a></p>
<p class="next"><a href="#ch3">Next: the AI race</a></p>
</section>

<section class="chapter card" id="ch3" aria-labelledby="ch3_h">
<p class="kicker">Step 3 of 4: the AI race</p>
<h2 id="ch3_h" class="finding">The AI race automates tasks within years</h2>
<p class="why">S3, this project's AI-economy model, rebuilt from the equations of {GATE}. Only the <strong>timing of automation</strong> is shown. Levels are flagged red because they are unvalidated.</p>
<div class="ctlrow"><span class="ctllab" id="c3_lab">AI investment setting</span><div class="seg" id="c3_seg" role="group" aria-labelledby="c3_lab"></div></div>
<div id="ch_s3" class="redframe"></div>
<p class="note" id="c3_note"></p>
<p class="status"><a class="badge red" href="limitations.html#status-ai"><span aria-hidden="true">&#9632;</span> Red: S3 failed its test against GATE (A1.3); levels are unvalidated, read the shape only</a></p>
<div class="withheld" role="note">Compute and electricity outputs are withheld until the S3 compute path is validated (awaiting Epoch AI); they currently leave any plausible range.</div>
<p class="next"><a href="#ch4">Next: what is connected</a></p>
</section>

<section class="chapter card" id="ch4" aria-labelledby="ch4_h">
<p class="kicker">Step 4 of 4: what is connected</p>
<h2 id="ch4_h" class="finding">Few of the links between the models are built</h2>
<p class="why">Five pieces, seven possible links. Solid lines are built, dashed lines are not built. The compute and electricity values of link 5 stay withheld above. Nothing in the Explorer depends on a dashed link.</p>
<div class="ctlrow"><span class="ctllab" id="c4_lab">Show links</span><div class="seg" id="c4_seg" role="group" aria-labelledby="c4_lab"></div></div>
<ol class="nodes" aria-label="The five pieces">{"".join(f'<li class="node {n["status"]}"><strong>{n["label"]}</strong><span>{n["sub"]}</span></li>' for n in links.NODES)}</ol>
<ol class="linkstrip" id="c4_list"></ol>
<script type="application/json" id="linksdata">{links.links_json()}</script>
<p class="next"><a href="connections.html">Open the connections map</a></p>
</section>

<section class="card" id="readfirst" aria-labelledby="rf_h">
<h2 id="rf_h">Read this first</h2>
<ul class="rfl">
<li class="rf"><strong>Scenarios, not forecasts.</strong> Each curve is one model run under stated assumptions. It has no probability and says nothing about what will happen.</li>
<li class="rf"><strong>Only one link between the pieces is built:</strong> warming lowers World3 industrial output, through a damage function, switched off by default. The AI model and World3 are two models of the same world and are not connected or reconciled.</li>
<li class="rf"><strong>Check the status badges.</strong> The climate run missed its test against observations by a small margin, the AI model's levels are unvalidated, and World3 was compared with its reference only for the standard run. Compute and electricity outputs are withheld.</li>
</ul>
<p class="cta"><a class="btn primary" href="explorer.html">Open the Explorer</a> <a class="btn" href="limitations.html">Read the Limitations</a></p>
</section>
<noscript><div class="notice">The charts on this page are drawn by JavaScript from the precomputed data in <code>data/explorer.js</code>. Without JavaScript only the text is shown.</div></noscript>
"""
