"""Reads Epoch AI's GATE reference runs for the S3 comparisons (D-026, D-063). Nothing from either source is committed.

Two sources, tried in this order:

1. **The playground bundle** (D-026): a pinned local copy named by ``F3_GATE_BUNDLE`` (default ``<repo>/.gate_cache/gate.js``,
   git-ignored), checked against its sha256. Its URL returned 404 on 2026-11-25 (D-026 outcome note); a copy that matches
   the pin still takes precedence if one is present. The reader is ``audit/t0/gate_playground_probe.py`` (``balanced``).
2. **The three preset runs Epoch sent** in November 2026 (D-063): ``default_run.json``, ``conservative_run.json`` and
   ``aggressive_run.json`` in the folder named by ``F3_GATE_RUNS`` (default ``<repo>/.gate_cache/runs``), each checked against
   the sha256 recorded in ``audit/gate-runs-identity.md``. Their identity with the shipped runs is supported by that
   report for the fields compared, not proven.

No source: the tests are skipped with a stated reason. A changed hash is a visible failure (``BundleChanged``).
Attribution: see ``attribution()``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

EXPECTED_SHA256 = "3afe8e4df5260ee062d987ce38a984fc37b488b6dcb5596a317b1fde106c55bf"
EXPECTED_BYTES = 3_167_570
REPO = Path(__file__).resolve().parents[1]
MESSAGE = ("The GATE playground bundle has changed since the hash recorded in D-026 (expected {exp}, got {got}). The reference "
           "runs may have changed. Re-read `research/gate-equations.md` sections 3 to 5, compare the three runs' parameter "
           "blocks and timing, and record the new hash by a dated note on D-026 before running comparisons.")

# stored run index -> setting name (D-005 amendment B)
SETTINGS = {"B0_default": 0, "B1_conservative": 1, "B2_aggressive": 2}


class BundleChanged(AssertionError):
    pass


#: D-063: the preset runs Epoch sent, in the order of the stored run index; sha256 from audit/gate-runs-identity.md
RUNS_FILES = ("default_run.json", "conservative_run.json", "aggressive_run.json")
RUNS_SHA256 = {
    "default_run.json": "bff0cbadf5f9fd8c0725cb4015d724a81aeccc547e9f252000a444d0ffb3e863",
    "conservative_run.json": "a36a022c68f9f444f91a785cc6ecae907d5360c5be771667f117f184a731f0f3",
    "aggressive_run.json": "968f48d2e8b525038bfd2d9a9c6559ffd85f2efdc1059fd07cc3e449cfe084be",
}
RUNS_MESSAGE = ("{name} in {folder} does not match the sha256 recorded for the runs Epoch sent (D-063; expected {exp}, got {got}). "
                "Do not update the hash: restore the file from the editor's copy of Epoch's attachment.")


def bundle_path() -> Path:
    return Path(os.environ.get("F3_GATE_BUNDLE", REPO / ".gate_cache" / "gate.js"))


def runs_dir() -> Path:
    return Path(os.environ.get("F3_GATE_RUNS", REPO / ".gate_cache" / "runs"))


def source() -> Optional[str]:
    """"bundle" (D-026), "runs" (D-063) or None. The bundle takes precedence when a copy is present."""
    if bundle_path().is_file():
        return "bundle"
    if all((runs_dir() / n).is_file() for n in RUNS_FILES):
        return "runs"
    return None


def bundle_available() -> bool:
    """True when either reference source is present (the name is kept for the existing skip marks)."""
    return source() is not None


def skip_reason() -> str:
    return (f"no GATE reference found: neither the playground bundle at {bundle_path()} (F3_GATE_BUNDLE; its URL returned 404 on "
            f"2026-11-25, D-026) nor the three preset runs Epoch sent in {runs_dir()} (F3_GATE_RUNS, D-063); never committed")


def attribution() -> str:
    if source() == "runs":
        return ("Reference values: Epoch AI, GATE runs produced with Epoch's solver and sent to the editor in November 2026 "
                "(D-063; identity with the shipped playground runs supported by audit/gate-runs-identity.md, not proven; "
                "the shipped bundle is no longer available)")
    return "Reference values: Epoch AI, GATE playground (https://epoch.ai/gate), CC BY 4.0, read from the public page"


def check_hash(path: Optional[Path] = None) -> str:
    """Checks the source in use (or the bundle at ``path``). Returns the bundle's hash, or the three run hashes joined."""
    if path is None and source() == "runs":
        got_all = []
        for n in RUNS_FILES:
            got = hashlib.sha256((runs_dir() / n).read_bytes()).hexdigest()
            if got != RUNS_SHA256[n]:
                raise BundleChanged(RUNS_MESSAGE.format(name=n, folder=runs_dir(), exp=RUNS_SHA256[n], got=got))
            got_all.append(got)
        return " ".join(got_all)
    path = path or bundle_path()
    data = path.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != EXPECTED_SHA256 or len(data) != EXPECTED_BYTES:
        raise BundleChanged(MESSAGE.format(exp=EXPECTED_SHA256, got=got))
    return got


def _probe():
    spec = importlib.util.spec_from_file_location("gate_playground_probe", REPO / "audit" / "t0" / "gate_playground_probe.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CACHE: Dict[str, list] = {}


def _runs_from_folder() -> List[dict]:
    """The runs Epoch sent, in the bundle's shape: each ``<name>_path`` series of 80 scalars becomes field ``<name>``."""
    out = []
    for n in RUNS_FILES:
        raw = json.loads((runs_dir() / n).read_text(encoding="utf-8"))
        series = {k[:-5]: v for k, v in raw.items()
                  if k.endswith("_path") and isinstance(v, list) and len(v) == 80 and not isinstance(v[0], list)}
        out.append({"params": None, "states": [{k: v[i] for k, v in series.items()} for i in range(80)]})
    return out


def load_runs() -> List[dict]:
    """The three reference runs (hash checked first). Each: {'params': modelParams or None, 'states': [80 dicts]}."""
    src = source()
    if src == "runs":
        key = "runs:" + str(runs_dir())
        if key not in _CACHE:
            check_hash()
            _CACHE[key] = _runs_from_folder()
        return _CACHE[key]
    path = bundle_path()
    key = str(path)
    if key not in _CACHE:
        check_hash(path)
        probe = _probe()
        text = path.read_text(encoding="utf-8", errors="replace")
        cache = json.loads(probe.balanced(text, text.index("[", text.find("// legacy/one-offs/gate/backend/cache.json")), "[", "]"))
        _CACHE[key] = [{"params": e["args"]["modelParams"], "states": e["run"]["world_path"]["states"]} for e in cache]
    return _CACHE[key]


def field(run: dict, name: str, n: int = 76) -> np.ndarray:
    """Stored field by name, indices 0..n-1 (index k = end of 2025 + k)."""
    return np.array([s[name] for s in run["states"][:n]], dtype=float)


def investment_shares(run: dict, n: int = 80) -> Dict[str, np.ndarray]:
    names = ("q_consumption", "q_compute", "q_capital", "q_hardware_rnd", "q_software_rnd", "q_training_compute")
    return {k: field(run, k, n) for k in names}
