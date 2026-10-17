"""The coupled M2 slice (track A): S3 (GATE equations, R3 investment rule) + data-centre electricity module + S6 climate, S1 exogenous.

Wiring (all by name, units checked by ``f3.core.model``; explicit coupling at step boundaries, step 0.25 year, t = Y is 1 January; from 2025):

    earth4all_supply.supply  [TWh/year]      -> s4_datacentre.supply        recorded Earth4All.jl electricity production (ene.EP)
    s3_ai.compute_stock      [FLOP/year]     -> s4_datacentre.compute_stock  R1: more investment, more compute, more demand
    s3_ai.hardware           [FLOP/year/USD] -> s4_datacentre.hardware
    s4_datacentre.supply_ratio [1]           -> s3_ai.supply_ratio           B1: scarce electricity scales usable compute down
    s6_climate.warming       [K]             -> s3_ai.warming                B2: damage fraction c*T^2 lowers output (D-007)

S1 (population) is exogenous: S3 carries GATE's own labour path, so no S1 sector is in this slice (the plan: "S1 population exogenous").
Emissions are prescribed (D-021): no F3 sector feeds S6, so the climate is the same for every lever and can be computed once and replayed
**exactly** (``ClimateReplay``): S3 reads ``warming`` only at the start of each year, where the replayed value equals the sector's published
value. Coupling off = ``electricity=False`` (no supply_ratio input) and ``damage="off"`` removes B2; both leave S3 bit-identical to standalone.

Labels: ``S3AI.validation_status`` (D-029), ``S6Climate.validation_status`` (D-030, D-021), ``DataCentre.validation_status``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from f3.core.model import Coupling, Model
from f3.core.replay import ReplaySector
from f3.sectors.s3_ai import GateParams, S3AI
from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
from f3.sectors.s4_datacentre import DataCentre, DCParams, supply_series
from f3.sectors.s6_climate import ClimateSetup, S6Climate

T0, T1 = 2025.0, 2100.0
CLIMATE_OUTPUTS = {"warming": "K", "warming_p05": "K", "warming_p95": "K", "co2_concentration": "ppm"}


class ClimateReplay(ReplaySector):
    """A recorded S6Climate run (same name, same outputs). Exact for this slice because S6 has no inputs (prescribed emissions)."""

    validation_status = S6Climate.validation_status

    def __init__(self, years: np.ndarray, series: Dict[str, np.ndarray]):
        super().__init__("s6_climate", years, series, CLIMATE_OUTPUTS)


def record_climate(setup: ClimateSetup = ClimateSetup(), t0: float = T0, t1: float = T1, dt: float = 0.25) -> Dict[str, np.ndarray]:
    """One S6Climate loop run (D-021 option a: exact FaIR re-run each year); returns values at each 1 January from t0 to t1."""
    res = Model([S6Climate(setup)], [], t0=t0, t1=t1, dt=dt).run()
    keep = [i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9]
    out = {"years": res.time[keep]}
    for n in CLIMATE_OUTPUTS:
        out[n] = res.series[("s6_climate", n)][keep]
    return out


def climate_replay(rec: Dict[str, np.ndarray]) -> ClimateReplay:
    return ClimateReplay(rec["years"], {n: rec[n] for n in CLIMATE_OUTPUTS})


@dataclass(frozen=True)
class SliceConfig:
    levers: R3Levers = R3Levers()
    damage: str = "central"                 # "low" | "central" | "high" | "off"
    electricity: bool = True                # False: S3-S4 coupling off
    dc: DCParams = DCParams()
    supply_scenario: str = "TLTL"
    gate: GateParams = GateParams()


def build(cfg: SliceConfig, climate: Optional[ReplaySector] = None, climate_setup: ClimateSetup = ClimateSetup(n_members=20),
          dt: float = 0.25):
    """Return the Model. ``climate`` is a recorded run (``climate_replay``) or None for a live S6Climate with ``climate_setup``."""
    damage_on = cfg.damage != "off"
    s3 = S3AI(cfg.gate, rule=R3Rule(cfg.levers), electricity_limited=cfg.electricity, damage_option=cfg.damage if damage_on else None)
    sectors = [s3]
    couplings = []
    if cfg.electricity:
        dc = DataCentre(cfg.gate, cfg.dc)
        sectors += [dc, supply_series(cfg.supply_scenario)]
        couplings += [Coupling("earth4all_supply", "supply", "s4_datacentre", "supply"),
                      Coupling("s3_ai", "compute_stock", "s4_datacentre", "compute_stock"),
                      Coupling("s3_ai", "hardware", "s4_datacentre", "hardware"),
                      Coupling("s4_datacentre", "supply_ratio", "s3_ai", "supply_ratio")]
    s6 = climate if climate is not None else S6Climate(climate_setup)
    sectors.append(s6)
    if damage_on:
        couplings.append(Coupling("s6_climate", "warming", "s3_ai", "warming"))
    return Model(sectors, couplings, t0=T0, t1=T1, dt=dt)


def run_slice(cfg: SliceConfig, climate: Optional[ReplaySector] = None, climate_setup: ClimateSetup = ClimateSetup(n_members=20), dt: float = 0.25):
    return build(cfg, climate, climate_setup, dt).run()
