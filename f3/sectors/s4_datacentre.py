"""Data-centre electricity module (spec S4: E_dc = C_hw_operating / eta_hw * PUE), M2 slice; track A, Provisional P-A1 and P-A2.

Form
----
    E_dc [TWh/year] = compute_stock [FLOP/year] / eta_hw [FLOP/J] * PUE / 3.6e15 [J/TWh]
    eta_hw(t)      = eta_0 * hardware(t) / hardware(2025)     (S3's hardware price-performance drives energy efficiency; assumption)

Calibration (NOT validation)
----------------------------
``eta_0`` is chosen once so that E_dc(2025) equals the IEA's 485 TWh for 2025 (IEA, Key Questions on Energy and AI, 2026, CC BY 4.0). That
number is a CALIBRATION point; the IEA's 415 TWh for 2024 is a reference value (an input before 2025, D-020); the IEA's 950 TWh for 2030
is a report-only comparison. None of them is a validation of the module, and no independent test of modelled data-centre electricity against
estimates exists before 2025 (plan 14.2a). ``eta_0`` is a calibration constant, not a hardware measurement.
Boundary: a data centre is a facility housing servers, storage, networking equipment and associated components (IEA, Energy and AI); whether
crypto-mining load is excluded from the IEA totals is [unverified]. PUE = 1.4, between the IEA's ranges (1.1 to 1.2 best-in-class
hyperscale, 1.5 to 1.7 older or enterprise sites; Key Questions); an input, labelled.

Optional efficiency cap (D-055, Provisional; default OFF)
-----------------------------------------------------------
``DCParams.eta_cap`` (FLOP/J; ``None`` = OFF, every recorded result unchanged) bounds ``eta`` by the physical efficiency behind the paper's compute limit
``C_L``: ``PAPER_ETA_CAP = 4e15`` FLOP/J (GATE paper, arXiv:2503.04941, appendix D.3.2: the theoretical maximum CMOS efficiency). With the cap set,
``eta = min(eta_0 x hardware / H0, eta_cap)``. A binding cap RAISES demand (demand is compute / eta); with the supply limit on, the changed ``supply_ratio`` also changes S3.
Hand check: ``eta_0`` is about 8.06e9 FLOP/J, so at S3's hardware ceiling
``H_max`` (1e5 times ``H0``) ``eta`` is 8.06e14, below the cap: with S3's own hardware limit the paper's cap cannot bind.

Electricity link to World3 (D-059, Provisional; default OFF in M6)
-------------------------------------------------------------------
``industry_ratio = clip((supply x supply_scale - e_dc) / (supply_2025 - 485 TWh), 0, 1)``: the electricity left for everything but data centres,
relative to its 2025 level. The M6 wiring (``M6Config.electricity_link``) feeds it to World3 as a multiplier on industrial output. No new coefficient.

Loop B1 (electricity limit)
---------------------------
Electricity available to data centres = ``dc_share_cap`` x total supply, where total supply is a recorded series (Earth4All.jl electricity
production ``ene.EP``, pinned commit 16f37d0, scenario TLTL by default, ``f3/data/earth4all_electricity_supply.csv``) times ``supply_scale``.
``e_dc_demand`` is what the installed compute would draw; ``e_dc = e_dc_demand * supply_ratio`` is the electricity actually used.
``supply_ratio = min(1, available / E_dc_demand)`` is an input to S3, which multiplies its usable compute by it. It is computed from the
start-of-step values, so it lags S3 by one period (explicit coupling, D-022). ``supply_scale = inf`` makes B1 inactive.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd

from f3.core.replay import ReplaySector
from f3.core.sector import Context, Sector
from f3.sectors.s3_ai import GateParams

J_PER_TWH = 3.6e15
IEA_2024_TWH = 415.0          # reference value (Energy and AI, 2025), an input, not a validation
IEA_2025_TWH = 485.0          # calibration point (Key Questions on Energy and AI, 2026)
IEA_2030_TWH = 950.0          # IEA projection, report-only comparison (Key Questions); 945 in Energy and AI
PAPER_ETA_CAP = 4.0e15        # FLOP/J, theoretical maximum CMOS efficiency behind C_L (GATE paper, appendix D.3.2); D-055 option, default off
SUPPLY_CSV = Path(__file__).resolve().parents[1] / "data" / "earth4all_electricity_supply.csv"
BOUNDARY = ("data centre = a facility housing servers, storage, networking equipment and associated components (IEA, Energy and AI); "
            "whether crypto-mining load is excluded from the IEA totals is [unverified]")


@dataclass(frozen=True)
class DCParams:
    pue: float = 1.4
    calibration_twh_2025: float = IEA_2025_TWH
    dc_share_cap: float = 0.05        # share of total electricity supply available to data centres (Provisional P-A2)
    supply_scale: float = 1.0         # scenario lever on the supply series; math.inf = unlimited
    eta_cap: float = None             # FLOP/J upper bound on the energy efficiency (D-055); None = OFF (the committed behaviour); PAPER_ETA_CAP is the paper's value


def initial_compute_stock(p: GateParams) -> float:
    C0 = p.C_T0 + p.runtime_compute_init
    return C0 / (1.0 - C0 / p.C_L)


def eta_0(gp: GateParams, dp: DCParams) -> float:
    """FLOP/J: the value that makes E_dc(2025) equal the calibration point."""
    return initial_compute_stock(gp) * dp.pue / (dp.calibration_twh_2025 * J_PER_TWH)


def e_dc_twh(compute_stock: float, hardware: float, gp: GateParams, dp: DCParams) -> float:
    eta = eta_0(gp, dp) * hardware / gp.H0
    if dp.eta_cap is not None:
        if not (dp.eta_cap > 0.0):                                        # also catches NaN
            raise ValueError(f"eta_cap must be positive, got {dp.eta_cap}")
        eta = min(eta, dp.eta_cap)
    return compute_stock / eta * dp.pue / J_PER_TWH


def supply_series(scenario: str = "TLTL") -> ReplaySector:
    d = pd.read_csv(SUPPLY_CSV)
    d = d[d["scenario"] == scenario]
    return ReplaySector("earth4all_supply", d["year"].to_numpy(), {"supply": d["EP_TWh"].to_numpy()}, {"supply": "TWh/year"})


class DataCentre(Sector):
    name = "s4_datacentre"
    inputs = {"compute_stock": "FLOP/year", "hardware": "FLOP/year/USD", "supply": "TWh/year"}
    outputs = {"e_dc_demand": "TWh/year", "e_dc": "TWh/year", "supply_ratio": "1", "dc_available": "TWh/year", "industry_ratio": "1"}
    validation_status = ("Calibrated to 485 TWh in 2025 (a calibration point, not a validation); 415 TWh (2024) a reference; no independent "
                         "test of modelled data-centre electricity against estimates exists before 2025; the IEA 2030 figure (950 TWh) is a "
                         "report-only comparison. Values after about 2027 inherit S3's unvalidated output (D-029). " + BOUNDARY + ".")

    def __init__(self, gp: GateParams = GateParams(), dp: DCParams = DCParams()):
        self.gp, self.dp = gp, dp
        self._out: Dict[str, float] = {}

    def reset(self, t0: float, t1: float, dt: float) -> None:
        if abs(t0 - 2025.0) > 1e-9:
            raise ValueError("the data-centre module starts in 2025 (D-020)")
        self._out = {"e_dc_demand": self.dp.calibration_twh_2025, "e_dc": self.dp.calibration_twh_2025, "supply_ratio": 1.0, "dc_available": float("nan"),
                     "industry_ratio": 1.0}
        self._supply_ref = None

    def current_outputs(self) -> Dict[str, float]:
        return dict(self._out)

    def advance(self, t: float, h: float, ctx: Context) -> None:
        e = e_dc_twh(ctx.input("compute_stock", t), ctx.input("hardware", t), self.gp, self.dp)
        avail = self.dp.dc_share_cap * ctx.input("supply", t) * self.dp.supply_scale
        ratio = 1.0 if (not math.isfinite(avail) or e <= 0.0) else min(1.0, avail / e)
        if self._supply_ref is None:
            self._supply_ref = ctx.input("supply", t)                    # unscaled recorded supply at the first step (2025)
        self._out = {"e_dc_demand": e, "e_dc": e * ratio, "supply_ratio": ratio, "dc_available": avail,
                     "industry_ratio": self._industry_ratio(t, e * ratio, ctx)}

    def _industry_ratio(self, t: float, e_used: float, ctx: Context) -> float:
        """D-059: electricity left for everything but data centres, relative to its 2025 level, clipped to [0, 1] (World3 industrial-output multiplier)."""
        total = ctx.input("supply", t) * self.dp.supply_scale
        if not math.isfinite(total):
            return 1.0
        base = self._supply_ref - self.dp.calibration_twh_2025
        return min(1.0, max(0.0, (total - e_used) / base))
