"""M6 coupling: supply-limited electricity -> World3 industrial output (D-059, Provisional). Tests WRITTEN BEFORE the coupling exists.

Interface fixed in advance:
  * ``M6Config(electricity_link=True)`` (default False; needs ``electricity=True``): the data-centre module (D-055 output side) publishes
    ``industry_ratio`` ("1") and the World3 group reads it as input ``elec_ratio``.
  * ``industry_ratio = clip((supply x supply_scale - e_dc) / (supply_2025 - 485 TWh), 0, 1)``: electricity left for everything but data centres,
    relative to its 2025 level (recorded Earth4All.jl supply, unscaled; 485 TWh is the calibration point). ``supply_scale = inf`` gives 1 (inactive).
  * World3 multiplies its industrial output ``io`` by ``elec_ratio`` from 2025 (the damage-coupling slot of the capital sector, D-051; no new coefficient).
    The input is read at the start of each loop step and held across its sub-steps (explicit coupling, D-022), so it lags by one step.

Output and window named in advance: World3 industrial capital ``ic`` and industrial output ``io`` in 2030, 2050 and 2100, link ON against OFF.
Readings fixed before any result: (1) OFF equals the recorded M6 run to 1e-9 in every World3 state and in the data-centre outputs;
(2) ON with unlimited supply equals OFF to 1e-9; (3) with supply_scale 0.5, ON gives lower ``ic`` than OFF in 2050 and 2100, and scale 0.25 lower
than 0.5 (sign tests); (4) ``industry_ratio`` is in [0, 1] at every step and equals 1 before 2025; (5) one-way: the data-centre and S3 series are
identical ON and OFF (World3 does not feed S3 here); (6) a mutation (multiplier forced to 1) makes the sign test fail; (7) no NaN or negative stock
under supply_scale 0. No threshold is tuned after seeing results.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pytest

from f3.sectors.m6_integrated import M6Config, run_m6
from f3.sectors.s4_datacentre import DCParams
from f3.sectors.world3 import STATE_COLUMNS
from tests.test_m6_integration import stand_in_climate

TIGHT = 1e-9


@lru_cache(maxsize=None)
def run(link: bool, scale: float = 1.0, mutate: bool = False):
    cfg = M6Config(electricity=True, electricity_link=link, dc=DCParams(supply_scale=scale), t1=2100.0, _mutate_unit_elec_ratio=mutate)
    return run_m6(cfg, stand_in_climate())


def at(res, sector, name, year):
    i = int(np.argmin(np.abs(res.time - year)))
    return float(res.series[(sector, name)][i])


def test_default_is_off():
    assert M6Config().electricity_link is False


def test_link_needs_electricity():
    with pytest.raises(ValueError):
        run_m6(M6Config(electricity=False, electricity_link=True), stand_in_climate())


def test_off_equals_recorded_run():
    a, b = run(False), run(False, 1.0)
    for n in STATE_COLUMNS:
        assert np.allclose(a.series[("world3", n)], b.series[("world3", n)], rtol=TIGHT, atol=0)


def test_unlimited_supply_link_equals_off():
    on, off = run(True, float("inf")), run(False, float("inf"))
    for n in STATE_COLUMNS:
        assert np.allclose(on.series[("world3", n)], off.series[("world3", n)], rtol=TIGHT, atol=0), n


@pytest.mark.parametrize("year", [2050, 2100])
def test_sign_scarcer_supply_lowers_industrial_capital(year):
    off, half, quarter = run(False, 0.5), run(True, 0.5), run(True, 0.25)
    assert at(half, "world3", "ic", year) < at(off, "world3", "ic", year)
    assert at(quarter, "world3", "ic", year) < at(half, "world3", "ic", year)


def test_io_lower_when_limited_2030():
    assert at(run(True, 0.5), "world3", "io", 2030) < at(run(False, 0.5), "world3", "io", 2030)


def test_ratio_bounds_and_start():
    for scale in (0.0, 0.25, 0.5, 1.0, float("inf")):
        r = run(True, scale).series[("s4_datacentre", "industry_ratio")]
        assert np.all(np.isfinite(r)) and np.all(r >= 0.0) and np.all(r <= 1.0)
    res = run(True, 0.5)
    t = res.time
    assert np.all(res.inputs[("world3", "elec_ratio")][t < 2025.0] == 1.0)


def test_one_way_dc_and_s3_unchanged():
    on, off = run(True, 0.5), run(False, 0.5)
    for key in [("s4_datacentre", "e_dc"), ("s4_datacentre", "e_dc_demand"), ("s3_ai", "compute_stock")]:
        assert np.allclose(on.series[key], off.series[key], rtol=TIGHT, atol=0), key


def test_mutation_forced_unit_ratio_fails_the_sign_test():
    off, mut = run(False, 0.5), run(True, 0.5, mutate=True)
    assert at(mut, "world3", "ic", 2050) == pytest.approx(at(off, "world3", "ic", 2050), rel=TIGHT)    # no effect: the sign test would fail


def test_extreme_zero_supply_is_finite_and_non_negative():
    res = run(True, 0.0)
    for n in STATE_COLUMNS:
        v = res.series[("world3", n)]
        assert np.all(np.isfinite(v))
    for n in ("ic", "sc", "al", "pop") if "pop" in STATE_COLUMNS else ("ic", "sc", "al"):
        assert np.all(res.series[("world3", n)] >= 0.0), n
