"""Tests of the S1 population sector port (step 1.4, D-012, D-015, D-004).

Reference: WorldDynamics.jl v1.0.0 in the pinned environment ``audit/env`` (D-017), default solver options.
The reference trajectories and the four exogenous input series were exported by ``audit/t0/world3_s1_export.jl``
into ``tests/fixtures/`` and are matched by variable name. Tolerance: +-2% (D-004).

1974 parameter set: the port must match WorldDynamics.jl ``World3`` within 2%; PyWorld3 (unmodified) is the second check.
2004 parameter set: the port must match WorldDynamics.jl ``World3_03.scenario1`` within 2%; the PyWorld3 check of this
set overrides parameters and tables on an instance and is **diagnostic** (see ``tests/pyworld3_check.py``).
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from f3.sectors.s1_population import (PARAMETER_SETS, STATE_NAMES, Inputs, PopulationSector, interpolate)

FIX = Path(__file__).parent / "fixtures"
TOL = 0.02                      # D-004

TAGS = {"1974": "world3_1974", "2004": "world3_2004"}
# WorldDynamics.jl names -> port names
STATE_MAP = {"p1": "pop₊p1", "p2": "pop₊p2", "p3": "pop₊p3", "p4": "pop₊p4", "ehspc": "dr₊ehspc",
             "ple": "br₊ple", "ple2": "br₊ple2", "ple1": "br₊ple1",
             "diopc": "br₊diopc", "diopc2": "br₊diopc2", "diopc1": "br₊diopc1", "aiopc": "br₊aiopc",
             "fcfpc": "br₊fcfpc", "fcfpc2": "br₊fcfpc2", "fcfpc1": "br₊fcfpc1"}
DERIVED_MAP = {"le": "dr₊le", "br": "pop₊br", "dr": "pop₊dr", "tf": "br₊tf"}
KEY = ("p1", "p2", "p3", "p4", "pop", "le", "br", "dr", "tf")      # population, life expectancy, births, deaths, fertility


def _load(path: Path) -> dict:
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


@pytest.fixture(scope="module", params=["1974", "2004"])
def case(request):
    ps = request.param
    tag = TAGS[ps]
    inp = _load(FIX / f"s1_inputs_{tag}.csv")
    inputs = Inputs(inp["time"], inp["dr₊fpc"], inp["br₊sopc"], inp["dr₊iopc"], inp["dr₊ppolx"])
    ref = _load(FIX / f"s1_reference_{tag}_default.csv")
    tight = _load(FIX / f"s1_reference_{tag}_tight.csv")
    out = PopulationSector(ps).run(inputs, dt=0.25)
    idx = np.array([int(np.argmin(np.abs(out["time"] - t))) for t in ref["time"]])
    assert np.allclose(out["time"][idx], ref["time"], atol=1e-9), "port grid does not contain the reference years"
    return dict(ps=ps, inputs=inputs, ref=ref, tight=tight, out=out, idx=idx)


def _relerr(port: np.ndarray, ref: np.ndarray) -> np.ndarray:
    return np.abs(port - ref) / np.maximum(np.abs(ref), 1e-30)


def _ref_pop(d: dict) -> np.ndarray:
    return d["pop₊p1"] + d["pop₊p2"] + d["pop₊p3"] + d["pop₊p4"]


def _ref(d: dict, key: str) -> np.ndarray:
    if key == "pop":
        return _ref_pop(d)
    return d[STATE_MAP[key]] if key in STATE_MAP else d[DERIVED_MAP[key]]


# ----------------------------------------------------------------------------------------------------------
# start-up
# ----------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_initial_state_matches_reference(ps):
    """The port starts from WorldDynamics.jl's own initial state (start-up convention 1). The reference values are
    stored with 10 significant digits."""
    ref = _load(FIX / f"s1_reference_{TAGS[ps]}_default.csv")
    y0 = PopulationSector(ps).initial_state()
    for name, v in zip(STATE_NAMES, y0):
        assert abs(v - ref[STATE_MAP[name]][0]) <= 1e-8 * abs(ref[STATE_MAP[name]][0]), name


def test_initial_state_same_for_both_parameter_sets():
    """WorldDynamics.jl computes the initial values from the 1974 tables whichever set is run (the 1900 rows of
    its two runs are identical); the port reproduces that, and so the two sets start from the same state."""
    assert np.array_equal(PopulationSector("1974").initial_state(), PopulationSector("2004").initial_state())


# ----------------------------------------------------------------------------------------------------------
# D-004: within 2% of the WorldDynamics.jl reference at every reported year
# ----------------------------------------------------------------------------------------------------------
def test_key_variables_within_2_percent_of_worlddynamics(case):
    for k in KEY:
        e = _relerr(case["out"][k][case["idx"]], _ref(case["ref"], k))
        assert e.max() <= TOL, f"{case['ps']} {k}: max {100 * e.max():.3f}% at {case['ref']['time'][e.argmax()]}"


def test_all_states_within_2_percent_of_worlddynamics(case):
    for k in STATE_NAMES:
        e = _relerr(case["out"][k][case["idx"]], _ref(case["ref"], k))
        assert e.max() <= TOL, f"{case['ps']} {k}: max {100 * e.max():.3f}% at {case['ref']['time'][e.argmax()]}"


def test_all_states_within_2_percent_of_tight_tolerance_reference(case):
    """Diagnostic: the reference's own solver error. The same comparison against WorldDynamics.jl solved with
    reltol = abstol = 1e-8."""
    for k in STATE_NAMES:
        e = _relerr(case["out"][k][case["idx"]], _ref(case["tight"], k))
        assert e.max() <= TOL, f"{case['ps']} {k}: max {100 * e.max():.3f}% at {case['tight']['time'][e.argmax()]}"


def test_reference_default_vs_tight_is_itself_within_2_percent(case):
    """If this failed, the reference would not be a yardstick at 2% for those states. Recorded: the largest
    default-vs-tight gap is in the delay stage ``fcfpc1`` in the 1974 set (about 1.6%)."""
    for k in STATE_NAMES:
        e = _relerr(_ref(case["ref"], k), _ref(case["tight"], k))
        assert e.max() <= TOL, f"{case['ps']} {k}: reference alone differs {100 * e.max():.3f}%"


# ----------------------------------------------------------------------------------------------------------
# switches and numerics
# ----------------------------------------------------------------------------------------------------------
def test_health_service_switch_at_1940_is_a_step_boundary():
    """``lmhs`` switches from the first health-service table to the second at 1940 (``iphst``). The integration is
    split there, so a step never straddles the switch, and the multiplier jumps at 1940 (it is not smoothed)."""
    ps = PopulationSector("1974")
    assert 1940.0 in ps._breakpoints(1900.0, 2100.0)
    inp = _load(FIX / "s1_inputs_world3_1974.csv")
    inputs = Inputs(inp["time"], inp["dr₊fpc"], inp["br₊sopc"], inp["dr₊iopc"], inp["dr₊ppolx"])
    out = ps.run(inputs, dt=0.25)
    # 1940 is on the grid once (the end of the first segment); the switch uses ``t >= iphst``, so the value at
    # 1940 is the after-switch value and the value one step earlier is the before-switch value.
    j = int(np.where(np.isclose(out["time"], 1940.0))[0][0])
    assert np.isclose(out["time"][j - 1], 1939.75)
    ehspc = out["ehspc"][j]
    P, T = ps.params, ps.tables
    assert out["lmhs"][j] == pytest.approx(interpolate(ehspc, T["lmhs2"]))
    assert out["lmhs"][j - 1] == pytest.approx(interpolate(out["ehspc"][j - 1], T["lmhs1"]))
    # the jump is real: at 1940 the second table gives a larger multiplier than the first would
    assert interpolate(ehspc, T["lmhs2"]) > interpolate(ehspc, T["lmhs1"])


def test_switches_that_never_fire_are_inert_in_the_horizon():
    """zpgt, fcest and pet are all 4000, outside 1900-2100: no breakpoint is created for them."""
    for ps in ("1974", "2004"):
        assert PopulationSector(ps)._breakpoints(1900.0, 2100.0) == [1900.0, 1940.0, 2100.0]


def test_step_convergence_quarter_vs_eighth_year(case):
    """D-003 check: results at 0.25 year do not change materially at 0.125 year (the port's own convergence)."""
    out125 = PopulationSector(case["ps"]).run(case["inputs"], dt=0.125)
    for k in ("pop", "le", "br", "dr"):
        a = case["out"][k]
        b = out125[k][::2]
        n = min(len(a), len(b))
        e = np.abs(a[:n] - b[:n]) / np.maximum(np.abs(b[:n]), 1e-30)
        assert e.max() <= 0.001, f"{case['ps']} {k}: 0.25 vs 0.125 year differ {100 * e.max():.4f}%"


def test_unknown_parameter_set_is_rejected():
    with pytest.raises(ValueError):
        PopulationSector("1992")


def test_tables_differ_only_where_documented():
    """The two parameter sets differ in dcfsn and in the tables lmf, lmhs2, fm, sfsn (D-015, finding 1)."""
    p74, t74 = PARAMETER_SETS["1974"]
    p04, t04 = PARAMETER_SETS["2004"]
    assert {k for k in p74 if p74[k] != p04[k]} == {"dcfsn"}
    assert {k for k in t74 if t74[k] != t04[k]} == {"lmf", "lmhs2", "fm", "sfsn"}


def test_interpolate_matches_tabhl_conventions():
    tbl = ((0.0, 10.0, 20.0), (0.0, 2.0))
    assert interpolate(-1.0, tbl) == 0.0 and interpolate(3.0, tbl) == 20.0 and interpolate(1.0, tbl) == 10.0
    assert interpolate(0.5, tbl) == pytest.approx(5.0)


# ----------------------------------------------------------------------------------------------------------
# second check: PyWorld3 (unmodified from PyPI). Slow: two 200-year runs at dt = 0.05.
# ----------------------------------------------------------------------------------------------------------
@pytest.fixture(scope="module", params=["1974", "2004"])
def pyworld3_case(request):
    pytest.importorskip("pyworld3")
    from tests.pyworld3_check import compare, pyworld3_initial_state, run_pyworld3

    w, t, inputs, n = run_pyworld3(request.param)
    return dict(ps=request.param, w=w, inputs=inputs, n=n, compare=compare, y0=pyworld3_initial_state(w))


def test_matches_pyworld3_from_the_same_start(pyworld3_case):
    """Population equations only: same inputs, same initial state (PyWorld3's own), same parameters. For the 2004
    set the PyWorld3 side is a DIAGNOSTIC override on an instance, not a separate implementation."""
    c = pyworld3_case
    out = PopulationSector(c["ps"]).run(c["inputs"], dt=0.25, y0=c["y0"])
    res = c["compare"](out, c["w"], c["n"])
    for k in ("p1", "p2", "p3", "p4", "pop", "ple", "ehspc", "aiopc"):
        assert res[k][0] <= TOL, f"{c['ps']} {k}: {100 * res[k][0]:.3f}% at {res[k][1]}"
    # fcfpc is a small per-capita delay stage; it also stays inside the band
    assert res["fcfpc"][0] <= TOL


def test_pyworld3_start_up_differs_from_worlddynamics(pyworld3_case):
    """Start-up convention, documented apart from equation differences: PyWorld3 starts the sector from different
    derived values than WorldDynamics.jl (for example fcfpc 0.0887 against 0.0384, ehspc 7.2 against 7.45).
    Started from WorldDynamics.jl's state instead of PyWorld3's, the port's total population differs from PyWorld3
    by up to 0.74% (1974 set) and 1.75% (2004 set, diagnostic override): inside 2%, but a visible effect of the
    start-up values, not of the equations (started from PyWorld3's own state the gap is 0.04%)."""
    c = pyworld3_case
    own = PopulationSector(c["ps"]).run(c["inputs"], dt=0.25, y0=c["y0"])
    wdj = PopulationSector(c["ps"]).run(c["inputs"], dt=0.25)
    e_own = c["compare"](own, c["w"], c["n"], names=("pop",))["pop"][0]
    e_wdj = c["compare"](wdj, c["w"], c["n"], names=("pop",))["pop"][0]
    assert e_wdj > 5 * e_own             # the start-up values, not the equations, produce the gap
    assert e_wdj <= TOL
