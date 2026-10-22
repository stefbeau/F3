"""Explorer v0.2 stage 2 (D-056): the story front door (site/index.html). Structure and honesty checks on the generated markup; the numbers are checked in
tests/test_site_v02_core.py and live in a browser (see docs/site-explorer.md)."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"


def story() -> str:
    return (SITE / "index.html").read_text(encoding="utf-8")


def test_four_chapters_each_with_a_finding_title_one_chart_and_one_control():
    html = story()
    for n in (1, 2, 3, 4):
        sec = re.search(rf'<section class="chapter card" id="ch{n}".*?</section>', html, re.S)
        assert sec, n
        s = sec.group(0)
        assert f'id="ch{n}_h" class="finding"' in s, n                                  # the finding title (the script writes it from the data)
        assert len(re.findall(r'class="seg"', s)) == 1, n                               # one control
        if n < 4:
            assert len(re.findall(r'id="ch_s\d"', s)) == 1, n                           # one chart
    assert len(re.findall(r'<section class="chapter card"', html)) == 4


def test_step_indicator_links_the_four_chapters_in_order():
    nav = re.search(r'<nav class="steps".*?</nav>', story(), re.S).group(0)
    assert re.findall(r'href="#(ch\d)"', nav) == ["ch1", "ch2", "ch3", "ch4"]
    assert 'aria-label="Story steps' in nav


def test_banner_and_status_badges_stay_visible():
    html = story()
    assert "Public draft, published 2026-10-21. Conditional scenarios, not forecasts." in html
    assert 'class="badge red" href="limitations.html#status-ai"' in html                 # chapter 3: levels flagged red
    assert 'class="badge amber" href="limitations.html#status-world3"' in html
    assert 'class="badge amber" href="limitations.html#status-climate"' in html
    ch2 = re.search(r'id="ch2".*?</section>', html, re.S).group(0).lower()
    assert "high is not the upper end of the literature" in ch2 and "a2.1" in ch2 and "not compared with worlddynamics.jl" in ch2
    ch3 = re.search(r'id="ch3".*?</section>', html, re.S).group(0)
    assert "A1.3" in ch3 and "withheld" in ch3 and 'class="withheld"' in ch3 and "automation" in ch3.lower()
    assert 'id="ch_compute"' not in html and 'id="ch_edc"' not in html
    assert html.count('class="rf"') == 3 and 'id="readfirst"' in html


def test_message_without_interaction_a_static_headline_and_a_generated_line():
    html = story()
    assert re.search(r"<h1>.*turns down.*</h1>", html) and 'id="hero_line"' in html
    for n in (1, 2, 3, 4):                                                               # static fallback titles exist even before the script runs
        assert re.search(rf'id="ch{n}_h" class="finding">[^<]{{12,}}<', html), n


def test_links_vocabulary_solid_dashed_dotted_and_seven_links():
    import json
    html = story()
    data = json.loads(re.search(r'<script type="application/json" id="linksdata">(.*?)</script>', html, re.S).group(1))
    assert len(data["links"]) == 7 and [l["n"] for l in data["links"]] == list(range(1, 8))
    built = {l["id"] for l in data["links"] if l["status"] == "built"}
    assert built == {"fair-warming-to-world3-output", "fair-warming-to-s3-damage"}
    assert {l["status"] for l in data["links"]} == {"built", "not-built", "withheld"}
    assert [n["id"] for n in data["nodes"]] == ["warming", "world3", "s3", "dc", "emissions"]
    # the story strip and the v0.1 loop diagram agree on which links are built
    ex = (SITE / "explorer.html").read_text(encoding="utf-8")
    loop_built = set(re.findall(r'data-link="([^"]+)" data-built="yes"', ex))
    assert loop_built == built


def test_social_module_is_not_on_the_story_page():
    visible = re.sub(r"<script.*?</script>|<style.*?</style>", "", story(), flags=re.S)
    assert not re.search(r"\bS7\b|s7_social|social module|inequality index", visible)


def test_scripts_and_data_are_local_files_no_network():
    html = story()
    srcs = re.findall(r'<script src="([^"]+)"', html) + re.findall(r'<link rel="stylesheet" href="([^"]+)"', html)
    assert srcs and all(not s.startswith(("http:", "https:", "//")) for s in srcs), srcs
    for s in srcs:
        assert (SITE / s).exists(), s
    assert not re.search(r"https?://[^\"' ]+\.(js|css|woff2?)", html)
