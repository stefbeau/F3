"""Explorer v0.2 (D-056): the pure functions of site_src/core.js (headlines, tiles, deltas, hash state, CSV) run in Node on the committed data and on
synthetic data, and the page scripts are scanned for hard-coded model numbers (extends the D-052 pattern of tests/test_site_ux.py).

Written before the stage-2 front end. Readings: (1) every number in a generated headline, tile or delta equals a number computed here from the data;
(2) a synthetic dataset with different values gives different headlines and the real values are absent; (3) hash state round-trips and bad hashes
fall back to defaults; (4) delta maths: B minus A, change against the baseline, identical rows flagged; (5) no page script contains a number that is
derived from the data. Nothing here relaxes any earlier test."""
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
SCRIPTS = ["story.js", "dashboard.js", "charts.js", "shell.js"]       # page scripts that must hold no model numbers (dashboard.js, compare.js, connections.js are added by later stages)


def data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def node(expr: str, tmp_path: Path, payload: dict = None):
    prog = (f"const F3=require({json.dumps(str(CORE))});const IN=" + json.dumps(payload or {}) + ";\n" +
            "process.stdout.write(JSON.stringify((function(){" + expr + "})()));")
    f = tmp_path / "t.js"
    f.write_text(prog, encoding="utf-8")
    return json.loads(subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)


def run_of(d, levers, damage):
    return d["world3"]["runs"]["|".join(map(str, levers)) + "|" + damage]


STD = [1, 0, 0]


# ------------------------------------------------------------------------------------------------------ formats
@need_node
def test_human_rel_and_signed_pct(tmp_path):
    out = node("return [F3.human(7530000000),F3.human(3.5e9),F3.human(1.2e6),F3.human(0.5),F3.rel(-0.123),F3.rel(0.04),F3.rel(0),F3.signedPct(-0.123),F3.signedPct(0.04),F3.signedPct(0)]", tmp_path)
    assert out == ["7.53 billion", "3.5 billion", "1.2 million", "0.5", "12.3% lower", "4.0% higher", "unchanged", "-12.3%", "+4.0%", "0.0%"]


# ------------------------------------------------------------------------------------------------------ (1) headlines from the data
@need_data
@need_node
def test_population_finding_numbers_come_from_the_data(tmp_path):
    d = data()
    yrs = d["world3"]["years"]
    run, std = run_of(d, [2, 1, 1], "off"), run_of(d, STD, "off")
    s = node("return F3.popFinding(IN.y, IN.run, IN.std, 'In this run')", tmp_path, {"y": yrs, "run": run, "std": std})
    pk = max(range(len(run["pop"])), key=lambda i: run["pop"][i])
    sp = max(range(len(std["pop"])), key=lambda i: std["pop"][i])
    assert str(yrs[pk]) in s and str(yrs[sp]) in s and "the standard run peaks at" in s
    same = node("return F3.popFinding(IN.y, IN.std, IN.std, 'In the standard run')", tmp_path, {"y": yrs, "std": std})
    assert "the standard run peaks at" not in same and str(yrs[sp]) in same


@need_data
@need_node
def test_other_findings(tmp_path):
    d = data()
    yrs = d["world3"]["years"]
    off, cen = run_of(d, STD, "off"), run_of(d, STD, "central")
    io = node("return F3.industryFinding(IN.y, IN.run, IN.off, 'central')", tmp_path, {"y": yrs, "run": cen, "off": off})
    eff = (cen["io"][-1] / off["io"][-1] - 1) * 100
    assert f"{abs(eff):.1f}% lower" in io and "central" in io
    assert "damage" not in node("return F3.industryFinding(IN.y, IN.off, IN.off, 'off')", tmp_path, {"y": yrs, "off": off})
    assert f"{off['nrfr'][-1]:.2f}" in node("return F3.resourcesFinding(IN.y, IN.off)", tmp_path, {"y": yrs, "off": off})
    pol = node("return F3.pollutionFinding(IN.y, IN.off)", tmp_path, {"y": yrs, "off": off})
    assert f"{max(off['ppolx']):.1f}" in pol and f"{off['ppolx'][-1]:.2f}" in pol
    c = d["climate"]
    t = node("return F3.temperatureFinding(IN.y, IN.m, IN.lo, IN.hi)", tmp_path, {"y": d["years"], "m": c["warming"], "lo": c["warming_p05"], "hi": c["warming_p95"]})
    assert f"{c['warming'][-1]:.2f}" in t and f"{c['warming_p05'][-1]:.2f}" in t and f"{c['warming_p95'][-1]:.2f}" in t
    r = d["runs"]["central|central|1"]
    a = node("return F3.automationFinding(IN.y, IN.f, 'central')", tmp_path, {"y": d["years"], "f": r["frac_automated"]})
    y05 = next(d["years"][i] for i, v in enumerate(r["frac_automated"]) if v >= 0.5)
    y10 = next(d["years"][i] for i, v in enumerate(r["frac_automated"]) if v >= 0.999)
    assert str(y05) in a and str(y10) in a
    never = node("return F3.automationFinding(IN.y, IN.f, 'low')", tmp_path, {"y": d["years"], "f": [0.1] * len(d["years"])})
    assert "no year before" in never
    dm = {o: d["runs"][f"central|{o}|1"]["damage_fraction"] for o in ("low", "central", "high")}
    ai = node("return F3.aiDamageFinding(IN.y, IN.dm)", tmp_path, {"y": d["years"], "dm": dm})
    assert f"{dm['low'][-1] * 100:.1f}%" in ai and f"{dm['high'][-1] * 100:.1f}%" in ai


