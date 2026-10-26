"""Register metadata, part 3: D4 climate impacts for yield and health, D5 labour and automation. S, CROSS_CHECKS, NEEDS_USER are injected."""

# --------------------------------------------------------------------------------------------------------------- D4 yield, health, damages
S(id="lancet_countdown", title="Lancet Countdown 2025 report: indicator data downloads (53 workbooks incl. heat exposure, heat-related mortality, labour capacity, outdoor workers)", publisher="Lancet Countdown on health and climate change",
  url="https://lancetcountdown.org/explore-our-data/", domains=["D4"], supports=["L3", "L4"], version="2025 report (published online 2025-10-29), workbooks as served 2026-10-22", status="retrieved",
  licence={"name": "CC BY-NC-SA 4.0", "quote": "This data, and associated data visualisations, are provided at no-cost under a Creative Commons Attribution-Non Commercial-Share Alike License (CC BY-NC-SA 4.0).",
           "quote_file": "lancet_countdown/Indicator-1.1.5_Data-Download_2025-Lancet-Countdown-Report-1.xlsx", "url": "https://lancetcountdown.org/explore-our-data/"},
  redistribution="no", redistribution_note="Non-commercial and share-alike (stated in the DATA GUIDANCE sheet of the workbooks): incompatible with F3's CC BY derived data. Raw only; headline numbers may be cited with attribution (for example heat-related deaths 546,000 a year in 2012-2021, +63.2% on 1990-1999, indicator 1.1.5). The page also says its visualisations are free to use and share, which is not the data licence.",
  units="deaths, % of deaths, days, hours of labour lost, people", geography="global, WHO regions, Lancet Countdown regions, HDI groups, countries", time_span="1990/2000 to 2024 depending on the indicator",
  variables=["1.1.5 heat-related mortality (attributable fraction and number)", "1.1.2 heatwave exposure", "1.1.3 outdoor workers", "1.1.4 heat and physical activity", "1.3.x labour capacity loss (see workbook list)", "crop-related indicators"],
  notes="Heat mortality is estimated with the Zhao et al. (2021) three-stage method (quasi-Poisson DLNM, multivariate meta-regression), per the workbook guidance.")
S(id="isimip", title="ISIMIP agriculture sector: ISIMIP3b crop-model yield simulations (records, API listing and terms; model output files NOT downloaded)", publisher="ISIMIP / PIK", url="https://data.isimip.org/10.48364/ISIMIP.723340",
  landing_page="https://data.isimip.org/", domains=["D4"], supports=["L3"], version="ISIMIP3b simulation data (DOI 10.48364/ISIMIP.723340) and pre-processed bias-adjusted yield data (DOI 10.48364/ISIMIP.910253, v1.0 2024-08-08)", status="partial",
  licence={"name": "CC0 1.0 Universal Public Domain Dedication (dataset records)", "quote": "CC0 1.0 Universal Public Domain Dedication (CC0 1.0)", "quote_file": "isimip/preprocessed-yield-910253.html",
           "url": "https://data.isimip.org/10.48364/ISIMIP.910253"},
  redistribution="yes", redistribution_note="CC0 per the dataset record 910253; the ISIMIP site content is CC BY 4.0. Only the record pages, the terms page and two API listing pages (1001 ISIMIP3b agriculture yield datasets, about 10 MB each) were saved: the model outputs are tens of GB and were not downloaded in this run.",
  units="t/ha (yield), per crop, model, GCM, scenario, irrigation", geography="global 0.5 degree grids (annual)", time_span="1850-2100 (historical, picontrol, ssp126, ssp370, ssp585)",
  variables=["yield by crop (maize, wheat, rice, soy), crop model, GCM, SSP, irrigation, soc scenario"], notes="This is the dataset needed for yield-versus-global-warming-level curves; see needs-user and docs/links/L3.md for a small defined subset.")
