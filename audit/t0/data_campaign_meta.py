"""Curated metadata for the D-058 source register (hand-written; part 1 of the file).

Every licence quote is verified verbatim against the saved file named in quote_file by data_campaign_register.py.
A source whose licence is not stated, or is stated ambiguously, is recorded as redistribution 'unclear' (never guessed).
Domains: D1 AI compute and hardware; D2 data-centre electricity and water; D3 emissions; D4 climate impacts (yield, health, damages);
D5 labour and automation; D6 minerals and materials; D7 calibration and history; D8 other.
Supports: L3 yield/health, L4 labour, L5 compute-electricity, L6 and L7 emissions, DC data centres, AI context, M5 minerals/water.
"""

SOURCES = []
CROSS_CHECKS = []
NEEDS_USER = []

EPOCH_QUOTE = "Epoch AI's data is free to use, distribute, and reproduce provided the source and authors are credited under the"
EPOCH_NOTE = "Epoch's data page and the README in each ZIP state the Creative Commons Attribution license (version not named in the sentence; the README links the 4.0 text). Attribution: Epoch AI, with the dataset name and URL given in the README."


def S(**kw):
    SOURCES.append(kw)


def epoch(id, title, url, version, units, span, variables, supports, zipname, notes="", member="README.md", geography="global"):
    S(id=id, title=title, publisher="Epoch AI", url=url, landing_page="https://epoch.ai/data", domains=["D1"] + (["D2"] if "DC" in supports else []),
      supports=supports, version=version, status="retrieved",
      licence={"name": "Creative Commons Attribution (CC BY; the README links version 4.0)", "quote": EPOCH_QUOTE,
               "quote_file": f"{id}/{zipname}!{member}" if zipname.endswith(".zip") else "epoch_data_page/data.html",
               "url": "https://epoch.ai/data"},
      redistribution="yes", redistribution_note=EPOCH_NOTE, units=units, geography=geography, time_span=span, variables=variables, notes=notes)


# --------------------------------------------------------------------------------------------------------------- D1 AI compute and hardware
S(id="epoch_data_page", title="Epoch AI data hub (page listing every dataset, update dates and the licence sentence)", publisher="Epoch AI",
  url="https://epoch.ai/data", domains=["D1"], supports=["AI"], version="page as served 2026-10-22 (datasets updated 2026-03-13 to 2026-10-22)", status="retrieved", role="document",
  licence={"name": "Creative Commons Attribution", "quote": "Epoch AI's data is free to use, distribute, and reproduce provided the source and authors are credited under the Creative Commons Attribution license.",
           "quote_file": "epoch_data_page/data.html", "url": "https://epoch.ai/data"},
  redistribution="yes", redistribution_note="Licence sentence for Epoch datasets; the page itself is kept only as a record.", units="n/a", geography="n/a", time_span="n/a",
  variables=["dataset list", "update dates"], notes="Used to find the download links and to quote the licence for the CSV file that has no README.")

epoch("epoch_ai_models", "Epoch AI: Data on AI models (notable, frontier, large-scale, all)", "https://epoch.ai/data/ai_models.zip", "ZIP updated 2026-10-19",
      "FLOP (training compute), parameters, dataset size, USD (2023) compute cost, W (training power draw)", "1950-07 to 2026-10 (publication dates; notable 1078 rows, all 3628 rows)",
      ["training compute (FLOP)", "parameters", "publication date", "organisation", "training hardware", "hardware quantity", "training time (h)", "training cost (2023 USD)", "training power draw (W)"],
      ["AI", "L5", "DC"], "ai_models.zip",
      notes="Compute is estimated by Epoch; the 'Confidence' column grades each row. The OWID series 'training computation' is a processed copy of this dataset.")
epoch("epoch_ai_chip_sales", "Epoch AI: Data on AI chip sales", "https://epoch.ai/data/ai_chip_sales.zip", "ZIP updated 2026-10-21",
      "chips (units), H100-equivalents (H100e), W (TDP), USD", "2022-Q1 to 2026-Q3 (quarterly, estimates generated 2026-08/10)",
      ["units sold by chip type and quarter (median, 5th, 95th percentile)", "H100e compute", "total TDP (W)", "designer", "cumulative timelines"],
      ["AI", "L5", "DC"], "ai_chip_sales.zip", notes="Estimates with 5th and 95th percentiles from Epoch's model of company disclosures; incomplete rows flagged in the 'Incomplete' column.")
