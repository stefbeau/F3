"""D-055: optional efficiency cap on the data-centre module (eta <= 4e15 FLOP/J, the value behind C_L in the GATE paper). WRITTEN BEFORE the cap exists.

Interface fixed in advance: ``DCParams.eta_cap`` (FLOP/J, default None = OFF) and ``f3.sectors.s4_datacentre.PAPER_ETA_CAP = 4e15``;
``eta(hardware) = min(eta_0 x hardware / H0, eta_cap)`` when the cap is set, ``eta_0 x hardware / H0`` when it is None. ``e_dc_twh`` uses it.

Readings (written before any run):
 1. OFF (the default) equals every recorded result to 1e-9: the coupled slice, three shipped settings, stand-in climate, against the snapshot taken before
    this change (tests/fixtures/s4_baseline_before_eta_cap.csv); gwp, compute stock, usable compute, hardware, demand, used electricity, supply ratio.
 2. The cap is respected: with the cap set, eta never exceeds it for any hardware value (direct, on a grid from 1x to 1e8x H0), and demand at hardware beyond
    the cap point equals compute / eta_cap x PUE / J_PER_TWH exactly. A control that can fail: with the cap OFF the same grid gives eta above the cap.
 3. A cap that does not bind changes nothing: with the paper's cap and hardware inside S3's range the demand equals the OFF value to 1e-12 (the hand check of D-055:
    eta_0 x H_max / H0 = 8.06e14 < 4e15, so the paper's cap cannot bind inside S3's hardware range). A cap that DOES bind (set low) lowers demand strictly, from the year
    hardware passes the cap point, and never raises it (named output: e_dc_demand, window 2025-2100).
 4. A2.5 unchanged with the cap set: zero compute growth keeps demand at 485 TWh; unlimited electricity makes B1 inactive. B1 unchanged: the cap changes demand only,
    so S3's inputs from the module (supply_ratio) are equal to OFF to 1e-12 when the cap does not bind.
 5. Bounds: demand finite and non-negative over the cap grid; the cap must be positive (a non-positive cap raises).
No criterion or earlier test is touched.
"""
from __future__ import annotations

import csv
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

from f3.core.model import Coupling, Model
from f3.core.replay import ReplaySector
from f3.sectors.s3_ai import GateParams
from f3.sectors.s4_datacentre import IEA_2025_TWH, J_PER_TWH, DataCentre, DCParams, e_dc_twh, eta_0, initial_compute_stock
from f3.sectors.slice_m2 import ClimateReplay, SliceConfig, run_slice
from tests.s3_checks import SETTINGS_B

FIX = Path(__file__).parent / "fixtures" / "s4_baseline_before_eta_cap.csv"
YEARS = np.arange(2025.0, 2101.0)
GP = GateParams()
PAPER = 4.0e15


def stand_in():
    w = 1.2 + (2.9 - 1.2) * (YEARS - 2025.0) / 75.0
    return ClimateReplay(YEARS, {"warming": w, "warming_p05": w - 0.4, "warming_p95": w + 0.4, "co2_concentration": 420.0 + 2.0 * (YEARS - 2025.0)})


@lru_cache(maxsize=None)
def baseline():
    rows = list(csv.DictReader(open(FIX, encoding="utf-8")))
    out = {}
    for r in rows:
        out.setdefault(r["setting"], []).append(r)
    return out


@lru_cache(maxsize=None)
def slice_run(setting: str, cap):
    params = SETTINGS_B[setting][1]
    return run_slice(SliceConfig(damage="central", gate=params, dc=DCParams(eta_cap=cap)), stand_in(), t1=2100.0)


def yearly(res):
    return [i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9]


def test_default_is_off_and_paper_value_is_exported():
    from f3.sectors import s4_datacentre as m
    assert DCParams().eta_cap is None
    assert m.PAPER_ETA_CAP == PAPER


# ------------------------------------------------------------------------------------------------------ (1) OFF equals the recorded results
@pytest.mark.parametrize("setting", list(SETTINGS_B))
def test_off_equals_the_recorded_results_to_1e_9(setting):
    res = slice_run(setting, None)
    ix = yearly(res)
    rows = baseline()[setting]
    assert len(rows) == len(ix)
    cols = {"s3_ai.gwp": ("s3_ai", "gwp"), "s3_ai.compute_stock": ("s3_ai", "compute_stock"), "s3_ai.usable_compute": ("s3_ai", "usable_compute"),
            "s3_ai.hardware": ("s3_ai", "hardware"), "s4_datacentre.e_dc_demand": ("s4_datacentre", "e_dc_demand"),
            "s4_datacentre.e_dc": ("s4_datacentre", "e_dc"), "s4_datacentre.supply_ratio": ("s4_datacentre", "supply_ratio")}
    for c, key in cols.items():
        ref = np.array([float(r[c]) for r in rows])
        got = res.series[key][ix]
        assert np.max(np.abs(got - ref) / np.maximum(np.abs(ref), 1e-300)) <= 1e-9, (setting, c)


