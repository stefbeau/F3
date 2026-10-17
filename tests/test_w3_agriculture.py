"""M3, sector 1 of 4: World3 agriculture (land development, agricultural inputs, investment allocation, land erosion and
urban-industrial use, land fertility, land maintenance). Test list written BEFORE the port (docs/tracks/track-b.md).

Reference: WorldDynamics.jl v1.0.0 in the pinned environment (D-017), default options, fixtures by name from
``audit/t0/world3_m3_export.jl``. Tolerance: +-2% (D-004), A3.1: the sector alone with the recorded inputs of the full run,
from the reference's own initial state, 1900-2100, both parameter sets.
"""

from __future__ import annotations

import numpy as np
import pytest

from f3.core import Coupling, Model
from f3.sectors.w3_agriculture import PARAMETER_SETS, STATE_NAMES, Agriculture
from tests.w3_helpers import TOL, a31, recorded_initial_inputs, reference, relerr, state_table

INPUTS = {"pop": "ld₊pop", "io": "ld₊io", "iopc": "ld₊iopc", "ppolx": "lfd₊ppolx"}
STATES = {"al": "ld₊al", "pal": "ld₊pal", "ai": "ai₊ai", "uil": "leuiu₊uil", "lfert": "lfd₊lfert", "pfr": "dlm₊pfr"}
OUTS = {"fpc": "ld₊fpc", "f": "ld₊f", "fioaa": "ld₊fioaa", "aiph": "ai₊aiph", "ly": "ai₊ly"}


def test_state_names_are_the_six_reference_states():
    assert set(STATE_NAMES) == set(STATES)


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_initial_state_matches_reference(ps):
    ref = reference(ps)
    y0 = Agriculture(ps).initial_state()
    for n, v in zip(STATE_NAMES, y0):
        assert abs(v - ref[STATES[n]][0]) <= 1e-8 * abs(ref[STATES[n]][0]), n


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_initial_outputs_match_reference(ps):
    ref = reference(ps)
    s = Agriculture(ps)
    s.set_initial_inputs(recorded_initial_inputs(ps, INPUTS))
    s.reset(1900.0, 2100.0, 0.25)
    out = s.current_outputs()
    for n, col in OUTS.items():
        assert abs(out[n] - ref[col][0]) <= 1e-8 * abs(ref[col][0]), n


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a31_states_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Agriculture, ps, INPUTS, STATES, OUTS)
    tab = state_table(s, idx, ref, tight, STATES)
    for n, (e, yr, et, er, mean) in tab.items():
        print(f"agriculture {ps} {n}: port vs reference max {100*e:.3f}% (mean {100*mean:.3f}%, year {yr}); vs tight {100*et:.3f}%; "
              f"reference default vs tight {100*er:.3f}%")
        assert e <= TOL, f"{ps} {n}: {100*e:.3f}% in {yr}"


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_a31_published_outputs_within_2_percent(ps):
    s, res, idx, ref, tight = a31(Agriculture, ps, INPUTS, STATES, OUTS)
    for n, col in OUTS.items():
        e = relerr(res.series[("w3_agriculture", n)][idx], ref[col])
        print(f"agriculture {ps} output {n}: max {100*e.max():.3f}% in {ref['time'][int(e.argmax())]}")
        assert e.max() <= TOL, f"{ps} {n}: {100*e.max():.3f}%"


def test_parameter_sets_differ_as_documented():
    """D-015 finding 1: agriculture differs by ``alln`` (6000 -> 1000) and the ``lymc`` table; nothing else."""
    p74, t74 = PARAMETER_SETS["1974"]
    p04, t04 = PARAMETER_SETS["2004"]
    assert p74["alln"] == 6000.0 and p04["alln"] == 1000.0
    assert {k for k in p74 if p74[k] != p04[k]} == {"alln"}
    assert {k for k in t74 if t74[k] != t04[k]} == {"lymc"}


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_restart_in_1970_from_the_reference_state_stays_within_2_percent(ps):
    """D-019 mechanics: started in 1970 from the reference's own 1970 state."""
    s, res, idx, ref, tight = a31(Agriculture, ps, INPUTS, STATES, OUTS, t0=1970.0, use_1970_state=True)
    sel = ref["time"] >= 1970.0
    st = s.states()
    for n, col in STATES.items():
        e = relerr(st[n][idx[sel]], ref[col][sel])
        assert e.max() <= TOL, f"{ps} {n}: {100*e.max():.3f}%"


def test_sector_is_accepted_by_the_loop_and_units_are_checked():
    s = Agriculture("2004")
    assert set(s.inputs) == set(INPUTS)
    assert s.inputs["iopc"] == "dollars/person-year" and s.inputs["ppolx"] == "1"
    assert s.outputs["fpc"] == "vegetable-equivalent kilograms/person-year"
