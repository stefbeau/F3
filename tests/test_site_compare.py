"""Explorer v0.2 stage 4 (D-056): the Compare page. Structure and honesty checks on the generated markup and scripts; the delta maths, headline and hash round trip
are tested in tests/test_site_v02_core.py, and the page was exercised in a real browser (docs/site-explorer.md)."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
SRC = REPO / "site_src"


def page() -> str:
    return (SITE / "compare.html").read_text(encoding="utf-8")


def test_compare_page_is_in_the_navigation_of_every_page():
    for name in ("index.html", "explorer.html", "compare.html", "methods.html", "limitations.html", "sources.html", "about.html"):
        html = (SITE / name).read_text(encoding="utf-8")
        assert 'href="compare.html"' in html, name


def test_two_pickers_a_fixed_baseline_and_the_phone_step_flow():
    html = page()
    for k in ("a", "b"):
        assert f'id="sel_{k}"' in html and f'id="seg_{k}"' in html                    # a preset and a damage option each
    assert "The baseline is fixed" in html and "standard run with climate damage off" in html
    assert re.findall(r'data-step="([a-z]+)"', re.search(r'<nav class="actionbar".*?</nav>', html, re.S).group(0)) == ["choose", "result", "reliability"]
    for ident in ("headline", "ch_over", "ch_bars", "tb_delta", "identical_note", "metric_seg"):
        assert f'id="{ident}"' in html, ident


def test_overlay_has_at_most_three_lines_baseline_a_b_in_the_scenario_colours():
    js = (SRC / "compare.js").read_text(encoding="utf-8")
    overlay = js[js.index("C.lineChart($(\"ch_over\")"):js.index("/* diverging bars")]
    assert overlay.count("tcolor:") == 3                                              # three series, no more
    assert "sc.base" in overlay and "sc.a" in overlay and "sc.b" in overlay
    assert 'dash: "7 4"' in overlay                                                    # baseline dashed grey


def test_bars_have_a_visible_zero_line_and_a_diverging_scale():
    charts = (SRC / "charts.js").read_text(encoding="utf-8")
    bar = charts[charts.index("function barChart"):charts.index("/* ---------- downloads")]
    assert "stroke-width=\"2.2\"" in bar and "zx" in bar                                # the zero line is drawn thicker than the grid
    assert "vals = [0]" in bar                                                          # zero is always inside the scale, so bars diverge from it


def test_delta_table_columns_and_identical_row_note():
    js = (SRC / "compare.js").read_text(encoding="utf-8")
    for col in ("Baseline", "A vs baseline", "B vs baseline", "B minus A", "Note"):
        assert col in js, col
    assert "Identical in all three" in js and "Identical in the baseline, A and B" in js
    assert "same warming" in js                                                         # warming is the identical row, and the page says why


def test_caveats_stay_visible_on_the_compare_page():
    html = page().lower()
    for phrase in ("public draft, published 2026-10-21. conditional scenarios, not forecasts.", "high is not the upper end of the literature", "not compared with worlddynamics.jl",
                   "s3's economy and world3's are not reconciled", "no health or yield effect of warming", "a3.4(b)", "a2.1"):
        assert phrase in html, phrase
    js = (SRC / "compare.js").read_text(encoding="utf-8")
    assert "damageNotice" in js and 'id="cmp_damage_notice"' in page()                  # the damage notice appears when either scenario has damage on


def test_no_social_module_and_no_forbidden_chart_types():
    visible = re.sub(r"<script.*?</script>", "", page(), flags=re.S)
    assert not re.search(r"\bS7\b|social module|inequality index", visible)
    for name in ("charts.js", "compare.js", "dashboard.js", "story.js"):
        src = (SRC / name).read_text(encoding="utf-8").lower()
        assert not re.search(r"\bpie\b|donut|doughnut|yaxis2|secondary axis|dual axis|b3db|3-d", src), name
