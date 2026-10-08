"""A1.1 evidence for M1 (docs/phase-2-plan.md): what Epoch AI's GATE playground (https://epoch.ai/gate) contains and can export.

This script READS a copy of the playground's script bundle that has been downloaded to a scratch folder OUTSIDE the repository
(``curl -sSL https://epoch.ai/generated/gate.js -o gate.js``; the bundle is not committed, and none of its code is reused).
It prints: the parameter table the page embeds (names, defaults, the playground's two presets, soft and hard limits), what the
page's download/upload actions do, and the structure and precision of the three precomputed runs the page ships.

    uv run python audit/t0/gate_playground_probe.py <path to gate.js>

Findings are in research/gate-equations.md, section "What the playground can export". The numbers printed here are Epoch AI's
(CC BY, credit required) and are not stored in the repository.
"""

from __future__ import annotations

import json
import re
import sys

BS = chr(92)


def balanced(text: str, start: int, open_ch: str, close_ch: str) -> str:
    depth, instr, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if instr:
            if esc:
                esc = False
            elif ch == BS:
                esc = True
            elif ch == '"':
                instr = False
        elif ch == '"':
            instr = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError("unbalanced")


def parameter_table(t: str):
    a = t.index('[', t.find('// legacy/one-offs/gate/sidebar/input.csv'))
    seg = t[a:t.index('];', a)]
    starts = [m.start() for m in re.finditer(r'\{\s*"Parameter name"\s*:', seg)] + [len(seg)]
    fields = ["Parameter name", "Symbol", "Units", "Default", "Conservative", "Aggressive", "Hard minimum", "Soft minimum",
              "Soft maximum", "Hard maximum", "Variable in code", "Playground visibility"]
    rows = []
    for s0, s1 in zip(starts[:-1], starts[1:]):
        txt, row = seg[s0:s1], {}
        for f in fields:
            m = re.search(r'"' + re.escape(f) + r'"\s*:\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^,}\n]+)', txt)
            if m:
                v = m.group(1).strip()
                row[f] = v[1:-1] if v[:1] in "\"'" else v
        rows.append(row)
    return rows


def main(path: str) -> None:
    t = open(path, encoding="utf-8", errors="replace").read()
    rows = parameter_table(t)
    print(f"parameter table: {len(rows)} rows")
    print("| name | code name | default | conservative | aggressive | soft min | soft max | hard min | hard max | visibility |")
    for r in rows:
        print("| " + " | ".join(r.get(k, "") for k in ["Parameter name", "Variable in code", "Default", "Conservative", "Aggressive",
                                                      "Soft minimum", "Soft maximum", "Hard minimum", "Hard maximum",
                                                      "Playground visibility"]) + " |")

    print("\nactions in the page script:")
    for pat, label in ((r'function downloadJSON', "downloadJSON(parameters)"), (r'function uploadJSON', "uploadJSON(parameters)"),
                       (r'function downloadSVG', "downloadSVG -> PNG of a chart"), (r'epoch-gate-parameters\.json', "file name of the parameter download"),
                       (r'epoch-gate-model-', "file-name prefix of a chart download"), (r'Copy link', "'Copy link' label")):
        print(f"  {label:42s} {'present' if re.search(pat, t) else 'absent'}")
    print("  CSV download of result series:             ", "present" if re.search(r'text/csv|\.csv"\)|toCSV', t) else "no sign of one in the script")

    cache = json.loads(balanced(t, t.index('[', t.find('// legacy/one-offs/gate/backend/cache.json')), '[', ']'))
    print(f"\nshipped results cache: {len(cache)} runs")
    keys = None
    for k, e in enumerate(cache):
        p = e["args"]["modelParams"]
        st = e["run"]["world_path"]["states"]
        keys = keys or list(st[0].keys())
        print(f"  run {k}: T(OOM)={p['automation']['train_reqs']}, hw returns={p['rnd']['hardware_returns']}, sw returns={p['rnd']['software_returns']}, "
              f"lambda_H={p['rnd']['total_lambda_rnd_hardware']}, lambda_S={p['rnd']['total_lambda_rnd_software']}; "
              f"{len(st)} states, time {st[0]['time']}..{st[-1]['time']}; solver {e['args']['simulationArgs'].get('implementation')}, "
              f"dt={e['args']['simulationArgs'].get('dt')}, {e['args']['simulationArgs'].get('precision')}")
    print("  fields per state:", keys)
    raw = json.dumps(cache)
    nums = re.findall(r'-?\d+\.\d+(?:e[+-]?\d+)?', raw)
    digs = sorted(len(re.sub(r'[^0-9]', '', n.split('e')[0]).strip('0')) for n in nums if n.split('e')[0].replace('.', '').strip('-0'))
    print(f"  stored precision: median {digs[len(digs) // 2]} significant digits (min {digs[0]}, max {digs[-1]})")

    s0 = cache[0]["run"]["world_path"]["states"][0]
    p0 = cache[0]["args"]["modelParams"]
    print("\nfirst stored state of run 0 against the initial conditions in the same run's parameters (timing convention):")
    pairs = [("labor", p0["main"]["labor_force_init"]), ("gwp", p0["main"]["gwp_init"]), ("capital", p0["main"]["capital_init"]),
             ("hardware", p0["main"]["hardware_init"]), ("software", p0["main"]["software_init"]),
             ("best_training_run", p0["main"]["best_training_run"]), ("frac_automated", p0["automation"]["initial_frac"])]
    for name, init in pairs:
        print(f"  {name:20s} stored state[0] = {s0[name]:.7g}   parameter (initial) = {init:.7g}   ratio {s0[name] / init:.4g}")
    import math
    print(f"  labor: initial * exp(g_L) = {p0['main']['labor_force_init'] * math.exp(p0['labor']['pop_growth']):.7g} (g_L = {p0['labor']['pop_growth']})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1])
