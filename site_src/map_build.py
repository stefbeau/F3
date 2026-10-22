"""Explorer warming map data (D-057, Part B). Method fixed in docs/warming-map.md before this ran. Data and display layer only.

    PYTHONPATH=. uv run python site_src/map_build.py <atlas dir> <natural-earth dir>

<atlas dir>: the pinned downloads of the IPCC-WG1/Atlas repository (regions.geojson, land__*.csv, sea__*.csv, landsea__*.csv, manifest.json).
<natural-earth dir>: ne_110m_land.geojson and ne_sha.txt.
Writes site/data/warming-map.json, audit/data/warming-map-check.json, audit/data/atlas-cmip6-files.json; merges source entries into audit/data/sources-history.json.
Coefficients are NOT rescaled or adjusted; the global-mean check is reported as computed.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from history_build import merge_sources, sha  # noqa: E402

SCEN = ["ssp126", "ssp245", "ssp585"]
R_EARTH_KM = 6371.0088
LABEL = ("Illustrative downscaling of the global FaIR result. Not a regional climate projection. "
         "Pattern-scaling ignores regional feedbacks, aerosols, ocean dynamics.")


def read_annual(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path, comment="#")
    d["year"] = d["date"].str.slice(0, 4).astype(int)
    return d.drop(columns="date").groupby("year").mean()


def ring_area_km2(ring) -> float:
    """Signed spherical-ish area of a lon/lat ring (edges taken as straight in lon/lat): R^2/2 * sum (dlon)(sin lat1 + sin lat2)."""
    a = 0.0
    for (x1, y1), (x2, y2) in zip(ring[:-1], ring[1:]):
        a += math.radians(x2 - x1) * (math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return a * R_EARTH_KM ** 2 / 2


def polys(geom):
    return [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]


def region_area(geom) -> float:
    tot = 0.0
    for poly in polys(geom):
        tot += abs(ring_area_km2(poly[0])) - sum(abs(ring_area_km2(h)) for h in poly[1:])
    return tot


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    p = np.asarray(pts, float)
    keep = np.zeros(len(p), bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(p) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = p[i], p[j]
        ab = b - a
        n = np.hypot(*ab)
        seg = p[i + 1:j]
        d = np.hypot(*(seg - a).T) if n == 0 else np.abs(ab[0] * (seg[:, 1] - a[1]) - ab[1] * (seg[:, 0] - a[0])) / n
        k = int(np.argmax(d))
        if d[k] > eps:
            keep[i + 1 + k] = True
            stack += [(i, i + 1 + k), (i + 1 + k, j)]
    return p[keep].tolist()


def split_long_edges(ring):
    """No edge may span more than 180 degrees of longitude (2026-10-22 check). The only such edges in the source are full-width edges ALONG a pole
    (lat -90 or 90 at both ends, -180 to 180: the Antarctic and Arctic caps); they are not antimeridian wraps and are kept, but split at longitude 0
    so a renderer that interpolates the short way round cannot smear them. Any other long edge is a real antimeridian crossing: fail the build."""
    out = [ring[0]]
    for prev, cur in zip(ring, ring[1:]):
        if abs(cur[0] - prev[0]) > 180:
            if not (abs(prev[1]) == 90 and prev[1] == cur[1]):
                raise ValueError("polygon edge crosses the antimeridian away from a pole: %r -> %r (split the polygon at 180 degrees)" % (prev, cur))
            out.append([0.0, prev[1]])
        out.append(cur)
    return out


def simp_rings(rings, eps):
    out = []
    for r in rings:
        s = rdp(r, eps)
        if len(s) >= 4 and abs(ring_area_km2(s)) > 5e4:
            out.append(split_long_edges([[round(x, 1), round(y, 1)] for x, y in s]))
    return out


def main(atlas: Path, ne: Path) -> None:
    man = json.loads((atlas / "manifest.json").read_text(encoding="utf-8"))
    gj = json.loads((atlas / "regions.geojson").read_text(encoding="utf-8"))
    feats = {f["properties"]["Acronym"]: f for f in gj["features"]}
    acr = list(feats)
    kind_of = {a: {"Land": "land", "Ocean": "sea", "Land-Ocean": "landsea"}[feats[a]["properties"]["Type"]] for a in acr}

    slopes = {a: [] for a in acr}                # one slope per model
    slopes_ls = {a: [] for a in acr}             # diagnostic: land-and-sea file for every region
    used = []
    for mod in man["models"]:
        def f(kind, exp):
            hit = [x for x in man["files"] if x[0].startswith(kind + "__CMIP6_" + mod + "_" + exp + "_")]
            assert len(hit) == 1, (kind, mod, exp, hit)
            return atlas / hit[0][0]
        X, Y, Yls = [], {a: [] for a in acr}, {a: [] for a in acr}
        for s in SCEN:
            cols = {}
            ann = {k: pd.concat([read_annual(f(k, "historical")), read_annual(f(k, s))]) for k in ("land", "sea", "landsea")}
            ann = {k: v[~v.index.duplicated(keep="last")].sort_index() for k, v in ann.items()}
            g = ann["landsea"]["world"]
            X.append(g.values)
            for a in acr:
                Y[a].append(ann[kind_of[a]][a].values)
                Yls[a].append(ann["landsea"][a].values)
        x = np.concatenate(X)
        for a in acr:
            for store, src in ((slopes, Y), (slopes_ls, Yls)):
                y = np.concatenate(src[a])
                ok = np.isfinite(x) & np.isfinite(y)
                xc = x[ok] - x[ok].mean()
                store[a].append(float((xc * (y[ok] - y[ok].mean())).sum() / (xc ** 2).sum()))
        used.append(mod)

    c = {a: float(np.mean(slopes[a])) for a in acr}
    csd = {a: float(np.std(slopes[a], ddof=1)) for a in acr}
    cls_ = {a: float(np.mean(slopes_ls[a])) for a in acr}
    area = {a: region_area(feats[a]["geometry"]) for a in acr}
    tot = sum(area.values())
    sphere = 4 * math.pi * R_EARTH_KM ** 2
    wmean = sum(area[a] * c[a] for a in acr) / tot
    wmean_ls = sum(area[a] * cls_[a] for a in acr) / tot
    permodel = [sum(area[a] * slopes[a][i] for a in acr) / tot for i in range(len(used))]
    land = [a for a in acr if feats[a]["properties"]["Type"] != "Ocean"]
    ocean = [a for a in acr if feats[a]["properties"]["Type"] == "Ocean"]
    land_mean = sum(area[a] * c[a] for a in land) / sum(area[a] for a in land)
    ocean_mean = sum(area[a] * c[a] for a in ocean) / sum(area[a] for a in ocean)
    check = {
        "rule": "area-weighted mean of c_r over all regions must be 1 within 2% (docs/warming-map.md); no coefficient is rescaled",
        "area_weighted_mean_c": round(wmean, 4), "deviation_from_1_pct": round((wmean - 1) * 100, 2), "passes_2pct": abs(wmean - 1) <= 0.02,
        "diagnostic_landsea_file_for_every_region": {"area_weighted_mean_c": round(wmean_ls, 4), "deviation_from_1_pct": round((wmean_ls - 1) * 100, 2)},
        "per_model_area_weighted_mean_c": {"min": round(min(permodel), 3), "median": round(float(np.median(permodel)), 3), "max": round(max(permodel), 3)},
        "polygon_area_covers_fraction_of_sphere": round(tot / sphere, 4),
        "sign_tests": {"ARO_c_gt_1": c["ARO"] > 1, "ARO_c": round(c["ARO"], 3), "land_mean_c": round(land_mean, 3), "ocean_mean_c": round(ocean_mean, 3), "land_gt_ocean": land_mean > ocean_mean},
        "models_used": used, "n_models": len(used),
        "spread": {"c_min": round(min(c.values()), 3), "c_max": round(max(c.values()), 3), "arg_min": min(c, key=c.get), "arg_max": max(c, key=c.get)},
    }

    ne_geo = json.loads((ne / "ne_110m_land.geojson").read_text(encoding="utf-8"))
    coast = []
    for ft in ne_geo["features"]:
        coast += simp_rings([p[0] for p in polys(ft["geometry"])], 0.4)
    regions = []
    for a in acr:
        pr = feats[a]["properties"]
        rings = []
        for poly in polys(feats[a]["geometry"]):
            rings.append(simp_rings(poly, 0.6))
        regions.append({"id": a, "name": pr["Name"], "type": pr["Type"], "c": round(c[a], 3), "c_sd": round(csd[a], 3), "area_km2": round(area[a]),
                        "polys": [r for r in rings if r]})
    out = {
        "meta": {
            "decision": "D-057", "label": LABEL, "method": "regional warming = global FaIR warming x c_r (K per K, multi-model-mean OLS slope of region annual mean on global annual mean, intercept ignored)",
            "pattern_source": "IPCC AR6 WGI Atlas repository, CMIP6 regionally aggregated monthly tas (CC BY 4.0), commit " + man["atlas_commit"] + "; slopes derived by F3 (docs/warming-map.md)",
            "n_models": len(used), "scenarios": SCEN, "regions": "IPCC AR6 reference regions v4: %d land (incl. 3 land-ocean) and %d ocean" % (len(land), len(ocean)),
            "pattern_uncertainty_shown": False, "pattern_uncertainty_note": "c_sd (spread of the slope across models) is stored but not drawn; the uncertainty shown is the global FaIR uncertainty only",
            "check": check, "attribution": ["IPCC-WG1/Atlas (Iturbide et al. 2022, Sci. Data 9, 629), CC BY 4.0, CMIP6 terms of use acknowledged on the Sources page", "Natural Earth (public domain)"],
        },
        "regions": regions, "coast": coast,
    }
    (REPO / "site" / "data" / "warming-map.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8", newline="\n")
    (REPO / "audit" / "data" / "warming-map-check.json").write_text(json.dumps(check, indent=1) + "\n", encoding="utf-8", newline="\n")
    (REPO / "audit" / "data" / "atlas-cmip6-files.json").write_text(json.dumps({"atlas_commit": man["atlas_commit"], "files": [[n, s, b] for n, s, b, _ in man["files"]]}) + "\n", encoding="utf-8", newline="\n")
    neb = (ne / "ne_110m_land.geojson").read_bytes()
    merge_sources({
        "ipcc_ar6_atlas_cmip6": {
            "series": "CMIP6 monthly near-surface air temperature averaged over the AR6 reference regions (land, sea and land-sea files) for %d models, historical + SSP1-2.6, SSP2-4.5, SSP5-8.5, one run per model, plus the region polygons" % len(used),
            "name": "IPCC-WG1/Atlas, datasets-aggregated-regionally/data/CMIP6/CMIP6_tas_{land,sea,landsea} and reference-regions/IPCC-WGI-reference-regions-v4.geojson",
            "version": "repository commit " + man["atlas_commit"] + " (2026-06-11)", "retrieved": "2026-10-22",
            "url": "https://github.com/IPCC-WG1/Atlas/tree/" + man["atlas_commit"], "landing_page": "https://github.com/IPCC-WG1/Atlas",
            "licence": "CC BY 4.0 for the datasets (CMIP6 aggregated data under the CMIP6 terms of use); Apache 2.0 for code",
            "licence_quote": "All datasets and notebooks in this repository are provided under the Creative Commons Attribution 4.0 license (CC BY 4.0). Code are licensed under the Apache License, Version 2.0, unless otherwise explicitly stated. ... The CMIP6 aggregated dataset in this repository is distributed under the CC BY 4.0 under the CMIP6 terms of use.",
            "licence_url": "https://github.com/IPCC-WG1/Atlas/blob/" + man["atlas_commit"] + "/LICENSE.md",
            "redistribution": "only the derived coefficients (one number per region) and simplified region outlines are published; the 385 raw CSV files (about 170 MB) are not committed. Per-file checksums: audit/data/atlas-cmip6-files.json",
            "attribution": "Iturbide, M., Fernandez, J., Gutierrez, J.M. et al. Implementation of FAIR principles in the IPCC: the WGI AR6 Atlas repository. Sci Data 9, 629 (2022), doi:10.1038/s41597-022-01739-y. IPCC (2023) Atlas, in Climate Change 2021, doi:10.1017/9781009157896.021. We acknowledge the World Climate Research Programme, which, through its Working Group on Coupled Modelling, coordinated and promoted CMIP6; the climate modelling groups for producing and making available their model output; the ESGF for archiving the data; and the funding agencies who support CMIP6 and ESGF.",
            "models": used, "manifest_sha256": sha((atlas / "manifest.json").read_bytes()),
            "note": "The slopes are computed by F3 from these aggregates; the Atlas does not publish pattern-scaling coefficients."},
        "natural_earth_110m_land": {
            "series": "Natural Earth 1:110m physical vectors, land polygons (coastlines), simplified for the map",
            "name": "Natural Earth ne_110m_land (nvkelso/natural-earth-vector, geojson/ne_110m_land.geojson)",
            "version": "repository commit " + (ne / "ne_sha.txt").read_text().strip(), "retrieved": "2026-10-22",
            "url": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/" + (ne / "ne_sha.txt").read_text().strip() + "/geojson/ne_110m_land.geojson",
            "landing_page": "https://www.naturalearthdata.com/",
            "licence": "Public domain",
            "licence_quote": "All versions of Natural Earth raster + vector map data found on this website are in the public domain. You may use the maps in any manner, including modifying the content and design, electronic dissemination, and offset printing.",
            "licence_url": "https://www.naturalearthdata.com/about/terms-of-use/",
            "redistribution": "yes (simplified outlines in site/data/warming-map.json)", "attribution": "Made with Natural Earth.",
            "file": "ne_110m_land.geojson", "sha256": sha(neb), "bytes": len(neb)}})
    print(json.dumps(check, indent=1))
    print("size bytes", (REPO / "site" / "data" / "warming-map.json").stat().st_size)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
