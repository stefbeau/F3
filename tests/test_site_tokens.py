"""Explorer v0.2 (D-056) design tokens: WCAG AA contrast is verified programmatically from the stylesheet itself (site_src/style.css),
the scenario colours are the ones in docs/design-guidelines.md, and no text is set below 13 px."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CSS = (REPO / "site_src" / "style.css").read_text(encoding="utf-8")


def theme(name: str) -> dict:
    sel = r":root,:root\[data-theme=light\]" if name == "light" else r":root\[data-theme=dark\]"
    m = re.search(sel + r"\{(.*?)\}", CSS, re.S)
    assert m, name
    return dict(re.findall(r"--([a-z0-9-]+):(#[0-9a-fA-F]{6})", m.group(1)))


def lum(h: str) -> float:
    h = h.lstrip("#")
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4          # noqa: E731
    return 0.2126 * f(ch[0]) + 0.7152 * f(ch[1]) + 0.0722 * f(ch[2])


def ratio(a: str, b: str) -> float:
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


TEXT_ON_SURFACE = ["fg", "mut", "link", "base-t", "sa-t", "sb-t", "acc1", "acc2", "acc3", "heat"]
GRAPHICS = ["base", "sa", "sb", "acc1", "acc2", "acc3", "heat"]
PAIRS = [("on-sa", "sa"), ("on-sb", "sb"), ("amber-t", "amber-bg"), ("red-t", "red-bg"), ("ok-t", "ok-bg"), ("btn-on-fg", "btn-on-bg"), ("fg", "warn")]


@pytest.mark.parametrize("name", ["light", "dark"])
def test_text_colours_meet_aa_4_5(name):
    t = theme(name)
    for surface in ("bg", "card", "card2"):
        for tok in TEXT_ON_SURFACE:
            assert ratio(t[tok], t[surface]) >= 4.5, (name, tok, surface, round(ratio(t[tok], t[surface]), 2))


@pytest.mark.parametrize("name", ["light", "dark"])
def test_graphic_colours_meet_3_to_1_on_the_card(name):
    t = theme(name)
    for tok in GRAPHICS:
        assert ratio(t[tok], t["card"]) >= 3.0, (name, tok, round(ratio(t[tok], t["card"]), 2))


@pytest.mark.parametrize("name", ["light", "dark"])
def test_badge_and_button_pairs_meet_aa(name):
    t = theme(name)
    for fg, bg in PAIRS:
        assert ratio(t[fg], t[bg]) >= 4.5, (name, fg, bg, round(ratio(t[fg], t[bg]), 2))


def test_contrast_function_is_not_vacuous():
    assert ratio("#777777", "#888888") < 1.5 and ratio("#000000", "#ffffff") > 20


@pytest.mark.parametrize("name", ["light", "dark"])
def test_scenario_colours_are_the_guideline_hexes_in_both_themes(name):
    t = theme(name)
    assert (t["base"].lower(), t["sa"].lower(), t["sb"].lower()) == ("#6b7280", "#1f78b4", "#d95f02")


def test_guidelines_record_the_hex_codes():
    g = (REPO / "docs" / "design-guidelines.md").read_text(encoding="utf-8").lower()
    for name in ("light", "dark"):
        for tok, h in theme(name).items():
            if tok in ("base", "sa", "sb", "acc1", "acc2", "acc3", "heat", "bg", "card", "fg"):
                assert h.lower() in g, (name, tok, h)


def test_no_font_size_below_13px():
    for m in re.finditer(r"font-size:([0-9.]+)(rem|em|px)", CSS):
        v, unit = float(m.group(1)), m.group(2)
        px = v * 16 if unit in ("rem", "em") else v
        assert px >= 13 - 1e-9, m.group(0)


def test_font_is_embedded_not_fetched():
    assert "@import" not in CSS and "fonts.googleapis" not in CSS
    assert "/*FONT*/" in CSS
    css_out = REPO / "site" / "assets" / "f3.css"
    if css_out.exists():
        out = css_out.read_text(encoding="utf-8")
        assert "data:font/woff2;base64," in out and "http" not in re.sub(r"data:font/woff2;base64,[A-Za-z0-9+/=]+", "", out)
