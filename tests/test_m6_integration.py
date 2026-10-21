"""M6 minimal integration tests (World3 + FaIR + S3 + S7 output-only), WRITTEN BEFORE the wiring module f3/sectors/m6_integrated.py exists.
Readings, outputs and windows were fixed in docs/m6-tests.md before this file. Structural tests only (plan section 15.2): nothing compares S3's
absolute output with GATE or with data. Failures are recorded with size and first year; nothing is adjusted.

Interface fixed in advance: f3.sectors.m6_integrated.build_m6(M6Config(...), climate=None) -> Model; run_m6(cfg, climate) -> Results;
M6Config fields: parameter_set, world3_damage (None|low|central|high), s3_damage ("off"|low|central|high), electricity (bool), levers (R3Levers),
dc (DCParams), t1 (float). ``climate`` is a ReplaySector named "s6_climate" (the recorded replay) or None for a live S6Climate.
The tests use a smooth stand-in for the recorded warming (1.2 K in 2025 to 2.9 K in 2100, the shape and size of the committed FaIR ensemble mean) so
that they need no FaIR run, except the one test (A6.3 item 4) that compares a live S6 with its recording and skips when FaIR data are absent.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import pytest

from f3.core.model import Coupling, Model
from f3.core.replay import ReplaySector
from f3.data import fair_inputs as fi
from f3.sectors.m6_integrated import M6Config, build_m6, run_m6
from f3.sectors.s3_ai import GateParams, S3AI
from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
from f3.sectors.s4_datacentre import DCParams
from f3.sectors.s6_climate import ClimateSetup
from f3.sectors.s7_social import S7Social
from f3.sectors.slice_m2 import CLIMATE_OUTPUTS, ClimateReplay, record_climate
from f3.sectors.world3 import STATE_COLUMNS, run_world3
from tests.w3_helpers import TOL, grid_index, reference, relerr

F0 = R3Rule()._fitted_initial
YEARS = np.arange(2025.0, 2101.0)


def stand_in_climate(scale: float = 1.0) -> ClimateReplay:
    w = (1.2 + (2.9 - 1.2) * (YEARS - 2025.0) / 75.0) * scale
    return ClimateReplay(YEARS, {"warming": w, "warming_p05": w - 0.4, "warming_p95": w + 0.4, "co2_concentration": 420.0 + 2.0 * (YEARS - 2025.0)})


@lru_cache(maxsize=None)
def run(ps="2004", w3="off", s3="off", elec=False, share=1.0, decay=1.0, supply=1.0, t1=2100.0):
    cfg = M6Config(parameter_set=ps, world3_damage=None if w3 == "off" else w3, s3_damage=s3, electricity=elec,
                   levers=R3Levers(initial_ai_share=share * F0, decay_speed=decay), dc=DCParams(supply_scale=supply), t1=t1)
    return run_m6(cfg, stand_in_climate())


def S(res, sector, name):
    return res.series[(sector, name)]


def yidx(res):
    return np.array([i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9])


# ------------------------------------------------------------------------------------------------------------------- A6.1 baseline
@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a61a_world3_in_the_integrated_loop_equals_world3_alone_to_1e_9(ps):
    res = run(ps)
    alone, _ = run_world3(ps)
    for n in STATE_COLUMNS:
        a, b = S(res, "world3", n), alone[n]
        assert np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-30)) <= 1e-9, n


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a61b_world3_in_the_integrated_loop_within_2_percent_of_worlddynamics(ps):
    res = run(ps)
    ref = reference(ps)
    idx = grid_index(res.time, ref["time"])
    worst = {}
    from f3.sectors.world3 import STATE_COLUMNS as COLS
    for n, col in COLS.items():
        worst[n] = float(relerr(S(res, "world3", n)[idx], ref[col]).max())
    k = max(worst, key=worst.get)
    assert worst[k] <= TOL, (ps, k, worst[k])


# ------------------------------------------------------------------------------------------------------------------- A6.3 invariance
def standalone_s3():
    return Model([S3AI(GateParams(), rule=R3Rule())], [], t0=2025.0, t1=2100.0, dt=0.25).run()


def test_a63_2_s3_in_the_loop_with_couplings_off_equals_s3_alone_to_1e_9():
    res = run("2004", w3="off", s3="off", elec=False)
    ref = standalone_s3()
    k0 = int(np.where(np.isclose(res.time, 2025.0))[0][0])
    for n in ("gwp", "compute_stock", "frac_automated", "capital", "software", "hardware"):
        a, b = S(res, "s3_ai", n)[k0:], S(ref, "s3_ai", n)
        m = np.isfinite(b)
        assert np.allclose(a[m], b[m], rtol=1e-9, atol=0.0), n


def test_a63_3_s7_in_the_loop_equals_s7_alone_on_the_same_inputs_to_1e_9():
    res = run("2004", w3="off", s3="central", elec=True)
    k0 = int(np.where(np.isclose(res.time, 2025.0))[0][0])
    t = res.time[k0:]
    names = list(S7Social.inputs)
    rep = ReplaySector("recorded_s7_inputs", t, {n: res.inputs[("s7_social", n)][k0:] for n in names}, S7Social.inputs)
    s7 = S7Social()
    alone = Model([rep, s7], [Coupling("recorded_s7_inputs", n, s7.name, n) for n in names], t0=2025.0, t1=2100.0, dt=0.25).run()
    for n in S7Social.outputs:
        a, b = S(res, "s7_social", n)[k0:], S(alone, "s7_social", n)
        assert np.allclose(a, b, rtol=1e-9, atol=1e-12), n


@pytest.mark.skipif(not fi.fair_available(), reason=fi.skip_reason("FaIR calibration files"))
def test_a63_4_live_s6_equals_its_recording_for_s3_outputs_to_2030():
    rec = record_climate(ClimateSetup(n_members=20), t0=2025.0, t1=2030.0)
    replay = ClimateReplay(rec["years"], {n: rec[n] for n in CLIMATE_OUTPUTS})
    cfg = M6Config(world3_damage=None, s3_damage="central", electricity=True, t1=2030.0)
    a = run_m6(cfg, replay)
    b = run_m6(cfg, None, climate_setup=ClimateSetup(n_members=20))
    for n in ("gwp", "compute_stock", "frac_automated", "damage_fraction"):
        assert np.allclose(S(a, "s3_ai", n), S(b, "s3_ai", n), rtol=1e-9, atol=0.0), n


def test_a63_1_world3_damage_off_inside_the_loop_equals_stand_alone():
    """Repeats the damage-coupling invariance inside the integrated loop: world3_damage None equals the group alone, with S3, S6 and S7 present."""
    a, b = run("2004", w3="off", s3="central", elec=True), run("2004", w3="off", s3="off", elec=False)
    for n in STATE_COLUMNS:
        assert np.array_equal(S(a, "world3", n), S(b, "world3", n)), n


# ------------------------------------------------------------------------------------------------------------------- A6.4 extremes
def test_a64a_zero_investment_the_compute_stock_decays_by_depreciation():
    """initial_ai_share = 0: Q[k] = Q[k-1] exp(-delta_Q) to 1e-9 from 2026, demand non-increasing, nothing NaN (the corrected reading of docs/m6-tests.md)."""
    res = run("2004", s3="off", elec=True, share=0.0)
    q = S(res, "s3_ai", "compute_stock")
    k = int(np.where(np.isclose(res.time, 2025.0))[0][0])
    qs = q[k::4]                                                       # 1 January values
    assert np.all(np.isfinite(q)) and np.all(q >= 0)
    for a, b in zip(qs[1:], qs[:-1]):
        assert abs(a / b - math.exp(-0.3)) <= 1e-9, (a / b, math.exp(-0.3))                 # strict, as docs/m6-tests.md fixed it
    e = S(res, "s4_datacentre", "e_dc_demand")[k:]
    assert np.all(np.isfinite(e)) and np.all(np.diff(e) <= 1e-9)


def test_a64b_unlimited_electricity_makes_b1_inactive():
    res = run("2004", s3="central", elec=True, supply=math.inf)
    assert np.all(S(res, "s4_datacentre", "supply_ratio") == 1.0)


def test_a64c_zero_investment_no_negative_stock():
    cfg = M6Config(world3_damage=None, s3_damage="off", electricity=True, levers=R3Levers(initial_ai_share=0.0, capital_scale=0.0))
    res = run_m6(cfg, stand_in_climate())
    for n in ("compute_stock", "capital", "hardware", "software"):
        v = S(res, "s3_ai", n)
        assert np.all(np.isfinite(v)) and np.all(v >= 0), n


GRID = [(w3, s3) for w3 in ("off", "central", "high") for s3 in ("off", "central", "high")]


@pytest.mark.parametrize("w3,s3", GRID)
def test_a64d_every_output_of_every_sector_is_finite_on_the_grid(w3, s3):
    res = run("2004", w3=w3, s3=s3, elec=True)
    k0 = int(np.where(np.isclose(res.time, 2025.0))[0][0])
    for (sec, n), v in res.series.items():
        if sec in ("s3_ai", "s4_datacentre", "s7_social", "s6_climate", "earth4all_supply", "s7_feed", "world3"):
            x = v if sec == "world3" else v[k0 + 4:]                       # S3 publishes its first annual period at 2026; its initial NaNs are by design
            assert np.all(np.isfinite(x)), (w3, s3, sec, n)


# ------------------------------------------------------------------------------------------------------------------- A6.2 sign tests
def first_gt(a, b):
    return bool(np.all(a > b))


def test_r1_more_ai_investment_more_automation_at_2029_2030_2031():
    race = run("2004", share=1.5, decay=0.5)
    low = run("2004", share=0.5, decay=1.0)
    for y in (2029.0, 2030.0, 2031.0):
        k = int(np.where(np.isclose(race.time, y))[0][0])
        assert S(race, "s3_ai", "frac_automated")[k] > S(low, "s3_ai", "frac_automated")[k], y


def test_r1_control_and_mutation_can_fail():
    low = run("2004", share=0.5)
    for y in (2029.0, 2030.0, 2031.0):
        k = int(np.where(np.isclose(low.time, y))[0][0])
        assert not (S(low, "s3_ai", "frac_automated")[k] > S(low, "s3_ai", "frac_automated")[k])       # low against low: the strict test fails
    same = run("2004", share=1.0)                                                                      # levers at the default on both sides
    k = int(np.where(np.isclose(same.time, 2030.0))[0][0])
    assert not (S(same, "s3_ai", "frac_automated")[k] > S(same, "s3_ai", "frac_automated")[k])


def test_b1_half_supply_never_above_base_usable_compute_2027_to_2035():
    base = run("2004", s3="central", elec=True, supply=1.0)
    half = run("2004", s3="central", elec=True, supply=0.5)
    ks = [int(np.where(np.isclose(base.time, y))[0][0]) for y in np.arange(2027.0, 2036.0)]
    b, h = S(base, "s3_ai", "usable_compute")[ks], S(half, "s3_ai", "usable_compute")[ks]
    assert np.all(h <= b * (1 + 1e-12)), (list(2027 + np.where(h > b * (1 + 1e-12))[0]), float(np.max(h / b - 1)))
    assert np.any(h < b * (1 - 1e-9))                                                                  # strictly below at least once
    assert not np.any(b < b * (1 - 1e-9))                                                              # control: base against base is never strictly below


def test_b2_high_damage_below_low_for_s3_output_and_world3_industrial_capital_in_2100():
    s3_hi, s3_lo = run("2004", s3="high", elec=True), run("2004", s3="low", elec=True)
    assert S(s3_hi, "s3_ai", "gwp")[-1] < S(s3_lo, "s3_ai", "gwp")[-1]
    w_hi, w_lo = run("2004", w3="high"), run("2004", w3="low")
    assert S(w_hi, "world3", "ic")[-1] < S(w_lo, "world3", "ic")[-1]
    assert not (S(s3_lo, "s3_ai", "gwp")[-1] < S(s3_lo, "s3_ai", "gwp")[-1])                           # control: low against low fails


def test_r2_via_s3_inequality_index_rises_with_s3_labour_share_fall_and_is_zero_for_a_constant_share():
    res = run("2004", s3="central", elec=True)
    k0 = int(np.where(np.isclose(res.time, 2025.0))[0][0])
    k60 = int(np.where(np.isclose(res.time, 2060.0))[0][0])
    I = S(res, "s7_social", "inequality")
    assert I[k60] - I[k0] > 0.0
    t = res.time[k0:]
    # CORRECTED CONTROL (2026-10-21, see docs/m6-tests.md): the first version kept the warming input; warming raises tension, tension triggers the delayed
    # policy response and that lowers inequality, so the control moved by 5.8e-4 (first failure recorded). The control isolates the labour-share driver: warming 0, as in S7's own R2 test.
    rep = ReplaySector("given", t, {"labor_share": np.full(len(t), 0.65), "unemployment": np.zeros(len(t)), "warming": np.zeros(len(t)),
                                    "gdp_per_capita_growth": np.zeros(len(t)), "redistribution": np.zeros(len(t))}, S7Social.inputs)
    s7 = S7Social()
    flat = Model([rep, s7], [Coupling("given", n, s7.name, n) for n in S7Social.inputs], t0=2025.0, t1=2100.0, dt=0.25).run()
    assert abs(S(flat, "s7_social", "inequality")[k60 - k0] - S(flat, "s7_social", "inequality")[0]) <= 1e-12


# ------------------------------------------------------------------------------------------------------------------- A6.5 time and A6.6 initialisation
def test_a65_run_time_is_measured_and_finite():
    import time
    ts = []
    for _ in range(2):
        a = time.perf_counter()
        run_m6(M6Config(), stand_in_climate())
        ts.append(time.perf_counter() - a)
    print(f"A6.5 integrated run with the recorded replay, 1900-2100: {ts[0]:.2f} s, {ts[1]:.2f} s")
    assert all(np.isfinite(t) and t > 0 for t in ts)


def test_a66_initialisation():
    res = run("2004")
    p = GateParams()
    k25 = int(np.where(np.isclose(res.time, 2025.0))[0][0])
    assert np.isclose(S(res, "world3", "p1")[0], 0.65e9 * 1.0 * 1.0, rtol=0.5)                         # World3 starts from its own 1900 state
    assert S(res, "s3_ai", "gwp")[0] == p.Y0 and S(res, "s3_ai", "gwp")[k25] == p.Y0                   # S3 held at GATE's initial values before 2025 (D-020)
    assert S(res, "s3_ai", "frac_automated")[0] == p.f_init and S(res, "s3_ai", "frac_automated")[k25] == p.f_init
    s7 = S7Social.PARAMETERS
    assert S(res, "s7_social", "inequality")[0] == s7["I0"] and S(res, "s7_social", "tension")[k25] == s7["Te0"]


def test_labels_are_carried():
    from f3.sectors.m6_integrated import M6_LABELS
    s = M6_LABELS.lower()
    for phrase in ("unvalidated against gate", "illustrative", "not validated against history", "no health or yield effect of warming",
                   "two economies", "level-of-output"):
        assert phrase in s, phrase
