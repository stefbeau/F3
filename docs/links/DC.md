# DC — Data-centre module: constraints and AI context (draft, D-058)

**Status of this page:** data and literature plan, written before any code or test run. No result is reported. Provisional (delegated). Link numbering as in L3.md. The module is D-032 (boundary, IEA descriptive) and D-033 (form, calibration, supply, coupling), Track A, branch `track-a`; this page lists what the campaign found to constrain it. It changes neither.

## What must connect
Compute (S3) to data-centre electricity and cooling water (S4/S5), bounded by electricity supply, chip-critical minerals and water. The module compares its `E_dc` with the IEA's totals on the descriptive boundary of D-032.

## Candidate variables and units, with sources
| Variable | Unit | Source |
|---|---|---|
| Global data-centre electricity | TWh/yr | IEA Energy and AI (CC BY 4.0 report): 415 TWh in 2024, 1.5% of world electricity; Base Case 945 TWh in 2030, about 1,200 in 2035; Lift-Off over 1,260 (2030); High Efficiency about 800 (2030); Headwinds about 670 (2030); 2035 range 700 to 1,720. `iea_energy_ai_figures` holds 16 facts, each with PDF page |
| Regional split | share | IEA: US 45%, China 25%, Europe 15%; US 180 TWh |
| PUE | ratio | IEA 1.41 to 1.29 |
| US data-centre electricity | TWh | LBNL 2024: 176 TWh in 2023 (4.4% of US electricity); 325 to 580 TWh in 2028 (PDF, no open licence: cite page only) |
| Direct and indirect water | litres | LBNL: direct 21.2 billion litres (2014 scope), indirect about 800 billion litres; Li et al. 2023 "Making AI less thirsty" [from memory, unverified] |
| Frontier data centres | MW, GW timeline | `epoch_data_centers_summary` (95 sites, 2018-2030 timelines) |
| Chip stock and hardware efficiency | H100e; FLOP/J | `epoch_ai_chip_stock_quarterly`, `epoch_hardware_efficiency` |
| Foundry and packaging | wafers, energy | TSMC sustainability report (unclear licence, cite only) |
| Hyperscaler electricity and water | TWh, m3 | Google, Microsoft, Meta, Amazon 2025 reports (unclear licence, cite by page; no derived file) |
| Water stress | index | `aqueduct_water_stress_by_country` (Aqueduct 4.0, CC BY 4.0) |
| Critical minerals | kt | `iea_critical_minerals_demand` (copper and lithium: 2025 edition, STEPS; cobalt: 2024 edition, APS), `usgs_mcs2026_world_production_reserves` (8 commodities; copper 23,000 kt, lithium 222,000 t, cobalt 302,000 t in 2024) |
| Grid CO2 intensity | gCO2/kWh | `ember_electricity_world` |

## Functional forms in the literature
1. Energy = chips x power x utilisation x PUE, with chip stock as the state (Epoch; LBNL) [from memory, unverified].
2. Water = energy x water usage effectiveness (on-site) plus energy x grid water intensity (off-site) (Li et al. 2023) [from memory, unverified].
3. Supply limit: demand clipped by available electricity, with a delay to grid connection; Epoch's site timelines give the lead time empirically.
4. Scenario spread rather than a point: IEA's four cases bracket 2030 at roughly 670 to over 1,260 TWh.

## Calibration data and what is missing
- **Available:** one 2024 global level and four 2030 scenario values (IEA), one US history to 2023 and a 2028 range (LBNL), Epoch's site and chip data, company reports.
- **Missing:** IEA regional spreadsheets (login), a second global estimate, a water time series, measured utilisation, the formal IEA boundary (D-032: could not be verified), data-centre mineral intensity per MW (not found).
- **Tension recorded:** the IEA share 1.5% versus 1.34% on Ember's denominator (10% gap); Epoch's 95 frontier sites are about 70% below the IEA average load (different scope).
- **Not committed:** anything from LBNL, TSMC or the corporate reports.

## Pass/fail test (written without results)
1. 2024 modelled global `E_dc` within a pre-set tolerance of 415 TWh (editor fixes the tolerance; propose the IEA-versus-Ember denominator gap as the minimum).
2. 2030 central value inside the IEA Headwinds to Lift-Off envelope; outside is reported.
3. US share of modelled demand within a pre-set band of 45% in 2024.
4. Water: modelled direct plus indirect water per kWh within the LBNL-implied order of magnitude; the source scope (US, 2014) is stated with the result.
5. Supply-limit test: with electricity supply cut, `E_dc` falls to supply and the unmet demand is recorded.
6. D-029 label stays: S3 unvalidated against GATE after about 2027.

## Badge it would earn
**Amber, "Constrained by one level and four scenarios, not validated"**; **red** for water and minerals constraints until a global series or the unread sources are available.
