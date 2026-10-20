"""Generic A4.1 checks for the M4 sectors (plan: docs/tracks/track-c-plan.md, section 2). Each ``test_e4a_<sector>.py`` declares a
``Case`` (states and headline variables, fixed in the plan before any result) and calls these functions. A failure is never
adjusted: it is recorded as a strict xfail with its size and first year."""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from tests.e4a_helpers import FINE, TOL, Case, Row, T0, cached_run, compare, reference, report_line, worst, all_variables


def measure(case: Case, scen: str, tag: str, substep_override: Optional[float] = None) -> Dict[str, Row]:
    """tag: 'S0' Euler 1/64, 'S1' RK4 1/64, 'S2' RK4 at the loop step 0.25 (module SUBSTEP rule applied if set)."""
    if tag == "S0":
        sector, res = cached_run(case.key, scen, FINE, "euler", None)
    elif tag == "S1":
        sector, res = cached_run(case.key, scen, FINE, "rk4", None)
    elif tag == "S2":
        sector, res = cached_run(case.key, scen, 0.25, "rk4", substep_override)
    else:
        raise ValueError(tag)
    return compare(res, sector.name, scen, case.criterion)


def informational_all(case: Case, scen: str, tag: str):
    """Worst over every variable of the sector (not a criterion)."""
    if tag == "S0":
        sector, res = cached_run(case.key, scen, FINE, "euler", None)
    elif tag == "S1":
        sector, res = cached_run(case.key, scen, FINE, "rk4", None)
    else:
        sector, res = cached_run(case.key, scen, 0.25, "rk4", None)
    names = [n for n in all_variables(sector.name.replace("e4a_", ""), scen)]
    return compare(res, sector.name, scen, names)


def check_states_are_reference_states(case: Case):
    from tests.e4a_helpers import sector_class
    mod, cls = sector_class(case.key)
    assert tuple(cls.STATE_NAMES) == tuple(case.states) or set(cls.STATE_NAMES) == set(case.states)
    ref = reference("tltl")
    for n in case.states:
        assert f"{case.key}.{n}" in ref, n


def check_initial_state(case: Case, scen: str):
    from tests.e4a_helpers import sector_class, signals, signal_column
    mod, cls = sector_class(case.key)
    s = cls(scenario=scen)
    y0 = s.initial_state()
    ref = reference(scen)
    for i, n in enumerate(s.STATE_NAMES):
        b = ref[f"{case.key}.{n}"][0]
        assert abs(y0[i] - b) <= 1e-9 * max(abs(b), 1e-12), (n, y0[i], b)


def check_within_tolerance(case: Case, scen: str, tag: str, substep_override: Optional[float] = None):
    rows = measure(case, scen, tag, substep_override)
    print(report_line(case, tag, scen, rows))
    bad = {n: (r.max_err, r.first_year_above) for n, r in rows.items() if not r.excluded and r.max_err > TOL}
    assert not bad, f"{case.key} {scen} {tag}: above 2%: {bad}"
    # every state must be a live (non-excluded) criterion unless its reference is identically zero
    return rows