epoch("epoch_data_centers", "Epoch AI: AI data centers (frontier data centre hub)", "https://epoch.ai/data/data_centers/data_centers.zip", "ZIP updated 2026-10-20",
      "MW (power), H100e, USD billion (2025), MGD (water use), 8-bit OP/s", "2018-12 to 2030-01 (timelines include projected dates)",
      ["current power (MW)", "current H100e", "capital cost (2025 USD bn)", "timeline of IT power, power, H100e per date", "chillers and cooling towers", "water use (MGD)", "owner, country"],
      ["DC", "L5", "AI"], "data_centers.zip",
      notes="95 data centres, sum of current power 14,203 MW at retrieval (computed here). Water use (MGD) is filled for few rows (median 0). Timelines past the retrieval date are Epoch projections from permits and construction, not observations.")
epoch("epoch_gpu_clusters", "Epoch AI: GPU clusters (supercomputers, 2010-2025)", "https://epoch.ai/data/gpu_clusters.csv", "CSV updated 2026-03-13 (legacy dataset, superseded by the data centers hub for 2025 on)",
      "OP/s, H100e, MW, USD", "2010-11 to 2025-07 (first operational dates)", ["max OP/s", "H100 equivalents", "chip type and quantity", "power capacity (MW)", "hardware cost", "country, owner, sector"],
      ["AI", "DC"], "gpu_clusters.csv", notes="482 clusters; final update before the move to the data centers hub.")
epoch("epoch_ml_hardware", "Epoch AI: Machine learning hardware (183 accelerators)", "https://epoch.ai/data/ml_hardware.zip", "ZIP updated 2026-10-21",
      "FLOP/s, W (TDP), bytes, byte/s, USD, nm, FLOP/s per W", "2008-06 to 2026-09 (release dates)",
      ["tensor FP16/BF16, FP8, FP4 FLOP/s", "TDP (W)", "memory", "bandwidth", "release price", "process node", "energy efficiency", "price-performance"], ["L5", "DC", "AI"], "ml_hardware.zip",
      notes="Basis for the hardware-efficiency (FLOP per joule) trend the data-centre module needs against its eta ceiling (D-055).")
epoch("epoch_ai_chip_owners", "Epoch AI: AI chip owners (who holds the world's AI chips and compute)", "https://epoch.ai/data/ai_chip_owners.zip", "ZIP updated 2026-05-12",
      "H100e, W, units", "2022 to 2026 (cumulative by quarter)", ["cumulative H100e by designer and chip type", "power (MW)"], ["AI", "DC"], "ai_chip_owners.zip")
epoch("epoch_ai_chip_users", "Epoch AI: AI chip users (compute used or rented by the leading AI developers)", "https://epoch.ai/data/ai_chip_users.zip", "ZIP updated 2026-09-09",
      "H100e", "year-end snapshots", ["H100e by lab"], ["AI"], "ai_chip_users.zip")
epoch("epoch_ai_chip_components", "Epoch AI: AI chip components (wafer capacity, CoWoS packaging, HBM consumed by AI chip designers)", "https://epoch.ai/data/ai_chip_components.zip", "ZIP updated 2026-07-23",
      "wafers, CoWoS capacity share, HBM bytes", "quarterly", ["advanced logic wafers by chip and designer", "CoWoS", "HBM", "supply denominators"], ["AI", "DC", "M5"], "ai_chip_components.zip",
      notes="Supply-side constraint on chips (fabrication and packaging), relevant to the supply-limited diagnostic.")
epoch("epoch_ai_companies", "Epoch AI: AI companies (revenue, funding, staff, compute spend)", "https://epoch.ai/data/ai_companies.zip", "ZIP updated 2026-10-08",
      "USD, people", "2015 to 2026", ["annualized revenue (USD)", "valuation", "equity funding", "staff count", "compute spend"], ["AI", "L4"], "ai_companies.zip",
      notes="Company-reported or press-reported figures collected by Epoch; confidence graded per row.")
epoch("epoch_benchmark_data", "Epoch AI: Capabilities and benchmarking data (benchmarks, Epoch Capabilities Index)", "https://epoch.ai/data/benchmark_data.zip", "ZIP updated 2026-10-22",
      "benchmark scores, ECI score", "model release dates to 2026-10", ["benchmark scores by model", "ECI scores", "model metadata (compute, parameters)"], ["AI"], "benchmark_data.zip",
      notes="Context for the capability side of the AI race; not an input to any current sector.")

