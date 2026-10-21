"""S3 diagnostic (D-053, Provisional): where do the implausible S3 / data-centre outputs come from? DIAGNOSTIC ONLY: no sector, test or label is changed.

    set PYTHONUTF8=1
    set F3_GATE_BUNDLE=<path to gate.js>   (read at test time only, D-026; nothing from the bundle is stored except comparison figures)
    uv run --group dev python audit/t0/s3_diagnostic.py <climate841.npz>

Method and the PRE-REGISTERED plausibility criteria: docs/s3-diagnostic.md section 2 (committed before this script was run).
Stages, each for the three shipped settings (B0 default, B1 conservative, B2 aggressive; D-005 amendment B):
  A0  S3 on GATE's own investment path with Epoch's stored composite T supplied   (S3's laws of motion alone)
  A1  S3 on GATE's own investment path, S3's own composite                         (the A1.3 configuration)
  R0  S3 under R3 with the stored composite T supplied                             (R3's own error)
  R1  S3 under R3, own composite                                                   (the configuration F3 uses)
  each of A0..R1 also through the data-centre module (post hoc on the series: no supply limit, no loop)
  STORED  the stored GATE run itself through the same data-centre module           (is the electricity result a property of GATE's own path?)
  SLICE   the coupled M2 slice (R3 + data-centre module + damage central, recorded FaIR replay), default setting only
Writes audit/data/s3-diagnostic.json: S3's own values and log10 ratios against the stored run at the decade years, plus the stored run's order of
magnitude rounded to 0.1 in log10 (a comparison figure, not a series).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from f3.core.model import Model  # noqa: E402
from f3.sectors.s3_ai import S3AI, GateParams, usable_compute  # noqa: E402
from f3.sectors.s3_rule_r3 import R3Rule  # noqa: E402
from f3.sectors.s4_datacentre import DCParams, e_dc_twh, supply_series  # noqa: E402
from f3.sectors.slice_m2 import ClimateReplay, SliceConfig, run_slice  # noqa: E402
from tests import gate_reference as gr  # noqa: E402
from tests.s3_checks import N_PERIODS, SETTINGS_B, run_s3  # noqa: E402

OUT = REPO / "audit" / "data" / "s3-diagnostic.json"
YEARS = [2025, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]          # index k = year - 2025 = end of that year (stored-index convention)
IDX = [y - 2025 for y in YEARS]
DP = DCParams()
# absolute bounds for electricity (TWh/year); sources in docs/s3-diagnostic.md section 2
J_PER_TWH = 3.6e15
BOUNDS = {"above_5pct_of_supply_cap": None, "above_total_supply": None, "above_todays_world_energy_5e20J": 5e20 / J_PER_TWH, "above_paper_1pct_dissipation_5e22J": 5e22 / J_PER_TWH}


def supply_twh() -> np.ndarray:
    s = supply_series("TLTL")
    return np.array([s.output_at("supply", 2025.0 + k + 1) for k in range(N_PERIODS)])


def run_with(params: GateParams, shares=None, rule=None, stored_T=None) -> dict:
    """S3 for 76 periods. ``shares`` (GATE's path, replayed) or ``rule`` (R3); ``stored_T`` is the DIAGNOSTIC composite input."""
    if rule is not None:
        s3 = S3AI(params, rule=rule, stored_T=stored_T)
        Model([s3], [], 2025.0, 2025.0 + N_PERIODS, 0.25).run()
        return s3.series()
    if stored_T is None:
        return run_s3(params, shares)
    from f3.core.model import Coupling
    from f3.core.replay import ReplaySector
    from f3.sectors.s3_ai import SHARE_NAMES
    t = 2025.0 + np.arange(len(next(iter(shares.values()))))
    rep = ReplaySector("investment_path", t, dict(shares), {k: "1" for k in shares})
    s3 = S3AI(params, stored_T=stored_T)
    Model([rep, s3], [Coupling("investment_path", k, "s3_ai", k) for k in SHARE_NAMES], 2025.0, 2025.0 + N_PERIODS, 0.25).run()
    return s3.series()


def quantities(params: GateParams, q: np.ndarray, hw: np.ndarray, sw: np.ndarray, gwp: np.ndarray) -> dict:
    eff = np.array([usable_compute(x, params.C_L) for x in q]) * sw
    e = np.array([e_dc_twh(x, h, params, DP) for x, h in zip(q, hw)])
    return {"compute_stock": q, "effective_compute": eff, "gwp": gwp, "e_dc_demand_twh": e}


def of_s3(params, s):
    return quantities(params, s["compute_stock"][:N_PERIODS], s["hardware"][:N_PERIODS], s["software"][:N_PERIODS], s["gwp"][:N_PERIODS])


def of_stored(params, run):
    return quantities(params, gr.field(run, "compute"), gr.field(run, "hardware"), gr.field(run, "software"), gr.field(run, "gwp"))


def l10(x):
    return float(np.log10(x)) if x > 0 and math.isfinite(x) else float("nan")


def first_year(mask: np.ndarray):
    i = np.where(mask)[0]
    return int(2025 + i[0]) if len(i) else None


def compare(mine: dict, ref: dict, sup: np.ndarray) -> dict:
    out = {}
    for name in mine:
        m, r = mine[name], ref[name]
        with np.errstate(divide="ignore", invalid="ignore"):
            lr = np.log10(m / r)
        out[name] = {"values": {str(y): float(m[k]) for y, k in zip(YEARS, IDX)},
                     "log10_ratio_vs_stored": {str(y): (None if not np.isfinite(lr[k]) else round(float(lr[k]), 3)) for y, k in zip(YEARS, IDX)},
                     "stored_log10_magnitude": {str(y): round(l10(r[k]), 1) for y, k in zip(YEARS, IDX)},
                     "first_year_factor_2": first_year(np.abs(lr) >= math.log10(2.0)), "first_year_factor_10": first_year(np.abs(lr) >= 1.0),
                     "max_abs_log10_ratio": round(float(np.nanmax(np.abs(lr))), 3), "max_abs_log10_ratio_year": int(2025 + np.nanargmax(np.abs(lr)))}
    return out


def electricity_bounds(e: np.ndarray, sup: np.ndarray) -> dict:
    return {"first_year_above_5pct_of_supply_cap": first_year(e > DP.dc_share_cap * sup), "first_year_above_total_supply": first_year(e > sup),
            "first_year_above_todays_world_energy_5e20J": first_year(e > BOUNDS["above_todays_world_energy_5e20J"]),
            "first_year_above_paper_1pct_dissipation_5e22J": first_year(e > BOUNDS["above_paper_1pct_dissipation_5e22J"]),
            "e_dc_twh_at_decades": {str(y): float(e[k]) for y, k in zip(YEARS, IDX)}}


def slice_stage(rec_path: Path) -> dict:
    z = np.load(rec_path)
    rep = ClimateReplay(z["years"], {n: z[n] for n in ("warming", "warming_p05", "warming_p95", "co2_concentration")})
    res = run_slice(SliceConfig(), rep, t1=2101.0)
    t = res.time
    def at(sec, name, k):
        i = int(np.argmin(np.abs(t - (2025.0 + k + 1))))
        return float(res.series[(sec, name)][i])
    return {n: {str(y): at(sec, n, k) for y, k in zip(YEARS, IDX)} for sec, n in (("s3_ai", "compute_stock"), ("s3_ai", "usable_compute"), ("s3_ai", "gwp"),
                                                                               ("s4_datacentre", "e_dc_demand"), ("s4_datacentre", "supply_ratio"))} | {
        "note": "from the loop: the data-centre module reads the start-of-step values, so its demand lags S3 by one period; the 2100 point is the end of 2100 (t = 2101, replay held at 2100)"}


def main() -> None:
    rec_path = Path(sys.argv[1])
    runs = gr.load_runs()
    sup = supply_twh()
    report = {"years": YEARS, "bounds_twh": {k: v for k, v in BOUNDS.items() if v}, "supply_twh_at_decades": {str(y): float(sup[k]) for y, k in zip(YEARS, IDX)},
              "settings": {}, "bundle_sha256": gr.check_hash()}
    for name, (ridx, params) in SETTINGS_B.items():
        run = runs[ridx]
        shares = gr.investment_shares(run, 80)
        T = gr.field(run, "cognitive_ces_term", 80)
        stored = of_stored(params, run)
        stages = {
            "A0_gate_path_stored_T": run_with(params, shares=shares, stored_T=T),
            "A1_gate_path_own_T": run_with(params, shares=shares),
            "R0_R3_stored_T": run_with(params, rule=R3Rule(), stored_T=T),
            "R1_R3_own_T": run_with(params, rule=R3Rule()),
        }
        rec = {"STORED_through_module": {"e_dc_twh": electricity_bounds(stored["e_dc_demand_twh"], sup), "stored_log10_magnitude": {
            n: {str(y): round(l10(stored[n][k]), 1) for y, k in zip(YEARS, IDX)} for n in stored}}}
        for sname, s in stages.items():
            mine = of_s3(params, s)
            rec[sname] = {"vs_stored": compare(mine, stored, sup), "electricity_bounds": electricity_bounds(mine["e_dc_demand_twh"], sup),
                          "max_Q_over_CL": float(np.max(s["compute_stock"][:N_PERIODS]) / params.C_L)}
        report["settings"][name] = rec
        print("done", name, flush=True)
    report["SLICE_coupled_default"] = slice_stage(rec_path)
    OUT.write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
