"""S7 social module tests (M5 step 2), written BEFORE the module exists. Plan: docs/m5-s7-tests.md; parameters: docs/m5-s7-parameters.md.

Every test drives S7 with GIVEN input series (labour share, unemployment, warming, growth, redistribution) through the coupling loop's
ReplaySector; none uses S3, S1 or S6 output (S3's level is unvalidated, D-029). Every test is about direction, bounds, invariance or a
fixed identity; none compares anything with the world. Sign tests have a control run, and test_mutations_are_caught shows that they can fail.

Interface fixed by docs/m5-s7-parameters.md: f3.sectors.s7_social.S7Social(overrides=None), class attribute PARAMETERS (dict), validation_status,
inputs {labor_share, unemployment, warming, gdp_per_capita_growth, redistribution}, outputs {inequality, trust, tension, wellbeing, policy_response}.
Until that module is written this file fails at import: that is intended.
"""
from __future__ import annotations

import itertools
import re
from pathlib import Path

import numpy as np
import pytest

from f3.core.model import Coupling, Model
from f3.core.replay import ReplaySector
from f3.sectors.s7_social import S7Social

REPO = Path(__file__).resolve().parents[1]
INPUTS = {"labor_share": "1", "unemployment": "1", "warming": "K", "gdp_per_capita_growth": "1/year", "redistribution": "1"}
OUTPUTS = ("inequality", "trust", "tension", "wellbeing", "policy_response")
BOUNDS = {"inequality": (0.10, 0.90), "trust": (0.0, 1.0), "tension": (0.0, 1.0), "wellbeing": (0.0, 1.0), "policy_response": (0.0, 1.0)}
DT = 0.25


def ramp(start, end, years, total):
    """Linear from ``start`` to ``end`` over ``years`` years, then constant; sampled every year over ``total`` years (+1)."""
    t = np.arange(total + 1, dtype=float)
    return np.where(t < years, start + (end - start) * t / years, end)


def const(v, total):
    return np.full(total + 1, float(v))


def run(total=100, overrides=None, **series):
    """Run S7 for ``total`` years from t = 0 with given input series (scalars become constants). Returns {output: value at every step}."""
    base = {"labor_share": 1.0, "unemployment": 0.0, "warming": 0.0, "gdp_per_capita_growth": 0.0, "redistribution": 0.0}
    base.update(series)
    data = {k: (v if np.ndim(v) else const(v, total)) for k, v in base.items()}
    rep = ReplaySector("inputs", np.arange(total + 1, dtype=float), data, INPUTS)
    s7 = S7Social(overrides=overrides)
    res = Model([rep, s7], [Coupling("inputs", k, s7.name, k) for k in INPUTS], t0=0.0, t1=float(total), dt=DT).run()
    out = {n: res.series[(s7.name, n)] for n in OUTPUTS}
    out["time"] = res.time
    return out


def at(r, name, year):
    return float(r[name][int(round(year / DT))])


# ----------------------------------------------------------------------------------------------------------------- A5.2 bounds
GRID = list(itertools.product((1.0, 0.7, 0.2), (0.0, 0.15, 0.6), (0.0, 2.0, 6.0), (0.0, 0.5, 1.0), (-0.05, 0.0, 0.05)))   # 243 combinations


@pytest.mark.parametrize("combo", GRID[::3])        # every third combination: 81 scenarios
def test_b1_bounds_and_finiteness_over_the_grid(combo):
    ls_end, ue, w, red, g = combo
    r = run(200, labor_share=ramp(1.0, ls_end, 60, 200), unemployment=ue, warming=w, redistribution=red, gdp_per_capita_growth=g)
    for n in OUTPUTS:
        v = r[n]
        assert np.all(np.isfinite(v)), (n, combo)
        lo, hi = BOUNDS[n]
        assert v.min() >= lo - 1e-12 and v.max() <= hi + 1e-12, (n, combo, v.min(), v.max())


