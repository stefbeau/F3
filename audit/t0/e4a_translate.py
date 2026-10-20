"""Mechanical translation of Earth4All.jl sector sources (MIT, commit 16f37d0) into the F3 sector modules f3/sectors/e4a_<sector>.py.

    python audit/t0/e4a_translate.py <clone> <sector keys...>      # writes f3/sectors/e4a_<key>.py

Reads only src/<sector>/{subsystems,parameters,initialisations}.jl of the clone (never vensim_source/ or VensimOutput/). Each
equation of the main system function (the ``*_support`` scaffolding systems are skipped) becomes one Python expression, with the
source line number kept beside it. The translation is syntactic: ``^`` to ``**``, ``IfElse.ifelse(c, a, b)`` to ``(a if c else b)``,
``inits[:K]`` to the initial-value constant ``I_K``, the time ``t`` in a comparison or in ``step``/``pulse`` to the switch time ``ts``.
The three F3 additions (switches of the warming channels, plan A4.2) are explicit patches listed in PATCHES and marked in the module.
The generated modules are committed; this script is the provenance of their equations.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

KEYS = {"output": "Output", "inventory": "Inventory", "finance": "Finance", "labourmarket": "LabourMarket", "public": "Public",
        "demand": "Demand", "energy": "Energy", "other": "Other"}
GL = {  # src/earth4all/scenarios.jl, run_gl: dem lines 39-45, ene 48-51, out 67-68, pub 74
    "demand": {"EETF2022": 0.02, "EGTRF2022": 0.01, "EPTF2022": 0.02, "ETGBW": 0.2, "FETPO": 0.8, "FGDC2022": 0.1, "GEIC": 0.02},
    "energy": {"GFCO2SCCS": 0.9, "EROCEPA2022": 0.004, "GFNE": 1.0, "GREF": 1.0},
    "output": {"USPIS2022": 0.01, "USPUS2022": 0.01},
    "public": {"MIROTA2022": 0.005},
}
# F3 additions (A4.2): a switch multiplies the coefficient of the warming channel; default 1 reproduces Earth4All.jl exactly.
PATCHES = {
    "output": {
        "OWECC": ("1 + OWECCM * (OW / OW2022 - 1)", "1 + SW_OWECC * OWECCM * (OW / OW2022 - 1)"),
        "OWELC": ("1 + OWELCM * (OW / OW2022 - 1)", "1 + SW_OWELC * OWELCM * (OW / OW2022 - 1)"),
    },
    "public": {"OWTFP": ("1 + OWETFP * (OW / OW2022 - 1)", "1 + SW_OWTFP * OWETFP * (OW / OW2022 - 1)")},
}
EXTRA_PARAMS = {"output": {"SW_OWECC": 1.0, "SW_OWELC": 1.0}, "public": {"SW_OWTFP": 1.0}}
FUNCS = {"if", "else", "ramp", "step", "pulse", "withlookup", "max", "min", "exp", "log", "ifelse", "True", "False"}


def split_top(s: str, sep: str = ","):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out]


def match_paren(s: str, i: int) -> int:
    """index of the ')' closing the '(' at s[i]"""
    d = 0
    for j in range(i, len(s)):
        if s[j] == "(":
            d += 1
        elif s[j] == ")":
            d -= 1
            if d == 0:
                return j
    raise ValueError("unbalanced: " + s)


def conv_ifelse(s: str) -> str:
    k = s.find("IfElse.ifelse(")
    while k >= 0:
        o = k + len("IfElse.ifelse")
        c = match_paren(s, o)
        a = split_top(s[o + 1:c])
        assert len(a) == 3, s
        s = s[:k] + f"(({conv_ifelse(a[1])}) if ({conv_ifelse(a[0])}) else ({conv_ifelse(a[2])}))" + s[c + 1:]
        k = s.find("IfElse.ifelse(")
    return s


def to_py(expr: str) -> str:
    s = conv_ifelse(expr)
    s = s.replace("^", "**")
    s = re.sub(r"inits\[:(\w+)\]", r"I_\1", s)
    s = re.sub(r"\bt\s*(>=|>|<=|<)", r"ts_ \1", s)
    s = re.sub(r"\b(step|pulse)\(t\b", r"\1(ts_", s)

    def rep(m):
        w = m.group(0)
        if w in FUNCS:
            return w
        if w == "ts_":
            return "v.ts"
        return "v." + w

    return re.sub(r"(?<![\w.])[A-Za-z_]\w*", rep, s)


def parse_dict(path: Path, name: str):
    txt = path.read_text(encoding="utf-8")
    out = {}
    for ln in txt.splitlines():
        m = re.match(r"\s*:(\w+)\s*=>\s*([^,#]+),", ln)
        if m:
            out[m.group(1)] = float(eval(m.group(2).strip()))
    return out


def main_body(lines):
    """(start, end) 0-based line indices of the body of the main system function"""
    for i, ln in enumerate(lines):
        if re.match(r"function \w+\(; name", ln) and "support" not in ln:
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("end"):
                    return i + 1, j
    raise ValueError("no main function")


def units_from_desc(d: str) -> str:
    d = d.strip()
    if d.endswith("(1)"):
        return "1"
    toks = d.split()
    last = toks[-1] if toks else ""
    if ")" in last or "(" in last:
        return "1"
    if len(toks) > 1 and re.search(r"[/0-9]|dollar|^M[pu]|^G[a-z]|^k[a-z]|GW|TWh|Mtoe|toe|deg|^y$|ftj", last, re.I):
        return last.lower().replace("dollar", "usd")
    return "1"


def translate(key: str, clone: Path):
    base = clone / "src" / key
    sub = (base / "subsystems.jl").read_text(encoding="utf-8").splitlines()
    params = parse_dict(base / "parameters.jl", "_params")
    inits = parse_dict(base / "initialisations.jl", "_inits")
    a, b = main_body(sub)
    eqs, ders, states, plain, state_init, pexpr, units = {}, {}, [], [], {}, {}, {}
    declared_params = []
    lineno_eq, lineno_der = {}, {}
    for i in range(a, b):
        ln = sub[i].strip()
        ln1 = i + 1
        if not ln or ln.startswith("#") or ln == "eqs = []" or ln.startswith("return ODESystem"):
            continue
        m = re.match(r"@parameters (\w+) = (.+?)(?: \[description = \"(.*)\"\])?$", ln)
        if m:
            declared_params.append((m.group(1), m.group(2)))
            continue
        m = re.match(r"@variables (\w+)\(t\)(?: = (.+?))?(?: \[description = \"(.*)\"\])?$", ln)
        if m:
            nm, init, desc = m.group(1), m.group(2), m.group(3)
            if desc:
                units[nm] = units_from_desc(desc)
            if init:
                state_init[nm] = init
            if not desc and not init:
                plain.append(nm)
            continue
        m = re.match(r"smooth!\(eqs, (\w+), (.+)\)$", ln)
        if m:
            args = split_top(m.group(2))
            x = m.group(1)
            assert len(args) == 2, ln
            ders[x] = f"({to_py(args[0])} - v.{x}) / ({to_py(args[1])})"
            lineno_der[x] = ln1
            states.append(x)
            continue
        m = re.match(r"add_equation!\(eqs, (.+)\)$", ln)
        if m:
            lhs, rhs = [x.strip() for x in m.group(1).split(" ~ ", 1)]
            md = re.match(r"D\((\w+)\)$", lhs)
            if md:
                ders[md.group(1)] = to_py(rhs)
                lineno_der[md.group(1)] = ln1
                states.append(md.group(1))
            else:
                p = PATCHES.get(key, {}).get(lhs)
                if p:
                    assert p[0] in rhs, (lhs, rhs)
                    rhs = rhs.replace(p[0], p[1])
                eqs[lhs] = to_py(rhs)
                lineno_eq[lhs] = ln1
            continue
        raise ValueError(f"{key} line {ln1}: unparsed: {ln}")
    # parameters: dict values, plus declared parameters whose expression is not the plain dict entry
    P = dict(params)
    P.update(EXTRA_PARAMS.get(key, {}))
    for nm, ex in declared_params:
        mm = re.fullmatch(r"params\[:(\w+)\]", ex)
        if mm and mm.group(1) == nm:
            assert nm in params, (key, nm)
            continue
        if mm:
            pexpr[nm] = f'P["{mm.group(1)}"]'
        else:
            pexpr[nm] = re.sub(r"params\[:(\w+)\]", r'P["\1"]', ex)
    # units of unit-less plain inputs come from the support systems of the same file
    sup_units = {}
    for ln in sub:
        mm = re.match(r"\s*@variables (\w+)\(t\) \[description = \"(.*)\"\]", ln)
        if mm:
            sup_units.setdefault(mm.group(1), units_from_desc(mm.group(2).split(".", 1)[-1]))
    # inputs: plain variables not defined by an equation or state
    inputs = [x for x in plain if x not in eqs and x not in ders]
    return dict(params=params, P=P, inits=inits, pexpr=pexpr, state_init=state_init, eqs=eqs, ders=ders, states=states, inputs=inputs,
                units=units, sup_units=sup_units, lineno_eq=lineno_eq, lineno_der=lineno_der)


def render(key: str, T: dict, clone: Path) -> str:
    cls = KEYS[key] + "Sector"
    H = f'''"""F3 port of the Earth4All.jl `{KEYS[key]}` sector ({key}), generated by audit/t0/e4a_translate.py.

