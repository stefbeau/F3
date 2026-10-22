"""Register metadata, part 4: D6 minerals, D7 calibration and history, D8 other. S, CROSS_CHECKS, NEEDS_USER are injected."""

# --------------------------------------------------------------------------------------------------------------- D6 minerals and materials
S(id="usgs_mcs2026", title="USGS Mineral Commodity Summaries 2026 (report PDF, version 1.3 May 2026) and revision history", publisher="US Geological Survey", url="https://doi.org/10.3133/mcs2026",
  landing_page="https://pubs.usgs.gov/periodicals/mcs2026/mcs2026.pdf", domains=["D6"], supports=["M5", "DC", "AI"], version="Version 1.3, May 2026 (first posted 2026-02-06; revised March 2026 v1.1, April 2026 v1.2, May 2026 v1.3). The earlier register said 1.1 and the M5 plan 1.3 from a search result: the PDF itself says 1.3.",
  status="retrieved", only=["mcs2026.pdf", "versionHist.txt", "mcs2026-landing.html"],
  licence={"name": "Public domain (US Government), third-party copyrighted material excepted", "quote": "Although this report is in the public domain, permission must be secured from the individual copyright owners to reproduce any copyrighted material contained within this report.",
           "quote_file": "usgs_mcs2026/mcs2026.pdf", "url": "https://pubs.usgs.gov/periodicals/mcs2026/mcs2026.pdf"},
  redistribution="yes", redistribution_note="The report states it is in the public domain. This resolves the M5 plan/D-006 STOP item 4 for the licence AND the content: the PDF was downloaded and read here (17.6 MB, pdftotext). World production and reserves tables are parsed in -raw mode; the layout mode scrambles the rows (checked).",
  units="metric tons of contained metal (copper in thousand tons), as stated per commodity", geography="world by producing country", time_span="mine production 2024 and 2025 estimated; US salient statistics 2021-2025e; reserves as of 2025",
  variables=["world mine production 2024 and 2025e by country", "reserves", "US import reliance", "price", "consumption"], derived=["usgs_mcs2026_world_production_reserves"],
  notes="Machine-readable data release (ScienceBase) is blocked, see usgs_mcs2026_data.")
S(id="usgs_mcs2026_data", title="USGS Mineral Commodity Summaries 2026 data release (ScienceBase DOI 10.5066/P1WKQ63T): catalogue pages and FGDC metadata; the CSV files were not retrievable", publisher="US Geological Survey",
  url="https://doi.org/10.5066/P1WKQ63T", domains=["D6"], supports=["M5"], version="data release dated 2026-02-06", status="blocked",
  licence={"name": "Public domain (USA.gov public domain label)", "quote": "License http://www.usa.gov/publicdomain/label/1.0/", "quote_file": "usgs_mcs2026_data/datacatalog-69837ec8.html", "url": "https://data.usgs.gov/datacatalog/data/USGS:69837ec8b66b01367d7ec7d9"},
  redistribution="yes", redistribution_note="Public domain label on the catalogue record. The DOI landing page and the ScienceBase item and file URLs returned HTTP 403, and usgs.gov returned an empty bot-challenge response (HTTP 202): not worked around. The catalogue and metadata pages were saved. The CSVs (MCS2026_Commodities_Data.csv, 3 MB) are in needs-user.",
  units="various", geography="world", time_span="2021 to 2025", variables=["commodity-level salient statistics and world production (CSV, not retrieved)"], notes="")
S(id="usgs_mcs2025", title="USGS Mineral Commodity Summaries 2025 (report PDF)", publisher="US Geological Survey", url="https://doi.org/10.3133/mcs2025", domains=["D6"], supports=["M5"],
  version="MCS 2025 as served 2026-10-22", status="retrieved",
  licence={"name": "Public domain (US Government)", "quote": "Although this report is in the public domain, permission must be secured from the individual copyright owners to reproduce any copyrighted material contained within this report.",
           "quote_file": "usgs_mcs2025/mcs2025.pdf", "url": "https://pubs.usgs.gov/periodicals/mcs2025/mcs2025.pdf"},
  redistribution="yes", redistribution_note="Same statement as the 2026 edition (checked in the saved file). Used for the year-over-year revision cross-check of world totals.",
  units="as MCS 2026", geography="world", time_span="2024 estimated production in the 2025 edition; 2023 revised", variables=["world mine production 2023 and 2024e", "reserves"], derived=["usgs_mcs2026_world_production_reserves"], notes="")