def test_b2_extreme_inputs_keep_the_bounds():
    for ls, ue, w, g in ((0.0, 1.0, 20.0, 1.0), (1.0, 1.0, 20.0, -1.0), (0.0, 0.0, 0.0, 1.0), (5.0, 5.0, -5.0, -5.0)):
        r = run(150, labor_share=ls, unemployment=ue, warming=w, gdp_per_capita_growth=g, redistribution=1.0)
        for n in OUTPUTS:
            lo, hi = BOUNDS[n]
            assert np.all(np.isfinite(r[n])) and r[n].min() >= lo - 1e-12 and r[n].max() <= hi + 1e-12, (n, ls, ue, w, g)


# ----------------------------------------------------------------------------------------------------------------- A5.3 extremes
def test_e1_no_automation_the_start_is_a_fixed_point():
    r = run(100)
    p = S7Social.PARAMETERS
    start = {"inequality": p["I0"], "trust": p["Tr0"], "tension": p["Te0"], "wellbeing": p["W0"], "policy_response": p["P0"]}
    for n, v0 in start.items():
        assert np.allclose(r[n], v0, atol=1e-12), (n, r[n].min(), r[n].max(), v0)


def test_e2_policy_loop_off_is_identical_to_no_policy_response():
    kw = dict(labor_share=ramp(1.0, 0.5, 40, 100), unemployment=0.2)
    off = run(100, overrides={"kP": 0.0}, **kw)
    assert np.allclose(off["policy_response"], 0.0, atol=1e-12)
    # with the loop off, redistribution input 0 and no policy pressure, inequality equals the run with the threshold set unreachable
    unreachable = run(100, overrides={"Te_threshold": 2.0}, **kw)
    for n in OUTPUTS:
        assert np.allclose(off[n], unreachable[n], atol=1e-12), n


# ----------------------------------------------------------------------------------------------------------------- A5.5 sign: R2
R2_CAUSE = dict(labor_share=ramp(1.0, 0.7, 40, 100))
R2_CONTROL = dict(labor_share=1.0)


def r2_assertions(cause, control):
    assert at(cause, "inequality", 40) > at(control, "inequality", 40)
    assert at(cause, "tension", 40) > at(control, "tension", 40)
    assert at(cause, "wellbeing", 40) < at(control, "wellbeing", 40)
    k = int(round(40 / DT))
    assert np.all(np.diff(cause["inequality"][: k + 1]) >= -1e-12)          # inequality non-decreasing over the first 40 years


def test_r2_automation_raises_inequality_and_tension_and_lowers_wellbeing():
    r2_assertions(run(100, **R2_CAUSE), run(100, **R2_CONTROL))


def test_mutations_are_caught():
    """The R2 and B5 sign tests can fail: with the R2 gain gI_LS set to 0 the R2 assertions must fail, and with kP = 0 the B5 ones must."""
    with pytest.raises(AssertionError):
        r2_assertions(run(100, overrides={"gI_LS": 0.0}, **R2_CAUSE), run(100, overrides={"gI_LS": 0.0}, **R2_CONTROL))
    with pytest.raises(AssertionError):
        b5_assertions(run(150, overrides={"kP": 0.0}, **B5_KW), run(150, overrides={"kP": 0.0}, **B5_KW))


# ----------------------------------------------------------------------------------------------------------------- A5.5 sign: B5
B5_KW = dict(labor_share=ramp(1.0, 0.5, 40, 150), unemployment=0.2)


def first_year(series, time, level):
    idx = np.where(series > level)[0]
    return float(time[idx[0]]) if len(idx) else None


def b5_assertions(on, off):
    th = S7Social.PARAMETERS["Te_threshold"]
    t = on["time"]
    y_te = first_year(on["tension"], t, th)
    assert y_te is not None, "tension never exceeds the threshold in this regime"
    pre = on["policy_response"][t <= y_te]
    assert np.all(pre <= 1e-9)                                              # (a) no response before the threshold is exceeded
    assert on["policy_response"].max() > 0.05                               # (a) positive afterwards
    y_pr = first_year(on["policy_response"], t, 0.05)
    assert y_pr is not None and y_pr > y_te                                 # (b) the response lags tension
    assert at(on, "inequality", 100) < at(off, "inequality", 100)           # (c) lower inequality with the loop on


