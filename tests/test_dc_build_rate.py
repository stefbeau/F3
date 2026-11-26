"""Step E1 of the electricity module (D-066): powered capacity limited by a build rate. Readings in docs/e1-build-rate-tests.md, written before the code.
Provisional settings approved by the editor on 2026-11-26: build rates 15%, 30%, 50% a year; outer share 25%."""
from __future__ import annotations

import math
import warnings
from functools import lru_cache

import numpy as np
import pytest

from f3.core.model import Coupling, Model
from f3.sectors.s3_ai import GateParams, S3AI
from f3.sectors.s3_rule_r3 import R3Rule
from f3.sectors.s4_datacentre import DataCentre, DCParams, supply_series

OUTS = ("e_dc_demand", "e_dc", "supply_ratio", "dc_available", "industry_ratio")
COUPLINGS = [Coupling("earth4all_supply", "supply", "s4_datacentre", "supply"), Coupling("s3_ai", "compute_stock", "s4_datacentre", "compute_stock"),
             Coupling("s3_ai", "hardware", "s4_datacentre", "hardware"), Coupling("s4_datacentre", "supply_ratio", "s3_ai", "supply_ratio")]


@lru_cache(maxsize=None)
def run(g_max: float = None, outer: float = None, scale: float = 1.0, dt: float = 0.25, legacy: bool = False):
    """S3 under R3 with the electricity limit, the data-centre module and the recorded supply. ``legacy`` builds DCParams without the new fields."""
    gp = GateParams()
    kw = {} if legacy else {k: v for k, v in (("g_max", g_max), ("outer_share", outer)) if v is not None}
    dp = DCParams(supply_scale=scale, **kw)
    s3, dc = S3AI(gp, rule=R3Rule(), electricity_limited=True), DataCentre(gp, dp)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = Model([s3, dc, supply_series("TLTL")], COUPLINGS, t0=2025.0, t1=2100.0, dt=dt).run()
    out = {n: np.asarray(res.series[("s4_datacentre", n)], dtype=float) for n in OUTS}
    out["time"] = np.asarray(res.time, dtype=float)
    out["supply"] = np.asarray(res.series[("earth4all_supply", "supply")], dtype=float)
    out["usable"] = np.asarray(s3.series()["usable_compute"], dtype=float)
    out["powered"] = np.asarray(getattr(dc, "powered_history", []), dtype=float)
    return out


def test_et1_neutral_values_equal_the_module_without_the_new_parameters():
    a, b = run(legacy=True), run(g_max=math.inf)
    for n in OUTS + ("usable",):
        np.testing.assert_allclose(b[n][1:], a[n][1:], rtol=1e-9, atol=0, equal_nan=True, err_msg=n)
    assert DCParams().g_max == math.inf and DCParams().outer_share is None


@pytest.mark.parametrize("g_max", [0.0, 0.15, 0.30, 0.50])
@pytest.mark.parametrize("outer", [0.05, 0.25])
@pytest.mark.parametrize("scale", [1.0, 0.5])
def test_et2_conservation(g_max, outer, scale):
    r = run(g_max=g_max, outer=outer, scale=scale)
    p = r["powered"]
    assert len(p) == len(r["time"]) - 1 and np.all(np.diff(p) >= -1e-9), "P fell"
    used = r["e_dc"][1:]
    assert np.all(used <= p * (1 + 1e-9)) and np.all(used <= outer * scale * r["supply"][1:] * (1 + 1e-9) + 1e-9)
    for n in OUTS:
        assert np.all(np.isfinite(r[n][1:])) and np.all(r[n][1:] >= 0.0), n


def test_et3_extremes():
    r = run(g_max=0.0, outer=0.25)
    used, dem = r["e_dc"][1:], r["e_dc_demand"][1:]
    assert np.all(used <= 485.0 * (1 + 1e-9))
    np.testing.assert_allclose(used[dem >= 485.0], 485.0, rtol=1e-9)
    a, b = run(legacy=True), run(g_max=math.inf, outer=0.05)
    for n in OUTS:
        np.testing.assert_allclose(b[n][1:], a[n][1:], rtol=1e-9, equal_nan=True, err_msg=n)


def never_raises(lower: dict, higher: dict) -> bool:
    return bool(np.all(lower["usable"] <= higher["usable"] * (1 + 1e-9)))


def test_et4_sign_slower_build_or_less_supply_never_raises_usable_compute():
    r15, r30, r50 = (run(g_max=g, outer=0.25) for g in (0.15, 0.30, 0.50))
    assert never_raises(r15, r30) and never_raises(r30, r50)                         # halving (or lowering) the build rate
    assert never_raises(run(g_max=0.30, outer=0.25, scale=0.5), r30)                 # halving supply
    assert not never_raises(r50, r15), "control: the reverse claim must be false"


def test_et5_step_halving_within_a_tenth_of_a_percent():
    a, b = run(g_max=0.30, outer=0.25), run(g_max=0.30, outer=0.25, dt=0.125)
    years = np.arange(2026.0, 2100.5)
    pick = lambda r: np.array([r["e_dc"][int(np.argmin(np.abs(r["time"] - y)))] for y in years])      # noqa: E731
    rel = np.abs(pick(b) / pick(a) - 1.0)
    assert rel.max() <= 1e-3, f"largest difference {rel.max():.4%} in {int(years[rel.argmax()])}"
