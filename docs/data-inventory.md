# Data inventory (D-058 data retrieval campaign)

Generated from `audit/data/sources-register.json` by the campaign tooling on 2026-10-22; the register is authoritative, this page is a reading aid. Raw downloads are **not** in the repository (folder `F3-tracks/data-raw`, outside git); only derived series with provenance are committed (`audit/data/derived/`, 24 files). Obtaining a dataset is not a decision to use it: every use in the model needs its own decision (CLAUDE.md STOP rules).

**Totals.** 94 source records, 312 files, 2.62 GB raw; status retrieved 63, partial 17, blocked 14; redistribution yes 45, no 12, unclear 37; 49 failed fetches (listed in the register); 33 items need the user (`audit/data/needs-user.json`).

**Redistributable** means: the licence text was quoted and found verbatim in the saved file, and it permits redistribution of derived numbers with attribution. `unclear` and `no` sources are raw-only: nothing from them is committed. **Link** column: L3 climate impacts to yield and health; L4 AI and automation to labour and income; L5 compute to electricity; L6 energy-system emissions to climate; L7 history for calibration of the coupled model; DC data-centre module; M5 minerals and water; AI = S3 AI sector. See `docs/links/`.


## D1 AI compute and hardware

| Source (register id) | Vintage | Licence | Redistributable | Coverage | Supports | Status | Derived series |
|---|---|---|---|---|---|---|---|
| Epoch AI data hub (page listing every dataset, update dates and the licence sent (`epoch_data_page`) | page as served 2026-10-22 (datasets updated 2026-0 | Creative Commons Attribution | yes | n/a; n/a | AI | retrieved (0.1 MB) | none |
| Epoch AI: Data on AI models (notable, frontier, large-scale, all) (`epoch_ai_models`) | ZIP updated 2026-10-19 | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; 1950-07 to 2026-10 (publication dates; n | AI, L5, DC | retrieved (3.3 MB) | none |
| Epoch AI: Data on AI chip sales (`epoch_ai_chip_sales`) | ZIP updated 2026-10-21 | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; 2022-Q1 to 2026-Q3 (quarterly, estimates | AI, L5, DC | retrieved (27 kB) | none |
| Epoch AI: AI data centers (frontier data centre hub) (`epoch_data_centers`) | ZIP updated 2026-10-20 | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; 2018-12 to 2030-01 (timelines include pr | DC, L5, AI | retrieved (0.1 MB) | none |
| Epoch AI: GPU clusters (supercomputers, 2010-2025) (`epoch_gpu_clusters`) | CSV updated 2026-03-13 (legacy dataset, superseded | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; 2010-11 to 2025-07 (first operational da | AI, DC | retrieved (0.3 MB) | none |
| Epoch AI: Machine learning hardware (183 accelerators) (`epoch_ml_hardware`) | ZIP updated 2026-10-21 | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; 2008-06 to 2026-09 (release dates) | L5, DC, AI | retrieved (32 kB) | none |
| Epoch AI: AI chip owners (who holds the world's AI chips and compute) (`epoch_ai_chip_owners`) | ZIP updated 2026-05-12 | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; 2022 to 2026 (cumulative by quarter) | AI, DC | retrieved (51 kB) | none |
| Epoch AI: AI chip users (compute used or rented by the leading AI developers) (`epoch_ai_chip_users`) | ZIP updated 2026-09-09 | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; year-end snapshots | AI | retrieved (6 kB) | none |
| Epoch AI: AI chip components (wafer capacity, CoWoS packaging, HBM consumed by A (`epoch_ai_chip_components`) | ZIP updated 2026-07-23 | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; quarterly | AI, DC, M5 | retrieved (64 kB) | none |
| Epoch AI: AI companies (revenue, funding, staff, compute spend) (`epoch_ai_companies`) | ZIP updated 2026-10-08 | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; 2015 to 2026 | AI, L4 | retrieved (45 kB) | none |
| Epoch AI: Capabilities and benchmarking data (benchmarks, Epoch Capabilities Ind (`epoch_benchmark_data`) | ZIP updated 2026-10-22 | Creative Commons Attribution (CC BY; the README links version 4.0) | yes | global; model release dates to 2026-10 | AI | retrieved (2.4 MB) | none |
| Our World in Data: computation used to train notable AI systems (processed Epoch (`owid_ai_compute`) | grapher export 2026-10-22; Epoch AI (2026) with ma | CC BY (Our World in Data), data adapted from Epoch AI (CC BY) | yes | global; 1950 to 2026 | AI | retrieved (0.3 MB) | none |
| Stanford HAI: AI Index Report 2025 (PDF) and 2026 report pages (`stanford_ai_index`) | AI Index 2025 annual report (PDF); 2026 report web | CC BY-ND 4.0 (report) | no | global; to 2024 (2025 report) | AI | partial (31.8 MB) | none |
| TOP500 supercomputer lists (June 2026, November 2025 list pages; FAQ) (`top500`) | list pages 2026/06 and 2025/11 as served 2026-10-2 | No licence stated on the pages read (page footer: Copyright 1993-2026  | unclear | global; 2025-11 and 2026-06 lists | AI | partial (0.3 MB) | none |
| Semiconductor Industry Association: global semiconductor sales press releases (m (`sia_sales`) | page as served 2026-10-22 (latest release 2026-10- | Copyright SIA, all rights reserved (page footer) | no | global; 2025-09 to 2026-08 (page 1 of 28) | AI, DC | retrieved (0.1 MB) | none |
| WSTS Historical Billings Report (monthly semiconductor revenue by region, free d (`wsts`) | August 2026 data (file posted 2026-10) | Copyright WSTS, all rights reserved | no | Americas, Europe, Japan, Asia Pacific; 1986 to 2026-08 | AI, DC | retrieved (0.2 MB) | none |
| TSMC: 2025 Sustainability Report, Water Statement, 2024 Annual Report pages (`tsmc_esg`) | Sustainability Report published 2025 (file name 20 | No licence stated in the documents read (corporate report) | unclear | TSMC fabs (Taiwan, others); 2024 and earlier (reporting year stated  | DC, M5, AI | retrieved (22.1 MB) | none |
| Erdil et al. (2025), GATE: An Integrated Assessment Model for AI Automation, arX (`papers_epoch_gate`) | arXiv version retrieved 2026-10-22 | No licence stated in the PDF | unclear | as in the paper; as in the paper | AI, DC, L5 | retrieved (1.8 MB) | none |

## D2 Data-centre electricity and water

| Source (register id) | Vintage | Licence | Redistributable | Coverage | Supports | Status | Derived series |
|---|---|---|---|---|---|---|---|
| Our World in Data: data centres' share of electricity demand (processed IEA/Embe (`owid_dc_share`) | grapher export 2026-10-22 | Mixed: OWID CC BY processing of IEA (Non-CC terms) and Ember (CC BY) d | unclear | selected countries and world; 2024 and later (small file) | DC, L5 | retrieved (5 kB) | none |
| IEA: Energy and AI (report, April 2025) with executive summary and the Key Quest (`iea_energy_ai`) | report published 2025-04-10 (PDF 8.2 MB); Key Ques | CC BY 4.0 (report) | yes | world and regions (US, China, Europe, As; 2020 to 2035 (2024 estimates, 2030 and 2 | DC, L5, AI | retrieved (9.0 MB) | none |
| IEA: Energy and AI and Key Questions on Energy and AI (data products, spreadshee (`iea_energy_ai_data`) | Energy and AI data product last updated June 2025; | IEA Terms of Use for Non-CC Material | no | world and regions; 2020 to 2035 | DC, L5 | blocked (0.2 MB) | none |
| Lawrence Berkeley National Laboratory: 2024 United States Data Center Energy Usa (`lbnl_dc_2024`) | 2024-12-20, DOI 10.71468/P1WC7Q (eScholarship copy | No open licence in the document read; US Government retains a licence  | unclear | United States; 2014 to 2023 estimates, 2024 to 2028 sce | DC, L5, M5 | retrieved (4.4 MB) | none |
| Ember: Yearly electricity data (long format: capacity, generation, demand, impor (`ember_yearly`) | yearly_full_release_long_format.csv as served 2026 | CC BY 4.0 | yes | about 215 countries and regional aggrega; 2000 to 2025 | L5, L6, L7, DC | retrieved (49.3 MB) | `ember_electricity_world` |
| Ember: yearly generation release (new format, global) and methodology PDF (`ember_release_global`) | served 2026-10-22; new download format of July 202 | CC BY 4.0 | yes | countries and regions; 2000 to 2025 | L5, L6, L7 | retrieved (17.6 MB) | none |
| US EIA: copyright and reuse policy, open data and bulk-file pages (policy pages  (`eia_policy`) | pages as served 2026-10-22 | US Government work, public domain | yes | United States and international; n/a | DC, L5 | partial (0.5 MB) | none |
| Google Environmental Report 2024 and 2025 (PDF) and the 2025 report landing page (`google_env`) | 2025 report (data year 2024) and 2024 report (data | No licence stated (corporate report) | unclear | Google data centres, global; 2019 to 2024 | DC, L5, L6 | retrieved (34.4 MB) | none |
| Microsoft Environmental Data Fact Sheets 2025 and 2026 (PDF) (`microsoft_env`) | 2025 and 2026 editions (FY24 and FY25 data) as ser | No licence stated (corporate report) | unclear | Microsoft datacenters by location; FY2020 to FY2025 | DC, L5, L6 | retrieved (5.1 MB) | none |
| Meta 2025 Sustainability Report (PDF, fiscal year 2024) (`meta_sustainability`) | 2025 report (data year 2024); file saved from the  | No licence stated (corporate report) | unclear | Meta data centres; 2019 to 2024 | DC, L5, L6 | retrieved (28.5 MB) | none |
| Amazon Sustainability Reports 2024 and 2025 and AWS 2025 summary (PDF) (`amazon_sustainability`) | 2024 report, 2025 report and AWS summary as served | No licence stated (corporate report) | unclear | AWS data centres, global; 2019 to 2025 | DC, L5, L6 | retrieved (18.0 MB) | none |
| WRI Aqueduct 4.0: water risk data (global maps, country and province rankings) (`aqueduct40`) | Aqueduct 4.0 (Kuzma et al. 2023), files as served  | CC BY 4.0 | yes | global, basins, countries, provinces; baseline 1979-2019; projections 2030, 20 | M5, DC | retrieved (274.5 MB) | `aqueduct_water_stress_by_country` |
| FAO AQUASTAT: dissemination system and catalogue listing (no data series retriev (`fao_aquastat`) | CKAN catalogue listing 2026-10-22 | CC BY-NC-SA 4.0 (catalogue record of the AQUASTAT Dissemination System | no | countries; 1960s to recent | M5 | blocked (0.5 MB) | none |
| Li, Yang, Islam and Ren (2023), Making AI Less 'Thirsty', arXiv:2304.03271 (`papers_li2023_thirsty`) | arXiv version retrieved 2026-10-22 | No licence stated in the PDF | unclear | as in the paper; as in the paper | DC, M5 | retrieved (0.7 MB) | none |
| Luccioni, Viguier and Ligozat (2022), Estimating the Carbon Footprint of BLOOM,  (`papers_luccioni2022`) | arXiv version retrieved 2026-10-22 | No licence stated in the PDF | unclear | as in the paper; as in the paper | DC, L5, L6 | retrieved (0.3 MB) | none |

## D3 Emissions

| Source (register id) | Vintage | Licence | Redistributable | Coverage | Supports | Status | Derived series |
|---|---|---|---|---|---|---|---|
| EDGAR (JRC/IEA) GHG emissions of all world countries, 2025 report: totals and se (`edgar2025`) | EDGAR_2025_GHG (2025), JRC143227, DOI 10.2760/9816 | CC BY 4.0 for material owned by the European Union (excludes fossil CO | yes | all countries, EU27, global total; 1970 to 2024 | L6, L7 | retrieved (4.9 MB) | `edgar_global_non_co2_by_sector` |
| EDGAR/IEA fossil CO2 emissions workbook (IEA-EDGAR CO2 v4) (`edgar2025_fossil_co2`) | EDGAR_2025_GHG_booklet_2025_fossilCO2only.xlsx as  | CC BY-NC-ND 4.0 (IEA data as modified by JRC) | no | countries; 1970 to 2024 | L6, L7 | retrieved (1.5 MB) | none |
| CEDS v_2025_03_18 aggregate emissions data (species x country x sector, 1750-202 (`ceds2025`) | v_2025_03_18 (Zenodo record 15059443, published 20 | CC BY 4.0 (Zenodo record metadata) | yes | 220 countries and regions; 1750 to 2023 | L6, L7 | retrieved (63.6 MB) | `ceds_global_emissions` |
| Climate TRACE emissions inventory v5.6.0 (selected sectors: power, mineral extra (`climate_trace`) | V5.6.0, Zenodo record 20414751, published 2026-04- | CC BY 4.0 (Zenodo record metadata) | yes | source level, global; 2015 to 2025 (annual country, monthly so | L6, L7, DC | partial (328.3 MB) | none |
| Our World in Data: CO2 and greenhouse gas emissions dataset (owid-co2-data.csv) (`owid_co2`) | master branch file as served 2026-10-22 | CC BY (OWID compilation); third-party components under their own terms | unclear | countries and world; 1750 to 2024 | L6, L7 | retrieved (14.4 MB) | none |
| Global Carbon Budget 2025 (ICOS landing and data licence pages; the committed 20 (`gcb2025`) | Global Carbon Budget 2025 v1.0 (Friedlingstein et  | CC BY 4.0 (ICOS data licence) | yes | world; 1750 to 2024 | L6, L7 | partial (0.2 MB) | none |
| FaIR 2.2.4 calibrated constrained ensemble inputs (fair-calibrate v1.4.1) and ex (`fair_inputs`) | FAIR repository commit 28572bb00e40d73f83f3365395f | Apache License 2.0 for the repository (software); no separate licence  | unclear | World; 1750.5 to 2500.5 (mid-year columns); run | L6, L7 | retrieved (3.0 MB) | none |
| NOAA GML: Mauna Loa annual mean CO2 (`noaa_co2`) | file as served 2026-10-22 | US Government work, public domain (NOAA) | yes | Mauna Loa observatory (global proxy); 1959 to 2025 | L6, L7 | retrieved (27 kB) | `noaa_co2_annual` |
| IIASA SSP Database (Shared Socioeconomic Pathways) and AR6 scenario explorer: em (`iiasa_ssp_db`) | not retrieved | Registration and terms required (not read) | unclear | world, regions; 2005 to 2100 | L6, L7 | blocked | none |
| UNFCCC GHG data portal (landing page, 212 bytes) (`unfccc_ghg`) | not retrieved | Not read | unclear | n/a; n/a | L6 | blocked (0 kB) | none |
| Hoesly et al. (2018), Historical (1750-2014) anthropogenic emissions of reactive (`papers_hoesly2018_ceds`) | published 2018 | CC BY 3.0 (as printed) | yes | as in the paper; as in the paper | L6, L7 | retrieved (6.8 MB) | none |
| Leach et al. (2021), FaIRv2.0.0: a generalized impulse response model for climat (`papers_leach2021_fair`) | published 2021 | CC BY 4.0 (as printed) | yes | as in the paper; as in the paper | L6, L7 | retrieved (6.6 MB) | none |
| Nicholls et al. (2020), Reduced Complexity Model Intercomparison Project Phase 1 (`papers_nicholls_rcmip`) | published 2020 | CC BY 4.0 (as printed); the RCMIP data are stated as CC BY-SA 4.0 in t | yes | as in the paper; as in the paper | L6, L7 | retrieved (12.5 MB) | none |

## D4 Climate impacts (yield, health, damages)

| Source (register id) | Vintage | Licence | Redistributable | Coverage | Supports | Status | Derived series |
|---|---|---|---|---|---|---|---|
| Lancet Countdown 2025 report: indicator data downloads (53 workbooks incl. heat  (`lancet_countdown`) | 2025 report (published online 2025-10-29), workboo | CC BY-NC-SA 4.0 | no | global, WHO regions, Lancet Countdown re; 1990/2000 to 2024 depending on the indic | L3, L4 | retrieved (25.4 MB) | none |
| ISIMIP agriculture sector: ISIMIP3b crop-model yield simulations (records, API l (`isimip`) | ISIMIP3b simulation data (DOI 10.48364/ISIMIP.7233 | CC0 1.0 Universal Public Domain Dedication (dataset records) | yes | global 0.5 degree grids (annual); 1850-2100 (historical, picontrol, ssp126 | L3 | partial (0.6 MB) | none |
| Burke, Hsiang and Miguel (2015) replication data: projected GDP per capita with  (`burke2015`) | author page as served 2026-10-22; SDR record versi | No licence stated; SDR: 'may be subject to additional license and use  | unclear | countries; 2010 to 2099 | L3, L4 | partial (0.3 MB) | none |
| Kalkuhl and Wenz (2020) replication data record (Zenodo 4743845; README only ret (`kalkuhl_wenz2020`) | Zenodo record published 2020-08-04 | CC BY 4.0 (Zenodo record) | yes | 1,500+ regions in 77 countries; 1900 to 2014 | L3, L4 | partial (8 kB) | none |
| IPCC AR6 WGII chapters 4 (water), 5 (food, fibre), 7 (health), 16 (key risks) an (`ipcc_ar6_wg2`) | AR6 WGII final chapter PDFs as served 2026-10-22 | IPCC copyright: personal non-commercial use; no redistribution | no | global and regional; to 2100 | L3, M5 | retrieved (66.5 MB) | none |
| WHO Global Health Observatory: climate change topic landing page (page only) (`who_gho`) | page as served 2026-10-22 | Not read (WHO data terms are a separate page) | unclear | n/a; n/a | L3 | partial (0.1 MB) | none |
| Kalkuhl and Wenz (2020), The impact of climate conditions on economic production (`papers_kalkuhl_wenz2020`) | published 2020; PIK open-access copy | CC BY-NC-ND (as printed in the article) | no | as in the paper; as in the paper | L3, L4 | retrieved (2.0 MB) | none |
| Jagermeyr et al. (2021), Climate impacts on global agriculture emerge earlier in (`papers_jagermeyr2021`) | published 2021; the publisher returned the article | Not read (article page only) | unclear | as in the paper; as in the paper | L3 | partial (0.5 MB) | none |
| Vicedo-Cabrera et al. (2021), The burden of heat-related mortality attributable  (`papers_vicedo2021`) | published 2021; article page only | Not read (article page only) | unclear | as in the paper; as in the paper | L3 | partial (0.5 MB) | none |
| Dunne et al. (2013), Reduced work capacity in a warming climate, Nature Climate  (`papers_dunne2013`) | published 2013; article page only | Not read (article page only) | unclear | as in the paper; as in the paper | L3, L4 | partial (0.3 MB) | none |
| Zhao et al. (2017), Temperature increase reduces global yields of major crops in (`papers_zhao2017`) | not retrieved | Not read | unclear | as in the paper; as in the paper | L3 | blocked | none |
| Schlenker and Roberts (2009), Nonlinear temperature effects indicate severe dama (`papers_schlenker_roberts2009`) | not retrieved | Not read | unclear | as in the paper; as in the paper | L3 | blocked | none |
| Burke, Hsiang and Miguel (2015), Global non-linear effect of temperature on econ (`papers_burke2015`) | not retrieved | Not read | unclear | as in the paper; as in the paper | L3 | blocked | none |
| Carleton et al. (2022), Valuing the global mortality consequences of climate cha (`papers_carleton2022`) | not retrieved | Not read | unclear | as in the paper; as in the paper | L3 | blocked | none |
| Gasparrini et al. (2017), Projections of temperature-related excess mortality un (`papers_gasparrini2017`) | not retrieved | Not read | unclear | as in the paper; as in the paper | L3 | blocked | none |
| IPCC WGI Atlas repository LICENSE (CMIP6 regional aggregates used by the warming (`ipcc_ar6_wg1_atlas`) | commit ed29da33d38ae767d19caafd4cde06042cbe00f4 | CC BY 4.0 (datasets), Apache 2.0 (code) | yes | AR6 regions; 1850-2100 | L3, L7 | partial (3 kB) | none |

## D5 Labour and automation

| Source (register id) | Vintage | Licence | Redistributable | Coverage | Supports | Status | Derived series |
|---|---|---|---|---|---|---|---|
| ILOSTAT (via the rplumber API): labour income share, output per worker, producti (`ilostat`) | indicator files as served 2026-10-22; modelled est | CC BY 4.0 (ILO data published as of 3 May 2023) | yes | about 276 countries/areas and aggregates; labour income share 2004 to 2026; output | L4, L7 | retrieved (394.1 MB) | `ilostat_labour_income_share`, `ilostat_world_employment_by_sector` |
| Penn World Table 11.0 (pwt110.xlsx, user guide) with the DataverseNL record (`pwt110`) | PWT 11.0, DataverseNL version 2.0 released 2025-10 | CC BY 4.0 | yes | 185 countries; 1950 to 2023 | L4, L7 | retrieved (6.0 MB) | `pwt_labour_share` |
| World Bank WDI labour indicators (labour force, employment ratio, unemployment,  (`wdi_labour`) | WDI API as served 2026-10-22 | CC BY 4.0 (World Bank default) | yes | all countries and aggregates; 1960 to 2025 | L4 | retrieved (31.1 MB) | `wdi_world_series` |
| Anthropic Economic Index (labor market impacts: job exposure and task penetratio (`anthropic_econ_index`) | repository main as served 2026-10-22; labor_market | CC BY (README); the dataset-card header says 'license: mit' (conflict  | yes | O*NET/SOC occupations (US); 2025-2026 usage windows | L4, AI | retrieved (2.3 MB) | `task_exposure_summary` |
| OpenAI: GPTs are GPTs occupation-level exposure (occ_level.csv) (`gpts_are_gpts`) | repository main as served 2026-10-22 | MIT | yes | US occupations (O*NET); 2023 ratings | L4 | retrieved (0.1 MB) | `task_exposure_summary` |
| Felten, Raj, Seamans AI Occupational Exposure (AIOE) data appendix (`aioe_felten`) | repository as served 2026-10-22 (last push 2024-06 | No licence file in the repository (GitHub API license field is null) | unclear | US occupations; 2021 method; appendix to 2024 | L4 | retrieved (0.2 MB) | none |
| O*NET 31.0 database (Excel files) and licence page (`onet`) | O*NET 31.0 | CC BY 4.0 | yes | US occupations; 2026 database | L4 | retrieved (48.3 MB) | none |
| World Inequality Database: data page, methodology page and bulk file wid_all_dat (`wid`) | bulk file as served 2026-10-22 | No licence or terms statement found on the pages read | unclear | about 200 countries and regions; 1800 to 2024 depending on series | L4, L7 | retrieved (888.8 MB) | none |
| OECD Employment Outlook 2023 (AI and jobs) and OECD terms pages (not retrieved) (`oecd_ai`) | not retrieved | Not read (terms page returned HTTP 403) | unclear | OECD; n/a | L4 | blocked | none |
| US Census Bureau Business Trends and Outlook Survey: data downloads page (page o (`census_btos`) | page as served 2026-10-22 | Not read | unclear | US; n/a | AI | partial (5 kB) | none |
| Acemoglu (2024), The Simple Macroeconomics of AI, NBER w32487 (`papers_acemoglu2024`) | NBER working paper, 2024 | Copyright reserved by the author (NBER notice) | no | as in the paper; as in the paper | L4, AI | retrieved (0.8 MB) | none |
| Acemoglu and Restrepo (2016), The Race between Man and Machine, NBER w22252 (`papers_acemoglu_restrepo2016`) | NBER working paper, 2016 | Copyright reserved by the authors (NBER notice) | no | as in the paper; as in the paper | L4 | retrieved (1.0 MB) | none |
| Karabarbounis and Neiman (2013), The Global Decline of the Labor Share, NBER w19 (`papers_karabarbounis_neiman2013`) | NBER working paper, 2013 | Copyright reserved by the authors (NBER notice) | no | as in the paper; as in the paper | L4 | retrieved (0.4 MB) | none |
| Brynjolfsson, Chandar and Chen (2025), Canaries in the Coal Mine? Six Facts abou (`papers_brynjolfsson2025`) | working paper, 2025 | No licence stated in the PDF | unclear | as in the paper; as in the paper | L4, AI | retrieved (3.4 MB) | none |
| Eloundou, Manning, Mishkin and Rock (2023), GPTs are GPTs: An Early Look at the  (`papers_eloundou2023`) | arXiv version retrieved 2026-10-22 | No licence stated in the PDF (arXiv default distribution licence) | unclear | as in the paper; as in the paper | L4, AI | retrieved (2.1 MB) | none |

## D6 Minerals

| Source (register id) | Vintage | Licence | Redistributable | Coverage | Supports | Status | Derived series |
|---|---|---|---|---|---|---|---|
| USGS Mineral Commodity Summaries 2026 (report PDF, version 1.3 May 2026) and rev (`usgs_mcs2026`) | Version 1.3, May 2026 (first posted 2026-02-06; re | Public domain (US Government), third-party copyrighted material except | yes | world by producing country; mine production 2024 and 2025 estimated; | M5, DC, AI | retrieved (17.7 MB) | `usgs_mcs2026_world_production_reserves` |
| USGS Mineral Commodity Summaries 2026 data release (ScienceBase DOI 10.5066/P1WK (`usgs_mcs2026_data`) | data release dated 2026-02-06 | Public domain (USA.gov public domain label) | yes | world; 2021 to 2025 | M5 | blocked (0.7 MB) | none |
| USGS Mineral Commodity Summaries 2025 (report PDF) (`usgs_mcs2025`) | MCS 2025 as served 2026-10-22 | Public domain (US Government) | yes | world; 2024 estimated production in the 2025 ed | M5 | retrieved (10.5 MB) | `usgs_mcs2026_world_production_reserves` |
| IEA Global Critical Minerals Outlook 2025: report landing page and mineral pages (`iea_cmo2025`) | published 2025-05-21; mineral pages as served 2026 | CC BY 4.0 | yes | world; 2021, 2024, 2030, 2040 (STEPS and other  | M5, DC | partial (1.0 MB) | `iea_critical_minerals_demand` |
| British Geological Survey World Mineral Statistics (landing page only) (`bgs_wms`) | page as served 2026-10-22 | Not read (page text names no licence) | unclear | world; n/a | M5 | partial (94 kB) | none |
| USGS Historical Statistics for Mineral and Material Commodities and USGS copyrig (`usgs_historical`) | not retrieved | Not read | unclear | n/a; n/a | M5 | blocked | none |

## D7 Calibration and history

| Source (register id) | Vintage | Licence | Redistributable | Coverage | Supports | Status | Derived series |
|---|---|---|---|---|---|---|---|
| UN World Population Prospects 2024: total population by sex (CSV) and Summary of (`wpp2024_totpop`) | WPP 2024 (28th revision) | CC BY 3.0 IGO | yes | countries, regions, world; 1950 to 2100 (estimates to 2023) | L3, L4, L7 | retrieved (35.5 MB) | `wpp2024_world_population` |
| UN World Population Prospects 2024: demographic indicators, medium variant (life (`wpp2024_demographic`) | WPP 2024 (28th revision) | CC BY 3.0 IGO | yes | countries, regions, world; 1950 to 2100 | L3, L7 | retrieved (16.6 MB) | `wpp2024_world_population` |
| World Bank WDI calibration indicators (GDP, GDP per capita, population, life exp (`wdi_calibration`) | WDI API as served 2026-10-22 | CC BY 4.0 (World Bank default) | yes | all countries and aggregates; 1960 to 2025 | L3, L4, L7, M5 | retrieved (60.2 MB) | `wdi_world_series` |
| Our World in Data: energy dataset (owid-energy-data.csv) and README (`owid_energy`) | master branch file as served 2026-10-22 (README wa | CC BY (OWID compilation); third-party components under their own terms | unclear | countries and world; 1900 to 2025 | L5, L7 | retrieved (9.2 MB) | none |
| FAOSTAT bulk: crops and livestock production (normalized) and land use inputs (n (`faostat`) | bulk files as served 2026-10-22 | CC BY 4.0 with additional FAO terms (attribution format, no endorsemen | yes | countries, regions, world; 1961 to 2024 | L3, M5 | partial (37.0 MB) | `faostat_world_cereals` |
| HadCRUT5 (HadCRUT.5.2.0.0) global annual summary series (`hadcrut5`) | HadCRUT.5.2.0.0 as served 2026-10-22 | Open Government Licence v3.0 (Crown copyright) | yes | global; 1850 to 2025 | L6, L7 | retrieved (10 kB) | `hadcrut5_global_annual` |
| NASA GISTEMP v4 global annual mean (cross-check only) (`gistemp`) | as served 2026-10-22 | Not stated for the data table | unclear | global; 1880 to 2026 (partial) | L6, L7 | retrieved (32 kB) | none |
| Maddison Project Database 2023 (mpd2023_web.xlsx) (`maddison2023`) | MPD 2023, DataverseNL version 1 released 2024-04-2 | CC BY 4.0 | yes | 169 countries/regions; 1 CE to 2022 | L7 | retrieved (5.0 MB) | `maddison_world_gdp_per_capita` |
| Energy Institute Statistical Review of World Energy 2026: data downloads page (t (`energy_institute_sr`) | page as served 2026-10-22 | Not read (terms and conditions page not opened) | unclear | n/a; n/a | L5, L7 | blocked (90 kB) | none |

## D8 Other

| Source (register id) | Vintage | Licence | Redistributable | Coverage | Supports | Status | Derived series |
|---|---|---|---|---|---|---|---|
| UCDP/PRIO Armed Conflict Dataset v26.1 and v25.1 (CSV zips) and UCDP downloads p (`ucdp`) | v26.1 (1946-2025) and v25.1 | CC BY 4.0 | yes | countries/locations; 1946 to 2025 | L4 | retrieved (0.2 MB) | `ucdp_conflicts_per_year` |
| IRENA renewable capacity statistics (not retrieved) (`irena_stats`) | not retrieved | Not read | unclear | n/a; n/a | L5, L7 | blocked | none |

## Licence cautions

- **World Bank WDI republishes third-party series.** `EN.GHG.CO2.MT.CE.AR5` is the EDGAR/IEA fossil CO2 series (cross-check `wdi_co2_is_edgar`: world 2024 agrees to the digits shown), `EG.USE.ELEC.KH.PC` is IEA electricity use and `ER.H2O.FWTL.K3` is FAO AQUASTAT withdrawal. The WDI default is CC BY 4.0 but the underlying owners' terms differ, so these three are excluded from `wdi_world_series` (17 indicators kept).
- **EDGAR fossil CO2 is CC BY-NC-ND 4.0** (IEA data as modified by EDGAR): raw only, no values committed; only the relative difference to the Global Carbon Budget is stored (`co2_gcb_vs_edgar_2024`). The EDGAR non-CO2 gases are CC BY 4.0 and are committed (`edgar_global_non_co2_by_sector`).
- **Lancet Countdown 2025 is CC BY-NC-SA 4.0**: raw only. Share-alike is also incompatible with the project's CC BY 4.0 data licence, so it cannot be merged into a derived series even if the NC question were settled.
- **FAO AQUASTAT is CC BY-NC-SA 4.0** per the catalogue record: not retrieved, not used.
- **IEA data products (Energy and AI spreadsheets, Critical Minerals data) sit under the IEA Terms of Use for Non-CC Material** and need a login; not retrieved. The IEA Energy and AI report text is CC BY 4.0 and the 16 figures in `iea_energy_ai_figures` are quoted with PDF page numbers. The 2025 Critical Minerals Outlook report is CC BY 4.0.
- **Corporate sustainability reports (Google, Microsoft, Meta, Amazon), TSMC, LBNL (2024 report), OWID compilations of third-party data, the FaIR input files, TOP500 and WID have no licence statement the campaign could quote** (`redistribution: unclear`). Raw only. In the data-centre document DC.md they are cited by report and page number, never copied into a data file.
- **SIA and WSTS are all-rights-reserved**; **IPCC AR6 WGII and Stanford AI Index 2025 are non-commercial or no-derivatives**: raw only.
- **Research papers** are registered as documents (role `document`): read for parameters, not redistributed. Papers that could not be read (Zhao 2017, Schlenker and Roberts 2009, Burke 2015, Carleton 2022, Gasparrini 2017, Lobell 2011, Vicedo-Cabrera 2021 and Dunne 2013 in full) are in the needs-user list; where the link documents quote a number from them it is labelled "[from memory, unverified]".
- **Obtaining a dataset is not a decision to use it** (CLAUDE.md, D-058): any series that feeds the model needs its own decision, and third-party use outside D-001, D-014 and D-026 needs a STOP-and-ask.

## Cross-checks done (25 recorded in `audit/data/cross-checks.json`, summarised in the register)

Identical: the four FaIR input files re-downloaded from the pinned commit match the audit's checksums; HadCRUT5 and WPP match; HadCRUT5 1850-1900 offset equals D-057's. Close (under 3%): Ember old versus new long format (0.5%); GCB versus OWID (0.002%), CEDS (1.6%) and EDGAR (2.7%) world fossil CO2; EDGAR versus CEDS methane (2.5%); WPP versus WDI population (0.3%); FAOSTAT versus WDI cereal yield (0.02%); MCS 2025 versus 2026 for copper, rare earths, nickel, graphite (1 to 2%); OWID versus Epoch largest training run (vintage only). Larger, and explained by definition: the IEA data-centre share of electricity 1.5% versus 1.34% on Ember's denominator (-10.5%); PWT versus ILO median labour share 2019 (-11%, different definitions and samples); lithium +8.8% and cobalt +27% between MCS editions (not investigated: could be an USGS revision or a table-parsing issue; check the PDF page before using either); Epoch's 95 tracked frontier AI data centres draw about 70% less than the IEA all-data-centre average load (different scope and date, not a disagreement).

## Coverage gaps

| Gap | Why it matters | State |
|---|---|---|
| **No damage-function data for L3 beyond FAOSTAT yields.** ISIMIP crop and health outputs not downloaded; Jagermeyr, Zhao, Schlenker-Roberts, Burke, Carleton, Gasparrini, Vicedo-Cabrera not read in full | the yield and mortality response to temperature cannot be calibrated from retrieved data | needs-user (priority 1 and 2); `isimip_subset` |
| **Long data-centre electricity history** (pre-2018) and regional capacity/PUE series | the DC module can be compared with one 2024 IEA figure, LBNL 2014-2023 for the US, and Epoch's facility timelines (2018-2030) only | IEA data product behind login; LBNL record not retrieved |
| **Data-centre water**: LBNL direct 21.2 billion litres (2014) and indirect about 800 billion litres are one-year US figures; the corporate reports give 2019-2024 company totals (not committed, unclear licence) | no global water series, no time series for a calibration | gap |
| **Global Carbon Budget full workbook** (land and ocean sinks, 1750-2024) | the carbon-cycle side of the FaIR check | ICOS click-through not accepted by the campaign; a 2015-2024 CO2 extract is in the repository |
| **SSP database emissions** | the FaIR extension file carries the ScenarioMIP set but its original licence is unstated | IIASA login |
| **USGS historical production series** (copper, lithium, gallium, rare earths, silicon since 1900) and MCS data release CSVs | the minerals module can be anchored on 2024 world production and reserves (8 commodities) but not on a history | usgs.gov answered with an empty HTTP 202 challenge, ScienceBase 403; not worked around |
| **Labour-income link**: no task-level AI-exposure series over time; Anthropic exposure covers 2025-2026 only; WID unclear; OECD AI data blocked | L4 has a labour share history (PWT 1950-2023, ILO from 2004) but no measured automation effect on it | see L4.md |
| **Top500 and AI cluster power** | only list pages were read | account needed |
| **Other Climate TRACE sectors, EIA bulk electricity, IRENA, Energy Institute** | secondary checks only | not retrieved or gated |
| **Regional detail**: most derived series are world totals or 16 areas (Ember); no regional series for yields, labour or mortality | the coupled model is global | by design for now |
