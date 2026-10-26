"""The World3 sector group as ONE Sector of the coupling loop, advanced with internal sub-steps (D-031).

Rule (D-031, written before any re-run): the five World3 sectors (S1 population, agriculture, capital, resources, pollution) are
advanced with sub-steps of ``substep`` = 0.0625 year inside each loop step of 0.25 year (D-003 and D-022 unchanged for coupling
with other sectors). Within the group the coupling is the same explicit start-of-sub-step coupling as in D-022: each sector reads
the others' values at the start of the sub-step, held across it; every sector's own RK4 and equations are unchanged. The group
publishes the 29 states at each loop boundary (``outputs``); it has no inputs from other sectors in M3.

Interface code only. The Sector interface is not changed.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence

from f3.core.sector import Context, Sector

SUBSTEP = 0.0625
DAMAGE_START_YEAR = 2025.0            # the recorded climate replay and the coupling start in 2025 (D-020)
DAMAGE_COUPLING_LABEL = (
    "Climate damage to World3 industrial output (D-051): a level-of-output effect, the D-007 damage function (default central; low, central and "
    "high are Nordhaus 2017, Barrage and Nordhaus 2024 and Howard and Sterner 2017). The default is off. The 'high' option is not the upper end "
    "of the literature: growth-effect estimates are larger and are not represented. No new coefficient. The damage multiplies World3's whole industrial "
    "output flow, which feeds investment, agriculture, resources and population; when it is on, World3 is no longer compared with WorldDynamics.jl. "
    "Warming comes from the recorded FaIR replay (D-021 option A: emissions prescribed); FaIR starts about 0.04 to 0.07 K below observed (D-030)."
)


class World3Group(Sector):
    name = "world3"
    inputs: Mapping[str, str] = {}

    def __init__(self, sectors: Sequence[Sector], couplings, init_inputs: Mapping[str, Mapping[str, float]], state_names: Mapping[str, str],
                 substep: float = SUBSTEP, damage_option: Optional[str] = None, warming=None, _mutate_zero_damage: bool = False,
                 electricity_link: bool = False, _mutate_unit_elec_ratio: bool = False):
        self._sectors: Dict[str, Sector] = {s.name: s for s in sectors}
        self._order: List[str] = [s.name for s in sectors]
        self._substep = float(substep)
        self._init_inputs = init_inputs
        # state name -> sector that holds it; the group publishes all 29 states by name
        self._state_owner: Dict[str, str] = {}
        for s in sectors:
            for n in self._state_names_of(s):
                self._state_owner[n] = s.name
        self.outputs = {n: "state" for n in self._state_owner}
        self.outputs["io"] = "dollars/year"                       # World3 industrial output, published for the M6 tests
        self.outputs["lf"] = "jobs"                               # labour force (p2 + p3) x lfpf, derived from the published states (D-054 item 5)
        # M6 climate-damage coupling (D-051): OFF unless damage_option is given; warming is a callable year -> K (recorded FaIR replay)
        if damage_option is not None:
            from f3.sectors.damages import check_option
            check_option(damage_option)
            if warming is None:
                raise ValueError("damage_option needs a warming source (a callable year -> K from the recorded replay)")
        self._damage_option = damage_option
        self._warming = warming
        # D-059 electricity link: OFF unless electricity_link; the group then reads ``elec_ratio`` (data-centre module, 0..1) from the loop
        self._elec_link = bool(electricity_link)
        self._mutate_unit_elec_ratio = _mutate_unit_elec_ratio    # test hook: the sign test must fail when the ratio is forced to 1
        if self._elec_link:
            self.inputs = {"elec_ratio": "1"}
        self._mutate_zero_damage = _mutate_zero_damage            # test hook: the sign test must fail when the multiplier is forced to 1
        self._wiring: Dict[str, Dict[str, tuple]] = {n: {} for n in self._sectors}
        for c in couplings:
            src, tgt = self._sectors[c.source], self._sectors[c.target]
            if src.outputs[c.source_output] != tgt.inputs[c.target_input]:
                raise ValueError(f"unit mismatch: {c.source}.{c.source_output} -> {c.target}.{c.target_input}")
            self._wiring[c.target][c.target_input] = (c.source, c.source_output)
        for n, s in self._sectors.items():
            missing = [i for i in s.inputs if i not in self._wiring[n]]
            if missing:
                raise ValueError(f"sector {n!r}: inputs not wired inside the group: {missing}")
        self._published: Dict[str, Dict[str, float]] = {}

    @staticmethod
    def _state_names_of(s: Sector):
        from f3.sectors.s1_population import STATE_NAMES as S1
        return S1 if s.name == "s1_population" else s.STATE_NAMES

    def _states_now(self) -> Dict[str, float]:
        out = {}
        for n in self._order:
            s = self._sectors[n]
            for i, name in enumerate(self._state_names_of(s)):
                out[name] = float(s._y[i])
        return out

    # -- Sector interface ---------------------------------------------------------------------------------------------
    def reset(self, t0: float, t1: float, dt: float) -> None:
        k = dt / self._substep
        if abs(k - round(k)) > 1e-9 or round(k) < 1:
            raise ValueError(f"loop step {dt} is not a whole number of sub-steps of {self._substep}")
        self._n_sub = int(round(k))
        h = dt / self._n_sub
        for n, s in self._sectors.items():
            if n != "s1_population":
                s.set_initial_inputs(self._init_inputs[n])
            s.reset(t0, t1, h)
        self._h = h
        self._published = {n: dict(s.current_outputs()) for n, s in self._sectors.items()}
        self._sectors["w3_capital"].damage_mult = 1.0

    def current_outputs(self) -> Dict[str, float]:
        out = self._states_now()
        out["io"] = float(self._published["w3_capital"]["io"])
        out["lf"] = (out["p2"] + out["p3"]) * self._sectors["w3_capital"].params["lfpf"]      # same fraction as the capital sector's Line 80
        return out

    def advance(self, t: float, h: float, ctx: Optional[Context]) -> None:
        if self._damage_option is not None or self._elec_link:
            mult = 1.0
            if self._damage_option is not None:
                mult = self._damage_mult(t)
            if self._elec_link and t >= DAMAGE_START_YEAR - 1e-9 and not self._mutate_unit_elec_ratio:
                mult *= float(ctx.input("elec_ratio", t))
            self._sectors["w3_capital"].damage_mult = mult
        for j in range(self._n_sub):
            tt = t + j * self._h
            snapshot = {n: dict(v) for n, v in self._published.items()}
            pending = {}
            for n in self._order:
                s = self._sectors[n]
                s.advance(tt, self._h, Context(s, self._wiring[n], snapshot, self._sectors))
                pending[n] = dict(s.current_outputs())
            self._published = pending

    def _damage_mult(self, t: float) -> float:
        """Climate-damage multiplier from the warming at the START of the loop step, held across its sub-steps (explicit coupling, D-022); 1 before 2025."""
        from f3.sectors.damages import damage_fraction
        if t >= DAMAGE_START_YEAR - 1e-9 and not self._mutate_zero_damage:
            return 1.0 - damage_fraction(float(self._warming(t)), self._damage_option)
        return 1.0
