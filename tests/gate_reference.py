"""Reads Epoch AI's shipped GATE runs from a pinned local copy of the playground bundle (D-026).

Nothing from the bundle is committed. The copy is found through the environment variable ``F3_GATE_BUNDLE`` (default:
``<repo>/.gate_cache/gate.js``, which is git-ignored). Its sha256 is checked before use: a missing copy means the
tests are skipped with a stated reason; a changed hash is a visible failure (``BundleChanged``). The reader is
``audit/t0/gate_playground_probe.py`` (``balanced``).
Reference values: Epoch AI, GATE playground (https://epoch.ai/gate), CC BY 4.0, read from the public page.
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


def bundle_path() -> Path:
    return Path(os.environ.get("F3_GATE_BUNDLE", REPO / ".gate_cache" / "gate.js"))


def bundle_available() -> bool:
    return bundle_path().is_file()


def skip_reason() -> str:
    return (f"GATE playground bundle not found at {bundle_path()} (set F3_GATE_BUNDLE, or download "
            f"https://epoch.ai/generated/gate.js there; D-026: never committed)")


def check_hash(path: Optional[Path] = None) -> str:
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


def load_runs() -> List[dict]:
    """The three shipped runs (hash checked first). Each: {'params': modelParams, 'states': [80 dicts]}."""
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
