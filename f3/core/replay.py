"""Replay sector: serves recorded series by name (the Phase 1 test method: a sector is tested alone against the inputs
its reference had). Values at times between samples are linearly interpolated, as ``f3.sectors.s1_population.Inputs`` does."""

from __future__ import annotations

from typing import Dict, Mapping

import numpy as np

from f3.core.sector import Context, Sector


class ReplaySector(Sector):
    exact_in_time = True

    def __init__(self, name: str, time: np.ndarray, series: Mapping[str, np.ndarray], units: Mapping[str, str]):
        self.name = name
        self._time = np.asarray(time, dtype=float)
        self._series = {k: np.asarray(v, dtype=float) for k, v in series.items()}
        if set(self._series) != set(units):
            raise ValueError("series and units must have the same names")
        self.outputs = dict(units)
        self.inputs = {}
        self._t = None

    def reset(self, t0: float, t1: float, dt: float) -> None:
        self._t = t0

    def advance(self, t: float, h: float, ctx: Context) -> None:
        self._t = t + h

    def current_outputs(self) -> Dict[str, float]:
        return {k: self.output_at(k, self._t) for k in self._series}

    def output_at(self, name: str, t: float) -> float:
        return float(np.interp(t, self._time, self._series[name]))
