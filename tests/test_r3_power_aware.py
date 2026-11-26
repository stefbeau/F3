"""Step E2 of the electricity module (D-066): R3 reduces its compute share by the unpowered part of the compute stock (lever, default off).
Readings in docs/e2-power-aware-tests.md, written before the code."""
from __future__ import annotations

import itertools
import warnings
from functools import lru_cache

import numpy as np
import pytest

from f3.core.model import Model
from f3.sectors.s3_ai import GateParams, S3AI
from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
from f3.sectors.s4_datacentre import DataCentre, DCParams, supply_series
from tests.test_dc_build_rate import COUPLINGS

FS, US, RATIOS = (0.1, 0.3, 0.6, 0.9, 1.0), (1e-6, 1e-3, 0.1, 0.5), (0.0, 0.01, 0.3, 0.7, 1.0)
FIRST_FIVE = ("q_consumption", "q_compute", "q_capital", "q_hardware_rnd", "q_software_rnd")


def test_e2t1_lever_off_equals_the_rule_before_the_change():
    assert R3Levers().power_aware is False
    rule = R3Rule()
    for f, u, r in itertools.product(FS, US, RATIOS):
        a, b = rule.shares(f, u), rule.shares(f, u, power_ratio=r)
        assert a.keys() == b.keys() and all(abs(a[k] - b[k]) <= 1e-12 for k in a), (f, u, r)


def test_e2t2_shares_stay_valid_with_the_lever_on():
    off, on = R3Rule(), R3Rule(R3Levers(power_aware=True))
    for f, u, r in itertools.product(FS, US, RATIOS):
        a, b = off.shares(f, u), on.shares(f, u, power_ratio=r)
        assert min(b.values()) >= 0.0 and abs(sum(b[k] for k in FIRST_FIVE) - 1.0) <= 1e-12, (f, u, r)
        assert abs(b["q_compute"] - a["q_compute"] * r) <= 1e-12
        changed = {k for k in a if abs(a[k] - b[k]) > 1e-12}
        assert changed <= {"q_compute", "q_consumption"}, changed
        if r == 1.0:
            assert not changed


@lru_cache(maxsize=None)
def run(g_max: float, aware: bool, scale: float = 1.0, outer: float = 0.25):
    gp, dp = GateParams(), DCParams(supply_scale=scale, g_max=g_max, outer_share=outer)
    s3, dc = S3AI(gp, rule=R3Rule(R3Levers(power_aware=aware)), electricity_limited=True), DataCentre(gp, dp)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = Model([s3, dc, supply_series("TLTL")], COUPLINGS, t0=2025.0, t1=2100.0, dt=0.25).run()
    h = s3.series()
    out = {k: np.asarray(h[k], dtype=float) for k in ("usable_compute", "compute_stock", "gwp", "frac_automated")}
    t = np.asarray(res.time, dtype=float)
    at = lambda n, y: float(res.series[("s4_datacentre", n)][int(np.argmin(np.abs(t - (y + 1.0))))])      # noqa: E731
    out["used"] = {y: at("e_dc", y) for y in (2030, 2040, 2060)}
    out["overhang"] = {y: at("e_dc_demand", y) / at("e_dc", y) for y in (2030, 2040, 2060)}
    out["dc_finite"] = all(np.all(np.isfinite(np.asarray(res.series[("s4_datacentre", n)], dtype=float)[1:])) for n in ("e_dc_demand", "e_dc", "supply_ratio", "industry_ratio"))
    return out


def never_raises(lower: dict, higher: dict, name: str) -> bool:
    return bool(np.all(lower[name] <= higher[name] * (1 + 1e-9)))


@pytest.mark.parametrize("name", ["usable_compute", "compute_stock"])
def test_e2t3_sign_with_e2_on(name):
    r15, r30, r50 = (run(g, True) for g in (0.15, 0.30, 0.50))
    assert never_raises(r15, r30, name) and never_raises(r30, r50, name)
    assert never_raises(run(0.30, True, scale=0.5), r30, name)


@pytest.mark.parametrize("name", ["usable_compute", "compute_stock"])
def test_e2t3_control_the_reverse_claim_is_false(name):
    assert not never_raises(run(0.50, True), run(0.15, True), name)


@pytest.mark.parametrize("g_max", [0.15, 0.30, 0.50])
def test_e2t4_overhang_in_2040_is_lower_with_e2(g_max):
    assert run(g_max, True)["overhang"][2040] < run(g_max, False)["overhang"][2040]


@pytest.mark.parametrize("g_max", [0.15, 0.30, 0.50])
def test_e2t5_outputs_finite(g_max):
    r = run(g_max, True)
    assert r["dc_finite"] and all(np.all(np.isfinite(r[k])) for k in ("usable_compute", "compute_stock", "gwp", "frac_automated"))
