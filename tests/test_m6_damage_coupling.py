"""M6 coupling: climate damage -> World3 industrial output. Tests WRITTEN BEFORE the coupling exists (D-051; docs/m6-minimal-plan.md section 9).

Interface fixed in advance (section 9.2): ``run_world3(parameter_set, ..., damage_option=None, warming=None)``
  * ``damage_option``: None (OFF, the default) or "low" / "central" / "high" (f3.sectors.damages, D-007; level-of-output effects);
  * ``warming``: a callable year -> K (FaIR ensemble-mean warming above 1850-1900, from the RECORDED replay), or an array aligned with years;
    required when ``damage_option`` is not None. The multiplier acts from 2025 (D-020); before 2025 it is 1.
  * the multiplier is io = io_gross * (1 - Omega(T)), Omega(T) = c * T^2 (damages.damage_fraction), applied to World3's industrial output in
    the capital sector, so it acts through every link io has (service and industrial investment, agriculture, resources, population via iopc).
No new coefficient. Warming is held across the sub-steps of a loop step (explicit coupling, D-022).

Output and window NAMED IN ADVANCE for the sign test: industrial output ``io`` in 2050 and in 2100, ON against OFF, and ON-with-doubled-warming
against ON. ``io`` is read through the group's published states: the group publishes the 29 STATES, so ``io`` is recomputed here from ``ic``, ``cuf``
and ``icor`` is not available; the sign test therefore uses the state the damage acts on most directly, industrial capital ``ic``, AND the group
exposes ``io`` as an extra output named ``io`` (interface requirement: ``World3Group.outputs`` contains "io"). Control runs that must fail and a
mutation check are below. No threshold is tuned after seeing results.

The 1e-9 baseline is a snapshot of the World3 group BEFORE any change (tests/fixtures/w3_group_baseline_before_damage_coupling.csv, produced by
the pre-change code and committed before this file).
"""
from __future__ import annotations

import csv
import itertools
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

from f3.sectors import damages
from f3.sectors.world3 import STATE_COLUMNS, run_world3

FIX = Path(__file__).parent / "fixtures" / "w3_group_baseline_before_damage_coupling.csv"
TIGHT = 1e-9


@lru_cache(maxsize=None)
def baseline(ps: str):
    rows = [r for r in csv.DictReader(open(FIX, encoding="utf-8")) if r["parameter_set"] == ps]
    return {"time": np.array([float(r["time"]) for r in rows]), **{n: np.array([float(r[n]) for r in rows]) for n in STATE_COLUMNS}}


def yearly(states, res):
    idx = [i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9]
    return np.array([int(round(res.time[i])) for i in idx]), {n: states[n][idx] for n in states}


# warming paths (K above 1850-1900), as functions of the calendar year; the recorded path is a smooth stand-in of the right shape and size
# (1.2 K in 2025 to about 2.9 K in 2100, the ensemble mean of the committed FaIR recording), so the tests need no FaIR run and no data file
def w_zero(y):
    return 0.0


def w_recorded_like(y):
    return 1.2 + (2.9 - 1.2) * min(max((y - 2025.0) / 75.0, 0.0), 1.0)


def w_doubled(y):
    return 2.0 * w_recorded_like(y)


def w_const6(y):
    return 6.0


PATHS = {"zero": w_zero, "recorded_like": w_recorded_like, "doubled": w_doubled, "const6": w_const6}


@lru_cache(maxsize=None)
def run(ps, option, path):
    states, res = run_world3(ps, damage_option=option, warming=(PATHS[path] if option else None))
    yr, st = yearly(states, res)
    return yr, st


# ------------------------------------------------------------------------------------------------------- A6.3 invariance (OFF = stand-alone)
@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_off_equals_the_stand_alone_world3_to_1e_9(ps):
    """Switch OFF (the default) equals the World3 group as it was BEFORE this coupling existed (snapshot fixture), every state, every year."""
    yr, st = run(ps, None, "zero")
    b = baseline(ps)
    assert np.array_equal(yr, b["time"].astype(int))
    for n in STATE_COLUMNS:
        scale = np.maximum(np.abs(b[n]), 1e-30)
        assert np.max(np.abs(st[n] - b[n]) / scale) <= TIGHT, n


def test_default_call_has_the_switch_off():
    import inspect
    sig = inspect.signature(run_world3)
    assert sig.parameters["damage_option"].default is None


# ------------------------------------------------------------------------------------------------------- zero warming = baseline
@pytest.mark.parametrize("ps", ["1974", "2004"])
@pytest.mark.parametrize("option", ["low", "central", "high"])
def test_zero_warming_equals_the_off_run(ps, option):
    yr, on = run(ps, option, "zero")
    _, off = run(ps, None, "zero")
    for n in STATE_COLUMNS:
        assert np.max(np.abs(on[n] - off[n]) / np.maximum(np.abs(off[n]), 1e-30)) <= TIGHT, (option, n)


