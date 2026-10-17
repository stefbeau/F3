"""Shared helpers for the M3 tests (docs/tracks/track-b.md): fixtures exported by audit/t0/world3_m3_export.jl, matched by name."""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np

from f3.core import Coupling, Model, ReplaySector

FIX = Path(__file__).parent / "fixtures"
TAGS = {"1974": "world3_1974", "2004": "world3_2004"}
TOL = 0.02          # D-004


@lru_cache(maxsize=None)
def load(name: str) -> Dict[str, np.ndarray]:
    rows = list(csv.DictReader(open(FIX / name, encoding="utf-8-sig")))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def signals(ps: str) -> Dict[str, np.ndarray]:
    return load(f"w3_signals_{TAGS[ps]}.csv")


def reference(ps: str, kind: str = "default") -> Dict[str, np.ndarray]:
    return load(f"w3_reference_{TAGS[ps]}_{kind}.csv")


def relerr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs(a - b) / np.maximum(np.abs(b), 1e-30)


def replay(ps: str, mapping: Dict[str, str], units: Dict[str, str]) -> ReplaySector:
    """Recorded inputs of a sector: ``mapping`` is input name -> fixture column (WorldDynamics.jl name)."""
    s = signals(ps)
    return ReplaySector("recorded_inputs", s["time"], {k: s[v] for k, v in mapping.items()}, {k: units[k] for k in mapping})


def run_alone(sector, ps: str, mapping: Dict[str, str], t0: float = 1900.0, dt: float = 0.25):
    rp = replay(ps, mapping, sector.inputs)
    res = Model([rp, sector], [Coupling("recorded_inputs", n, sector.name, n) for n in mapping], t0=t0, t1=2100.0, dt=dt).run()
    return res


def grid_index(time: np.ndarray, ref_time: np.ndarray) -> np.ndarray:
    idx = np.array([int(np.argmin(np.abs(time - t))) for t in ref_time])
    assert np.allclose(time[idx], ref_time, atol=1e-9)
    return idx


def worst(states: Dict[str, np.ndarray], ref: Dict[str, np.ndarray], names: Dict[str, str], idx: np.ndarray) -> Dict[str, Tuple[float, float]]:
    """name -> (max relative error, year of max) of port ``states[name]`` against fixture column ``names[name]``."""
    out = {}
    t = ref["time"]
    for n, col in names.items():
        e = relerr(states[n][idx], ref[col])
        out[n] = (float(e.max()), float(t[int(e.argmax())]))
    return out
