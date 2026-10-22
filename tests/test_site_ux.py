"""Explorer v0.1 (D-052). WRITTEN BEFORE the front end: the interface of the page's pure functions and the readings below were fixed first.

Interface (site_src/explorer.js, between the markers /*PURE-START*/ and /*PURE-END*/; plain functions, no DOM):
  human(v), peakOf(years, ys) -> [year, value], firstReach(years, ys, th) -> year | null,
  w3Takeaway(years, run, runOff, damage) -> {sentence, tiles:[{k, v}]}        (tiles: peak population and year, resources left 2100, pollution peak,
                                                                               plus the damage effect on 2100 population when damage != "off")
  climateTakeaway(years, mean, lo, hi) -> {sentence, tiles}                    (2100 mean, 5th and 95th percentile)
  aiTakeaway(years, frac, dmg) -> {sentence, tiles}                            (first year at 0.5, first year at 1.0, damage share 2100)
  damageNotice(damage) -> string ("" when off)
  encodeState(st) / decodeState(hash, nLevers) -> {levers:[...], damage, ai, aidmg}, invalid input falls back to the defaults
  csvOf(years, cols) -> text, PRESETS = [{name, levers}], each a grid point.

Readings: (1) every number in a takeaway is computed from the data it is given (a synthetic dataset with different peaks gives different numbers, and the real
numbers are absent); (2) the damage notice carries the three phrases the editor required, and is empty when damage is off; (3) every preset and every
grid point is in the data and the hash round-trips; (4) the 108-run grid agrees with stand-alone World3 where damage is off and obeys the sign and ordering of
the M6 tests where it is on; (5) no page says "local draft" or "not published"; (6) the infographics draw as built exactly the links that exist, with text
alternatives; (7) S7 is not shown. Nothing here relaxes any earlier test.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
JS = REPO / "site_src" / "explorer.js"
DATA = SITE / "data" / "explorer.json"
NODE = shutil.which("node")
PAGES = ["index.html", "explorer.html", "methods.html", "limitations.html", "sources.html", "about.html"]

need_data = pytest.mark.skipif(not DATA.exists(), reason="site/data/explorer.json not present (build the site first)")
need_node = pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH")


def data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def pure_js() -> str:
    src = JS.read_text(encoding="utf-8")
    return src[src.index("/*PURE-START*/"):src.index("/*PURE-END*/")]


def node(expr: str, tmp_path: Path, payload: dict = None) -> str:
    prog = (pure_js() + ";const IN=" + json.dumps(payload or {}) + ";\n" + "process.stdout.write(JSON.stringify((function(){" + expr + "})()));")
    f = tmp_path / "t.js"
    f.write_text(prog, encoding="utf-8")
    return subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout


def w3(d, key):
    return d["world3"]["runs"][key]


# ------------------------------------------------------------------------------------------------------ (5) stale text
@pytest.mark.parametrize("page", PAGES)
def test_no_stale_publication_text_and_new_text_present(page):
    html = (SITE / page).read_text(encoding="utf-8")
    low = html.lower()
    for stale in ("local draft", "not published", "has not approved", "not been approved for publication", "editor has not approved"):
        assert stale not in low, (page, stale)
    assert "Public draft, published 2026-10-21. Conditional scenarios, not forecasts." in html, page


def test_about_names_the_commit_that_contains_the_built_pages():
    html = (SITE / "about.html").read_text(encoding="utf-8")
    assert re.search(r"<code>[0-9a-f]{7,40}</code>", html) and "contains the built pages" in html


# ------------------------------------------------------------------------------------------------------ (4) the data grid
@need_data
def test_grid_has_27_lever_runs_times_4_damage_states():
    d = data()
    runs = d["world3"]["runs"]
    assert len(runs) == 108
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for dm in ("off", "low", "central", "high"):
                    assert f"{i}|{j}|{k}|{dm}" in runs
    assert d["world3"]["standard"] + "|off" in runs and d["world3"]["damage"]["default"] == "off"


@need_data
def test_damage_off_runs_equal_stand_alone_world3():
    import numpy as np
    from f3.sectors.world3 import run_world3
    d = data()
    states, res = run_world3("2004")
    idx = [i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9]
    pop = sum(states[n] for n in ("p1", "p2", "p3", "p4"))[idx]
    run = w3(d, d["world3"]["standard"] + "|off")
    assert np.max(np.abs(np.array(run["pop"]) - pop) / pop) < 1e-5                  # the file keeps 6 significant digits
    assert np.max(np.abs(np.array(run["ic"]) - states["ic"][idx]) / states["ic"][idx]) < 1e-5


@need_data
def test_damage_on_lowers_industrial_output_in_order_and_is_flat_before_2025():
    d = data()
    yrs = d["world3"]["years"]
    k25, k2100 = yrs.index(2025), yrs.index(2100)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                base = f"{i}|{j}|{k}|"
                io = {dm: w3(d, base + dm)["io"] for dm in ("off", "low", "central", "high")}
                assert io["off"][k2100] > io["low"][k2100] > io["central"][k2100] > io["high"][k2100], base
                for dm in ("low", "central", "high"):
                    assert io[dm][:k25 + 1] == io["off"][:k25 + 1], (base, dm)         # multiplier 1 before 2025 (D-020)


@need_data
def test_the_sign_check_can_fail_control():
    """Control: comparing a run with itself must not satisfy the strict ordering the previous test asserts."""
    d = data()
    r = w3(d, d["world3"]["standard"] + "|central")["io"][-1]
    assert not (r > r)


@need_data
def test_all_grid_series_finite_and_nonnegative():
    import math
    for key, run in data()["world3"]["runs"].items():
        for n, ys in run.items():
            assert all(math.isfinite(v) and v >= 0 for v in ys), (key, n)


# ------------------------------------------------------------------------------------------------------ (1) takeaways from the data
@need_data
@need_node
def test_w3_takeaway_numbers_come_from_the_data(tmp_path):
    d = data()
    std = d["world3"]["standard"]
    run, off = w3(d, std + "|central"), w3(d, std + "|off")
    out = json.loads(node("return w3Takeaway(IN.years, IN.run, IN.off, 'central')", tmp_path, {"years": d["world3"]["years"], "run": run, "off": off}))
    yrs = d["world3"]["years"]
    pk = max(range(len(run["pop"])), key=lambda i: run["pop"][i])
    text = out["sentence"] + " " + " ".join(t["k"] + " " + t["v"] for t in out["tiles"])
    assert str(yrs[pk]) in text
    assert len(out["tiles"]) == 4                                                       # damage on: peak population, resources 2100, pollution peak, damage effect
    effect = (run["pop"][-1] / off["pop"][-1] - 1) * 100
    assert f"{effect:.1f}" in text or f"{abs(effect):.1f}" in text
    out_off = json.loads(node("return w3Takeaway(IN.years, IN.run, IN.off, 'off')", tmp_path, {"years": yrs, "run": off, "off": off}))
    assert len(out_off["tiles"]) == 3


@need_node
def test_takeaways_change_when_the_data_change_and_hold_no_typed_numbers(tmp_path):
    years = list(range(1900, 2101))
    n = len(years)

    def run(peak_year, peak, end, nr_end, pp_peak):
        pop = [peak * (1 - abs(y - peak_year) / 400.0) if y != 2100 else end for y in years]
        return {"pop": pop, "io": [1.0] * n, "ic": [1.0] * n, "al": [1.0] * n, "nrfr": [1 - (1 - nr_end) * (y - 1900) / 200 for y in years],
                "ppolx": [pp_peak * (1 - abs(y - 2013) / 300.0) for y in years]}

    a = run(1981, 9.1e9, 3.3e9, 0.31, 7.7)
    b = run(2047, 4.4e9, 1.1e9, 0.62, 2.2)
    sa = json.loads(node("return w3Takeaway(IN.years, IN.a, IN.a, 'off')", tmp_path, {"years": years, "a": a}))
    sb = json.loads(node("return w3Takeaway(IN.years, IN.b, IN.b, 'off')", tmp_path, {"years": years, "b": b}))
    ta = sa["sentence"] + " ".join(t["v"] for t in sa["tiles"])
    tb = sb["sentence"] + " ".join(t["v"] for t in sb["tiles"])
    assert "1981" in ta and "2047" in tb and ta != tb
    assert "9.1" in ta and "4.4" in tb and "0.31" in ta and "0.62" in tb and "7.7" in ta and "2.2" in tb
    assert "2047" not in ta and "1981" not in tb
    # no typed data: the committed run's peak year and value are not constants of the page script
    if DATA.exists():
        d = data()
        r = w3(d, d["world3"]["standard"] + "|off")
        pk = max(range(len(r["pop"])), key=lambda i: r["pop"][i])
        src = JS.read_text(encoding="utf-8")
        assert not re.search(rf"\b{d['world3']['years'][pk]}\b[^\n]*peak", pure_js())
        assert f"{r['pop'][pk]:.6g}" not in src


@need_data
@need_node
def test_climate_and_ai_takeaways(tmp_path):
    d = data()
    c = d["climate"]
    out = json.loads(node("return climateTakeaway(IN.years, IN.m, IN.lo, IN.hi)", tmp_path, {"years": d["years"], "m": c["warming"], "lo": c["warming_p05"], "hi": c["warming_p95"]}))
    text = out["sentence"] + " ".join(t["v"] for t in out["tiles"])
    assert f"{c['warming'][-1]:.2f}" in text and f"{c['warming_p05'][-1]:.2f}" in text and f"{c['warming_p95'][-1]:.2f}" in text
    r = d["runs"]["central|central|1"]
    out = json.loads(node("return aiTakeaway(IN.years, IN.f, IN.dm)", tmp_path, {"years": d["years"], "f": r["frac_automated"], "dm": r["damage_fraction"]}))
    y05 = next(d["years"][i] for i, v in enumerate(r["frac_automated"]) if v >= 0.5)
    y10 = next(d["years"][i] for i, v in enumerate(r["frac_automated"]) if v >= 0.999)
    text = out["sentence"] + " ".join(t["v"] for t in out["tiles"])
    assert str(y05) in text and str(y10) in text and f"{r['damage_fraction'][-1] * 100:.1f}" in text
    assert len(out["tiles"]) == 3
    # not reached inside the horizon is said, not invented
    never = json.loads(node("return aiTakeaway(IN.years, IN.f, IN.dm)", tmp_path, {"years": d["years"], "f": [0.1] * len(d["years"]), "dm": [0.0] * len(d["years"])}))
    assert "not" in (never["sentence"] + " ".join(t["v"] for t in never["tiles"])).lower()


# ------------------------------------------------------------------------------------------------------ (2) labels when damage is on
@need_node
def test_damage_notice_carries_the_required_phrases(tmp_path):
    assert json.loads(node("return damageNotice('off')", tmp_path)) == ""
    for dm in ("low", "central", "high"):
        s = json.loads(node(f"return damageNotice('{dm}')", tmp_path)).lower()
        for phrase in ("level-of-output effect, not the upper end of the literature", "not compared with worlddynamics.jl", "it has no climate damage",
                       "s3's economy and world3's are not reconciled", "no health or yield effect of warming"):
            assert phrase in s, (dm, phrase)


def test_the_notice_is_a_visible_live_region_not_a_tooltip():
    html = (SITE / "explorer.html").read_text(encoding="utf-8")
    assert 'id="w3_damage_notice"' in html and 'aria-live="polite"' in html


# ------------------------------------------------------------------------------------------------------ (3) presets and hash
@need_data
@need_node
def test_presets_are_grid_points_and_hash_round_trips(tmp_path):
    d = data()
    presets = json.loads(node("return PRESETS", tmp_path))
    assert [p["name"] for p in presets] == ["Standard", "More resources", "Farming tech", "Pollution cut", "Combined"]
    for p in presets:
        assert "|".join(map(str, p["levers"])) + "|off" in d["world3"]["runs"], p
    assert "|".join(map(str, presets[0]["levers"])) == d["world3"]["standard"]
    cases = [{"levers": [i, j, k], "damage": dm, "ai": "race", "aidmg": "high"} for i in range(3) for j in range(3) for k in range(3) for dm in ("off", "low", "central", "high")]
    out = json.loads(node("return IN.c.map(s=>decodeState(encodeState(s),3))", tmp_path, {"c": cases}))
    assert out == cases


@need_node
def test_bad_hash_falls_back_to_defaults(tmp_path):
    for bad in ("", "#", "#w3=9.9.9&d=huge", "#w3=a.b.c", "garbage", "#w3=1.0&d=off", "#d=central&w3=1.0.0&ai=nope"):
        out = json.loads(node(f"return decodeState({json.dumps(bad)},3)", tmp_path))
        assert len(out["levers"]) == 3 and all(isinstance(v, int) and 0 <= v <= 2 for v in out["levers"]), bad
        assert out["damage"] in ("off", "low", "central", "high") and out["ai"] in ("low", "central", "race") and out["aidmg"] in ("low", "central", "high"), bad
    ok = json.loads(node("return decodeState('#w3=2.1.0&d=central',3)", tmp_path))
    assert ok["levers"] == [2, 1, 0] and ok["damage"] == "central"
    assert json.loads(node("return decodeState('#w3=9.9.9&d=huge',3)", tmp_path))["damage"] == "off"          # the default damage is OFF


# ------------------------------------------------------------------------------------------------------ chart download
@need_node
def test_csv_has_one_row_per_year_and_the_values(tmp_path):
    years = [2020, 2021, 2022]
    out = json.loads(node("return csvOf(IN.y, [{name:'a, b',y:[1,2.5,3]},{name:'c',y:[4,5,6]}])", tmp_path, {"y": years}))
    lines = out.strip().split("\n")
    assert lines[0] == 'year,"a, b",c' and lines[1] == "2020,1,4" and lines[3] == "2022,3,6" and len(lines) == 4


# ------------------------------------------------------------------------------------------------------ (6) infographics, (7) S7, structure
def index_html() -> str:
    """The v0.1 panels page. Since D-056 stage 2 it lives at explorer.html (index.html is the story); stage 3 replaces it with the dashboard."""
    return (SITE / "explorer.html").read_text(encoding="utf-8")


def svg_of(html: str, ident: str) -> str:
    m = re.search(rf'<svg[^>]*id="{ident}".*?</svg>', html, re.S)
    assert m, ident
    return m.group(0)


def test_loop_diagram_marks_only_links_that_exist_as_built():
    svg = svg_of(index_html(), "ig_loops")
    links = re.findall(r'<(?:path|line)[^>]*data-link="([^"]+)"[^>]*data-built="(yes|no)"', svg)
    built = {l for l, b in links if b == "yes"}
    assert built == {"fair-warming-to-world3-output", "fair-warming-to-s3-damage"}, built
    unbuilt = {l for l, b in links if b == "no"}
    assert unbuilt, "the diagram must show links that are not built, dashed"
    # every unbuilt link is drawn dashed, every built link solid (link ids contain no ">" so a tag can be matched up to its closing bracket)
    assert all(">" not in l for l, _ in links)
    for m in re.finditer(r'<(?:path|line)[^>]*>', svg):
        tag = m.group(0)
        if 'data-built="no"' in tag:
            assert "stroke-dasharray" in tag, tag
        if 'data-built="yes"' in tag:
            assert "stroke-dasharray" not in tag, tag


def test_roadmap_first_coupling_solid_others_dashed():
    svg = svg_of(index_html(), "ig_roadmap")
    tags = re.findall(r'<(?:path|line)[^>]*data-link="([^"]+)"[^>]*>', svg)
    assert "fair-warming-to-world3-output" in tags
    for m in re.finditer(r'<(?:path|line)[^>]*data-link="([^"]+)"[^>]*>', svg):
        solid = "stroke-dasharray" not in m.group(0)
        assert solid == (m.group(1) in ("fair-warming-to-world3-output", "fair-warming-to-s3-damage")), m.group(0)


def test_every_infographic_has_a_text_alternative_and_readable_text():
    html = index_html()
    for ident in ("ig_loops", "ig_roadmap", "ig_stripes"):
        svg = svg_of(html, ident)
        assert 'role="img"' in svg and re.search(r"<title[ >]", svg) and re.search(r"<desc[ >]", svg), ident
        for ref in re.search(r'aria-labelledby="([^"]+)"', svg).group(1).split():                 # the label must point at ids that exist in the drawing
            assert f'id="{ref}"' in svg, (ident, ref)
        sizes = [float(x) for x in re.findall(r'font-size="([0-9.]+)"', svg)]
        assert sizes and min(sizes) >= 13, (ident, min(sizes) if sizes else None)


def test_stripes_are_labelled_with_the_a21_failure():
    html = index_html()
    seg = html[html.index('id="ig_stripes"') - 600:html.index('id="ig_stripes"') + 4000]
    assert "A2.1" in seg and "failed" in seg.lower()


def test_status_badges_link_to_limitations_and_have_text():
    html = index_html()
    badges = re.findall(r'<a class="badge[^"]*" href="limitations\.html#([a-z0-9-]+)"[^>]*>(.*?)</a>', html, re.S)
    assert len(badges) == 3, badges
    for _, txt in badges:
        assert re.search(r"[A-Za-z]{4,}", re.sub(r"<[^>]+>", "", txt))
    lim = (SITE / "limitations.html").read_text(encoding="utf-8")
    for anchor, _ in badges:
        assert f'id="{anchor}"' in lim, anchor


def test_layout_elements_present():
    html = index_html()
    assert 'class="tabs"' in html and all(f'href="#{a}"' in html for a in ("p_w3", "p_climate", "p_ai"))
    assert 'id="readfirst"' in html and html.count('class="rf"') == 3
    for term in ("S3", "R3", "FaIR", "GATE", "World3"):
        assert re.search(rf'<abbr[^>]*title="[^"]{{20,}}"[^>]*>{term}</abbr>', html), term
    assert "Reset" in html and "Custom" in html
    for name in ("Standard", "More resources", "Farming tech", "Pollution cut", "Combined"):
        assert name in html or name in JS.read_text(encoding="utf-8")


def test_s7_is_not_shown_on_the_site():
    for page in PAGES:
        html = (SITE / page).read_text(encoding="utf-8")
        visible = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
        assert not re.search(r"\bS7\b|s7_social|social module|inequality index", visible), page


def test_methods_limitations_sources_describe_the_new_coupling_and_drop_the_old_claim():
    for page in ("methods.html", "limitations.html", "sources.html"):
        html = (SITE / page).read_text(encoding="utf-8")
        assert "climate damage" in html.lower(), page
        assert "The three panels are not coupled" not in html and "The panels are not coupled" not in html and "NOT yet coupled" not in html, page
    lim = (SITE / "limitations.html").read_text(encoding="utf-8").lower()
    for phrase in ("level-of-output", "worlddynamics.jl", "not reconciled", "no health or yield effect of warming"):
        assert phrase in lim, phrase
    assert "withheld" in index_html().lower()                                           # S3 compute and electricity stay withheld
    assert 'id="ch_compute"' not in index_html() and 'id="ch_edc"' not in index_html()


# ------------------------------------------------------------------------------------------------------ editor review 2026-10-21 (added after the change)
def test_page_order_and_tab_bar_order():
    html = index_html()
    pos = [html.index(m) for m in ('class="banner"', 'id="readfirst"', 'class="tabs"', 'id="p_w3"', 'id="p_climate"', 'id="p_ai"', 'id="connected"', 'id="notshown"')]
    assert pos == sorted(pos), pos
    assert html.index("<h1>") < pos[0]
    tabs = re.search(r'<nav class="tabs".*?</nav>', html, re.S).group(0)
    assert re.findall(r'href="#([a-z0-9_]+)"', tabs) == ["p_w3", "p_climate", "p_ai", "connected", "notshown"]
    for ident in ("ig_loops", "ig_roadmap", "ig_stripes"):                         # every diagram is still there
        assert f'id="{ident}"' in html


def test_industrial_output_unit_label_and_methods():
    assert 'o("Model dollars per year"' in JS.read_text(encoding="utf-8")
    assert "Dollars per year" not in JS.read_text(encoding="utf-8")
    m = (SITE / "methods.html").read_text(encoding="utf-8")
    assert "model dollars per year" in m.lower() and "constant dollars" in m
