"""Merge the results of all registry-snapshot jobs (and the older pin jobs) into one markdown table.

Reads <dir>/<job>/ folders named snap_<date> (or pin_<version>) containing
t0_1_world3_report.md, t0_4_crosscheck_report.md, registry_commit.txt and install.log.
Prints markdown. The question the table answers: does WorldDynamics.jl solve World3
with DEFAULT options in this dependency set, and does the result agree with PyWorld3?
"""
import re
import sys
from pathlib import Path

KEYS = ["ModelingToolkit", "SciMLBase", "OrdinaryDiffEq", "DiffEqBase", "DifferentialEquations"]
DEFAULT_LABELS = ["default options", "default options, saveat = 0.5",
                  "default options, saveat = 0.5, reltol = abstol = 1e-8"]
NOINIT_LABEL = "NoInit()"


def parse_world3(path):
    versions, attempts, pending = {}, {}, None
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"\s+- (\w+) (\d+\.\d+\.\d+\S*)$", line)
        if m and m.group(1) in KEYS + ["OrdinaryDiffEqCore"]:
            versions[m.group(1)] = m.group(2)
        m = re.match(r"\s+- return code: `(\w+)`; (\d+) time point", line)
        if m:
            pending = {"ret": m.group(1), "n": int(m.group(2))}
        m = re.match(r"- (✅|❌) Solve \(1900–2100\), (.*)$", line)
        if m:
            label = m.group(2)
            if m.group(1) == "✅":
                attempts[label] = pending or {"ret": "?", "n": 0}
            else:
                err, j = "", i + 1
                while j < len(lines) and not lines[j].strip().startswith("```"):
                    j += 1
                if j + 1 < len(lines):
                    err = lines[j + 1].strip()
                attempts[label] = {"ret": "error", "n": 0, "err": err[:80]}
            pending = None
    return versions, attempts


def parse_cross(path):
    out, tag = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"- `(\w+)` \((\d+) points\)", line)
        if m:
            tag = m.group(1)
            out[tag] = {}
        m = re.match(r"  - vs (.*?): \d+ variables; worst \*\*([\d.]+)%\*\* \(`(\w+)`, (\d+)\)", line)
        if m and tag:
            what = m.group(1)
            key = ("diag" if "diagnostic" in what else "fine" if what.endswith("dt=0.05") else "coarse")
            out[tag][key] = f"{float(m.group(2)):.2f}% ({m.group(3)}, {m.group(4)})"
    return out


def cell(a):
    if a is None:
        return "—"
    if a["ret"] == "error":
        return f"error: {a.get('err', '')}"
    return f"{a['ret']} ({a['n']} pt)"


def main(root):
    rows, failures = [], []
    for d in sorted(p for p in Path(root).iterdir() if p.is_dir() and re.match(r"(snap|pin)_", p.name)):
        name = d.name.split("_", 1)[1]
        commit = (d / "registry_commit.txt").read_text().strip()[:8] if (d / "registry_commit.txt").exists() else ""
        r1 = d / "t0_1_world3_report.md"
        if not r1.exists():
            log = d / "install.log"
            tail = log.read_text(errors="replace").strip().splitlines()[-14:] if log.exists() else ["(no install log)"]
            rows.append((name, commit, "—", "—", "—", "no report", "—", "—", "install failed"))
            failures.append((name, tail))
            continue
        versions, attempts = parse_world3(r1)
        defaults = [attempts.get(l) for l in DEFAULT_LABELS]
        works = any(a and a["ret"] == "Success" and a["n"] >= 50 for a in defaults)
        noinit = attempts.get(NOINIT_LABEL)
        cross = {}
        r4 = d / "t0_4_crosscheck_report.md"
        if r4.exists():
            cross = parse_cross(r4)
        pref = ["default_tight", "default_saveat", "default", "noinit_tight", "noinit_saveat", "noinit"]
        tag = next((t for t in pref if t in cross), None)
        gap = f"`{tag}`: shipped {cross[tag].get('fine', '—')}; diagnostic {cross[tag].get('diag', '—')}" if tag else "—"
        rows.append((name, commit, versions.get("ModelingToolkit", "?"), versions.get("SciMLBase", "?"),
                     versions.get("OrdinaryDiffEq", "?"), cell(defaults[0]), cell(noinit),
                     "**YES**" if works else "no", gap))
    print("## World3 / WorldDynamics.jl: does it solve with default options?\n")
    print("| job | registry commit | ModelingToolkit | SciMLBase | OrdinaryDiffEq | default options | NoInit() | works with defaults | cross-check: worst gap vs PyWorld3 dt=0.05 (stock, year) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    for name, tail in failures:
        print(f"\n### Install failed: {name}\n\n```")
        for t in tail:
            print(t[:170])
        print("```")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "audit/results")
