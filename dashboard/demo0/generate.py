"""Demo 0 generator (track A, plan section 10): runs the PRECOMPUTED scenario grid and writes ONE self-contained static page,
dashboard/demo0/index.html (inline CSS and JS, no network, data embedded as JSON). Local file; NOT published (A2.7 is the editor's).

Usage (after record_climate.py has produced the 841-member recording):
    PYTHONPATH=. python dashboard/demo0/generate.py <climate841.npz> [out.html]

Grid (documented, small): AI-race setting {low, central, race} x damage option {low, central, high} = 9 runs, plus two electricity-supply
cases (0.5 x and unlimited) for the central/central scenario to show the B1 sign. Climate is recorded ONCE with all 841 members (exact:
emissions are prescribed, so no lever changes them) and replayed in every run.
  low     initial_ai_share = 0.5 x fitted, decay_speed 1.0
  central R3 defaults (the fitted curves)
  race    initial_ai_share = 1.5 x fitted, decay_speed 0.5 (AI share falls more slowly as automation proceeds)
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

from f3.data import fair_inputs as fi
from f3.sectors import damages
from f3.sectors.s3_ai import S3AI
from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
from f3.sectors.s4_datacentre import IEA_2024_TWH, IEA_2025_TWH, IEA_2030_TWH, DataCentre, DCParams
from f3.sectors.s6_climate import S6Climate
from f3.sectors.slice_m2 import SliceConfig, climate_replay, run_slice

REPO = Path(__file__).resolve().parents[2]
F0 = R3Rule()._fitted_initial
SETTINGS = {
    "low": R3Levers(initial_ai_share=0.5 * F0),
    "central": R3Levers(),
    "race": R3Levers(initial_ai_share=1.5 * F0, decay_speed=0.5),
}
SETTING_TEXT = {"low": "initial AI share 0.5 x fitted", "central": "R3 fitted defaults", "race": "initial AI share 1.5 x fitted, decay speed 0.5"}
DAMAGES = ("low", "central", "high")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def series(res, years_idx, s, n):
    return [float(x) for x in res.series[(s, n)][years_idx]]


def run_all(rec) -> dict:
    out = {"years": [int(y) for y in rec["years"]], "runs": {}}
    climate = lambda: climate_replay(rec)
    cases = [(f"{s}|{d}|1", SliceConfig(levers=SETTINGS[s], damage=d)) for s in SETTINGS for d in DAMAGES]
    cases += [("central|central|0.5", SliceConfig(damage="central", dc=DCParams(supply_scale=0.5))),
              ("central|central|inf", SliceConfig(damage="central", dc=DCParams(supply_scale=math.inf)))]
    for key, cfg in cases:
        res = run_slice(cfg, climate())
        idx = [i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9]
        out["runs"][key] = {
            "gwp": series(res, idx, "s3_ai", "gwp"), "gwp_gross": series(res, idx, "s3_ai", "gwp_gross"),
            "compute_stock": series(res, idx, "s3_ai", "compute_stock"), "usable_compute": series(res, idx, "s3_ai", "usable_compute"),
            "effective_compute": series(res, idx, "s3_ai", "effective_compute"),
            "frac_automated": series(res, idx, "s3_ai", "frac_automated"), "damage_fraction": series(res, idx, "s3_ai", "damage_fraction"),
            "e_dc_demand": series(res, idx, "s4_datacentre", "e_dc_demand"), "e_dc": series(res, idx, "s4_datacentre", "e_dc"),
            "supply_ratio": series(res, idx, "s4_datacentre", "supply_ratio"), "dc_available": series(res, idx, "s4_datacentre", "dc_available"),
        }
    out["climate"] = {n: [float(x) for x in rec[n]] for n in ("warming", "warming_p05", "warming_p95", "co2_concentration")}
    return out


def provenance(rec_path: Path) -> dict:
    try:
        commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:
        commit = "unknown"
    sup = REPO / "f3" / "data" / "earth4all_electricity_supply.csv"
    return {
        "git_commit_of_generator": commit,
        "fair_files_sha256": fi.FAIR_FILES, "fair_commit": fi.FAIR_COMMIT,
        "gcb_extract_sha256": sha(REPO / "f3" / "data" / "gcb2025_co2_2015_2024.csv"),
        "earth4all_supply_sha256": sha(sup), "earth4all_commit": "16f37d013a2f68135f03e7815bf861dbf47311f2",
        "r3_curves_sha256": sha(REPO / "f3" / "sectors" / "r3_curves.json"),
        "climate_recording_sha256": sha(rec_path), "climate_members": 841,
        "iea_key_questions_pdf_sha256": "a3a47f07b35420e74b243878f631192b04788110db3c75275feb0fbdee7f4858",
        "hadcrut5": "HadCRUT.5.2.0.0 annual series, pinned through 2024: " + fi.HADCRUT_HASH_THROUGH_2024,
    }


def main() -> None:
    rec_path = Path(sys.argv[1])
    z = np.load(rec_path)
    rec = {k: z[k] for k in z.files}
    if len(rec["years"]) != 76 or int(rec["years"][0]) != 2025:
        raise SystemExit("climate recording must cover 2025..2100")
    data = run_all(rec)
    data["meta"] = {
        "settings": SETTING_TEXT, "damage_coeff_pct_per_K2": {k: v * 100 for k, v in damages.OPTIONS.items() if k != "off"},
        "damage_sources": damages.SOURCES, "iea": {"2024": IEA_2024_TWH, "2025": IEA_2025_TWH, "2030": IEA_2030_TWH},
        "s3_status": S3AI.validation_status, "s6_status": S6Climate.validation_status, "dc_status": DataCentre.validation_status,
        "provenance": provenance(rec_path),
    }
    tpl = (Path(__file__).with_name("template.html")).read_text(encoding="utf-8")
    html = tpl.replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).with_name("index.html")
    out.write_text(html, encoding="utf-8", newline="\n")
    print("wrote", out, len(html), "bytes")


if __name__ == "__main__":
    main()