ATTRIBUTION
-----------
Ported from Earth4All.jl (https://github.com/worlddynamics/Earth4All.jl) commit 16f37d013a2f68135f03e7815bf861dbf47311f2, MIT licence,
Copyright (c) 2023 World Dynamics (see NOTICE, licenses/Earth4All.jl-MIT.txt; decisions D-011, D-016, D-018). Equations are from
`src/{key}/subsystems.jl` (function `{KEYS[key].lower() if key != "labourmarket" else "labour_market"}`; the `*_support` scaffolding systems are not ported),
parameters from `src/{key}/parameters.jl`, initial values from `src/{key}/initialisations.jl`; the number after `L` beside each
equation is its line in `subsystems.jl`. Giant Leap overrides: `src/earth4all/scenarios.jl` `run_gl`. Nothing is taken from
`vensim_source/` or from `VensimOutput/` (D-014). F3 code is Apache 2.0 (D-001).

The reference for the tests is Earth4All.jl itself (D-011, D-018); Earth4All.jl follows Vensim closely for most variables but not for
all, and nothing here claims that the port reproduces Vensim.

{{EXTRA}}
Inputs (variables read from other sectors): {", ".join(T["inputs"]) or "none"}.
States ({len(T["states"])}): {", ".join(T["states"])}.
"""

from __future__ import annotations

import numpy as np

from f3.sectors.e4a_common import E4ASector, ifelse, pulse, ramp, step, withlookup  # noqa: F401
'''
    extra = ""
    if key == "output":
        extra = ("F3 ADDITION (plan A4.2): the three warming channels are switchable. `SW_OWECC` and `SW_OWELC` (default 1) multiply the\n"
                 "coefficients of `OWECC` (cost of capacity) and `OWELC` (life of capacity); 1 reproduces Earth4All.jl exactly, 0 switches\n"
                 "the channel off. Earth4All.jl divides the observed warming by the constant `OW2022` = 1.35 degrees C (D-023: the baseline\n"
                 "of F3's own warming against this constant is NOT checked).")
    if key == "public":
        extra = ("F3 ADDITION (plan A4.2): `SW_OWTFP` (default 1) multiplies the coefficient of the warming channel `OWTFP` on the indicated\n"
                 "TFP; 0 switches it off.\n"
                 "DOCUMENTED PARAMETER `EDROTA2022` = 0.003 per year (Extra Domestic Rate Of Technological Advance from 2022, `DRTA` L61):\n"
                 "non-zero in both scenarios of Earth4All.jl (D-016); from 2022 it adds `EDROTA2022 * (1 + SCROTA * (SC / SC1980 - 1))` to\n"
                 "the domestic rate of technological advance `DRTA`. Pass `params={'EDROTA2022': value}` to change it.")
    if key == "demand":
        extra = ("NOTE (plan, section 1): `IC2022` (L159) has the ramp end `2020 + IPP` where the other policy ramps use `2022 + IPP`; whether the\n"
                 "Vensim model has it was not checked; the port copies it as in Earth4All.jl so that the reference is reproduced.")
    out = H.replace("{EXTRA}", extra)
    # units
    allu = dict(T["sup_units"])
    allu.update(T["units"])
    names = list(T["eqs"]) + list(T["states"])
    out += "\nPARAMS = {\n" + "".join(f'    "{k}": {v!r},\n' for k, v in T["P"].items()) + "}\n"
    out += "PARAMS_GL = " + repr(GL.get(key, {})) + "\n"
    out += "PARAM_EXPR = {\n" + "".join(f'    "{k}": {v!r},\n' for k, v in T["pexpr"].items()) + "}\n"
    out += "INITS = {\n" + "".join(f'    "{k}": {v!r},\n' for k, v in T["inits"].items()) + "}\n"
    out += "STATE_NAMES = (" + "".join(f'"{s}", ' for s in T["states"]) + ")\n"
    out += "STATE_INIT = {\n"
    for s in T["states"]:
        ex = T["state_init"].get(s)
        assert ex is not None, (key, s)
        ex = re.sub(r"params\[:(\w+)\]", r'P["\1"]', ex)
        ex = re.sub(r"inits\[:(\w+)\]", r'I["\1"]', ex)
        out += f'    "{s}": {ex!r},\n'
    out += "}\n"
    out += "INPUT_NAMES = (" + "".join(f'"{s}", ' for s in T["inputs"]) + ")\n"
    out += "UNITS = {\n" + "".join(f'    "{n}": "{allu.get(n, "1")}",\n' for n in sorted(set(names) | set(T["inputs"]))) + "}\n\n"
    out += "# algebraic equations (name: expression of the other variables; L = line in subsystems.jl)\nEQ = {\n"
    for lhs, ex in T["eqs"].items():
        out += f'    "{lhs}": lambda v: {ex},  # L{T["lineno_eq"][lhs]}\n'
    out += "}\n\n# derivatives of the states (smooth!(x, input, T) is D(x) = (input - x) / T)\nDER = {\n"
    for s in T["states"]:
        out += f'    "{s}": lambda v: {T["ders"][s]},  # L{T["lineno_der"][s]}\n'
    out += "}\n"
    out += f'''

class {cls}(E4ASector):
    name = "e4a_{key}"
    SECTOR_KEY = "{key}"
    STATE_NAMES = STATE_NAMES
    PARAMS = PARAMS
    PARAMS_GL = PARAMS_GL
    PARAM_EXPR = PARAM_EXPR
    INITS = INITS
    STATE_INIT = STATE_INIT
    EQ = EQ
    DER = DER
    INPUT_NAMES = INPUT_NAMES
    inputs = {{n: UNITS[n] for n in INPUT_NAMES}}
    outputs = {{n: UNITS[n] for n in list(EQ) + list(STATE_NAMES)}}


SECTOR_CLASS = {cls}
'''
    # initial-value constants I_K are provided through PARAMS-like base: expose as parameters
    return out


if __name__ == "__main__":
    clone = Path(sys.argv[1])
    root = Path(__file__).resolve().parents[2]
    for key in sys.argv[2:]:
        T = translate(key, clone)
        for k, v in T["inits"].items():
            T["P"]["I_" + k] = v
        text = render(key, T, clone)
        (root / "f3" / "sectors" / f"e4a_{key}.py").write_text(text, encoding="utf-8", newline="\n")
        print(key, "states", len(T["states"]), "eqs", len(T["eqs"]), "inputs", T["inputs"])
