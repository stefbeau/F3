"""Explorer v0.2 (D-056): the data file is strict JSON and null means "no value", never zero.

Readings written before the code: (1) site/data/explorer.json parses with Python's json module with parse_constant raising (no NaN, Infinity or -Infinity token anywhere) and
with Node's JSON.parse; (2) the generator turns NaN and infinity into null and refuses to write a NaN (allow_nan=False); (3) every function of core.js that reads a data
value treats null as missing: formats say "no value", a peak or a first-reach skips it, a change against a missing value is missing, a CSV cell is empty, a headline never
shows a zero in its place; (4) isFinite is used only inside core.js's isNum (isFinite(null) is true in JavaScript), so no page script can read null as 0."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "site_src"
CORE = SRC / "core.js"
DATA = REPO / "site" / "data" / "explorer.json"
NODE = shutil.which("node")
need_node = pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH")
need_data = pytest.mark.skipif(not DATA.exists(), reason="site/data/explorer.json not present (build the site first)")


def _refuse(token):
    raise ValueError("non-JSON constant in the data file: " + token)


@need_data
def test_data_file_parses_with_a_strict_json_parser():
    text = DATA.read_text(encoding="utf-8")
    d = json.loads(text, parse_constant=_refuse)
    assert d["world3"]["years"][0] == 1900 and d["years"][0] == 2025
    outside_strings = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)                                       # the null note in meta spells the words inside a string; only bare tokens matter
    assert not re.search(r"NaN|Infinity", outside_strings)


@need_data
@need_node
def test_data_file_parses_with_node_json_parse(tmp_path):
    f = tmp_path / "p.js"
    f.write_text("const d=JSON.parse(require('fs').readFileSync(" + json.dumps(str(DATA)) + ",'utf8'));process.stdout.write(JSON.stringify([d.years.length,Object.keys(d.runs).length,d.meta.null_means.length>0]));", encoding="utf-8")
    n_years, n_runs, note = json.loads(subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)
    assert n_years == 76 and n_runs >= 9 and note is True


@need_data
def test_the_former_nan_fields_are_null_and_say_what_null_means():
    d = json.loads(DATA.read_text(encoding="utf-8"), parse_constant=_refuse)
    nulls = [k for k, r in d["runs"].items() if r["dc_available"][0] is None]
    assert nulls, "dc_available's first year was NaN before the null rule; it must now be null"
    assert "never zero" in d["meta"]["null_means"]
    assert all(r["dc_available"][0] is None for r in d["runs"].values())                      # a missing value is null, not 0 and not a string


def test_generator_turns_nan_and_infinity_into_null_and_refuses_to_write_a_nan():
    sys.path.insert(0, str(SRC))
    sys.path.insert(0, str(REPO))
    import generate
    out = generate.strict({"a": [float("nan"), float("inf"), float("-inf"), 1.5, 0], "b": {"c": float("nan")}, "s": "NaN"})
    assert out == {"a": [None, None, None, 1.5, 0], "b": {"c": None}, "s": "NaN"}
    assert out["a"][4] == 0 and out["a"][4] is not None                                        # a real zero stays zero
    json.loads(generate.dumps(out), parse_constant=_refuse)
    with pytest.raises(ValueError):
        generate.dumps({"x": float("nan")})                                                    # a NaN that slipped past strict() would fail the build, not ship


def node(expr: str, tmp_path: Path, payload: dict = None):
    prog = (f"const F3=require({json.dumps(str(CORE))});const IN=" + json.dumps(payload or {}) + ";\n" +
            "process.stdout.write(JSON.stringify((function(){" + expr + "})()));")
    f = tmp_path / "t.js"
    f.write_text(prog, encoding="utf-8")
    return json.loads(subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)


@need_node
def test_formats_and_helpers_treat_null_as_no_value(tmp_path):
    out = node("return {h:F3.human(null),k:Object.keys(F3.FMT).map(function(k){return F3.FMT[k](null)}),r:F3.rel(null),s:F3.signedPct(null),sf:F3.signedFmt(null,'people'),"
               "chg:[F3.chg(null,1),F3.chg(1,null),F3.chg(1,0),F3.chg(2,1)],diff:F3.diff(null,1),scale:[F3.scale(null,100),F3.scale(0,100)],fx:[F3.fx(null,2),F3.fx(0,2)],"
               "isnum:[F3.isNum(null),F3.isNum(undefined),F3.isNum(NaN),F3.isNum(0),F3.isNum('1')]}", tmp_path)
    assert out["h"] == "no value" and set(out["k"]) == {"no value"} and out["r"] == out["s"] == out["sf"] == "no value"
    assert out["chg"] == [None, None, None, 1] and out["diff"] is None and out["scale"] == [None, 0] and out["fx"] == ["no value", "0.00"]
    assert out["isnum"] == [False, False, False, True, False]


@need_node
def test_series_helpers_skip_null_and_never_read_it_as_zero(tmp_path):
    out = node("var y=[2000,2001,2002,2003,2004];return {peak:F3.peakOf(y,[null,5,3,null,4]),none:F3.peakOf(y,[null,null,null,null,null]),"
               "negpeak:F3.peakOf(y,[null,-5,-3,null,-4]),reach0:F3.firstReach(y,[null,null,0,1,2],0),reach:F3.firstReach(y,[null,0.1,0.6,null,1],0.5),"
               "spread:F3.maxSpread(y,[[1,null,null,1,1],[2,null,9,1,1]]),runs:F3.runs([null,1,2,null,3,null,null,4]),runsAll:F3.runs([1,2,3]),runsNone:F3.runs([null,null]),"
               "last:[F3.lastNum([1,null,3,null]),F3.lastNum([null])],same:[F3.sameSeries([1,null],[1,null]),F3.sameSeries([1,null],[1,0])]}", tmp_path)
    assert out["peak"] == [2001, 5] and out["none"] == [None, None] and out["negpeak"] == [2002, -3]     # an all-negative series has a negative peak, a null is not a zero peak
    assert out["reach0"] == 2002                                                                  # null is not >= 0
    assert out["reach"] == 2002
    assert out["spread"] == {"gap": 1, "year": 2000}                                              # at 2002 only one series has a value, so no gap is computed (9 against a null is not 9 against 0)
    assert out["runs"] == [[1, 2], [4, 4], [7, 7]] and out["runsAll"] == [[0, 2]] and out["runsNone"] == []
    assert out["last"] == [2, -1] and out["same"] == [True, False]


@need_node
def test_csv_writes_an_empty_cell_for_null_and_says_so(tmp_path):
    out = node("return [F3.csvOf([1,2,3],[{name:'a',y:[1,null,0]},{name:'b',y:[null,2,3]}],['n']),F3.csvOf([1],[{name:'a',y:[0]}],[])]", tmp_path)
    lines = out[0].splitlines()
    assert lines[:4] == ["year,a,b", "1,1,", "2,,2", "3,0,3"] and lines[-1].startswith("# An empty cell means no value")
    assert "empty cell" not in out[1]                                                              # no null: no note


def synthetic(null_end: bool):
    yrs = [2000, 2025, 2050, 2075, 2100]
    mk = lambda pop, io: {"pop": pop, "io": io, "nrfr": [1, 0.8, 0.5, 0.3, 0.2], "ppolx": [1, 2, 3, 2, 1]}      # noqa: E731
    std = mk([1, 2, 3, 2, 1], [1, 2, 3, 3, 3])
    run = mk([1, 2, 3, 2, None if null_end else 1], [1, 2, 3, 3, None if null_end else 3])
    return {"y": yrs, "std": std, "run": run, "off": std}


@need_node
def test_findings_tiles_and_deltas_never_show_a_zero_for_a_missing_value(tmp_path):
    p = synthetic(True)
    out = node("var t=[F3.popFinding(IN.y,IN.run,IN.std,'In this run'),F3.industryFinding(IN.y,IN.run,IN.off,'low'),F3.resourcesFinding(IN.y,{nrfr:[1,null]}),"
               "F3.pollutionFinding(IN.y,{ppolx:[null,null,null,null,null]}),F3.temperatureFinding([1],[null],[null],[null]),F3.aiDamageFinding([1],{low:[null],high:[null]}),"
               "F3.w3Kpis(IN.y,IN.run,IN.std,IN.off,'low'),F3.damageBarsFinding(IN.y,F3.damageEffect(IN.run,IN.off,4),'low'),"
               "F3.compareRows(IN.y,IN.std,IN.run,IN.run,null),F3.compareHeadline(IN.y,F3.compareRows(IN.y,IN.std,IN.run,IN.run,null),{a:'A',b:'B'}),"
               "F3.barsFinding(IN.y,F3.compareRows(IN.y,IN.std,IN.run,IN.std,null),{a:'A',b:'B'})];return t", tmp_path, p)
    pop, ind, res, pol, temp, aidmg, tiles, bars, rows, head, barsf = out
    assert "no value" in pop and "falls to" not in pop and "still" not in pop                # the end value is missing: said, not turned into 0 or a fall to 0
    assert "cannot be computed" in ind and "no value" in ind
    assert "no value" in res and "no value" in pol and "no value" in temp and "no value" in aidmg
    by = {t["id"]: t for t in tiles}
    assert by["end"]["v"] == "no value" and "no value" in by["end"]["sub"] and by["dmg"]["v"] == "no value"
    assert "no value" in bars and "0.0%" not in bars and "unchanged" not in bars
    pop_row = next(r for r in rows if r["id"] == "pop")
    assert pop_row["a"] is None and pop_row["dA"] is None and pop_row["bMinusA"] is None and pop_row["bMinusAFrac"] is None
    assert "cannot be compared" in head and "no value" in head
    assert "largest" in barsf and "no value" not in barsf                                        # rows with a missing change are skipped, the others still count


@need_node
def test_without_nulls_the_same_functions_give_their_usual_numbers(tmp_path):
    p = synthetic(False)
    out = node("return [F3.popFinding(IN.y,IN.run,IN.std,'In this run'),F3.w3Kpis(IN.y,IN.run,IN.std,IN.off,'off')]", tmp_path, p)
    assert "peaks at 3 in 2050" in out[0] and "no value" not in out[0]
    assert all("no value" not in json.dumps(t) for t in out[1] if t["id"] != "dmg")


def test_is_finite_is_only_used_inside_isnum_so_no_script_reads_null_as_zero():
    for name in ("charts.js", "dashboard.js", "story.js", "compare.js", "connections.js", "shell.js"):
        src = (SRC / name).read_text(encoding="utf-8")
        assert "isFinite(" not in src and "isNaN(" not in src, name
    core = (CORE).read_text(encoding="utf-8")
    assert core.count("isFinite(") == 1 and 'typeof v === "number" && isFinite(v)' in core
    charts = (SRC / "charts.js").read_text(encoding="utf-8")
    assert "F3.runs(" in charts and "F3.isNum(" in charts                                         # lines and bands are broken at a missing value; bars say "no value"
