"""Link 3 (warming to World3 land yield; health not built): readings in docs/link3-link4-tests.md, written before the code."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pytest

from f3.core import Model
from f3.sectors.world3 import STATE_COLUMNS, _initial_inputs, build_world3
from f3.sectors.world3_group import World3Group

C = {"low": 0.031, "central": 0.04925, "high": 0.074}
T2025 = 1.35


def recorded(t: float) -> float:                         # a smooth stand-in with the recorded end points (1.35 K in 2025, 2.86 K in 2100); exact values are used in the report
    return T2025 + (2.86 - T2025) * max(0.0, t - 2025.0) / 75.0


@lru_cache(maxsize=None)
def run(option=None, path="recorded", damage=None, mutate=False):
    warming = {"recorded": recorded, "flat": lambda t: T2025, "step": lambda t: T2025 + (1.0 if t > 2025.0 + 1e-9 else 0.0)}[path]
    sectors, couplings = build_world3("2004")
    kw = {}
    if option is not None:
        kw.update(yield_option=option, warming=warming, _mutate_unit_yield=mutate)
    if damage is not None:
        kw.update(damage_option=damage, warming=warming)
    g = World3Group(sectors, couplings, _initial_inputs(sectors, 1900.0), STATE_COLUMNS, **kw)
    res = Model([g], [], t0=1900.0, t1=2100.0, dt=0.25).run()
    out = {n: np.asarray(res.series[(g.name, n)], dtype=float) for n in list(STATE_COLUMNS) + ["io", "ly"]}
    out["time"] = np.asarray(res.time, dtype=float)
    out["mult"] = np.asarray(g.yield_mult_history, dtype=float)
    return out


def states_equal(a, b, upto=None, tol=1e-9):
    m = slice(None) if upto is None else (a["time"] <= upto + 1e-9)
    for n in STATE_COLUMNS:
        np.testing.assert_allclose(b[n][m], a[n][m], rtol=tol, atol=0, err_msg=n)


def test_l3t1_off_equals_the_group_alone_and_l3t2_flat_warming_changes_nothing():
    base = run()
    assert np.all(base["mult"] == 1.0)
    states_equal(base, run("central", path="flat"))


@pytest.mark.parametrize("option", ["low", "central", "high"])
def test_l3t3_the_multiplier_is_the_stated_one(option):
    r = run(option, path="step")
    after = r["mult"][r["time"][1:] > 2026.0]
    np.testing.assert_allclose(after, 1.0 - C[option], rtol=0, atol=1e-12)
    assert np.all(r["mult"][r["time"][1:] <= 2025.0] == 1.0)


def test_l3t4_sign_and_order():
    off = run()["ly"][-1]
    lo, ce, hi = (run(o)["ly"][-1] for o in ("low", "central", "high"))
    assert hi < ce < lo < off


def test_l3t4_control_with_the_multiplier_forced_to_one_the_comparison_fails():
    assert not (run("central", mutate=True)["ly"][-1] < run()["ly"][-1])


def test_l3t5_nothing_changes_before_2025():
    states_equal(run(), run("high"), upto=2025.0)


def test_l3t6_with_output_damage_on_as_well():
    r = run("central", damage="central")
    for n in STATE_COLUMNS:
        assert np.all(np.isfinite(r[n])) and np.all(r[n] >= 0.0), n
    assert r["ly"][-1] < run(damage="central")["ly"][-1]