S(id="iea_cmo2025", title="IEA Global Critical Minerals Outlook 2025: report landing page and mineral pages with demand tables (copper, lithium, cobalt)", publisher="International Energy Agency",
  url="https://www.iea.org/reports/global-critical-minerals-outlook-2025", domains=["D6"], supports=["M5", "DC"], version="published 2025-05-21; mineral pages as served 2026-10-22", status="partial",
  licence={"name": "CC BY 4.0", "quote": "Published 21 May 2025 Licence CC BY 4.0", "quote_file": "iea_cmo2025/landing.html", "url": "https://www.iea.org/reports/global-critical-minerals-outlook-2025"},
  redistribution="yes", redistribution_note="Report pages carry 'Licence CC BY 4.0'. The nickel, graphite and rare-earth pages returned HTTP 403 and the full report PDF link was not found on the pages read, so only copper, lithium and cobalt tables were saved.",
  units="kt of contained metal per year", geography="world", time_span="2021, 2024, 2030, 2040 (STEPS and other scenarios)", variables=["cleantech demand", "other uses", "total demand", "top producers"], derived=["iea_critical_minerals_demand"],
  notes="Demand table values are read from the saved HTML text (for example copper cleantech demand 6002 kt in 2021, 7737 kt in 2024, 10 910 kt in 2030 in the STEPS table).")
S(id="bgs_wms", title="British Geological Survey World Mineral Statistics (landing page only)", publisher="British Geological Survey", url="https://www.bgs.ac.uk/mineralsuk/statistics/world-mineral-statistics/", domains=["D6"], supports=["M5"],
  version="page as served 2026-10-22", status="partial", role="document", licence={"name": "Not read (page text names no licence)", "quote": ""}, redistribution="unclear",
  redistribution_note="Only the landing page was saved; the production data pages guessed returned 404. BGS data are often under the Open Government Licence but the page read does not say.", units="n/a", geography="world", time_span="n/a", variables=[], notes="See needs-user.")

# --------------------------------------------------------------------------------------------------------------- D7 calibration and history
S(id="wpp2024_totpop", title="UN World Population Prospects 2024: total population by sex (CSV) and Summary of Results (PDF)", publisher="United Nations DESA Population Division", url="https://population.un.org/wpp/",
  domains=["D7"], supports=["L3", "L4", "L7"], version="WPP 2024 (28th revision)", status="retrieved", dirs=["wpp2024_totpop"],
  licence={"name": "CC BY 3.0 IGO", "quote": "Figures and tables in this publication can be reproduced without prior permission under a Creative Commons license", "quote_file": "wpp2024_totpop/WPP2024_Summary-of-Results.pdf",
           "url": "https://population.un.org/wpp/assets/Files/WPP2024_Summary-of-Results.pdf"},
  redistribution="yes", redistribution_note="Licence quoted from the Summary of Results (now saved with sha256); a statement attached to the CSV itself was not found. Same sha256 as the file in audit/data/sources-history.json (cross-checked).",
  units="thousand persons", geography="countries, regions, world", time_span="1950 to 2100 (estimates to 2023)", variables=["total population by sex", "variants"], derived=["wpp2024_world_population"], notes="")
S(id="wpp2024_demographic", title="UN World Population Prospects 2024: demographic indicators, medium variant (life expectancy, fertility, deaths, births)", publisher="United Nations DESA Population Division", url="https://population.un.org/wpp/",
  domains=["D7"], supports=["L3", "L7"], version="WPP 2024 (28th revision)", status="retrieved",
  licence={"name": "CC BY 3.0 IGO", "quote": "Figures and tables in this publication can be reproduced without prior permission under a Creative Commons license", "quote_file": "wpp2024_totpop/WPP2024_Summary-of-Results.pdf",
           "url": "https://population.un.org/wpp/assets/Files/WPP2024_Summary-of-Results.pdf"},
  redistribution="yes", redistribution_note="Same statement as wpp2024_totpop.", units="years, births per woman, thousand persons", geography="countries, regions, world", time_span="1950 to 2100",
  variables=["life expectancy at birth", "total fertility rate", "births", "deaths", "population"], derived=["wpp2024_world_population"], notes="")
