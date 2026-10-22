"""Register metadata, part 5: further published papers saved as documents. S, CROSS_CHECKS, NEEDS_USER are injected."""


def paper(id, title, publisher, url, version, licence, quote, quote_file, redistribution, note, supports, domains, status="retrieved"):
    S(id=id, title=title, publisher=publisher, url=url, domains=list(domains), supports=supports, version=version, status=status, role="document",
      licence={"name": licence, "quote": quote, **({"quote_file": quote_file, "url": url} if quote else {})}, redistribution=redistribution, redistribution_note=note,
      units="n/a (published parameters and results)", geography="as in the paper", time_span="as in the paper", variables=["published results used for functional forms and parameter values"], notes="")


NBER = "All rights reserved. Short sections of text, not to exceed two"
NBER_NOTE = "NBER working paper with the standard notice: short sections of text may be quoted with credit. Parameters and results are cited with page references only; nothing is republished."

paper("papers_acemoglu2024", "Acemoglu (2024), The Simple Macroeconomics of AI, NBER w32487", "NBER", "https://www.nber.org/papers/w32487", "NBER working paper, 2024",
      "Copyright reserved by the author (NBER notice)", NBER, "papers_acemoglu2024/acemoglu2024_simple_macro_ai_nber_w32487.pdf", "no", NBER_NOTE, ["L4", "AI"], ["D5"])
paper("papers_acemoglu_restrepo2016", "Acemoglu and Restrepo (2016), The Race between Man and Machine, NBER w22252", "NBER", "https://www.nber.org/papers/w22252", "NBER working paper, 2016",
      "Copyright reserved by the authors (NBER notice)", NBER, "papers_acemoglu_restrepo2016/acemoglu_restrepo2016_race_nber_w22252.pdf", "no", NBER_NOTE, ["L4"], ["D5"])
paper("papers_karabarbounis_neiman2013", "Karabarbounis and Neiman (2013), The Global Decline of the Labor Share, NBER w19136", "NBER", "https://www.nber.org/papers/w19136", "NBER working paper, 2013",
      "Copyright reserved by the authors (NBER notice)", NBER, "papers_karabarbounis_neiman2013/karabarbounis_neiman2013_nber_w19136.pdf", "no", NBER_NOTE, ["L4"], ["D5"])
paper("papers_brynjolfsson2025", "Brynjolfsson, Chandar and Chen (2025), Canaries in the Coal Mine? Six Facts about the Recent Employment Effects of Artificial Intelligence", "Stanford Digital Economy Lab",
      "https://digitaleconomy.stanford.edu/", "working paper, 2025", "No licence stated in the PDF", "", "", "unclear", "No licence statement in the document read; cited with page references only.", ["L4", "AI"], ["D5"])
paper("papers_eloundou2023", "Eloundou, Manning, Mishkin and Rock (2023), GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models, arXiv:2303.10130", "arXiv", "https://arxiv.org/abs/2303.10130",
      "arXiv version retrieved 2026-10-22", "No licence stated in the PDF (arXiv default distribution licence)", "", "", "unclear", "The PDF carries no licence line; cited with page references only. The occupation data are separate (gpts_are_gpts, MIT).", ["L4", "AI"], ["D5"])
paper("papers_epoch_gate", "Erdil et al. (2025), GATE: An Integrated Assessment Model for AI Automation, arXiv:2503.04941", "arXiv / Epoch AI", "https://arxiv.org/abs/2503.04941", "arXiv version retrieved 2026-10-22",
      "No licence stated in the PDF", "", "", "unclear", "The model description S3 is built from; kept as a document for page references (D-001 treats re-implementation from the paper as the only route).", ["AI", "DC", "L5"], ["D1"])
paper("papers_li2023_thirsty", "Li, Yang, Islam and Ren (2023), Making AI Less 'Thirsty', arXiv:2304.03271", "arXiv", "https://arxiv.org/abs/2304.03271", "arXiv version retrieved 2026-10-22",
      "No licence stated in the PDF", "", "", "unclear", "Water-footprint method for AI training and inference (direct and indirect, WUE and PUE). Cited with page references only.", ["DC", "M5"], ["D2"])
paper("papers_luccioni2022", "Luccioni, Viguier and Ligozat (2022), Estimating the Carbon Footprint of BLOOM, arXiv:2211.02001", "arXiv", "https://arxiv.org/abs/2211.02001", "arXiv version retrieved 2026-10-22",
      "No licence stated in the PDF", "", "", "unclear", "Energy and emissions of one large training run; cited with page references only.", ["DC", "L5", "L6"], ["D2"])
paper("papers_hoesly2018_ceds", "Hoesly et al. (2018), Historical (1750-2014) anthropogenic emissions of reactive gases and aerosols from the Community Emissions Data System (CEDS), Geosci. Model Dev. 11:369-408", "Copernicus (open access)",
      "https://doi.org/10.5194/gmd-11-369-2018", "published 2018", "CC BY 3.0 (as printed)", "Creative Commons Attribution 3.0 License", "papers_hoesly2018_ceds/hoesly2018_ceds_gmd.pdf", "yes",
      "Open access, CC BY 3.0; the method paper for the CEDS historical series. Used here as a document only.", ["L6", "L7"], ["D3"])
paper("papers_leach2021_fair", "Leach et al. (2021), FaIRv2.0.0: a generalized impulse response model for climate uncertainty and future scenario exploration, Geosci. Model Dev. 14:3007-3036", "Copernicus (open access)",
      "https://doi.org/10.5194/gmd-14-3007-2021", "published 2021", "CC BY 4.0 (as printed)", "Creative Commons Attribution 4.0 License", "papers_leach2021_fair/leach2021_fair_gmd.pdf", "yes",
      "Open access, CC BY 4.0; the method paper for FaIR v2.", ["L6", "L7"], ["D3"])
paper("papers_nicholls_rcmip", "Nicholls et al. (2020), Reduced Complexity Model Intercomparison Project Phase 1 (RCMIP), Geosci. Model Dev. 13:3571-3605", "Copernicus (open access)",
      "https://doi.org/10.5194/gmd-13-3571-2020", "published 2020", "CC BY 4.0 (as printed); the RCMIP data are stated as CC BY-SA 4.0 in the text", "Creative Commons Attribution 4.0 License", "papers_nicholls_rcmip/nicholls2020_rcmip_gmd.pdf", "yes",
      "The paper is CC BY 4.0. The text states 'The license for all data is Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)' for the RCMIP data. This is relevant to the emissions inputs of FaIR if they derive from RCMIP.", ["L6", "L7"], ["D3"])
