"""Explorer observed-history data (D-057, Part A). Data and display layer only: no model code, no parameter.

Reads the raw downloads (kept OUTSIDE the repo, never committed), checks them, and writes
  * site/data/history.json              derived annual values + the FaIR hindcast band (what the page draws)
  * audit/data/sources-history.json     source, version, retrieval date, licence (quoted), URL, checksum of every file read

    F3_FAIR_DATA=<dir with the pinned FaIR files> PYTHONPATH=. uv run python site_src/history_build.py <raw dir>

<raw dir> holds: wpp2024_totpop.csv.gz, wb_gdp.json, hadcrut5_5200.csv, gistemp.csv (see sources-history.json for the URLs).
GISTEMP is a cross-check only: its licence statement was not found on the data page, so none of its values are published
(only the size of the difference to HadCRUT5 is recorded).
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

RETRIEVED = "2026-10-22"
WPP_LAST_ESTIMATE = 2023            # WPP 2024: estimates to 2023, medium-variant projection from 2024


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def merge_sources(entries: dict) -> None:
    p = REPO / "audit" / "data" / "sources-history.json"
    cur = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"sources": {}}
    cur["sources"].update(entries)
    cur["note"] = ("Every external series or file used by the Explorer's history overlay and warming map (D-057). Raw files are NOT committed; "
                   "the checksums identify exactly what was read. Licences are quoted from the page named in licence_url, not inferred.")
    p.write_text(json.dumps(cur, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def population(raw: Path):
    b = (raw / "wpp2024_totpop.csv.gz").read_bytes()
    rows = list(csv.DictReader(io.StringIO(gzip.decompress(b).decode("utf-8-sig"))))
    w = {int(r["Time"]): float(r["PopTotal"]) for r in rows if r["Location"] == "World" and r["Variant"] == "Medium"}
    yrs = [y for y in range(1950, 2026)]
    out = {"years": yrs, "billions": [round(w[y] / 1e6, 5) for y in yrs], "is_estimate": [y <= WPP_LAST_ESTIMATE for y in yrs]}
    src = {"wpp2024_totpop": {
        "series": "World total population, medium variant (estimates 1950-2023, projection 2024 onward), 1 July, 1950-2025",
        "name": "United Nations, DESA Population Division, World Population Prospects 2024, file WPP2024_TotalPopulationBySex",
        "version": "WPP 2024 (28th revision). A web search on the retrieval date found no newer revision (next revision reported as postponed to 2027 by a secondary site, not confirmed by the UN); an interim January 2026 update reported to correct Togo only was not checked in this file.",
        "retrieved": RETRIEVED,
        "url": "https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/WPP2024_TotalPopulationBySex.csv.gz",
        "landing_page": "https://population.un.org/wpp/",
        "licence": "CC BY 3.0 IGO",
        "licence_quote": "Figures and tables in this publication can be reproduced without prior permission under a Creative Commons license (CC BY 3.0 IGO), http://creativecommons.org/licenses/by/3.0/igo/",
        "licence_url": "https://population.un.org/wpp/assets/Files/WPP2024_Summary-of-Results.pdf",
        "licence_caveat": "The quoted sentence is from the WPP 2024 Summary of Results publication. A licence statement attached to the CSV file itself was not found (the data portal pages are script-rendered and could not be read); the UN's R-package mirror states the same CC BY 3.0 IGO for the data. Derived annual world totals are shown with attribution.",
        "redistribution": "derived annual world totals shown on the site, with attribution; the raw file (about 17 MB gz, all countries) is not committed",
        "attribution": "United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024. Used under CC BY 3.0 IGO. Values re-expressed in billions; no other change.",
        "file": "wpp2024_totpop.csv.gz", "sha256": sha(b), "bytes": len(b)}}
    return out, src


def gdp(raw: Path):
    b = (raw / "wb_gdp.json").read_bytes()
    d = json.loads(b)
    last_updated = d[0]["lastupdated"]
    v = {int(r["date"]): r["value"] for r in d[1] if r["value"] is not None and r["countryiso3code"] == "WLD"}
    yrs = sorted(y for y in v if 1960 <= y)
    out = {"years": yrs, "trillion_usd_2015": [round(v[y] / 1e12, 4) for y in yrs]}
    src = {"wb_wdi_gdp": {
        "series": "World GDP, constant 2015 US$ (NY.GDP.MKTP.KD), country code WLD, %d-%d" % (yrs[0], yrs[-1]),
        "name": "World Bank, World Development Indicators, indicator NY.GDP.MKTP.KD",
        "version": "WDI as served by the World Bank API on the retrieval date; API field lastupdated = %s" % last_updated,
        "retrieved": RETRIEVED,
        "url": "https://api.worldbank.org/v2/country/WLD/indicator/NY.GDP.MKTP.KD?format=json&per_page=200",
        "landing_page": "https://data.worldbank.org/indicator/NY.GDP.MKTP.KD",
        "licence": "CC BY 4.0 (the World Bank default licence for its open datasets)",
        "licence_quote": "The World Bank Group ... licenses datasets under the Creative Commons Attribution 4.0 International license (CC-BY 4.0). ... CC-BY 4.0, with the additional terms below, is the default license for all Datasets produced by the World Bank itself and distributed as open data.",
        "licence_url": "https://datacatalog.worldbank.org/public-licenses",
        "licence_caveat": "This is the default licence page; a dataset-specific statement for NY.GDP.MKTP.KD was not separately read.",
        "redistribution": "derived annual world totals shown on the site, with attribution",
        "attribution": "World Bank, World Development Indicators, NY.GDP.MKTP.KD (GDP, constant 2015 US$), World aggregate. Used under CC BY 4.0. Values re-expressed in trillions of dollars and shown as an index (1990 = 1) on the chart.",
        "file": "wb_gdp.json", "sha256": sha(b), "bytes": len(b)}}
    return out, src


def hadcrut(raw: Path):
    b = (raw / "hadcrut5_5200.csv").read_bytes()
    rows = [l.split(",") for l in b.decode("utf-8").strip().splitlines()[1:]]
    arr = {int(r[0]): tuple(map(float, r[1:4])) for r in rows}
    base = float(np.mean([arr[y][0] for y in range(1850, 1901)]))
    return arr, base, b


def gistemp_crosscheck(raw: Path, had, had_base):
    b = (raw / "gistemp.csv").read_bytes()
    lines = b.decode("utf-8").splitlines()
    hdr = next(i for i, l in enumerate(lines) if l.startswith("Year,"))
    g = {}
    for r in csv.DictReader(lines[hdr:]):
        try:
            g[int(r["Year"])] = float(r["J-D"])
        except (ValueError, KeyError):
            pass
    # each re-based to its own 1880-1900 mean (GISTEMP starts in 1880), so only shape and drift are compared
    gb = np.mean([g[y] for y in range(1880, 1901)])
    hb = np.mean([had[y][0] for y in range(1880, 1901)])
    yrs = [y for y in range(1880, 2026) if y in g]
    d = np.array([(g[y] - gb) - (had[y][0] - hb) for y in yrs])
    last = {y: round(float((g[y] - gb) - (had[y][0] - hb)), 3) for y in (2015, 2020, 2023, 2024, 2025) if y in g}
    res = {"years": [yrs[0], yrs[-1]], "mean_abs_diff_K": round(float(np.mean(np.abs(d))), 3), "max_abs_diff_K": round(float(np.max(np.abs(d))), 3),
           "max_abs_diff_year": int(yrs[int(np.argmax(np.abs(d)))]), "diff_2015_2025_mean_K": round(float(np.mean([x for y, x in zip(yrs, d) if y >= 2015])), 3),
           "gistemp_minus_hadcrut_by_year_K": last,
           "reading": "Both series re-based to their own 1880-1900 mean; difference = GISTEMP minus HadCRUT5, annual J-D. Cross-check only; no GISTEMP value is published on the site."}
    src = {"gistemp_v4": {
        "series": "GISTEMP v4 Land-Ocean Temperature Index, global annual mean (J-D), relative to 1951-1980, used for a cross-check only",
        "name": "NASA GISS Surface Temperature Analysis (GISTEMP v4), table GLB.Ts+dSST.csv",
        "version": "GISTEMP v4, file as served on the retrieval date (file contains a partial year 2026, not used)",
        "retrieved": RETRIEVED,
        "url": "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
        "landing_page": "https://data.giss.nasa.gov/gistemp/",
        "licence": "NOT STATED on the pages read. The GISTEMP page asks for citation and states that graphics created with its tools need no permission but should credit NASA GISS; it makes no statement about redistributing the data table.",
        "licence_quote": "Graphics from these GISTEMP pages are subject to NASA Image and Media guidance. ... graphics you may create using the website tools here do not require permission for you to use elsewhere, but acknowledgment of their source should be given.",
        "licence_url": "https://data.giss.nasa.gov/gistemp/",
        "redistribution": "NO values published. Used only to compute the size of the difference to HadCRUT5 (recorded in this file under crosscheck).",
        "citation": "GISTEMP Team, 2026: GISS Surface Temperature Analysis (GISTEMP), version 4. NASA Goddard Institute for Space Studies. Dataset accessed 2026-10-22 at https://data.giss.nasa.gov/gistemp/. Lenssen et al. (2024), J. Geophys. Res. Atmos. 129, e2023JD040179, doi:10.1029/2023JD040179.",
        "file": "gistemp.csv", "sha256": sha(b), "bytes": len(b), "crosscheck": res}}
    return res, src


def fair_hindcast():
    """841-member FaIR hindcast, calendar years 1850-2025, K above 1850-1900 (same method as tests/fair_checks.fair_calendar_year; run to 2026
    so the calendar year 2025 exists). Same published configuration as the D-021 recording; nothing is tuned."""
    from f3.sectors.s6_climate import ClimateSetup, anomaly_on_bounds, run_fair
    f = run_fair(2026, ClimateSetup())
    a = anomaly_on_bounds(f)
    tb = np.asarray(f.timebounds)
    cal = 0.5 * (a[:-1] + a[1:])
    years = [int(y) for y in tb[:-1]]
    i0 = years.index(1850)
    cal = cal[i0:]
    years = years[i0:]
    return years, cal, a.shape[1]


def main(raw: Path) -> None:
    pop, s1 = population(raw)
    g, s2 = gdp(raw)
    had, base, hb = hadcrut(raw)
    cross, s3 = gistemp_crosscheck(raw, had, base)
    years, cal, nmem = fair_hindcast()
    yrs = [y for y in years if y <= 2025]
    em = cal.mean(axis=1)
    idx = {y: i for i, y in enumerate(years)}
    temp = {
        "years": yrs,
        "hadcrut5": [round(had[y][0] - base, 4) for y in yrs],
        "hadcrut5_lower": [round(had[y][1] - base, 4) for y in yrs],
        "hadcrut5_upper": [round(had[y][2] - base, 4) for y in yrs],
        "fair_mean": [round(float(em[idx[y]]), 4) for y in yrs],
        "fair_p05": [round(float(np.quantile(cal[idx[y]], 0.05)), 4) for y in yrs],
        "fair_p95": [round(float(np.quantile(cal[idx[y]], 0.95)), 4) for y in yrs],
    }
    s4 = {"hadcrut5": {
        "series": "HadCRUT5 global annual mean temperature anomaly with 95%% limits, 1850-2025 (2026 is a partial year, not used), re-based to the mean of the annual best estimates 1850-1900 (offset %.4f K subtracted)" % base,
        "name": "Met Office Hadley Centre / Climatic Research Unit, HadCRUT.5.2.0.0, analysis summary series, global, annual",
        "version": "HadCRUT.5.2.0.0 (the site states it was updated to 5.2.0.0 on 2026-09-18)",
        "retrieved": RETRIEVED,
        "url": "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.2.0.0/analysis/diagnostics/HadCRUT.5.2.0.0.analysis.summary_series.global.annual.csv",
        "landing_page": "https://www.metoffice.gov.uk/hadobs/hadcrut5/",
        "licence": "Open Government Licence v3.0 (Crown copyright)",
        "licence_quote": "HadCRUT5 is subject to Crown copyright protection and is provided under the Open Government License v3. ... A term of the licence is that users must include the following acknowledgement when the data are used: HadCRUT.[version number] data were obtained from http://www.metoffice.gov.uk/hadobs/hadcrut5 on [date downloaded] and are (c) British Crown Copyright, Met Office [year of first publication], provided under an Open Government License, http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "licence_url": "https://www.metoffice.gov.uk/hadobs/hadcrut5/terms_and_conditions.html",
        "redistribution": "permitted with the acknowledgement; derived annual values (re-based) are shown",
        "attribution": "HadCRUT.5.2.0.0 data were obtained from http://www.metoffice.gov.uk/hadobs/hadcrut5 on 2026-10-22 and are (c) British Crown Copyright, Met Office (year of first publication not stated on the pages read), provided under an Open Government License, http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/. Morice et al. (2021), J. Geophys. Res. Atmos. 126, e2019JD032361, doi:10.1029/2019JD032361.",
        "file": "hadcrut5_5200.csv", "sha256": sha(hb), "bytes": len(hb),
        "note": "Identical (same sha256) to the file in the local cache used by the A2.1 report; the A2.1 pin covers rows to 2024, the 2025 row is new."},
        "fair_hindcast": {
        "series": "FaIR 2.2.4 hindcast, %d members, calendar years 1850-2025, K above 1850-1900 (mean, 5th and 95th percentile of members)" % nmem,
        "name": "F3 run: FaIR 2.2.4 (Apache 2.0, unmodified), fair-calibrate v1.4.1 constrained ensemble as published, same configuration as the D-021 recording, started in 1750, run to 2026",
        "version": "see audit/data/explorer provenance (explorer.json meta.provenance): FaIR files pinned by sha256",
        "retrieved": RETRIEVED, "url": "(computed here)", "licence": "F3 output; docs and processed data CC BY 4.0 (D-001)",
        "redistribution": "yes", "note": "Emissions from 2025 are the prescribed medium-extension scenario (CO2 from GCB 2025 to 2024); non-CO2 emissions are prescribed, not modelled (D-021). Calendar year = mean of the time bounds at the start and end of the year, as in A2.1."}}
    hist = {
        "meta": {
            "decision": "D-057", "retrieved": RETRIEVED, "temperature_baseline": "1850-1900 (mean of the annual HadCRUT5 best estimates; FaIR anomalies use the notebook's weighted 1850-1900 mean)",
            "temperature_baseline_offset_K": round(base, 4), "wpp_last_estimate_year": WPP_LAST_ESTIMATE, "fair_members": nmem,
            "gistemp_crosscheck": cross,
            "units": {"population": "billions of people (UN WPP, 1 July)", "gdp": "trillion constant-2015 US$ (World Bank)", "temperature": "K above 1850-1900"},
            "attribution": [v["attribution"] for v in (s1["wpp2024_totpop"], s2["wb_wdi_gdp"], s4["hadcrut5"])],
        },
        "population": pop, "gdp": g, "temperature": temp,
    }
    (REPO / "site" / "data" / "history.json").write_text(json.dumps(hist, separators=(",", ":")), encoding="utf-8", newline="\n")
    merge_sources({**s1, **s2, **s3, **s4})
    print("wrote site/data/history.json; years", pop["years"][0], pop["years"][-1], g["years"][0], g["years"][-1], temp["years"][0], temp["years"][-1])
    print("hadcrut offset", base, "gistemp cross-check", {k: v for k, v in cross.items() if k != "gistemp_minus_hadcrut_by_year_K"})
    print("fair 2025 mean/p05/p95", temp["fair_mean"][-1], temp["fair_p05"][-1], temp["fair_p95"][-1], "hadcrut 2025", temp["hadcrut5"][-1], temp["hadcrut5_lower"][-1], temp["hadcrut5_upper"][-1])


if __name__ == "__main__":
    main(Path(sys.argv[1]))