S(id="wdi_calibration", title="World Bank WDI calibration indicators (GDP, GDP per capita, population, life expectancy, cereal yield, electricity use, CO2, freshwater withdrawal, Gini, poverty, industry value added, investment, arable land)",
  publisher="World Bank", url="https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.KD", landing_page="https://data.worldbank.org/", domains=["D7"], supports=["L3", "L4", "L7", "M5"],
  version="WDI API as served 2026-10-22", status="retrieved", dirs=["wdi_calibration", "worldbank_wdi_terms"],
  licence={"name": "CC BY 4.0 (World Bank default)", "quote": "The World Bank Group makes data publicly available according to open data standards and licenses datasets under the Creative Commons Attribution 4.0 International license (CC-BY 4.0).",
           "quote_file": "wdi_calibration/public-licenses.html", "url": "https://datacatalog.worldbank.org/public-licenses"},
  redistribution="yes", redistribution_note="World Bank default CC BY 4.0 with the same caveat (other licences for some datasets). Only world aggregates of national-accounts series are republished.",
  units="constant 2015 USD, persons, years, kg/ha, kWh per capita, Mt CO2e, billion m3, % ", geography="all countries and aggregates", time_span="1960 to 2025",
  variables=["NY.GDP.MKTP.KD", "NY.GDP.PCAP.KD", "SP.POP.TOTL", "SP.DYN.LE00.IN", "AG.YLD.CREL.KG", "EG.USE.ELEC.KH.PC", "EN.GHG.CO2.MT.CE.AR5", "ER.H2O.FWTL.K3", "SI.POV.GINI", "SI.POV.DDAY", "NV.IND.TOTL.KD", "NE.GDI.TOTL.KD", "AG.LND.ARBL.HA"],
  derived=["wdi_world_series"], notes="Same API and licence page as the history register entry wb_wdi_gdp.")
S(id="owid_energy", title="Our World in Data: energy dataset (owid-energy-data.csv) and README", publisher="Our World in Data (from Energy Institute, Ember, EIA and others)", url="https://github.com/owid/energy-data",
  domains=["D7", "D2"], supports=["L5", "L7"], version="master branch file as served 2026-10-22 (README warns the dataset is moving to a new home and the primary-energy method changed)", status="retrieved", dirs=["owid_energy"],
  licence={"name": "CC BY (OWID compilation); third-party components under their own terms", "quote": "The data produced by third parties and made available by Our World in Data is subject to the license terms from the original third-party authors.",
           "quote_file": "owid_energy/README.md", "url": "https://github.com/owid/energy-data"},
  redistribution="unclear", redistribution_note="Columns come from the Energy Institute Statistical Review, Ember and EIA, each with its own terms; OWID says to check them. The Ember columns are available directly from Ember (CC BY). Raw only.",
  units="TWh, %, various", geography="countries and world", time_span="1900 to 2025", variables=["primary energy", "electricity generation and demand", "energy mix"], notes="Used only as a cross-check of Ember electricity totals.")
S(id="faostat", title="FAOSTAT bulk: crops and livestock production (normalized) and land use inputs (normalized); database terms of use", publisher="Food and Agriculture Organization of the United Nations",
  url="https://www.fao.org/faostat/en/#data/QCL", domains=["D7", "D4"], supports=["L3", "M5"], version="bulk files as served 2026-10-22", status="partial",
  licence={"name": "CC BY 4.0 with additional FAO terms (attribution format, no endorsement)", "quote": "all datasets disseminated through FAO corporate statistical databases (see examples in Annex 1) are licensed under the Creative Commons Attribution-4.0 International licence (CC BY 4.0)",
           "quote_file": "faostat/db-terms-of-use.html", "url": "https://www.fao.org/contact-us/terms/db-terms-of-use/en/"},
  redistribution="yes", redistribution_note="CC BY 4.0 'unless specified otherwise in their metadata or webpage'; required citation format: FAO. [year]. [database: dataset]. [Accessed date]. [URL] Licence: CC-BY-4.0. The Food Balances bulk file returned HTTP 403 and was not retrieved; the QCL file is 545 MB uncompressed (34 MB zip).",
  units="tonnes, hectares, kg/ha, heads", geography="countries, regions, world", time_span="1961 to 2024", variables=["area harvested, yield, production for crops", "land use areas"], derived=["faostat_world_cereals"],
  notes="")
