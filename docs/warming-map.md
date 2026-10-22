# Warming map: method, fixed before the coefficients were computed (D-057, Part B)

Illustrative downscaling of the global FaIR result. **Not a regional climate projection.** Pattern-scaling ignores regional feedbacks, aerosols and ocean dynamics.

## Method
regional warming(year, run) = global warming(year, run) x c_r, where c_r is the multi-model-mean regression slope of region r's annual mean near-surface air temperature on the global annual mean (K per K), and global warming is the recorded FaIR 841-member result already in `site/data/explorer.json` (ensemble mean, 5th and 95th percentile). Only the global uncertainty is shown. Pattern uncertainty (the spread of c_r across models) is stored in the file (`c_sd`) but not drawn, and the page says so. Warming is above 1850-1900 in FaIR, so the regional value is also "above 1850-1900" under the proportionality assumption (intercept ignored).

## Pattern source (chosen)
IPCC AR6 WGI Atlas repository, `datasets-aggregated-regionally`, CMIP6 monthly regional means of near-surface air temperature (`tas`) over the 58 AR6 reference regions plus a `world` column (CC BY 4.0 under the CMIP6 terms of use, quoted in `audit/data/sources-history.json`). Pinned to the repository commit recorded there. One run per model; models with historical + SSP1-2.6 + SSP2-4.5 + SSP5-8.5 only; SSP3-7.0 is not used. No gridded pattern file with a redistributable licence was found, so the fallback in the brief applies: **AR6 reference regions, with slopes derived here from the published regional aggregates** (the Atlas does not publish the slopes themselves; the derivation is ours and is labelled so). Polygons: IPCC-WGI-reference-regions-v4.geojson from the same repository (CC BY 4.0), simplified. Coastlines: Natural Earth 110 m land (public domain), simplified.

## Computation (fixed now)
1. Per model and scenario: annual means of the monthly values (calendar year). Series = historical 1850-2014 followed by the scenario 2015-2100.
2. Region series: `Type` Land -> land-only file; Ocean -> sea-only file; Land-Ocean -> land-and-sea file. Global series: `world` of the land-and-sea file. The `world` value is a land-and-sea near-surface air temperature, FaIR's temperature is the model's surface temperature anomaly: the two are treated as the same quantity, which is an assumption.
3. Per model: ordinary least squares of the region annual mean on the global annual mean, with intercept, pooled over the three scenarios (each scenario = its historical segment + its future segment; the historical segment enters once per scenario).
4. c_r = mean over models of the slope; c_sd = standard deviation over models; n models stored.
5. No smoothing, no rescaling, no adjustment to improve the check below.

## Checks fixed now
* **Global-mean consistency:** area-weighted mean over all 58 regions of c_r, weights = spherical area of the region polygon, must equal 1 within 2% (so that area-weighted regional warming equals global warming). Reported as computed. If it fails it is recorded as a failure, with the size, and **no coefficient is rescaled**. Also reported as a diagnostic: the same check using the land-and-sea file for every region (shows how much of any gap is due to mixing land-only and sea-only values over polygons that contain both).
* Schema test of `site/data/warming-map.json`; every region in the file has a polygon and a coefficient; the sentence under the map is generated from the data.
* Polar amplification and land-ocean contrast must show (sign test): c in the Arctic Ocean region ARO > 1; c over land regions on average > c over ocean regions. Reported as computed; a failure is recorded, not fixed.
