"""EXPLORATORY PROTOTYPE for docs/electricity-module-proposal.md (D-066, Proposed). NOT a model component: nothing imports it.

Data-centre electricity limited by a powered-capacity stock that can only grow at a maximum rate per year (and by an outer
share of total supply), with an optional response of the compute investment to the power shortfall. Prints figures only.

Usage:  python audit/t0/dc_build_rate_prototype.py
"""
import sys, warnings, numpy as np
warnings.filterwarnings("ignore")
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from f3.core.model import Coupling, Model
from f3.sectors.s3_ai import GateParams, S3AI
from f3.sectors.s3_rule_r3 import R3Rule
from f3.sectors.s4_datacentre import DataCentre, DCParams, supply_series, e_dc_twh

class PoweredDC(DataCentre):
    def __init__(self, gp, dp, g_max, outer_share):
        super().__init__(gp, dp); self.g_max, self.outer = g_max, outer_share
    def reset(self, t0, t1, dt):
        super().reset(t0, t1, dt); self.P = self.dp.calibration_twh_2025
    def advance(self, t, h, ctx):
        e = e_dc_twh(ctx.input("compute_stock", t), ctx.input("hardware", t), self.gp, self.dp)
        if e > self.P:                                              # build only when wanted, at most g_max a year
            self.P = min(e, self.P * (1.0 + self.g_max) ** h)
        avail = min(self.P, self.outer * ctx.input("supply", t))
        ratio = min(1.0, avail / e) if e > 0 else 1.0
        if self._supply_ref is None: self._supply_ref = ctx.input("supply", t)
        self._out = {"e_dc_demand": e, "e_dc": e * ratio, "supply_ratio": ratio, "dc_available": avail, "industry_ratio": self._industry_ratio(t, e * ratio, ctx)}

class PowerAwareR3(R3Rule):
    dc = None
    def shares(self, f, u):
        q = super().shares(f, u)
        r = self.dc._out.get("supply_ratio", 1.0) if self.dc is not None and self.dc._out else 1.0
        moved = q["q_compute"] * (1.0 - r)                          # do not buy compute that cannot be powered
        q["q_compute"] -= moved; q["q_consumption"] += moved
        return q

def run(g_max, aware, outer=0.25):
    gp, dp = GateParams(), DCParams()
    rule = PowerAwareR3() if aware else R3Rule()
    s3 = S3AI(gp, rule=rule, electricity_limited=True); dc = PoweredDC(gp, dp, g_max, outer)
    if aware: rule.dc = dc
    res = Model([s3, dc, supply_series("TLTL")],
                [Coupling("earth4all_supply","supply","s4_datacentre","supply"), Coupling("s3_ai","compute_stock","s4_datacentre","compute_stock"),
                 Coupling("s3_ai","hardware","s4_datacentre","hardware"), Coupling("s4_datacentre","supply_ratio","s3_ai","supply_ratio")],
                t0=2025.0, t1=2100.0, dt=0.25).run()
    t = res.time; h = s3.series(); yrs = 2025 + np.arange(len(h["gwp"]))
    dcv = lambda n, y: float(res.series[("s4_datacentre", n)][int(np.where(np.isclose(t, y + 1.0))[0][0])])
    s3v = lambda n, y: float(h[n][int(np.where(yrs == y)[0][0])])
    sup = lambda y: float(res.series[("earth4all_supply", "supply")][int(np.where(np.isclose(t, y + 1.0))[0][0])])
    f = h["frac_automated"]; full = int(yrs[np.where(f >= 0.999)[0][0]]) if (f >= 0.999).any() else None
    g = h["gwp"]; gr = g[1:] / g[:-1] - 1
    return {"used": [dcv("e_dc", y) for y in (2026, 2030, 2035, 2040, 2060, 2099)], "share": [dcv("e_dc", y) / sup(y) for y in (2030, 2040, 2060, 2099)],
            "overhang2040": dcv("e_dc_demand", 2040) / dcv("e_dc", 2040), "gwp": [s3v("gwp", y) / 1e12 for y in (2030, 2040, 2060, 2099)],
            "full": full, "maxg": float(gr.max()), "maxg_year": int(yrs[1 + int(gr.argmax())])}


for g_max in (0.15, 0.30, 0.50):
    for aware in (False, True):
        r = run(g_max, aware)
        print(f"\ng_max {g_max:.0%} aware={aware}: DC use TWh 2026/30/35/40/60/99 " + " ".join(f"{v:,.0f}" for v in r["used"]))
        print("   share of supply 2030/40/60/99 " + " ".join(f"{v:.1%}" for v in r["share"]) + f" | demand/use 2040 {r['overhang2040']:,.1f}x")
        print("   gwp trn 2030/40/60/99 " + " ".join(f"{v:,.0f}" for v in r["gwp"]) + f" | full automation {r['full']} | max growth {r['maxg']:.0%} in {r['maxg_year']}")