def test_before_2025_the_multiplier_is_one():
    """Even with large warming, every state before 2025 equals the OFF run (the coupling starts in 2025, D-020)."""
    yr, on = run("2004", "central", "const6")
    _, off = run("2004", None, "zero")
    m = yr <= 2025
    for n in STATE_COLUMNS:
        assert np.max(np.abs(on[n][m] - off[n][m]) / np.maximum(np.abs(off[n][m]), 1e-30)) <= TIGHT, n


# ------------------------------------------------------------------------------------------------------- sign test (named in advance)
def sign_assertions(on, off, on_hot, yr):
    """Named output: industrial capital ``ic`` (the state the damage acts on through io) and the group's published ``io``; window: 2050 and 2100."""
    for year in (2050, 2100):
        k = int(np.where(yr == year)[0][0])
        assert on["ic"][k] < off["ic"][k], ("ic ON vs OFF", year)
        assert on_hot["ic"][k] < on["ic"][k], ("ic doubled warming vs recorded-like", year)
        assert on["io"][k] < off["io"][k], ("io ON vs OFF", year)
        assert on_hot["io"][k] < on["io"][k], ("io doubled warming vs recorded-like", year)


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_more_warming_lowers_industrial_output_in_2050_and_2100(ps):
    yr, on = run(ps, "central", "recorded_like")
    _, off = run(ps, None, "zero")
    _, hot = run(ps, "central", "doubled")
    sign_assertions(on, off, hot, yr)


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_damage_options_are_ordered_low_central_high(ps):
    """Higher coefficient, lower industrial capital in 2100 (D-007 order, level-of-output effects)."""
    k = -1
    vals = [run(ps, o, "recorded_like")[1]["ic"][k] for o in ("low", "central", "high")]
    assert vals[0] > vals[1] > vals[2], vals


def test_the_sign_test_can_fail_control_and_mutation():
    """Control: the OFF run against itself must FAIL the sign assertions (nothing differs). Mutation: with the multiplier forced to 1 (switch ON but
    the damage fraction replaced by zero) the ON run equals the OFF run and the assertions must FAIL."""
    yr, off = run("2004", None, "zero")
    with pytest.raises(AssertionError):
        sign_assertions(off, off, off, yr)
    states, res = run_world3("2004", damage_option="central", warming=w_recorded_like, _mutate_zero_damage=True)
    yr2, on0 = yearly(states, res)
    states_h, res_h = run_world3("2004", damage_option="central", warming=w_doubled, _mutate_zero_damage=True)
    _, hot0 = yearly(states_h, res_h)
    with pytest.raises(AssertionError):
        sign_assertions(on0, off, hot0, yr2)


# ------------------------------------------------------------------------------------------------------- bounds and NaN over the full grid
GRID = list(itertools.product(("1974", "2004"), (None, "low", "central", "high"), ("zero", "recorded_like", "doubled", "const6")))
NONNEG = ("p1", "p2", "p3", "p4", "ic", "sc", "al", "pal", "uil", "lfert", "nr", "ppol", "ppapr1", "ppapr2", "ppapr3", "ai", "pfr", "lufd")


@pytest.mark.parametrize("ps,option,path", [g for g in GRID if g[1] is not None or g[2] == "zero"])
def test_full_grid_is_finite_and_stocks_nonnegative(ps, option, path):
    yr, st = run(ps, option, path)
    for n in STATE_COLUMNS:
        assert np.all(np.isfinite(st[n])), (ps, option, path, n)
    for n in NONNEG:
        assert st[n].min() >= -1e-9 * max(1.0, abs(st[n]).max()), (ps, option, path, n, st[n].min())


# ------------------------------------------------------------------------------------------------------- anchors and labels
def test_damage_anchors_at_3_k():
    assert damages.damage_fraction(3.0, "low") == pytest.approx(0.236e-2 * 9, abs=1e-12)
    assert damages.damage_fraction(3.0, "central") == pytest.approx(0.344e-2 * 9, abs=1e-12)
    assert damages.damage_fraction(3.0, "high") == pytest.approx((0.595 * 1.25 + 0.260) * 1e-2 * 9, abs=1e-12)


def test_the_coupling_declares_its_labels():
    from f3.sectors import world3_group
    s = (getattr(world3_group, "DAMAGE_COUPLING_LABEL", "") or "").lower()
    assert "level-of-output" in s and "not the upper end of the literature" in s and "default off" in s.replace("default is off", "default off")