@need_data
@need_node
def test_damage_bars_finding_and_effects(tmp_path):
    d = data()
    yrs = d["world3"]["years"]
    off, hi = run_of(d, STD, "off"), run_of(d, STD, "high")
    eff = node("return F3.damageEffect(IN.run, IN.off, IN.n)", tmp_path, {"run": hi, "off": off, "n": len(yrs) - 1})
    assert abs(eff["io"] - (hi["io"][-1] / off["io"][-1] - 1)) < 1e-12 and eff["io"] < 0
    s = node("return F3.damageBarsFinding(IN.y, IN.eff, 'high')", tmp_path, {"y": yrs, "eff": eff})
    assert f"{abs(eff['io']) * 100:.1f}%" in s and "high" in s
    assert "off" in node("return F3.damageBarsFinding(IN.y, null, 'off')", tmp_path, {"y": yrs}) and "pick an option" in node("return F3.damageBarsFinding(IN.y, null, 'off')", tmp_path, {"y": yrs})


@need_node
def test_findings_change_with_the_data_and_hold_no_typed_numbers(tmp_path):
    years = list(range(1900, 2101))
    n = len(years)

    def run(peak_year, peak, end, nr_end, pp_peak):
        pop = [peak * (1 - abs(y - peak_year) / 400.0) if y != 2100 else end for y in years]
        return {"pop": pop, "io": [1.0] * n, "ic": [1.0] * n, "al": [1.0] * n, "nrfr": [1 - (1 - nr_end) * (y - 1900) / 200 for y in years],
                "ppolx": [pp_peak * (1 - abs(y - 2013) / 300.0) for y in years]}

    a, b = run(1981, 9.1e9, 3.3e9, 0.31, 7.7), run(2047, 4.4e9, 1.1e9, 0.62, 2.2)
    sa = node("return F3.popFinding(IN.y, IN.a, null, 'X')", tmp_path, {"y": years, "a": a})
    sb = node("return F3.popFinding(IN.y, IN.b, null, 'X')", tmp_path, {"y": years, "b": b})
    assert "1981" in sa and "9.1 billion" in sa and "3.3 billion" in sa and "2047" in sb and "4.4 billion" in sb and "1.1 billion" in sb
    assert "2047" not in sa and "1981" not in sb
    assert "0.31" in node("return F3.resourcesFinding(IN.y, IN.a)", tmp_path, {"y": years, "a": a}) and "0.62" in node("return F3.resourcesFinding(IN.y, IN.b)", tmp_path, {"y": years, "b": b})
    assert "7.7" in node("return F3.pollutionFinding(IN.y, IN.a)", tmp_path, {"y": years, "a": a}) and "2.2" in node("return F3.pollutionFinding(IN.y, IN.b)", tmp_path, {"y": years, "b": b})
    rising = {"pop": [1e9 + i * 1e7 for i in range(n)], "io": [1.0] * n, "nrfr": [1.0] * n, "ppolx": [1.0] * n}
    assert "is still" in node("return F3.popFinding(IN.y, IN.r, null, 'X')", tmp_path, {"y": years, "r": rising}) and "falls" not in node("return F3.popFinding(IN.y, IN.r, null, 'X')", tmp_path, {"y": years, "r": rising})


