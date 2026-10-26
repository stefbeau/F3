"""Inline SVG infographics for the Explorer (D-052, restyled to the v0.2 tokens in D-056). Static markup; the stripes are filled in by the page script from the data.

Honesty rule: a link is drawn SOLID only if the coupling is built and tested today (data-built="yes"): climate warming to World3 industrial output
(M6, default off) and climate warming to the AI model's output (the M2 slice). Everything not built is DASHED and says so (data-built="no").
A link that is built in the AI-race slice but whose outputs are withheld is DOTTED (data-built="withheld"). The same vocabulary, numbers, colours and
dash patterns as the connections map (links.py, style.css): colours come from CSS variables, so both themes work; no colour carries meaning alone.

The viewBox is 310 wide, narrower than the inside of a card on a 375 px phone (about 313 px), so the drawing only ever scales up and text set at 13 renders at 13 px
or more; diagrams are capped at 520 px. The link paths put `class` before `data-link` on purpose: the map's own markup (connections_body.py) is the one that
tests/test_site_connections.py counts, and these two diagrams complement the map, they do not replace it.
"""

# one arrowhead per status, drawn with the same classes as the map's markers (.mk.built, .mk.not-built, .mk.withheld in style.css)
STATUS = {"built": ("yes", ""), "not-built": ("no", ' stroke-dasharray="7 5"'), "withheld": ("withheld", ' stroke-dasharray="1 6" stroke-linecap="round"')}


def markers(prefix: str) -> str:
    return "<defs>" + "".join(
        f'<marker id="{prefix}_{s}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="mk {s}"/></marker>'
        for s in STATUS) + "</defs>"


def num(x, y, n):
    return f'<circle cx="{x}" cy="{y}" r="10" class="numdot"/><text x="{x}" y="{y + 4.5}" text-anchor="middle" font-size="13" font-weight="700" class="numtxt">{n}</text>'


def box(x, y, w, h, lines, cls="nodebox"):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" class="{cls}"/>'
    n = len(lines)
    for i, t in enumerate(lines):
        ty = y + h / 2 + (i - (n - 1) / 2) * 16 + 4.5
        out += f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" font-size="13" class="svgt{" b" if i == 0 else ""}">{t}</text>'
    return out


def link(prefix: str, ident: str, status: str, d: str) -> str:
    built, dash = STATUS[status]
    return f'<path class="ln {status}" data-link="{ident}" data-built="{built}" d="{d}"{dash} marker-end="url(#{prefix}_{status})"/>'


LOOPS = (
    '<svg id="ig_loops" viewBox="0 0 310 464" role="img" aria-labelledby="ig_loops_t ig_loops_d" class="ig">'
    '<title id="ig_loops_t">Feedback loops: which links exist today and which are not built</title>'
    '<desc id="ig_loops_d">Boxes: warming from the climate model, World3, the AI model S3, data-centre electricity, and emissions. Solid arrows are links that are built and '
    'tested: warming lowers World3 industrial output (optional, off by default), and warming lowers S3 output. Dashed arrows are links that are not built: warming '
    'effects on health and yield in World3, S3 output feeding World3, data-centre electricity feeding emissions, and World3 feeding emissions. The arrow '
    'S3 compute to data-centre electricity, is built, but its outputs are withheld in the Explorer.</desc>'
    + markers("lp")
    + box(75, 8, 160, 46, ["Warming", "climate model (FaIR)"])
    + box(0, 150, 140, 60, ["World3", "population,", "food, industry"])
    + box(170, 150, 140, 60, ["S3 (AI race)", "economy,", "automation"])
    + box(170, 290, 140, 60, ["Data-centre", "electricity", "(output withheld)"], "nodebox withheldbox")
    + box(65, 410, 180, 46, ["Emissions", "prescribed, not modelled"], "nodebox notbuilt")
    # built (solid)
    + link("lp", "fair-warming-to-world3-output", "built", "M 105 54 L 70 148") + num(67, 98, 1)
    + link("lp", "fair-warming-to-s3-damage", "built", "M 205 54 L 240 148") + num(242, 98, 2)
    # not built (dashed)
    + link("lp", "fair-warming-to-world3-health-yield", "not-built", "M 130 54 L 110 148") + num(139, 100, 3)
    + link("lp", "s3-output-to-world3", "not-built", "M 168 180 L 142 180") + num(155, 163, 4)
    + link("lp", "data-centre-electricity-to-emissions", "not-built", "M 230 352 L 190 408") + num(238, 380, 6)
    + link("lp", "world3-to-emissions", "not-built", "M 50 212 L 95 408") + num(50, 300, 7)
    # built (solid); values withheld in the Explorer
    + link("lp", "s3-compute-to-data-centre-electricity", "built", "M 240 212 L 240 288") + num(260, 250, 5)
    + '</svg>'
)

