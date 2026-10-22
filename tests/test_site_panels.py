"""Explorer v0.2 stage 6 (D-057 ported to the v0.2 layout): Model versus reality and the Warming map as tabs of the dashboard, one line in story chapter 1, a link from the
connections page. Written before the browser check. The numbers, thresholds and schemas of the data are tested in tests/test_site_history.py; here: the layout, the finding
titles generated from the data (committed and synthetic, incl. null), the card tools (data table, PNG, CSV, text alternative, assumptions link), the caveats kept verbatim,
and that the data reaches the page through the one data file."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
SRC = REPO / "site_src"
EXPL = SITE / "data" / "explorer.json"
NODE = shutil.which("node")
LABEL = "Illustrative downscaling of the global FaIR result. Not a regional climate projection. Pattern-scaling ignores regional feedbacks, aerosols, ocean dynamics."
need_node = pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH")
need_data = pytest.mark.skipif(not EXPL.exists(), reason="site data not built")


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def node(expr: str, tmp_path: Path, payload: dict = None):
    prog = ("global.window={};const F3=require(" + json.dumps(str(SRC / "core.js")) + ");window.F3=F3;global.document={};require(" + json.dumps(str(SRC / "charts.js")) + ");const C=window.F3C;"
            "const IN=" + json.dumps(payload or {}) + ";\nprocess.stdout.write(JSON.stringify((function(){" + expr + "})()));")
    f = tmp_path / "t.js"
    f.write_text(prog, encoding="utf-8")
    return json.loads(subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)


def dash() -> str:
    return (SITE / "explorer.html").read_text(encoding="utf-8")


# ----------------------------------------------------------------------------------------------------------- data path
@need_data
def test_history_and_map_reach_the_page_through_the_one_data_file_and_equal_the_builders_files():
    d = load(EXPL)
    assert d["history"] == load(SITE / "data" / "history.json") and d["warming_map"] == load(SITE / "data" / "warming-map.json")
    for bad in ("NaN", "Infinity"):                                                         # strictness of the whole file is tested in test_site_nulls.py
        assert bad not in re.sub(r'"(?:[^"\\]|\\.)*"', '""', EXPL.read_text(encoding="utf-8"))
    js = (SITE / "assets" / "dashboard.js").read_text(encoding="utf-8")
    assert "F3DATA.history" in js and "F3DATA.warming_map" in js and "fetch(" not in js


# ----------------------------------------------------------------------------------------------------------- layout
def test_dashboard_has_three_tabs_and_two_panels_after_the_reliability_section():
    html = dash()
    tabs = re.search(r'<div class="dtabs".*?</div>', html, re.S).group(0)
    assert re.findall(r'role="tab" id="(tab_[a-z]+)"', tabs) == ["tab_scenario", "tab_history", "tab_map"]
    assert tabs.count('aria-selected="true"') == 1 and re.findall(r'aria-controls="([a-z_]+)"', tabs) == ["result", "p_history", "p_map"]
    assert 'data-tab="scenario"' in html.split('id="dash"')[1][:80]
    for ident in ("p_history", "p_map"):
        assert f'<section class="panel" id="{ident}" role="tabpanel"' in html
    pos = [html.index(m) for m in ('id="dtabs"', 'id="result"', 'id="reliability"', 'id="p_history"', 'id="p_map"', 'class="actionbar"')]
    assert pos == sorted(pos)
    hist = html[html.index('id="p_history"'):html.index('id="p_map"')]
    assert 'id="ch_hpop"' in hist and 'id="ch_htemp"' in hist
    sec = re.search(r'<details class="secondary" id="hist_sec">(.*?)</details>', hist, re.S).group(1)
    assert 'id="ch_hio"' in sec and "Secondary comparison" in hist                           # the output index is secondary: collapsed under its own summary
    assert hist.index('id="gap_io"') > hist.index("</details>")   # its different-quantities sentence stays visible, outside the collapsed block
    assert 'id="ch_map"' in html[html.index('id="p_map"'):] and 'id="map_year"' in html


def test_phone_rules_and_tab_visibility_in_the_stylesheet():
    css = (SRC / "style.css").read_text(encoding="utf-8")
    assert ".dash[data-tab=scenario] .panel" in css and ".dash[data-tab=history] #result" in css and ".dash[data-tab=map] #p_history" in css
    assert ".dash[data-step=reliability] #p_history" in css and "#result,.panel{order:1}#reliability{order:2}" in css
    js = (SRC / "dashboard.js").read_text(encoding="utf-8")
    assert 'role=tab' in js and '"ArrowRight"' in js and '"Home"' in js and "&tab=" in js and "tabFromHash" in js


def test_panel_status_badges_exist_link_to_limitations_and_the_anchors_exist():
    html = dash()
    badges = re.findall(r'<a class="badge amber" href="limitations\.html#(status-history|status-map)">(.*?)</a>', html, re.S)
    assert [b[0] for b in badges] == ["status-history", "status-map"]
    lim = (SITE / "limitations.html").read_text(encoding="utf-8")
    for anchor, txt in badges:
        assert f'id="{anchor}"' in lim and re.search(r"[A-Za-z]{4,}", re.sub(r"<[^>]+>", "", txt))


def test_existing_caveats_are_kept_verbatim_in_the_panels():
    html = dash()
    for phrase in (LABEL, "This is not a validation.", "nothing was tuned to improve the match", "Test A3.4(b) FAILED:", "Test A2.1 FAILED", "0.93% (0.25% required)",
                   "hollow dots for 2024 and 2025 are the UN's own projection", "Pattern uncertainty is not shown", "the spread of the coefficients across 32 CMIP6 models is stored in the data file and not drawn",
                   "They are not the same quantity.", "GISTEMP was used as a cross-check only", "none of its values is shown", "No country-level, damage or population map is shown.",
                   "The coefficients are derived by F3; the Atlas does not publish them.", "the map inherits both", "Natural Earth (public domain)"):
        assert phrase in html, phrase
    meth = (SITE / "methods.html").read_text(encoding="utf-8")
    assert 'id="history-overlay"' in meth and 'id="warming-map"' in meth and "It is a comparison, not a validation." in meth and "Nothing in any model was tuned" in meth


def test_story_chapter_one_has_one_generated_line_and_the_connections_page_links_to_both_views():
    story = (SITE / "index.html").read_text(encoding="utf-8")
    ch1 = re.search(r'id="ch1".*?</section>', story, re.S).group(0)
    assert 'id="ch1_hist"' in ch1 and 'href="explorer.html#tab=history"' in ch1 and ch1.count('id="ch1_hist"') == 1
    assert "historyPopGap" in (SRC / "story.js").read_text(encoding="utf-8") and not re.search(r"\d+\.\d{2}", re.sub(r'<[^>]+>', '', ch1.split('id="ch_s1"')[1].split("</p>")[0]))   # the line is written by the script, none typed
    con = (SITE / "connections.html").read_text(encoding="utf-8")
    box = re.search(r'<section class="card" id="outside">.*?</section>', con, re.S).group(0)
    assert 'href="explorer.html#tab=history"' in box and 'href="explorer.html#tab=map"' in box and "not a validation" in box and "not a regional projection" in box


# ----------------------------------------------------------------------------------------------------------- generated titles
@need_data
@need_node
def test_finding_titles_are_generated_from_the_data(tmp_path):
    d = load(EXPL)
    H, M, E = d["history"], d["warming_map"], d
    run = E["world3"]["runs"][E["world3"]["standard"] + "|off"]
    r = node("return {p:F3.historyPopGap(IN.y,IN.pop,IN.H),i:F3.historyIoGap(IN.y,IN.io,IN.H),t:F3.historyTempGap(IN.H),m:F3.mapTakeaway(IN.M,IN.C,2100)}", tmp_path,
             {"y": E["world3"]["years"], "pop": run["pop"], "io": run["io"], "H": H, "M": M, "C": {"years": E["years"], **E["climate"]}})
    p, i, t, m = r["p"], r["i"], r["t"], r["m"]
    assert f"{p['gapPct']:+.1f}%" in p["title"] and f"{p['model']:.2f}" in p["title"] and f"{p['obs']:.2f}" in p["title"] and str(p["year"]) in p["title"]
    assert ("within" if p["within"] else "outside") in p["title"] and "5% band" in p["title"]
    assert f"{i['gapPct']:+.1f}%" in i["title"] and "not the same quantity" in i["title"]
    assert f"{t['diff']:+.2f} K" in t["title"] and "A2.1" in t["title"]
    assert f"{m['hottest']['value']:.1f} K" in m["title"] and m["hottest"]["name"] in m["title"] and f"{m['global']['mean']:.2f} K" in m["title"]
    syn = json.loads(json.dumps(H))
    syn["population"]["billions"] = [v * 1.2 for v in syn["population"]["billions"]]
    p2 = node("return F3.historyPopGap(IN.y,IN.pop,IN.H)", tmp_path, {"y": E["world3"]["years"], "pop": run["pop"], "H": syn})
    assert p2["title"] != p["title"] and f"{p['obs']:.2f}" not in p2["title"]


@need_node
def test_titles_say_no_value_for_missing_data_never_zero(tmp_path):
    H = {"population": {"years": [2022, 2023], "is_estimate": [True, True], "billions": [None, None]}, "gdp": {"years": [1990, 2000], "trillion_usd_2015": [None, 1]},
         "temperature": {"years": [2025], "hadcrut5": [None], "hadcrut5_lower": [0], "hadcrut5_upper": [1], "fair_mean": [0.5], "fair_p05": [0], "fair_p95": [1]}}
    r = node("var y=[2020,2021,2022,2023,2024],a=[1e9,2e9,3e9,4e9,5e9];return {p:F3.historyPopGap(y,a,IN.H),i:F3.historyIoGap(y,a,IN.H),t:F3.historyTempGap(IN.H),cal:[F3.calYear([1,null,3],[1,2,3],1),F3.calYear([1,2,3],[1,2,3],1)],"
             "m:F3.mapTakeaway({regions:[{id:'A',name:'A',c:1}]},{years:[2100],warming:[null],warming_p05:[null],warming_p95:[null]},2100)}", tmp_path, {"H": H})
    for k in ("p", "i", "t"):
        assert "no value" in r[k]["title"] and r[k]["gapPct" if k != "t" else "diff"] is None
    assert r["cal"] == [None, 1.5] and "no value" in r["m"]["title"] and r["m"]["hottest"] is None


# ----------------------------------------------------------------------------------------------------------- card tools for the map
@need_data
@need_node
def test_map_spec_csv_table_and_assumptions(tmp_path):
    d = load(EXPL)
    M = d["warming_map"]
    spec = node("return F3.mapSpec(IN.M, IN.C, IN.y, 2050)", tmp_path, {"M": M, "C": d["climate"], "y": d["years"]})
    g = d["climate"]["warming"][d["years"].index(2050)]
    assert spec["global"] == pytest.approx(g) and spec["year"] == 2050 and spec["assume"]["href"] == "methods.html#warming-map"
    assert LABEL in spec["caveat"] and "pattern uncertainty is not" in spec["caveat"].lower() and "A2.1" in spec["caveat"]
    assert LABEL in spec["summary"]
    csv = node("return C.csvFor({spec:IN.s})", tmp_path, {"s": spec}).splitlines()
    assert csv[0] == "region_id,region,type,coefficient_K_per_K,warming_K_2050" and sum(1 for ln in csv if ln and not ln.startswith("#") and not ln.startswith("region_id")) == 58
    best = max(M["regions"], key=lambda r: r["c"])
    assert csv[1].startswith(best["id"] + ",") and float(csv[1].split(",")[-1]) == pytest.approx(best["c"] * g)
    assert any(ln.startswith("# ") and LABEL in ln for ln in csv) and any("not a forecast" in ln for ln in csv)
    charts = (SRC / "charts.js").read_text(encoding="utf-8")
    seg = charts[charts.index("function regionMap("):charts.index("function mapRead(")]
    for needle in ("mount(el, spec)", "tableHtml(c,", "setText(c, spec)", "F3.mapTable"):
        assert needle in seg, needle


def test_history_charts_draw_observed_series_as_points_with_hollow_projection_years():
    charts = (SRC / "charts.js").read_text(encoding="utf-8")
    assert "if (s.dots)" in charts and "s.proj && s.proj[i]" in charts
    js = (SRC / "dashboard.js").read_text(encoding="utf-8")
    assert "dots: true" in js and "is_estimate.map(function (e) { return !e; })" in js
    assert js.count("assume: F3.ASSUME.history") == 3
