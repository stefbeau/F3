"""Explorer v0.2 (D-056): the warming stripes are a chart card like the others: a finding title generated from the data, a text alternative, a data table (every year),
PNG and CSV download, all carrying the A2.1 caveat. Written before the code. The browser side (clicking the buttons, the downloaded files) is checked live in
docs/site-explorer.md; here: the markup, the pure spec in core.js on the committed data and on synthetic data (incl. null), and charts.js's CSV for the stripes."""
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
DATA = SITE / "data" / "explorer.json"
NODE = shutil.which("node")
need_node = pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH")
need_data = pytest.mark.skipif(not DATA.exists(), reason="site/data/explorer.json not present (build the site first)")


def node(expr: str, tmp_path: Path, payload: dict = None):
    prog = ("global.window={};const F3=require(" + json.dumps(str(SRC / "core.js")) + ");window.F3=F3;global.document={};require(" + json.dumps(str(SRC / "charts.js")) + ");const C=window.F3C;"
            "const IN=" + json.dumps(payload or {}) + ";\nprocess.stdout.write(JSON.stringify((function(){" + expr + "})()));")
    f = tmp_path / "t.js"
    f.write_text(prog, encoding="utf-8")
    return json.loads(subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)


def test_stripes_sit_in_a_chart_card_slot_on_the_story_and_the_dashboard():
    for page in ("index.html", "explorer.html"):
        html = (SITE / page).read_text(encoding="utf-8")
        slot = re.search(r'<div id="ch_stripes">(.*?)</div>', html, re.S).group(1)
        assert 'id="ig_stripes"' in slot and 'role="img"' in slot and "<title" in slot and "<desc" in slot       # the text alternative is in the markup, the script adopts it
        assert "A2.1" in slot and "failed" in slot
        js = (SRC / ("story.js" if page == "index.html" else "dashboard.js")).read_text(encoding="utf-8")
        assert 'C.stripes($("ch_stripes"), F3.stripesSpec(' in js and "rgb(" not in js                         # one shared drawing routine, no copy in the page script


@need_node
def test_charts_module_offers_the_card_tools_for_the_stripes():
    charts = (SRC / "charts.js").read_text(encoding="utf-8")
    seg = charts[charts.index("function stripes("):charts.index("/* ---------- downloads")]
    for needle in ("mount(el, spec)", "tableHtml(c,", "setText(c, spec)", "no value"):
        assert needle in seg, needle
    assert 'kind === "stripes"' in charts[charts.index("function csvFor"):]


@need_data
@need_node
def test_stripes_spec_title_and_table_come_from_the_data(tmp_path):
    d = json.loads(DATA.read_text(encoding="utf-8"))
    w, years = d["climate"]["warming"], d["years"]
    spec = node("return F3.stripesSpec(IN.c, IN.y)", tmp_path, {"c": d["climate"], "y": years})
    lo, hi = min(w), max(w)
    assert f"{lo:.2f} K in {years[w.index(lo)]}" in spec["title"] and f"{hi:.2f} K in {years[w.index(hi)]}" in spec["title"]
    assert spec["values"] == w and spec["years"] == years
    assert "A2.1" in spec["caveat"] and "failed" in spec["caveat"] and "not observed" in spec["caveat"] and "prescribed" in spec["caveat"]
    assert spec["summary"].startswith(spec["title"]) and spec["caveat"] in spec["summary"]
    syn = {"warming": [0.5 + 0.01 * i for i in range(len(years))]}
    spec2 = node("return F3.stripesSpec(IN.c, IN.y)", tmp_path, {"c": syn, "y": years})
    assert spec2["title"] != spec["title"] and "0.50 K in 2025" in spec2["title"] and f"{0.5 + 0.01 * 75:.2f} K in 2100" in spec2["title"]


@need_node
def test_stripes_csv_has_one_row_per_year_and_carries_the_caveat_and_null_is_empty(tmp_path):
    years = [2025, 2026, 2027]
    out = node("var s=F3.stripesSpec({warming:[1.2,null,1.4]},IN.y);return C.csvFor({spec:s})", tmp_path, {"y": years})
    lines = out.splitlines()
    assert lines[0] == "year,FaIR ensemble mean warming above 1850-1900 (K)" and lines[1:4] == ["2025,1.2", "2026,", "2027,1.4"]
    text = out
    assert "# F3 Explorer v0.2: a conditional scenario, not a forecast." in text and "test A2.1 failed" in text and "not observed data" in text
    assert "An empty cell means no value" in text
    title = node("return F3.stripesSpec({warming:[null,null]},[2025,2026]).title", tmp_path)
    assert "no value" in title


def test_stylesheet_has_the_swatch_and_long_table_rules():
    css = (SRC / "style.css").read_text(encoding="utf-8")
    assert ".leg i.sw{" in css and ".dtbox.long .tblwrap{max-height" in css
