"""Link 7 of the connections map: World3 to emissions (D-069; readings in docs/link7-tests.md). OFF unless called.

Fossil CO2 = World3 industrial output x k(t), with k(t) = exp(a + b t) fitted in-sample to 1970-2024 (the CO2 FFI series FaIR itself is given)
and extended at the same trend. From 2026 this REPLACES the prescribed fossil CO2; up to 2025 nothing changes. One-way: the warming does not feed
back into the World3 run through this link. Non-CO2 emissions and land-use CO2 stay prescribed (D-021); the climate starts about 0.04 to 0.07 K
below observed (D-030). The fitted parameters and the fit's error figures are stored in f3/data/link7_intensity.json; the observed series is not.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

PARAMS_JSON = Path(__file__).resolve().parents[1] / "data" / "link7_intensity.json"
FIT_YEARS = range(1970, 2025)
FIRST_YEAR, LAST_YEAR = 2026, 2099
NOTICE = ("Link 7 is one-way and off by default: from 2026 the prescribed fossil CO2 is replaced by World3 industrial output times an intensity fitted "
          "in-sample to 1970-2024 and extended at its fitted trend. The warming does not feed back into World3 through this link. Non-CO2 emissions and "
          "land-use CO2 are prescribed, not modelled (D-021); the climate starts about 0.04 to 0.07 K below observed (D-030). World3 with changed "
          "levers has not been compared with its reference.")


@lru_cache(maxsize=None)
def _world3_io(levers: Tuple[Tuple[str, float], ...]) -> tuple:
    from f3.core import Model
    from f3.sectors.world3 import STATE_COLUMNS, _initial_inputs, build_world3
    from f3.sectors.world3_group import World3Group
    sectors, couplings = build_world3("2004")
    for s in sectors:
        if hasattr(s, "params"):
            for k, v in levers:
                if k in s.params:
                    s.params[k] = v
    g = World3Group(sectors, couplings, _initial_inputs(sectors, 1900.0), STATE_COLUMNS, damage_option=None, warming=None)
    res = Model([g], [], t0=1900.0, t1=2100.0, dt=0.25).run()
    io = res.series[(g.name, "io")]
    return tuple((int(round(t)), float(v)) for t, v in zip(res.time, io) if abs(t - round(t)) < 1e-9)


def world3_io(**levers: float) -> Dict[int, float]:
    """World3 industrial output on 1 January of each year 1900-2100 (2004 parameter set, D-031 group); levers as in the Explorer (nri, lyf2, ppgf21)."""
    return dict(_world3_io(tuple(sorted(levers.items()))))


def observed_ffi_gt() -> Dict[int, float]:
    """Fossil CO2 (Gt CO2 a year) that FaIR is given for 1970-2024: the pinned file with GCB 2025 for 2023-2024. Read from the cache; not stored."""
    from f3.sectors.s6_climate import ClimateSetup, inputs
    e = inputs().emissions_for(ClimateSetup()).query("scenario == 'medium-extension'")
    row = e.loc[e["variable"] == "CO2 FFI"]
    return {y: float(row[f"{y}.5"].iloc[0]) for y in FIT_YEARS}


def fit_intensity(obs: Dict[int, float], io: Dict[int, float]) -> Tuple[float, float]:
    """Least squares of ln(obs / io) on the year, 1970-2024: returns (a, b) of k(t) = exp(a + b t)."""
    t = np.array(list(FIT_YEARS), dtype=float)
    y = np.log(np.array([obs[int(v)] / io[int(v)] for v in t]))
    b, a = np.polyfit(t, y, 1)
    return float(a), float(b)


def params() -> Tuple[float, float]:
    p = json.loads(PARAMS_JSON.read_text(encoding="utf-8"))
    return float(p["a"]), float(p["b"])


def modelled_ffi_gt(io: Dict[int, float]) -> Dict[int, float]:
    a, b = params()
    return {y: v * math.exp(a + b * y) for y, v in io.items()}


def replacement_gt(io: Dict[int, float]) -> Dict[int, float]:
    m = modelled_ffi_gt(io)
    return {y: m[y] for y in range(FIRST_YEAR, LAST_YEAR + 1)}


def setup_with(replace: Optional[Dict[int, float]], extra: Optional[Dict[int, float]] = None, n_members: int = 841):
    from f3.sectors.s6_climate import ClimateSetup
    return ClimateSetup(n_members=n_members, co2_ffi_replace=tuple(sorted(replace.items())) if replace else None,
                        co2_ffi_extra=tuple(sorted(extra.items())) if extra else None)


def climate(replace: Optional[Dict[int, float]], extra: Optional[Dict[int, float]] = None, n_members: int = 841) -> Dict[str, np.ndarray]:
    """One FaIR run to 2100 (link 6's L6-T6 shows one run equals the sector's yearly re-runs to 1e-9)."""
    from f3.sectors.s6_climate import anomaly_on_bounds, run_fair
    f = run_fair(2100, setup_with(replace, extra, n_members))
    a = anomaly_on_bounds(f)
    tb = np.asarray(f.timebounds)
    keep = [int(np.where(tb == y)[0][0]) for y in range(2025, 2101)]
    co2 = f.concentration.sel(specie="CO2").values[:, 0, :]
    return {"years": np.arange(2025, 2101), "warming": a[keep].mean(axis=1), "warming_p05": np.percentile(a[keep], 5, axis=1),
            "warming_p95": np.percentile(a[keep], 95, axis=1), "co2_concentration": co2[keep].mean(axis=1)}


# ------------------------------------------------------------------------------------------------------------------------------------------
# Variant B (POST-HOC, docs/link7-variant-b.md): written after the first form failed its hindcast. The first form above is unchanged.
PARAMS_B_JSON = Path(__file__).resolve().parents[1] / "data" / "link7_intensity_b.json"
LEVER_GRID = {"nri": (0.5e12, 1.0e12, 2.0e12), "lyf2": (1.0, 1.5, 2.0), "ppgf21": (1.0, 0.5, 0.25)}          # the Explorer's 27 settings (D-046)


def select_reference(gdp: Dict[int, float]) -> Tuple[Dict[str, float], float]:
    """The lever setting whose industrial output, indexed to 1970, is closest to observed GDP indexed to 1970 over 1970-2024 (RMS of log differences).
    The emissions series is not read."""
    import itertools
    best = None
    for combo in itertools.product(*LEVER_GRID.values()):
        lv = dict(zip(LEVER_GRID, combo))
        io = world3_io(**lv)
        d = np.array([math.log(io[y] / io[1970]) - math.log(gdp[y] / gdp[1970]) for y in FIT_YEARS])
        rms = float(np.sqrt((d ** 2).mean()))
        if best is None or rms < best[1] - 1e-15:
            best = (lv, rms)
    return best


def reference_levers() -> Dict[str, float]:
    return dict(json.loads(PARAMS_B_JSON.read_text(encoding="utf-8"))["reference_levers"])


def params_b() -> Tuple[float, float]:
    p = json.loads(PARAMS_B_JSON.read_text(encoding="utf-8"))
    return float(p["a"]), float(p["b"])


def prescribed_ffi_gt(year: int) -> float:
    from f3.sectors.s6_climate import ClimateSetup, inputs
    e = inputs().emissions_for(ClimateSetup()).query("scenario == 'medium-extension'")
    return float(e.loc[e["variable"] == "CO2 FFI", f"{year}.5"].iloc[0])


def join_factor(io: Dict[int, float]) -> float:
    """h: the constant that makes this run's 2025 value equal the prescribed 2025 value."""
    a, b = params_b()
    return prescribed_ffi_gt(2025) / (io[2025] * math.exp(a + b * 2025))


def replacement_gt_b(io: Dict[int, float]) -> Dict[int, float]:
    a, b = params_b()
    h = join_factor(io)
    return {y: io[y] * math.exp(a + b * y) * h for y in range(FIRST_YEAR, LAST_YEAR + 1)}
