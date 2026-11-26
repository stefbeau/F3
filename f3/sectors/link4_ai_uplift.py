"""Link 4 of the connections map: S3 output to World3 industrial output, bounded by a growth cap (D-069; readings in docs/link3-link4-tests.md).
OFF unless a caller passes the uplift to World3Group(ai_uplift=...).

S3's uplift factor (output with AI investment / output without) is unbounded even with the electricity limits of steps E1 and E2, so it is not
applied as measured. ``bounded_uplift`` lets it grow by at most ``cap`` a year. THE CAP IS A SCENARIO ASSUMPTION, NOT DATA, and has no default.
Where the cap binds, the result is the cap. One-way: World3 does not feed back on S3. S3's level is unvalidated under F3's own investment rule.
"""
from __future__ import annotations

import warnings
from functools import lru_cache
from typing import Callable, Dict

import numpy as np

NOTICE = ("Link 4 is one-way and off by default: World3 industrial output is multiplied by S3's uplift factor, limited to a growth of at most the chosen cap "
          "a year. The cap is a scenario assumption, not data; where it binds, the result is the cap. S3's level is unvalidated under F3's own investment "
          "rule and the two economies are not reconciled.")


@lru_cache(maxsize=None)
def _gwp(ai_off: bool, g_max: float, outer_share: float, power_aware: bool) -> tuple:
    from f3.core.model import Coupling, Model
    from f3.sectors.s3_ai import GateParams, S3AI
    from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
    from f3.sectors.s4_datacentre import DataCentre, DCParams, supply_series
    gp = GateParams()
    lv = R3Levers(initial_ai_share=0.0, power_aware=power_aware) if ai_off else R3Levers(power_aware=power_aware)
    s3, dc = S3AI(gp, rule=R3Rule(lv), electricity_limited=True), DataCentre(gp, DCParams(g_max=g_max, outer_share=outer_share))
    cp = [Coupling("earth4all_supply", "supply", "s4_datacentre", "supply"), Coupling("s3_ai", "compute_stock", "s4_datacentre", "compute_stock"),
          Coupling("s3_ai", "hardware", "s4_datacentre", "hardware"), Coupling("s4_datacentre", "supply_ratio", "s3_ai", "supply_ratio")]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        Model([s3, dc, supply_series("TLTL")], cp, t0=2025.0, t1=2100.0, dt=0.25).run()
    return tuple(float(v) for v in np.asarray(s3.series()["gwp"], dtype=float))


def s3_uplift(ai_off: bool = False, g_max: float = 0.30, outer_share: float = 0.25, power_aware: bool = True) -> Dict[int, float]:
    """S3 output with AI investment over S3 output without, by year 2025..2099, normalised to 1 in 2025 (R3 central, steps E1 and E2 on)."""
    on, off = _gwp(ai_off, g_max, outer_share, power_aware), _gwp(True, g_max, outer_share, power_aware)
    u = [a / b for a, b in zip(on, off)]
    return {2025 + i: v / u[0] for i, v in enumerate(u)}


def bounded_uplift(u: Dict[int, float], cap: float) -> Dict[int, float]:
    """U_b(2025) = 1; U_b(t) = min(U(t), U_b(t-1) x (1 + cap)). ``cap`` is required: it is an assumption the caller must state."""
    if not (cap >= 0.0):
        raise ValueError("cap must be zero or positive")
    years = sorted(u)
    out = {years[0]: 1.0}
    for y in years[1:]:
        out[y] = min(u[y], out[y - 1] * (1.0 + cap))
    return out


def binding_years(u: Dict[int, float], cap: float) -> list:
    ub = bounded_uplift(u, cap)
    return [y for y in sorted(u)[1:] if u[y] > ub[y] * (1 + 1e-12)]


def as_callable(ub: Dict[int, float]) -> Callable[[float], float]:
    """The factor for the calendar year containing t (held through the year); the last year's value after it."""
    last = max(ub)
    return lambda t: ub[min(int(np.floor(t + 1e-9)), last)]
