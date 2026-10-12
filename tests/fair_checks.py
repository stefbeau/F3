"""Helpers for the FaIR tests and the M2 report (docs/m2-step1-fair.md section 4). Reads HadCRUT5 from the pinned cache; stores nothing."""
from __future__ import annotations

import numpy as np
import pandas as pd

from f3.data import fair_inputs as fi
from f3.sectors.s6_climate import ClimateSetup, anomaly_on_bounds, run_fair

YEARS = np.arange(2015, 2025)


def hadcrut_rebased() -> pd.DataFrame:
    """HadCRUT5 annual best estimate and 95% limits, re-based to 1850-1900 (mean of the annual best estimates 1850 to 1900)."""
    fi.check_hadcrut()
    d = pd.read_csv(fi.cache_dir() / fi.HADCRUT_NAME)
    d.columns = ["year", "best", "lower", "upper"]
    d = d.set_index("year")
    base = d.loc[1850:1900, "best"].mean()
    return d - base


def fair_calendar_year(setup: ClimateSetup = ClimateSetup(), end: int = 2025) -> pd.DataFrame:
    """Per member calendar-year anomaly = mean of the time bounds at the start and end of the year (notebook method). Index: year."""
    f = run_fair(end, setup)
    a = anomaly_on_bounds(f)
    tb = np.asarray(f.timebounds)
    years = tb[:-1]
    cal = 0.5 * (a[:-1] + a[1:])
    return pd.DataFrame(cal, index=years)


def a21(setup: ClimateSetup = ClimateSetup()) -> dict:
    """A2.1 as fixed in docs/m2-step1-fair.md section 4: ensemble-mean FaIR 2015-2024 mean inside the mean HadCRUT5 95% interval."""
    obs = hadcrut_rebased()
    cal = fair_calendar_year(setup)
    em = cal.mean(axis=1)
    F = float(em.loc[2015:2024].mean())
    lo, hi = float(obs.loc[2015:2024, "lower"].mean()), float(obs.loc[2015:2024, "upper"].mean())
    return {"fair_mean_2015_2024": F, "obs_lower": lo, "obs_upper": hi, "obs_best": float(obs.loc[2015:2024, "best"].mean()),
            "passes": bool(lo <= F <= hi), "per_year": {int(y): {"fair_mean": float(em.loc[y]), "fair_p05": float(cal.loc[y].quantile(.05)),
                                                                   "fair_p95": float(cal.loc[y].quantile(.95)),
                                                                   "obs_best": float(obs.loc[y, "best"]), "obs_lower": float(obs.loc[y, "lower"]),
                                                                   "obs_upper": float(obs.loc[y, "upper"])} for y in YEARS}}
