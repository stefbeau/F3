"""M2 slice tests A2.2 to A2.6 and the loop-sign tests. Fixed in docs/tracks/track-a-plan.md section 2 BEFORE any result was produced.
Failures are results, not defects to tune.

ENSEMBLE: climate for these tests is a recorded S6Climate run with the documented 20-member development subset (first 20 members of the
published ensemble); the published Demo 0 grid uses all 841 (D-021 editor note). The recording is exact for this slice (S6 has no inputs).
Readings of the plan's sentences used below (written before the first run):
* A2.4: (i) S3-S4 coupling off and damages off; (ii) S3-S4 coupling present but inactive (unlimited supply) and damages off. Each equals the
  standalone S3 driven by R3 to 1e-9 relative, on every S3 output.
* A2.6: outputs gwp, compute_stock, frac_automated, e_dc, warming at every year 2025..2100; relative difference <= 1e-3 (0.1%).
* B1: supply_scale 0.5 against 1.0: compute_stock never higher at any year, strictly lower at 2040, mean annual log growth 2026-2040 lower.
* R1: initial_ai_share 0.9 x the fitted value against 1.1 x: compute_stock and frac_automated higher at 2065 (full slice).
* B2: high against low damage: gwp in 2100 lower.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from f3.core.model import Coupling, Model
from f3.core.replay import ReplaySector
from f3.data import fair_inputs as fi
from f3.sectors.damages import damage_fraction
from f3.sectors.s3_ai import GateParams, S3AI
from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
from f3.sectors.s4_datacentre import IEA_2025_TWH, DataCentre, DCParams, initial_compute_stock
from f3.sectors.s6_climate import ClimateSetup
from f3.sectors.slice_m2 import SliceConfig, climate_replay, record_climate, run_slice

UNITS = {"warming": "K", "warming_p05": "K", "warming_p95": "K", "co2_concentration": "ppm"}


@pytest.fixture(scope="module")
def rec():
    if not fi.fair_available():
        pytest.skip(fi.skip_reason("FaIR calibration files"))
    return record_climate(ClimateSetup(n_members=20))


def S(res, sector, name):
    return res.series[(sector, name)]


def yearly(res):
    return [i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9]


def standalone():
    return Model([S3AI(GateParams(), rule=R3Rule())], [], t0=2025.0, t1=2100.0, dt=0.25).run()


def test_a22_initial_value_consistency():
    """A2.2 (plan 14.2a): the 2025 initial E_dc is within +-10% of 485 TWh. A consistency check of the calibration, not a validation."""
    flat = ReplaySector("s6_climate", np.array([2025.0, 2100.0]), {k: np.array([1.2, 3.0]) for k in UNITS}, UNITS)
    res = run_slice(SliceConfig(damage="off"), flat)
    e0 = S(res, "s4_datacentre", "e_dc_demand")[0]
    assert 0.9 * IEA_2025_TWH <= e0 <= 1.1 * IEA_2025_TWH, e0


def test_a24_invariance_coupling_off(rec):
    ref = standalone()
    for cfg in (SliceConfig(damage="off", electricity=False), SliceConfig(damage="off", electricity=True, dc=DCParams(supply_scale=math.inf))):
        res = run_slice(cfg, climate_replay(rec))
        for (sec, name), a in ref.series.items():
            b = res.series[(sec, name)]
            m = np.isfinite(a)
            assert np.allclose(a[m], b[m], rtol=1e-9, atol=0.0), (cfg, name)


def test_a25_zero_compute_growth_keeps_edc_constant():
    gp = GateParams()
    t = np.arange(2025.0, 2031.0)
    src = ReplaySector("src", t, {"cs": np.full(len(t), initial_compute_stock(gp)), "hw": np.full(len(t), gp.H0), "sup": np.full(len(t), 3e4)},
                       {"cs": "FLOP/year", "hw": "FLOP/year/USD", "sup": "TWh/year"})
    m = Model([src, DataCentre(gp, DCParams())],
              [Coupling("src", "cs", "s4_datacentre", "compute_stock"), Coupling("src", "hw", "s4_datacentre", "hardware"),
               Coupling("src", "sup", "s4_datacentre", "supply")], t0=2025.0, t1=2030.0, dt=0.25)
    assert np.allclose(S(m.run(), "s4_datacentre", "e_dc_demand"), IEA_2025_TWH, rtol=1e-12)


def test_a25_unlimited_electricity_makes_b1_inactive(rec):
    res = run_slice(SliceConfig(damage="central", dc=DCParams(supply_scale=math.inf)), climate_replay(rec))
    assert np.all(S(res, "s4_datacentre", "supply_ratio") == 1.0)
    off = run_slice(SliceConfig(damage="central", electricity=False), climate_replay(rec))
    for n in ("gwp", "compute_stock", "frac_automated"):
        assert np.allclose(S(res, "s3_ai", n), S(off, "s3_ai", n), rtol=1e-12)


def test_a26_step_halving(rec):
    a = run_slice(SliceConfig(), climate_replay(rec), dt=0.25)
    b = run_slice(SliceConfig(), climate_replay(rec), dt=0.125)
    ia, ib = yearly(a), yearly(b)
    worst = {}
    for sec, n in (("s3_ai", "gwp"), ("s3_ai", "compute_stock"), ("s3_ai", "frac_automated"), ("s4_datacentre", "e_dc"), ("s6_climate", "warming")):
        x, y = S(a, sec, n)[ia], S(b, sec, n)[ib]
        worst[n] = float(np.max(np.abs(x - y) / np.maximum(np.abs(x), 1e-300)))
    assert max(worst.values()) <= 1e-3, worst


def test_loop_sign_r1(rec):
    f0 = R3Rule()._fitted_initial
    lo = run_slice(SliceConfig(levers=R3Levers(initial_ai_share=0.9 * f0)), climate_replay(rec))
    hi = run_slice(SliceConfig(levers=R3Levers(initial_ai_share=1.1 * f0)), climate_replay(rec))
    k = yearly(lo)[40]
    assert S(hi, "s3_ai", "compute_stock")[k] > S(lo, "s3_ai", "compute_stock")[k]
    assert S(hi, "s3_ai", "frac_automated")[k] > S(lo, "s3_ai", "frac_automated")[k]


def test_loop_sign_b1(rec):
    base = run_slice(SliceConfig(), climate_replay(rec))
    low = run_slice(SliceConfig(dc=DCParams(supply_scale=0.5)), climate_replay(rec))
    i = yearly(base)
    cb, cl = S(base, "s3_ai", "compute_stock")[i], S(low, "s3_ai", "compute_stock")[i]
    assert np.all(cl <= cb * (1 + 1e-12))
    assert cl[15] < cb[15]
    assert np.mean(np.diff(np.log(cl[1:16]))) < np.mean(np.diff(np.log(cb[1:16])))


def test_loop_sign_b2(rec):
    lo = run_slice(SliceConfig(damage="low"), climate_replay(rec))
    hi = run_slice(SliceConfig(damage="high"), climate_replay(rec))
    assert S(hi, "s3_ai", "gwp")[-1] < S(lo, "s3_ai", "gwp")[-1]


def test_damage_function_anchors():
    assert damage_fraction(3.0, "low") == pytest.approx(0.0212, abs=1e-4)
    assert damage_fraction(3.0, "central") == pytest.approx(0.0310, abs=1e-4)
    assert damage_fraction(3.0, "high") == pytest.approx(0.0903, abs=1e-4)
    assert damage_fraction(4.5, "central") == pytest.approx(0.0697, abs=1e-4)
    assert damage_fraction(2.0, "off") == 0.0
    with pytest.raises(ValueError):
        damage_fraction(1.0, "growth")
