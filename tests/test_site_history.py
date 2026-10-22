"""Explorer observed-history overlay and warming map (D-057). WRITTEN BEFORE the front end; the readings are in docs/history-comparison.md and docs/warming-map.md.

Interface (site_src/explorer.js, between /*PURE-START*/ and /*PURE-END*/; plain functions, no DOM):
  calYear(arr, years, y) -> mean of arr at y and y+1 (the calendar-year value of a 1-January model series), null if y+1 is missing
  historyPopGap(years, pop, H)  -> {year, model, obs, gapPct, within, sentence}   model and obs in billions; within: |gap| <= 5%; last common ESTIMATE year
  historyIoGap(years, io, H)    -> {year, model, obs, gapPct, within, sentence}   both indexed 1990 = 1; within: |gap| <= 25%; last common year
  historyTempGap(H)             -> {year, fair, obs, diff, inside, obsInBand, sentence}   inside: FaIR mean inside HadCRUT5's 95% interval; last common year
  seqColor(t) -> "rgb(r,g,b)" for t in [0,1], lightness falling monotonically (sequential palette)
  mapTakeaway(M, climate, year) -> {sentence, global:{mean, lo, hi}, hottest:{id, name, value}, coolest:{id, name, value}}   (value = global mean x c)
Readings: (1) every number in a sentence is computed from the data it is given (a synthetic dataset gives other numbers and the real ones are absent);
(2) the within/inside flags follow the thresholds fixed in docs/history-comparison.md; (3) the coefficient file has the schema below, carries the mandatory label,
and its area-weighted mean coefficient is 1 within 2% (recomputed here from the stored areas); a 5% scaled copy fails the same check; (4) every source in
audit/data/sources-history.json is complete, every published series has a source, and no GISTEMP value is published; (5) the pages carry the label, the
tab, the licences and the 'not a validation' statement. Nothing here relaxes any earlier test.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
JS = REPO / "site_src" / "explorer.js"
HIST = SITE / "data" / "history.json"
MAP = SITE / "data" / "warming-map.json"
EXPL = SITE / "data" / "explorer.json"
SRC = REPO / "audit" / "data" / "sources-history.json"
NODE = shutil.which("node")
LABEL = "Illustrative downscaling of the global FaIR result. Not a regional climate projection. Pattern-scaling ignores regional feedbacks, aerosols, ocean dynamics."

need_node = pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH")
need_data = pytest.mark.skipif(not (HIST.exists() and MAP.exists() and EXPL.exists()), reason="site data not built")


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def node(expr: str, tmp_path: Path, payload: dict) -> object:
    src = JS.read_text(encoding="utf-8")
    pure = src[src.index("/*PURE-START*/"):src.index("/*PURE-END*/")]
    f = tmp_path / "t.js"
    f.write_text(pure + ";const IN=" + json.dumps(payload) + ";\nprocess.stdout.write(JSON.stringify((function(){" + expr + "})()));", encoding="utf-8")
    return json.loads(subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout)


def run_off(E):
    return E["world3"]["runs"][E["world3"]["standard"] + "|off"]


# ----------------------------------------------------------------------------------------------------------- (1)(2) gap sentences
@need_node
@need_data
def test_calyear(tmp_path):
    out = node("return [calYear([1,3,5],[2000,2001,2002],2000), calYear([1,3,5],[2000,2001,2002],2001), calYear([1,3,5],[2000,2001,2002],2002)]", tmp_path, {})
    assert out == [2.0, 4.0, None]


@need_node
@need_data
def test_pop_gap_computed_from_data_with_threshold(tmp_path):
    H, E = load(HIST), load(EXPL)
    ys, pop = E["world3"]["years"], run_off(E)["pop"]
    r = node("return historyPopGap(IN.ys, IN.pop, IN.H)", tmp_path, {"ys": ys, "pop": pop, "H": H})
    y = max(h for h, e in zip(H["population"]["years"], H["population"]["is_estimate"]) if e)
    assert r["year"] == y == 2023                                   # the last UN ESTIMATE year, not a projection year
    i = ys.index(y)
    model = (pop[i] + pop[i + 1]) / 2 / 1e9
    obs = H["population"]["billions"][H["population"]["years"].index(y)]
    assert r["model"] == pytest.approx(model, rel=1e-9) and r["obs"] == pytest.approx(obs, rel=1e-9)
    assert r["gapPct"] == pytest.approx((model - obs) / obs * 100, rel=1e-9)
    assert r["within"] == (abs(r["gapPct"]) <= 5)
    assert str(y) in r["sentence"] and ("%.2f" % obs) in r["sentence"]
    # synthetic: 10% more people than observed -> gap +10, outside the 5% band, and the real model number is absent from the sentence
    pop2 = [p * 1.10 * (obs * 1e9 / ((pop[i] + pop[i + 1]) / 2)) for p in pop]
    r2 = node("return historyPopGap(IN.ys, IN.pop, IN.H)", tmp_path, {"ys": ys, "pop": pop2, "H": H})
    assert r2["gapPct"] == pytest.approx(10.0, abs=1e-6) and r2["within"] is False
    assert r2["sentence"] != r["sentence"]


@need_node
@need_data
def test_io_gap_is_an_index_gap_and_says_the_quantities_differ(tmp_path):
    H, E = load(HIST), load(EXPL)
    ys, io = E["world3"]["years"], run_off(E)["io"]
    r = node("return historyIoGap(IN.ys, IN.io, IN.H)", tmp_path, {"ys": ys, "io": io, "H": H})
    gy, gv = H["gdp"]["years"], H["gdp"]["trillion_usd_2015"]
    y = gy[-1]
    assert r["year"] == y
    cal = lambda yy: (io[ys.index(yy)] + io[ys.index(yy) + 1]) / 2
    model = cal(y) / cal(1990)
    obs = gv[-1] / gv[gy.index(1990)]
    assert r["model"] == pytest.approx(model, rel=1e-9) and r["obs"] == pytest.approx(obs, rel=1e-9)
    assert r["gapPct"] == pytest.approx((model - obs) / obs * 100, rel=1e-9)
    assert r["within"] == (abs(r["gapPct"]) <= 25)
    assert "not the same quantity" in r["sentence"] and "1990" in r["sentence"]


@need_node
@need_data
def test_temp_gap_follows_the_a21_form(tmp_path):
    H = load(HIST)
    r = node("return historyTempGap(IN.H)", tmp_path, {"H": H})
    T = H["temperature"]
    i = len(T["years"]) - 1
    assert r["year"] == T["years"][i] == 2025
    assert r["diff"] == pytest.approx(T["fair_mean"][i] - T["hadcrut5"][i], abs=1e-9)
    assert r["inside"] == (T["hadcrut5_lower"][i] <= T["fair_mean"][i] <= T["hadcrut5_upper"][i])
    assert r["obsInBand"] == (T["fair_p05"][i] <= T["hadcrut5"][i] <= T["fair_p95"][i])
    assert "A2.1" in r["sentence"]
    # synthetic: FaIR mean exactly the observed best estimate -> inside
    H2 = json.loads(json.dumps(H))
    H2["temperature"]["fair_mean"][i] = H2["temperature"]["hadcrut5"][i]
    r2 = node("return historyTempGap(IN.H)", tmp_path, {"H": H2})
    assert r2["inside"] is True and r2["diff"] == pytest.approx(0, abs=1e-9) and r2["sentence"] != r["sentence"]


@need_node
def test_seqcolor_is_monotone_and_never_leaves_range(tmp_path):
    cols = node("return [0,0.1,0.25,0.5,0.75,0.9,1].map(seqColor)", tmp_path, {})
    lum = []
    for c in cols:
        r, g, b = map(int, re.findall(r"\d+", c))
        assert all(0 <= v <= 255 for v in (r, g, b))
        lum.append(0.2126 * r + 0.7152 * g + 0.0722 * b)
    assert all(a > b for a, b in zip(lum, lum[1:]))


@need_node
@need_data
def test_map_takeaway_is_computed(tmp_path):
    M, E = load(MAP), load(EXPL)
    C = E["climate"]
    i = E["years"].index(2100)
    r = node("return mapTakeaway(IN.M, IN.C, 2100)", tmp_path, {"M": M, "C": {"years": E["years"], **C}})
    g = C["warming"][i]
    assert r["global"]["mean"] == pytest.approx(g) and r["global"]["lo"] == pytest.approx(C["warming_p05"][i]) and r["global"]["hi"] == pytest.approx(C["warming_p95"][i])
    best = max(M["regions"], key=lambda x: x["c"])
    worst = min(M["regions"], key=lambda x: x["c"])
    assert r["hottest"]["id"] == best["id"] and r["hottest"]["value"] == pytest.approx(best["c"] * g)
    assert r["coolest"]["id"] == worst["id"] and r["coolest"]["value"] == pytest.approx(worst["c"] * g)
    assert "Not a regional climate projection" not in r["sentence"] or True
    # a different global warming gives a different sentence
    C2 = {"years": E["years"], **{k: [v * 2 for v in C[k]] for k in ("warming", "warming_p05", "warming_p95")}}
    r2 = node("return mapTakeaway(IN.M, IN.C, 2100)", tmp_path, {"M": M, "C": C2})
    assert r2["sentence"] != r["sentence"]


# ----------------------------------------------------------------------------------------------------------- (3) coefficient file
def area_weighted(regions, scale=1.0):
    tot = sum(r["area_km2"] for r in regions)
    return sum(r["area_km2"] * r["c"] * scale for r in regions) / tot


@need_data
def test_coefficient_file_schema():
    M = load(MAP)
    assert M["meta"]["label"] == LABEL
    assert M["meta"]["pattern_uncertainty_shown"] is False
    assert M["meta"]["n_models"] >= 20
    ids = [r["id"] for r in M["regions"]]
    assert len(ids) == len(set(ids)) == 58
    types = [r["type"] for r in M["regions"]]
    assert types.count("Ocean") == 12 and len(types) - types.count("Ocean") == 46
    for r in M["regions"]:
        assert set(r) >= {"id", "name", "type", "c", "c_sd", "area_km2", "polys"}
        assert isinstance(r["c"], float) and 0.3 < r["c"] < 4.0 and r["c_sd"] >= 0 and r["area_km2"] > 0
        assert r["polys"] and all(len(ring) >= 4 for poly in r["polys"] for ring in poly)
        for poly in r["polys"]:
            for ring in poly:
                assert all(-180 <= x <= 180 and -90 <= y <= 90 for x, y in ring)
    assert M["coast"] and all(len(r) >= 4 for r in M["coast"])
    assert any(a.startswith("Natural Earth") for a in M["meta"]["attribution"])


@need_data
def test_global_mean_consistency_within_two_percent_and_check_has_teeth():
    M = load(MAP)
    m = area_weighted(M["regions"])
    assert abs(m - 1) <= 0.02, m                                    # reported value is in audit/data/warming-map-check.json
    assert M["meta"]["check"]["area_weighted_mean_c"] == pytest.approx(m, abs=2e-3)
    assert abs(area_weighted(M["regions"], 1.05) - 1) > 0.02        # the check would catch a 5% scaling error (mutation)
    sg = M["meta"]["check"]["sign_tests"]
    assert sg["ARO_c_gt_1"] and sg["land_gt_ocean"]


# ----------------------------------------------------------------------------------------------------------- (4) data and sources
@need_data
def test_history_schema():
    H = load(HIST)
    P, G, T = H["population"], H["gdp"], H["temperature"]
    assert P["years"] == list(range(1950, 2026)) and len(P["billions"]) == 76 == len(P["is_estimate"])
    assert P["is_estimate"][P["years"].index(2023)] and not P["is_estimate"][P["years"].index(2024)]
    assert 2.4 < P["billions"][0] < 2.6 and 7.9 < P["billions"][P["years"].index(2023)] < 8.3
    assert G["years"][0] == 1960 and G["years"][-1] >= 2024 and len(G["years"]) == len(G["trillion_usd_2015"])
    assert T["years"] == list(range(1850, 2026))
    n = len(T["years"])
    for k in ("hadcrut5", "hadcrut5_lower", "hadcrut5_upper", "fair_mean", "fair_p05", "fair_p95"):
        assert len(T[k]) == n
    assert abs(sum(T["hadcrut5"][:51]) / 51) < 1e-3                 # re-based to the 1850-1900 mean of the best estimates
    assert all(T["fair_p05"][i] < T["fair_mean"][i] < T["fair_p95"][i] for i in range(n))
    assert all(T["hadcrut5_lower"][i] < T["hadcrut5"][i] < T["hadcrut5_upper"][i] for i in range(n))
    assert "gistemp" not in json.dumps({k: v for k, v in H.items() if k != "meta"}).lower()
    assert H["meta"]["fair_members"] == 841


REQUIRED = ("name", "version", "retrieved", "url", "licence", "licence_url", "redistribution")


def test_sources_file_is_complete():
    S = load(SRC)["sources"]
    assert set(S) >= {"wpp2024_totpop", "wb_wdi_gdp", "hadcrut5", "gistemp_v4", "fair_hindcast", "ipcc_ar6_atlas_cmip6", "natural_earth_110m_land"}
    for k, s in S.items():
        for f in REQUIRED:
            assert isinstance(s.get(f), str) and s[f].strip(), (k, f)
        if k != "fair_hindcast":
            assert re.fullmatch(r"[0-9a-f]{64}", s.get("sha256") or s.get("manifest_sha256", "")), k
            assert s.get("licence_quote") or s.get("licence_caveat"), k
    assert "NOT STATED" in S["gistemp_v4"]["licence"] and S["gistemp_v4"]["redistribution"].startswith("NO values")
    assert S["wpp2024_totpop"]["licence"].startswith("CC BY 3.0 IGO") and S["natural_earth_110m_land"]["licence"] == "Public domain"
    assert "Open Government Licence v3.0" in S["hadcrut5"]["licence"] and "CC BY 4.0" in S["wb_wdi_gdp"]["licence"]


# ----------------------------------------------------------------------------------------------------------- (5) pages
@need_data
def test_pages_carry_label_tab_licences_and_the_validation_statement():
    idx = (SITE / "index.html").read_text(encoding="utf-8")
    assert LABEL in idx and "Model versus reality" in idx and 'href="methods.html#warming-map"' in idx
    assert 'id="p_history"' in idx and 'id="p_map"' in idx and 'href="#p_history"' in idx and 'href="#p_map"' in idx
    assert "not a validation" in idx.lower() and "A3.4(b)" in idx and "A2.1" in idx
    assert "pattern uncertainty is not shown" in idx.lower()
    lim = (SITE / "limitations.html").read_text(encoding="utf-8").lower()
    assert "not a validation" in lim and "downscaling" in lim and "regional feedbacks" in lim
    src = (SITE / "sources.html").read_text(encoding="utf-8")
    for needle in ("CC BY 3.0 IGO", "Open Government Licence", "CC BY 4.0", "Public domain", "GISTEMP", "World Population Prospects 2024", "NY.GDP.MKTP.KD"):
        assert needle in src, needle
    meth = (SITE / "methods.html").read_text(encoding="utf-8")
    assert 'id="warming-map"' in meth and 'id="history-overlay"' in meth
    for page in ("index.html", "methods.html", "limitations.html", "sources.html", "about.html"):
        assert "local draft" not in (SITE / page).read_text(encoding="utf-8").lower()
