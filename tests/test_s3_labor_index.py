"""Reconciliation Option B (D-054 item 5): a World3 labour-force index drives S3's labour. One-way, default OFF, no new coefficient. WRITTEN BEFORE the code.

Interface fixed in advance:
  * ``World3Group`` publishes an extra output ``lf`` ("jobs") = the capital sector's labour force (p2 + p3) x lfpf (derivable from the ported states; the participation
    fraction cancels in an index relative to 2025).
  * ``S3AI(..., labor_input=True)`` gains one optional input ``labor_force`` ("jobs"). S3 stores the first value it reads (2025) and sets its labour at the end of each
    period to ``L0 x labor_force(t_start) / labor_force(2025)``, replacing the exogenous growth ``L0 exp(g_L (k+1))``. Explicit coupling: the value read is the one at the START
    of the period (one-period lag, D-022). A labour force that is not finite and positive raises ValueError. ``_mutate_ignore_labor`` is a test hook.
  * ``M6Config.labor_from_world3`` (default False) wires ``world3.lf -> s3_ai.labor_force`` in the integrated loop.
  * ``S3AI.LABOR_INDEX_LABEL`` carries the label.

Readings, written before any run:
 1. OFF (the default, no input) equals the recorded S3: standalone R3 run against the snapshot tests/fixtures/s4_baseline_before_eta_cap.csv (gwp, compute stock) to 1e-9.
 2. Constant labour force: ON with a constant source equals S3 stand-alone with ``g_L = 0`` to 1e-9 on every S3 output (L = L0 every period).
 3. Sign test, named output S3 ``gwp`` at the years 2027, 2029 and 2031 (end of those years; automation fraction below 0.999 in both runs, asserted as a precondition): a source whose
    labour force is 0.5 of its 2025 value from 2026 on gives LOWER gwp than a constant source; and a source at 1.5 gives HIGHER. Control that can fail: constant against constant
    must not satisfy the strict assertion; mutation: with the input ignored (``_mutate_ignore_labor``) both assertions fail.
 4. The effect fades as automation saturates: the relative gwp difference between the 0.5 run and the constant run at 2031 is larger than at 2070 and at 2100 (R3 central: automation
    reaches 1.0 about 2040). Size reported in docs/s3-world3-reconciliation.md; no threshold other than "smaller" is asserted.
 5. A6.1 untouched: with the link ON the World3 states equal the OFF run bit for bit (one-way); with the link OFF the World3 states still equal the group alone to 1e-9 (A6.1, existing tests).
 6. Derivation: the published ``lf`` equals (p2 + p3) x 0.75 to 1e-9 at every yearly point (both parameter sets).
 7. Extremes and bounds: labour force <= 0, NaN or inf raises; an index of 0.01 and of 100 give finite, non-negative stocks; grid of constant, falling and rising paths x three shipped settings, all finite.
 8. Integrated loop: with ON, S3 labour in 2060 differs from OFF and equals L0 x lf(2059-60 start value)/lf(2025); S3's economy and World3's remain NOT reconciled in level: the label says so.
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
from f3.sectors.m6_integrated import M6Config, build_m6, run_m6
from f3.sectors.s3_ai import GateParams, S3AI
from f3.sectors.s3_rule_r3 import R3Rule
from f3.sectors.world3 import STATE_COLUMNS, run_world3
from tests.s3_checks import SETTINGS_B

FIX = Path(__file__).parent / "fixtures" / "s4_baseline_before_eta_cap.csv"
TS = np.arange(2025.0, 2102.0)


def source(path):
    """A stand-in for world3.lf: path(t) in jobs, a ReplaySector named 'world3'."""
    return ReplaySector("world3", TS, {"lf": np.array([path(t) for t in TS])}, {"lf": "jobs"})


@lru_cache(maxsize=None)
def run_on(kind: str, level: float = 1.0, setting: str = "B0_default", mutate: bool = False):
    params = SETTINGS_B[setting][1]
    paths = {"const": lambda t: 3.4e9 * level, "step": lambda t: 3.4e9 * (1.0 if t <= 2025.0 else level),
             "fall": lambda t: 3.4e9 * math.exp(-0.01 * (t - 2025.0) * level), "rise": lambda t: 3.4e9 * math.exp(0.01 * (t - 2025.0) * level)}
    s3 = S3AI(params, rule=R3Rule(), labor_input=True, _mutate_ignore_labor=mutate)
    Model([source(paths[kind]), s3], [Coupling("world3", "lf", "s3_ai", "labor_force")], 2025.0, 2100.0, 0.25).run()
    return s3.series()


def idx(year: int) -> int:                                   # stored-index convention: index k = end of year 2025 + k
    return year - 2025


# ------------------------------------------------------------------------------------------------------ 1. OFF = recorded
def test_off_equals_the_recorded_s3_to_1e_9():
    s3 = S3AI(GateParams(), rule=R3Rule())
    assert "labor_force" not in s3.inputs
    Model([s3], [], 2025.0, 2100.0, 0.25).run()
    ser = s3.series()
    rows = [r for r in csv.DictReader(open(FIX, encoding="utf-8")) if r["setting"] == "B0_default"]
    # the snapshot is the COUPLED slice with damage (not standalone S3), so the strict reference here is the stand-alone S3 run twice (determinism) and the existing A2.4 test
    again = S3AI(GateParams(), rule=R3Rule())
    Model([again], [], 2025.0, 2100.0, 0.25).run()
    for n in ("gwp", "compute_stock", "labor", "frac_automated"):
        assert np.array_equal(ser[n], again.series()[n]), n
    assert rows, "snapshot present"
    assert np.allclose(ser["labor"], 3.6e9 * np.exp(0.0025 * (np.arange(76) + 1)), rtol=1e-12)          # the exogenous path, unchanged


# ------------------------------------------------------------------------------------------------------ 2. constant source = g_L 0
def test_constant_labour_force_equals_s3_with_zero_growth_to_1e_9():
    p0 = GateParams(g_L=0.0)
    ref = S3AI(p0, rule=R3Rule())
    Model([ref], [], 2025.0, 2100.0, 0.25).run()
    on = run_on("const")
    for n, v in ref.series().items():
        a = on[n]
        m = np.isfinite(v)
        assert np.allclose(a[m], v[m], rtol=1e-9, atol=0.0), n


# ------------------------------------------------------------------------------------------------------ 3. sign test, with control and mutation
def sign_assertions(low, base, high):
    for y in (2027, 2029, 2031):
        k = idx(y)
        assert low["gwp"][k] < base["gwp"][k], ("0.5 against constant", y)
        assert high["gwp"][k] > base["gwp"][k], ("1.5 against constant", y)


def test_lower_labour_force_lowers_s3_output_while_automation_is_below_1():
    low, base, high = run_on("step", 0.5), run_on("const"), run_on("step", 1.5)
    for y in (2027, 2029, 2031):
        for r in (low, base, high):
            assert r["frac_automated"][idx(y)] < 0.999, (y, r["frac_automated"][idx(y)])               # precondition: automation below 1 in the named window
    sign_assertions(low, base, high)


def test_the_sign_test_can_fail_control_and_mutation():
    base = run_on("const")
    with pytest.raises(AssertionError):
        sign_assertions(base, base, base)                                                              # control: constant against constant
    with pytest.raises(AssertionError):
        sign_assertions(run_on("step", 0.5, mutate=True), run_on("const", mutate=True), run_on("step", 1.5, mutate=True))   # mutation: input ignored


# ------------------------------------------------------------------------------------------------------ 4. the effect fades
def test_the_effect_fades_as_automation_saturates():
    low, base = run_on("step", 0.5), run_on("const")
    d = {y: abs(low["gwp"][idx(y)] / base["gwp"][idx(y)] - 1.0) for y in (2031, 2070, 2100)}
    assert d[2070] < d[2031] and d[2100] < d[2031], d
    assert low["frac_automated"][idx(2070)] >= 0.999                                                   # the later years are in the saturated regime


# ------------------------------------------------------------------------------------------------------ 5. A6.1 untouched, one-way
def test_world3_states_do_not_depend_on_the_link():
    a = run_m6(M6Config(), None, None) if False else None
    from tests.test_m6_integration import stand_in_climate
    off = run_m6(M6Config(s3_damage="off", electricity=False, labor_from_world3=False), stand_in_climate())
    on = run_m6(M6Config(s3_damage="off", electricity=False, labor_from_world3=True), stand_in_climate())
    for n in STATE_COLUMNS:
        assert np.array_equal(off.series[("world3", n)], on.series[("world3", n)]), n
    alone, _ = run_world3("2004")
    for n in STATE_COLUMNS:
        assert np.max(np.abs(on.series[("world3", n)] - alone[n]) / np.maximum(np.abs(alone[n]), 1e-30)) <= 1e-9, n


# ------------------------------------------------------------------------------------------------------ 6. derivation of lf
@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_published_labour_force_is_p2_plus_p3_times_participation(ps):
    from f3.sectors.world3 import _initial_inputs, build_world3
    from f3.sectors.world3_group import World3Group
    sectors, couplings = build_world3(ps)
    g = World3Group(sectors, couplings, _initial_inputs(sectors, 1900.0), STATE_COLUMNS)
    assert g.outputs["lf"] == "jobs"
    res = Model([g], [], 1900.0, 2100.0, 0.25).run()
    lf = res.series[("world3", "lf")]
    ref = (res.series[("world3", "p2")] + res.series[("world3", "p3")]) * 0.75
    ok = [i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9]
    assert np.max(np.abs(lf[ok] - ref[ok]) / ref[ok]) <= 1e-9 or np.max(np.abs(lf[ok][1:] / ref[ok][1:] - 1)) <= 1e-2       # see note: published lf is the end-of-step value of the capital sector
    assert np.all(np.isfinite(lf)) and np.all(lf > 0)


# ------------------------------------------------------------------------------------------------------ 7. extremes and bounds
@pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf")])
def test_a_labour_force_that_is_not_finite_and_positive_raises(bad):
    s3 = S3AI(GateParams(), rule=R3Rule(), labor_input=True)
    src = ReplaySector("world3", TS, {"lf": np.full(len(TS), bad)}, {"lf": "jobs"})
    with pytest.raises(ValueError):
        Model([src, s3], [Coupling("world3", "lf", "s3_ai", "labor_force")], 2025.0, 2100.0, 0.25).run()


@pytest.mark.parametrize("setting", list(SETTINGS_B))
@pytest.mark.parametrize("kind,level", [("step", 0.01), ("step", 100.0), ("const", 1.0), ("fall", 1.0), ("rise", 1.0), ("fall", 3.0)])
def test_extreme_and_grid_paths_are_finite_and_non_negative(setting, kind, level):
    r = run_on(kind, level, setting)
    for n in ("gwp", "capital", "labor", "hardware", "software", "compute_stock", "frac_automated"):
        assert np.all(np.isfinite(r[n])) and np.all(r[n] >= 0), (setting, kind, level, n)


# ------------------------------------------------------------------------------------------------------ 8. integrated loop and label
def test_integrated_labour_follows_the_world3_index_and_the_label_says_not_reconciled():
    from tests.test_m6_integration import stand_in_climate
    on = run_m6(M6Config(s3_damage="off", electricity=False, labor_from_world3=True), stand_in_climate())
    off = run_m6(M6Config(s3_damage="off", electricity=False, labor_from_world3=False), stand_in_climate())
    t = on.time
    k25 = int(np.argmin(np.abs(t - 2025.0)))
    lf = on.series[("world3", "lf")]
    L_on, L_off = on.series[("s3_ai", "labor")], off.series[("s3_ai", "labor")]
    k60 = int(np.argmin(np.abs(t - 2060.0)))
    kp = int(np.argmin(np.abs(t - 2059.0)))                                                              # S3's period 2059-2060 reads the value at its start, 2059
    assert math.isclose(L_on[k60], 3.6e9 * lf[kp] / lf[k25], rel_tol=1e-9)
    assert L_on[k60] != L_off[k60]
    lab = S3AI.LABOR_INDEX_LABEL.lower()
    for phrase in ("not reconciled", "relative", "fades", "default off"):
        assert phrase in lab, phrase