# ------------------------------------------------------------------------------------------------------ tiles
@need_data
@need_node
def test_w3_kpis_are_at_most_five_and_from_the_data(tmp_path):
    d = data()
    yrs = d["world3"]["years"]
    std, run, off = run_of(d, STD, "off"), run_of(d, [2, 1, 1], "central"), run_of(d, [2, 1, 1], "off")
    tiles = node("return F3.w3Kpis(IN.y, IN.run, IN.std, IN.off, 'central')", tmp_path, {"y": yrs, "run": run, "std": std, "off": off})
    assert 3 <= len(tiles) <= 5
    text = " | ".join(t["k"] + " " + t["v"] + " " + t["sub"] for t in tiles)
    pk = max(range(len(run["pop"])), key=lambda i: run["pop"][i])
    assert str(yrs[pk]) in text and f"{run['nrfr'][-1]:.2f}" in text
    assert f"{(run['pop'][-1] / std['pop'][-1] - 1) * 100:+.1f}%" in text and f"{(run['io'][-1] / off['io'][-1] - 1) * 100:+.1f}%" in text
    t_off = node("return F3.w3Kpis(IN.y, IN.std, IN.std, IN.std, 'off')", tmp_path, {"y": yrs, "std": std})
    dm = [t for t in t_off if t["id"] == "dmg"][0]
    assert dm["v"] == "n/a" and "off" in dm["sub"]
    assert any("same as the standard run" in t["sub"] for t in t_off)


# ------------------------------------------------------------------------------------------------------ (3) hash state
@need_node
def test_decode_state_bad_hashes_fall_back(tmp_path):
    for bad in ("", "#", "#w3=9.9.9&d=huge", "#w3=a.b.c", "garbage", "#w3=1.0&d=off", "#d=central&w3=1.0.0&ai=nope"):
        out = node(f"return F3.decodeState({json.dumps(bad)},3)", tmp_path)
        assert len(out["levers"]) == 3 and all(isinstance(v, int) and 0 <= v <= 2 for v in out["levers"]), bad
        assert out["damage"] in ("off", "low", "central", "high")
    assert node("return F3.decodeState('#w3=2.1.0&d=central',3)", tmp_path)["levers"] == [2, 1, 0]
    assert node("return F3.decodeState('#w3=9.9.9&d=huge',3)", tmp_path)["damage"] == "off"


@need_node
def test_state_hash_round_trips_for_every_grid_point(tmp_path):
    cases = [{"levers": [i, j, k], "damage": dm, "ai": "race", "aidmg": "high"} for i in range(3) for j in range(3) for k in range(3) for dm in ("off", "low", "central", "high")]
    assert node("return IN.c.map(s=>F3.decodeState(F3.encodeState(s),3))", tmp_path, {"c": cases}) == cases


@need_data
@need_node
def test_presets_are_grid_points(tmp_path):
    d = data()
    presets = node("return F3.PRESETS", tmp_path)
    assert [p["name"] for p in presets] == ["Standard", "More resources", "Farming tech", "Pollution cut", "Combined"]
    for p in presets:
        assert "|".join(map(str, p["levers"])) + "|off" in d["world3"]["runs"] and len(p["text"]) > 20
    assert "|".join(map(str, presets[0]["levers"])) == d["world3"]["standard"]


# ------------------------------------------------------------------------------------------------------ (4) compare maths
@need_data
@need_node
def test_compare_rows_delta_maths(tmp_path):
    d = data()
    yrs = d["world3"]["years"]
    base, a, b = run_of(d, STD, "off"), run_of(d, [1, 1, 0], "central"), run_of(d, [2, 1, 1], "high")
    rows = node("return F3.compareRows(IN.y, IN.base, IN.a, IN.b, IN.w)", tmp_path, {"y": yrs, "base": base, "a": a, "b": b, "w": d["climate"]["warming"]})
    by = {r["id"]: r for r in rows}
    assert [r["id"] for r in rows] == ["pop", "io", "nrfr", "ppolx", "warming"]
    for key in ("pop", "io", "nrfr", "ppolx"):
        r = by[key]
        v0, va, vb = base[key][-1], a[key][-1], b[key][-1]
        assert abs(r["dA"] - (va / v0 - 1)) < 1e-12 and abs(r["dB"] - (vb / v0 - 1)) < 1e-12
        assert abs(r["bMinusA"] - (vb - va)) < 1e-6 * max(1, abs(va)) and abs(r["bMinusAFrac"] - (vb / va - 1)) < 1e-12
        assert not r["identical"]
    w = by["warming"]
    assert w["identical"] and w["dA"] == 0 and w["dB"] == 0 and w["bMinusA"] == 0 and abs(w["base"] - d["climate"]["warming"][-1]) < 1e-12
    same = node("return F3.compareRows(IN.y, IN.base, IN.base, IN.base, null)", tmp_path, {"y": yrs, "base": base})
    assert all(r["identical"] and r["bMinusA"] == 0 and r["dA"] == 0 for r in same) and len(same) == 4