S(id="hadcrut5", title="HadCRUT5 (HadCRUT.5.2.0.0) global annual summary series", publisher="Met Office Hadley Centre and Climatic Research Unit", url="https://www.metoffice.gov.uk/hadobs/hadcrut5/", domains=["D7", "D3"],
  supports=["L6", "L7"], version="HadCRUT.5.2.0.0 as served 2026-10-22", status="retrieved",
  licence={"name": "Open Government Licence v3.0 (Crown copyright)", "quote": "HadCRUT5 is subject to Crown copyright protection and is provided under the Open Government License v3", "quote_file": "hadcrut5/terms_and_conditions.html",
           "url": "https://www.metoffice.gov.uk/hadobs/hadcrut5/terms_and_conditions.html"},
  redistribution="yes", redistribution_note="Redistribution with the acknowledgement in the terms page (see audit/data/sources-history.json). The sha256 equals the one recorded there (cross-checked).",
  units="K anomaly", geography="global", time_span="1850 to 2025", variables=["annual global mean temperature anomaly with 95% bounds"], derived=["hadcrut5_global_annual"], notes="Reused from D-057: same file, same sha256.")
S(id="gistemp", title="NASA GISTEMP v4 global annual mean (cross-check only)", publisher="NASA GISS", url="https://data.giss.nasa.gov/gistemp/", domains=["D7"], supports=["L6", "L7"], version="as served 2026-10-22",
  status="retrieved",
  licence={"name": "Not stated for the data table", "quote": "", "url": "https://data.giss.nasa.gov/gistemp/"}, redistribution="unclear",
  redistribution_note="As in sources-history.json: the page states terms for graphics, not for the data table. Cross-check only; no values published.", units="K anomaly (1951-1980 base)", geography="global", time_span="1880 to 2026 (partial)",
  variables=["land-ocean temperature index"], notes="")
S(id="maddison2023", title="Maddison Project Database 2023 (mpd2023_web.xlsx)", publisher="Groningen Growth and Development Centre (Bolt and van Zanden)", url="https://doi.org/10.34894/INZBF2",
  landing_page="https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023", domains=["D7"], supports=["L7"], version="MPD 2023, DataverseNL version 1 released 2024-04-26", status="retrieved",
  licence={"name": "CC BY 4.0", "quote": "Maddison Project Database, version 2023 by Jutta Bolt and Jan Luiten van Zanden is licensed under a Creative Commons Attribution 4.0 International License", "quote_file": "maddison2023/landing.html",
           "url": "https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023"},
  redistribution="yes", redistribution_note="CC BY 4.0. The GGDC page asks that the original papers be cited when data are shown graphically or when fewer than twelve countries are used; otherwise cite Bolt and van Zanden (2024), Journal of Economic Surveys, doi:10.1111/joes.12618.",
  units="2011 USD per person (GDP per capita), thousand persons", geography="169 countries/regions", time_span="1 CE to 2022", variables=["GDP per capita", "population"], derived=["maddison_world_gdp_per_capita"], notes="")
S(id="ucdp", title="UCDP/PRIO Armed Conflict Dataset v26.1 and v25.1 (CSV zips) and UCDP downloads page", publisher="Uppsala Conflict Data Program (UCDP) and PRIO", url="https://ucdp.uu.se/downloads/", domains=["D8"],
  supports=["L4"], version="v26.1 (1946-2025) and v25.1", status="retrieved",
  licence={"name": "CC BY 4.0", "quote": "All datasets are free of charge and licensed under CC BY 4.0", "quote_file": "ucdp/downloads.html", "url": "https://ucdp.uu.se/downloads/"},
  redistribution="yes", redistribution_note="CC BY 4.0 with citation of the publications listed with each dataset. M5 plan/D-008: used only as a labelled plausibility overlay for S7, never a calibration target.",
  units="conflict-year records, battle-related deaths (best estimate)", geography="countries/locations", time_span="1946 to 2025", variables=["state-based armed conflicts per year", "intensity level"], derived=["ucdp_conflicts_per_year"], notes="")