S(id="owid_ai_compute", title="Our World in Data: computation used to train notable AI systems (processed Epoch AI series)", publisher="Our World in Data (data from Epoch AI)",
  url="https://ourworldindata.org/grapher/artificial-intelligence-training-computation", domains=["D1"], supports=["AI"], version="grapher export 2026-10-22; Epoch AI (2026) with major processing by Our World in Data",
  status="retrieved",
  licence={"name": "CC BY (Our World in Data), data adapted from Epoch AI (CC BY)", "quote": "Data produced by us falls under our permissive CC BY license",
           "quote_file": "owid_terms/faqs.html", "url": "https://ourworldindata.org/faqs"},
  redistribution="yes", redistribution_note="OWID states CC BY for data it produces; the underlying Epoch AI data is CC BY. Not used for derived series (the Epoch original is used instead).",
  units="petaFLOP", geography="global", time_span="1950 to 2026", variables=["training computation (petaFLOP) by model"],
  notes="Duplicate in content of epoch_ai_models; kept as a cross-check of the processing.", dirs=["owid_ai_compute", "owid_terms"])
S(id="owid_dc_share", title="Our World in Data: data centres' share of electricity demand (processed IEA/Ember series)", publisher="Our World in Data (data from IEA 2025 and Ember 2026)",
  url="https://ourworldindata.org/grapher/data-centers-share-electricity-demand", domains=["D2"], supports=["DC", "L5"], version="grapher export 2026-10-22", status="retrieved",
  licence={"name": "Mixed: OWID CC BY processing of IEA (Non-CC terms) and Ember (CC BY) data", "quote": "The data produced by third parties and made available by Our World in Data is subject to the license terms from the original third-party authors.",
           "quote_file": "owid_energy/README.md", "url": "https://github.com/owid/energy-data"},
  redistribution="unclear", redistribution_note="The series is built on IEA data whose terms are 'Terms of Use for Non-CC Material' (iea_energy_ai data product page); OWID's CC BY does not remove that. Raw only; the IEA report itself (CC BY 4.0) is the citable source.",
  units="% of electricity demand", geography="selected countries and world", time_span="2024 and later (small file)", variables=["data centres' share of national electricity demand"],
  notes="Small file, retrieved only to see what OWID publishes from the IEA/Ember data.")

S(id="stanford_ai_index", title="Stanford HAI: AI Index Report 2025 (PDF) and 2026 report pages", publisher="Stanford Institute for Human-Centered AI",
  url="https://hai.stanford.edu/ai-index/2025-ai-index-report", domains=["D1"], supports=["AI"], version="AI Index 2025 annual report (PDF); 2026 report web pages retrieved 2026-10-22", status="partial",
  licence={"name": "CC BY-ND 4.0 (report)", "quote": "The AI Index 2025 Annual Report by Stanford University is licensed under Attribution-NoDerivatives 4.0 International.",
           "quote_file": "stanford_ai_index/hai_ai_index_report_2025.pdf", "url": "https://hai.stanford.edu/ai-index/2025-ai-index-report"},
  redistribution="no", redistribution_note="NoDerivatives: no derived series are made from the report. Numbers may be cited with attribution in documents. The AI Index public data (charts' spreadsheets) is a separate Google Drive download that was not found as a stable link; see needs-user.",
  units="various", geography="global", time_span="to 2024 (2025 report)", variables=["AI Index chapters: R&D, technical performance, economy, policy"],
  notes="The 2026 report landing pages were saved; the 2026 report PDF link was not found on the pages read.", dirs=["stanford_ai_index"])
S(id="top500", title="TOP500 supercomputer lists (June 2026, November 2025 list pages; FAQ)", publisher="TOP500.org", url="https://top500.org/lists/top500/", domains=["D1"], supports=["AI"],
  version="list pages 2026/06 and 2025/11 as served 2026-10-22", status="partial",
  licence={"name": "No licence stated on the pages read (page footer: Copyright 1993-2026 TOP500.org)", "quote": "Copyright 1993-2026 TOP500.org",
           "quote_file": "top500/top500-2026-06.html", "url": "https://top500.org/lists/top500/2026/06/"},
  redistribution="unclear", redistribution_note="Only the public HTML list pages were saved. The full list files (XML/Excel) need a TOP500 login, which is not used. No derived series made.",
  units="PFlop/s (Rmax, Rpeak), kW", geography="global", time_span="2025-11 and 2026-06 lists", variables=["system rank, Rmax, Rpeak, cores, power"],
  notes="HPC (Linpack, FP64) rather than AI training clusters; weak relevance to the AI-compute link.")
