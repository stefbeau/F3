"""Coupling loop (Phase 2, M0). Fixed step, explicit coupling at step boundaries, every exchanged series recorded.

Usage
-----
    model = Model([replay, s1], [Coupling("replay", "fpc", "s1_population", "fpc"), ...], t0=1900, t1=2100, dt=0.25)
    results = model.run()
    results.series[("s1_population", "pop")]        # outputs at every step boundary
    results.inputs[("s1_population", "fpc")]        # the input values each sector saw at the start of each step
    results.to_csv("folder")                        # one CSV per sector: outputs, and one for the inputs it saw

Scheme (per loop step k, from t_k = t0 + k*dt to t_{k+1}):
  1. snapshot = the published outputs of every sector at t_k;
  2. record outputs and inputs at t_k;
  3. advance every sector (its inputs come from the snapshot, or from the exact series of a replay sector);
  4. publish the new outputs (a slow sector, with ``period`` = m*dt, is advanced at every m-th step with h = period and
     publishes its outputs m steps later; in between its published value is held).
No averaging of fast inputs over a slow sector's period is done: a slow sector sees the value at the start of its period.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

import numpy as np

from f3.core.sector import Context, Sector


@dataclass(frozen=True)
class Coupling:
    """Output ``source_output`` of sector ``source`` feeds input ``target_input`` of sector ``target``."""

    source: str
    source_output: str
    target: str
    target_input: str


@dataclass
class Results:
    time: np.ndarray
    series: Dict[Tuple[str, str], np.ndarray] = field(default_factory=dict)     # (sector, output) -> values at t_k
    inputs: Dict[Tuple[str, str], np.ndarray] = field(default_factory=dict)     # (sector, input) -> values seen at t_k
    units: Dict[Tuple[str, str], str] = field(default_factory=dict)

    def to_csv(self, folder: str) -> List[str]:
        """Write ``<sector>_outputs.csv`` and ``<sector>_inputs.csv`` into ``folder``; return the file names."""
        os.makedirs(folder, exist_ok=True)
        written = []
        for kind, store in (("outputs", self.series), ("inputs", self.inputs)):
            sectors = sorted({s for s, _ in store})
            for s in sectors:
                names = sorted(n for (ss, n) in store if ss == s)
                fn = os.path.join(folder, f"{s}_{kind}.csv")
                with open(fn, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f, lineterminator="\n")
                    w.writerow(["time"] + [f"{n} [{self.units.get((s, n), '')}]" for n in names])
                    for i, t in enumerate(self.time):
                        w.writerow([repr(float(t))] + [repr(float(store[(s, n)][i])) for n in names])
                written.append(fn)
        return written


class Model:
    def __init__(self, sectors: Sequence[Sector], couplings: Sequence[Coupling], t0: float, t1: float, dt: float = 0.25):
        self.sectors = {s.name: s for s in sectors}
        if len(self.sectors) != len(sectors):
            raise ValueError("duplicate sector names")
        self.couplings = list(couplings)
        self.t0, self.t1, self.dt = float(t0), float(t1), float(dt)
        n = (self.t1 - self.t0) / self.dt
        if abs(n - round(n)) > 1e-9:
            raise ValueError(f"(t1 - t0) = {t1 - t0} is not a whole number of steps of {dt}")
        self.n_steps = int(round(n))
        self.multiple: Dict[str, int] = {}
        for s in sectors:
            if s.period is None:
                self.multiple[s.name] = 1
                continue
            m = s.period / self.dt
            if abs(m - round(m)) > 1e-9 or round(m) < 1:
                raise ValueError(f"sector {s.name!r}: period {s.period} is not a multiple of the loop step {dt}")
            if self.n_steps % int(round(m)) != 0:
                raise ValueError(f"sector {s.name!r}: the horizon is not a whole number of periods of {s.period}")
            self.multiple[s.name] = int(round(m))
        self._wiring: Dict[str, Dict[str, Tuple[str, str]]] = {name: {} for name in self.sectors}
        for c in self.couplings:
            for nm in (c.source, c.target):
                if nm not in self.sectors:
                    raise ValueError(f"coupling refers to unknown sector {nm!r}")
            src, tgt = self.sectors[c.source], self.sectors[c.target]
            if c.source_output not in src.outputs:
                raise ValueError(f"sector {c.source!r} has no output {c.source_output!r}")
            if c.target_input not in tgt.inputs:
                raise ValueError(f"sector {c.target!r} has no input {c.target_input!r}")
            if src.outputs[c.source_output] != tgt.inputs[c.target_input]:
                raise ValueError(f"unit mismatch: {c.source}.{c.source_output} is [{src.outputs[c.source_output]}] but "
                                 f"{c.target}.{c.target_input} expects [{tgt.inputs[c.target_input]}]")
            if c.target_input in self._wiring[c.target]:
                raise ValueError(f"input {c.target}.{c.target_input} is wired twice")
            self._wiring[c.target][c.target_input] = (c.source, c.source_output)
        for name, s in self.sectors.items():
            missing = [i for i in s.inputs if i not in self._wiring[name]]
            if missing:
                raise ValueError(f"sector {name!r}: inputs not wired: {missing}")

    def run(self) -> Results:
        N = self.n_steps
        time = np.array([self.t0 + k * self.dt for k in range(N + 1)])
        for s in self.sectors.values():
            s.reset(self.t0, self.t1, self.dt)
        published = {n: dict(s.current_outputs()) for n, s in self.sectors.items()}
        pending: Dict[str, Dict[str, float]] = {}
        res = Results(time=time)
        for n, s in self.sectors.items():
            for o, u in s.outputs.items():
                res.series[(n, o)] = np.empty(N + 1)
                res.units[(n, o)] = u
            for i, u in s.inputs.items():
                res.inputs[(n, i)] = np.empty(N + 1)
                res.units[(n, i)] = u

        def record(k: int, t: float, snapshot) -> None:
            for n, s in self.sectors.items():
                for o in s.outputs:
                    res.series[(n, o)][k] = snapshot[n][o]
                ctx = Context(s, self._wiring[n], snapshot, self.sectors)
                for i in s.inputs:
                    res.inputs[(n, i)][k] = ctx.input(i, t)

        for k in range(N):
            t = self.t0 + k * self.dt
            snapshot = {n: dict(v) for n, v in published.items()}
            record(k, t, snapshot)
            for n, s in self.sectors.items():
                m = self.multiple[n]
                if m == 1 or k % m == 0:
                    ctx = Context(s, self._wiring[n], snapshot, self.sectors)
                    s.advance(t, self.dt if m == 1 else s.period, ctx)
                    pending[n] = dict(s.current_outputs())
            for n in self.sectors:
                m = self.multiple[n]
                if m == 1 or (k + 1) % m == 0:
                    published[n] = pending[n]
        record(N, self.t0 + N * self.dt, {n: dict(v) for n, v in published.items()})
        return res
