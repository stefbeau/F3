"""D-058: rebuild the derived data series of the data retrieval campaign from the raw folder and verify checksums against the register.

Usage
    python -I site_src/data_campaign.py <raw dir> [--out audit/data/derived] [--only name1,name2] [--list] [--verify-only]
    F3_DATA_RAW=<raw dir> python -I site_src/data_campaign.py

The raw folder is NOT in the repository (downloads stay outside it). It must hold one directory per source, exactly as written by
audit/t0/data_campaign_fetch.py. Before any series is built, every raw file it reads is hashed and compared with the sha256 recorded in
audit/data/sources-register.json; a mismatch stops the build (the data changed, read what changed before using it).

Licence rule enforced in code: a series is only built from sources whose register entry says redistribution "yes" with a verified licence quote.
Series from other sources are never written to the repository. Series that need pdftotext (PDF tables) skip, with a message, if it is not installed.

Nothing here executes downloaded files; PDFs are read as text by pdftotext, spreadsheets by openpyxl, archives by zipfile.
Output is deterministic (no timestamps): the same raw files give byte-identical JSON.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
REGISTER = REPO / "audit" / "data" / "sources-register.json"
DEFAULT_OUT = REPO / "audit" / "data" / "derived"
RETRIEVAL_DATE = "2026-10-22"


class ChecksumError(AssertionError):
    pass


class Skip(Exception):
    """Raised by a builder that cannot run here (a tool or file is missing); the message says why."""


# ------------------------------------------------------------------------------------------------------------------ register and files
class Ctx:
    def __init__(self, raw: Path):
        self.raw = raw
        self.reg = json.loads(REGISTER.read_text(encoding="utf-8"))
        self.sources = {s["id"]: s for s in self.reg["sources"]}
        self.files = {f["path"]: f for s in self.reg["sources"] for f in s["files"]}
        self._ok: set[str] = set()
        self._pdf_text: dict[str, list[str]] = {}

    def path(self, rel: str) -> Path:
        return self.raw / rel

    def verify(self, rel: str) -> Path:
        if rel not in self.files:
            raise ChecksumError(f"{rel} is not in the register")
        p = self.raw / rel
        if not p.is_file():
            raise Skip(f"raw file missing: {rel}")
        if rel not in self._ok:
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            if h.hexdigest() != self.files[rel]["sha256"]:
                raise ChecksumError(f"{rel}: sha256 {h.hexdigest()} differs from the register ({self.files[rel]['sha256']})")
            self._ok.add(rel)
        return p

    def zip_csv(self, rel: str, member: str, **kw) -> pd.DataFrame:
        p = self.verify(rel)
        with zipfile.ZipFile(p) as z:
            return pd.read_csv(io.BytesIO(z.read(member)), **kw)

    def zip_text(self, rel: str, member: str) -> str:
        p = self.verify(rel)
        with zipfile.ZipFile(p) as z:
            return z.read(member).decode("utf-8", "replace")

    def pdf_pages(self, rel: str) -> list[str]:
        """Text of each page (pdftotext -raw); the raw mode keeps table rows together, the layout mode interleaves columns."""
        if rel not in self._pdf_text:
            p = self.verify(rel)
            exe = shutil.which("pdftotext")
            if not exe:
                raise Skip("pdftotext not installed")
            out = subprocess.run([exe, "-raw", str(p), "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
            self._pdf_text[rel] = out.split("\f")
        return self._pdf_text[rel]


def r(x, n=4):
    """Round for stable output; NaN and inf become None."""
    if x is None:
        return None
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(x) or math.isinf(x):
        return None
    return round(x, n)


def ri(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else int(round(float(x)))


# ------------------------------------------------------------------------------------------------------------------ series registry
BUILDERS: dict[str, dict] = {}


def series(name, *, title, description, sources, files, units, geography, time_span, variables, supports, method, caveats=(), attribution=None, needs_pdf=False):
    def deco(fn):
        BUILDERS[name] = dict(fn=fn, title=title, description=description, sources=list(sources), files=list(files), units=units, geography=geography,
                              time_span=time_span, variables=list(variables), supports=list(supports), method=method, caveats=list(caveats),
                              attribution=attribution, needs_pdf=needs_pdf)
        return fn
    return deco


def build_one(ctx: Ctx, name: str) -> dict:
    b = BUILDERS[name]
    for sid in b["sources"]:
        s = ctx.sources.get(sid)
        if s is None:
            raise ChecksumError(f"{name}: source {sid} not in the register")
        if s["redistribution"] != "yes" or not s["licence"].get("quote_verified"):
            raise ChecksumError(f"{name}: source {sid} is not redistributable with a verified licence quote (redistribution={s['redistribution']}); refusing to build")
    for rel in b["files"]:
        ctx.verify(rel)
    data = b["fn"](ctx)
    doc = {
        "id": name, "title": b["title"], "description": b["description"], "built_by": "site_src/data_campaign.py", "register": "audit/data/sources-register.json",
        "sources": [{"id": sid, "title": ctx.sources[sid]["title"], "version": ctx.sources[sid]["version"], "url": ctx.sources[sid]["url"],
                     "licence": ctx.sources[sid]["licence"]["name"], "licence_quote": ctx.sources[sid]["licence"]["quote"],
                     "redistribution": ctx.sources[sid]["redistribution"]} for sid in b["sources"]],
        "source_files": [{"path": rel, "sha256": ctx.files[rel]["sha256"], "bytes": ctx.files[rel]["bytes"]} for rel in b["files"]],
        "retrieved": RETRIEVAL_DATE, "redistribution": "yes",
        "attribution": b["attribution"] or "; ".join(f"{ctx.sources[sid]['publisher']}: {ctx.sources[sid]['title']}" for sid in b["sources"]),
        "units": b["units"], "geography": b["geography"], "time_span": b["time_span"], "variables": b["variables"], "supports": b["supports"],
        "method": b["method"], "caveats": b["caveats"], "data": data,
    }
    return doc


def write_json(path: Path, doc: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def ols_growth(years, values):
    """Least-squares slope of log10(values) on years: returns (factor per year, doubling time in years, n) or None."""
    y = np.log10(np.asarray(values, float))
    x = np.asarray(years, float)
    if len(x) < 3:
        return None
    slope, intercept = np.polyfit(x, y, 1)
    return {"factor_per_year": r(10 ** slope, 4), "doubling_time_years": r(math.log10(2) / slope, 3) if slope > 0 else None, "n_points": int(len(x))}


# ====================================================================================================================== D1 AI compute and hardware
EPOCH_ATTR = "Epoch AI, https://epoch.ai/data (CC BY); values re-expressed as annual aggregates by F3."


@series("epoch_training_compute_by_year",
        title="Training compute of notable AI models by publication year (Epoch AI)",
        description="Per publication year: number of notable models with a compute estimate, maximum, median and counts above 1e23 to 1e26 FLOP; the ten largest training runs; log-linear growth of the annual maximum.",
        sources=["epoch_ai_models"], files=["epoch_ai_models/ai_models.zip"], units="FLOP (floating-point operations of the training run)", geography="global",
        time_span="2010 to 2026 (publication dates up to 2026-09-30)", variables=["n_models", "max_flop", "median_flop", "counts above thresholds", "top_10"],
        supports=["AI", "L5", "DC"], attribution=EPOCH_ATTR,
        method="Rows of notable_ai_models.csv with a numeric 'Training compute (FLOP)' and a parseable publication date; grouped by calendar year. Growth: ordinary least squares of log10(annual maximum) on year, 2016-2025 (a description of the annual maxima, not a forecast).",
        caveats=["Compute is Epoch's estimate; its 'Confidence' column grades each row (the file's own text says the estimate can be off by a factor 2, more for undisclosed models).",
                 "The maximum is a single model and moves in jumps; the growth factor is sensitive to the window."])
def b_epoch_compute(ctx: Ctx):
    m = ctx.zip_csv("epoch_ai_models/ai_models.zip", "notable_ai_models.csv")
    c = "Training compute (FLOP)"
    m["date"] = pd.to_datetime(m["Publication date"], errors="coerce")
    m = m.dropna(subset=[c, "date"]).copy()
    m["year"] = m["date"].dt.year
    rows = []
    for y, g in m.groupby("year"):
        v = g[c].astype(float)
        rows.append({"year": int(y), "n_models": int(len(v)), "max_flop": float(v.max()), "median_flop": float(v.median()),
                     "n_ge_1e23": int((v >= 1e23).sum()), "n_ge_1e24": int((v >= 1e24).sum()), "n_ge_1e25": int((v >= 1e25).sum()), "n_ge_1e26": int((v >= 1e26).sum())})
    top = m.sort_values(c, ascending=False).head(10)
    top10 = [{"model": str(t["Model"]), "organization": str(t["Organization"]), "date": t["date"].strftime("%Y-%m-%d"), "flop": float(t[c]), "confidence": None if pd.isna(t["Confidence"]) else str(t["Confidence"])}
             for _, t in top.iterrows()]
    w = [x for x in rows if 2016 <= x["year"] <= 2025]
    return {"by_year": rows, "top_10": top10, "annual_max_growth_2016_2025": ols_growth([x["year"] for x in w], [x["max_flop"] for x in w])}


@series("epoch_ai_chip_stock_quarterly",
        title="Cumulative AI chip sales by quarter: H100-equivalents and thermal design power (Epoch AI)",
        description="Sum over chip types of Epoch's cumulative sales estimates at each quarter end, 2022-Q1 to 2026-Q3: H100e compute, TDP of the chips (GW) and units; by manufacturer for the latest quarter.",
        sources=["epoch_ai_chip_sales"], files=["epoch_ai_chip_sales/ai_chip_sales.zip"], units="H100-equivalents; GW (chip TDP); units", geography="global",
        time_span="2022-03-31 to 2026-09-30 (quarter ends)", variables=["h100e_median_sum", "tdp_gw_median_sum", "units_median_sum"], supports=["AI", "L5", "DC"], attribution=EPOCH_ATTR,
        method="File cumulative_timelines.csv has one row per chip type and quarter, cumulative from the chip's first sale. Medians are summed over chip types per end date. Percentiles are NOT summed (percentiles do not add), so the sums are sums of medians, close to the mean but not a median of the total.",
        caveats=["Cumulative sales, not installed base: retirements and stranded chips are not modelled.", "Rows flagged 'Incomplete' (a chip with partial data) are counted in n_incomplete_rows.",
                 "TDP is chip power only; it excludes servers, networking, cooling and PUE, so it is a lower bound on facility power."])
def b_epoch_chips(ctx: Ctx):
    d = ctx.zip_csv("epoch_ai_chip_sales/ai_chip_sales.zip", "cumulative_timelines.csv")
    d["end"] = pd.to_datetime(d["End date"])
    inc = d["Incomplete"].fillna("").astype(str).str.strip().ne("")
    out = []
    for e, g in d.groupby("end"):
        out.append({"quarter_end": e.strftime("%Y-%m-%d"), "h100e_median_sum": ri(g["H100e compute power (median)"].sum()), "tdp_gw_median_sum": r(g["Total TDP (W) (median)"].sum() / 1e9, 4),
                    "units_median_sum": ri(g["Number of units (median)"].sum()), "n_chip_types": int(g["Chip type"].nunique()), "n_incomplete_rows": int(inc[g.index].sum())})
    last = d[d["end"] == d["end"].max()]
    by_m = []
    for mf, g in last.groupby("Chip manufacturer"):
        by_m.append({"manufacturer": str(mf), "h100e_median_sum": ri(g["H100e compute power (median)"].sum()), "tdp_gw_median_sum": r(g["Total TDP (W) (median)"].sum() / 1e9, 4)})
    by_m.sort(key=lambda x: -(x["h100e_median_sum"] or 0))
    return {"by_quarter_end": out, "latest_quarter_by_manufacturer": by_m}


@series("epoch_data_centers_summary",
        title="Frontier AI data centres: current power and capacity timeline (Epoch AI)",
        description="95 tracked AI data centres: current power and H100e by country, and the sum over centres of power (MW) and H100e at each year end 2023-2030, using each centre's latest dated timeline entry on or before the date.",
        sources=["epoch_data_centers"], files=["epoch_data_centers/data_centers.zip"], units="MW; H100-equivalents; million gallons per day (water)", geography="global (tracked sites)",
        time_span="2018-12 to 2030-12 (dates after 2026-10-22 are Epoch projections)", variables=["current_power_mw", "current_h100e", "power_mw_at_year_end", "h100e_at_year_end"], supports=["DC", "L5", "AI"], attribution=EPOCH_ATTR,
        method="data_centers.csv: sum of 'Current power (MW)' and 'Current H100 equivalents' by country. data_center_timelines.csv: for each date D, each centre contributes its row with the latest Date <= D (its own construction timeline); centres without a row by D contribute nothing. Water use (MGD) is only partly filled, so only the number of centres with a value is reported.",
        caveats=["Covers the large AI-focused sites Epoch tracks, not the world's data-centre fleet: it is a lower bound on AI capacity and an unrelated scope to the IEA's all-data-centre figures.",
                 "Rows dated after the retrieval date are projections from permits and construction status.", "Power (MW) is facility power as modelled by Epoch.",
                 "Water use (MGD) is filled for only 9 to 20 of the sites at any date and the sum jumped between dates for that reason, so no water sum is published; only the count of sites with a value is."])
def b_epoch_dc(ctx: Ctx):
    cur = ctx.zip_csv("epoch_data_centers/data_centers.zip", "data_centers.csv")
    tl = ctx.zip_csv("epoch_data_centers/data_centers.zip", "data_center_timelines.csv")
    cur["Country"] = cur["Country"].fillna("Unknown")
    by_c = []
    for c, g in cur.groupby("Country"):
        by_c.append({"country": str(c), "n_sites": int(len(g)), "current_power_mw": r(g["Current power (MW)"].sum(), 1), "current_h100e": ri(g["Current H100 equivalents"].sum())})
    by_c.sort(key=lambda x: -(x["current_power_mw"] or 0))
    tl["d"] = pd.to_datetime(tl["Date"])
    ye = []
    for y in range(2023, 2031):
        cut = pd.Timestamp(f"{y}-12-31")
        g = tl[tl["d"] <= cut].sort_values("d").groupby("Data center").tail(1)
        wv = g["Water use (MGD)"].dropna()
        ye.append({"date": cut.strftime("%Y-%m-%d"), "projected": bool(cut > pd.Timestamp(RETRIEVAL_DATE)), "n_sites_with_entry": int(len(g)),
                   "power_mw": r(g["Power (MW)"].sum(), 1), "it_power_mw": r(g["IT power (MW)"].sum(), 1), "h100e": ri(g["H100 equivalents"].sum()),
                   "n_sites_with_water_value": int(len(wv))})
    return {"current_total_power_mw": r(cur["Current power (MW)"].sum(), 1), "current_total_h100e": ri(cur["Current H100 equivalents"].sum()), "n_sites": int(len(cur)),
            "current_by_country": by_c, "at_year_end": ye}


@series("epoch_hardware_efficiency",
        title="AI accelerator energy efficiency by release year: tensor FLOP/s per watt (Epoch AI)",
        description="For each release year: best and median of (tensor FP16/BF16 FLOP/s divided by TDP in W), i.e. FLOP per joule at peak, over GPUs, TPUs and other accelerators in Epoch's hardware table; log-linear growth of the best.",
        sources=["epoch_ml_hardware"], files=["epoch_ml_hardware/ml_hardware.zip"], units="FLOP per joule (peak tensor FP16/BF16 FLOP/s per W of TDP)", geography="global", time_span="2016 to 2026 (release dates)",
        variables=["best_flop_per_joule", "median_flop_per_joule", "n_chips", "best_chip"], supports=["L5", "DC", "AI"], attribution=EPOCH_ATTR,
        method="ml_hardware.csv rows with both 'Tensor-FP16/BF16 performance (FLOP/s)' and 'TDP (W)'; efficiency = performance / TDP. Grouped by release year. Growth = OLS of log10(best) on year over 2016-2025.",
        caveats=["Peak datasheet efficiency at 16-bit precision, not delivered FLOP per joule of a training run (utilisation, memory, networking and PUE reduce it by roughly an order of magnitude; the module's eta_0 is a delivered-compute figure, units differ).",
                 "Newer chips quote FP8/FP4 peaks that are not used here."])
def b_epoch_hw(ctx: Ctx):
    h = ctx.zip_csv("epoch_ml_hardware/ml_hardware.zip", "ml_hardware.csv")
    pc, tc = "Tensor-FP16/BF16 performance (FLOP/s)", "TDP (W)"
    h["date"] = pd.to_datetime(h["Release date"], errors="coerce")
    h = h.dropna(subset=[pc, tc, "date"]).copy()
    h = h[(h[tc] > 0) & (h[pc] > 0)]
    h["eff"] = h[pc] / h[tc]
    h["year"] = h["date"].dt.year
    rows = []
    for y, g in h.groupby("year"):
        b = g.sort_values("eff", ascending=False).iloc[0]
        rows.append({"year": int(y), "n_chips": int(len(g)), "best_flop_per_joule": float(b["eff"]), "best_chip": str(b["Hardware name"]), "median_flop_per_joule": float(g["eff"].median())})
    w = [x for x in rows if 2016 <= x["year"] <= 2025]
    return {"by_release_year": rows, "best_growth_2016_2025": ols_growth([x["year"] for x in w], [x["best_flop_per_joule"] for x in w])}


@series("epoch_gpu_clusters_by_year",
        title="Largest GPU clusters and supercomputers by year of first operation (Epoch AI, to 2025-07)",
        description="Per year of first operational date: number of clusters in the dataset, largest H100-equivalents, largest power capacity (MW), largest 16-bit OP/s.",
        sources=["epoch_gpu_clusters"], files=["epoch_gpu_clusters/gpu_clusters.csv"], units="H100-equivalents; MW; OP/s", geography="global", time_span="2010 to 2025", variables=["n_clusters", "max_h100e", "max_power_mw", "max_16bit_ops"],
        supports=["AI", "DC"], attribution=EPOCH_ATTR,
        method="gpu_clusters.csv, rows with a parseable 'First Operational Date'; grouped by calendar year; maxima over clusters (power uses 'Power Capacity (MW)').",
        caveats=["Legacy dataset (last update 2026-03-13); 2025 coverage ends in July.", "Reported and calculated power differ; the reported column is used where present."])
def b_epoch_clusters(ctx: Ctx):
    g = pd.read_csv(ctx.verify("epoch_gpu_clusters/gpu_clusters.csv"))
    g["d"] = pd.to_datetime(g["First Operational Date"], errors="coerce")
    g = g.dropna(subset=["d"]).copy()
    g["year"] = g["d"].dt.year
    rows = []
    for y, x in g.groupby("year"):
        rows.append({"year": int(y), "n_clusters": int(len(x)), "max_h100e": r(x["H100 equivalents"].max(), 1), "max_power_mw": r(x["Power Capacity (MW)"].max(), 2), "max_16bit_ops": r(x["16-bit OP/s"].max(), 0)})
    return {"by_year": rows}


@series("epoch_ai_company_revenue",
        title="Annualized revenue reports of AI companies (Epoch AI)",
        description="All revenue reports with an annualized revenue figure: company, date, annualized revenue in USD, type of figure, confidence.",
        sources=["epoch_ai_companies"], files=["epoch_ai_companies/ai_companies.zip"], units="USD per year (annualized)", geography="global (companies)", time_span="2022 to 2026", variables=["company", "date", "annualized_revenue_usd", "confidence"],
        supports=["AI", "L4"], attribution=EPOCH_ATTR,
        method="ai_companies_revenue_reports.csv: rows with 'Annualized revenue (USD)' and a date, sorted by company and date. Source columns are not copied.",
        caveats=["Annualized run-rate figures from press and company statements, not audited revenue; Epoch's confidence column is kept."])
def b_epoch_rev(ctx: Ctx):
    d = ctx.zip_csv("epoch_ai_companies/ai_companies.zip", "ai_companies_revenue_reports.csv")
    d = d.dropna(subset=["Annualized revenue (USD)", "Date"]).copy()
    d["date"] = pd.to_datetime(d["Date"], errors="coerce")
    d = d.dropna(subset=["date"]).sort_values(["Company", "date"])
    rows = [{"company": str(t["Company"]), "date": t["date"].strftime("%Y-%m-%d"), "annualized_revenue_usd": float(t["Annualized revenue (USD)"]),
             "confidence": None if pd.isna(t["Confidence"]) else str(t["Confidence"])} for _, t in d.iterrows()]
    return {"reports": rows, "n_companies": int(d["Company"].nunique())}


@series("openalex_ai_by_year_country",
        title="Publications tagged Artificial intelligence by year and by country (OpenAlex)",
        description="Number of OpenAlex works tagged with the concept Artificial intelligence per publication year 2000-2024, and the 15 countries with the most such works by authors' institutions.",
        sources=["openalex_ai_publications"], files=["openalex_ai_publications/by_year.json", "openalex_ai_publications/by_country.json"], units="works (publications)", geography="global; by country of authors' institutions",
        time_span="2000 to 2024 (publication years)", variables=["by_year", "by_country", "total_works"], supports=["AI"],
        attribution="OpenAlex (OurResearch), https://openalex.org (CC0 1.0); counts re-expressed as annual and per-country aggregates by F3. Retrieved 2026-10-28.",
        method="by_year.json and by_country.json are OpenAlex group_by responses for concept C154945302 and publication years 2000-2024. Years are sorted; countries are sorted by count and cut at 15. The response's own total (meta.count) is kept as total_works.",
        caveats=["Counts are of works that OpenAlex tags with the concept, not a share of all research and not a measure of quality or impact.",
                 "A work with authors at institutions in several countries is counted once in each country, so country counts overlap; the country response is truncated at 200 groups and its counts sum to less than total_works.",
                 "The file is retrieved 2026-10-28; the 'retrieved' field of this series is the campaign's build date."])
def b_openalex(ctx: Ctx):
    by_year = json.loads(ctx.verify("openalex_ai_publications/by_year.json").read_text(encoding="utf-8"))
    by_country = json.loads(ctx.verify("openalex_ai_publications/by_country.json").read_text(encoding="utf-8"))
    years = sorted(({"year": int(g["key"]), "count": int(g["count"])} for g in by_year["group_by"]), key=lambda x: x["year"])
    groups = by_country["group_by"]
    top = sorted(groups, key=lambda g: (-g["count"], g["key"]))[:15]
    return {"total_works": int(by_year["meta"]["count"]), "country_groups_returned": len(groups), "country_groups_sum": int(sum(g["count"] for g in groups)),
            "by_year": years, "by_country": [{"code": g["key"].rsplit("/", 1)[-1], "country": g["key_display_name"], "count": int(g["count"])} for g in top]}


# ====================================================================================================================== D2 electricity
EMBER_AREAS = ["World", "United States of America", "China", "India", "EU", "Ireland", "Netherlands", "Singapore", "Japan", "Germany", "United Kingdom", "Malaysia", "South Korea", "Sweden", "Norway", "Canada"]


@series("ember_electricity_world",
        title="Electricity demand, generation, capacity, emissions and CO2 intensity: world, major regions and data-centre hubs (Ember)",
        description="Annual 2000-2025 series for World, United States, China, India, EU, Ireland, Netherlands, Singapore, Japan, Germany, United Kingdom, Malaysia, South Korea, Sweden, Norway and Canada: demand (TWh), total generation, generation by fuel (TWh), capacity by fuel (GW), power-sector emissions (MtCO2) and CO2 intensity (gCO2/kWh).",
        sources=["ember_yearly"], files=["ember_yearly/yearly_full_release_long_format.csv"], units="TWh; GW; MtCO2; gCO2/kWh", geography="World and 15 areas", time_span="2000 to 2025",
        variables=["demand_twh", "generation_total_twh", "generation_by_fuel_twh", "capacity_by_fuel_gw", "emissions_total_mtco2", "co2_intensity_g_per_kwh"], supports=["L5", "L6", "L7", "DC"],
        attribution="Ember, Yearly electricity data, https://ember-energy.org/data/yearly-electricity-data/ (CC BY 4.0); selected areas and variables, reshaped by F3.",
        method="Rows of yearly_full_release_long_format.csv for the listed areas; each variable becomes an array aligned to the list of years (null where the file has no value).",
        caveats=["The file follows Ember's older download format; Ember announced a new format in July 2026 (see ember_release_global in the register). World demand 2024 differs by 0.0 TWh between the two in the cross-check, see register cross_checks.",
                 "Ember demand = generation + net imports, a different scope from the IEA's end-use electricity statistics."])
def b_ember(ctx: Ctx):
    d = pd.read_csv(ctx.verify("ember_yearly/yearly_full_release_long_format.csv"), usecols=["Area", "Year", "Category", "Subcategory", "Variable", "Unit", "Value"])
    d = d[d.Area.isin(EMBER_AREAS)]
    out = {}
    for area in EMBER_AREAS:
        a = d[d.Area == area]
        years = sorted(int(y) for y in a.Year.unique())
        def arr(cat, sub, var, unit):
            s = a[(a.Category == cat) & (a.Subcategory == sub) & (a.Variable == var) & (a.Unit == unit)].set_index("Year")["Value"]
            return [r(s.get(y), 3) for y in years]
        gen = {v: arr("Electricity generation", "Fuel", v, "TWh") for v in ["Coal", "Gas", "Nuclear", "Hydro", "Wind", "Solar", "Bioenergy", "Other Renewables", "Other Fossil"]}
        gen.update({v: arr("Electricity generation", "Aggregate fuel", v, "TWh") for v in ["Clean", "Fossil", "Renewables", "Wind and Solar"]})
        cap = {v: arr("Capacity", "Fuel", v, "GW") for v in ["Coal", "Gas", "Nuclear", "Hydro", "Wind", "Solar", "Bioenergy"]}
        out[area] = {"years": years, "demand_twh": arr("Electricity demand", "Demand", "Demand", "TWh"), "generation_total_twh": arr("Electricity generation", "Total", "Total Generation", "TWh"),
                     "net_imports_twh": arr("Electricity imports", "Electricity imports", "Net Imports", "TWh"), "generation_by_fuel_twh": gen, "capacity_by_fuel_gw": cap,
                     "emissions_total_mtco2": arr("Power sector emissions", "Total", "Total emissions", "mtCO2"), "co2_intensity_g_per_kwh": arr("Power sector emissions", "CO2 intensity", "CO2 intensity", "gCO2/kWh")}
    return out


# ====================================================================================================================== D3 emissions
@series("edgar_global_non_co2_by_sector",
        title="Global non-CO2 greenhouse-gas emissions by sector, 1970-2024 (EDGAR, JRC)",
        description="Global CH4, N2O and F-gas emissions in Mt CO2eq (GWP-100 AR5) by sector. Fossil CO2 is deliberately omitted (IEA data under CC BY-NC-ND).",
        sources=["edgar2025"], files=["edgar2025/EDGAR_2025_GHG_booklet_2025.xlsx"], units="Mt CO2eq per year (GWP-100, AR5)", geography="global total", time_span="1970 to 2024",
        variables=["ch4_by_sector", "n2o_by_sector", "f_gases"], supports=["L6", "L7"],
        attribution="Crippa et al., GHG emissions of all world countries, JRC/IEA 2025 Report, doi:10.2760/9816914 (EDGAR_2025_GHG; CC BY 4.0 for the non-CO2 material used here).",
        method="Sheet GHG_by_sector_and_country, rows with country 'GLOBAL TOTAL' and substance GWP_100_AR5_CH4, _N2O, _F-gases. The 'CO2' rows (fossil CO2 from the IEA) are not read into the output.",
        caveats=["EDGAR converts with AR5 GWP-100 values; FaIR takes emissions by mass, so these cannot be used as FaIR inputs without conversion back to mass."])
def b_edgar(ctx: Ctx):
    import openpyxl
    wb = openpyxl.load_workbook(ctx.verify("edgar2025/EDGAR_2025_GHG_booklet_2025.xlsx"), read_only=True, data_only=True)
    ws = wb["GHG_by_sector_and_country"]
    it = ws.iter_rows(values_only=True)
    hdr = next(it)
    years = [int(y) for y in hdr[4:]]
    out = {"years": years}
    for row in it:
        if row[2] != "GLOBAL TOTAL" or row[0] == "CO2" or row[0] is None:
            continue
        key = {"GWP_100_AR5_CH4": "ch4_by_sector", "GWP_100_AR5_N2O": "n2o_by_sector", "GWP_100_AR5_F-gases": "f_gases"}[row[0]]
        out.setdefault(key, {})[str(row[1])] = [r(v, 3) for v in row[4:]]
    return out


CEDS_PICK = {  # species: (file stem, unit key, how)
    "CO2": ("CO2_CEDS_global_estimates_by_sector_fuel_v_2025_03_18.csv", ["em", "sector", "fuel", "units"]),
    "CH4": ("CH4_CEDS_global_estimates_by_sector_v_2025_03_18.csv", ["em", "sector", "units"]),
    "N2O": ("N2O_CEDS_global_estimates_by_sector_v_2025_03_18.csv", ["em", "sector", "units"]),
    "SO2": ("SO2_CEDS_global_estimates_by_sector_fuel_v_2025_03_18.csv", ["em", "sector", "fuel", "units"]),
    "NOx": ("NOx_CEDS_global_estimates_by_sector_v_2025_03_18.csv", ["em", "sector", "units"]),
    "BC": ("BC_CEDS_global_estimates_by_sector_v_2025_03_18.csv", ["em", "sector", "units"]),
    "OC": ("OC_CEDS_global_estimates_by_sector_v_2025_03_18.csv", ["em", "sector", "units"]),
    "CO": ("CO_CEDS_global_estimates_by_sector_fuel_v_2025_03_18.csv", ["em", "sector", "fuel", "units"]),
    "NMVOC": ("NMVOC_CEDS_global_estimates_by_sector_fuel_v_2025_03_18.csv", ["em", "sector", "fuel", "units"]),
}


@series("ceds_global_emissions",
        title="Global historical emissions by species (CEDS v_2025_03_18)",
        description="Global annual totals of CO2, CH4, N2O, SO2, NOx, BC, OC, CO, NMVOC, and NH3 from CEDS, 1750-2023 (1970-2023 for species given only by sector), plus CO2 from electricity and heat production (sectors 1A1a).",
        sources=["ceds2025"], files=["ceds2025/CEDS_v_2025_03_18_aggregate.zip"], units="kt of the species per year (units string per species in the data)", geography="global", time_span="1750 to 2023 (species by sector: 1970 to 2023)",
        variables=["total_kt", "units", "years"], supports=["L6", "L7"],
        attribution="Hoesly et al. (2018) and O'Rourke et al., Community Emissions Data System v_2025_03_18, doi:10.5281/zenodo.15059443 (CC BY 4.0); annual global sums computed by F3.",
        method="Global files 'CEDS_global_estimates_by_sector[_fuel]' are summed over their rows (sectors, fuels); NH3 exists only per country, so it is the sum over the country-sector file. 'power_heat_co2_kt' sums the CO2 rows whose sector starts with 1A1a (electricity and heat).",
        caveats=["Species totals are as published; the NOx unit string in the file (as NO2) is kept.", "The 2025 release revises earlier CEDS values; do not mix with CMIP6-era CEDS (2017/2021) files."])
def b_ceds(ctx: Ctx):
    p = "ceds2025/CEDS_v_2025_03_18_aggregate.zip"
    pref = "CEDS_v_2025_03_18_aggregate/"
    out = {}
    for sp, (fn, idcols) in CEDS_PICK.items():
        d = ctx.zip_csv(p, pref + fn)
        ycols = [c for c in d.columns if re.fullmatch(r"X\d{4}", c)]
        out[sp] = {"units": str(d["units"].iloc[0]), "years": [int(c[1:]) for c in ycols], "total_kt": [r(v, 3) for v in d[ycols].sum().values], "source_file": fn}
        if sp == "CO2":
            pw = d[d["sector"].astype(str).str.startswith("1A1a")]
            out[sp]["power_heat_co2_kt"] = [r(v, 3) for v in pw[ycols].sum().values]
    d = ctx.zip_csv(p, pref + "NH3_CEDS_estimates_by_country_sector_v_2025_03_18.csv")
    ycols = [c for c in d.columns if re.fullmatch(r"X\d{4}", c)]
    out["NH3"] = {"units": str(d["units"].iloc[0]), "years": [int(c[1:]) for c in ycols], "total_kt": [r(v, 3) for v in d[ycols].sum().values], "source_file": "NH3_CEDS_estimates_by_country_sector_v_2025_03_18.csv (sum over countries)"}
    return out


@series("noaa_co2_annual", title="Atmospheric CO2, annual mean at Mauna Loa (NOAA GML)", description="Annual mean CO2 mole fraction in ppm with uncertainty, 1959-2025.",
        sources=["noaa_co2"], files=["noaa_co2/co2_annmean_mlo.csv"], units="ppm", geography="Mauna Loa (global proxy)", time_span="1959 to 2025", variables=["year", "mean_ppm", "unc_ppm"], supports=["L6", "L7"],
        attribution="NOAA Global Monitoring Laboratory, Mauna Loa CO2 annual mean (public domain; cite Dr. Xin Lan, NOAA/GML and Dr. Ralph Keeling, Scripps).",
        method="co2_annmean_mlo.csv with the comment lines removed.", caveats=["A single-site record; the global marine-surface mean is about 1 ppm lower."])
def b_noaa(ctx: Ctx):
    d = pd.read_csv(ctx.verify("noaa_co2/co2_annmean_mlo.csv"), comment="#")
    return {"rows": [{"year": int(t["year"]), "mean_ppm": r(t["mean"], 2), "unc_ppm": r(t["unc"], 2)} for _, t in d.iterrows()]}


@series("hadcrut5_global_annual", title="Global mean temperature anomaly, HadCRUT.5.2.0.0 annual, re-based to 1850-1900", description="Annual best estimate and 95% bounds, K above the mean of the 1850-1900 annual best estimates, 1850-2025 (2026 is a partial year, dropped).",
        sources=["hadcrut5"], files=["hadcrut5/HadCRUT.5.2.0.0.analysis.summary_series.global.annual.csv"], units="K relative to the 1850-1900 mean", geography="global", time_span="1850 to 2025", variables=["anomaly", "lower", "upper"], supports=["L6", "L7"],
        attribution="HadCRUT.5.2.0.0 data were obtained from http://www.metoffice.gov.uk/hadobs/hadcrut5 on 2026-10-22 and are (c) British Crown Copyright, Met Office, provided under an Open Government License, http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        method="Offset = mean of the annual best estimates for 1850-1900 inclusive, subtracted from all three columns; the offset is stored.", caveats=["Same file and re-basing as D-057 (audit/data/sources-history.json)."])
def b_had(ctx: Ctx):
    d = pd.read_csv(ctx.verify("hadcrut5/HadCRUT.5.2.0.0.analysis.summary_series.global.annual.csv"))
    d.columns = ["year", "a", "lo", "hi"]
    d = d[d.year <= 2025]
    off = float(d[(d.year >= 1850) & (d.year <= 1900)]["a"].mean())
    return {"offset_k": r(off, 4), "rows": [{"year": int(t.year), "anomaly": r(t.a - off, 4), "lower": r(t.lo - off, 4), "upper": r(t.hi - off, 4)} for t in d.itertuples()]}


# ====================================================================================================================== D7 calibration
@series("wpp2024_world_population", title="World population, fertility, life expectancy, births and deaths, UN WPP 2024 (medium variant, with high and low total population)",
        description="World total population (July 1, thousands) 1950-2100 for the medium, high and low variants, and world life expectancy, total fertility, births and deaths for the medium variant.",
        sources=["wpp2024_totpop", "wpp2024_demographic"], files=["wpp2024_totpop/wpp2024_totpop.csv.gz", "wpp2024_demographic/WPP2024_Demographic_Indicators_Medium.csv.gz"], units="thousand persons; years; births per woman; thousand births or deaths per year",
        geography="World", time_span="1950 to 2100 (estimates to 2023)", variables=["pop_total_thousand", "lex_years", "tfr", "births_thousand", "deaths_thousand"], supports=["L3", "L7"],
        attribution="United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024. Used under CC BY 3.0 IGO. Reshaped to world series; no other change.",
        method="Rows Location == 'World' of the two files; the medium variant for the demographic indicators.", caveats=["Projection from 2024 onward."])
def b_wpp(ctx: Ctx):
    t = pd.read_csv(ctx.verify("wpp2024_totpop/wpp2024_totpop.csv.gz"), low_memory=False)
    t = t[t.Location == "World"]
    out = {"years": sorted(int(y) for y in t[t.Variant == "Medium"].Time.unique())}
    for v, k in [("Medium", "pop_total_thousand_medium"), ("High", "pop_total_thousand_high"), ("Low", "pop_total_thousand_low")]:
        s = t[t.Variant == v].set_index("Time")["PopTotal"]
        out[k] = [r(s.get(y), 3) for y in out["years"]]
    e = pd.read_csv(ctx.verify("wpp2024_demographic/WPP2024_Demographic_Indicators_Medium.csv.gz"), low_memory=False)
    e = e[(e.Location == "World") & (e.Variant == "Medium")].set_index("Time")
    for col, k in [("LEx", "lex_years"), ("TFR", "tfr"), ("Births", "births_thousand"), ("Deaths", "deaths_thousand"), ("TPopulation1July", "pop_1july_thousand")]:
        out[k] = [r(e[col].get(y), 4) for y in out["years"]]
    return out


WDI_WORLD = ["NY.GDP.MKTP.KD", "NY.GDP.PCAP.KD", "SP.POP.TOTL", "SP.DYN.LE00.IN", "AG.YLD.CREL.KG", "NV.IND.TOTL.KD", "NE.GDI.TOTL.KD", "AG.LND.ARBL.HA", "SI.POV.GINI", "SI.POV.DDAY"]
# Excluded on purpose, from the indicator metadata saved with the data (meta-*.json, sourceOrganization):
#   EG.USE.ELEC.KH.PC   source IEA Energy Statistics (IEA terms, not CC)
#   EN.GHG.CO2.MT.CE.AR5 source EDGAR; its world 2024 value equals the IEA-EDGAR fossil CO2 total (CC BY-NC-ND) to the last digit shown
#   ER.H2O.FWTL.K3      source FAO AQUASTAT (CC BY-NC-SA 4.0 in the FAO catalogue)
WDI_EXCLUDED = {"EG.USE.ELEC.KH.PC": "IEA Energy Statistics (IEA terms, not CC)", "EN.GHG.CO2.MT.CE.AR5": "EDGAR / IEA-EDGAR fossil CO2 (CC BY-NC-ND)", "ER.H2O.FWTL.K3": "FAO AQUASTAT (CC BY-NC-SA 4.0)"}
WDI_LABOUR = ["SL.TLF.TOTL.IN", "SL.EMP.TOTL.SP.ZS", "SL.UEM.TOTL.ZS", "SL.AGR.EMPL.ZS", "SL.IND.EMPL.ZS", "SL.SRV.EMPL.ZS", "SL.TLF.CACT.ZS"]


@series("wdi_world_series", title="World aggregates from the World Bank WDI: output, population, labour, food, energy, water", description="World (WLD) annual series for 17 indicators where the World Bank publishes a world aggregate and the original provider allows redistribution; indicators without a world value, and three excluded for licence reasons, are listed.",
        sources=["wdi_labour", "wdi_calibration"], files=[f"wdi_labour/{i}.json" for i in WDI_LABOUR] + [f"wdi_calibration/{i}.json" for i in WDI_WORLD] + [f"wdi_calibration/meta-{i}.json" for i in WDI_LABOUR + WDI_WORLD if i not in WDI_LABOUR], units="as named per indicator", geography="World aggregate (WLD)", time_span="1960 to 2025", variables=WDI_LABOUR + WDI_WORLD,
        supports=["L3", "L4", "L7", "M5"], attribution="World Bank, World Development Indicators (CC BY 4.0), API as of 2026-10-08 (lastupdated field); world aggregates only.",
        method="For each indicator file, rows with countryiso3code == 'WLD'; null values dropped. Indicators with no WLD row are listed under missing.",
        caveats=["Labour series are ILO modelled estimates redistributed by the World Bank; GDP is in constant 2015 US dollars.", "SI.POV.GINI and AG.LND.ARBL.HA have no world (WLD) row here and appear under missing.", "Three indicators were left out because their original provider is not CC BY: see excluded_for_licence (checked against the indicator metadata)."])
def b_wdi(ctx: Ctx):
    out, missing = {}, []
    for d, ids in (("wdi_labour", WDI_LABOUR), ("wdi_calibration", WDI_WORLD)):
        for i in ids:
            j = json.loads(ctx.verify(f"{d}/{i}.json").read_text(encoding="utf-8"))
            rows = [x for x in j[1] if x["countryiso3code"] == "WLD" and x["value"] is not None]
            if not rows:
                missing.append(i)
                continue
            rows.sort(key=lambda x: int(x["date"]))
            meta_rel = f"wdi_calibration/meta-{i}.json"
            provider = None
            if meta_rel in ctx.files:
                provider = json.loads(ctx.verify(meta_rel).read_text(encoding="utf-8"))[1][0].get("sourceOrganization", "").split(", uri:")[0][:200]
            out[i] = {"name": rows[0]["indicator"]["value"], "provider": provider, "last_updated": j[0]["lastupdated"], "years": [int(x["date"]) for x in rows], "values": [r(x["value"], 4) for x in rows]}
    out["missing"] = missing
    out["excluded_for_licence"] = WDI_EXCLUDED
    return out


FAO_ITEMS = {15: "Wheat", 27: "Rice", 56: "Maize (corn)", 236: "Soya beans", 1717: "Cereals, primary"}


@series("faostat_world_cereals", title="World cereal and key-crop area, yield and production, 1961-2024 (FAOSTAT)", description="World (FAO area 5000) area harvested, yield and production for cereals (primary), wheat, rice, maize and soybeans.",
        sources=["faostat"], files=["faostat/Production_Crops_Livestock_E_All_Data_Normalized.zip"], units="ha; kg/ha; t", geography="World", time_span="1961 to 2024", variables=["area_harvested_ha", "yield_kg_per_ha", "production_t"], supports=["L3", "M5"],
        attribution="FAO. 2026. FAOSTAT: Crops and livestock products. Accessed on 22 October 2026. https://www.fao.org/faostat/en/#data/QCL. Licence: CC-BY-4.0.",
        method="The normalized crops-and-livestock file filtered to Area Code 5000 (World) and the item codes shown; elements 5312 (area harvested), 5412 (yield) and 5510 (production).", caveats=["FAOSTAT yield for aggregate items is production over area as FAO computes it; item definitions changed with the 2022+ classification (item codes are in the output)."])
def b_fao(ctx: Ctx):
    p = ctx.verify("faostat/Production_Crops_Livestock_E_All_Data_Normalized.zip")
    z = zipfile.ZipFile(p)
    n = [i.filename for i in z.infolist() if i.filename.endswith("Normalized).csv")][0]
    parts = []
    for ch in pd.read_csv(io.BytesIO(z.read(n)), encoding="latin-1", chunksize=500000, usecols=["Area Code", "Item Code", "Item", "Element Code", "Year", "Value"]):
        parts.append(ch[(ch["Area Code"] == 5000) & ch["Item Code"].isin(FAO_ITEMS) & ch["Element Code"].isin([5312, 5412, 5510])])
    d = pd.concat(parts)
    out = {}
    for code, label in FAO_ITEMS.items():
        g = d[d["Item Code"] == code]
        if g.empty:
            continue
        item = {"item_code": code, "item_name": str(g["Item"].iloc[0])}
        years = sorted(int(y) for y in g.Year.unique())
        item["years"] = years
        for ec, k in [(5312, "area_harvested_ha"), (5412, "yield_kg_per_ha"), (5510, "production_t")]:
            s = g[g["Element Code"] == ec].set_index("Year")["Value"]
            item[k] = [r(s.get(y), 2) for y in years]
        out[label] = item
    return out


@series("maddison_world_gdp_per_capita", title="World GDP per capita 1820-2022 (Maddison Project Database 2023, regional sheet)", description="World GDP per capita in 2011 international dollars as given in the MPD 2023 'Regional data' sheet, with regional GDP per capita.",
        sources=["maddison2023"], files=["maddison2023/mpd2023_web.xlsx"], units="2011 international USD per person", geography="World and 8 MPD regions", time_span="1820 to 2022 (irregular early years)", variables=["world_gdp_per_capita", "regional"], supports=["L7"],
        attribution="Bolt, J. and van Zanden, J.L. (2024), Maddison style estimates of the evolution of the world economy: A new 2023 update, Journal of Economic Surveys, doi:10.1111/joes.12618. Maddison Project Database 2023 (CC BY 4.0).",
        method="Sheet 'Regional data': first column year, regional GDPpc columns 1-8 and 'World GDP pc' column 9, as published by the MPD authors (not recomputed).", caveats=["Early years are sparse (decades before 1870/1950); regional values rest on whatever countries have estimates."])
def b_mpd(ctx: Ctx):
    x = pd.read_excel(ctx.verify("maddison2023/mpd2023_web.xlsx"), sheet_name="Regional data", header=None)
    regions = [str(v) for v in x.iloc[1, 1:9]]
    out = {"regions": regions, "rows": []}
    for i in range(2, len(x)):
        y = x.iloc[i, 0]
        if pd.isna(y):
            continue
        out["rows"].append({"year": int(y), "world": r(x.iloc[i, 9], 2), "regional": [r(v, 2) for v in x.iloc[i, 1:9]]})
    return out


PWT_COUNTRIES = ["USA", "CHN", "DEU", "JPN", "IND", "FRA", "GBR", "BRA", "KOR"]


@series("pwt_labour_share", title="Labour share of GDP (labsh), Penn World Table 11.0, 1950-2023", description="Labour compensation share in GDP by year: median across countries, GDP-weighted mean (rgdpna), number of countries, and selected countries. First long labour-share series for the S7 hindcast (M5 plan STOP item 3).",
        sources=["pwt110"], files=["pwt110/pwt110.xlsx"], units="share of GDP at current national prices (0-1)", geography="up to 185 countries", time_span="1950 to 2023", variables=["median", "gdp_weighted_mean", "n_countries", "selected_countries"], supports=["L4", "L7"],
        attribution="Feenstra, R.C., Inklaar, R. and Timmer, M.P. (2015), The Next Generation of the Penn World Table, American Economic Review 105(10), 3150-3182; PWT 11.0 (CC BY 4.0).",
        method="Sheet Data, variable labsh; per year the median and the rgdpna-weighted mean over countries with both values; selected countries as listed.",
        caveats=["PWT labsh for many countries is imputed from few national-accounts years and adjusted for self-employed income (see the PWT user guide); the sample composition changes over time, so the cross-country median moves with entry of countries."])
def b_pwt(ctx: Ctx):
    d = pd.read_excel(ctx.verify("pwt110/pwt110.xlsx"), sheet_name="Data", usecols=["countrycode", "year", "labsh", "rgdpna"])
    d = d.dropna(subset=["labsh"])
    rows = []
    for y, g in d.groupby("year"):
        w = g.dropna(subset=["rgdpna"])
        rows.append({"year": int(y), "n_countries": int(len(g)), "median": r(g["labsh"].median(), 4), "gdp_weighted_mean": r((w["labsh"] * w["rgdpna"]).sum() / w["rgdpna"].sum(), 4) if len(w) else None})
    sel = {}
    for c in PWT_COUNTRIES:
        g = d[d.countrycode == c].sort_values("year")
        sel[c] = {"years": [int(y) for y in g.year], "labsh": [r(v, 4) for v in g.labsh]}
    return {"by_year": rows, "selected_countries": sel}


@series("ilostat_labour_income_share", title="Labour income share of GDP, ILO SDG 10.4.1, 2004-2025", description="Per year: median and unweighted mean over countries, number of countries, and selected countries (ILO modelled estimates).",
        sources=["ilostat"], files=["ilostat/SDG_1041_NOC_RT_A.csv"], units="% of GDP", geography="countries (3-letter ISO codes; aggregates excluded)", time_span="2004 to 2025", variables=["median_pct", "mean_pct", "n_countries", "selected_countries"], supports=["L4", "L7"],
        attribution="ILOSTAT, SDG indicator 10.4.1 (labour income share as a percent of GDP), ILO modelled estimates, https://ilostat.ilo.org (CC BY 4.0 per ilo.org/rights-and-permissions).",
        method="Rows of SDG_1041_NOC_RT_A.csv with a 3-letter ref_area; years 2004-2025 (2026 is a projection/imputation and dropped).", caveats=["The series starts in 2004 (confirms D-008's note) and is modelled for many countries; PWT labsh is the long series.",
                                                                                                                                         "The ILO measure and PWT labsh differ in definition (ILO: labour compensation including an imputation for self-employed, as % of GDP at factor cost/market prices per national source)."])
def b_ilo_lis(ctx: Ctx):
    d = pd.read_csv(ctx.verify("ilostat/SDG_1041_NOC_RT_A.csv"), usecols=["ref_area", "time", "obs_value"])
    d = d[d.ref_area.str.fullmatch(r"[A-Z]{3}") & (d.time <= 2025)].dropna(subset=["obs_value"])
    rows = [{"year": int(y), "n_countries": int(len(g)), "median_pct": r(g.obs_value.median(), 3), "mean_pct": r(g.obs_value.mean(), 3)} for y, g in d.groupby("time")]
    sel = {c: {"years": [int(y) for y in g.sort_values("time").time], "pct": [r(v, 3) for v in g.sort_values("time").obs_value]} for c in PWT_COUNTRIES for g in [d[d.ref_area == c]]}
    return {"by_year": rows, "selected_countries": sel}


@series("ilostat_world_employment_by_sector", title="World employment by economic activity, 1991-2025 (ILO modelled estimates)", description="World employment (thousands) for broad sectors (agriculture, industry, services) and ISIC Rev.4 sections, both sexes.",
        sources=["ilostat"], files=["ilostat/EMP_2EMP_SEX_ECO_NB_A.csv"], units="thousand persons", geography="World (ILO aggregate)", time_span="1991 to 2025", variables=["employment by economic activity"], supports=["L4"],
        attribution="ILOSTAT, Employment by sex and economic activity -- ILO modelled estimates, Nov. 2025 (thousands), https://ilostat.ilo.org (CC BY 4.0 per ilo.org/rights-and-permissions).",
        method="Rows with ref_area label 'World' and sex SEX_T; each classif1 code is one series.", caveats=["Modelled estimates; ISIC sections J (information and communication) and K (finance) sit inside ISIC4 combined codes HJ and K as the ILO publishes them."])
def b_ilo_emp(ctx: Ctx):
    d = pd.read_csv(ctx.verify("ilostat/EMP_2EMP_SEX_ECO_NB_A.csv"), usecols=["ref_area.label", "sex", "classif1", "classif1.label", "time", "obs_value"])
    d = d[(d["ref_area.label"] == "World") & (d.sex == "SEX_T")]
    out = {}
    for code, g in d.groupby("classif1"):
        g = g.sort_values("time")
        out[code] = {"label": str(g["classif1.label"].iloc[0]), "years": [int(y) for y in g.time], "thousand_persons": [r(v, 1) for v in g.obs_value]}
    return out


@series("ucdp_conflicts_per_year", title="State-based armed conflicts per year, UCDP/PRIO v26.1, 1946-2025", description="Number of active state-based conflicts per year, of which at war intensity (1000 or more battle-related deaths), by type.",
        sources=["ucdp"], files=["ucdp/ucdp-prio-acd-261-csv.zip"], units="conflicts per year", geography="World", time_span="1946 to 2025", variables=["n_conflicts", "n_war", "by_type"], supports=["L4"],
        attribution="Davies, S., Pettersson, T., and Oberg, M. (2025), Organized violence 1989-2024, and the challenges of identifying civilian victims, Journal of Peace Research; Gleditsch et al. (2002), Armed Conflict 1946-2001; UCDP/PRIO Armed Conflict Dataset v26.1 (CC BY 4.0). Counts by F3.",
        method="UcdpPrioConflict_v26_1.csv, distinct conflict_id per year; intensity_level 2 = war; type_of_conflict 1-4 (extrasystemic, interstate, internal, internationalized internal).",
        caveats=["State-based armed conflict only; this is not 'social tension' (M5 plan/D-008): an overlay for plausibility, never a calibration target."])
def b_ucdp(ctx: Ctx):
    d = ctx.zip_csv("ucdp/ucdp-prio-acd-261-csv.zip", "UcdpPrioConflict_v26_1.csv")
    rows = []
    for y, g in d.groupby("year"):
        rows.append({"year": int(y), "n_conflicts": int(g.conflict_id.nunique()), "n_war": int(g[g.intensity_level == 2].conflict_id.nunique()),
                     "by_type": {str(int(t)): int(x.conflict_id.nunique()) for t, x in g.groupby("type_of_conflict")}})
    return {"by_year": rows}


# ====================================================================================================================== D5 task exposure
SOC_GROUPS = {"11": "Management", "13": "Business and Financial Operations", "15": "Computer and Mathematical", "17": "Architecture and Engineering", "19": "Life, Physical, and Social Science",
              "21": "Community and Social Service", "23": "Legal", "25": "Educational Instruction and Library", "27": "Arts, Design, Entertainment, Sports, and Media",
              "29": "Healthcare Practitioners and Technical", "31": "Healthcare Support", "33": "Protective Service", "35": "Food Preparation and Serving Related",
              "37": "Building and Grounds Cleaning and Maintenance", "39": "Personal Care and Service", "41": "Sales and Related", "43": "Office and Administrative Support",
              "45": "Farming, Fishing, and Forestry", "47": "Construction and Extraction", "49": "Installation, Maintenance, and Repair", "51": "Production",
              "53": "Transportation and Material Moving", "55": "Military Specific"}


@series("task_exposure_summary", title="AI and robot exposure of occupations, by SOC major group: observed (Anthropic), LLM-rated potential (OpenAI) and robot exposure (Anthropic)",
        description="Joins three occupation-level datasets on the 6-digit SOC code and reports unweighted means by SOC major group, plus the rank correlation between observed AI exposure and the LLM-rated exposure.",
        sources=["anthropic_econ_index", "gpts_are_gpts"], files=["anthropic_econ_index/job_exposure.csv", "anthropic_econ_index/robot_exposure_occupations.csv", "gpts_are_gpts/occ_level.csv"],
        units="exposure indices (0 to 1 as published; beta = share of tasks directly exposed plus half of tasks exposed with extra tooling)", geography="United States occupations (O*NET-SOC)", time_span="2023 ratings (OpenAI); 2025-2026 usage (Anthropic)",
        variables=["observed_exposure_mean", "gpt4_beta_mean", "human_beta_mean", "robot_exposure_mean", "n_occupations"], supports=["L4"],
        attribution="Anthropic Economic Index (labor_market_impacts, robot_exposure), CC BY; Eloundou et al. (2023), GPTs are GPTs, data in github.com/openai/GPTs-are-GPTs (MIT, Copyright (c) 2024 OpenAI). Aggregation by F3.",
        method="Anthropic job_exposure (6-digit SOC) as is; O*NET-SOC 8-digit rows of the OpenAI and robot files averaged to 6 digits; inner join on the 6-digit code; means by the first two digits (SOC major group), unweighted by employment.",
        caveats=["Unweighted by employment: a large group dominated by one big occupation is not represented by its mean. Employment weights (BLS OEWS) were not retrieved.",
                 "Exposure is not displacement: the OpenAI ratings are potential exposure to LLMs rated by GPT-4 and by humans; the Anthropic index is observed use in conversations. They measure different things; the correlation is reported, not assumed."])
def b_tasks(ctx: Ctx):
    a = pd.read_csv(ctx.verify("anthropic_econ_index/job_exposure.csv"))
    rb = pd.read_csv(ctx.verify("anthropic_econ_index/robot_exposure_occupations.csv"))
    g = pd.read_csv(ctx.verify("gpts_are_gpts/occ_level.csv"))
    rb["soc"] = rb["onetsoc_code"].str[:7]
    g["soc"] = g["O*NET-SOC Code"].str[:7]
    rb6 = rb.groupby("soc")["robot_exposure_index"].mean()
    g6 = g.groupby("soc")[["dv_rating_beta", "human_rating_beta", "dv_rating_alpha", "dv_rating_gamma"]].mean()
    a = a.rename(columns={"occ_code": "soc"}).set_index("soc")[["title", "observed_exposure"]]
    j = a.join(g6, how="inner").join(rb6, how="left")
    j["grp"] = j.index.str[:2]
    rows = []
    for k, x in j.groupby("grp"):
        rows.append({"soc_major_group": k, "name": SOC_GROUPS.get(k), "n_occupations": int(len(x)), "observed_exposure_mean": r(x.observed_exposure.mean(), 4), "gpt4_beta_mean": r(x.dv_rating_beta.mean(), 4),
                     "human_beta_mean": r(x.human_rating_beta.mean(), 4), "robot_exposure_mean": r(x.robot_exposure_index.mean(), 4)})
    return {"n_joined_occupations": int(len(j)), "overall": {"observed_exposure_mean": r(j.observed_exposure.mean(), 4), "gpt4_beta_mean": r(j.dv_rating_beta.mean(), 4), "human_beta_mean": r(j.human_rating_beta.mean(), 4), "robot_exposure_mean": r(j.robot_exposure_index.mean(), 4)},
            "spearman_observed_vs_gpt4_beta": r(j.observed_exposure.corr(j.dv_rating_beta, method="spearman"), 4), "spearman_observed_vs_human_beta": r(j.observed_exposure.corr(j.human_rating_beta, method="spearman"), 4),
            "spearman_gpt4_vs_human_beta": r(j.dv_rating_beta.corr(j.human_rating_beta, method="spearman"), 4), "by_soc_major_group": rows}


# ====================================================================================================================== D2 water and D6 minerals
@series("aqueduct_water_stress_by_country", title="Baseline water stress by country, WRI Aqueduct 4.0", description="Country-level baseline water stress score and category (country_baseline sheet, 'bws' indicator) with the country's ranking, for 2019-baseline conditions.",
        sources=["aqueduct40"], files=["aqueduct40/aqueduct-4-0-country-rankings.zip"], units="score 0 to 5; category label", geography="countries", time_span="baseline 1979-2019", variables=["score", "score_ranked", "cat", "label"], supports=["M5", "DC"],
        attribution="Kuzma et al. (2023), Aqueduct 4.0: Updated decision-relevant global water risk indicators, WRI Technical Note, doi:10.46830/writn.23.00061 (CC BY 4.0).",
        method="Sheet country_baseline, rows with indicator_name 'bws' (baseline water stress), industrial-weighted ('weight' column kept) as published.",
        caveats=["Country aggregates hide basin-level stress: a data-centre site's local water stress is not the national value (province_baseline and the gridded zip are in the raw folder)."])
def b_aqueduct(ctx: Ctx):
    p = ctx.verify("aqueduct40/aqueduct-4-0-country-rankings.zip")
    z = zipfile.ZipFile(p)
    n = [i.filename for i in z.infolist() if i.filename.endswith(".xlsx")][0]
    d = pd.read_excel(io.BytesIO(z.read(n)), sheet_name="country_baseline")
    names = sorted(d["indicator_name"].unique())
    b = d[d["indicator_name"] == "bws"] if "bws" in names else d[d["indicator_name"].astype(str).str.contains("ws", case=False)]
    rows = [{"iso3": str(t.gid_0), "country": str(t.name_0), "weight": str(t.weight), "score": r(t.score, 3), "rank": ri(t.score_ranked), "category": None if pd.isna(t.cat) else int(t.cat), "label": None if pd.isna(t.label) else str(t.label)}
            for t in b.itertuples()]
    return {"indicator_names_in_sheet": names, "rows": rows}


class _Tab(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self._row, self._cell, self._in = [], None, None, False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


def _num(s):
    s = re.sub(r"[\s  ]", "", s).replace("%", "")
    try:
        return float(s)
    except ValueError:
        return None


@series("iea_critical_minerals_demand", title="Demand for copper, lithium and cobalt: cleantech, other uses, total, secondary supply (IEA Critical Minerals Outlook)",
        description="The scenario table of the IEA mineral pages: cleantech demand, other uses, total demand, secondary supply and primary supply requirements, in kt, for 2021, 2024 (2023 for cobalt), 2030 and 2040.",
        sources=["iea_cmo2025"], files=["iea_cmo2025/copper-landing.html", "iea_cmo2025/lithium-landing.html", "iea_cmo2025/cobalt-landing.html"], units="kt of contained metal per year; shares in %", geography="world", time_span="2021 to 2040",
        variables=["cleantech_demand_kt", "other_uses_kt", "total_demand_kt", "secondary_supply_kt", "primary_supply_requirements_kt", "top3_mining_share_pct", "top3_refining_share_pct"], supports=["M5", "DC"],
        attribution="IEA (2025), Global Critical Minerals Outlook 2025 (copper, lithium pages); IEA (2024), Global Critical Minerals Outlook 2024 (cobalt page). CC BY 4.0.",
        method="The HTML table on each page is read with the standard-library HTML parser; thousands separators (thin spaces) are removed.",
        caveats=["Copper and lithium are the 2025 edition under the STEPS scenario (2021, 2024, 2030, 2040); the cobalt page is the 2024 edition under APS (2021, 2023, 2030, 2040) - not the same edition or scenario, so cobalt is not comparable year by year.",
                 "Nickel, graphite and rare-earth pages returned HTTP 403 and are missing."])
def b_iea_cmo(ctx: Ctx):
    out = {}
    for name, rel, ed in [("copper", "iea_cmo2025/copper-landing.html", "Global Critical Minerals Outlook 2025 (STEPS)"), ("lithium", "iea_cmo2025/lithium-landing.html", "Global Critical Minerals Outlook 2025 (STEPS)"),
                          ("cobalt", "iea_cmo2025/cobalt-landing.html", "Global Critical Minerals Outlook 2024 (APS)")]:
        t = ctx.verify(rel).read_text(encoding="utf-8", errors="replace")
        p = _Tab()
        p.feed(t)
        tab = [row for row in p.rows if row and re.search(r"Cleantech demand|Other uses|Total demand|Secondary supply|Primary supply|Share of top three", row[0])]
        hdr = [row for row in p.rows if len(row) >= 4 and all(re.fullmatch(r"\d{4}", c) for c in row[-4:])]
        years = [int(c) for c in hdr[0][-4:]] if hdr else None
        keymap = {"Cleantech demand": "cleantech_demand_kt", "Other uses": "other_uses_kt", "Total demand": "total_demand_kt", "Secondary supply": "secondary_supply_kt", "Primary supply": "primary_supply_requirements_kt",
                  "Share of top three mining": "top3_mining_share_pct", "Share of top three refining": "top3_refining_share_pct"}
        rows = {}
        for row in tab:
            for k, v in keymap.items():
                if row[0].startswith(k):
                    rows[v] = [_num(c) for c in row[1:5]]
        out[name] = {"edition_and_scenario": ed, "years": years, **rows}
    return out


NORM_WS = re.compile(r"\s+")


def _flat(s):
    return NORM_WS.sub(" ", s.replace("’", "'").replace("“", '"').replace("”", '"'))


IEA_FACTS = [  # (id, quantity, value, unit, year, scope, evidence text that must occur verbatim in the report)
    ("dc_electricity_2024", "Global data-centre electricity consumption", 415, "TWh", 2024, "world, estimate", "estimated approximately 415 TWh for 2024 (Figure 2.10), which accounted for around 1.5%"),
    ("dc_share_2024", "Data centres' share of global electricity consumption", 1.5, "%", 2024, "world, estimate", "approximately 415 TWh for 2024 (Figure 2.10), which accounted for around 1.5%"),
    ("dc_growth_hist", "Annual growth of data-centre electricity consumption over the last five years", 12, "% per year", 2024, "world", "It has grown at 12% per year over the last five years"),
    ("dc_electricity_2030_base", "Data-centre electricity consumption, Base Case", 945, "TWh", 2030, "world, projection", "around 945 TWh by 2030 in the Base Case, representing just under 3% of total global electricity consumption in 2030"),
    ("dc_growth_2024_2030", "Annual growth 2024-2030, Base Case", 15, "% per year", 2030, "world, projection", "From 2024 to 2030, data centre electricity consumption grows by around 15% per year"),
    ("dc_electricity_2035_base", "Data-centre electricity consumption, Base Case", 1200, "TWh", 2035, "world, projection", "global data centre electricity consumption rising to around 1 200 TWh by 2035"),
    ("dc_electricity_2030_liftoff", "Data-centre electricity consumption, Lift-Off Case", 1260, "TWh", 2030, "world, projection (over)", "consumption reaches over 1 260 TWh by 2030"),
    ("dc_electricity_2030_higheff", "Data-centre electricity consumption, High Efficiency Case", 800, "TWh", 2030, "world, projection", "consumption reaches around 800 TWh by 2030"),
    ("dc_electricity_2030_headwinds", "Data-centre electricity consumption, Headwinds Case", 670, "TWh", 2030, "world, projection", "In the Headwinds Case, it reaches around 670 TWh"),
    ("dc_electricity_2035_range", "Range of data-centre electricity consumption across the four cases", "700 to 1 720", "TWh", 2035, "world, projection", "spanning 700 TWh to 1 720 TWh across the four cases"),
    ("dc_electricity_2035_higheff", "Data-centre electricity demand, High Efficiency Case", 970, "TWh", 2035, "world, projection", "global electricity demand from data centres reaching around 970 TWh by 2035"),
    ("dc_us_2024", "US data-centre electricity consumption", 180, "TWh", 2024, "United States, estimate", "Data centres accounted for around 180 TWh of electricity consumption in 2024 in the United States"),
    ("dc_shares_2024", "Shares of global data-centre electricity consumption: United States, China, Europe", "45, 25, 15", "%", 2024, "world, estimate", "The United States accounted for the largest share of global data centre electricity consumption in 2024 (45%), followed by China (25%) and Europe (15%)"),
    ("dc_europe_2024", "European data-centre electricity consumption", 70, "TWh", 2024, "Europe, estimate", "at an estimated 70 TWh in 2024"),
    ("pue_2024_2030", "Global weighted-average PUE, 2024 to 2030 (Base Case)", "1.41 to 1.29", "ratio", 2030, "world", "decreasing from 1.41 to 1.29 on average"),
    ("n_virginia_capacity", "Northern Virginia installed and under-development data-centre capacity", "over 5 GW installed, more than 3 GW under development", "GW", 2024, "Loudoun and Prince William Counties", "with over 5 GW of installed capacity and more than 3 GW under development"),
]


@series("iea_energy_ai_figures", title="Data-centre electricity figures from the IEA report Energy and AI (2025), with page references",
        description="Sixteen headline figures (estimates for 2024, Base, Lift-Off, High Efficiency and Headwinds projections to 2035, regional shares, PUE) each with the report page where the sentence occurs and a check that the sentence is in the PDF text.",
        sources=["iea_energy_ai"], files=["iea_energy_ai/EnergyandAI.pdf"], units="TWh; % ; ratio; GW", geography="world and regions", time_span="2024 to 2035", variables=["id", "quantity", "value", "unit", "year", "scope", "page", "evidence"], supports=["DC", "L5", "AI"],
        attribution="IEA (2025), Energy and AI, IEA, Paris, https://www.iea.org/reports/energy-and-ai, Licence: CC BY 4.0. Figures transcribed with the sentence that contains them.",
        method="Each fact is a verbatim sentence fragment looked up in the page-by-page text of the PDF (pdftotext -raw, whitespace collapsed); the build fails if a fragment is not found. Page = PDF page index (1-based), not the printed number.",
        caveats=["The IEA data product (spreadsheets) has Non-CC terms and is not used; only report text is transcribed.", "Projections are the IEA's scenarios, not forecasts of F3."], needs_pdf=True)
def b_iea_ai(ctx: Ctx):
    pages = [_flat(p) for p in ctx.pdf_pages("iea_energy_ai/EnergyandAI.pdf")]
    out = []
    for fid, q, v, u, y, scope, ev in IEA_FACTS:
        ev_n = _flat(ev)
        hits = [i + 1 for i, p in enumerate(pages) if ev_n in p]
        if not hits:
            raise ChecksumError(f"IEA fact {fid}: evidence sentence not found in the PDF text: {ev}")
        out.append({"id": fid, "quantity": q, "value": v, "unit": u, "year": y, "scope": scope, "page": hits[0], "pages_with_same_sentence": hits, "evidence": ev})
    return {"facts": out}


# ---- USGS Mineral Commodity Summaries world tables (pdftotext -raw keeps rows together; footnote digits are glued to numbers and are resolved by a sum check)
MCS_CFG = [  # (page name, key, columns, label)
    ("COPPER", "copper", ["mine_2024", "mine_2025e", "refinery_2024", "refinery_2025e", "reserves"], "Mine and refinery production and reserves"),
    ("LITHIUM", "lithium", ["mine_2024", "mine_2025e", "reserves"], "Mine production and reserves"),
    ("GALLIUM", "gallium", ["primary_2024", "primary_2025e", "capacity_2025"], "Low-purity primary production and capacity"),
    ("RARE EARTHS", "rare_earths", ["mine_2024", "mine_2025e", "reserves"], "Mine production (rare-earth oxide equivalent) and reserves"),
    ("SILICON", "silicon", ["ferrosilicon_2024", "ferrosilicon_2025e", "silicon_metal_2024", "silicon_metal_2025e"], "Production of ferrosilicon and silicon metal"),
    ("COBALT", "cobalt", ["mine_2024", "mine_2025e", "reserves"], "Mine production and reserves"),
    ("NICKEL", "nickel", ["mine_2024", "mine_2025e", "reserves"], "Mine production and reserves"),
    ("GRAPHITE (NATURAL)", "graphite_natural", ["mine_2024", "mine_2025e", "reserves"], "Mine production and reserves"),
]
_NUM_OK = re.compile(r"^\d{1,3}(,\d{3})*(\.\d+)?$")


def _cands(tok):
    """Interpretations of one table token: a number with optional estimate prefix 'e', lower-bound '>' and 0 to 2 glued footnote digits.
    Returns (flags, [(value, n_digits_stripped), ...]); the unstripped reading comes first."""
    t = tok.strip()
    flags = {"e": False, "gt": False}
    t2 = re.sub(r"^\d{1,2}(?=(NA|W)$)", "", t)
    if t2 in ("NA", "W", "--") or re.fullmatch(r"\(\d\)", t2):
        return {"kind": t2 if t2 in ("NA", "W", "--") else "NA"}, []
    m = re.match(r"^([e>]*)(.*)$", t2)
    flags["e"] = "e" in m.group(1)
    flags["gt"] = ">" in m.group(1)
    body = m.group(2)
    vals = []
    for k in (0, 1, 2):
        b = body[k:]
        if b and not b.startswith("0") and _NUM_OK.fullmatch(b):
            vals.append((float(b.replace(",", "")), k))
    return {"kind": "num", **flags}, vals


def _label(tokens):
    s = " ".join(tokens)
    s = re.sub(r"\d+$", "", s).strip()
    if s.endswith("e") and s[:-1] in {"Japan", "Russia", "Korea, North", "Malaysia"}:
        s = s[:-1]
    return s


def _solve(rows, total_c, tol):
    """Choose one reading per row and one for the total so that the sum of rows is within tol of the total, with as few stripped footnote digits as possible.
    rows: list of candidate lists [(value, cost)], [] for non-numeric cells. Returns dict or None."""
    results = []
    for T, tcost in total_c:
        states = {0.0: (0, [])}
        for c in rows:
            if not c:
                states = {k: (v[0], v[1] + [None]) for k, v in states.items()}
                continue
            nxt = {}
            for sm, (cost, ch) in states.items():
                for j, (v, k) in enumerate(c):
                    ns = round(sm + v, 3)
                    if ns > (1 + tol) * T:
                        continue
                    cur = nxt.get(ns)
                    if cur is None or cost + k < cur[0]:
                        nxt[ns] = (cost + k, ch + [j])
            states = nxt
            if not states:
                break
        feas = [(cost, abs(sm - T) / T, ch) for sm, (cost, ch) in states.items() if abs(sm - T) / T <= tol]
        if feas:
            feas.sort(key=lambda x: (x[0], x[1]))
            results.append((feas[0][0] + tcost, feas[0][1], feas[0][2], T, tcost))
    if not results:
        return None
    results.sort(key=lambda x: (x[0], x[1]))
    best = results[0]
    unique_total = len(results) == 1 or results[1][0] > best[0]
    return {"cost": best[0], "rel_err": best[1], "choice": best[2], "total": best[3], "total_cost": best[4], "unique_total": unique_total}


def parse_mcs_table(pages, name, columns):
    pat = re.compile(r"^\s*(Prepared by[^\n]*\n)?\s*" + re.escape(name) + r"\d*\s*\n")
    hits = [i for i, p in enumerate(pages) if pat.match(p)]
    if not hits:
        return None
    txt = "\n".join(pages[h] for h in hits[:2])
    lines = txt.split("\n")
    unit = next((l.strip() for l in lines if re.match(r"^\s*[\(\[]Data in", l)), None)
    hd = [i for i, l in enumerate(lines) if re.match(r"^World .*(Production|Reserves)", l)]
    tot = [i for i, l in enumerate(lines) if l.startswith("World total")]
    if not hd or not tot:
        return {"unit": unit, "pages": [h + 1 for h in hits[:2]], "table": None}
    rows = []
    for l in lines[hd[0] + 1: tot[0]]:
        toks = l.split()
        k = next((i for i, t in enumerate(toks) if re.match(r"^([e>]*\d|W$|--$|NA$|\(\d\)$|\d{1,2}(NA|W)$)", t)), None)
        if k is None or k == 0:
            continue
        vals = toks[k:]
        if len(vals) != len(columns):
            continue
        rows.append((_label(toks[:k]), vals))
    ttoks = lines[tot[0]].split()[3:]
    if len(ttoks) != len(columns):
        return {"unit": unit, "pages": [h + 1 for h in hits[:2]], "table": None, "note": "world total row did not have the expected number of columns", "total_tokens": ttoks}
    res = {"unit": unit, "pages": [h + 1 for h in hits[:2]], "columns": columns, "world_total": {}, "countries": [], "n_country_rows": len(rows)}
    country = [{"country": lab, "values": {}} for lab, _ in rows]
    for ci, col in enumerate(columns):
        tol = 0.06 if ("reserves" in col or "capacity" in col) else 0.03
        tflags, tc = _cands(ttoks[ci])
        rc, rflags = [], []
        for lab, vals in rows:
            fl, c = _cands(vals[ci])
            rflags.append(fl)
            rc.append(c)
        tok = ttoks[ci]
        if tflags.get("gt") or not tc:
            res["world_total"][col] = {"token": tok, "value": None, "lower_bound": bool(tflags.get("gt")), "lower_bound_value": tc[0][0] if tc else None, "resolved": False, "reason": "the total is a lower bound (>) or not numeric"}
            for ri_ in range(len(rows)):
                country[ri_]["values"][col] = "unresolved"
            continue
        sol = _solve(rc, tc, tol)
        if sol is None:
            res["world_total"][col] = {"token": tok, "value": None, "resolved": False, "reason": f"no reading of the rows adds up to the total within {int(tol * 100)}%"}
            for ri_ in range(len(rows)):
                country[ri_]["values"][col] = "unresolved"
            continue
        ok = bool(sol["unique_total"])
        stripped = [rows[i][0] for i, ch in enumerate(sol["choice"]) if ch is not None and rc[i][ch][1] > 0]
        res["world_total"][col] = {"token": tok, "value": sol["total"] if ok else None, "estimated": bool(tflags.get("e")), "resolved": ok, "rel_error_sum_vs_total": r(sol["rel_err"], 4),
                                   "tolerance": tol, "total_footnote_digits_removed": sol["total_cost"], "rows_with_footnote_digits_removed": stripped}
        for ri_ in range(len(rows)):
            ch = sol["choice"][ri_]
            fl = rflags[ri_]
            if not ok:
                country[ri_]["values"][col] = "unresolved"
            elif ch is None:
                country[ri_]["values"][col] = fl.get("kind") if fl.get("kind") in ("W", "NA", "--") else None
            else:
                country[ri_]["values"][col] = rc[ri_][ch][0]
    res["countries"] = country
    return res


@series("usgs_mcs2026_world_production_reserves", title="World mine production and reserves of copper, lithium, gallium, rare earths, silicon, cobalt, nickel and natural graphite (USGS Mineral Commodity Summaries 2026)",
        description="World totals and country rows of the USGS 'World Mine Production and Reserves' tables for eight commodities; footnote digits glued to numbers by the PDF text extraction are removed only where the country rows then add up to the printed world total within 3%; otherwise the value is left unresolved.",
        sources=["usgs_mcs2026"], files=["usgs_mcs2026/mcs2026.pdf"], units="as stated per commodity in the unit field (thousand tons for copper and silicon, kg for gallium, metric tons for the others)", geography="world by producing country", time_span="2024 and 2025 estimate (production); reserves as of 2025",
        variables=["world_total", "countries"], supports=["M5", "DC", "AI"],
        attribution="U.S. Geological Survey, Mineral Commodity Summaries 2026, version 1.3 (May 2026), doi:10.3133/mcs2026. Public domain (US Government).",
        method="pdftotext -raw page text; the table between the 'World ... Production' heading and the 'World total' row. Each number token may carry 0 to 2 glued footnote digits; candidates are tested jointly with the total and the choice must make the sum of country rows equal the total within 3% and be clearly better than the next-best choice. 'W' (withheld), '--' (zero) and 'NA' are kept as such.",
        caveats=["Germanium has no country table in the report (data are 'limited', page 93) so it is absent; values for China and others are USGS estimates.", "Resolution can fail for a column; those cells say 'unresolved' and nothing is guessed.",
                 "Reserves are not resources; USGS notes reserves are revised with prices and technology."], needs_pdf=True)
def b_mcs(ctx: Ctx):
    pages = ctx.pdf_pages("usgs_mcs2026/mcs2026.pdf")
    out = {}
    for name, key, cols, label in MCS_CFG:
        t = parse_mcs_table(pages, name, cols)
        if t is None:
            raise ChecksumError(f"MCS page for {name} not found")
        t["table_label"] = label
        out[key] = t
    p93 = _flat(pages[92]) if len(pages) > 92 else ""
    out["germanium"] = {"table": None, "pages": [92, 93], "note": "No country table in the report.",
                        "evidence": "Because most producers do not publicly report germanium production, global production data were limited.", "evidence_found": "Because most producers do not publicly report germanium production, global production data were limited." in p93}
    return out


# ====================================================================================================================== cross-checks (second source for every key number where one exists)
CROSS_CHECKS_PATH = REPO / "audit" / "data" / "cross-checks.json"


def _cc(id_, quantity, a, b, comment, rel_only=False):
    """a, b: dict(source, value, unit, year). rel_only: do not republish the absolute values (licence), only the relative difference."""
    va, vb = a["value"], b["value"]
    rel = None if (va in (None, 0) or vb is None) else 100.0 * (vb - va) / va
    out = {"id": id_, "quantity": quantity, "a": dict(a), "b": dict(b), "difference_b_minus_a_pct": r(rel, 3), "comment": comment}
    for k in ("a", "b"):
        if out[k].get("republishable") is False:
            out[k]["value"] = "not republished (licence)"
        out[k].pop("republishable", None)
    return out


def compute_cross_checks(ctx: Ctx):
    cc = []
    def L(rel):  # the already built series (in memory), built on demand
        return ctx_cache.setdefault(rel, build_one(ctx, rel)["data"])
    ctx_cache: dict = {}
    # 1. pinned FaIR files: re-downloaded copies equal the pins of f3/data/fair_inputs.py
    pins = {"calibrated_constrained_parameters_calibration1.4.1.csv": "7b6c5d9fa0b0b0d3eb47189bf5d63cbf77e752ddac682947abee5ff529206780", "species_configs_properties_calibration1.4.1.csv": "42d04aa1a8f385cc53eae22beab26f857c535c5aa7dfdb98176d712bfc0c95a0",
            "volcanic_solar.csv": "621b551dafa6ff0e5a789b94a81a12876d796832c0e15f627545af40d6de58e5", "extensions_1750-2500.csv": "fcf994bb97bd08aae04bb4373ee7b8639e007f44055af1aa3d458aefc14b61ae"}
    same = {n: ctx.files.get(f"fair_inputs/{n}", {}).get("sha256") == h for n, h in pins.items()}
    cc.append({"id": "fair_pins", "quantity": "sha256 of the four FaIR input files, re-downloaded from the pinned commit vs the pins in f3/data/fair_inputs.py", "a": {"source": "f3/data/fair_inputs.py", "value": "pins"}, "b": {"source": "fair_inputs (this campaign)", "value": "re-download"},
               "difference_b_minus_a_pct": None, "comment": f"identical for all four files: {all(same.values())} ({same})"})
    # 2. HadCRUT5: same file as D-057
    hist = json.loads((REPO / "audit" / "data" / "sources-history.json").read_text(encoding="utf-8"))["sources"]
    cc.append({"id": "hadcrut5_sha", "quantity": "sha256 of HadCRUT.5.2.0.0 global annual summary: this campaign vs audit/data/sources-history.json", "a": {"source": "sources-history.json", "value": hist["hadcrut5"]["sha256"]},
               "b": {"source": "hadcrut5 (this campaign)", "value": ctx.files["hadcrut5/HadCRUT.5.2.0.0.analysis.summary_series.global.annual.csv"]["sha256"]}, "difference_b_minus_a_pct": None,
               "comment": "identical" if hist["hadcrut5"]["sha256"] == ctx.files["hadcrut5/HadCRUT.5.2.0.0.analysis.summary_series.global.annual.csv"]["sha256"] else "DIFFERENT"})
    cc.append({"id": "wpp_sha", "quantity": "sha256 of WPP2024_TotalPopulationBySex.csv.gz: this campaign vs sources-history.json", "a": {"source": "sources-history.json", "value": hist["wpp2024_totpop"]["sha256"]},
               "b": {"source": "wpp2024_totpop (this campaign)", "value": ctx.files["wpp2024_totpop/wpp2024_totpop.csv.gz"]["sha256"]}, "difference_b_minus_a_pct": None,
               "comment": "identical" if hist["wpp2024_totpop"]["sha256"] == ctx.files["wpp2024_totpop/wpp2024_totpop.csv.gz"]["sha256"] else "DIFFERENT"})
    h = L("hadcrut5_global_annual")
    cc.append({"id": "hadcrut5_offset", "quantity": "1850-1900 re-basing offset of HadCRUT5 (K)", "a": {"source": "sources-history.json (D-057)", "value": -0.3594, "unit": "K"}, "b": {"source": "hadcrut5_global_annual", "value": -h["offset_k"], "unit": "K"},
               "difference_b_minus_a_pct": 0.0, "comment": "same offset as D-057 (sign convention: subtracted)"})
    # 3. Ember: old long format vs new-format file, world total generation 2024 and 2025
    em = L("ember_electricity_world")["World"]
    g = pd.read_csv(ctx.verify("ember_release_global/release_generation_yearly_global.csv"), usecols=["Area", "Year", "Electricity source", "Generation (TWh)"])
    for yr in (2024, 2025):
        a = em["generation_total_twh"][em["years"].index(yr)]
        x = g[(g.Area == "World") & (g.Year == yr) & (g["Electricity source"].str.contains("Total", case=False))]
        b = float(x["Generation (TWh)"].iloc[0]) if len(x) else None
        cc.append(_cc(f"ember_total_gen_{yr}", f"World total generation {yr} (TWh): Ember old long format vs new format", {"source": "ember_yearly", "value": a, "unit": "TWh", "year": yr}, {"source": "ember_release_global", "value": b, "unit": "TWh", "year": yr},
                      "Same publisher, two download formats. The older long-format file is 0.5% lower than the July-2026-format file (a revision between releases); prefer the new format for generation, capacity and emissions. The new format has no demand series, so ember_electricity_world still takes demand from the older file."))
    # 4. IEA vs Ember: data-centre share of global electricity
    iea = {f["id"]: f for f in L("iea_energy_ai_figures")["facts"]}
    dem2024 = em["demand_twh"][em["years"].index(2024)]
    cc.append(_cc("dc_share_iea_vs_ember", "Data-centre share of world electricity, 2024 (%)", {"source": "iea_energy_ai (415 TWh / 'around 1.5%')", "value": 1.5, "unit": "%", "year": 2024},
                  {"source": "iea_energy_ai 415 TWh / ember_yearly world demand", "value": 100.0 * 415 / dem2024, "unit": "%", "year": 2024},
                  "The IEA's 1.5% rests on its own denominator (about 27,700 TWh implied); Ember's world demand (generation plus net imports, 30,912 TWh) is larger, which gives 1.3%. A scope difference in the denominator, not an error in either."))
    # 4b. scale: Epoch's tracked AI data centres vs the IEA's implied average load of all data centres
    epoch = L("epoch_data_centers_summary")
    cc.append(_cc("dc_scale_epoch_vs_iea", "Power: Epoch's 95 tracked frontier AI data centres (current MW) vs the IEA's average load implied by 415 TWh a year (MW)", {"source": "iea_energy_ai 415 TWh / 8760 h", "value": 415e6 / 8760.0, "unit": "MW (average)", "year": 2024},
                  {"source": "epoch_data_centers_summary current_total_power_mw", "value": epoch["current_total_power_mw"], "unit": "MW (nameplate/modelled, 2026-10)", "year": 2026},
                  "Different scope and date: the IEA figure is the average load of all data centres in 2024; Epoch's is the power of 95 large AI sites in late 2026. The ratio (about 0.3) says tracked frontier sites already reach roughly a third of the IEA's 2024 global average data-centre load, not that either is wrong."))
    # 5. IEA US data-centre electricity 2024 vs LBNL 2023 and LBNL's own share
    lb = " ".join(ctx.pdf_pages("lbnl_dc_2024/lbnl-2024-escholarship-qt32d6m0d1.pdf")) if "lbnl_dc_2024/lbnl-2024-escholarship-qt32d6m0d1.pdf" in ctx.files else ""
    lb_flat = _flat(lb)
    m = re.search(r"reaching (\d+) TWh by 2023, representing ([\d\.]+)% of total U\.S\. electricity", lb_flat)
    if m:
        cc.append(_cc("us_dc_iea_vs_lbnl", "US data-centre electricity: LBNL 2023 vs IEA 2024 (TWh)", {"source": "lbnl_dc_2024 (text: 176 TWh by 2023, 4.4% of US electricity)", "value": float(m.group(1)), "unit": "TWh", "year": 2023},
                      {"source": "iea_energy_ai (around 180 TWh in 2024)", "value": 180.0, "unit": "TWh", "year": 2024},
                      "Different years (IEA 2024 vs LBNL 2023). LBNL reports 176 TWh in 2023 (4.4% of US electricity); the IEA reports about 180 TWh in 2024 (more than 4%). LBNL projects 325 to 580 TWh in 2028, i.e. growth of 13% to 27% a year from 2023 (computed here from its text), so a 2024 value only 2% above 2023 is at odds with its own trajectory: the two use different scope or method. They agree at the order of magnitude, not to better than about 20%."))
    # 6. CO2 from fossil sources 2023: GCB vs OWID vs CEDS (EDGAR only as relative, licence)
    gcb = pd.read_csv(REPO / "f3" / "data" / "gcb2025_co2_2015_2024.csv", comment="#").set_index("year")
    gcb_co2 = {y: float(gcb.loc[y, "fossil_GtC"]) * 44.009 / 12.011 * 1000 for y in (2023, 2024)}
    ow = pd.read_csv(ctx.verify("owid_co2/owid-co2-data.csv"), usecols=["country", "year", "co2"])
    ow = ow[ow.country == "World"].set_index("year")["co2"]
    cd = L("ceds_global_emissions")["CO2"]
    cds23 = cd["total_kt"][cd["years"].index(2023)] / 1000.0
    cc.append(_cc("co2_gcb_vs_owid_2023", "World fossil CO2 emissions 2023 (Mt CO2): Global Carbon Budget 2025 vs Our World in Data", {"source": "gcb2025 extract (fossil_GtC x 3.664)", "value": gcb_co2[2023], "unit": "Mt CO2", "year": 2023},
                  {"source": "owid_co2 world 'co2' column", "value": float(ow.get(2023, float('nan'))), "unit": "Mt CO2", "year": 2023}, "OWID's world CO2 is built on the Global Carbon Project; they should agree to rounding (OWID may include cement carbonation, which GCB reports separately)."))
    cc.append(_cc("co2_gcb_vs_ceds_2023", "World CO2 emissions 2023 (Mt CO2): Global Carbon Budget 2025 fossil vs CEDS v_2025_03_18 total", {"source": "gcb2025 extract", "value": gcb_co2[2023], "unit": "Mt CO2", "year": 2023},
                  {"source": "ceds_global_emissions CO2 (all sectors and fuels)", "value": cds23, "unit": "Mt CO2", "year": 2023}, "CEDS is a bottom-up inventory scaled to energy statistics; it includes cement process CO2 and international shipping and aviation. A small gap is expected."))
    import openpyxl
    wb = openpyxl.load_workbook(ctx.verify("edgar2025/EDGAR_2025_GHG_booklet_2025_fossilCO2only.xlsx"), read_only=True, data_only=True)
    ws = wb.worksheets[0]
    edgar_total = None
    hdr = None
    for row in ws.iter_rows(values_only=True):
        if hdr is None and row and "Country" in [str(c) for c in row[:3]]:
            hdr = [str(c) for c in row]
        if row and any(str(c) == "GLOBAL TOTAL" for c in row[:3]) and hdr:
            vals = {h: v for h, v in zip(hdr, row)}
            edgar_total = vals.get("2024") or vals.get("2024.0")
            break
    if edgar_total is None:  # fall back to the GHG workbook: sum of the CO2 sector rows for the global total
        wb2 = openpyxl.load_workbook(ctx.verify("edgar2025/EDGAR_2025_GHG_booklet_2025.xlsx"), read_only=True, data_only=True)
        w2 = wb2["GHG_by_sector_and_country"]
        it = w2.iter_rows(values_only=True)
        hh = next(it)
        edgar_total = sum(float(rw[-1]) for rw in it if rw[2] == "GLOBAL TOTAL" and rw[0] == "CO2" and rw[-1] is not None)
    cc.append(_cc("co2_gcb_vs_edgar_2024", "World fossil CO2 2024 (Mt CO2): Global Carbon Budget 2025 vs EDGAR/IEA", {"source": "gcb2025 extract", "value": gcb_co2[2024], "unit": "Mt CO2", "year": 2024},
                  {"source": "edgar2025_fossil_co2 (IEA-EDGAR CO2 v4)", "value": float(edgar_total), "unit": "Mt CO2", "year": 2024, "republishable": False}, "EDGAR values are CC BY-NC-ND, so only the relative difference is stored.", rel_only=True))
    wdi = json.loads(ctx.verify("wdi_calibration/EN.GHG.CO2.MT.CE.AR5.json").read_text(encoding="utf-8"))[1]
    w24 = [x["value"] for x in wdi if x["countryiso3code"] == "WLD" and x["date"] == "2024"]
    cc.append({"id": "wdi_co2_is_edgar", "quantity": "WDI EN.GHG.CO2.MT.CE.AR5 world 2024 vs EDGAR fossil CO2 2024", "a": {"source": "edgar2025_fossil_co2", "value": "not republished (licence)"}, "b": {"source": "wdi_calibration EN.GHG.CO2.MT.CE.AR5", "value": "not republished (licence)"},
               "difference_b_minus_a_pct": r(100.0 * (float(w24[0]) - float(edgar_total)) / float(edgar_total), 4) if w24 else None,
               "comment": "The World Bank indicator is the EDGAR (IEA-EDGAR) series: the two world totals agree to the digits shown. Because EDGAR states those CO2 data are CC BY-NC-ND, the WDI series is excluded from the derived world file."})
    # 7. EDGAR CH4 (mass) vs CEDS CH4 2023
    ed = L("edgar_global_non_co2_by_sector")
    iy = ed["years"].index(2023)
    ch4_edgar_mt = sum((v[iy] or 0) for v in ed["ch4_by_sector"].values()) / 28.0
    ch4_ceds_mt = L("ceds_global_emissions")["CH4"]["total_kt"][L("ceds_global_emissions")["CH4"]["years"].index(2023)] / 1000.0
    cc.append(_cc("ch4_edgar_vs_ceds_2023", "World methane 2023 (Mt CH4): EDGAR (CO2eq / 28, GWP-100 AR5) vs CEDS", {"source": "edgar_global_non_co2_by_sector (/28)", "value": ch4_edgar_mt, "unit": "Mt CH4", "year": 2023},
                  {"source": "ceds_global_emissions CH4", "value": ch4_ceds_mt, "unit": "Mt CH4", "year": 2023}, "EDGAR includes wildfire/biomass sectors differently; both are anthropogenic inventories."))
    # 8. WDI world population vs WPP
    wd = L("wdi_world_series")
    wp = L("wpp2024_world_population")
    for yr in (2023, 2024):
        a = wp["pop_1july_thousand"][wp["years"].index(yr)] * 1000
        b = wd["SP.POP.TOTL"]["values"][wd["SP.POP.TOTL"]["years"].index(yr)]
        cc.append(_cc(f"pop_wpp_vs_wdi_{yr}", f"World population {yr}: WPP 2024 (1 July) vs World Bank WDI", {"source": "wpp2024_world_population", "value": a, "unit": "persons", "year": yr}, {"source": "wdi_world_series SP.POP.TOTL", "value": b, "unit": "persons", "year": yr},
                      "WDI's population comes from several sources including WPP; mid-year vs year-end conventions explain small gaps."))
    # 9. cereal yield: FAOSTAT vs WDI 2023
    fa = L("faostat_world_cereals")["Cereals, primary"]
    a = fa["yield_kg_per_ha"][fa["years"].index(2023)]
    b = wd["AG.YLD.CREL.KG"]["values"][wd["AG.YLD.CREL.KG"]["years"].index(2023)]
    cc.append(_cc("cereal_yield_fao_vs_wdi_2023", "World cereal yield 2023 (kg/ha): FAOSTAT 'Cereals, primary' vs WDI AG.YLD.CREL.KG", {"source": "faostat_world_cereals", "value": a, "unit": "kg/ha", "year": 2023}, {"source": "wdi_world_series AG.YLD.CREL.KG", "value": b, "unit": "kg/ha", "year": 2023},
                  "WDI uses FAO data but its 'cereals' aggregate excludes some items (for example it covers wheat, rice, maize, barley, oats, rye, millet, sorghum and mixed grains); differences of about 1% are definitional."))
    # 10. labour share: ILO vs PWT 2019 (different definitions)
    pw = {x["year"]: x for x in L("pwt_labour_share")["by_year"]}
    il = {x["year"]: x for x in L("ilostat_labour_income_share")["by_year"]}
    cc.append(_cc("labour_share_pwt_vs_ilo_2019", "Cross-country median labour share 2019 (%): PWT 11.0 labsh x 100 vs ILO SDG 10.4.1", {"source": "pwt_labour_share median", "value": 100 * pw[2019]["median"], "unit": "% of GDP", "year": 2019},
                  {"source": "ilostat_labour_income_share median", "value": il[2019]["median_pct"], "unit": "% of GDP", "year": 2019}, "Different definitions and samples (PWT adjusts for self-employed income and covers 100-140 countries; the ILO series is modelled for about 185 countries); a gap of several percentage points is expected. Neither is 'the' labour share."))
    # 11. OWID AI compute vs Epoch: maximum 2025 training compute
    ow_ai = pd.read_csv(ctx.verify("owid_ai_compute/artificial-intelligence-training-computation.csv"))
    col = [c for c in ow_ai.columns if "training" in c.lower() and "comput" in c.lower()]
    ep = L("epoch_training_compute_by_year")["by_year"]
    ep25 = [x for x in ep if x["year"] == 2025][0]["max_flop"]
    if col and "day" in ow_ai.columns:
        ow_ai["y"] = pd.to_datetime(ow_ai["day"], errors="coerce").dt.year
        mx = ow_ai[ow_ai.y == 2025][col[0]].max() * 1e15
        cc.append(_cc("owid_vs_epoch_compute_2025", "Largest 2025 training run: Epoch AI notable models vs OWID series (FLOP)", {"source": "epoch_training_compute_by_year", "value": ep25, "unit": "FLOP", "year": 2025},
                      {"source": "owid_ai_compute (petaFLOP x 1e15)", "value": float(mx), "unit": "FLOP", "year": 2025}, "OWID's chart is a processed copy of the Epoch data set; the gap is the data vintage (the OWID export predates Epoch's latest update) and any filtering to the 'notable' list."))
    # 12. USGS MCS 2025 vs 2026: world mine production 2024 (revision between editions)
    if "usgs_mcs2025/mcs2025.pdf" in ctx.files:
        p25 = ctx.pdf_pages("usgs_mcs2025/mcs2025.pdf")
        p26 = L("usgs_mcs2026_world_production_reserves")
        for name, key, cols, _ in MCS_CFG:
            if key not in ("copper", "lithium", "cobalt", "nickel", "rare_earths", "graphite_natural"):
                continue
            t25 = parse_mcs_table(p25, name, cols[:2] if False else cols)
            v26 = p26[key]["world_total"].get("mine_2024", {}).get("value")
            v25 = (t25 or {}).get("world_total", {}).get("mine_2024", {}).get("value") if t25 else None
            cc.append(_cc(f"mcs_edition_{key}_2024", f"World mine production {key.replace('_', ' ')} 2024: MCS 2025 (estimate) vs MCS 2026 (revised)", {"source": "usgs_mcs2025", "value": v25, "unit": p26[key]["unit"], "year": 2024},
                          {"source": "usgs_mcs2026", "value": v26, "unit": p26[key]["unit"], "year": 2024}, "Revision between USGS editions; unresolved if the 2025 edition table could not be parsed with the same method."))
    return cc


def write_cross_checks(ctx: Ctx):
    cc = compute_cross_checks(ctx)
    CROSS_CHECKS_PATH.write_text(json.dumps({"schema_version": 1, "campaign": "D-058", "note": "Differences between two sources for the same quantity. Absolute values of NC-ND sources are not republished.", "items": cc}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return cc


# --- BUILDERS CONTINUE HERE ---


# ====================================================================================================================== command line
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("raw", nargs="?", default=os.environ.get("F3_DATA_RAW"))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--only", default="")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--cross-checks", action="store_true", help="recompute audit/data/cross-checks.json (second-source comparisons)")
    a = ap.parse_args(argv)
    if a.list:
        for k, b in BUILDERS.items():
            print(f"{k}: {b['title']}  <- {', '.join(b['sources'])}")
        return 0
    if not a.raw:
        print("give the raw folder as an argument or set F3_DATA_RAW", file=sys.stderr)
        return 2
    ctx = Ctx(Path(a.raw))
    if a.verify_only:
        bad = 0
        for rel, f in ctx.files.items():
            if not (ctx.raw / rel).is_file():
                print("missing", rel)
                continue
            try:
                ctx.verify(rel)
            except ChecksumError as e:
                bad += 1
                print("MISMATCH", e)
        print("verify done; mismatches:", bad)
        return 1 if bad else 0
    if a.cross_checks:
        cc = write_cross_checks(ctx)
        print(f"wrote {len(cc)} cross-checks to {CROSS_CHECKS_PATH}")
        return 0
    names = [n for n in a.only.split(",") if n] or list(BUILDERS)
    out = Path(a.out)
    built, skipped = [], []
    for n in names:
        try:
            doc = build_one(ctx, n)
        except Skip as e:
            skipped.append((n, str(e)))
            print(f"skip {n}: {e}")
            continue
        write_json(out / f"{n}.json", doc)
        built.append(n)
        print(f"built {n}")
    print(f"built {len(built)}, skipped {len(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
