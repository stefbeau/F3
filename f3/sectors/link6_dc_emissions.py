"""Link 6 of the connections map: data-centre electricity to emissions (D-069; readings in docs/link6-tests.md). OFF unless called.

One-way: the electricity path is computed first (S3 under R3 with the build-rate limit of step E1, no climate), turned into an addition to the
prescribed fossil CO2 of FaIR, and FaIR is run once with it. The warming this adds does not feed back on the electricity.

* Intensity: CO2 from electricity over electricity produced, from the recorded Earth4All.jl run (tests/fixtures/e4a_reference_tltl.csv), using
  Earth4All's own identities (CO2EP, FFE): fossil fuel for electricity x t CO2 per toe x (1 - captured share) / electricity production.
* Baseline (Provisional, the editor's to confirm): the 2025 level, 485 TWh a year, held constant. The prescribed path already contains some
  data-centre growth of unknown size, so the addition is an upper reading.
* Non-CO2 emissions and land-use CO2 stay prescribed (D-021); the climate starts about 0.04 to 0.07 K below observed (D-030).
"""
from __future__ import annotations

import warnings
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from f3.sectors.s4_datacentre import IEA_2025_TWH

REFERENCE_CSV = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "e4a_reference_tltl.csv"
BASELINE_TWH = IEA_2025_TWH                       # 485 TWh a year: electricity already counted in the prescribed emissions (assumption)
FIRST_YEAR, LAST_YEAR = 2026, 2099
NOTICE = ("Link 6 is one-way and off by default: data-centre electricity above the 2025 level of 485 TWh a year, times the carbon intensity of electricity "
          "in the recorded Earth4All run, is added to the prescribed fossil CO2. The warming it adds does not feed back on the electricity. The baseline "
          "is an assumption, so the addition is an upper reading. Non-CO2 emissions and land-use CO2 are prescribed, not modelled (D-021); the climate "
          "starts about 0.04 to 0.07 K below observed (D-030). The electricity comes from S3 under F3's own investment rule, whose levels are unvalidated.")


@lru_cache(maxsize=1)
def intensity_kg_per_kwh() -> Dict[int, float]:
    """kg CO2 per kWh of electricity, by calendar year (value on 1 January), from the recorded Earth4All.jl TLTL run."""
    d = pd.read_csv(REFERENCE_CSV)
    d = d[np.isclose(d["time"] % 1.0, 0.0)]
    co2 = d["energy.FFE"] * d["energy.TCO2PT"] / 1000.0 * (1.0 - d["energy.FCO2SCCS"])     # Gt CO2 a year from electricity
    return {int(round(t)): float(v) for t, v in zip(d["time"], co2 / d["energy.EP"] * 1000.0)}   # Gt/TWh x 1000 = kg/kWh


#: POST-HOC calibration to the IEA Base Case (Energy and AI, 2025): 15% a year to 2030, then 4.9% a year ((1200 / 945)^(1/5) - 1), kept after 2035. Not a validation.
IEA_BASE_SCHEDULE = ((2025.0, 0.15), (2030.0, 0.049))


@lru_cache(maxsize=None)
def _electricity(g_max: float, outer_share: float, supply_scale: float, power_aware: bool, schedule: Optional[tuple] = None) -> tuple:
    from f3.core.model import Coupling, Model
    from f3.sectors.s3_ai import GateParams, S3AI
    from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
    from f3.sectors.s4_datacentre import DataCentre, DCParams, supply_series
    gp = GateParams()
    s3 = S3AI(gp, rule=R3Rule(R3Levers(power_aware=power_aware)), electricity_limited=True)
    dc = DataCentre(gp, DCParams(supply_scale=supply_scale, g_max=g_max, outer_share=outer_share, g_max_schedule=schedule))
    cp = [Coupling("earth4all_supply", "supply", "s4_datacentre", "supply"), Coupling("s3_ai", "compute_stock", "s4_datacentre", "compute_stock"),
          Coupling("s3_ai", "hardware", "s4_datacentre", "hardware"), Coupling("s4_datacentre", "supply_ratio", "s3_ai", "supply_ratio")]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = Model([s3, dc, supply_series("TLTL")], cp, t0=2025.0, t1=2100.0, dt=0.25).run()
    t, e = np.asarray(res.time, dtype=float), np.asarray(res.series[("s4_datacentre", "e_dc")], dtype=float)
    return tuple((y, float(e[(t > y + 1e-9) & (t <= y + 1.0 + 1e-9)].mean())) for y in range(2025, 2100))   # mean rate over the calendar year


def electricity_used_twh(g_max: float, outer_share: float = 0.25, supply_scale: float = 1.0, power_aware: bool = False, schedule: Optional[tuple] = None) -> Dict[int, float]:
    """Data-centre electricity used, TWh in each calendar year 2025 to 2099, with the build-rate limit of step E1 (it must be finite)."""
    if not np.isfinite(g_max):
        raise ValueError("link 6 needs the build-rate limit of step E1 (a finite g_max): without it the electricity is not bounded")
    return dict(_electricity(float(g_max), float(outer_share), float(supply_scale), bool(power_aware), tuple(schedule) if schedule else None))


def extra_co2_gt(used_twh: Dict[int, float]) -> Dict[int, float]:
    """Gt CO2 added in each calendar year 2026 to 2099: (electricity used - baseline) x intensity, never negative."""
    k = intensity_kg_per_kwh()
    return {y: max(0.0, used_twh[y] - BASELINE_TWH) * k[y] * 1e-3 for y in range(FIRST_YEAR, LAST_YEAR + 1)}


def setup_with(extra: Optional[Dict[int, float]], n_members: int = 841):
    from f3.sectors.s6_climate import ClimateSetup
    return ClimateSetup(n_members=n_members, co2_ffi_extra=tuple(sorted(extra.items())) if extra else None)


def climate(extra: Optional[Dict[int, float]], n_members: int = 841) -> Dict[str, np.ndarray]:
    """One FaIR run to 2100 with the addition; values on each 1 January from 2025 (L6-T6 checks this against the sector's yearly re-runs)."""
    from f3.sectors.s6_climate import anomaly_on_bounds, run_fair
    f = run_fair(2100, setup_with(extra, n_members))
    a = anomaly_on_bounds(f)
    tb = np.asarray(f.timebounds)
    keep = [int(np.where(tb == y)[0][0]) for y in range(2025, 2101)]
    co2 = f.concentration.sel(specie="CO2").values[:, 0, :]
    return {"years": np.arange(2025, 2101), "warming": a[keep].mean(axis=1), "warming_p05": np.percentile(a[keep], 5, axis=1),
            "warming_p95": np.percentile(a[keep], 95, axis=1), "co2_concentration": co2[keep].mean(axis=1)}