S(id="burke2015", title="Burke, Hsiang and Miguel (2015) replication data: projected GDP per capita with and without climate change (RCP8.5, SSP5) and Stanford Digital Repository record", publisher="Marshall Burke / Stanford Digital Repository",
  url="https://web.stanford.edu/~mburke/climate/data.html", landing_page="https://purl.stanford.edu/wb587wt4560", domains=["D4"], supports=["L3", "L4"], version="author page as served 2026-10-22; SDR record version 1 dated 2026-07-27", status="partial",
  licence={"name": "No licence stated; SDR: 'may be subject to additional license and use restrictions applied by the depositor'", "quote": "Content distributed via the Stanford Digital Repository may be subject to additional license and use restrictions applied by the depositor.",
           "quote_file": "burke2015/purl.html", "url": "https://purl.stanford.edu/wb587wt4560"},
  redistribution="unclear", redistribution_note="Two projection CSVs (per-country GDP per capita 2010-2099 with and without climate change) were saved; the full replication zip from the repository was not retrieved. The author page asks users to cite the paper. No licence is stated, so no derived file; the damage-function parameters (temperature optimum about 13 C, response coefficients) are to be read from the paper.",
  units="GDP per capita (constant USD, as in the files)", geography="countries", time_span="2010 to 2099", variables=["per capita GDP with climate change", "per capita GDP without climate change"], notes="D-007 says the Burke growth-rate form is not represented; this is context.")
S(id="kalkuhl_wenz2020", title="Kalkuhl and Wenz (2020) replication data record (Zenodo 4743845; README only retrieved)", publisher="MCC and PIK", url="https://zenodo.org/records/4743845", domains=["D4"], supports=["L3", "L4"],
  version="Zenodo record published 2020-08-04", status="partial",
  licence={"name": "CC BY 4.0 (Zenodo record)", "quote": "\"license\":{\"id\":\"cc-by-4.0\"}", "quote_file": "kalkuhl_wenz2020/zenodo-4743845.json", "url": "https://zenodo.org/records/4743845"},
  redistribution="yes", redistribution_note="Record licence cc-by-4.0. The 223 MB replication zip was not downloaded: the task asks for damage parameters only, which are read from the paper.",
  units="various", geography="1,500+ regions in 77 countries", time_span="1900 to 2014", variables=["regional GDP, temperature and precipitation panel"], notes="")
S(id="ipcc_ar6_wg2", title="IPCC AR6 WGII chapters 4 (water), 5 (food, fibre), 7 (health), 16 (key risks) and IPCC copyright page", publisher="IPCC", url="https://www.ipcc.ch/report/ar6/wg2/", domains=["D4"],
  supports=["L3", "M5"], version="AR6 WGII final chapter PDFs as served 2026-10-22", status="retrieved",
  licence={"name": "IPCC copyright: personal non-commercial use; no redistribution", "quote": "without any right to resell or redistribute it or to compile or create derivative works there from",
           "quote_file": "ipcc_ar6_wg2/copyright.html", "url": "https://www.ipcc.ch/copyright/"},
  redistribution="no", redistribution_note="Cited by chapter, page and table only; numbers are quoted in docs/links/L3.md with page references. No derived series.",
  units="% yield change per degree and per warming level, deaths, risk levels", geography="global and regional", time_span="to 2100", variables=["yield change vs warming level tables", "heat-related mortality", "water scarcity"],
  notes="Chapter 5 is 18 MB and 19,409 text lines; searched with pdftotext.")
S(id="who_gho", title="WHO Global Health Observatory: climate change topic landing page (page only)", publisher="World Health Organization", url="https://www.who.int/data/gho/data/themes/topics/topic-details/GHO/climate-change", domains=["D4"],
  supports=["L3"], version="page as served 2026-10-22", status="partial", role="document", licence={"name": "Not read (WHO data terms are a separate page)", "quote": ""}, redistribution="unclear",
  redistribution_note="Only the landing page was saved; no data file or terms page. No WHO heat-health dataset was found as a stable file.", units="n/a", geography="n/a", time_span="n/a", variables=[], notes="See needs-user.")

# --- published papers (documents; parameters are cited from them, with page references, in docs/links)
def paper(id, title, publisher, url, version, licence, quote, quote_file, redistribution, note, supports, status="retrieved", dirs=None, domains=("D4",), only=None):
    d = dict(id=id, title=title, publisher=publisher, url=url, domains=list(domains), supports=supports, version=version, status=status, role="document",
             licence={"name": licence, "quote": quote, **({"quote_file": quote_file, "url": url} if quote else {})}, redistribution=redistribution, redistribution_note=note,
             units="n/a (published parameters and results)", geography="as in the paper", time_span="as in the paper", variables=["published results used for functional forms and parameter values"], notes="")
    if dirs:
        d["dirs"] = dirs
    if only:
        d["only"] = only
    S(**d)


