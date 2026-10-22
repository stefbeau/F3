"""Explorer v0.2 (D-056): every chart card carries an assumptions link (design-guidelines 5, 'links to the assumptions behind it'), including the warming stripes.
Checks: the card template has the link; every chart call in a page script passes `assume`; each link target is an anchor that exists in the generated pages; the choice
follows the chart (World3, climate-damage coupling, FaIR, AI race, damage options). The live check (every .chartcard on every page has a working link) is in docs/site-explorer.md."""
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
NODE = shutil.which("node")
need_node = pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH")


def node(expr: str, tmp_path: Path):
    prog = "const F3=require(" + json.dumps(str(SRC / "core.js")) + ");process.stdout.write(JSON.stringify((function(){" + expr + "})()));"
    f = tmp_path / "t.js"
    f.write_text(prog, encoding="utf-8")
    return json.loads(subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)


def test_the_card_template_has_an_assumptions_link_updated_on_every_draw():
    charts = (SRC / "charts.js").read_text(encoding="utf-8")
    assert 'data-role="assume"' in charts and "c.assume.href = spec.assume.href" in charts
    mount = charts[charts.index("function mount("):charts.index("function setText(")]
    assert mount.index('data-role="assume"') < mount.index('data-dl="table"')                       # the link comes before the download buttons, visible without opening anything


def test_every_chart_call_in_the_page_scripts_passes_an_assumptions_target():
    for name in ("dashboard.js", "story.js", "compare.js"):
        src = (SRC / name).read_text(encoding="utf-8")
        calls = len(re.findall(r"C\.(?:lineChart|barChart)\(", src))
        assert calls >= 2 and calls == len(re.findall(r"\bassume:", src)), (name, calls)


@need_node
def test_targets_follow_the_chart_and_exist_as_anchors(tmp_path):
    out = node("return {off:F3.assumeFor('world3','off'),on:F3.assumeFor('world3','central'),none:F3.assumeFor('world3',undefined),clim:F3.assumeFor('climate','central'),ai:F3.assumeFor('ai'),"
               "all:F3.ASSUME,stripes:F3.stripesSpec({warming:[1]},[2025]).assume}", tmp_path)
    assert out["off"]["href"] == "methods.html#grids" and out["none"]["href"] == "methods.html#grids"
    assert out["on"]["href"] == "methods.html#coupling"                                              # damage on: the assumptions are the coupling's
    assert out["clim"]["href"] == "limitations.html#status-climate" and out["ai"]["href"] == "limitations.html#status-ai"
    assert out["stripes"] == out["all"]["climate"]
    for key, a in out["all"].items():
        page, anchor = a["href"].split("#")
        assert f'id="{anchor}"' in (SITE / page).read_text(encoding="utf-8"), (key, a["href"])
        assert len(a["text"]) > 20 and a["text"].startswith("Assumptions")


def test_stylesheet_styles_the_link():
    assert ".assume{" in (SRC / "style.css").read_text(encoding="utf-8")