S(id="sia_sales", title="Semiconductor Industry Association: global semiconductor sales press releases (market data page)", publisher="Semiconductor Industry Association (SIA)",
  url="https://www.semiconductors.org/policies/tax/market-data/", domains=["D1"], supports=["AI", "DC"], version="page as served 2026-10-22 (latest release 2026-10-05, August 2026 data)", status="retrieved",
  licence={"name": "Copyright SIA, all rights reserved (page footer)", "quote": "2026 Semiconductor Industry Association. All Rights Reserved.", "quote_file": "sia_sales/market-data.html",
           "url": "https://www.semiconductors.org/policies/tax/market-data/"},
  redistribution="no", redistribution_note="Press-release text is copyrighted. A few headline figures are cited in documents with attribution: annual sales 2025 $791.7 billion (+25.6% on $630.5 billion in 2024); August 2026 $159.7 billion in the month (SIA, 2026-10-05).",
  units="USD billion per month or year", geography="global", time_span="2025-09 to 2026-08 (page 1 of 28)", variables=["monthly and annual worldwide semiconductor sales"],
  notes="The underlying monthly series is WSTS data; the WSTS free file is raw-only (copyright).")
S(id="wsts", title="WSTS Historical Billings Report (monthly semiconductor revenue by region, free download)", publisher="World Semiconductor Trade Statistics (WSTS)",
  url="https://www.wsts.org/67/Historical-Billings-Report", domains=["D1"], supports=["AI", "DC"], version="August 2026 data (file posted 2026-10)", status="retrieved",
  licence={"name": "Copyright WSTS, all rights reserved", "quote": "All WSTS Publications, including this Web Site, are copyrighted by WSTS Inc. All rights reserved.",
           "quote_file": "wsts/historical-billings.html", "url": "https://www.wsts.org/67/Historical-Billings-Report"},
  redistribution="no", redistribution_note="The page says the file is a free download without login, but also that reproduction without written permission is prohibited. Raw only; used for reading, not redistributed.",
  units="USD thousand or million per month", geography="Americas, Europe, Japan, Asia Pacific", time_span="1986 to 2026-08", variables=["monthly semiconductor billings by region", "3-month moving average"],
  notes="Long monthly semiconductor revenue series: context for the chip-supply side of the AI race.")
S(id="tsmc_esg", title="TSMC: 2025 Sustainability Report, Water Statement, 2024 Annual Report pages", publisher="Taiwan Semiconductor Manufacturing Company",
  url="https://esg.tsmc.com/en/download", domains=["D1", "D2"], supports=["DC", "M5", "AI"], version="Sustainability Report published 2025 (file name 2025-TSMC-Sustainability-Report-e.pdf); 2024 Annual Report pages 158-159", status="retrieved",
  licence={"name": "No licence stated in the documents read (corporate report)", "quote": "", "url": "https://esg.tsmc.com/en/download"},
  redistribution="unclear", redistribution_note="Corporate report without a stated licence: cited figures only, with page references; no derived series are committed.",
  units="million m3 (water), GWh (electricity), tCO2e", geography="TSMC fabs (Taiwan, others)", time_span="2024 and earlier (reporting year stated in the report)", variables=["water withdrawal and consumption", "electricity use", "emissions", "unit water use"],
  notes="One company, not the sector. Figures extracted with page numbers in docs/links/DC.md and docs/links/L5.md.")


# --------------------------------------------------------------------------------------------------------------- later parts (injected globals S, CROSS_CHECKS, NEEDS_USER)
import importlib.util as _u
import pathlib as _p

for _n in ("d2_d3", "d4_d5", "d6_d7_d8", "papers", "crosschecks_needs"):
    _f = _p.Path(__file__).with_name(f"data_campaign_meta_{_n}.py")
    if _f.exists():
        _s = _u.spec_from_file_location(f"data_campaign_meta_{_n}", _f)
        _m = _u.module_from_spec(_s)
        _m.S, _m.CROSS_CHECKS, _m.NEEDS_USER = S, CROSS_CHECKS, NEEDS_USER
        _s.loader.exec_module(_m)