paper("papers_kalkuhl_wenz2020", "Kalkuhl and Wenz (2020), The impact of climate conditions on economic production, J. Environ. Econ. Manag. 103:102360", "Elsevier (open access, PIK copy)", "https://doi.org/10.1016/j.jeem.2020.102360",
      "published 2020; PIK open-access copy", "CC BY-NC-ND (as printed in the article)", "This is an open access article under the CC BY-NC-ND license", "papers_kalkuhl_wenz2020/kalkuhl_wenz2020.pdf", "no",
      "Open access under CC BY-NC-ND: parameters are cited with page numbers only, no text or figures are republished.", ["L3", "L4"])
paper("papers_jagermeyr2021", "Jagermeyr et al. (2021), Climate impacts on global agriculture emerge earlier in new generation of climate and crop models, Nature Food 2:873-885 (article page only)", "Springer Nature",
      "https://doi.org/10.1038/s43016-021-00400-y", "published 2021; the publisher returned the article page (abstract), not the PDF", "Not read (article page only)", "", "", "unclear",
      "Only the HTML article page with the abstract was returned for the PDF URL, so the licence statement of the full text was not read (the journal is open access; this was not verified). The abstract numbers (end-of-century maize change from +5% to -6% under SSP1-2.6 and from +1% to -24% under SSP5-8.5 versus the earlier generation) are cited from the abstract. Full text: needs-user.",
      ["L3"], status="partial", dirs=["papers_jagermeyr2021"])
paper("papers_vicedo2021", "Vicedo-Cabrera et al. (2021), The burden of heat-related mortality attributable to recent human-induced climate change, Nature Climate Change 11:492-500 (article page only)", "Springer Nature",
      "https://doi.org/10.1038/s41558-021-01058-x", "published 2021; article page only", "Not read (article page only)", "", "", "unclear",
      "Only the HTML article page (abstract) was returned. Needed for heat-mortality attribution by country; full text: needs-user.", ["L3"], status="partial", dirs=["papers_vicedo2021"])
paper("papers_dunne2013", "Dunne et al. (2013), Reduced work capacity in a warming climate, Nature Climate Change 3:563-566 (article page only)", "Springer Nature",
      "https://doi.org/10.1038/nclimate1827", "published 2013; article page only", "Not read (article page only)", "", "", "unclear",
      "Only the HTML article page (abstract) was returned. Needed for the labour-capacity-versus-heat-stress function; full text: needs-user.", ["L3", "L4"], status="partial", dirs=["papers_dunne2013"])
paper("papers_zhao2017", "Zhao et al. (2017), Temperature increase reduces global yields of major crops in four independent estimates, PNAS 114:9326-9331 (not retrieved)", "PNAS",
      "https://doi.org/10.1073/pnas.1701762114", "not retrieved", "Not read", "", "", "unclear",
      "The PNAS URL returned HTTP 403 and the PubMed Central PDF URL returned an HTML interstitial page, not a PDF; neither was worked around. The yield-per-degree values (wheat, rice, maize, soybean) are therefore NOT verified here against the paper; they appear in docs/links/L3.md only with the label [from memory, unverified]. Full text: needs-user.",
      ["L3"], status="blocked", dirs=["papers_zhao2017"])
paper("papers_schlenker_roberts2009", "Schlenker and Roberts (2009), Nonlinear temperature effects indicate severe damages to US crop yields under climate change, PNAS 106:15594-15598 (not retrieved)", "PNAS",
      "https://doi.org/10.1073/pnas.0906865106", "not retrieved", "Not read", "", "", "unclear",
      "PNAS returned HTTP 403 and the PubMed Central PDF URL returned an HTML interstitial page. The 29 C maize threshold is therefore labelled [from memory, unverified] in docs/links/L3.md. Full text: needs-user.", ["L3"], status="blocked", dirs=["papers_schlenker_roberts2009"])
