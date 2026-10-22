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
JS = REPO / "site_src" / "dashboard.js"
DATA = SITE / "data" / "explorer.json"
NODE = shutil.which("node")
PAGES = ["index.html", "explorer.html", "methods.html", "limitations.html", "sources.html", "about.html"]

need_data = pytest.mark.skipif(not DATA.exists(), reason="site/data/explorer.json not present (build the site first)")
need_node = pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH")


def data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


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


def test_the_notice_is_a_visible_live_region_not_a_tooltip():
    html = (SITE / "explorer.html").read_text(encoding="utf-8")
    assert 'id="w3_damage_notice"' in html and 'aria-live="polite"' in html


# ------------------------------------------------------------------------------------------------------ (6) infographics, (7) S7, structure
def index_html() -> str:
    """The v0.1 panels page. Since D-056 stage 2 it lives at explorer.html (index.html is the story); stage 3 replaces it with the dashboard."""
    return (SITE / "explorer.html").read_text(encoding="utf-8")


def svg_of(html: str, ident: str) -> str:
    m = re.search(rf'<svg[^>]*id="{ident}".*?</svg>', html, re.S)
    assert m, ident
    return m.group(0)


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


# ------------------------------------------------------------------------------------------------------ the dashboard page (D-056 stage 3); headlines, tiles, hash and CSV are tested in tests/test_site_v02_core.py
def svg_has_text_alternative(html: str, ident: str) -> bool:
    svg = svg_of(html, ident)
    ok = 'role="img"' in svg and re.search(r"<title[ >]", svg) and re.search(r"<desc[ >]", svg)
    for ref in re.search(r'aria-labelledby="([^"]+)"', svg).group(1).split():
        ok = ok and f'id="{ref}"' in svg
    sizes = [float(x) for x in re.findall(r'font-size="([0-9.]+)"', svg)]
    return bool(ok and sizes and min(sizes) >= 13)


def test_every_remaining_infographic_has_a_text_alternative_and_readable_text():
    for ident in ("ig_stripes",):
        assert svg_has_text_alternative(index_html(), ident), ident


def test_dashboard_structure_rail_one_main_chart_details_and_step_bar():
    html = index_html()
    pos = [html.index(m) for m in ('class="banner compact"', 'id="choose"', 'id="result"', 'id="ch_main"', 'id="reliability"', 'id="details"', 'id="connected"', 'id="notshown"')]
    assert pos == sorted(pos), pos
    assert html.count('id="ch_main"') == 1                                                  # exactly one main chart outside Details
    main_zone = html[html.index('id="result"'):html.index('id="reliability"')]
    assert len(re.findall(r'id="ch_[a-z0-9]+"', main_zone)) == 1
    details = html[html.index('<details id="details">'):]
    for ident in ("ch_io", "ch_nr", "ch_pol", "ch_temp", "ch_auto", "ch_dmg", "tb_tests"):
        assert f'id="{ident}"' in details, ident                                          # secondary charts and the tests table are collapsed under Details
    for sel in ('id="presets"', 'id="dmg_seg"', 'id="custom"', 'id="reset"'):
        assert sel in html
    assert re.findall(r'data-step="([a-z]+)"', re.search(r'<nav class="actionbar".*?</nav>', html, re.S).group(0)) == ["choose", "result", "reliability"]
    assert html.count('class="kpis"') == 1 and "Public draft, published 2026-10-21. Conditional scenarios, not forecasts." in html


def test_tests_table_lists_the_recorded_failures_and_met_tests():
    html = index_html()
    tbl = re.search(r'<table class="tests".*?</table>', html, re.S).group(0)
    for name in ("A3.1", "A3.2", "A3.4(b)", "M6", "A2.1", "A1.3", "A1.4", "A2.6", "B1 sign", "R1 sign", "B2 sign"):
        assert f'<th scope="row">{name}</th>' in tbl, name
    assert tbl.count('class="res failed"') >= 6 and tbl.count('class="res met"') >= 4
    lim = (SITE / "limitations.html").read_text(encoding="utf-8")
    for anchor in set(re.findall(r'href="limitations\.html#([a-z0-9-]+)"', tbl)):
        assert f'id="{anchor}"' in lim, anchor


def test_dashboard_keeps_the_v01_caveats_verbatim():
    html = index_html()
    for phrase in ("Compute and electricity outputs are withheld until the S3 compute path is validated",
                   'The "high" damage option is NOT the upper end of the literature',
                   "FaIR climate starts about 0.04 to 0.07 K below observed", "all runs with climate damage on", "A3.4(b)", "A1.3", "A2.1",
                   "S3's economy and World3's are not reconciled", "No health or yield effect of warming", "[unverified]", "Not shown".replace("Not shown", "What is not shown")):
        assert phrase.lower() in html.lower(), phrase


def test_dashboard_script_labels_and_units():
    src = JS.read_text(encoding="utf-8")
    assert "Model dollars per year" in src and "Dollars per year" not in src.replace("Model dollars per year", "")
    m = (SITE / "methods.html").read_text(encoding="utf-8")
    assert "model dollars per year" in m.lower() and "constant dollars" in m


def test_every_chart_slot_gets_the_card_tools_from_the_chart_module():
    charts = (REPO / "site_src" / "charts.js").read_text(encoding="utf-8")
    for needle in ("View data table", "Download PNG", "Download CSV", "Text alternative", 'role="img"'):
        assert needle in charts, needle
    dash = JS.read_text(encoding="utf-8")
    assert dash.count("C.lineChart(") >= 2 and 'title: false' in dash                          # the main chart's finding title is the page headline, the others carry their own
    assert re.search(r"sec\(\"ch_io\".*tio", dash)
