"""The seven links of the connections map (D-056), one definition used by the story strip (chapter 4) and the connections page.

Status vocabulary (D-052, unchanged): built = solid, not built = dashed, built but outputs withheld = dotted. A link is "built" only if the coupling exists and is tested
today. The ids and numbers match the v0.1 feedback-loop diagram (site_src/ig.py). Text here states records, not model numbers: every number shown for a link is computed
by the page script from site/data/explorer.json (key "effect").
"""
from __future__ import annotations

import json

# Geometry for the map: a 700 x 480 box; nodes are boxes (x, y, w, h), links are quadratic curves (start, control, end). Layout only, no model numbers.
MAP_W, MAP_H = 700, 480
NODES = [
    {"id": "warming", "label": "Warming", "sub": "FaIR climate model", "status": "built", "box": [265, 10, 170, 64]},
    {"id": "world3", "label": "World3", "sub": "population, food, industry", "status": "built", "box": [10, 190, 180, 78]},
    {"id": "s3", "label": "AI economy S3", "sub": "levels unvalidated", "status": "built", "box": [510, 190, 180, 78]},
    {"id": "dc", "label": "Data centres", "sub": "output withheld", "status": "built", "box": [510, 360, 180, 78]},
    {"id": "emissions", "label": "Emissions", "sub": "prescribed, not built", "status": "not-built", "box": [200, 392, 220, 70]},
]
CURVES = {
    1: [[300, 76], [170, 100], [100, 188]],
    2: [[400, 76], [530, 100], [580, 188]],
    3: [[322, 76], [250, 140], [150, 188]],
    4: [[508, 229], [350, 229], [194, 229]],
    5: [[600, 270], [600, 315], [600, 358]],
    6: [[508, 410], [470, 424], [424, 427]],
    7: [[100, 270], [110, 400], [198, 427]],
}


LINKS = [
    {"n": 1, "id": "fair-warming-to-world3-output", "from": "warming", "to": "world3", "status": "built",
     "label": "Warming lowers World3 industrial output",
     "what": "Climate damage multiplies World3's whole industrial output by (1 minus c x T squared) from 2025, with T the recorded FaIR ensemble-mean warming and c one of the three D-007 coefficients. A level-of-output effect, off by default. The change flows through investment, agriculture, resources and population.",
     "met": ["Switching damage off returns the stand-alone World3 to 1e-9 (M6 test).", "Zero warming equals the baseline (M6 test).", "More warming lowers industrial output, with a control that fails (M6 test).", "Nothing is NaN or negative over the whole 108-run grid (M6 test)."],
     "failed": ["A2.1: FaIR starts about 0.04 to 0.07 K below observed for the current decade (the warming that drives this link)."],
     "notcompared": ["Damage-on runs are not compared with WorldDynamics.jl, which has no climate damage.", "High is not the upper end of the literature: growth-effect estimates are larger and are not represented.", "S3's economy and World3's are not reconciled."],
     "effect": "w3damage", "methods": "methods.html#coupling"},
    {"n": 2, "id": "fair-warming-to-s3-damage", "from": "warming", "to": "s3", "status": "built",
     "label": "Warming lowers S3 output",
     "what": "The same damage function takes a share of S3's own output, with the recorded FaIR ensemble-mean warming and one of the three D-007 options.",
     "met": ["B2 sign: more damage, lower output (the sign test passed)."],
     "failed": ["A1.3: S3 does not reproduce GATE after about 2027; its output level is unvalidated.", "A2.1: FaIR starts about 0.04 to 0.07 K below observed."],
     "notcompared": ["Shares are of S3's own output, whose level is unvalidated.", "High is not the upper end of the literature."],
     "effect": "s3damage", "methods": "methods.html#coupling"},
    {"n": 3, "id": "fair-warming-to-world3-health-yield", "from": "warming", "to": "world3", "status": "not-built",
     "label": "Warming effects on health and yield",
     "what": "Not built. World3's population and food sectors have no warming term, so warming does not reach them except through industrial output (link 1). The Earth4All channels (life expectancy, land yield, CO2 effect on yield, CO2 lifetime) were left out by decision D-049, to be revisited.",
     "met": [], "failed": [], "notcompared": ["No health or yield effect of warming exists in the Explorer."], "effect": None, "methods": "limitations.html"},
    {"n": 4, "id": "s3-output-to-world3", "from": "s3", "to": "world3", "status": "not-built",
     "label": "S3 output feeding World3",
     "what": "Not built. S3's economy and World3's are two models of the same world and are not reconciled; nothing in the AI-race run changes anything in World3.",
     "met": [], "failed": [], "notcompared": ["No test: there is no link."], "effect": None, "methods": "methods.html#coupling"},
    {"n": 5, "id": "s3-compute-to-data-centre-electricity", "from": "s3", "to": "dc", "status": "built",
     "label": "S3 compute sets data-centre electricity",
     "what": "Built: S3 compute sets data-centre electricity demand, and supply limits compute (and, optionally and off by default, the electricity left for other users limits World3 industrial output, D-059). The compute and electricity outputs stay withheld in the Explorer because they leave any plausible range, which is a property of S3's compute path, not a finding about the world.",
     "met": ["The loop signs were tested before the results (tests/test_m2_slice.py)."],
     "failed": ["B1 sign: failed as written (a lower supply case had up to 17.8% more compute in 2038-2045).", "A2.6 step test failed (largest difference 0.565%, in data-centre electricity).", "A1.3: S3 levels unvalidated."],
     "notcompared": ["No independent test of modelled data-centre electricity against estimates exists before 2025.", "Compute and electricity values are withheld until the S3 compute path is validated (awaiting Epoch AI)."],
     "effect": None, "methods": "limitations.html#status-ai"},
    {"n": 6, "id": "data-centre-electricity-to-emissions", "from": "dc", "to": "emissions", "status": "not-built",
     "label": "Data-centre electricity feeding emissions",
     "what": "Not built. Emissions are prescribed, so the climate path is the same for every scenario in the Explorer.",
     "met": [], "failed": [], "notcompared": ["No test: there is no link."], "effect": None, "methods": "methods.html#coupling"},
    {"n": 7, "id": "world3-to-emissions", "from": "world3", "to": "emissions", "status": "not-built",
     "label": "World3 feeding emissions",
     "what": "Not built. World3 does not change emissions; the FaIR run replays one recorded path (D-021).",
     "met": [], "failed": [], "notcompared": ["No test: there is no link."], "effect": None, "methods": "methods.html#coupling"},
]

STATUS_TEXT = {"built": "Built and tested", "not-built": "Not built", "withheld": "Built, outputs withheld"}
LINE_STYLE = {"built": "solid", "not-built": "dashed", "withheld": "dotted"}


def links_json() -> str:
    return json.dumps({"nodes": NODES, "links": LINKS}, separators=(",", ":"))