paper("papers_burke2015", "Burke, Hsiang and Miguel (2015), Global non-linear effect of temperature on economic production, Nature 527:235-239 (not retrieved)", "Springer Nature", "https://doi.org/10.1038/nature15725", "not retrieved",
      "Not read", "", "", "unclear", "The author-page PDF URL returned HTTP 404 and the Nature PDF is paywalled. The coefficients are therefore NOT verified; they are labelled [from memory, unverified] in docs/links/L3.md. D-007 notes the same difficulty.", ["L3"], status="blocked", dirs=["papers_burke2015"])
paper("papers_carleton2022", "Carleton et al. (2022), Valuing the global mortality consequences of climate change accounting for adaptation costs and benefits, QJE 137:2037-2105 (not retrieved)", "Oxford University Press",
      "https://doi.org/10.1093/qje/qjac020", "not retrieved", "Not read", "", "", "unclear", "OUP returned HTTP 403. Needed for temperature-mortality response functions with adaptation; needs-user.", ["L3"], status="blocked", dirs=["papers_carleton2022"])
paper("papers_gasparrini2017", "Gasparrini et al. (2017), Projections of temperature-related excess mortality under climate change scenarios, Lancet Planetary Health 1:e360-e367 (not retrieved)", "Elsevier (Lancet)",
      "https://doi.org/10.1016/S2542-5196(17)30156-0", "not retrieved", "Not read", "", "", "unclear", "The Lancet URL returned HTTP 403.", ["L3"], status="blocked", dirs=["papers_gasparrini2017"])

# --------------------------------------------------------------------------------------------------------------- D5 labour and automation
S(id="ilostat", title="ILOSTAT (via the rplumber API): labour income share, output per worker, productivity growth, unemployment, employment by economic activity and by occupation (ILO modelled estimates, Nov 2025)", publisher="International Labour Organization",
  url="https://rplumber.ilo.org/data/indicator/", landing_page="https://ilostat.ilo.org/", domains=["D5"], supports=["L4", "L7"], version="indicator files as served 2026-10-22; modelled estimates Nov. 2025; SDG 10.4.1 last update 2026-03-20",
  status="retrieved",
  licence={"name": "CC BY 4.0 (ILO data published as of 3 May 2023)", "quote": "As of 3 May 2023, databases and datasets together with the accompanying referential metadata are covered by the Creative Commons CC BY 4.0 licence.",
           "quote_file": "ilostat/rights-and-permissions.html", "url": "https://www.ilo.org/rights-and-permissions"},
  redistribution="yes", redistribution_note="Statement is on the ILO 'rights and permissions' page; the ILOSTAT site's own copyright and bulk pages returned HTTP 403 and were not read. The page excludes restricted microdata and says data produced before 3 May 2023 need checking (the files used are current estimates). This resolves the M5 plan STOP item 2 as far as the ILO's public statement goes.",
  units="% of GDP (labour income share); constant 2015 USD per worker; % ; thousands of persons", geography="about 276 countries/areas and aggregates", time_span="labour income share 2004 to 2026; output per worker and employment 1991 to 2025/2027",
  variables=["SDG 10.4.1 labour income share as % of GDP", "GDP_205U output per worker, constant 2015 USD", "SDG 8.2.1 output per worker growth", "UNE_DEAP unemployment rate by sex and age", "EMP_2EMP_SEX_ECO employment by sex and economic activity", "EMP_2EMP_SEX_OCU employment by occupation"],
  derived=["ilostat_labour_income_share", "ilostat_world_employment_by_sector"], notes="Confirms the M5 plan/D-008 note that the labour income share series starts in 2004.")
S(id="pwt110", title="Penn World Table 11.0 (pwt110.xlsx, user guide) with the DataverseNL record", publisher="Groningen Growth and Development Centre (Feenstra, Inklaar, Timmer)", url="https://doi.org/10.34894/FABVLR",
  landing_page="https://www.rug.nl/ggdc/productivity/pwt/", domains=["D5", "D7"], supports=["L4", "L7"], version="PWT 11.0, DataverseNL version 2.0 released 2025-10-10", status="retrieved",
  licence={"name": "CC BY 4.0", "quote": "Penn World Table 11.0 by Robert C. Feenstra, Robert Inklaar and Marcel P. Timmer is licensed under a Creative Commons Attribution 4.0 International License", "quote_file": "pwt110/landing.html", "url": "https://www.rug.nl/ggdc/productivity/pwt/"},
  redistribution="yes", redistribution_note="CC BY 4.0 (page statement and the DataverseNL record licence field). Attribution: Feenstra, Inklaar and Timmer (2015), AER 105(10), 3150-3182. This supplies the long labour-share series (labsh) the M5 plan could not name (STOP item 3).",
  units="various: real GDP, capital, labour share (labsh), TFP, hours", geography="185 countries", time_span="1950 to 2023", variables=["rgdpna", "labsh (share of labour compensation in GDP)", "emp", "avh", "ctfp", "capital stock"],
  derived=["pwt_labour_share"], notes="")
