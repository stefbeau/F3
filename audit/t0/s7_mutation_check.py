"""D-050 item 4: show that each S7 test can FAIL on the real module. Breaks the module's equations one at a time (text replacement that must
match exactly once), runs the named test in a fresh subprocess with a fresh bytecode cache (so a same-size edit can never reuse a stale .pyc),
and requires FAIL under the mutation and PASS on the unmodified module. Always restores the module (checked byte for byte).

    set PYTHONUTF8=1
    uv run --group dev python audit/t0/s7_mutation_check.py

Prints a table; writes nothing else. A MISSED mutation means the test does not isolate that effect: it is reported, never hidden.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "f3" / "sectors" / "s7_social.py"
MAIN_TESTS = "tests/test_s7_social.py"
POSTHOC_TESTS = "tests/test_s7_social_posthoc.py"
ORIG = SRC.read_bytes()


def run(test_file: str, k: str) -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as cache:
        env = {**os.environ, "PYTHONUTF8": "1", "PYTHONPYCACHEPREFIX": cache, "PYTHONDONTWRITEBYTECODE": "1"}
        r = subprocess.run([sys.executable, "-m", "pytest", test_file, "-q", "--no-header", "-p", "no:cacheprovider", "-k", k, "-x"],
                           capture_output=True, text=True, cwd=REPO, env=env)
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    return ("PASS" if r.returncode == 0 else "FAIL"), (lines[-1] if lines else r.stderr[-80:])


I_CLIP = 'I_t = _clip(p["I0"] + p["gI_LS"] * lsp + p["gI_UE"] * uep - p["gI_R"] * R, *self.I_BOUNDS)'
I_FINAL = "self._state = (_clip(new[0], *self.I_BOUNDS), _clip(new[1], 0.0, 1.0)"
# (label, [(old, new), ...], test file, -k selector)
MUT = [
    ("R2: labour-share pressure never feeds inequality (the pre-registered mutation)", [('p["gI_LS"] * lsp', "0.0 * lsp")], MAIN_TESTS, "test_r2_automation"),
    ("R2: inequality does not raise tension", [('p["gTe_I"] * (I - p["I0"])', '0.0 * (I - p["I0"])')], MAIN_TESTS, "test_r2_automation"),
    ("R2: tension does not lower well-being", [('p["gW_Te"] * (Te - p["Te0"])', '0.0 * (Te - p["Te0"])')], MAIN_TESTS, "test_r2_automation"),
    ("B5: policy response never starts (the pre-registered mutation, kP = 0)", [('P_t = _clip(p["kP"] * max(Te - p["Te_threshold"], 0.0), 0.0, 1.0)', "P_t = 0.0")], MAIN_TESTS, "test_b5_policy"),
    ("B5: no delay (tau_P tiny)", [('p["tau_P"])', "1e-9)")], MAIN_TESTS, "test_b5_policy"),
    ("B5: policy does not reduce inequality", [("R = red + P", "R = red")], MAIN_TESTS, "test_b5_policy"),
    ("S1: warming has no effect", [('ts = _clip(warming / p["TSref"], 0.0, 2.0) / 2.0', "ts = 0.0")], MAIN_TESTS, "test_s1_warming"),
    ("S2: redistribution has no effect", [("R = red + P", "R = P")], MAIN_TESTS, "test_s2_redistribution"),
    ("S3: growth has no effect", [('+ p["gW_g"] * _clip(growth / p["gref"], -1.0, 1.0)', "+ 0.0")], MAIN_TESTS, "test_s3_growth"),
    ("S4: unemployment has no effect", [('uep = _clip(ue / p["UEmax"], 0.0, 1.0)', "uep = 0.0")], MAIN_TESTS, "test_s4_unemployment"),
    ("B-bounds: ONE of the two inequality clips removed (redundant by design)", [(I_CLIP, 'I_t = p["I0"] + 50.0 * (p["gI_LS"] * lsp + p["gI_UE"] * uep - p["gI_R"] * R)')], MAIN_TESTS, "test_b2_extreme"),
    ("B-bounds: BOTH inequality clips removed", [(I_CLIP, 'I_t = p["I0"] + 50.0 * (p["gI_LS"] * lsp + p["gI_UE"] * uep - p["gI_R"] * R)'),
                                                  (I_FINAL, "self._state = (new[0], _clip(new[1], 0.0, 1.0)")], MAIN_TESTS, "test_b2_extreme"),
    ("E1: the start is not a fixed point (tension offset)", [('Te_t = _clip(p["Te0"] + ', 'Te_t = _clip(p["Te0"] + 0.05 + ')], MAIN_TESTS, "test_e1"),
]
# the post-hoc, stricter tests (tests/test_s7_social_posthoc.py) against the mutations the main tests missed
POST = [
    ("R2 link: inequality does not raise tension", MUT[1][1], POSTHOC_TESTS, "test_link_signs"),
    ("R2 link: tension does not lower well-being", MUT[2][1], POSTHOC_TESTS, "test_link_signs"),
    ("B5: no delay (tau_P tiny)", MUT[4][1], POSTHOC_TESTS, "test_policy_response_lags_its_own_target"),
]


def main() -> None:
    assert SRC.read_bytes() == ORIG
    rows = []
    try:
        for title, group in (("MAIN TESTS (pre-registered)", MUT), ("POST-HOC TESTS (added after the results above; labelled)", POST)):
            base = {}
            for entry in group:
                tf, k = entry[2], entry[3]
                if (tf, k) not in base:
                    base[(tf, k)] = run(tf, k)
            print(f"\n== {title}\nunmodified module: " + "; ".join(f"{k[1]} {v[0]}" for k, v in base.items()))
            caught = 0
            for entry in group:
                label, edits, tf, k = entry
                text = ORIG.decode("utf-8")
                for old, new in edits:
                    assert text.count(old) == 1, (label, old, text.count(old))
                    text = text.replace(old, new)
                SRC.write_bytes(text.encode("utf-8"))
                status, last = run(tf, k)
                caught += status == "FAIL"
                print(("CAUGHT  " if status == "FAIL" else "MISSED  ") + label + f"   [{k}] {last[:60]}")
            print(f"caught {caught} of {len(group)}")
    finally:
        SRC.write_bytes(ORIG)
    print("\nmodule restored byte for byte:", SRC.read_bytes() == ORIG)


if __name__ == "__main__":
    main()
