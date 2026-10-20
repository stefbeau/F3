"""M4 sector 8 of 8: Earth4All.jl other (no verdict in D-016; used for CTA). Test list and tolerances fixed BEFORE the port (docs/tracks/track-c-plan.md, committed first).

A4.1: all 1 states and the headline variables within 2% (D-004) of Earth4All.jl at every 0.5-year point, 1980-2100, both scenarios,
recorded inputs by name (CE, COFO, GDPP, INEQ, POP). Step effect: S0 Euler 1/64 (equations), S1 RK4 1/64, S2 RK4 at the loop step 0.25. A failure at a
step is a strict xfail recorded with size and first year, the sub-step rule of the plan then applies (no relaxation). Earth4All.jl's own
error against Vensim is printed beside the figures (D-018).
"""

from __future__ import annotations

import pytest

from tests.e4a_a41 import (check_initial_state, check_states_are_reference_states, check_within_tolerance, informational_all)
from tests.e4a_helpers import Case, SCENARIOS, sector_class

CASE = Case("other", ('PGDPP',), ('CTA', 'FB15', 'PB15', 'LK'))
INPUTS = {'COFO', 'GDPP', 'INEQ', 'CE', 'POP'}


def test_states_are_the_reference_states():
    check_states_are_reference_states(CASE)


def test_inputs_are_the_recorded_ones():
    mod, cls = sector_class("other")
    assert set(cls.inputs) == INPUTS


@pytest.mark.parametrize("scen", SCENARIOS)
def test_initial_state_matches_reference(scen):
    check_initial_state(CASE, scen)


@pytest.mark.parametrize("scen", SCENARIOS)
def test_a41_s0_equations_euler_1_64(scen):
    check_within_tolerance(CASE, scen, "S0")


@pytest.mark.parametrize("scen", SCENARIOS)
def test_a41_s1_rk4_1_64(scen):
    check_within_tolerance(CASE, scen, "S1")


@pytest.mark.parametrize("scen", SCENARIOS)
def test_a41_s2_loop_step_0_25(scen):
    check_within_tolerance(CASE, scen, "S2")


@pytest.mark.parametrize("scen", SCENARIOS)
def test_informational_all_variables(scen):
    for tag in ("S0", "S2"):
        rows = informational_all(CASE, scen, tag)
        live = [r for r in rows.values() if not r.excluded]
        w = max(live, key=lambda r: r.max_err)
        print(f"other {scen} {tag} all {len(live)} variables: worst {w.name} {100 * w.max_err:.4f}% (year {w.year_of_max})")
