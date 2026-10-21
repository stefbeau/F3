"""F3 Explorer v0 generator: writes site/index.html (one self-contained static page, inline CSS/JS/data) and site/data/explorer.json.

Static site (D-009): precomputed scenario grids, no backend. NOT published: publishing is the editor's decision.

    PYTHONPATH=. python site/generate.py <climate841.npz>

Three panels, NOT coupled to each other:
  1. World3 (2004 parameter set, D-015 provisional default), advanced with the D-031 group (0.0625-year sub-steps in the 0.25-year loop):
     a precomputed grid of 3 levers x 3 values = 27 runs, 1900-2100. Levers are World3 parameters chosen as a Provisional decision
     (docs/site-explorer.md): initial non-renewable resources (nri), land yield factor after the 1975 policy year (lyf2) and the
     persistent-pollution generation factor after 1975 (ppgf21). Only the standard run is compared with WorldDynamics.jl (A3.1, A3.2).
  2. Climate: the 841-member FaIR recording (D-021 option a, exact), emissions prescribed.
  3. AI race: the Demo 0 slice grid (S3 under R3 + data-centre module + damage option), reused from dashboard/demo0/generate.py.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from f3.core import Model  # noqa: E402
from f3.sectors.world3 import STATE_COLUMNS, _initial_inputs, build_world3  # noqa: E402
from f3.sectors.world3_group import World3Group  # noqa: E402

PPOL70 = 1.36e8                      # World3 ppol70 (persistent pollution in 1970), ppolx = ppol / ppol70

# Provisional (delegated) choice of levers: docs/site-explorer.md. (parameter, label, values, value labels, index of the standard value)
LEVERS = [
    ("nri", "Non-renewable resources at the start (1900)", [0.5e12, 1.0e12, 2.0e12], ["half (0.5e12)", "standard (1e12)", "double (2e12)"], 1),
    ("lyf2", "Land yield factor after 1975", [1.0, 1.5, 2.0], ["standard (1.0)", "1.5", "2.0"], 0),
    ("ppgf21", "Pollution generation factor after 1975", [1.0, 0.5, 0.25], ["standard (1.0)", "0.5", "0.25"], 0),
]


def load_demo0():
    spec = importlib.util.spec_from_file_location("demo0_generate", REPO / "dashboard" / "demo0" / "generate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_world3(over: dict, parameter_set: str = "2004"):
    sectors, couplings = build_world3(parameter_set)
    for s in sectors:
        if hasattr(s, "params"):
            for k, v in over.items():
                if k in s.params:
                    s.params[k] = v
    init = _initial_inputs(sectors, 1900.0)
    g = World3Group(sectors, couplings, init, STATE_COLUMNS)
    res = Model([g], [], t0=1900.0, t1=2100.0, dt=0.25).run()
    st = {n: res.series[(g.name, n)] for n in STATE_COLUMNS}
    idx = [i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9]            # yearly
    nri = over.get("nri", 1.0e12)
    out = {
        "pop": st["p1"] + st["p2"] + st["p3"] + st["p4"], "ic": st["ic"], "al": st["al"],
        "nrfr": st["nr"] / nri, "ppolx": st["ppol"] / PPOL70,
    }
    return [int(round(res.time[i])) for i in idx], {k: [float(f"{v[i]:.6g}") for i in idx] for k, v in out.items()}


def world3_grid() -> dict:
    years = None
    runs = {}
    for combo in itertools.product(*[range(3) for _ in LEVERS]):
        over = {p: vals[i] for (p, _, vals, _, _), i in zip(LEVERS, combo)}
        years, series = run_world3(over)
        runs["|".join(map(str, combo))] = series
    std = "|".join(str(l[4]) for l in LEVERS)
    return {"years": years, "runs": runs, "standard": std,
            "levers": [{"param": p, "label": lab, "values": vals, "value_labels": vl, "standard_index": si} for p, lab, vals, vl, si in LEVERS],
            "parameter_set": "2004 (World3_03 scenario 1; the provisional default of D-015)",
            "status": {"A3.1": "met: all 14 states of the four sectors within 0.124% of WorldDynamics.jl, both parameter sets",
                       "A3.2": "met after D-031 (0.0625-year sub-steps inside the 0.25-year loop): all 29 states within 2%, worst 1.906% (2004 set)",
                       "A3.4b": "FAILED: S1 inside the full run differs from S1 alone with recorded inputs by up to 0.931% (2004 set) against 0.25%",
                       "scope": "These tests used the STANDARD parameters only. Runs with changed parameters have NOT been compared with WorldDynamics.jl."}}


def main() -> None:
    d0 = load_demo0()
    rec_path = Path(sys.argv[1])
    z = np.load(rec_path)
    rec = {k: z[k] for k in z.files}
    if len(rec["years"]) != 76 or int(rec["years"][0]) != 2025:
        raise SystemExit("climate recording must cover 2025..2100")
    data = d0.run_all(rec)                                  # AI race + climate (the Demo 0 grid, 841-member climate replayed)
    data["meta"] = {
        "settings": d0.SETTING_TEXT, "damage_coeff_pct_per_K2": {k: v * 100 for k, v in d0.damages.OPTIONS.items() if k != "off"},
        "damage_sources": d0.damages.SOURCES, "iea": {"2024": d0.IEA_2024_TWH, "2025": d0.IEA_2025_TWH, "2030": d0.IEA_2030_TWH},
        "s3_status": d0.S3AI.validation_status, "s6_status": d0.S6Climate.validation_status, "dc_status": d0.DataCentre.validation_status,
        "provenance": d0.provenance(rec_path),
    }
    data["world3"] = world3_grid()
    here = Path(__file__).parent
    (here / "data").mkdir(exist_ok=True)
    (here / "data" / "explorer.json").write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8", newline="\n")
    tpl = (here / "template.html").read_text(encoding="utf-8")
    html = tpl.replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))
    (here / "index.html").write_text(html, encoding="utf-8", newline="\n")
    print("wrote site/index.html", len(html), "bytes; site/data/explorer.json", (here / "data" / "explorer.json").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
