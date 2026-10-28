"""Markup of the AI Impact page (ai.html). Four sections: three stat tiles, publications by year, publications by country, proposed links.
The charts are inline SVG written here from the numbers in ai_data.py (no chart library); ai.js only adds the draw-in, the fade-in and the hover tooltip.
Colours come from the stylesheet tokens (class names, not fixed colours), so both themes work. Nothing here is a forecast or a causal claim: the page shows counts."""
import html as _h

import index_body

PUBLIC = index_body.PUBLIC

# Proposed links, wording verbatim from docs/architecture.md (D-060 gap analysis): (code, name, proposed link). None is built.
PROPOSED = [
    ("L8", "Disaster-economy", "extreme weather event damage to GDP and food loss"),
    ("L9", "Climate-migration-labour", "displacement to labour supply and skill mix"),
    ("L_MH", "Mental health", "AI displacement and climate stress to productivity"),
    ("L_CONF", "Conflict", "resource and climate stress to armed conflict to the economy"),
    ("L_RISK", "AI safety", "incident rate and capability to catastrophic risk probability"),
]

W, H, L, R, T, B = 720, 340, 62, 24, 28, 44


def fmt_m(v: float) -> str:
    return f"{v / 1e6:.1f} M"


def axis_m(v: float) -> str:
    return "0" if v == 0 else f"{v / 1e6:g} M"


def tile(key: str, value: str, sub: str) -> str:
    return f'<div class="tile"><span class="tk_k">{_h.escape(key)}</span><strong class="tk_v">{_h.escape(value)}</strong><span class="tk_s">{_h.escape(sub)}</span></div>'


def tiles(s: dict) -> str:
    return ('<div class="tiles ai-tiles" aria-label="AI data in the repository">'
            + tile("Notable AI models (Epoch AI)", f'{s["epoch_models"]:,}', f'{s["epoch_year_min"]}–{s["epoch_year_max"]}')
            + tile("AI publications (OpenAlex)", fmt_m(s["oa_total"]), f'{s["oa_year_min"]}–{s["oa_year_max"]}')
            + tile("FDA AI-enabled medical devices", f'{s["fda_devices"]:,}', f'list current as of {s["fda_as_of"]}')
            + "</div>")


def missing(what: str) -> str:
    return f'<div class="notice" role="note">{what} was not found when this page was built, so its chart is left out. It is rebuilt from the raw OpenAlex files by <code>site_src/data_campaign.py</code>.</div>'


def year_chart(rows: list) -> str:
    if not rows:
        return missing("The OpenAlex by-year extract")
    x0, x1 = rows[0]["year"], rows[-1]["year"]
    top = max(r["count"] for r in rows)
    step = 0.5e6 if top <= 3e6 else 1e6
    ymax = -(-top // step) * step
    X = lambda y: L + (y - x0) / (x1 - x0) * (W - L - R)          # noqa: E731
    Y = lambda v: T + (1 - v / ymax) * (H - T - B)                 # noqa: E731
    pts = [(X(r["year"]), Y(r["count"])) for r in rows]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{pts[0][0]:.1f},{Y(0):.1f} " + line + f" {pts[-1][0]:.1f},{Y(0):.1f}"
    g = ""
    n = int(round(ymax / step))
    for k in range(n + 1):
        v = k * step
        g += f'<line class="ai-grid" x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text class="ai-tick" x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{axis_m(v)}</text>'
    for y in range(x0, x1 + 1, 5):
        g += f'<text class="ai-tick" x="{X(y):.1f}" y="{H - B + 22}" text-anchor="middle">{y}</text>'
    ann = ""
    if x0 <= 2022 <= x1:
        ax = X(2022)
        ann = (f'<line class="ai-rule" x1="{ax:.1f}" x2="{ax:.1f}" y1="{T}" y2="{Y(0):.1f}"/>'
               f'<text class="ai-note-t" x="{ax - 7:.1f}" y="{T + 12}" text-anchor="end">ChatGPT released, Nov 2022</text>')
    dots = "".join(f'<circle class="ai-dot" cx="{x:.1f}" cy="{y:.1f}" r="4.5" data-year="{r["year"]}" data-count="{r["count"]}"><title>{r["year"]}: {r["count"]:,}</title></circle>'
                   for (x, y), r in zip(pts, rows))
    alt = f'Line chart: publications tagged Artificial intelligence in OpenAlex by year, {x0} to {x1}, from {rows[0]["count"]:,} to {rows[-1]["count"]:,}. The same numbers are in the data table below.'
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{_h.escape(alt)}" focusable="false">{g}'
           f'<polygon class="ai-area" points="{area}"/><polyline class="ai-line" data-animate="line" pathLength="1" points="{line}"/>{ann}{dots}'
           f'<text class="ai-tick" x="{L}" y="{T - 10}">Publications per year</text></svg>')
    trs = "".join(f'<tr><th scope="row">{r["year"]}</th><td>{r["count"]:,}</td></tr>' for r in rows)
    table = f'<details class="ai-table"><summary>Data table</summary><table><tr><th scope="col">Year</th><th scope="col">Publications</th></tr>{trs}</table></details>'
    return f'<div class="ai-chart-wrap" data-chart="years">{svg}<div class="ai-tip" id="ai_tip" role="status" hidden></div></div>{table}'


def year_text(rows: list) -> str:
    if not rows:
        return ""
    a, z = rows[0], rows[-1]
    return (f'<p>Publications tagged with OpenAlex’s Artificial intelligence concept rose from {a["count"]:,} in {a["year"]} to {z["count"]:,} in {z["year"]}, '
            f'a factor of {z["count"] / a["count"]:.1f}. The count is of tagged works, not a share of all research, so it does not show whether AI’s share of research changed; '
            f'it also says nothing about why the count rose.</p>')


