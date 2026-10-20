"""M3, sector 3 of 4: World3 non-renewable resources. Test list written BEFORE the port (docs/tracks/track-b.md).
Reference and tolerance as in ``test_w3_agriculture.py`` (A3.1, +-2%, D-004, recorded inputs, reference's own initial state,
1900-2100, both sets).

State (1): ``nr``. Inputs: ``pop``, ``iopc``. Published: ``fcaor``, ``pcrum``, ``nrfr``, ``nrur``.
"""

from __future__ import annotations

import pytest

from f3.sectors.w3_resources import PARAMETER_SETS, STATE_NAMES, Resources
from tests.w3_helpers import TOL, a31, recorded_initial_inputs, reference, relerr, state_table

INPUTS = {"pop": "nr₊pop", "iopc": "nr₊iopc"}
STATES = {"nr": "nr₊nr"}
OUTS = {"fcaor": "nr₊fcaor", "pcrum": "nr₊pcrum", "nrfr": "nr₊nrfr", "nrur": "nr₊nrur"}


def test_state_names():
    assert tuple(STATE_NAMES) == ("nr",)


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_initial_state_matches_reference(ps):
    ref = reference(ps)
    assert abs(Resources(ps).initial_state()[0] - ref["nr₊nr"][0]) <= 1e-8 * ref["nr₊nr"][0]


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_initial_outputs_match_reference(ps):
    ref = reference(ps)
    s = Resources(ps)
    s.set_initial_inputs(recorded_initial_inputs(ps, INPUTS))
    s.reset(1900.0, 2100.0, 0.25)
    out = s.current_outputs()
    for n, col in OUTS.items():
        assert abs(out[n] - ref[col][0]) <= 1e-8 * abs(ref[col][0]), n


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a31_state_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Resources, ps, INPUTS, STATES, OUTS)
    for n, (e, yr, et, er, mean) in state_table(s, idx, ref, tight, STATES).items():
        print(f"resources {ps} {n}: port vs reference max {100*e:.3f}% (mean {100*mean:.3f}%, year {yr}); vs tight {100*et:.3f}%; "
              f"reference default vs tight {100*er:.3f}%")
        assert e <= TOL


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a31_published_outputs_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Resources, ps, INPUTS, STATES, OUTS)
    for n, col in OUTS.items():
        e = relerr(res.series[("w3_resources", n)][idx], ref[col])
        print(f"resources {ps} output {n}: max {100*e.max():.3f}% in {ref['time'][int(e.argmax())]}")
        assert e.max() <= TOL, f"{ps} {n}: {100*e.max():.3f}%"


def test_parameter_sets_differ_as_documented():
    """D-015 finding 1: non-renewable resources differ only by the ``pcrum`` table."""
    p74, t74 = PARAMETER_SETS["1974"]
    p04, t04 = PARAMETER_SETS["2004"]
    assert p74 == p04
    assert {k for k in t74 if t74[k] != t04[k]} == {"pcrum"}


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_restart_in_1970_from_the_reference_state_stays_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Resources, ps, INPUTS, STATES, OUTS, t0=1970.0, use_1970_state=True)
    e = relerr(s.states()["nr"][idx], ref["nr₊nr"])
    assert e.max() <= TOL


def test_units():
    s = Resources("2004")
    assert set(s.inputs) == set(INPUTS) and s.outputs["fcaor"] == "1"