# --------------------------------------------------------------------------------------------------------------- D8 / blocked or page-only
S(id="energy_institute_sr", title="Energy Institute Statistical Review of World Energy 2026: data downloads page (the Excel file needs an e-mail address and was not retrieved)", publisher="Energy Institute",
  url="https://www.energyinst.org/statistical-review/resources-and-data-downloads", domains=["D7", "D2"], supports=["L5", "L7"], version="page as served 2026-10-22", status="blocked", role="document",
  licence={"name": "Not read (terms and conditions page not opened)", "quote": ""}, redistribution="unclear",
  redistribution_note="The page says 'Please enter your email to access the download'; the direct file URL returned HTTP 403. Not worked around.", units="n/a", geography="n/a", time_span="n/a", variables=[], notes="See needs-user.")
S(id="irena_stats", title="IRENA renewable capacity statistics (not retrieved)", publisher="International Renewable Energy Agency", url="https://www.irena.org/Data/Downloads/IRENASTAT", domains=["D8"], supports=["L5", "L7"],
  version="not retrieved", status="blocked", role="document", licence={"name": "Not read", "quote": ""}, redistribution="unclear", redistribution_note="HTTP 403.", units="n/a", geography="n/a", time_span="n/a", variables=[], notes="")
S(id="unfccc_ghg", title="UNFCCC GHG data portal (landing page, 212 bytes)", publisher="UNFCCC", url="https://unfccc.int/process-and-meetings/transparency-and-reporting/greenhouse-gas-data/ghg-data-unfccc", domains=["D3"], supports=["L6"],
  version="not retrieved", status="blocked", role="document", licence={"name": "Not read", "quote": ""}, redistribution="unclear", redistribution_note="The page returned a 212-byte shell (JavaScript-rendered portal); no data.", units="n/a", geography="n/a", time_span="n/a", variables=[], notes="")
S(id="usgs_historical", title="USGS Historical Statistics for Mineral and Material Commodities and USGS copyright page (empty responses)", publisher="US Geological Survey", url="https://www.usgs.gov/centers/national-minerals-information-center/historical-statistics-mineral-and-material-commodities",
  domains=["D6"], supports=["M5"], version="not retrieved", status="blocked", role="document", dirs=["usgs_historical", "usgs_copyright", "usgs_mcs2025_data", "sciencebase_mcs2025", "sciencebase_mcs2026"],
  licence={"name": "Not read", "quote": ""}, redistribution="unclear", redistribution_note="usgs.gov answered with an empty HTTP 202 bot-challenge response, ScienceBase with HTTP 403; not worked around. The long copper, lithium, gallium, germanium, rare-earth and silicon production histories in this dataset are therefore missing: see needs-user.",
  units="n/a", geography="n/a", time_span="n/a", variables=[], notes="")
S(id="ipcc_ar6_wg1_atlas", title="IPCC WGI Atlas repository LICENSE (CMIP6 regional aggregates used by the warming map; raw 385 files not re-downloaded)", publisher="IPCC WGI Technical Support Unit / Atlas", url="https://github.com/IPCC-WG1/Atlas",
  domains=["D4", "D7"], supports=["L3", "L7"], version="commit ed29da33d38ae767d19caafd4cde06042cbe00f4", status="partial", role="document",
  licence={"name": "CC BY 4.0 (datasets), Apache 2.0 (code)", "quote": "All datasets and notebooks in this repository are provided under the Creative Commons Attribution 4.0 license (CC BY 4.0).", "quote_file": "ipcc_ar6_wg1_atlas/LICENSE.md", "url": "https://github.com/IPCC-WG1/Atlas/blob/ed29da33d38ae767d19caafd4cde06042cbe00f4/LICENSE.md"},
  redistribution="yes", redistribution_note="Files and checksums are in audit/data/atlas-cmip6-files.json (D-057); only the licence file was re-fetched here. The regional aggregates would also give world mean tas per CMIP6 model, needed to place ISIMIP runs on global-warming levels.",
  units="K", geography="AR6 regions", time_span="1850-2100", variables=["monthly regional tas for 32 CMIP6 models"], notes="")
