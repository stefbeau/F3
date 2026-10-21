"""M6 minimal integration (D-051, docs/m6-minimal-plan.md, docs/m6-tests.md): one loop, step 0.25 year, 1900-2100.

    world3 (the D-031 group, 1900)  <- warming (recorded replay) ONLY when the climate-damage coupling is on (``world3_damage``; default off)
    s6_climate (2025)               recorded replay (exact, emissions prescribed, D-021 A) or a live S6Climate
    s3_ai (R3) + s4_datacentre + earth4all_supply (2025)   the M2 slice wiring, held at initial values before 2025 by ``DelayedStart`` (D-020)
    s7_feed (adapter) -> s7_social (2025, OUTPUT ONLY: nothing reads it); s7_given: unemployment = 0 and redistribution = 0 (illustrative)

S3's economy and World3's are two models of the same world in one run; they are NOT reconciled (plan 14.2 item 2).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np

from f3.core.model import Coupling, Model, Results
from f3.core.replay import ReplaySector
from f3.core.sector import Context, Sector
from f3.sectors.s3_ai import GateParams, S3AI
from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
from f3.sectors.s4_datacentre import DataCentre, DCParams, supply_series
from f3.sectors.s6_climate import ClimateSetup, S6Climate
from f3.sectors.s7_social import S7Social
from f3.sectors.world3 import build_world3, _initial_inputs, STATE_COLUMNS
from f3.sectors.world3_group import World3Group

START = 2025.0
T0, T1 = 1900.0, 2100.0

M6_LABELS = (
    "M6 minimal integration. Two economies run side by side and are not reconciled: World3's output and S3's output describe the same world "
    "differently (plan 14.2). S3 is unvalidated against GATE after about 2027 (D-029) and the data-centre module inherits that. S7 is output-only, "
    "all its parameters are illustrative, tension is not validated against history (D-008), and there is no health or yield effect of warming (D-049). "
    "The climate-damage coupling to World3 is a level-of-output effect (D-007, D-051), default off. Results are conditional scenarios, not forecasts."
)


class DelayedStart(Sector):
    """Before ``start`` the wrapped sector publishes its initial outputs and does not advance; from ``start`` it is the wrapped sector."""

    def __init__(self, inner: Sector, start: float = START):
        self.inner, self.start = inner, float(start)
        self.name, self.inputs, self.outputs = inner.name, dict(inner.inputs), dict(inner.outputs)
        self.period, self.exact_in_time = inner.period, False
        self.validation_status = getattr(inner, "validation_status", "")

    def reset(self, t0: float, t1: float, dt: float) -> None:
        self.inner.reset(self.start, t1, dt)

    def current_outputs(self) -> Dict[str, float]:
        return self.inner.current_outputs()

    def advance(self, t: float, h: float, ctx: Context) -> None:
        if t >= self.start - 1e-9:
            self.inner.advance(t, h, ctx)


class S7Feed(Sector):
    """Adapter (labelled): S3 labor_share and gwp/labor -> S7 labor_share and gdp_per_capita_growth. Before S3's first annual period the labour
    share is the no-automation value 1 - alpha. Growth is the relative change of gwp/labor between consecutive annual values (S3 is annual)."""

    name = "s7_feed"
    inputs = {"labor_share": "1", "gwp": "USD/year", "labor": "persons"}
    outputs = {"labor_share": "1", "gdp_per_capita_growth": "1/year"}

    def __init__(self, gate: GateParams = GateParams()):
        self._ls0 = 1.0 - gate.alpha
        self._reset()

    def _reset(self):
        self._ls, self._g, self._prev, self._cur = self._ls0, 0.0, None, None

    def reset(self, t0: float, t1: float, dt: float) -> None:
        self._reset()

    def current_outputs(self) -> Dict[str, float]:
        return {"labor_share": self._ls, "gdp_per_capita_growth": self._g}

    def advance(self, t: float, h: float, ctx: Context) -> None:
        ls = ctx.input("labor_share", t)
        self._ls = self._ls0 if not math.isfinite(ls) else ls
        if t >= START + 1.0 - 1e-9 and abs(t - round(t)) < 1e-9:           # a new annual value of S3 exists
            gpc = ctx.input("gwp", t) / ctx.input("labor", t)
            self._prev, self._cur = self._cur, gpc
            self._g = 0.0 if self._prev is None else self._cur / self._prev - 1.0
        elif self._cur is None:
            self._cur = ctx.input("gwp", t) / ctx.input("labor", t)        # the 2025 value, the first reference


@dataclass(frozen=True)
class M6Config:
    parameter_set: str = "2004"
    world3_damage: Optional[str] = None          # None (off) | low | central | high
    s3_damage: str = "off"                       # off | low | central | high
    electricity: bool = False
    levers: R3Levers = field(default_factory=R3Levers)
    dc: DCParams = field(default_factory=DCParams)
    gate: GateParams = field(default_factory=GateParams)
    supply_scenario: str = "TLTL"
    t1: float = T1


def build_m6(cfg: M6Config, climate: Optional[ReplaySector] = None, climate_setup: ClimateSetup = ClimateSetup(n_members=20)) -> Model:
    sectors0, couplings0 = build_world3(cfg.parameter_set, None)
    init = _initial_inputs(sectors0, T0)
    warming = None
    if cfg.world3_damage is not None:
        if climate is None:
            raise ValueError("the World3 damage coupling needs the recorded climate replay (D-051: no new FaIR run per scenario)")
        warming = lambda t: climate.output_at("warming", t)             # noqa: E731
    group = World3Group(sectors0, couplings0, init, STATE_COLUMNS, damage_option=cfg.world3_damage, warming=warming)

    damage_on = cfg.s3_damage != "off"
    s3 = S3AI(cfg.gate, rule=R3Rule(cfg.levers), electricity_limited=cfg.electricity, damage_option=cfg.s3_damage if damage_on else None)
    s6 = climate if climate is not None else DelayedStart(S6Climate(climate_setup))
    feed, given = S7Feed(cfg.gate), ReplaySector("s7_given", [T0, 2100.0], {"unemployment": [0.0, 0.0], "redistribution": [0.0, 0.0]},
                                               {"unemployment": "1", "redistribution": "1"})
    s7 = DelayedStart(S7Social())
    sectors = [group, DelayedStart(s3), s6, feed, given, s7]
    couplings = [Coupling("s3_ai", "labor_share", "s7_feed", "labor_share"), Coupling("s3_ai", "gwp", "s7_feed", "gwp"),
                 Coupling("s3_ai", "labor", "s7_feed", "labor"),
                 Coupling("s7_feed", "labor_share", "s7_social", "labor_share"),
                 Coupling("s7_feed", "gdp_per_capita_growth", "s7_social", "gdp_per_capita_growth"),
                 Coupling("s7_given", "unemployment", "s7_social", "unemployment"),
                 Coupling("s7_given", "redistribution", "s7_social", "redistribution"),
                 Coupling("s6_climate", "warming", "s7_social", "warming")]
    if cfg.electricity:
        sectors += [DelayedStart(DataCentre(cfg.gate, cfg.dc)), supply_series(cfg.supply_scenario)]
        couplings += [Coupling("earth4all_supply", "supply", "s4_datacentre", "supply"),
                      Coupling("s3_ai", "compute_stock", "s4_datacentre", "compute_stock"),
                      Coupling("s3_ai", "hardware", "s4_datacentre", "hardware"),
                      Coupling("s4_datacentre", "supply_ratio", "s3_ai", "supply_ratio")]
    if damage_on:
        couplings.append(Coupling("s6_climate", "warming", "s3_ai", "warming"))
    return Model(sectors, couplings, t0=T0, t1=cfg.t1, dt=0.25)


def run_m6(cfg: M6Config, climate: Optional[ReplaySector] = None, climate_setup: ClimateSetup = ClimateSetup(n_members=20)) -> Results:
    return build_m6(cfg, climate, climate_setup).run()
