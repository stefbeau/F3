"""Pinned third-party inputs for the climate sector (M2 step 1; D-014 / D-026 pattern; docs/m2-step1-fair.md section 5).

The FaIR calibration files and the HadCRUT5 series are NOT committed. They are read from a local cache (``F3_FAIR_DATA``, default
``<repo>/.fair_cache``), each checked against the sha256 recorded here: a missing file means "skip with a stated reason", a changed
hash is a visible failure (``DataChanged``). ``fetch()`` downloads them from the pinned URLs. The Global Carbon Budget extract IS
committed (CC BY 4.0), see ``f3/data/gcb2025_co2_2015_2024.csv``.
"""

from __future__ import annotations

import hashlib
import os
import urllib.request
from pathlib import Path
from typing import Dict

REPO = Path(__file__).resolve().parents[2]
FAIR_COMMIT = "28572bb00e40d73f83f3365395fe8bc3a1b60bb9"
_FAIR_BASE = f"https://raw.githubusercontent.com/OMS-NetZero/FAIR/{FAIR_COMMIT}/examples/data/calibrated_constrained_ensemble/"
HADCRUT_URL = ("https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.2.0.0/analysis/diagnostics/"
               "HadCRUT.5.2.0.0.analysis.summary_series.global.annual.csv")

FAIR_FILES: Dict[str, str] = {
    "calibrated_constrained_parameters_calibration1.4.1.csv": "7b6c5d9fa0b0b0d3eb47189bf5d63cbf77e752ddac682947abee5ff529206780",
    "species_configs_properties_calibration1.4.1.csv": "42d04aa1a8f385cc53eae22beab26f857c535c5aa7dfdb98176d712bfc0c95a0",
    "volcanic_solar.csv": "621b551dafa6ff0e5a789b94a81a12876d796832c0e15f627545af40d6de58e5",
    "extensions_1750-2500.csv": "fcf994bb97bd08aae04bb4373ee7b8639e007f44055af1aa3d458aefc14b61ae",
}
HADCRUT_NAME = "HadCRUT.5.2.0.0.analysis.summary_series.global.annual.csv"
#: sha256 of the header line plus the data rows for years up to 2024 (the file gains a row each year, so the whole file is not pinned)
HADCRUT_HASH_THROUGH_2024 = "5e4395f05725fdf3f33b846f78884de4e471fb69b364f668891d69fb3f426931"
HADCRUT_LAST_PINNED_YEAR = 2024


class DataChanged(AssertionError):
    pass


def cache_dir() -> Path:
    return Path(os.environ.get("F3_FAIR_DATA", REPO / ".fair_cache"))


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def hadcrut_pinned_bytes(data: bytes) -> bytes:
    """Header plus rows for years <= 2024, with line endings normalised to LF."""
    lines = data.decode("utf-8").replace("\r\n", "\n").split("\n")
    keep = [lines[0]] + [l for l in lines[1:] if l and int(l.split(",")[0]) <= HADCRUT_LAST_PINNED_YEAR]
    return ("\n".join(keep) + "\n").encode("utf-8")


def check_fair_file(name: str) -> Path:
    path = cache_dir() / name
    got = _sha(path.read_bytes())
    if got != FAIR_FILES[name]:
        raise DataChanged(f"{name}: expected sha256 {FAIR_FILES[name]}, got {got}. The pinned FaIR calibration file changed; do not run "
                          f"comparisons until the change is read and recorded (docs/m2-step1-fair.md section 5).")
    return path


def check_hadcrut() -> Path:
    path = cache_dir() / HADCRUT_NAME
    got = _sha(hadcrut_pinned_bytes(path.read_bytes()))
    if got != HADCRUT_HASH_THROUGH_2024:
        raise DataChanged(f"HadCRUT5 rows up to {HADCRUT_LAST_PINNED_YEAR}: expected sha256 {HADCRUT_HASH_THROUGH_2024}, got {got}. The "
                          f"series was revised; read the HadCRUT5 release notes and record the new hash before running comparisons.")
    return path


def fair_available() -> bool:
    return all((cache_dir() / n).is_file() for n in FAIR_FILES)


def hadcrut_available() -> bool:
    return (cache_dir() / HADCRUT_NAME).is_file()


def skip_reason(what: str = "FaIR calibration files and HadCRUT5") -> str:
    return (f"{what} not found in {cache_dir()} (set F3_FAIR_DATA, or run `uv run python -m f3.data.fair_inputs` to download them; "
            f"D-014/D-026 pattern: never committed)")


def fetch() -> None:
    d = cache_dir()
    d.mkdir(parents=True, exist_ok=True)
    for name in FAIR_FILES:
        (d / name).write_bytes(urllib.request.urlopen(_FAIR_BASE + name, timeout=120).read())
        check_fair_file(name)
    (d / HADCRUT_NAME).write_bytes(urllib.request.urlopen(HADCRUT_URL, timeout=120).read())
    check_hadcrut()
    print(f"fetched and verified into {d}")


if __name__ == "__main__":
    fetch()
