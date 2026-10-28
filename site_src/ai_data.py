"""Data for the AI Impact page (ai.html), read at build time.

The OpenAlex counts come from the committed derived series audit/data/derived/openalex_ai_by_year_country.json (built by site_src/data_campaign.py from the
raw API responses, which are not in git), so the site builds on any machine. If that file is missing or unreadable every getter returns an empty list and the
page says so; the build never fails on it.

The Epoch and FDA counts are constants taken from the retrieval notes in audit/data/sources-register.json (their raw files are not in the repository).
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXTRACT = REPO / "audit" / "data" / "derived" / "openalex_ai_by_year_country.json"

# Register notes (sources-register.json, retrieved 2026-10-28): epoch_ai_compute "1083 data rows", span 1950-07-02 to 2026-10-12;
# fda_ai_devices "1614 devices", decisions 1995-2026, "Content current as of 2026-09-04".
EPOCH_MODELS, EPOCH_YEAR_MIN, EPOCH_YEAR_MAX = 1083, 1950, 2026
FDA_DEVICES, FDA_AS_OF = 1614, "2026-09-04"
OPENALEX_RETRIEVED = "2026-10-28"


def load_extract() -> dict:
    """The series' data block, or {} if the file is absent or malformed."""
    try:
        data = json.loads(EXTRACT.read_text(encoding="utf-8"))["data"]
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError, KeyError):
        return {}


def ai_stats(ex: dict) -> dict:
    by_year = ex.get("by_year", [])
    return {
        "epoch_models": EPOCH_MODELS, "epoch_year_min": EPOCH_YEAR_MIN, "epoch_year_max": EPOCH_YEAR_MAX,
        "oa_total": ex.get("total_works") or sum(r["count"] for r in by_year),
        "oa_year_min": by_year[0]["year"] if by_year else 2000, "oa_year_max": by_year[-1]["year"] if by_year else 2024,
        "fda_devices": FDA_DEVICES, "fda_as_of": FDA_AS_OF,
    }


def get_all() -> dict:
    ex = load_extract()
    return {"stats": ai_stats(ex), "by_year": ex.get("by_year", []), "by_country": ex.get("by_country", []),
            "country_groups_returned": ex.get("country_groups_returned", 0)}
