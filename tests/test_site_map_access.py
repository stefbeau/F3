"""Explorer v0.2b, warming map accessibility (2026-10-22): the map is ONE tab stop (roving tabindex), arrow keys move between regions by spatial neighbour, Home and End jump
to the first and last region in reading order, Escape leaves, and a "View as table" button toggles a visible table of every region sorted by value, highest first, with regions
that have no value listed last as "no value" and never as zero. The pure parts (neighbour choice, reading order, table rows) are run in Node on the committed data and on small
synthetic maps; the markup the script builds is pinned in the script source (the live keyboard checks are in docs/site-explorer.md)."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "site_src"
CORE = SRC / "core.js"
DATA = REPO / "site" / "data" / "explorer.json"
NODE = shutil.which("node")

need_data = pytest.mark.skipif(not DATA.exists(), reason="site/data/explorer.json not present (build the site first)")
need_node = pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH")


def node(expr: str, tmp_path: Path, payload: dict = None):
    prog = (f"const F3=require({json.dumps(str(CORE))});const IN=" + json.dumps(payload or {}) + ";\n" +
            "process.stdout.write(JSON.stringify((function(){" + expr + "})()));")
    f = tmp_path / "t.js"
    f.write_text(prog, encoding="utf-8")
    return json.loads(subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)


def box(rid, lon, lat, c=1.0):
    """a 10 x 10 degree square region centred on (lon, lat)"""
    return {"id": rid, "name": "Region " + rid, "type": "Land", "c": c,
            "polys": [[[[lon - 5, lat - 5], [lon + 5, lat - 5], [lon + 5, lat + 5], [lon - 5, lat + 5]]]]}


GRID = [box("A", 0, 0), box("B", 30, 0), box("C", 60, 0), box("D", 30, 30), box("E", 30, -30)]


# ------------------------------------------------------------------------------------------------------ neighbour choice and order
@need_node
def test_neighbour_follows_the_arrow_direction_on_a_synthetic_map(tmp_path):
    out = node("return ['left','right','up','down'].map(function(d){return F3.mapNeighbour(IN.R,'B',d)})", tmp_path, {"R": GRID})
    assert out == ["A", "C", "D", "E"]
    edge = node("return [F3.mapNeighbour(IN.R,'A','left'), F3.mapNeighbour(IN.R,'D','up'), F3.mapNeighbour(IN.R,'D','down'), F3.mapNeighbour(IN.R,'E','down')]", tmp_path, {"R": GRID})
    assert edge == [None, None, "B", None]                                         # nothing in that direction: the arrow stays put (the page keeps focus where it is)


@need_node
def test_reading_order_is_north_to_south_then_west_to_east(tmp_path):
    assert node("return F3.mapOrder(IN.R)", tmp_path, {"R": GRID}) == ["D", "A", "B", "C", "E"]


@need_data
@need_node
def test_every_real_region_is_reachable_by_arrow_keys_from_the_first_one(tmp_path):
    regs = json.loads(DATA.read_text(encoding="utf-8"))["warming_map"]["regions"]
    out = node("""var ids=F3.mapOrder(IN.R), seen={}, todo=[ids[0]]; seen[ids[0]]=1;
      while(todo.length){var id=todo.pop(); ['left','right','up','down'].forEach(function(d){var n=F3.mapNeighbour(IN.R,id,d); if(n && n!==id && !seen[n]){seen[n]=1; todo.push(n);}});}
      return {order:ids, reached:Object.keys(seen).length, never_self:IN.R.every(function(r){return ['left','right','up','down'].every(function(d){return F3.mapNeighbour(IN.R,r.id,d)!==r.id;});})};""",
               tmp_path, {"R": regs})
    assert sorted(out["order"]) == sorted(r["id"] for r in regs) and len(set(out["order"])) == len(regs)
    assert out["reached"] == len(regs), "a region with no arrow-key route would be unreachable from the keyboard"
    assert out["never_self"]


# ------------------------------------------------------------------------------------------------------ the table
@need_node
def test_table_sorts_descending_with_no_value_last_and_never_zero(tmp_path):
    regs = [box("A", 0, 0, 0.5), box("B", 30, 0, 2.0), box("C", 60, 0, None), box("D", 30, 30, 1.0)]
    t = node("return F3.mapValueTable({regions:IN.R}, IN.g, 2050)", tmp_path, {"R": regs, "g": 2.0})
    assert [r["id"] for r in t["rows"]] == ["B", "D", "A", "C"]
    assert [r["value"] for r in t["rows"]] == [4.0, 2.0, 1.0, None]
    assert t["missing"] == 1 and "1 with no value are listed last" in t["caption"] and "2050" in t["caption"] and "4 regions" in t["caption"]
    none = node("return F3.mapValueTable({regions:IN.R}, null, 2050)", tmp_path, {"R": regs})
    assert all(r["value"] is None for r in none["rows"]) and none["missing"] == 4         # a missing global value gives no value everywhere, not 0 K


@need_data
@need_node
def test_table_on_the_real_data_has_every_region_highest_first_and_a_caption_from_the_data(tmp_path):
    d = json.loads(DATA.read_text(encoding="utf-8"))
    M, yrs, w = d["warming_map"], d["years"], d["climate"]["warming"]
    y = yrs[-1]
    t = node("return F3.mapValueTable(IN.M, IN.g, IN.y)", tmp_path, {"M": M, "g": w[-1], "y": y})
    vals = [r["value"] for r in t["rows"]]
    assert len(t["rows"]) == len(M["regions"]) and vals == sorted(vals, reverse=True)
    assert vals[0] == pytest.approx(max(r["c"] for r in M["regions"]) * w[-1])
    assert t["caption"].startswith(f"Pattern-scaled warming in {y}, all {len(M['regions'])} regions, highest first")
    assert "K above 1850-1900" in t["unit"]


# ------------------------------------------------------------------------------------------------------ markup the script builds
def charts() -> str:
    s = (SRC / "charts.js").read_text(encoding="utf-8")
    return s[s.index("function regionMap("):s.index("function mapRead(")]


def test_map_is_one_tab_stop_with_roving_tabindex_and_arrow_home_end_escape_keys():
    seg = charts()
    assert seg.count("""tabindex="' + (r.id === c.tab ? "0" : "-1")""") == 1              # one region at 0, every other at -1 when the regions are built
    assert """setAttribute("tabindex", q === p ? "0" : "-1")""" in seg and 'c.plot.removeAttribute("tabindex")' in seg
    for key in ("ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", '"Home"', '"End"', '"Escape"'):
        assert key in seg, key
    assert "F3.mapNeighbour(" in seg and "F3.mapOrder(" in seg
    assert '"mouseenter"' in seg and 'addEventListener("focus"' in seg                      # hover and focus both show the readout
    assert 'class="ring"' in seg and "non-scaling-stroke" in seg                             # a visible focus ring drawn on top of the regions