S(id="wdi_labour", title="World Bank WDI labour indicators (labour force, employment ratio, unemployment, employment by sector, participation), all countries 1960-2025", publisher="World Bank (ILO modelled estimates)",
  url="https://api.worldbank.org/v2/country/all/indicator/SL.TLF.TOTL.IN", landing_page="https://data.worldbank.org/", domains=["D5", "D7"], supports=["L4"], version="WDI API as served 2026-10-22", status="retrieved",
  dirs=["wdi_labour"], licence={"name": "CC BY 4.0 (World Bank default)", "quote": "The World Bank Group makes data publicly available according to open data standards and licenses datasets under the Creative Commons Attribution 4.0 International license (CC-BY 4.0).",
                                "quote_file": "wdi_calibration/public-licenses.html", "url": "https://datacatalog.worldbank.org/public-licenses"},
  redistribution="yes", redistribution_note="World Bank default CC BY 4.0; the same page says 'Many datasets are available under other licenses', and WDI series carry their original provider (here ILO modelled estimates, themselves CC BY). Only world aggregates are republished.",
  units="persons, %", geography="all countries and aggregates", time_span="1960 to 2025", variables=["SL.TLF.TOTL.IN", "SL.EMP.TOTL.SP.ZS", "SL.UEM.TOTL.ZS", "SL.AGR.EMPL.ZS", "SL.IND.EMPL.ZS", "SL.SRV.EMPL.ZS", "SL.TLF.CACT.ZS"],
  derived=["wdi_world_series"], notes="Provider of the labour series: ILO modelled estimates, not World Bank national accounts.")
S(id="anthropic_econ_index", title="Anthropic Economic Index (labor market impacts: job exposure and task penetration; robot exposure by occupation; June 2026 release documentation)", publisher="Anthropic",
  url="https://huggingface.co/datasets/Anthropic/EconomicIndex", landing_page="https://www.anthropic.com/economic-index", domains=["D5"], supports=["L4", "AI"],
  version="repository main as served 2026-10-22; labor_market_impacts and robot_exposure folders; release 2026-06-26 documentation (the 77 MB and 219 MB usage CSVs of that release were not downloaded)", status="retrieved",
  licence={"name": "CC BY (README); the dataset-card header says 'license: mit' (conflict recorded)", "quote": "Data released under CC-BY, code released under MIT License.", "quote_file": "anthropic_econ_index/README.md", "url": "https://huggingface.co/datasets/Anthropic/EconomicIndex"},
  redistribution="yes", redistribution_note="The README body says data CC-BY and code MIT; the YAML header of the same README says 'license: mit'. Both are permissive; the stricter reading (CC BY, attribution to Anthropic) is applied. Version of CC BY is not named.",
  units="exposure scores, shares", geography="O*NET/SOC occupations (US)", time_span="2025-2026 usage windows", variables=["observed AI exposure by occupation (job_exposure)", "task-level penetration", "robot exposure by occupation"],
  derived=["task_exposure_summary"], notes="")
S(id="gpts_are_gpts", title="OpenAI: GPTs are GPTs occupation-level exposure (occ_level.csv)", publisher="OpenAI (Eloundou, Manning, Mishkin, Rock)", url="https://github.com/openai/GPTs-are-GPTs", domains=["D5"], supports=["L4"],
  version="repository main as served 2026-10-22", status="retrieved",
  licence={"name": "MIT", "quote": "Copyright (c) 2024 OpenAI", "quote_file": "gpts_are_gpts/LICENSE", "url": "https://github.com/openai/GPTs-are-GPTs/blob/main/LICENSE"},
  redistribution="yes", redistribution_note="MIT licence on the repository including the CSV; keep the copyright notice.", units="share of tasks exposed (alpha, beta, gamma) by occupation", geography="US occupations (O*NET)", time_span="2023 ratings",
  variables=["dv_rating (GPT-4) and human ratings: alpha=E1, beta=E1+0.5*E2, gamma=E1+E2"], derived=["task_exposure_summary"], notes="Exposure to LLMs, not observed automation.")
