"""The "Average or spread?" page (spread.html, D-062, Proposed). It states a hypothesis; nothing on it is F3 output.
The tests check the labels that keep it honest, the drawing rules shared with the other infographics, and that the page is reachable from every page."""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
sys.path.insert(0, str(REPO / "site_src"))


def html() -> str:
    return (SITE / "spread.html").read_text(encoding="utf-8")


def test_hypothesis_is_labelled_untested_and_not_f3_output():
    h = html()
    assert "A hypothesis, not a result of the F3 model." in h
    assert "Nothing on this page is computed by F3" in h and "<strong>untested</strong>" in h
    assert "most published evidence so far shows gaps narrowing" in h
    assert "Conditional scenarios, not forecasts." in h                       # the site banner is on this page too
    assert "proposed, not built" in h and "None of this is built or decided" in h


def test_verification_level_is_stated():
    h = html()
    assert "read from search extracts on 2026-11-12; the primary pages were not opened" in h
    assert "this page's inference, not a statement quoted from the source" in h


def test_three_infographics_with_text_alternatives_and_min_font():
    h = html()
    svgs = re.findall(r"<svg id=\"(ig_spread_[a-z])\".*?</svg>", h, flags=re.S)
    assert svgs == ["ig_spread_h", "ig_spread_k", "ig_spread_s"]
    for block in re.findall(r"<svg id=\"ig_spread_[a-z]\".*?</svg>", h, flags=re.S):
        assert 'role="img"' in block and "<title" in block and "<desc" in block
        assert 'viewBox="0 0 310 ' in block                                 # phone-first width, as ig.py
        sizes = [float(x) for x in re.findall(r'font-size="([0-9.]+)"', block)]
        assert sizes and min(sizes) >= 13
        assert not re.search(r"#[0-9a-fA-F]{3,6}\b", block)                # colours come from the stylesheet tokens


def test_measured_is_solid_and_untested_is_dashed():
    h = html()
    assert len(re.findall(r'class="cv measured" data-status="measured"', h)) == 1
    assert len(re.findall(r'class="cv untested" data-status="untested"', h)) == 1
    css = (SITE / "assets" / "f3.css").read_text(encoding="utf-8")
    assert re.search(r"svg\.ig \.cv\.untested\{[^}]*stroke-dasharray", css)
    assert not re.search(r"svg\.ig \.cv\.measured\{[^}]*stroke-dasharray", css)
    assert not re.search(r"svg\.ig \.cv\.[a-z]+\{[^}]*var\(--s[ab]\)", css)   # never the scenario colours (design guidelines 4.1)


def test_every_figure_has_a_source_link():
    import spread_body
    h = html()
    for row in spread_body.SOURCES + spread_body.STUDIES:
        assert row[-1].startswith("https://") and f'href="{row[-1]}"' in h
    assert {r[2] for r in spread_body.SOURCES} == {"fits", "mixed", "different"}
    assert sum(r[2] == "fits" for r in spread_body.SOURCES) == 2             # the heading says "it fits two"


def test_page_is_in_the_navigation_of_every_page():
    for p in SITE.glob("*.html"):
        assert 'href="spread.html"' in p.read_text(encoding="utf-8"), p.name