def test_b5_policy_response_is_delayed_and_lowers_inequality():
    b5_assertions(run(150, **B5_KW), run(150, overrides={"kP": 0.0}, **B5_KW))


# ----------------------------------------------------------------------------------------------------------------- other signs
def test_s1_warming_raises_tension_and_lowers_wellbeing():
    hot, cold = run(100, warming=3.0), run(100, warming=0.0)
    assert at(hot, "tension", 40) > at(cold, "tension", 40)
    assert at(hot, "wellbeing", 40) < at(cold, "wellbeing", 40)


def test_s2_redistribution_lowers_inequality():
    kw = dict(labor_share=ramp(1.0, 0.7, 40, 100))
    assert at(run(100, redistribution=0.5, **kw), "inequality", 40) < at(run(100, redistribution=0.0, **kw), "inequality", 40)


def test_s3_growth_raises_wellbeing():
    assert at(run(100, gdp_per_capita_growth=0.03), "wellbeing", 40) > at(run(100, gdp_per_capita_growth=-0.03), "wellbeing", 40)


def test_s4_unemployment_raises_inequality_and_tension():
    hi, lo = run(100, unemployment=0.2), run(100, unemployment=0.0)
    assert at(hi, "inequality", 40) > at(lo, "inequality", 40)
    assert at(hi, "tension", 40) > at(lo, "tension", 40)


# ----------------------------------------------------------------------------------------------------------------- interface and labels
def test_i1_units_are_declared_and_the_loop_accepts_the_module():
    assert set(S7Social.inputs) == set(INPUTS) and all(isinstance(u, str) for u in S7Social.inputs.values())
    assert set(S7Social.outputs) == set(OUTPUTS) and all(isinstance(u, str) for u in S7Social.outputs.values())
    run(10)                                                                  # builds and runs through the coupling core


def test_i2_validation_status_carries_the_required_labels():
    s = S7Social.validation_status.lower()
    assert "illustrative" in s and "not validated against history" in s
    assert "unvalidated" in s and "gate" in s                                # the D-029 sentence about S3


def parse_parameter_table():
    text = (REPO / "docs" / "m5-s7-parameters.md").read_text(encoding="utf-8")
    sec = text.split("## 3. Parameters")[1].split("## 4.")[0]
    rows = {}
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and re.match(r"^`[A-Za-z_0-9, `]+`", cells[0]):
            rows[cells[0]] = cells
    return rows


def test_i3_parameter_document_and_module_agree_and_every_parameter_is_marked():
    rows = parse_parameter_table()
    documented = {}
    for name_cell, cells in rows.items():
        names = [n.strip().strip("`") for n in re.findall(r"`([A-Za-z_0-9]+)`", name_cell)]
        values = [v.strip() for v in re.split(r",\s*", cells[1])]
        value_text = cells[1]
        if len(names) > 1 and len(values) == len(names):
            for n, v in zip(names, values):
                documented[n] = (v, cells[3])
        elif len(names) >= 1:
            documented[names[0]] = (value_text, cells[3])
    skip = {"LS0", "bounds"}
    params = S7Social.PARAMETERS
    missing = [n for n in params if n not in documented]
    assert not missing, f"parameters in the module but not in the document: {missing}"
    for n, v in params.items():
        doc_value, source = documented[n]
        assert abs(float(re.findall(r"[-+]?\d*\.?\d+", doc_value)[0]) - float(v)) < 1e-12, (n, doc_value, v)
        assert "illustrative" in source.lower() or "read" in source.lower(), (n, source)      # every parameter is marked
    extra = [n for n in documented if n not in params and n not in skip and not n.startswith("start")]
    assert not extra, f"documented but not in the module: {extra}"


def test_i4_the_module_imports_nothing_from_s3_s1_or_s6():
    src = (REPO / "f3" / "sectors" / "s7_social.py").read_text(encoding="utf-8")
    assert not re.search(r"^\s*(from|import)\s+f3\.sectors\.(s3_ai|s1_|s1_population|s1_sector|s6_climate|s3_rule)", src, re.M)
