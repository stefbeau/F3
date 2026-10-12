"""Write the small committed extract of the Global Carbon Budget 2025 (CC BY 4.0) used by the climate sector.

    uv run --group dev python audit/t0/gcb_extract.py <path to Global_Carbon_Budget_2025_v1.0.xlsx>

Source: Global Carbon Project (2026), Supplemental data of Global Carbon Budget 2025 (Version 1.0), https://doi.org/10.18160/gcp-2025,
ICOS Carbon Portal; Friedlingstein et al. (2026), ESSD 18, 3211-3288. Licence: CC BY 4.0 (ICOS data licence; derived products and
redistribution allowed with attribution). Sheet "Historical Budget", columns 'fossil emissions excluding carbonation' and
'land-use change emissions', GtC/yr; years 2015 to 2024. Checks the xlsx sha256 against the one recorded in research/SOURCES.md.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

SHA256 = "a928cf06c57576b66761d1fec8224c9a41a781eb63442afc03ba902858dd64a9"
OUT = Path(__file__).resolve().parents[2] / "f3" / "data" / "gcb2025_co2_2015_2024.csv"
HEADER = """# Global Carbon Budget 2025 v1.0, sheet 'Historical Budget', GtC/yr (billion tonnes of carbon per year); extract of years 2015 to 2024.
# Source: Global Carbon Project (2026). Supplemental data of Global Carbon Budget 2025 (Version 1.0). https://doi.org/10.18160/gcp-2025
#   ICOS Carbon Portal; Friedlingstein et al. (2026), Earth System Science Data 18, 3211-3288, https://doi.org/10.5194/essd-18-3211-2026
# Licence: CC BY 4.0 (ICOS data licence: derived products and redistribution allowed, attribution required).
# Source file sha256: %s
"""


def main(path: str) -> None:
    got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if got != SHA256:
        sys.exit(f"sha256 mismatch: expected {SHA256}, got {got}")
    d = pd.read_excel(path, "Historical Budget", header=None)
    hdr = d.index[d.iloc[:, 0].astype(str).str.contains("Year", na=False)][0]
    t = d.iloc[hdr + 1:].copy()
    t.columns = d.iloc[hdr]
    t = t.dropna(subset=["Year"])
    t = t[(t["Year"] >= 2015) & (t["Year"] <= 2024)]
    out = pd.DataFrame({"year": t["Year"].astype(int), "fossil_GtC": t["fossil emissions excluding carbonation"].astype(float),
                        "land_use_change_GtC": t["land-use change emissions"].astype(float)})
    OUT.write_text(HEADER % SHA256 + out.to_csv(index=False, float_format="%.9g", lineterminator="\n"), encoding="utf-8", newline="\n")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1])
