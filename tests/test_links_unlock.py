"""Readings of docs/links-unlock-tests.md, written 2026-11-26 before the code and before any result (except where the document says a number was already seen)."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pytest

from f3.core import Model
from f3.sectors.world3 import STATE_COLUMNS, _initial_inputs, build_world3
from f3.sectors.world3_group import World3Group

fair = pytest.importorskip("fair")
D = {"central": (0.001, 0.002, 0.013, 0.037, 0.070), "high": (0.003, 0.013, 0.045, 0.101, 0.180), "low": (0.000, -0.003, -0.007, -0.012, -0.018)}
PATHS = {"recorded": lambda t: 1.35 + 1.51 * max(0.0, t - 2025.0) / 75.0, "flat": lambda t: 1.35, "step": lambda t: 4.0 if t > 2025.0 + 1e-9 else 2.0}


@lru_cache(maxsize=None)
def run(mortality=None, path="recorded", mutate=False, yield_option=None, damage=None, ai_cap=None):
    kw = {}
    if mortality is not None:
        kw.update(mortality_option=mortality, warming=PATHS[path], _mutate_unit_mortality=mutate)
    if yield_option is not None:
        kw.update(yield_option=yield_option, warming=PATHS[path])
    if damage is not None:
        kw.update(damage_option=damage, warming=PATHS[path])
    if ai_cap is not None:
        from f3.sectors import link4_ai_uplift as m
        kw["ai_uplift"] = m.as_callable(m.bounded_uplift(m.s3_uplift(), m.SOURCED_CAPS[ai_cap]))
    sectors, couplings = build_world3("2004")
    g = World3Group(sectors, couplings, _initial_inputs(sectors, 1900.0), STATE_COLUMNS, **kw)
    res = Model([g], [], t0=1900.0, t1=2100.0, dt=0.25).run()
    out = {n: np.asarray(res.series[(g.name, n)], dtype=float) for n in list(STATE_COLUMNS) + ["io"]}
    out["time"] = np.asarray(res.time, dtype=float)
    out["pop"] = sum(out[p] for p in ("p1", "p2", "p3", "p4"))
    out["mm"] = np.asarray(g.mortality_mult_history, dtype=float)
    return out


def same(a, b, upto=None):
    m = slice(None) if upto is None else (a["time"] <= upto + 1e-9)
    for n in STATE_COLUMNS:
        np.testing.assert_allclose(b[n][m], a[n][m], rtol=1e-9, atol=0, err_msg=n)


# ---- link 3, health ----
def test_l3h_t1_t2_off_and_flat_warming():
    assert np.all(run()["mm"] == 1.0)
    same(run(), run("central", path="flat"))


@pytest.mark.parametrize("o", ["low", "central", "high"])
def test_l3h_t3_stated_multiplier(o):
    r = run(o, path="step")
    np.testing.assert_allclose(r["mm"][r["time"][1:] > 2026.0], (1 + D[o][3]) / (1 + D[o][1]), rtol=0, atol=1e-12)


def test_l3h_t4_sign_and_order_and_control():
    off, lo, ce, hi = (run(o)["pop"][-1] for o in (None, "low", "central", "high"))
    assert hi < ce < off and lo >= off
    assert not (run("central", mutate=True)["pop"][-1] < off)


def test_l3h_t5_t6_before_2025_and_bounds():
    same(run(), run("high"), upto=2025.0)
    r = run("high", yield_option="high", damage="central")
    for n in STATE_COLUMNS:
        assert np.all(np.isfinite(r[n])) and np.all(r[n] >= 0.0), n


# ---- link 4, sourced caps ----
def test_l4s_t1_t2_values_and_cap():
    from f3.sectors import link4_ai_uplift as m
    assert m.SOURCED_CAPS == {"acemoglu_2024": 0.0007, "oecd_low": 0.0025, "oecd_high": 0.006, "goldman_world": 0.0125}
    u = m.s3_uplift()
    for cap in m.SOURCED_CAPS.values():
        ub = m.bounded_uplift(u, cap)
        assert all(ub[y] <= ub[y - 1] * (1 + cap) * (1 + 1e-12) for y in range(2026, 2100))


def test_l4s_t3_order_in_2040():
    io = [float(run(ai_cap=k)["io"][np.argmin(np.abs(run()["time"] - 2040.0))]) for k in ("acemoglu_2024", "oecd_low", "oecd_high", "goldman_world")]
    assert io[0] < io[1] < io[2] < io[3]


# ---- link 6, comparison with the IEA ----
def dc():
    from f3.sectors import link6_dc_emissions as m
    used, k = m.electricity_used_twh(0.15), m.intensity_kg_per_kwh()
    return m, used, {y: used[y] * k[y] for y in (2030, 2035)}          # TWh x kg/kWh = Mt


def test_l6v_t1_electricity_2030_within_10_percent_of_iea():
    assert abs(dc()[1][2030] / 945.0 - 1.0) <= 0.10


@pytest.mark.xfail(strict=True, reason="L6V-T2 FAILED (recorded 2026-11-26, audit/links-unlock.md): 1,863 TWh in 2035 against the IEA's 1,200 (+55%); a constant 15% a year overshoots after 2030. Tolerance unchanged.")
def test_l6v_t2_electricity_2035_within_25_percent_of_iea():
    assert abs(dc()[1][2035] / 1200.0 - 1.0) <= 0.25


@pytest.mark.xfail(strict=True, reason="L6V-T3 FAILED on 2035 (recorded 2026-11-26): 347 Mt in 2030 against 320 (+8%, inside 30%) but 637 Mt in 2035 against 300 (+112%). Tolerance unchanged.")
def test_l6v_t3_co2_within_30_percent_of_iea():
    mt = dc()[2]
    assert abs(mt[2030] / 320.0 - 1.0) <= 0.30 and abs(mt[2035] / 300.0 - 1.0) <= 0.30


def test_l6v_t4_baseline_is_the_iea_2025_figure():
    assert dc()[0].BASELINE_TWH == 485.0


# ---- link 7, reference run calibrated by others ----
def l7():
    from f3.sectors import link7_world3_emissions as m
    return m


@pytest.mark.xfail(strict=True, reason="L7N-T1 FAILED (recorded 2026-11-26): rms log distance to observed GDP 0.2457 for the partial, unverified copy of Recalibration23 against 0.1775 for the standard run. It is not used as a reference.")
def test_l7n_t1_closer_to_observed_gdp_than_the_standard_run():
    m = l7()
    assert m.gdp_distance(m.world3_io(**m.NEBEL_PARTIAL)) < 0.1775


@pytest.mark.xfail(strict=True, reason="L7N-T2 FAILED (recorded 2026-11-26, reported only since T1 failed): largest hindcast error 40.1% (2024), 35 of 55 years outside 10%.")
def test_l7n_t2_hindcast_within_10_percent():
    m = l7()
    io, obs = m.world3_io(**m.NEBEL_PARTIAL), m.observed_ffi_gt()
    a, b = m.fit_intensity(obs, io)
    # corrected 2026-11-26 before the first run: fit_intensity returns k(t) = exp(a + b t) with t the calendar year (my test had t - 2000); the reading is unchanged
    err = [abs(io[y] * np.exp(a + b * y) / obs[y] - 1.0) for y in range(1970, 2025)]
    assert max(err) <= 0.10


@pytest.mark.xfail(strict=True, reason="L7N-T3 FAILED (recorded 2026-11-26, reported only): step of -5.6% at the join against 5%.")
def test_l7n_t3_join_step_within_5_percent():
    m = l7()
    io = m.world3_io(**m.NEBEL_PARTIAL)
    assert abs(m.replacement_gt_b(io)[2026] / m.prescribed_ffi_gt(2025) - 1.0) <= 0.05


# ---- link 6, post-hoc: build rate that follows the IEA Base Case (calibration, not validation) ----
def test_l6c_t1_single_entry_schedule_equals_the_plain_setting():
    from f3.sectors import link6_dc_emissions as m
    a, b = m.electricity_used_twh(0.15), m.electricity_used_twh(0.15, schedule=((2025.0, 0.15),))
    assert all(abs(a[y] - b[y]) <= 1e-12 * a[y] for y in a)


def test_l6c_t2_electricity_follows_the_iea_base_case():
    from f3.sectors import link6_dc_emissions as m
    u = m.electricity_used_twh(0.15, schedule=m.IEA_BASE_SCHEDULE)
    assert abs(u[2030] / 945.0 - 1.0) <= 0.10 and abs(u[2035] / 1200.0 - 1.0) <= 0.10


def test_l6c_t3_co2_2035_within_30_percent_of_iea():
    from f3.sectors import link6_dc_emissions as m
    u, k = m.electricity_used_twh(0.15, schedule=m.IEA_BASE_SCHEDULE), m.intensity_kg_per_kwh()
    assert abs(u[2035] * k[2035] / 300.0 - 1.0) <= 0.30
