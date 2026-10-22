"""Explorer v0.2 stage 5 (D-056): the connections map as an interface. The map, its numbered buttons and the list are generated from site_src/links.py, so these tests check the
generated markup: exactly the built links are solid, every not-built link is dashed, the withheld link is dotted, every link has a numbered button and a list entry, text
alternatives exist, and the inspector's effect numbers are computed from the data. Keyboard operation was tested in a real browser (docs/site-explorer.md)."""
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


def page() -> str:
    return (SITE / "connections.html").read_text(encoding="utf-8")


def linkdata() -> dict:
    return json.loads(re.search(r'<script type="application/json" id="linksdata">(.*?)</script>', page(), re.S).group(1))


def test_exactly_the_built_links_are_solid_not_built_dashed_withheld_dotted():
    html = page()
    paths = re.findall(r'<path data-link="([^"]+)" data-built="(yes|no|withheld)"[^>]*>', html)
    assert len(paths) == 7
    tags = {m.group(1): m.group(0) for m in re.finditer(r'<path data-link="([^"]+)"[^>]*>', html)}
    built = {link for link, b in paths if b == "yes"}
    assert built == {"fair-warming-to-world3-output", "fair-warming-to-s3-damage"}
    for link, b in paths:
        tag = tags[link]
        if b == "yes":
            assert "stroke-dasharray" not in tag, tag
        elif b == "no":
            assert 'stroke-dasharray="7 5"' in tag, tag
        else:
            assert 'stroke-dasharray="1 6"' in tag and link == "s3-compute-to-data-centre-electricity", tag
    assert {entry["id"] for entry in linkdata()["links"] if entry["status"] == "built"} == built        # the JSON the inspector reads agrees with the drawing


def test_seven_numbered_buttons_nodes_and_list_entries():
    html = page()
    assert [int(n) for n in re.findall(r'<button type="button" class="nbtn [a-z-]+" data-n="(\d)"', html)] == list(range(1, 8))
    for label in re.findall(r'class="nbtn [^"]*" data-n="\d" style="[^"]*" aria-label="([^"]+)"', html):
        assert re.match(r"Link \d: .+ to .+\. (Built and tested|Not built|Built, outputs withheld)\.", label), label
    assert len(re.findall(r'<li class="li ', html)) == 7 and len(re.findall(r'class="lbtn"', html)) == 7
    names = re.findall(r'<div class="mnode [a-z-]+" style="[^"]*"><strong>([^<]+)</strong>', html)
    assert names == ["Warming", "World3", "AI economy S3", "Data centres", "Emissions"]
    assert "output withheld" in html.lower()


def test_nodes_are_absolutely_positioned_and_the_list_replaces_the_map_below_900px():
    css = (SRC / "style.css").read_text(encoding="utf-8")
    assert ".mnode{position:absolute" in css and ".nbtn{position:absolute" in css
    assert "@media (max-width:899px){.conn{display:none}.linklist{display:block}" in css
    assert ".linklist{display:none" in css


def test_map_has_a_text_alternative_legend_and_the_status_vocabulary():
    html = page()
    assert 'role="group" aria-label="Map of the seven links' in html
    for word in ("Solid: built and tested", "Dotted: built, outputs withheld", "Dashed: not built"):
        assert word in html
    assert 'aria-live="polite"' in html and 'id="inspector"' in html


def test_every_link_has_inspector_content_met_failed_and_not_compared():
    links = linkdata()["links"]
    for entry in links:
        assert entry["what"] and entry["label"] and entry["methods"]
        assert {"met", "failed", "notcompared"} <= set(entry), entry["id"]
        if entry["status"] == "built":
            assert entry["met"] and entry["notcompared"], entry["id"]                      # a built link states what was tested and what was not compared
        assert entry["status"] in ("built", "not-built", "withheld")
    by = {entry["id"]: entry for entry in links}
    assert by["fair-warming-to-world3-output"]["effect"] == "w3damage" and by["fair-warming-to-s3-damage"]["effect"] == "s3damage"
    assert all(entry["effect"] is None for entry in links if entry["status"] != "built")   # no effect numbers for links that are not built or withheld
    w3 = by["fair-warming-to-world3-output"]
    assert any("WorldDynamics.jl" in t for t in w3["notcompared"]) and any("upper end of the literature" in t for t in by["fair-warming-to-s3-damage"]["notcompared"])
    assert any("A1.3" in t for t in by["fair-warming-to-s3-damage"]["failed"]) and any("A2.1" in t for t in w3["failed"])
    assert any("B1" in t for t in by["s3-compute-to-data-centre-electricity"]["failed"])


def test_methods_links_resolve_to_anchors_that_exist():
    for entry in linkdata()["links"]:
        target, _, anchor = entry["methods"].partition("#")
        html = (SITE / target).read_text(encoding="utf-8")
        assert not anchor or f'id="{anchor}"' in html, entry["methods"]


@pytest.mark.skipif(NODE is None or not DATA.exists(), reason="Node.js or data not available")
def test_effect_numbers_are_computed_from_the_data(tmp_path):
    d = json.loads(DATA.read_text(encoding="utf-8"))
    prog = ("const IN=" + json.dumps(linkdata()["links"]) + f";const F3=require({json.dumps(str(SRC / 'core.js'))});"
            "const D=" + json.dumps(d) + ";"                         # the data file is strict JSON (null = no value), so this literal is valid JSON as well as valid JavaScript
            "process.stdout.write(JSON.stringify([F3.effectTable('w3damage',D),F3.effectTable('s3damage',D),F3.effectTable(null,D),F3.linksFinding(IN)]));")
    f = tmp_path / "e.js"
    f.write_text(prog, encoding="utf-8")
    w3, s3, none, finding = json.loads(subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)
    std = d["world3"]["standard"]
    for row in w3["rows"]:
        run, off = d["world3"]["runs"][f"{std}|{row[0]}"], d["world3"]["runs"][f"{std}|off"]
        assert f"{(run['io'][-1] / off['io'][-1] - 1) * 100:+.1f}%" == row[2] and f"{(run['pop'][-1] / off['pop'][-1] - 1) * 100:+.1f}%" == row[3]
        assert row[1] == f"{d['world3']['damage']['coeff_pct_per_K2'][row[0]]:.3f}"
    for row in s3["rows"]:
        assert row[2] == f"{d['runs'][f'central|{row[0]}|1']['damage_fraction'][-1] * 100:.1f}%"
    assert f"{d['climate']['warming'][-1]:.2f} K" in w3["note"] and none is None
    assert finding.startswith("2 of 7 links") and "1 more is built with outputs withheld" in finding and "4 are not built" in finding


def test_connections_script_holds_no_model_numbers_and_the_social_module_is_absent():
    src = (SRC / "connections.js").read_text(encoding="utf-8")
    assert not re.search(r"\d+\.\d{2,}", src)
    visible = re.sub(r"<script.*?</script>", "", page(), flags=re.S)
    assert not re.search(r"\bS7\b|social module|inequality index", visible)