def country_chart(rows: list) -> str:
    if not rows:
        return missing("The OpenAlex by-country extract")
    rows = rows[:10]
    top = rows[0]["count"]
    bw, rh, lw, vw = 420, 30, 150, 90
    h = len(rows) * rh + 8
    out = ""
    for i, r in enumerate(rows):
        y = 4 + i * rh
        w = r["count"] / top * bw
        cls = "ai-bar first" if i == 0 else "ai-bar"
        out += (f'<text class="ai-tick" x="{lw - 10}" y="{y + 19}" text-anchor="end">{_h.escape(r["country"])}</text>'
                f'<rect class="{cls}" x="{lw}" y="{y + 4}" width="{w:.1f}" height="{rh - 10}" rx="2"/>'
                f'<text class="ai-tick" x="{lw + w + 8:.1f}" y="{y + 19}">{r["count"]:,}</text>')
    alt = "Bar chart: the ten countries with the most AI publications in OpenAlex, 2000 to 2024. " + "; ".join(f'{r["country"]} {r["count"]:,}' for r in rows) + "."
    svg = f'<svg viewBox="0 0 {lw + bw + vw} {h}" role="img" aria-label="{_h.escape(alt)}" focusable="false">{out}</svg>'
    return f'<div class="ai-chart-wrap" data-chart="countries">{svg}</div>'


def country_text(rows: list, total: int, groups: int) -> str:
    if len(rows) < 2 or not total:
        return ""
    a, b = rows[0], rows[1]
    return (f'<p>{_h.escape(a["country"])} ({a["count"]:,}) and {_h.escape(b["country"])} ({b["count"]:,}) have the two largest counts, equal to {a["count"] / total:.0%} and {b["count"] / total:.0%} '
            f'of the {fmt_m(total)} works. Countries are taken from the authors’ institutions, so a work with authors in several countries is counted in each of them; the by-country response was cut off at {groups} countries. '
            f'These are counts, not exact shares.</p>')


def links_box() -> str:
    items = "".join(f'<li><code>{c}</code> <strong>{_h.escape(n)}</strong>: {_h.escape(d)} <span class="proposed">(proposed, not implemented)</span></li>' for c, n, d in PROPOSED)
    return ('<aside class="ai-model-links" aria-labelledby="ai_links_h"><h3 id="ai_links_h">Proposed links in the F3 architecture</h3>'
            f'<ul>{items}</ul>'
            '<p class="note">Five of the ten links proposed in <code>docs/architecture.md</code> (D-060 gap analysis). Each is a proposal: none is built, tested or approved, and none appears on the '
            '<a href="connections.html">Connections</a> page, which shows the seven links of the current model.</p></aside>')


def body(ai_data: dict) -> str:
    s = ai_data["stats"]
    by_year, by_country = ai_data["by_year"], ai_data["by_country"]
    return f"""
<div class="banner compact" role="note"><strong class="big">{PUBLIC}</strong>Every curve in the Explorer is the output of a model run under stated assumptions. This page is different: it shows published counts, not model output, and no AI-sector model runs here. See <a href="limitations.html">Limitations</a>.</div>
<h1 class="headline" id="headline">AI in the data F3 has collected</h1>
<p class="lead">Counts from three open datasets in the repository, as retrieved on 2026-10-28. They describe the amount of AI activity that is recorded; they are not inputs to any model run shown in the Explorer.</p>
<section class="ai-section" id="ai_a" aria-label="Headline numbers">
{tiles(s)}
</section>
<section class="ai-section card" id="ai_b" aria-labelledby="ai_b_h">
<h2 id="ai_b_h">Research surge</h2>
{year_chart(by_year)}
{year_text(by_year)}
</section>
<section class="ai-section card" id="ai_c" aria-labelledby="ai_c_h">
<h2 id="ai_c_h">Who publishes</h2>
{country_chart(by_country)}
{country_text(by_country, s["oa_total"], ai_data.get("country_groups_returned", 0))}
</section>
<section class="ai-section" id="ai_d" aria-labelledby="ai_d_h">
<h2 id="ai_d_h">In the F3 model</h2>
<p>Nothing on this page feeds the Explorer. The AI-sector model (S3) is unvalidated against GATE after about 2027 (<a href="limitations.html#status-ai">Limitations</a>). Links that would connect AI to other parts of the model are only proposed so far:</p>
{links_box()}
</section>
<section class="card" id="ai_src" aria-labelledby="ai_src_h">
<h2 id="ai_src_h">Sources</h2>
<ul class="note">
<li>Publications: OpenAlex, concept Artificial intelligence (C154945302), publication years 2000–2024, retrieved 2026-10-28, CC0 1.0. Counts are of works OpenAlex tags with that concept.</li>
<li>Notable AI models: Epoch AI, Notable AI Models, 1,083 rows with publication dates 1950–2026, retrieved 2026-10-28, CC BY (credit: Epoch AI).</li>
<li>Medical devices: US FDA, AI-enabled medical devices list, 1,614 devices, content current as of 2026-09-04; US federal government work, public domain.</li>
<li>Versions, licences and checksums: <a href="sources.html">Sources</a> and <code>audit/data/sources-register.json</code>.</li>
</ul></section>
<noscript><div class="notice">Without JavaScript the charts are shown without animation or hover values; every number is in the data table and the labels.</div></noscript>
"""