LOOPS_KEY = (
    '<ol class="igkey">'
    '<li><strong>Built, solid:</strong> warming lowers World3 industrial output through the D-007 damage function. A level-of-output effect, <strong>off by default</strong>; set it with the climate-damage control on the <a href="explorer.html">Explorer</a>.</li>'
    '<li><strong>Built, solid:</strong> warming lowers the AI model\'s (S3) own output through the same damage function (the AI-race charts under Details on the Explorer).</li>'
    '<li><strong>Not built, dashed:</strong> any effect of warming on World3 health or yield. There is no health or yield effect of warming; the Earth4All channels were left out by decision (D-049).</li>'
    '<li><strong>Not built, dashed:</strong> the AI model feeding World3. S3\'s economy and World3\'s are two models of the same world and are not reconciled.</li>'
    '<li><strong>Built, solid (values withheld):</strong> S3 compute sets data-centre electricity demand and supply limits compute. The values are withheld until S3\'s compute path is validated.</li>'
    '<li><strong>Not built, dashed:</strong> data-centre electricity feeding emissions.</li>'
    '<li><strong>Not built, dashed:</strong> World3 feeding emissions. Emissions are prescribed, so the climate path is the same for every scenario in the Explorer.</li>'
    '</ol>'
)

ROADMAP = (
    '<svg id="ig_roadmap" viewBox="0 0 310 316" role="img" aria-labelledby="ig_roadmap_t ig_roadmap_d" class="ig">'
    '<title id="ig_roadmap_t">What is connected: World3, climate and the AI model</title>'
    '<desc id="ig_roadmap_d">Three pieces: climate (FaIR), World3 and the AI model S3. Solid arrows: climate warming to World3 industrial output (the first coupling, off by default) '
    'and climate warming to S3 output. Dashed arrows are not built: S3 and World3 exchanging values, and an emissions feedback that would let the economy change the climate.</desc>'
    + markers("rm")
    + box(75, 8, 160, 46, ["Climate", "FaIR, 841 members"])
    + box(0, 150, 140, 46, ["World3", "1900 to 2100"])
    + box(170, 150, 140, 46, ["S3 (AI race)", "levels unvalidated"])
    + box(65, 262, 180, 46, ["Emissions feedback", "not built"], "nodebox notbuilt")
    + link("rm", "fair-warming-to-world3-output", "built", "M 105 54 L 70 148")
    + link("rm", "fair-warming-to-s3-damage", "built", "M 205 54 L 240 148")
    + link("rm", "s3-and-world3-exchange", "not-built", "M 168 173 L 142 173")
    + link("rm", "world3-to-emissions-feedback", "not-built", "M 60 198 L 105 260")
    + link("rm", "s3-to-emissions-feedback", "not-built", "M 250 198 L 205 260")
    + '<text x="100" y="118" font-size="13" class="svgt b">first coupling</text>'
    + '</svg>'
)

ROADMAP_KEY = (
    '<ul class="igkey"><li><strong>Solid:</strong> built and tested. The first coupling is climate damage to World3 industrial output (default off); the warming-to-S3 link is the AI-race run\'s damage option.</li>'
    '<li><strong>Dashed:</strong> not built. Nothing here claims that the AI model changes World3 or that either changes the climate.</li></ul>'
)

STRIPES = (
    '<svg id="ig_stripes" viewBox="0 0 320 132" role="img" aria-labelledby="ig_stripes_t ig_stripes_d" class="ig">'
    '<title id="ig_stripes_t">Warming stripes of the FaIR ensemble mean, 2025 to 2100</title>'
    '<desc id="ig_stripes_d">One stripe per year from 2025 to 2100, coloured from the lowest to the highest ensemble-mean warming in that period (blue to red). '
    'This is a model run with prescribed emissions, not observed data. FaIR failed test A2.1: it starts about 0.04 to 0.07 K below observed.</desc>'
    '<g id="stripes_g"></g>'
    '<text id="stripes_l" x="0" y="106" font-size="13" class="svgt">2025</text>'
    '<text id="stripes_r" x="320" y="106" font-size="13" text-anchor="end" class="svgt">2100</text>'
    '<text x="0" y="126" font-size="13" class="svgt b">FaIR mean, not observed; test A2.1 failed</text>'
    '</svg>'
)
STRIPES_CAP = ('<p class="note">One stripe per year, 2025 to 2100, coloured by the FaIR ensemble mean (blue is the lowest mean in the period, red the highest). The colour scale is relative to this '
               'run, not to observations. <strong>Test A2.1 failed</strong>: FaIR starts about 0.04 to 0.07 K below observed for the current decade, and emissions are prescribed. '
               'See <a href="limitations.html#status-climate">Limitations</a>.</p>')
