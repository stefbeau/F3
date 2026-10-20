"""The eight reused Earth4All sectors as ONE Sector of the coupling loop (M4, A4.5; the D-031 pattern).

ATTRIBUTION: the members are ports of Earth4All.jl (MIT, commit 16f37d013a2f68135f03e7815bf861dbf47311f2, Copyright (c) 2023 World Dynamics),
see NOTICE and licenses/Earth4All.jl-MIT.txt and the headers of the member modules. This file is F3 interface code (Apache 2.0).

Rule (track-c-plan.md, written before the run; D-003 and D-022 are not edited): the members (output, inventory, finance, labour market,
public, demand, energy, other) are advanced with internal sub-steps of ``substep`` (default 1/64 year, the rung at which every sector
alone is within 2%) inside each 0.25-year loop step. Inside the group the coupling is explicit at the start of each sub-step: each member
reads the others' published values at the start of the sub-step, held across it. The group's own inputs (the signals of the replaced
sectors: POP, GDPP, EGDPP, A20PA, OW, CAC, COFO, IPP) come from the loop context (a ReplaySector in A4.5, adapters later, D-023) and
are read at the sub-step times. The group publishes every member output as ``<sector>.<NAME>`` at each loop boundary.

START-UP INPUT (labelled): the values the members read from each other at 1980 (needed to publish the first outputs, because the loop
publishes before it advances) are given by ``start_values``; in the tests they are the recorded Earth4All.jl values at 1980.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional

from f3.core.sector import Context, Sector
from f3.sectors.e4a_demand import DemandSector
from f3.sectors.e4a_energy import EnergySector
from f3.sectors.e4a_finance import FinanceSector
from f3.sectors.e4a_inventory import InventorySector
from f3.sectors.e4a_labourmarket import LabourMarketSector
from f3.sectors.e4a_other import OtherSector
from f3.sectors.e4a_output import OutputSector
from f3.sectors.e4a_public import PublicSector

SUBSTEP = 1.0 / 64.0
MEMBER_CLASSES = (OutputSector, InventorySector, FinanceSector, LabourMarketSector, PublicSector, DemandSector, EnergySector, OtherSector)


class _External(Sector):
    """Proxy that serves the group's own inputs from the loop context at any time inside the step."""

    name = "external"
    exact_in_time = True

    def __init__(self, ctx: Optional[Context], names):
        self._ctx = ctx
        self.outputs = {n: "" for n in names}

    def output_at(self, name: str, t: float) -> float:
        return self._ctx.input(name, t)


class E4AEconomy(Sector):
    name = "e4a_economy"

    def __init__(self, scenario: str = "tltl", method: str = "euler", substep: Optional[float] = None,
                 switches: Optional[Mapping[str, float]] = None, params: Optional[Mapping[str, float]] = None,
                 start_values: Optional[Mapping[str, float]] = None):
        self._sub = SUBSTEP if substep is None else float(substep)
        self.members: Dict[str, Sector] = {}
        for cls in MEMBER_CLASSES:
            sw = {k: v for k, v in (switches or {}).items() if k in cls.PARAMS}
            pr = {k: v for k, v in (params or {}).items() if k in cls.PARAMS}
            m = cls(scenario=scenario, method=method, substep=self._sub, switches=sw or None, params=pr or None)
            self.members[cls.SECTOR_KEY] = m
        # who computes each name (algebraic or state)
        owner: Dict[str, List[str]] = {}
        for k, m in self.members.items():
            for n in list(m.EQ) + list(m.STATE_NAMES):
                owner.setdefault(n, []).append(k)
        self._wiring: Dict[str, Dict[str, tuple]] = {k: {} for k in self.members}
        ext: Dict[str, str] = {}
        for k, m in self.members.items():
            for n, u in m.inputs.items():
                srcs = [s for s in owner.get(n, []) if s != k]
                if len(srcs) > 1:
                    raise ValueError(f"input {n!r} of {k!r} is computed by several members: {srcs}")
                if srcs:
                    self._wiring[k][n] = (srcs[0], n)
                else:
                    self._wiring[k][n] = ("external", n)
                    ext[n] = u
        self.inputs = dict(ext)
        self.outputs = {f"{k}.{n}": u for k, m in self.members.items() for n, u in m.outputs.items()}
        self._start = dict(start_values or {})
        self._published: Dict[str, Dict[str, float]] = {}
        self._init_inputs: Optional[Dict[str, float]] = None

    def set_initial_inputs(self, inp: Mapping[str, float]) -> None:
        self._init_inputs = {k: float(inp[k]) for k in self.inputs}

    def reset(self, t0: float, t1: float, dt: float) -> None:
        k = dt / self._sub
        if abs(k - round(k)) > 1e-9 or round(k) < 1:
            raise ValueError(f"loop step {dt} is not a whole number of sub-steps of {self._sub}")
        self._n_sub = int(round(k))
        self._h = dt / self._n_sub
        if self._init_inputs is None:
            raise ValueError("initial inputs not set")
        for key, m in self.members.items():
            init = {}
            for n in m.inputs:
                src, nm = self._wiring[key][n]
                if src == "external":
                    init[n] = self._init_inputs[n]
                elif n in self._start:
                    init[n] = self._start[n]
                else:
                    raise ValueError(f"start-up value of {n!r} (read by {key!r} from {src!r}) not given")
            m.set_initial_inputs(init)
            m.reset(t0, t1, self._h)
        self._published = {k: dict(m.current_outputs()) for k, m in self.members.items()}

    def current_outputs(self) -> Dict[str, float]:
        return {f"{k}.{n}": v for k, d in self._published.items() for n, v in d.items()}

    def advance(self, t: float, h: float, ctx: Context) -> None:
        ext = _External(ctx, list(self.inputs))
        members = dict(self.members)
        members["external"] = ext
        for j in range(self._n_sub):
            tt = t + j * self._h
            snapshot = {k: dict(v) for k, v in self._published.items()}
            snapshot["external"] = {}
            pending = {}
            for key, m in self.members.items():
                m.advance(tt, self._h, Context(m, self._wiring[key], snapshot, members))
                pending[key] = dict(m.current_outputs())
            self._published = pending

    def states(self, sector: str) -> Dict[str, "object"]:
        return self.members[sector].states()