S(id="aioe_felten", title="Felten, Raj, Seamans AI Occupational Exposure (AIOE) data appendix", publisher="Felten, Raj and Seamans (AIOE-Data repository)", url="https://github.com/AIOE-Data/AIOE", domains=["D5"], supports=["L4"],
  version="repository as served 2026-10-22 (last push 2024-06-03)", status="retrieved",
  licence={"name": "No licence file in the repository (GitHub API license field is null)", "quote": ""}, redistribution="unclear",
  redistribution_note="Repository has no LICENSE (the raw LICENSE URL returned 404; the API reported no licence). Raw only.", units="AIOE index", geography="US occupations", time_span="2021 method; appendix to 2024", variables=["AIOE by SOC occupation", "language modelling and image generation AIOE"], notes="")
S(id="onet", title="O*NET 31.0 database (Excel files) and licence page", publisher="US Department of Labor, Employment and Training Administration (O*NET)", url="https://www.onetcenter.org/database.html", domains=["D5"], supports=["L4"],
  version="O*NET 31.0", status="retrieved",
  licence={"name": "CC BY 4.0", "quote": "the content of the O*NET 31.0 Database is licensed under a Creative Commons Attribution 4.0 International License", "quote_file": "onet/license_db.html", "url": "https://www.onetcenter.org/license_db.html"},
  redistribution="yes", redistribution_note="CC BY 4.0 with required credit text (USDOL/ETA) and a note when modified. Basis for the task and occupation structure that the exposure datasets map onto.", units="scales 1-100, importance, level", geography="US occupations", time_span="2026 database",
  variables=["occupations, tasks, work activities, skills"], notes="")
S(id="wid", title="World Inequality Database: data page, methodology page and bulk file wid_all_data.zip", publisher="World Inequality Lab", url="https://wid.world/data/", domains=["D5", "D7"], supports=["L4", "L7"],
  version="bulk file as served 2026-10-22", status="retrieved",
  licence={"name": "No licence or terms statement found on the pages read", "quote": ""}, redistribution="unclear",
  redistribution_note="The data page offers 'Download full dataset' without a licence; guessed legal-notice URLs returned 404; the home page says 'Download our open-access datasets'. Open access is not a licence, so redistribution is unclear. Raw only; this is the M5 plan STOP item 1 and is not resolved. See needs-user.",
  units="income and wealth shares, national income, % ", geography="about 200 countries and regions", time_span="1800 to 2024 depending on series", variables=["pre-tax national income shares (top 10%, bottom 50%)", "wealth shares", "factor income shares", "carbon inequality"],
  notes="Download is slow (about 0.5 GB); the file and checksum are listed if complete.")
S(id="oecd_ai", title="OECD Employment Outlook 2023 (AI and jobs) and OECD terms pages (not retrieved)", publisher="OECD", url="https://www.oecd.org/en/publications/oecd-employment-outlook-2023_08785bba-en.html", domains=["D5"], supports=["L4"],
  version="not retrieved", status="blocked", role="document", dirs=["oecd_ai", "oecd_terms"], licence={"name": "Not read (terms page returned HTTP 403)", "quote": ""}, redistribution="unclear",
  redistribution_note="OECD publication and terms pages returned HTTP 403 to automated access; not worked around.", units="n/a", geography="OECD", time_span="n/a", variables=[], notes="See needs-user.")
S(id="census_btos", title="US Census Bureau Business Trends and Outlook Survey: data downloads page (page only)", publisher="US Census Bureau", url="https://www.census.gov/hfp/btos/data_downloads", domains=["D5", "D8"], supports=["AI"],
  version="page as served 2026-10-22", status="partial", role="document", licence={"name": "Not read", "quote": ""}, redistribution="unclear",
  redistribution_note="Only the downloads page was saved (5 KB; no data file). US Government work is normally public domain, but the page statement was not read, so unclear here.", units="n/a", geography="US", time_span="n/a", variables=[], notes="")
