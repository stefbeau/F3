"""T0 cross-check: World3 main stocks, WorldDynamics.jl variants vs PyWorld3.

Both implement the 1974 World3 model (*Dynamics of Growth in a Finite World*):
WorldDynamics.jl's `World3` module and PyWorld3's `World3` class.

Compared (levels): population cohorts p1-p4 and their sum, industrial capital ic,
service capital sc, arable land al, potentially arable land pal, urban-industrial
land uil, land fertility lfert, persistent pollution ppol, nonrenewable resources nr.

Every WorldDynamics.jl solver variant exported by world3_t0.jl
(world3_worlddynamics_states_<variant>.csv) is compared with PyWorld3 at its default
step (dt=0.5) and with the fine-step run (dt=0.05, near the continuous limit).

Gap metric: |WorldDynamics - PyWorld3| / max(|PyWorld3|, 0.1% of that variable's
maximum). The floor stops near-zero values from producing meaningless huge ratios.
Informational at T0 (D-012: gaps must be explained, not necessarily zero).

Guards (added after run #3 produced a false "0.00% gap" from a 1-point solution): a
file with fewer than 50 time points, or not covering 1900-2100, is refused; a
variable whose column cannot be identified unambiguously is reported, not guessed.
"""
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(os.environ.get("F3_OUT", Path(__file__).resolve().parents[1] / "results"))
MIN_POINTS = 50
BAND = 0.02  # D-004
STOCKS = ["p1", "p2", "p3", "p4", "ic", "sc", "al", "pal", "uil", "lfert", "ppol", "nr"]
report = ["## T0 — World3 cross-check (WorldDynamics.jl vs PyWorld3), main stocks", ""]


def column_for(df, name):
    """The single column whose last name component is `name` (e.g. 'pop₊p1(t)')."""
    pat = re.compile(r"(^|[₊.])" + re.escape(name) + r"(\(t\))?$")
    hits = [c for c in df.columns[1:] if pat.search(c)]
    return hits[0] if len(hits) == 1 else (None if not hits else hits)


def gap(t, y, ref_t, ref_y):
    ref_i = np.interp(t, ref_t, ref_y)
    floor = 1e-3 * np.abs(ref_y).max()
    rel = np.abs(y - ref_i) / np.maximum(np.abs(ref_i), floor if floor > 0 else 1.0)
    return rel, int(np.argmax(rel))


def compare_variant(df, refs):
    """-> (rows, notes). rows: list of (variable, ref_label, max, t_of_max, mean)."""
    t = df[df.columns[0]].to_numpy()
    rows, notes = [], []
    series = {}
    for name in STOCKS:
        col = column_for(df, name)
        if col is None:
            notes.append(f"`{name}`: no matching column")
        elif isinstance(col, list):
            notes.append(f"`{name}`: ambiguous columns {col}")
        else:
            series[name] = df[col].to_numpy()
    if all(k in series for k in ("p1", "p2", "p3", "p4")):
        series["pop"] = sum(series[k] for k in ("p1", "p2", "p3", "p4"))
    for name, y in series.items():
        for label, ref in refs:
            if name not in ref:
                continue
            rel, k = gap(t, y, ref["time"].to_numpy(), ref[name].to_numpy())
            rows.append((name, label, rel.max(), t[k], rel.mean()))
    return rows, notes


try:
    py = pd.read_csv(OUT / "world3_pyworld3.csv")
    fine_path = OUT / "world3_pyworld3_fine.csv"
    refs = [("PyWorld3 dt=0.5", py)]
    if fine_path.exists():
        refs.append(("PyWorld3 dt=0.05", pd.read_csv(fine_path)))
    files = sorted(OUT.glob("world3_worlddynamics_states_*.csv"))
    if not files:
        report.append("- ❌ No WorldDynamics.jl export found (an earlier step failed)")
    results = {}
    for f in files:
        tag = f.stem.replace("world3_worlddynamics_states_", "")
        df = pd.read_csv(f)
        try:
            t = df[df.columns[0]]
            if len(df) < MIN_POINTS:
                raise ValueError(f"only {len(df)} time points (need >= {MIN_POINTS})")
            if t.min() > 1901 or t.max() < 2099:
                raise ValueError(f"time range {t.min():.0f}-{t.max():.0f} does not cover 1900-2100")
            rows, notes = compare_variant(df, refs)
            if not rows:
                raise ValueError("no stock column could be identified")
        except Exception as e:
            report.append(f"- ❌ `{tag}`: refused: {e}")
            continue
        results[tag] = (df, rows, notes)
        line = f"- `{tag}` ({len(df)} points)"
        for label, _ in refs:
            sub = [r for r in rows if r[1] == label]
            worst = max(sub, key=lambda r: r[2])
            n_out = sum(r[2] > BAND for r in sub)
            line += (f"\n  - vs {label}: {len(sub)} variables; worst **{worst[2] * 100:.2f}%** "
                     f"(`{worst[0]}`, {worst[3]:.0f}); {n_out} outside ±2%")
        for n in notes:
            line += f"\n  - ⚠️ {n}"
        report.append(line)

    if results:
        best = "noinit_tight" if "noinit_tight" in results else max(results, key=lambda k: len(results[k][0]))
        df, rows, _ = results[best]
        report.append("")
        report.append(f"### Per-variable gaps, variant `{best}`")
        report.append("")
        report.append("| variable | " + " | ".join(f"max / mean vs {l}" for l, _ in refs) + " |")
        report.append("|---|" + "---|" * len(refs))
        for name in sorted({r[0] for r in rows}, key=lambda n: (n == "pop", STOCKS.index(n) if n in STOCKS else 99)):
            cells = []
            for label, _ in refs:
                r = [x for x in rows if x[0] == name and x[1] == label]
                cells.append(f"{r[0][2] * 100:.2f}% / {r[0][4] * 100:.2f}%" if r else "—")
            report.append(f"| `{name}` | " + " | ".join(cells) + " |")
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            t = df[df.columns[0]].to_numpy()
            fig, axes = plt.subplots(3, 4, figsize=(14, 8))
            fine = refs[-1][1]
            for ax, name in zip(axes.ravel(), STOCKS):
                col = column_for(df, name)
                if isinstance(col, str):
                    ax.plot(t, df[col], label=f"WorldDynamics.jl ({best})")
                ax.plot(py["time"], py[name], "--", label="PyWorld3 dt=0.5")
                if name in fine:
                    ax.plot(fine["time"], fine[name], ":", label="PyWorld3 dt=0.05")
                ax.set_title(name)
            axes[0, 0].legend(fontsize=7)
            fig.suptitle("World3 (1974) main stocks: WorldDynamics.jl vs PyWorld3")
            fig.tight_layout()
            fig.savefig(OUT / "world3_stocks_crosscheck.png", dpi=110)
            report.append("")
            report.append("- Figure saved: `world3_stocks_crosscheck.png`")
        except Exception as e:
            report.append(f"- (figure not produced: {e})")
except FileNotFoundError as e:
    report.append(f"- ❌ Input missing (an earlier step failed): {e.filename}")
except Exception as e:
    report.append(f"- ❌ Comparison failed: {type(e).__name__}: {e}")

(OUT / "t0_4_crosscheck_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
