"""Atlas pages (D-067, Provisional): reported figures about AI's effects, shown beside F3 output. Written before the pages.
Readings fixed here: (1) every atlas page says its figures are reported and are not F3 output; (2) every page states what F3 does with the topic
(modelled, withheld or not modelled) and never draws a withheld series; (3) every F3 number shown is read from site/data/explorer.json and carries the
notice of its sector (D-029 for S3, D-030 for climate, the D-007 sentence wherever the high option appears); (4) every citation resolves to a linked
source on the same page; (5) the claim about forest clearing is stated as unsupported."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
TOPICS = ["energy", "water", "land", "work", "health", "mind", "safety", "military", "creative", "surveillance", "nature"]
PAGES = ["atlas.html"] + [f"atlas-{t}.html" for t in TOPICS]
F3_STATE = {"energy": "model", "work": "model", "land": "model", "water": "none", "health": "none", "mind": "none", "safety": "none",
            "military": "none", "creative": "none", "surveillance": "none", "nature": "none"}
LABEL = "Reported figures, not F3 model output"


def read(name: str) -> str:
    return (SITE / name).read_text(encoding="utf-8")


def data() -> dict:
    return json.loads((SITE / "data" / "explorer.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", PAGES)
def test_every_atlas_page_exists_is_labelled_and_sits_in_the_site_nav(name):
    html = read(name)
    assert LABEL in html
    assert '<a href="atlas.html" aria-current="page">Atlas</a>' in html
    assert "Conditional scenarios, not forecasts." in html                           # the site footer
    assert not re.search(r"#[0-9a-fA-F]{6}\b", re.sub(r"<head>.*?</head>", "", html, flags=re.S))      # colours come from the stylesheet tokens


def test_the_other_pages_link_to_the_atlas():
    for name in ("index.html", "explorer.html", "ai.html", "limitations.html"):
        assert '<a href="atlas.html">Atlas</a>' in read(name), name


@pytest.mark.parametrize("topic", TOPICS)
def test_every_topic_states_what_f3_does_with_it(topic):
    html = read(f"atlas-{topic}.html")
    m = re.search(r'<section class="card at-f3" data-f3="(model|withheld|none)"', html)
    assert m and m.group(1) == F3_STATE[topic], topic
    if m.group(1) == "none":
        assert "F3 does not model this" in html
    for c in re.findall(r'href="#(s-[a-z0-9-]+)"', html):                           # reading 4
        assert f'id="{c}"' in html, (topic, c)
    assert re.findall(r'<li id="s-[a-z0-9-]+"><a href="https?://', html), topic


def test_no_withheld_series_is_drawn_or_tabulated():
    d = data()
    r = d["runs"]["central|central|1"]
    for name in PAGES:
        html = read(name)
        for key in ("e_dc", "compute_stock", "effective_compute", "gwp"):
            assert key not in html, (name, key)
        for v in (r["e_dc_demand"][5], r["gwp"][5] / 1e12):                          # the 2030 values of two withheld or undrawn series
            assert f"{v:,.0f}" not in html, (name, v)
    energy = read("atlas-energy.html")
    assert "withheld" in energy and 'href="limitations.html#status-ai"' in energy


def test_energy_page_shows_f3_warming_from_the_data_file_with_its_notice():
    d = data()
    html = read("atlas-energy.html")
    y, c = d["years"], d["climate"]
    for yr in (2030, 2050, 2100):
        i = y.index(yr)
        assert f'{c["warming"][i]:.1f} K' in html and f'{c["warming_p05"][i]:.1f} to {c["warming_p95"][i]:.1f}' in html, yr
    assert "A2.1" in html and "0.04 to 0.07 K" in html and "prescribed" in html     # D-030
    assert "841" in html and "not a forecast" in html
    for o in ("low", "central", "high"):
        assert f'{100 * d["runs"]["central|" + o + "|1"]["damage_fraction"][y.index(2100)]:.1f}%' in html, o
    assert "not the upper end of the literature" in html                              # D-007, wherever the high option appears


def test_work_page_shows_the_automated_fraction_with_the_s3_notice():
    d = data()
    html = read("atlas-work.html")
    y = d["years"]
    for s in ("low", "central", "race"):
        for yr in (2030, 2040):
            assert f'{100 * d["runs"][s + "|central|1"]["frac_automated"][y.index(yr)]:.0f}%' in html, (s, yr)
    assert "unvalidated against GATE after about 2027" in html and "does not reproduce GATE" in html      # D-029
    assert "not a forecast" in html


def test_land_page_shows_world3_resources_and_says_forest_clearing_is_unsupported():
    d = data()
    html = read("atlas-land.html")
    w = d["world3"]
    run = w["runs"][w["standard"] + "|off"]
    for yr in (2025, 2050, 2100):
        assert f'{100 * run["nrfr"][w["years"].index(yr)]:.0f}%' in html, yr
    assert "A3.4b" in html
    assert "no sourced figure for forest clearing" in html.lower()


def test_the_hub_lists_every_topic_with_its_f3_state():
    html = read("atlas.html")
    for t in TOPICS:
        assert f'href="atlas-{t}.html"' in html, t
    assert html.count('class="at-state model"') == 3 and html.count('class="at-state none"') == 8
    assert 'href="ai.html"' in html and 'href="limitations.html"' in html
