"""Markup of the Connections page (connections.html), D-056 stage 5: the map as an interface. Nodes are absolutely positioned boxes, the seven links are SVG curves with
numbered buttons; clicking a button (or a link) opens the inspector. Below 900 px the map collapses to a list of the same links with the same inspector.
The map, the buttons and the list are generated here from links.py, so the solid/dashed/dotted vocabulary cannot drift from the records. Effect numbers are written by connections.js from the data."""
import html as _h

import ig
import index_body
import links

PUBLIC = index_body.PUBLIC
DASH = {"built": "", "not-built": ' stroke-dasharray="7 5"', "withheld": ' stroke-dasharray="1 6" stroke-linecap="round"'}
BUILT_ATTR = {"built": "yes", "not-built": "no", "withheld": "withheld"}
NODE = {n["id"]: n for n in links.NODES}
W, H = links.MAP_W, links.MAP_H


def pct(v: float, total: int) -> str:
    return f"{v / total * 100:.3f}%"


def mid(c: list) -> tuple:
    (x0, y0), (cx, cy), (x1, y1) = c
    return (0.25 * x0 + 0.5 * cx + 0.25 * x1, 0.25 * y0 + 0.5 * cy + 0.25 * y1)


def label_of(link: dict) -> str:
    return f'{NODE[link["from"]]["label"]} to {NODE[link["to"]]["label"]}'


def map_html() -> str:
    paths = ""
    for l in links.LINKS:
        (x0, y0), (cx, cy), (x1, y1) = links.CURVES[l["n"]]
        d = f"M {x0} {y0} Q {cx} {cy} {x1} {y1}"
        paths += (f'<path data-link="{l["id"]}" data-built="{BUILT_ATTR[l["status"]]}" data-n="{l["n"]}" d="{d}" class="ln {l["status"]}"{DASH[l["status"]]} marker-end="url(#mk_{l["status"]})"/>'
                  f'<path class="hit" data-hit="{l["n"]}" d="{d}"/>')
    markers = "".join(f'<marker id="mk_{s}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="mk {s}"/></marker>' for s in ("built", "not-built", "withheld"))
    svg = (f'<svg class="mapsvg" viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false"><defs>{markers}</defs>{paths}</svg>')
    nodes = ""
    for n in links.NODES:
        x, y, w, h = n["box"]
        nodes += (f'<div class="mnode {n["status"]}" style="left:{pct(x, W)};top:{pct(y, H)};width:{pct(w, W)};height:{pct(h, H)}"><strong>{_h.escape(n["label"])}</strong><span>{_h.escape(n["sub"])}</span></div>')
    btns = ""
    for l in links.LINKS:
        mx, my = mid(links.CURVES[l["n"]])
        aria = f'Link {l["n"]}: {label_of(l)}. {links.STATUS_TEXT[l["status"]]}.'
        btns += (f'<button type="button" class="nbtn {l["status"]}" data-n="{l["n"]}" style="left:{pct(mx, W)};top:{pct(my, H)}" aria-label="{_h.escape(aria)}" aria-pressed="false">{l["n"]}</button>')
    return f'<div class="map" id="map" role="group" aria-label="Map of the seven links between the models. Use Tab or the arrow keys to move between numbered links; Enter opens the inspector.">{svg}{nodes}{btns}</div>'


def list_html() -> str:
    items = ""
    for l in links.LINKS:
        samp = f'<svg viewBox="0 0 44 10" aria-hidden="true" class="samp {l["status"]}"><line x1="2" y1="5" x2="42" y2="5" stroke-width="3.4"{DASH[l["status"]]}/></svg>'
        items += (f'<li class="li {l["status"]}" data-n="{l["n"]}"><button type="button" class="lbtn" data-n="{l["n"]}" aria-expanded="false" aria-controls="insp_l{l["n"]}">{samp}'
                  f'<span><strong>{l["n"]}. {_h.escape(label_of(l))}</strong><br>{_h.escape(l["label"])}. <em>{links.STATUS_TEXT[l["status"]]}.</em></span></button>'
                  f'<div class="inspl" id="insp_l{l["n"]}" hidden></div><p class="what">{_h.escape(l["what"])}</p></li>')
    return f'<ol class="linklist" id="linklist" aria-label="The seven links">{items}</ol>'


LEGEND = ('<ul class="maplegend" aria-label="Line styles">'
          '<li><svg viewBox="0 0 44 10" aria-hidden="true" class="samp built"><line x1="2" y1="5" x2="42" y2="5" stroke-width="3.4"/></svg> Solid: built and tested</li>'
          '<li><svg viewBox="0 0 44 10" aria-hidden="true" class="samp withheld"><line x1="2" y1="5" x2="42" y2="5" stroke-width="3.4" stroke-dasharray="1 6" stroke-linecap="round"/></svg> Dotted: built, outputs withheld</li>'
          '<li><svg viewBox="0 0 44 10" aria-hidden="true" class="samp not-built"><line x1="2" y1="5" x2="42" y2="5" stroke-width="3.4" stroke-dasharray="7 5"/></svg> Dashed: not built</li></ul>')


def body() -> str:
    return f"""
<div class="banner compact" role="note"><strong class="big">{PUBLIC}</strong>Every curve is the output of a model run under stated assumptions. None is a prediction, none has a likelihood. See <a href="limitations.html">Limitations</a>.</div>
<h1 class="headline" id="headline">What is connected</h1>
<p class="lead">Five pieces, seven numbered links. Select a link to see what it does, the effect numbers computed from the data, and which tests it met, failed or was not compared with. Nothing in the Explorer depends on a dashed link.</p>
{LEGEND}
<div class="conn">
<div class="mapwrap">{map_html()}</div>
<section class="inspector card" id="inspector" aria-labelledby="insp_h" aria-live="polite" tabindex="-1"><h2 id="insp_h">Inspector</h2><div id="insp_body"><p class="note">Select a numbered link on the map.</p></div></section>
</div>
{list_html()}
<script type="application/json" id="linksdata">{links.links_json()}</script>
<noscript><div class="notice">The inspector needs JavaScript. Without it, the list above gives each link, its status and what it does.</div></noscript>
<section class="card" id="loop"><h2>The same links as a feedback loop</h2>
<p class="note">A fixed picture of the seven links, numbered as on the map above, with the same line styles. It complements the interactive map: it shows which links close a loop and which do not exist.</p>
{LEGEND}
{ig.LOOPS}
{ig.LOOPS_KEY}
</section>
<section class="card" id="notbuilt"><h2>Why most links are not built</h2>
<ul>
<li><strong>Emissions are prescribed.</strong> The FaIR run replays one recorded emissions path (D-021); neither World3 nor the AI model changes it. The climate is the same in every scenario.</li>
<li><strong>S3's economy and World3's are not reconciled.</strong> They are two models of the same world; connecting them is future work, not something the Explorer shows.</li>
<li><strong>Warming has no health or yield effect.</strong> The Earth4All channels were left out by decision (D-049), to be revisited.</li>
<li>S3 compute and data-centre electricity outputs are withheld until the S3 compute path is validated (awaiting Epoch AI).</li>
</ul></section>
"""