@need_data
@need_node
def test_compare_headline_is_generated_from_the_rows(tmp_path):
    d = data()
    yrs = d["world3"]["years"]
    base, a, b = run_of(d, STD, "off"), run_of(d, STD, "central"), run_of(d, [2, 1, 1], "central")
    rows = node("return F3.compareRows(IN.y, IN.base, IN.a, IN.b, null)", tmp_path, {"y": yrs, "base": base, "a": a, "b": b})
    names = {"a": "Scenario A", "b": "Scenario B"}
    h = node("return F3.compareHeadline(IN.y, IN.rows, IN.names)", tmp_path, {"y": yrs, "rows": rows, "names": names})
    pa, pb = a["pop"][-1], b["pop"][-1]
    assert "Scenario B ends 2100" in h and ("more" if pb > pa else "fewer") in h and "people than Scenario A" in h
    assert f"{abs(b['io'][-1] / a['io'][-1] - 1) * 100:.1f}%" in h
    same = node("return F3.compareHeadline(IN.y, IN.rows, IN.names)", tmp_path,
                {"y": yrs, "rows": node("return F3.compareRows(IN.y, IN.b, IN.b, IN.b, null)", tmp_path, {"y": yrs, "b": b}), "names": names})
    assert "same population and industrial output" in same
    swapped = node("return F3.compareHeadline(IN.y, IN.rows, IN.names)", tmp_path,
                   {"y": yrs, "rows": node("return F3.compareRows(IN.y, IN.base, IN.b, IN.a, null)", tmp_path, {"y": yrs, "base": base, "a": a, "b": b}), "names": names})
    assert swapped != h                                                                        # swapping A and B changes the sentence


@need_node
def test_compare_hash_round_trip_and_fallback(tmp_path):
    cases = [{"a": {"levers": [i, j, 2 - i], "damage": dm}, "b": {"levers": [2 - j, i, j], "damage": "off"}, "metric": m}
             for i in range(3) for j in range(3) for dm in ("off", "low", "central", "high") for m in ("pop", "io", "nrfr", "ppolx")]
    assert node("return IN.c.map(s=>F3.compareState(F3.encodeCompare(s)))", tmp_path, {"c": cases}) == cases
    default = node("return F3.compareState('')", tmp_path)
    for bad in ("#a=9.9.9-off", "#a=1.0.0-wild&b=zzz", "#m=nope", "garbage", "#a=1.0-off"):
        out = node(f"return F3.compareState({json.dumps(bad)})", tmp_path)
        assert len(out["a"]["levers"]) == 3 and len(out["b"]["levers"]) == 3 and out["a"]["damage"] in ("off", "low", "central", "high") and out["metric"] == "pop", bad
    assert node("return F3.compareState('#a=9.9.9-off')", tmp_path) == default
    assert node("return F3.scenarioName([2,0,0],'off')", tmp_path) == "More resources (damage off)"
    assert node("return F3.scenarioName([0,0,0],'low')", tmp_path) == "Custom 0.0.0 (low damage)"


@need_data
@need_node
def test_overlay_and_bars_findings_and_signed_format(tmp_path):
    d = data()
    yrs = d["world3"]["years"]
    base, a, b = run_of(d, STD, "off"), run_of(d, [1, 1, 0], "central"), run_of(d, [2, 1, 1], "high")
    names = {"a": "Scenario A", "b": "Scenario B"}
    vals = {"base": base["pop"][-1], "a": a["pop"][-1], "b": b["pop"][-1]}
    f = node("return F3.overlayFinding(IN.y, 'Population', 'people', IN.v, IN.n)", tmp_path, {"y": yrs, "v": vals, "n": names})
    assert "Population in 2100" in f and all(node(f"return F3.human({v})", tmp_path) in f for v in vals.values())
    rows = node("return F3.compareRows(IN.y, IN.base, IN.a, IN.b, IN.w)", tmp_path, {"y": yrs, "base": base, "a": a, "b": b, "w": d["climate"]["warming"]})
    bf = node("return F3.barsFinding(IN.y, IN.rows, IN.n)", tmp_path, {"y": yrs, "rows": rows, "n": names})
    cand = [(abs(r["dA"]), "Scenario A", r) for r in rows if not r["identical"]] + [(abs(r["dB"]), "Scenario B", r) for r in rows if not r["identical"]]
    top = max(cand, key=lambda c: c[0])
    assert top[1] in bf and top[2]["label"].lower() in bf and f"{abs(top[0]) * 100:.1f}%" in bf and "warming" not in bf.lower()
    same = node("return F3.compareRows(IN.y, IN.base, IN.base, IN.base, null)", tmp_path, {"y": yrs, "base": base})
    assert "match the standard run" in node("return F3.barsFinding(IN.y, IN.rows, IN.n)", tmp_path, {"y": yrs, "rows": same, "n": names})
    assert node("return [F3.signedFmt(-0.05,'fraction'),F3.signedFmt(1.2e9,'people'),F3.signedFmt(0,'index')]", tmp_path) == ["-0.05", "+1.2 billion", "0"]


