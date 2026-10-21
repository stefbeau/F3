"""M4 sector 6 of 8: Earth4All.jl demand (S2). Test list and tolerances fixed BEFORE the port (docs/tracks/track-c-plan.md, committed first).

A4.1: all 7 states and the headline variables within 2% (D-004) of Earth4All.jl at every 0.5-year point, 1980-2100, both scenarios,
recorded inputs by name (ECTAF2022, EGDPP, GBC, IPP, NI, POP, WBC, WF, WSO). Step effect: S0 Euler 1/64 (equations), S1 RK4 1/64, S2 RK4 at the loop step 0.25. A failure at a
step is a strict xfail recorded with size and first year, the sub-step rule of the plan then applies (no relaxation). Earth4All.jl's own
error against Vensim is printed beside the figures (D-018).
"""

from __future__ import annotations

import pytest

from tests.e4a_a41 import (check_initial_state, check_rule, check_states_are_reference_states, check_within_tolerance, informational_all, recorded)
from tests.e4a_helpers import Case, SCENARIOS, sector_class

CASE = Case("demand", ('ETF2022', 'FGBW', 'GD', 'PGCIN', 'POCI', 'PWCIN', 'WD'), ('GS', 'GPU', 'GIPC', 'INEQ', 'INEQI', 'TPP', 'TS', 'WDI', 'GNI', 'CFWB', 'CFGB'))
INPUTS = {'WSO', 'WBC', 'NI', 'GBC', 'EGDPP', 'ECTAF2022', 'IPP', 'POP', 'WF'}


def test_states_are_the_reference_states():
    check_states_are_reference_states(CASE)


def test_inputs_are_the_recorded_ones():
    mod, cls = sector_class("demand")
    assert set(cls.inputs) == INPUTS


@pytest.mark.parametrize("scen", SCENARIOS)
def test_initial_state_matches_reference(scen):
    check_initial_state(CASE, scen)


@pytest.mark.parametrize("scen", SCENARIOS)
def test_a41_s0_equations_euler_1_64(scen):
    """The port with the reference's own scheme (Euler, 1/64 year) and the recorded inputs on the reference's own 1/64 grid."""
    check_within_tolerance(CASE, scen, "S0")


@pytest.mark.parametrize("scen", [recorded(CASE, s, "S1") for s in SCENARIOS])
def test_a41_s1_rk4_1_64(scen):
    """Step-free limit: RK4 at 1/64. Its difference from S0 is the REFERENCE's own Euler error (strict xfail where recorded)."""
    check_within_tolerance(CASE, scen, "S1")


@pytest.mark.parametrize("scen", [recorded(CASE, s, "S2") for s in SCENARIOS])
def test_a41_s2_loop_step_0_25(scen):
    """RK4 at the loop step 0.25 year, one step per loop step (the F3 default of S1 and World3): strict xfail where recorded."""
    check_within_tolerance(CASE, scen, "S2")


@pytest.mark.parametrize("scen", SCENARIOS)
def test_a41_s3_rule_euler_substep_1_64_in_loop_step_0_25(scen):
    """The recorded rule (docs/tracks/track-c.md): Euler with internal sub-step 1/64 inside the 0.25-year loop step."""
    check_rule(CASE, scen)


@pytest.mark.parametrize("scen", SCENARIOS)
def test_informational_all_variables(scen):
    for tag in ("S0", "S2"):
        rows = informational_all(CASE, scen, tag)
        live = [r for r in rows.values() if not r.excluded]
        w = max(live, key=lambda r: r.max_err)
        print(f"{CASE.key} {scen} {tag} all {len(live)} variables: worst {w.name} {100 * w.max_err:.4f}% (year {w.year_of_max})")
