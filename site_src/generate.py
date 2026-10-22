"""F3 Explorer v0.2 generator (D-056): writes site/index.html (story), explorer.html (dashboard), compare.html, connections.html, methods.html, limitations.html, sources.html,
about.html, site/assets/* (stylesheet with the embedded font, core.js, charts.js and the page scripts) and site/data/explorer.json plus its script form site/data/explorer.js.

Static site (D-009): precomputed scenario grids, no backend. Published as a public draft on 2026-10-21 (editor).

    PYTHONPATH=. python site_src/generate.py <climate841.npz>      # full build: runs the grids (about 2 minutes)
    PYTHONPATH=. python site_src/generate.py --reuse               # restamp pages from site/data/explorer.json (date, commit hash); add --built-commit <hash> after committing the pages, so About names the commit that contains them

The generator and templates live in site_src/ (not in site/) so that what is deployed is only pages and data.
Three panels; ONE coupling is shown (D-052, D-051): climate damage to World3 industrial output (default off):
  1. World3 (2004 parameter set, D-015), D-031 group: 27 runs from 3 levers x 3 values (D-046, Provisional) x 4 damage states (off, low, central, high).
  2. Climate: the 841-member FaIR recording (D-021 option a, exact), emissions prescribed.
  3. AI race: the Demo 0 slice grid (S3 under R3 + data-centre module + damage option), reused from dashboard/demo0/generate.py.
     The S3 compute and data-centre electricity series stay in the data but are NOT rendered (withheld until the S3 compute path is validated).
"""
from __future__ import annotations

import datetime
import importlib.util
import itertools
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).parent))

import pages  # noqa: E402

PPOL70 = 1.36e8                      # World3 ppol70 (persistent pollution in 1970), ppolx = ppol / ppol70

# Provisional (delegated) choice of levers (D-046): (parameter, label, values, value labels, index of the standard value)
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


DAMAGE_STATES = ["off", "low", "central", "high"]


def run_world3(over: dict, parameter_set: str = "2004", damage: str = "off", warming=None):
    """One World3 group run. ``damage`` is "off" (the default, bit-identical to stand-alone World3) or a D-007 option; with damage on, the merged M6
    coupling is used (io = io_gross x (1 - Omega(T)) from 2025) with ``warming`` = the recorded FaIR ensemble mean (a callable year -> K)."""
    from f3.core import Model
    from f3.sectors.world3 import STATE_COLUMNS, _initial_inputs, build_world3
    from f3.sectors.world3_group import World3Group

    sectors, couplings = build_world3(parameter_set)
    for s in sectors:
        if hasattr(s, "params"):
            for k, v in over.items():
                if k in s.params:
                    s.params[k] = v
    init = _initial_inputs(sectors, 1900.0)
    g = World3Group(sectors, couplings, init, STATE_COLUMNS, damage_option=None if damage == "off" else damage, warming=warming)
    res = Model([g], [], t0=1900.0, t1=2100.0, dt=0.25).run()
    st = {n: res.series[(g.name, n)] for n in STATE_COLUMNS}
    st["io"] = res.series[(g.name, "io")]
    idx = [i for i, t in enumerate(res.time) if abs(t - round(t)) < 1e-9]            # yearly
    nri = over.get("nri", 1.0e12)
    out = {"pop": st["p1"] + st["p2"] + st["p3"] + st["p4"], "io": st["io"], "ic": st["ic"], "al": st["al"], "nrfr": st["nr"] / nri, "ppolx": st["ppol"] / PPOL70}
    return [int(round(res.time[i])) for i in idx], {k: [float(f"{v[i]:.6g}") for i in idx] for k, v in out.items()}