@need_node
def test_max_spread_and_csv(tmp_path):
    sp = node("return F3.maxSpread([1,2,3],[[0,1,0.5],[0,0.4,0.5],[0,0.9,0.5]])", tmp_path)
    assert abs(sp["gap"] - 0.6) < 1e-12 and sp["year"] == 2
    out = node("return F3.csvOf(IN.y, [{name:'a, b',y:[1,2.5,3]},{name:'c',y:[4,5,6]}])", tmp_path, {"y": [2020, 2021, 2022]})
    lines = out.strip().split("\n")
    assert lines[0] == 'year,"a, b",c' and lines[1] == "2020,1,4" and lines[3] == "2022,3,6" and len(lines) == 4


@need_node
def test_damage_notice_phrases(tmp_path):
    assert node("return F3.damageNotice('off')", tmp_path) == ""
    for dm in ("low", "central", "high"):
        s = node(f"return F3.damageNotice('{dm}')", tmp_path).lower()
        for phrase in ("level-of-output effect, not the upper end of the literature", "not compared with worlddynamics.jl", "it has no climate damage",
                       "s3's economy and world3's are not reconciled", "no health or yield effect of warming"):
            assert phrase in s, (dm, phrase)


# ------------------------------------------------------------------------------------------------------ (5) no hard-coded data in page scripts
def derived_strings(d: dict) -> set[str]:
    """Strings a page script would contain if it had a model number typed into it: peaks, end values, effects, shares, written the ways the page writes them."""
    out: set[str] = set()
    yrs = d["world3"]["years"]
    for key, run in d["world3"]["runs"].items():
        pk = max(range(len(run["pop"])), key=lambda i: run["pop"][i])
        out.add(f"{run['pop'][pk]:.6g}")
        out.add(f"{run['pop'][-1]:.6g}")
        out.add(f"{run['io'][-1]:.6g}")
        out.add(f"{run['nrfr'][-1]:.2f}")
    std = d["world3"]["runs"][d["world3"]["standard"] + "|off"]
    pk = max(range(len(std["pop"])), key=lambda i: std["pop"][i])
    out.add(f"{std['pop'][pk] / 1e9:.3g} billion")
    out.add(f"{std['pop'][-1] / 1e9:.3g} billion")
    out.add(f"{d['climate']['warming'][-1]:.2f}")
    out.add(f"{d['climate']['warming_p95'][-1]:.2f}")
    for o in ("low", "central", "high"):
        out.add(f"{d['runs'][f'central|{o}|1']['damage_fraction'][-1] * 100:.1f}%")
    out.discard("0.00")
    return {s for s in out if len(s) >= 4}


@need_data
@pytest.mark.parametrize("script", SCRIPTS)
def test_page_scripts_hold_no_data_derived_numbers(script):
    path = SRC / script
    if not path.exists():
        pytest.skip(f"{script} not built yet")
    src = path.read_text(encoding="utf-8")
    hits = [s for s in derived_strings(data()) if s in src]
    assert not hits, (script, hits)
    # control: the scan can fail. A script that did contain the standard run's peak population would be caught.
    std = data()["world3"]["runs"][data()["world3"]["standard"] + "|off"]
    peak = f"{max(std['pop']):.6g}"
    assert [s for s in derived_strings(data()) if s in (src + " " + peak)], "control failed: the scan would miss a typed value"


@pytest.mark.parametrize("script", SCRIPTS + ["core.js"])
def test_page_scripts_have_no_inline_years_for_peaks(script):
    path = SRC / script
    if not path.exists():
        pytest.skip(f"{script} not built yet")
    src = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
    assert not re.search(r"\b(peak|peaks)\b[^\n]{0,40}\b(?!1970)(19|20)\d\d\b", src), script


def test_core_is_pure_no_dom():
    src = re.sub(r"/\*.*?\*/", "", CORE.read_text(encoding="utf-8"), flags=re.S)
    for token in ("document.", "window.", "getElementById", "localStorage", "fetch("):
        assert token not in src, token
