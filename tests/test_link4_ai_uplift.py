"""Link 4 (S3 output to World3 industrial output, bounded by a growth cap): readings in docs/link3-link4-tests.md, written before the code."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pytest

from f3.core import Model
from f3.sectors.world3 import STATE_COLUMNS, _initial_inputs, build_world3
from f3.sectors.world3_group import World3Group

CAPS = (0.01, 0.02, 0.05)


def l4():
    from f3.sectors import link4_ai_uplift as m
    return m


@lru_cache(maxsize=None)
def run(cap=None, ai_off=False, unit=False):
    kw = {}
    if cap is not None or unit:
        m = l4()
        u = {y: 1.0 for y in range(2025, 2101)} if unit else m.bounded_uplift(m.s3_uplift(ai_off=ai_off), cap)
        kw["ai_uplift"] = m.as_callable(u)
    sectors, couplings = build_world3("2004")
    g = World3Group(sectors, couplings, _initial_inputs(sectors, 1900.0), STATE_COLUMNS, **kw)
    res = Model([g], [], t0=1900.0, t1=2100.0, dt=0.25).run()
    out = {n: np.asarray(res.series[(g.name, n)], dtype=float) for n in list(STATE_COLUMNS) + ["io"]}
    out["time"] = np.asarray(res.time, dtype=float)
    return out


def at(r, name, year):
    return float(r[name][int(np.argmin(np.abs(r["time"] - year)))])


def test_l4t1_t2_off_and_unit_uplift_equal_the_group_alone():
    a, b = run(), run(unit=True)
    for n in STATE_COLUMNS:
        np.testing.assert_allclose(b[n], a[n], rtol=1e-9, atol=0, err_msg=n)


@pytest.mark.parametrize("cap", CAPS)
def test_l4t3_the_cap_is_respected(cap):
    m = l4()
    u = m.s3_uplift()
    ub = m.bounded_uplift(u, cap)
    assert ub[2025] == 1.0
    for y in range(2026, 2100):
        assert ub[y] <= ub[y - 1] * (1.0 + cap) * (1 + 1e-12) and ub[y] <= u[y] * (1 + 1e-12)
        if u[y] >= 1.0:
            assert ub[y] >= 1.0 - 1e-12
        if u[y] <= ub[y - 1] * (1.0 + cap):
            assert abs(ub[y] - u[y]) <= 1e-12 * u[y]


def test_l4_no_default_cap():
    with pytest.raises(TypeError):
        l4().bounded_uplift(l4().s3_uplift())


def test_l4t4_sign_and_order():
    off, c1, c5 = run(), run(0.01), run(0.05)
    for y in (2030, 2040):
        assert at(c1, "io", y) > at(off, "io", y) and at(c5, "io", y) >= at(c1, "io", y)


def test_l4t4_control_with_ai_investment_off_the_comparison_fails():
    assert not (at(run(0.05, ai_off=True), "io", 2040) > at(run(), "io", 2040))


@pytest.mark.parametrize("cap", CAPS)
def test_l4t5_bounds(cap):
    r = run(cap)
    for n in STATE_COLUMNS:
        assert np.all(np.isfinite(r[n])) and np.all(r[n] >= 0.0), n
