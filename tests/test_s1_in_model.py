"""A0.1 and A0.2 of docs/phase-2-plan.md: S1 inside the coupling loop equals stand-alone S1.

Acceptance criterion (written before the work, in the plan): relative difference at most 1e-9 on all 15 states, both
parameter sets, and the 22 existing S1 tests still pass. A0.2 (the equations in ``s1_population.py`` are untouched) is
checked against git in ``test_s1_population_equations_unchanged``.
"""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path

import numpy as np
import pytest

from f3.core import Coupling, Model, ReplaySector
from f3.sectors.s1_population import STATE_NAMES, Inputs, PopulationSector
from f3.sectors.s1_sector import S1Population

FIX = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-9


def _load(p: Path) -> dict:
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def _setup(ps: str):
    inp = _load(FIX / f"s1_inputs_world3_{'1974' if ps == '1974' else '2004'}.csv")
    series = {"fpc": inp["dr₊fpc"], "sopc": inp["br₊sopc"], "iopc": inp["dr₊iopc"], "ppolx": inp["dr₊ppolx"]}
    units = S1Population.inputs
    replay = ReplaySector("recorded_inputs", inp["time"], series, units)
    couplings = [Coupling("recorded_inputs", n, "s1_population", n) for n in series]
    return inp, replay, couplings


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_s1_in_model_equals_standalone_s1(ps):
    inp, replay, couplings = _setup(ps)
    standalone = PopulationSector(ps).run(Inputs(inp["time"], inp["dr₊fpc"], inp["br₊sopc"], inp["dr₊iopc"],
                                                 inp["dr₊ppolx"]), dt=0.25)
    s1 = S1Population(ps)
    res = Model([replay, s1], couplings, t0=1900.0, t1=2100.0, dt=0.25).run()
    assert np.array_equal(np.array(s1.time_history), standalone["time"])
    assert np.array_equal(res.time, standalone["time"])
    states = s1.states()
    worst = 0.0
    for n in STATE_NAMES:
        a, b = states[n], standalone[n]
        e = np.abs(a - b) / np.maximum(np.abs(b), 1e-30)
        worst = max(worst, float(e.max()))
        assert e.max() <= TOL, f"{ps} {n}: {e.max():.3e}"
    # published outputs agree with the stand-alone cohorts
    for n in ("p1", "p2", "p3", "p4", "pop"):
        e = np.abs(res.series[("s1_population", n)] - standalone[n]) / np.maximum(np.abs(standalone[n]), 1e-30)
        assert e.max() <= TOL
    print(f"S1 in model vs stand-alone, {ps}: worst relative difference over 15 states = {worst:.3e}")


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_s1_in_model_equals_standalone_from_1970(ps):
    """The D-019 mechanics (restart in 1970 from a recorded state) work inside the loop as they do stand-alone."""
    inp, replay, couplings = _setup(ps)
    ref = _load(FIX / f"s1_reference_world3_{'1974' if ps == '1974' else '2004'}_default.csv")
    i70 = int(np.where(np.isclose(ref["time"], 1970.0))[0][0])
    names = {"p1": "pop₊p1", "p2": "pop₊p2", "p3": "pop₊p3", "p4": "pop₊p4", "ehspc": "dr₊ehspc", "ple": "br₊ple",
             "ple2": "br₊ple2", "ple1": "br₊ple1", "diopc": "br₊diopc", "diopc2": "br₊diopc2", "diopc1": "br₊diopc1",
             "aiopc": "br₊aiopc", "fcfpc": "br₊fcfpc", "fcfpc2": "br₊fcfpc2", "fcfpc1": "br₊fcfpc1"}
    y0 = np.array([ref[names[n]][i70] for n in STATE_NAMES])
    standalone = PopulationSector(ps).run(Inputs(inp["time"], inp["dr₊fpc"], inp["br₊sopc"], inp["dr₊iopc"],
                                                 inp["dr₊ppolx"]), t0=1970.0, dt=0.25, y0=y0)
    s1 = S1Population(ps, y0=y0)
    Model([replay, s1], couplings, t0=1970.0, t1=2100.0, dt=0.25).run()
    for n in STATE_NAMES:
        e = np.abs(s1.states()[n] - standalone[n]) / np.maximum(np.abs(standalone[n]), 1e-30)
        assert e.max() <= TOL, f"{ps} {n}: {e.max():.3e}"


def test_switch_time_must_be_on_the_loop_grid():
    """A step that would straddle the 1940 switch is refused, not silently integrated across it."""
    inp, replay, couplings = _setup("1974")
    # 1940 is 39.5 years after 1900.5: not a whole number of steps of 1.0, so the loop must refuse
    with pytest.raises(ValueError, match="grid"):
        Model([replay, S1Population("1974")], couplings, t0=1900.5, t1=2100.5, dt=1.0).run()


def test_s1_population_equations_unchanged():
    """A0.2: ``s1_population.py`` has not been modified by the coupling work (compared with the last commit that
    touched it before M0 began, cc9f791)."""
    out = subprocess.run(["git", "diff", "--stat", "cc9f791", "--", "f3/sectors/s1_population.py"], cwd=ROOT,
                         capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("git history not available (shallow clone)")
    assert out.stdout.strip() == "", f"s1_population.py differs from cc9f791:\n{out.stdout}"
