"""Explorer (D-070, Provisional (delegated)): the range chart ("tornado") on the Explorer and the dumbbell on Compare.

Written BEFORE the chart code. Readings: docs/site-tornado-dumbbell.md (R-T1 to R-T6, R-D1 to R-D4). The pure functions of site_src/core.js run in Node on the
committed data and on synthetic data; every expected number is recomputed here in Python from site/data/explorer.json. Structure checks read the sources and the
generated pages. Nothing here relaxes any earlier test."""
from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "site_src"
SITE = REPO / "site"
CORE = SRC / "core.js"
DATA = SITE / "data" / "explorer.json"
NODE = shutil.which("node")

need_data = pytest.mark.skipif(not DATA.exists(), reason="site/data/explorer.json not present (build the site first)")
need_node = pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH")

SERIES = {"pop": "pop", "io": "io", "nrfr": "nrfr", "ppolx": "ppolx"}
STATES = ["off", "low", "central", "high"]


def world3() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))["world3"]


def node(expr: str, tmp_path: Path, payload: dict = None):
    f = tmp_path / "in.json"
    f.write_text(json.dumps(payload or {}), encoding="utf-8")
    prog = (f"const F3=require({json.dumps(str(CORE))});const IN=JSON.parse(require('fs').readFileSync({json.dumps(str(f))},'utf8'));\n" +
            "process.stdout.write(JSON.stringify((function(){" + expr + "})()));")
    p = tmp_path / "t.js"
    p.write_text(prog, encoding="utf-8")
    return json.loads(subprocess.run([NODE, str(p)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)


def key(levers, damage) -> str:
    return "|".join(map(str, levers)) + "|" + damage


def expected_rows(W: dict, levers, damage, series):
    """The ranges, computed independently of core.js: one setting at a time, the others as chosen."""
    out = []
    for i, lev in enumerate(W["levers"]):
        vals = []
        for j in range(len(lev["values"])):
            lv = list(levers)
            lv[i] = j
            vals.append(W["runs"][key(lv, damage)][series][-1])
        out.append((lev["param"], vals))
    out.append(("damage", [W["runs"][key(levers, s)][series][-1] for s in STATES]))
    return out


def tornado(tmp_path, W, levers, damage, metric):
    return node("return F3.tornadoSpec(IN.W, IN.levers, IN.damage, IN.metric)", tmp_path, {"W": W, "levers": levers, "damage": damage, "metric": metric})


# ------------------------------------------------------------------------------------------------------ range chart
@need_data
@need_node
@pytest.mark.parametrize("levers,damage", [([1, 0, 0], "off"), ([2, 1, 1], "central")])
@pytest.mark.parametrize("metric", ["pop", "io", "nrfr", "ppolx"])
def test_rt1_rt3_bar_ends_are_the_min_and_max_of_one_setting_at_a_time(tmp_path, levers, damage, metric):
    W = world3()
    spec = tornado(tmp_path, W, levers, damage, metric)
    here = W["runs"][key(levers, damage)][SERIES[metric]][-1]
    assert spec["kind"] == "tornado" and spec["here"] == here and spec["year"] == W["years"][-1]
    by = {r["id"]: r for r in spec["rows"]}
    exp = dict(expected_rows(W, levers, damage, SERIES[metric]))
    assert set(by) == set(exp)
    for rid, vals in exp.items():
        r = by[rid]
        assert r["lo"]["v"] == min(vals) and r["hi"]["v"] == max(vals), rid
        assert r["swing"] == pytest.approx(max(vals) - min(vals), rel=1e-12, abs=0)
        assert r["lo"]["v"] <= here <= r["hi"]["v"], rid                               # the chosen run is one of the settings, so it is inside every bar
        assert len(r["points"]) == len(vals) and sum(1 for p in r["points"] if p["chosen"]) == 1


@need_data
@need_node
def test_rt2_rows_sorted_widest_first_and_the_title_names_the_first_row(tmp_path):
    W = world3()
    spec = tornado(tmp_path, W, [1, 0, 0], "off", "pop")
    swings = [r["swing"] for r in spec["rows"]]
    assert swings == sorted(swings, reverse=True)
    top = spec["rows"][0]
    human = node("return [F3.human(IN.a), F3.human(IN.b)]", tmp_path, {"a": top["lo"]["v"], "b": top["hi"]["v"]})
    assert top["label"].lower()[:20] in spec["title"].lower()
    assert human[0] in spec["title"] and human[1] in spec["title"] and str(W["years"][-1]) in spec["title"]
    assert spec["title"] in spec["summary"]


@need_node
def test_rt2_equal_widths_keep_the_order_of_the_data_file(tmp_path):
    W = synthetic(lambda lv, s: 10.0 + lv[0] + lv[1] + lv[2] + (0 if s == "off" else 1))          # every lever has width 2, damage width 1
    spec = tornado(tmp_path, W, [0, 0, 0], "off", "pop")
    assert [r["id"] for r in spec["rows"]] == ["nri", "lyf2", "ppgf21", "damage"]


def synthetic(value) -> dict:
    """A small World3-shaped data set: 3 levers x 3 values x 4 damage states, two years; value(levers, damage) gives the last-year value of every series."""
    levers = [{"param": p, "label": lab, "values": [1, 2, 3], "value_labels": ["one", "two", "three"], "standard_index": 0}
              for p, lab in (("nri", "Lever N"), ("lyf2", "Lever Y"), ("ppgf21", "Lever P"))]
    runs = {}
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for s in STATES:
                    v = value([a, b, c], s)
                    runs[key([a, b, c], s)] = {k: [1.0, v] for k in ("pop", "io", "ic", "al", "nrfr", "ppolx")}
    return {"years": [2000, 2050], "runs": runs, "levers": levers, "damage_states": STATES, "standard": "0|0|0"}


@need_data
@need_node
def test_rt5_synthetic_data_gives_a_different_title_without_the_real_values(tmp_path):
    W = world3()
    real = tornado(tmp_path, W, [1, 0, 0], "off", "pop")
    syn = tornado(tmp_path, synthetic(lambda lv, s: 1234.0 + 100 * lv[1] + 7 * lv[0]), [0, 0, 0], "off", "pop")
    assert syn["rows"][0]["id"] == "lyf2" and syn["rows"][0]["swing"] == 200
    assert syn["title"] != real["title"] and "2050" in syn["title"] and "Lever Y".lower() in syn["title"].lower()
    for r in real["rows"]:
        for end in ("lo", "hi"):
            h = node("return F3.human(IN.v)", tmp_path, {"v": r[end]["v"]})
            assert h not in syn["title"], h


@need_node
def test_rt4_null_is_no_value_never_zero(tmp_path):
    W = synthetic(lambda lv, s: 50.0 + 10 * lv[0] + lv[2])
    for b in range(3):                                                                # lever Y: only the chosen value is known, the two others are missing
        for s in STATES:
            if b != 0:
                W["runs"][key([0, b, 0], s)]["pop"][-1] = None
    W["runs"][key([2, 0, 0], "off")]["pop"][-1] = None                                # lever N loses its highest value: the range is over the two that remain
    spec = tornado(tmp_path, W, [0, 0, 0], "off", "pop")
    by = {r["id"]: r for r in spec["rows"]}
    assert by["lyf2"]["swing"] is None and spec["rows"][-1]["id"] == "lyf2"            # fewer than two values: no width, listed last
    assert by["nri"]["lo"]["v"] == 50.0 and by["nri"]["hi"]["v"] == 60.0               # the missing 70 is left out, and 0 never appears as an end
    assert all(r["lo"] is None or r["lo"]["v"] != 0 for r in spec["rows"])
    assert "no value" in json.dumps(spec["table"])
    flat = tornado(tmp_path, synthetic(lambda lv, s: 5.0), [0, 0, 0], "off", "pop")
    assert all(r["swing"] == 0 for r in flat["rows"])
    assert re.search(r"no(ne| setting).*chang", flat["title"].lower()), flat["title"]


@need_data
@need_node
def test_rt6_the_mandatory_labels_are_in_the_caveat_and_the_text_alternative(tmp_path):
    spec = tornado(tmp_path, world3(), [1, 0, 0], "off", "pop")
    for text in (spec["caveat"], spec["summary"]):
        low = text.lower()
        for phrase in ("one setting", "combin", "not an uncertainty range", "not a sensitivity analysis", "not the upper end of the literature", "level-of-output",
                       "not compared with worlddynamics.jl", "no health or yield effect of warming", "not a forecast"):
            assert phrase in low, phrase
    assert spec["assume"]["href"] == "methods.html#grids"
    on = tornado(tmp_path, world3(), [1, 0, 0], "central", "pop")
    assert on["assume"]["href"] == "methods.html#coupling"                             # damage on in the chosen run: the assumptions are the coupling's


@need_data
@need_node
def test_tornado_table_and_csv_come_from_the_rows(tmp_path):
    spec = tornado(tmp_path, world3(), [1, 0, 0], "off", "io")
    assert len(spec["table"]["rows"]) == len(spec["rows"]) and len(spec["csv"]["rows"]) == len(spec["rows"])
    for r, raw in zip(spec["rows"], spec["csv"]["rows"]):
        assert r["lo"]["v"] in raw and r["hi"]["v"] in raw and spec["here"] in raw       # raw numbers in the CSV, not formatted text
    assert spec["file"].startswith("f3-") and spec["unit"]


# ------------------------------------------------------------------------------------------------------ dumbbell
def compare(tmp_path, W, a, b):
    base = W["runs"][W["standard"] + "|off"]
    return node("var rows=F3.compareRows(IN.y, IN.base, IN.a, IN.b, null);return {rows:rows, spec:F3.dumbbellSpec(IN.y, rows, {a:'Scenario A',b:'Scenario B'}, {a:'first',b:'second'}, 'CAVEAT TEXT.')}",
                tmp_path, {"y": W["years"], "base": base, "a": a, "b": b})


@need_data
@need_node
def test_rd1_rd2_markers_gap_and_order_come_from_compare_rows(tmp_path):
    W = world3()
    out = compare(tmp_path, W, W["runs"][key([1, 0, 0], "central")], W["runs"][key([2, 1, 1], "central")])
    spec, rows = out["spec"], {r["id"]: r for r in out["rows"]}
    assert spec["kind"] == "dumbbell" and len(spec["rows"]) == sum(1 for r in out["rows"] if not r["identical"])
    for r in spec["rows"]:
        src = rows[r["id"]]
        assert r["a"] == pytest.approx(src["dA"] * 100, rel=1e-12) and r["b"] == pytest.approx(src["dB"] * 100, rel=1e-12)
        assert r["gap"] == pytest.approx((src["dB"] - src["dA"]) * 100, rel=1e-9)
    gaps = [abs(r["gap"]) for r in spec["rows"]]
    assert gaps == sorted(gaps, reverse=True)
    top = spec["rows"][0]
    assert top["label"].lower() in spec["title"].lower() and f"{abs(top['gap']):.1f}" in spec["title"] and str(W["years"][-1]) in spec["title"]
    assert "CAVEAT TEXT." in spec["caveat"] and "first" in spec["summary"] and "second" in spec["summary"]
    assert spec["assume"]["href"].startswith("methods.html#")


@need_data
@need_node
def test_rd3_a_equal_to_b_says_so(tmp_path):
    W = world3()
    run = W["runs"][key([2, 1, 1], "central")]
    spec = compare(tmp_path, W, run, run)["spec"]
    assert all(r["gap"] == 0 for r in spec["rows"])
    assert re.search(r"coincide|same", spec["title"].lower()), spec["title"]
    base = W["runs"][W["standard"] + "|off"]
    none = compare(tmp_path, W, base, base)["spec"]
    assert none["rows"] == [] and "standard run" in none["title"].lower()


@need_data
@need_node
def test_rd4_null_is_no_value_and_goes_last(tmp_path):
    W = world3()
    a, b = copy.deepcopy(W["runs"][key([1, 0, 0], "central")]), copy.deepcopy(W["runs"][key([2, 1, 1], "central")])
    b["pop"][-1] = None
    spec = compare(tmp_path, W, a, b)["spec"]
    last = spec["rows"][-1]
    assert last["id"] == "pop" and last["gap"] is None and last["b"] is None and last["a"] is not None
    assert "no value" in json.dumps(spec["table"])
    assert all(r["gap"] is not None for r in spec["rows"][:-1])


# ------------------------------------------------------------------------------------------------------ structure: sources and generated pages
def charts() -> str:
    return (SRC / "charts.js").read_text(encoding="utf-8")


def fn(src: str, name: str) -> str:
    i = src.index("function " + name + "(")
    j = src.find("\n  function ", i + 10)
    return src[i:j if j > 0 else len(src)]


def test_chart_functions_exist_draw_a_reference_line_and_never_read_null_as_zero():
    src = charts()
    for name in ("tornadoChart", "dumbbellChart"):
        body = fn(src, name)
        assert "F3.isNum" in body and "F3.NA" in body, name                             # a missing value is tested and written as "no value"
        assert "isFinite(" not in body.replace("F3.isNum", ""), name
        assert re.search(r'stroke-width="2\.[0-9]"', body), name                        # the chosen-run line or the zero line is drawn thicker than the grid
        assert "role=\"img\"" in body and "<title>" in body and "<desc>" in body, name
        for m in re.finditer(r'font-size="?\'?\s*\+?\s*([0-9.]+)', body):
            assert float(m.group(1)) >= 13, (name, m.group(0))
    assert "tornadoChart: tornadoChart" in src and "dumbbellChart: dumbbellChart" in src


def test_dumbbell_marks_differ_by_shape_and_letter_not_only_by_colour():
    body = fn(charts(), "dumbbellChart")
    assert "<circle" in body and "<rect" in body                                        # A is a circle, B is a square
    assert "sc.a" in body and "sc.b" in body and "sc.aT" in body and "sc.bT" in body      # the scenario colours of design-guidelines 4.1, with their text variants


def test_csv_download_handles_the_new_kinds():
    src = charts()
    body = fn(src, "csvFor")
    assert "s.csv" in body and "conditional scenario, not a forecast" in body


def test_pages_carry_the_new_cards_and_the_scripts_draw_them_from_core():
    exp, cmp_ = (SITE / "explorer.html").read_text(encoding="utf-8"), (SITE / "compare.html").read_text(encoding="utf-8")
    det = exp[exp.index('<details id="details">'):exp.index("</details>", exp.index('id="tb_tests"'))]
    assert 'id="ch_tornado"' in det and 'id="tornado_seg"' in det                       # under Details, with a measure selector
    assert det.index('id="ch_tornado"') > det.index('id="ch_pol"')                      # after the World3 charts it summarises
    assert 'id="ch_dumb"' in cmp_ and cmp_.index('id="ch_dumb"') > cmp_.index('id="ch_bars"') and cmp_.index('id="ch_dumb"') < cmp_.index('id="tb_delta"')
    dash, comp = (SRC / "dashboard.js").read_text(encoding="utf-8"), (SRC / "compare.js").read_text(encoding="utf-8")
    assert "C.tornadoChart(" in dash and "F3.tornadoSpec(" in dash
    assert "C.dumbbellChart(" in comp and "F3.dumbbellSpec(" in comp
    assert "C.barChart(" in comp and 'id="ch_bars"' in cmp_                             # the bars stay


def test_the_visible_text_says_what_the_range_chart_is_not():
    exp = (SITE / "explorer.html").read_text(encoding="utf-8")
    i = exp.index('id="ch_tornado"')
    near = re.sub(r"<[^>]+>", " ", exp[i - 1500:i + 1500]).lower()
    for phrase in ("one setting at a time", "not an uncertainty range", "not a sensitivity analysis", "compare"):
        assert phrase in near, phrase
