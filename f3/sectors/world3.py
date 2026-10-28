"""The full World3 model in the coupling loop: S1 population plus the four M3 sectors (agriculture, capital, resources,
pollution). Interface and wiring code only; the equations are in ``s1_population.py`` and ``w3_*.py``.

The wiring below is the set of cross-sector variables of WorldDynamics.jl ``World3.historicalrun`` (``variable_connections``),
matched by name:

    S1 population        reads  fpc (agriculture), sopc and iopc (capital), ppolx (pollution)
    w3_agriculture       reads  pop (S1), io and iopc (capital), ppolx (pollution)
    w3_capital           reads  pop, p2, p3 (S1), fcaor (resources), fioaa, aiph, al (agriculture)
    w3_resources         reads  pop (S1), iopc (capital)
    w3_pollution         reads  pcrum (resources), pop (S1), aiph and al (agriculture)

Explicit coupling at step boundaries (D-022): each sector reads the start-of-step values of the others, held across the step.
Initial outputs: before the first step each sector's outputs are needed, and they depend on each other's; the dependency graph
at the start time has no cycle, so a few passes of evaluation (``_initial_inputs``) give the exact start-time values from the
initial states, with no recorded data.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Tuple

import numpy as np

from f3.core import Coupling, Model, Results
from f3.sectors.s1_population import STATE_NAMES as S1_STATES
from f3.sectors.s1_sector import S1Population
from f3.sectors.w3_agriculture import Agriculture, STATE_NAMES as AG_STATES
from f3.sectors.w3_capital import Capital, STATE_NAMES as CAP_STATES
from f3.sectors.w3_common import W3Sector
from f3.sectors.w3_pollution import Pollution, STATE_NAMES as POL_STATES
from f3.sectors.w3_resources import Resources, STATE_NAMES as RES_STATES

# state name -> WorldDynamics.jl variable name (fixture column), the 29 states of World3
STATE_COLUMNS: Dict[str, str] = {
    "p1": "pop₊p1", "p2": "pop₊p2", "p3": "pop₊p3", "p4": "pop₊p4", "ehspc": "dr₊ehspc",
    "ple": "br₊ple", "ple2": "br₊ple2", "ple1": "br₊ple1",
    "diopc": "br₊diopc", "diopc2": "br₊diopc2", "diopc1": "br₊diopc1", "aiopc": "br₊aiopc",
    "fcfpc": "br₊fcfpc", "fcfpc2": "br₊fcfpc2", "fcfpc1": "br₊fcfpc1",
    "al": "ld₊al", "pal": "ld₊pal", "ai": "ai₊ai", "uil": "leuiu₊uil", "lfert": "lfd₊lfert", "pfr": "dlm₊pfr",
    "ic": "is₊ic", "sc": "ss₊sc", "lufd": "js₊lufd", "nr": "nr₊nr",
    "ppapr1": "pp₊ppapr1", "ppapr2": "pp₊ppapr2", "ppapr3": "pp₊ppapr3", "ppol": "pp₊ppol",
}

# (source sector, source output) -> [(target sector, target input)]
_WIRING: List[Tuple[str, str, str, str]] = [
    ("w3_agriculture", "fpc", "s1_population", "fpc"),
    ("w3_capital", "sopc", "s1_population", "sopc"),
    ("w3_capital", "iopc", "s1_population", "iopc"),
    ("w3_pollution", "ppolx", "s1_population", "ppolx"),
    ("s1_population", "pop", "w3_agriculture", "pop"),
    ("w3_capital", "io", "w3_agriculture", "io"),
    ("w3_capital", "iopc", "w3_agriculture", "iopc"),
    ("w3_pollution", "ppolx", "w3_agriculture", "ppolx"),
    ("s1_population", "pop", "w3_capital", "pop"),
    ("s1_population", "p2", "w3_capital", "p2"),
    ("s1_population", "p3", "w3_capital", "p3"),
    ("w3_resources", "fcaor", "w3_capital", "fcaor"),
    ("w3_agriculture", "fioaa", "w3_capital", "fioaa"),
    ("w3_agriculture", "aiph", "w3_capital", "aiph"),
    ("w3_agriculture", "al", "w3_capital", "al"),
    ("s1_population", "pop", "w3_resources", "pop"),
    ("w3_capital", "iopc", "w3_resources", "iopc"),
    ("w3_resources", "pcrum", "w3_pollution", "pcrum"),
    ("s1_population", "pop", "w3_pollution", "pop"),
    ("w3_agriculture", "aiph", "w3_pollution", "aiph"),
    ("w3_agriculture", "al", "w3_pollution", "al"),
]


def build_world3(parameter_set: str = "2004", y0: Optional[Mapping[str, float]] = None):
    """Return ``(sectors, couplings)`` of the full World3 model. ``y0`` maps state names to start values (D-019 restart)."""
    def pick(names):
        return None if y0 is None else np.array([y0[n] for n in names], dtype=float)

    s1 = S1Population(parameter_set, y0=pick(S1_STATES))
    sectors = [s1, Agriculture(parameter_set, y0=pick(AG_STATES)), Capital(parameter_set, y0=pick(CAP_STATES)),
               Resources(parameter_set, y0=pick(RES_STATES)), Pollution(parameter_set, y0=pick(POL_STATES))]
    couplings = [Coupling(a, b, c, d) for a, b, c, d in _WIRING]
    return sectors, couplings


def _initial_inputs(sectors, t0: float) -> Dict[str, Dict[str, float]]:
    """Exact start-time inputs of the four M3 sectors from the initial states (no cycle at t0; five passes settle it)."""
    s1 = sectors[0]
    s1_out = _s1_outputs(s1)
    m3 = {s.name: s for s in sectors[1:]}
    out: Dict[str, Dict[str, float]] = {"s1_population": s1_out}
    for s in m3.values():
        out[s.name] = {k: 1.0 for k in s.outputs}                 # positive placeholders, overwritten by the passes
    inputs: Dict[str, Dict[str, float]] = {s.name: {} for s in m3.values()}
    for _ in range(6):
        for s in m3.values():
            for src, so, tgt, ti in _WIRING:
                if tgt == s.name:
                    inputs[s.name][ti] = out[src][so]
        for s in m3.values():
            y = s._y0 if s._y0 is not None else s.initial_state()
            out[s.name] = s.compute_outputs(y, inputs[s.name], t0)
    return inputs


def _s1_outputs(s1: S1Population) -> Dict[str, float]:
    y = s1._y0 if s1._y0 is not None else s1._sector.initial_state()
    p = [float(y[S1_STATES.index(n)]) for n in ("p1", "p2", "p3", "p4")]
    return {"p1": p[0], "p2": p[1], "p3": p[2], "p4": p[3], "pop": sum(p)}


def run_world3(parameter_set: str = "2004", t0: float = 1900.0, t1: float = 2100.0, dt: float = 0.25,
               y0: Optional[Mapping[str, float]] = None, substep: Optional[float] = 0.0625) -> Tuple[Dict[str, np.ndarray], Results]:
    """Run the full World3 model. Returns the 29 states by name at every loop-step boundary, and the loop results.

    D-031: by default the five World3 sectors form one group advanced with sub-steps of 0.0625 year inside each loop step
    (``substep=0.0625``). ``substep=None`` runs the five sectors directly in the loop at ``dt`` with plain start-of-step coupling (the
    M3 first version, whose A3.2 failure is recorded; kept for that record).
    """
    sectors, couplings = build_world3(parameter_set, y0)
    init = _initial_inputs(sectors, t0)
    if substep is None:
        for s in sectors[1:]:
            s.set_initial_inputs(init[s.name])
        res = Model(sectors, couplings, t0=t0, t1=t1, dt=dt).run()
        states: Dict[str, np.ndarray] = {}
        for s in sectors:
            states.update(s.states())
        return states, res
    from f3.sectors.world3_group import World3Group
    group = World3Group(sectors, couplings, init, STATE_COLUMNS, substep=substep)
    res = Model([group], [], t0=t0, t1=t1, dt=dt).run()
    return {n: res.series[(group.name, n)] for n in STATE_COLUMNS}, res