# ------------------------------------------------------------------------------------------------------ (2) the cap is respected
def test_cap_is_respected_over_a_grid_and_the_control_fails_when_off():
    dp_on, dp_off = DCParams(eta_cap=PAPER), DCParams()
    Q = initial_compute_stock(GP)
    grid = GP.H0 * np.logspace(0, 8, 60)
    e_on = np.array([e_dc_twh(Q, h, GP, dp_on) for h in grid])
    e_off = np.array([e_dc_twh(Q, h, GP, dp_off) for h in grid])
    eta_on = Q / (e_on * J_PER_TWH / dp_on.pue)                                    # eta implied by the demand
    eta_off = Q / (e_off * J_PER_TWH / dp_off.pue)
    assert np.all(eta_on <= PAPER * (1 + 1e-12))
    assert np.max(eta_off) > PAPER                                                  # control: with the cap OFF the same grid exceeds it, so the assertion above can fail
    binding = grid * eta_0(GP, dp_on) / GP.H0 > PAPER
    assert binding.any() and (~binding).any()
    assert np.allclose(e_on[binding], Q / PAPER * dp_on.pue / J_PER_TWH, rtol=1e-12)
    assert np.allclose(e_on[~binding], e_off[~binding], rtol=1e-12)


def test_a_non_positive_cap_is_refused():
    for bad in (0.0, -1.0, float("nan")):
        with pytest.raises(ValueError):
            e_dc_twh(1e28, 1e18, GP, DCParams(eta_cap=bad))


# ------------------------------------------------------------------------------------------------------ (3) a cap that does not bind / one that does
@pytest.mark.parametrize("setting", list(SETTINGS_B))
def test_the_paper_cap_does_not_bind_inside_s3s_hardware_range(setting):
    off, on = slice_run(setting, None), slice_run(setting, PAPER)
    hw = off.series[("s3_ai", "hardware")]
    assert np.max(hw) <= GP.H_max * (1 + 1e-12)
    assert np.max(hw) * eta_0(GP, DCParams()) / GP.H0 < PAPER                       # the hand check: the cap point lies above S3's maximum hardware
    for key in (("s4_datacentre", "e_dc_demand"), ("s4_datacentre", "e_dc"), ("s4_datacentre", "supply_ratio"), ("s3_ai", "gwp"), ("s3_ai", "compute_stock")):
        assert np.allclose(off.series[key], on.series[key], rtol=1e-12, atol=0.0), (setting, key)


def test_a_cap_that_binds_lowers_demand_and_never_raises_it():
    """Named output e_dc_demand, window 2025-2100, standard settings: a low cap (2x eta_0) binds once hardware doubles."""
    low_cap = 2.0 * eta_0(GP, DCParams())
    off = slice_run("B0_default", None)
    p = SETTINGS_B["B0_default"][1]
    on = run_slice(SliceConfig(damage="central", gate=p, dc=DCParams(eta_cap=low_cap)), stand_in(), t1=2100.0)
    d_off, d_on = off.series[("s4_datacentre", "e_dc_demand")], on.series[("s4_datacentre", "e_dc_demand")]
    assert np.all(d_on <= d_off * (1 + 1e-9))
    assert np.any(d_on < d_off * (1 - 1e-6))                                        # strictly lower at least once
    assert not np.any(d_off < d_off * (1 - 1e-6))                                   # control: OFF against OFF is never strictly lower


# ------------------------------------------------------------------------------------------------------ (4) A2.5 and B1 unchanged
def test_a25_zero_compute_growth_with_the_cap_set():
    t = np.arange(2025.0, 2031.0)
    src = ReplaySector("src", t, {"cs": np.full(len(t), initial_compute_stock(GP)), "hw": np.full(len(t), GP.H0), "sup": np.full(len(t), 3e4)},
                       {"cs": "FLOP/year", "hw": "FLOP/year/USD", "sup": "TWh/year"})
    m = Model([src, DataCentre(GP, DCParams(eta_cap=PAPER))],
              [Coupling("src", "cs", "s4_datacentre", "compute_stock"), Coupling("src", "hw", "s4_datacentre", "hardware"), Coupling("src", "sup", "s4_datacentre", "supply")],
              t0=2025.0, t1=2030.0, dt=0.25)
    assert np.allclose(m.run().series[("s4_datacentre", "e_dc_demand")], IEA_2025_TWH, rtol=1e-12)


def test_a25_unlimited_electricity_makes_b1_inactive_with_the_cap_set():
    res = run_slice(SliceConfig(damage="central", dc=DCParams(eta_cap=PAPER, supply_scale=math.inf)), stand_in(), t1=2100.0)
    assert np.all(res.series[("s4_datacentre", "supply_ratio")] == 1.0)


def test_b1_direction_unchanged_by_the_cap_that_does_not_bind():
    """The B1 sign test recorded as failed in test_m2_slice stays as it is; here only that the cap adds no change to the two supply cases."""
    for scale in (1.0, 0.5):
        a = run_slice(SliceConfig(damage="central", dc=DCParams(supply_scale=scale)), stand_in(), t1=2100.0)
        b = run_slice(SliceConfig(damage="central", dc=DCParams(supply_scale=scale, eta_cap=PAPER)), stand_in(), t1=2100.0)
        assert np.allclose(a.series[("s3_ai", "compute_stock")], b.series[("s3_ai", "compute_stock")], rtol=1e-12)


# ------------------------------------------------------------------------------------------------------ (5) bounds
@pytest.mark.parametrize("cap", [None, PAPER, 1e12, 1e10, 1e9])
def test_demand_is_finite_and_non_negative_over_the_cap_grid(cap):
    for setting in SETTINGS_B:
        p = SETTINGS_B[setting][1]
        res = run_slice(SliceConfig(damage="central", gate=p, dc=DCParams(eta_cap=cap)), stand_in(), t1=2100.0)
        for n in ("e_dc_demand", "e_dc", "supply_ratio"):
            v = res.series[("s4_datacentre", n)]
            assert np.all(np.isfinite(v)) and np.all(v >= 0), (cap, setting, n)
