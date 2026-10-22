"""Shared definitions (tooltip terms and the public-draft sentence) from the v0.1 Explorer page (D-052). The v0.1 page body was retired in D-056 stage 3; its caveat blocks live on in dash_blocks.py."""
import ig

PUBLIC = "Public draft, published 2026-10-21. Conditional scenarios, not forecasts."


def tip(term, text):
    return f'<abbr title="{text}">{term}</abbr>'


S3, R3 = (tip("S3", "S3 is this project's AI-economy model: a re-implementation of the GATE equations for output, automation and compute, driven by a scenario investment rule. Its levels are unvalidated."),
          tip("R3", "R3 is the scenario-lever rule that sets how much S3 invests in compute, hardware research and software research. It is a lever, not a replica of GATE."))
FAIR = tip("FaIR", "FaIR is the open climate model used here, with the published 841-member calibrated ensemble. Emissions are prescribed, so every scenario has the same climate.")
GATE = tip("GATE", "GATE is Epoch AI's model of the economy under AI automation. F3 re-implemented its equations from the paper; the re-implementation does not reproduce GATE after about 2027.")
W3 = tip("World3", "World3 is the system-dynamics model behind The Limits to Growth: population, food, industry, resources and pollution, 1900 to 2100.")
