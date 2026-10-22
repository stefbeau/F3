"""Explorer v0.2 (D-056): the feedback-loop diagram (Connections page) and the roadmap (Methods page), restored from the v0.1 markup in site_src/ig.py and restyled to the
v0.2 tokens. They complement the interactive map. Checks: solid/dashed/dotted vocabulary agrees with site_src/links.py, text alternatives, 13 px text, no hard-coded colours."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
SRC = REPO / "site_src"
sys.path.insert(0, str(SRC))

import links  # noqa: E402

BUILT = {l["id"] for l in links.LINKS if l["status"] == "built"}
BY_ID = {l["id"]: l for l in links.LINKS}
YES = {"built": "yes", "not-built": "no", "withheld": "withheld"}


def svg_of(html: str, ident: str) -> str:
    m = re.search(rf'<svg[^>]*id="{ident}".*?</svg>', html, re.S)
    assert m, ident
    return m.group(0)


def paths(svg: str) -> list[str]:
    return re.findall(r"<path [^>]*data-link=[^>]*>", svg)


def test_loop_diagram_is_on_the_connections_page_next_to_the_map():
    html = (SITE / "connections.html").read_text(encoding="utf-8")
    assert 'id="ig_loops"' in html and 'id="map"' in html          # the diagram complements the map, it does not replace it
    svg = svg_of(html, "ig_loops")
    ps = paths(svg)
    assert len(ps) == 7
    seen = {}
    for p in ps:
        ident = re.search(r'data-link="([^"]+)"', p).group(1)
        built = re.search(r'data-built="([^"]+)"', p).group(1)
        seen[ident] = (built, p)
    assert set(seen) == set(BY_ID)                                  # the same seven links as links.py
    for ident, (built, p) in seen.items():
        status = BY_ID[ident]["status"]
        assert built == YES[status], ident
        assert f'class="ln {status}"' in p, ident
        if status == "built":
            assert "stroke-dasharray" not in p, ident              # exactly the built links are solid
        elif status == "not-built":
            assert 'stroke-dasharray="7 5"' in p, ident
        else:
            assert 'stroke-dasharray="1 6"' in p, ident
    assert {i for i, (b, _) in seen.items() if b == "yes"} == BUILT
    nums = [int(n) for n in re.findall(r'class="numtxt">(\d)</text>', svg)]
    assert sorted(nums) == list(range(1, 8))


def test_roadmap_is_on_the_methods_page_and_only_the_built_links_are_solid():
    html = (SITE / "methods.html").read_text(encoding="utf-8")
    svg = svg_of(html, "ig_roadmap")
    ps = paths(svg)
    assert len(ps) == 5
    solid = {re.search(r'data-link="([^"]+)"', p).group(1) for p in ps if "stroke-dasharray" not in p}
    assert solid == BUILT
    assert all(re.search(r'data-built="yes"', p) for p in ps if "stroke-dasharray" not in p)
    assert all(re.search(r'data-built="no"', p) for p in ps if "stroke-dasharray" in p)
    assert 'href="connections.html"' in html and "emissions feedback" in svg.lower()


def test_both_diagrams_have_text_alternatives_and_readable_text_and_use_only_tokens():
    for page, ident in (("connections.html", "ig_loops"), ("methods.html", "ig_roadmap")):
        svg = svg_of((SITE / page).read_text(encoding="utf-8"), ident)
        assert 'role="img"' in svg and re.search(r"<title[ >]", svg) and re.search(r"<desc[ >]", svg)
        for ref in re.search(r'aria-labelledby="([^"]+)"', svg).group(1).split():
            assert f'id="{ref}"' in svg
        sizes = [float(x) for x in re.findall(r'font-size="([0-9.]+)"', svg)]
        assert sizes and min(sizes) >= 13
        assert not re.search(r"#[0-9a-fA-F]{3,6}\b|rgb\(", svg), "colours must come from CSS variables"
    assert "Not built, dashed" in (SITE / "connections.html").read_text(encoding="utf-8")        # the key keeps its text alternative
    assert "Dashed:" in (SITE / "methods.html").read_text(encoding="utf-8")


def test_stylesheet_styles_the_diagram_links_with_the_theme_tokens():
    css = (SRC / "style.css").read_text(encoding="utf-8")
    for rule in ("svg.ig .ln.built{stroke:var(--sa)", "svg.ig .ln.not-built{stroke:var(--mut)", "svg.ig .ln.withheld{stroke:var(--warnl)"):
        assert rule in css, rule
