"""M3, sector 2 of 4: World3 capital (industrial subsector, service subsector, job subsector). Test list written BEFORE the
port (docs/tracks/track-b.md). Reference and tolerance as in ``test_w3_agriculture.py``: A3.1, +-2% (D-004), recorded inputs,
the reference's own initial state, 1900-2100, both parameter sets.

States (3): industrial capital ``ic``, service capital ``sc``, labour utilisation fraction delayed ``lufd``.
Inputs: ``pop``, ``p2``, ``p3`` (population sector), ``fcaor`` (resources), ``fioaa`` and ``aiph``, ``al`` (agriculture).
Published: ``io``, ``iopc``, ``so``, ``sopc``, ``cuf``, ``j``, ``lf``.
"""

from __future__ import annotations

import pytest

from f3.sectors.w3_capital import PARAMETER_SETS, STATE_NAMES, Capital
from tests.w3_helpers import TOL, a31, recorded_initial_inputs, reference, relerr, state_table

INPUTS = {"pop": "is₊pop", "p2": "js₊p2", "p3": "js₊p3", "fcaor": "is₊fcaor", "fioaa": "is₊fioaa", "aiph": "js₊aiph",
          "al": "js₊al"}
STATES = {"ic": "is₊ic", "sc": "ss₊sc", "lufd": "js₊lufd"}
OUTS = {"io": "is₊io", "iopc": "is₊iopc", "so": "ss₊so", "sopc": "ss₊sopc", "cuf": "js₊cuf", "j": "js₊j", "lf": "js₊lf"}


def test_state_names_are_the_three_reference_states():
    assert set(STATE_NAMES) == set(STATES)


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_initial_state_matches_reference(ps):
    ref = reference(ps)
    for n, v in zip(STATE_NAMES, Capital(ps).initial_state()):
        assert abs(v - ref[STATES[n]][0]) <= 1e-8 * abs(ref[STATES[n]][0]), n


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_initial_outputs_match_reference(ps):
    ref = reference(ps)
    s = Capital(ps)
    s.set_initial_inputs(recorded_initial_inputs(ps, INPUTS))
    s.reset(1900.0, 2100.0, 0.25)
    out = s.current_outputs()
    for n, col in OUTS.items():
        assert abs(out[n] - ref[col][0]) <= 1e-8 * abs(ref[col][0]), n


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a31_states_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Capital, ps, INPUTS, STATES, OUTS)
    for n, (e, yr, et, er, mean) in state_table(s, idx, ref, tight, STATES).items():
        print(f"capital {ps} {n}: port vs reference max {100*e:.3f}% (mean {100*mean:.3f}%, year {yr}); vs tight {100*et:.3f}%; "
              f"reference default vs tight {100*er:.3f}%")
        assert e <= TOL, f"{ps} {n}: {100*e:.3f}% in {yr}"


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a31_published_outputs_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Capital, ps, INPUTS, STATES, OUTS)
    for n, col in OUTS.items():
        e = relerr(res.series[("w3_capital", n)][idx], ref[col])
        print(f"capital {ps} output {n}: max {100*e.max():.3f}% in {ref['time'][int(e.argmax())]}")
        assert e.max() <= TOL, f"{ps} {n}: {100*e.max():.3f}%"


def test_parameter_sets_are_identical():
    """D-015 finding 1: capital has no differences between the 1974 and 2004 sets."""
    assert PARAMETER_SETS["1974"] == PARAMETER_SETS["2004"]


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_restart_in_1970_from_the_reference_state_stays_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Capital, ps, INPUTS, STATES, OUTS, t0=1970.0, use_1970_state=True)
    st = s.states()
    for n, col in STATES.items():
        e = relerr(st[n][idx], ref[col])
        assert e.max() <= TOL, f"{ps} {n}: {100*e.max():.3f}%"


def test_units():
    s = Capital("2004")
    assert set(s.inputs) == set(INPUTS)
    assert s.outputs["sopc"] == "dollars/person-year" and s.outputs["io"] == "dollars/year"
