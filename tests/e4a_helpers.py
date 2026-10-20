"""Shared helpers for the M4 tests (docs/tracks/track-c-plan.md): fixtures exported by audit/t0/earth4all_m4_export.jl from the
pinned Earth4All.jl run (MIT, commit 16f37d0), matched BY NAME. Error rule, tolerance and criterion sets are those fixed in the
plan before any result: +-2% (D-004) at every 0.5-year point, true relative error, near-zero rule 1e-6 x max|reference|."""

from __future__ import annotations

import csv
import importlib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from f3.core import Coupling, Model, ReplaySector

FIX = Path(__file__).parent / "fixtures"
AUD = Path(__file__).parent.parent / "audit" / "data"
TOL = 0.02                      # D-004
SCENARIOS = ("tltl", "gl")
T0, T1 = 1980.0, 2100.0
FINE = 1.0 / 64.0               # Earth4All.jl's own Euler step

MODULES = {"output": "e4a_output", "inventory": "e4a_inventory", "finance": "e4a_finance", "labourmarket": "e4a_labourmarket",
           "public": "e4a_public", "demand": "e4a_demand", "energy": "e4a_energy", "other": "e4a_other"}
REPLACED = ("population", "climate", "foodland", "wellbeing")


@lru_cache(maxsize=None)
def _load(path: str) -> Dict[str, np.ndarray]:
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def reference(scen: str) -> Dict[str, np.ndarray]:
    """Columns ``sector.VAR`` at the 0.5-year points 1980 ... 2100 (241 rows)."""
    return _load(str(FIX / f"e4a_reference_{scen}.csv"))


def signals(scen: str) -> Dict[str, np.ndarray]:
    """Columns ``sector.VAR`` of every variable that crosses a sector boundary, on the 1/16-year grid."""
    return _load(str(FIX / f"e4a_signals_{scen}.csv"))


def vensim_error(scen: str) -> Dict[Tuple[str, str], dict]:
    """Earth4All.jl's OWN error against Vensim (true relative error, names and figures only; D-014, D-018)."""
    rows = list(csv.DictReader(open(AUD / f"e4a_vs_vensim_{scen}.csv", encoding="utf-8")))
    return {(r["sector"], r["variable"]): r for r in rows}


def sector_class(key: str):
    mod = importlib.import_module(f"f3.sectors.{MODULES[key]}")
    return mod, getattr(mod, "SECTOR_CLASS")


def signal_column(name: str, scen: str, exclude_sector: Optional[str] = None) -> str:
    cols = [c for c in signals(scen) if c.endswith("." + name) and (exclude_sector is None or not c.startswith(exclude_sector + "."))]
    if len(cols) != 1:
        raise KeyError(f"signal {name!r}: columns {cols}")
    return cols[0]


def replay_for(inputs: Sequence[str], scen: str, units: Dict[str, str], sector: str, overrides: Optional[Dict[str, np.ndarray]] = None) -> ReplaySector:
    s = signals(scen)
    series = {}
    for n in inputs:
        series[n] = overrides[n] if overrides and n in overrides else s[signal_column(n, scen, exclude_sector=sector)]
    return ReplaySector("recorded_inputs", s["time"], series, {n: units[n] for n in inputs})


def run_alone(key: str, scen: str, dt: float, method: str = "rk4", substep: Optional[float] = None, switches: Optional[Dict[str, float]] = None,
              overrides: Optional[Dict[str, np.ndarray]] = None, params: Optional[Dict[str, float]] = None, t1: float = T1):
    mod, cls = sector_class(key)
    sector = cls(scenario=scen, method=method, substep=substep, switches=switches, params=params)
    sector.set_initial_inputs({n: float(np.interp(T0, signals(scen)["time"], overrides[n] if overrides and n in overrides else
                                                    signals(scen)[signal_column(n, scen, exclude_sector=key)])) for n in sector.inputs})
    rp = replay_for(list(sector.inputs), scen, sector.inputs, key, overrides)
    model = Model([rp, sector], [Coupling("recorded_inputs", n, sector.name, n) for n in sector.inputs], t0=T0, t1=t1, dt=dt)
    return sector, model.run()


def rel_err(a: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]:
    """True relative error at each point; None if the reference is identically zero (the variable is excluded and listed)."""
    scale = float(np.max(np.abs(b)))
    if scale == 0.0:
        return None
    thr = 1e-6 * scale
    big = np.abs(b) > thr
    e = np.zeros_like(b, dtype=float)
    e[big] = np.abs(a[big] - b[big]) / np.abs(b[big])
    small = ~big
    e[small] = np.where(np.abs(a[small] - b[small]) <= thr, 0.0, np.inf)
    return e


def grid_index(time: np.ndarray, ref_time: np.ndarray) -> np.ndarray:
    idx = np.array([int(np.argmin(np.abs(time - t))) for t in ref_time])
    assert np.allclose(time[idx], ref_time, atol=1e-9)
    return idx


@dataclass
class Row:
    name: str
    max_err: float
    year_of_max: float
    first_year_above: Optional[float]
    excluded: bool = False


def compare(res, sector_name: str, scen: str, names: Sequence[str]) -> Dict[str, Row]:
    """Port against the reference, by name, at the 0.5-year points; ``names`` are the package's symbols."""
    ref = reference(scen)
    idx = grid_index(res.time, ref["time"])
    out = {}
    for n in names:
        a = res.series[(sector_name, n)][idx]
        e = rel_err(a, ref[f"{sector_name}.{n}"])
        if e is None:
            out[n] = Row(n, 0.0, float("nan"), None, excluded=True)
            continue
        above = np.where(e > TOL)[0]
        out[n] = Row(n, float(e.max()), float(ref["time"][int(e.argmax())]), float(ref["time"][above[0]]) if len(above) else None)
    return out


def worst(rows: Dict[str, Row]) -> Row:
    live = [r for r in rows.values() if not r.excluded]
    return max(live, key=lambda r: r.max_err)


def all_variables(sector_name: str, scen: str) -> List[str]:
    p = sector_name + "."
    return [c[len(p):] for c in reference(scen) if c.startswith(p)]


@dataclass
class Case:
    """One sector's criterion set (plan, section 1 table)."""
    key: str
    states: Tuple[str, ...]
    headline: Tuple[str, ...]

    @property
    def criterion(self) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(self.states + self.headline))


@lru_cache(maxsize=None)
def cached_run(key: str, scen: str, dt: float, method: str, substep: Optional[float]):
    sector, res = run_alone(key, scen, dt, method, substep)
    return sector, res


def report_line(case: Case, tag: str, scen: str, rows: Dict[str, Row]) -> str:
    live = [r for r in rows.values() if not r.excluded]
    w = max(live, key=lambda r: r.max_err)
    ex = [r.name for r in rows.values() if r.excluded]
    veps = vensim_error(scen)
    v = veps.get((case.key, w.name))
    vs = f"; Earth4All.jl vs Vensim for this variable: p95 {100 * float(v['p95']):.2f}%, max {100 * float(v['maximum']):.2f}%" if v and v["all_zero"] != "true" else ""
    return (f"{case.key} {scen} {tag}: worst {w.name} {100 * w.max_err:.4f}% (year {w.year_of_max}), first above 2%: "
            f"{[(r.name, r.first_year_above) for r in live if r.first_year_above is not None][:4]}, excluded (identically zero): {ex}{vs}")
