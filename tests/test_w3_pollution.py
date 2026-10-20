"""M3, sector 4 of 4: World3 persistent pollution. Test list written BEFORE the port (docs/tracks/track-b.md).
Reference and tolerance as in ``test_w3_agriculture.py`` (A3.1, +-2%, D-004, recorded inputs, reference's own initial state,
1900-2100, both sets).

States (4): the third-order delay ``ppapr1``, ``ppapr2``, ``ppapr3`` and the stock ``ppol``.
Inputs: ``pcrum``, ``pop``, ``aiph``, ``al``. Published: ``ppolx``, ``ppgr``, ``ppapr``, ``ppasr``, ``ahl``.
The initial state is the reference's own (every stage of the ``ppapr`` chain starts at ``pptd * ppgr / 3``, Pollution
initialisations.jl); the PyWorld3 start-up difference is a second-check matter (A3.3), not tested here.
"""

from __future__ import annotations

import pytest

from f3.sectors.w3_pollution import PARAMETER_SETS, STATE_NAMES, Pollution
from tests.w3_helpers import TOL, a31, recorded_initial_inputs, reference, relerr, state_table

INPUTS = {"pcrum": "pp₊pcrum", "pop": "pp₊pop", "aiph": "pp₊aiph", "al": "pp₊al"}
STATES = {"ppapr1": "pp₊ppapr1", "ppapr2": "pp₊ppapr2", "ppapr3": "pp₊ppapr3", "ppol": "pp₊ppol"}
OUTS = {"ppolx": "pp₊ppolx", "ppgr": "pp₊ppgr", "ppapr": "pp₊ppapr", "ppasr": "pp₊ppasr", "ahl": "pp₊ahl"}


def test_state_names():
    assert set(STATE_NAMES) == set(STATES)


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_initial_state_matches_reference(ps):
    ref = reference(ps)
    for n, v in zip(STATE_NAMES, Pollution(ps).initial_state()):
        assert abs(v - ref[STATES[n]][0]) <= 1e-8 * abs(ref[STATES[n]][0]), n


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_initial_outputs_match_reference(ps):
    ref = reference(ps)
    s = Pollution(ps)
    s.set_initial_inputs(recorded_initial_inputs(ps, INPUTS))
    s.reset(1900.0, 2100.0, 0.25)
    out = s.current_outputs()
    for n, col in OUTS.items():
        assert abs(out[n] - ref[col][0]) <= 1e-8 * abs(ref[col][0]), n


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a31_states_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Pollution, ps, INPUTS, STATES, OUTS)
    for n, (e, yr, et, er, mean) in state_table(s, idx, ref, tight, STATES).items():
        print(f"pollution {ps} {n}: port vs reference max {100*e:.3f}% (mean {100*mean:.3f}%, year {yr}); vs tight {100*et:.3f}%; "
              f"reference default vs tight {100*er:.3f}%")
        assert e <= TOL, f"{ps} {n}: {100*e:.3f}% in {yr}"


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a31_published_outputs_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Pollution, ps, INPUTS, STATES, OUTS)
    for n, col in OUTS.items():
        e = relerr(res.series[("w3_pollution", n)][idx], ref[col])
        print(f"pollution {ps} output {n}: max {100*e.max():.3f}% in {ref['time'][int(e.argmax())]}")
        assert e.max() <= TOL, f"{ps} {n}: {100*e.max():.3f}%"


def test_parameter_sets_are_identical():
    """D-015 finding 1: persistent pollution has no differences between the sets."""
    assert PARAMETER_SETS["1974"] == PARAMETER_SETS["2004"]


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_restart_in_1970_from_the_reference_state_stays_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Pollution, ps, INPUTS, STATES, OUTS, t0=1970.0, use_1970_state=True)
    st = s.states()
    for n, col in STATES.items():
        assert relerr(st[n][idx], ref[col]).max() <= TOL, n


def test_units():
    s = Pollution("2004")
    assert set(s.inputs) == set(INPUTS) and s.outputs["ppolx"] == "1"