def test_view_as_table_is_a_real_button_with_aria_expanded_controlling_a_table():
    seg = charts()
    assert '<button type="button" class="mapbtn"' in seg and 'aria-expanded="false"' in seg and "aria-controls=" in seg and "View as table" in seg
    assert 'setAttribute("aria-expanded", String(open))' in seg
    assert "<table" in seg and "<caption>" in seg and 'scope="col"' in seg and "F3.mapValueTable(" in seg and "F3.NA" in seg
    assert 'tabindex="0" hidden' in seg                                                      # the table box scrolls and is reachable from the keyboard when open


def test_the_map_container_ships_once_and_the_new_styles_keep_13px_text():
    html = (REPO / "site" / "explorer.html").read_text(encoding="utf-8")
    assert html.count('id="ch_map"') == 1
    css = (SRC / "style.css").read_text(encoding="utf-8")
    block = "\n".join(ln for ln in css.splitlines() if ".mapbtn" in ln or ".maptable" in ln or ".maptblbox" in ln)
    assert block and ".maptable caption" in block and ".maptblbox:focus-visible" in block
    sizes = re.findall(r"font-size:([\d.]+)rem", block)
    assert sizes and all(float(x) * 16 >= 13 for x in sizes), sizes
    assert "overflow:auto" in block and "max-width:100%" in block                           # scrolls inside its own box; the page itself never scrolls sideways