def world3_grid(rec) -> dict:
    """27 lever runs x 4 damage states (D-052). Key: "i|j|k|damage". Warming for the damage runs is the recorded FaIR ensemble mean (no new FaIR run)."""
    import numpy as np
    wy, ww = np.asarray(rec["years"], dtype=float), np.asarray(rec["warming"], dtype=float)
    warming = lambda t: float(np.interp(t, wy, ww))          # noqa: E731
    years, runs = None, {}
    for combo in itertools.product(*[range(3) for _ in LEVERS]):
        over = {p: vals[i] for (p, _, vals, _, _), i in zip(LEVERS, combo)}
        for dmg in DAMAGE_STATES:
            years, series = run_world3(over, damage=dmg, warming=warming)
            runs["|".join(map(str, combo)) + "|" + dmg] = series
    std = "|".join(str(l[4]) for l in LEVERS)
    from f3.sectors import damages
    from f3.sectors.world3_group import DAMAGE_COUPLING_LABEL, DAMAGE_START_YEAR
    return {"years": years, "runs": runs, "standard": std, "damage_states": DAMAGE_STATES,
            "levers": [{"param": p, "label": lab, "values": vals, "value_labels": vl, "standard_index": si} for p, lab, vals, vl, si in LEVERS],
            "damage": {"default": "off", "start_year": DAMAGE_START_YEAR, "label": DAMAGE_COUPLING_LABEL,
                       "coeff_pct_per_K2": {k: v * 100 for k, v in damages.OPTIONS.items() if k != "off"}},
            "parameter_set": "2004 (World3_03 scenario 1; the provisional default of D-015)",
            "status": {"A3.1": "met: all 14 states of the four sectors within 0.124% of WorldDynamics.jl, both parameter sets",
                       "A3.2": "met after D-031 (0.0625-year sub-steps inside the 0.25-year loop): all 29 states within 2%, worst 1.906% (2004 set)",
                       "A3.4b": "FAILED: S1 inside the full run differs from S1 alone with recorded inputs by up to 0.931% (2004 set) against 0.25%",
                       "scope": "These tests used the STANDARD parameters only. Runs with changed parameters have NOT been compared with WorldDynamics.jl.",
                       "M6": "the damage coupling is tested (tests/test_m6_damage_coupling.py: switch off equals stand-alone World3 to 1e-9; zero warming equals baseline; more warming lowers industrial output; bounds over the full grid). Damage-on runs are NOT compared with WorldDynamics.jl, which has no climate damage."}}


def git(*args) -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True).stdout.strip()
    except Exception:
        return "unknown"


def build_data(rec_path: Path) -> dict:
    import numpy as np
    d0 = load_demo0()
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
    data["world3"] = world3_grid(rec)
    return data


def main() -> None:
    here = REPO / "site"
    (here / "data").mkdir(parents=True, exist_ok=True)
    jpath = here / "data" / "explorer.json"
    built = sys.argv[sys.argv.index("--built-commit") + 1] if "--built-commit" in sys.argv else None
    if len(sys.argv) > 1 and sys.argv[1] == "--reuse":
        data = json.loads(jpath.read_text(encoding="utf-8"))
    else:
        data = build_data(Path(sys.argv[1]))
        jpath.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8", newline="\n")
    (here / "data" / "explorer.js").write_text("window.F3DATA=" + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    stamp = {"date": datetime.date.today().isoformat(), "commit": git("rev-parse", "--short", "HEAD") or "unknown"}
    if built:
        stamp["built_commit"] = built
    stamp["dirty"] = "yes" if git("status", "--porcelain", "--", "site_src", "docs", "f3") else "no"
    for name, html in pages.render_all(data, stamp, Path(__file__).parent).items():
        (here / name).write_text(html, encoding="utf-8", newline="\n")
        print("wrote site/" + name, len(html), "bytes")
    for rel, text in pages.render_assets(Path(__file__).parent).items():
        (here / rel).parent.mkdir(parents=True, exist_ok=True)
        (here / rel).write_text(text, encoding="utf-8", newline="\n")
        print("wrote site/" + rel, len(text), "bytes")
    print("stamp:", stamp)


if __name__ == "__main__":
    main()
