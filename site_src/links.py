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
    {"id": "emissions", "label": "Emissions", "sub": "prescribed in the Explorer", "status": "withheld", "box": [200, 392, 220, 70]},
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
     "failed": ["A1.3 as first written failed (one row for the default composite; the earlier composites on several). As amended by D-064 the default composite meets it. S3 does not reproduce GATE; its level under F3's own investment rule is unvalidated.", "A2.1: FaIR starts about 0.04 to 0.07 K below observed."],
     "notcompared": ["Shares are of S3's own output, whose level is unvalidated.", "High is not the upper end of the literature."],
     "effect": "s3damage", "methods": "methods.html#coupling"},
    {"n": 3, "id": "fair-warming-to-world3-health-yield", "from": "warming", "to": "world3", "status": "withheld",
     "label": "Warming effects on health and yield",
     "what": "Built, outputs withheld. From 2025, World3's land yield can be lowered in proportion to warming above the 2025 level, with a low, central and high loss per degree taken from the crop-yield literature (Zhao and others, 2017). It is off by default and the Explorer does not use it: no scenario on this site changes because of it, and no number from it is shown here. A health effect is built as well: the mortality of all age groups can be scaled with warming, using a published mortality function of global mean temperature (Bressler, 2021). In the model the health effect is small beside the yield effect. Provisional, awaiting the editor's review (D-069).",
     "met": ["All six readings written before the code were met: switch-off invariance, no effect without extra warming, the stated multiplier, sign and order with its control, nothing changes before 2025, and bounds with climate damage on (tests/test_link3_yield.py).", "Health: all six readings written before the code were met (tests/test_links_unlock.py)."],
     "failed": [],
     "notcompared": ["No hindcast: the link is inactive before 2025 by construction.", "Only the abstract of the source paper was read; three other candidate papers were not read.", "CO2 fertilisation, adaptation, breeding, other crops and regional differences are left out. An earlier version of this page called the loss an upper reading; that was wrong: a 2025 study that includes observed adaptation (Hultgren and others) finds losses that are not smaller.", "Health: the source table was read through a parsing tool, not read by eye; age structure and all mortality that is not temperature-related are left out.", "No health or yield effect of warming exists in the Explorer."],
     "effect": None, "methods": "limitations.html"},
    {"n": 4, "id": "s3-output-to-world3", "from": "s3", "to": "world3", "status": "withheld",
     "label": "S3 output feeding World3",
     "what": "Built, outputs withheld. World3's industrial output can be multiplied by S3's uplift (output with AI investment over output without), limited to a yearly growth cap that the person running it must choose. Four caps taken from published estimates of AI's effect on productivity growth are provided (Acemoglu; OECD low and high; Goldman Sachs); they are ten-year estimates, extended here to 2100, which is an extrapolation. It is off by default and the Explorer does not use it: no scenario on this site changes because of it, and no number from it is shown here. S3's economy and World3's are still not reconciled, and the link is one-way. Provisional, awaiting the editor's review (D-069).",
     "met": ["All readings written before the code were met: switch-off invariance, an uplift of 1 changes nothing, the cap is respected, sign and order with its control, and bounds (tests/test_link4_ai_uplift.py)."],
     "failed": ["Not a failed test, but the finding that matters: S3's uplift is unbounded even with the electricity limits on, so the cap binds in every year from 2027, with the published caps as with any other. The result is the cap, not S3. A search found nothing measured that bounds S3's own output."],
     "notcompared": ["No comparison with any measured effect of AI on world output.", "S3's level is unvalidated under F3's own investment rule (A1.3)."],
     "effect": None, "methods": "methods.html#coupling"},
    {"n": 5, "id": "s3-compute-to-data-centre-electricity", "from": "s3", "to": "dc", "status": "built",
     "label": "S3 compute sets data-centre electricity",
     "what": "Built: S3 compute sets data-centre electricity demand, and supply limits compute (and, optionally and off by default, the electricity left for other users limits World3 industrial output, D-059). The compute and electricity outputs stay withheld in the Explorer because they leave any plausible range, which is a property of S3's compute path, not a finding about the world.",
     "met": ["The loop signs were tested before the results (tests/test_m2_slice.py)."],
     "failed": ["B1 sign: failed as written (a lower supply case had up to 17.8% more compute in 2038-2045).", "A2.6 step test failed (largest difference 0.565%, in data-centre electricity).", "A1.3: S3 levels unvalidated."],
     "notcompared": ["No independent test of modelled data-centre electricity against estimates exists before 2025.", "Compute and electricity values are withheld: under F3's own investment rule they leave any plausible range (D-066 approved, not built)."],
     "effect": None, "methods": "limitations.html#status-ai"},
    {"n": 6, "id": "data-centre-electricity-to-emissions", "from": "dc", "to": "emissions", "status": "withheld",
     "label": "Data-centre electricity feeding emissions",
     "what": "Built, outputs withheld. The electricity used by data centres above its 2025 level can be turned into extra fossil CO2 with the carbon intensity of the Earth4All reference path, and added to the emissions FaIR reads. It is off by default and the Explorer does not use it: no scenario on this site changes because of it, and no number from it is shown here. In the Explorer, emissions stay prescribed and the climate path is the same for every scenario. One-way. Provisional, awaiting the editor's review (D-069).",
     "met": ["All eight readings written before the code were met (tests/test_link6_dc_emissions.py).", "Against the IEA (Energy and AI, 2025): electricity in 2030 within 10%.", "With a build rate that follows the IEA Base Case (post-hoc: a calibration, not a validation), electricity in 2030 and 2035 is within 10% and CO2 in 2035 within 30%."],
     "failed": ["Against the IEA with a constant build rate of 15% a year: FAILED in 2035 (electricity 55% above, CO2 112% above). The failures stand; tolerances were not changed."],
     "notcompared": ["It is an upper reading: the 2025 level of data-centre electricity is held constant as the baseline, and the electricity itself comes from S3's unvalidated compute path, bounded only by an assumed build rate.", "Nothing after 2035: the IEA gives no later figure, and the last growth rate is simply kept."],
     "effect": None, "methods": "methods.html#coupling"},
    {"n": 7, "id": "world3-to-emissions", "from": "world3", "to": "emissions", "status": "withheld",
     "label": "World3 feeding emissions",
     "what": "Built, outputs withheld. Fossil CO2 from 2026 can be computed from World3's industrial output and a carbon intensity fitted to 1970 to 2024, replacing the prescribed path that FaIR reads. It is off by default and the Explorer does not use it: no scenario on this site changes because of it, and no number from it is shown here. There are two constructions. The first failed its hindcast. The second is a post-hoc proposal, labelled as such: it picks the World3 run closest to observed world output as reference and joins other runs to the 2025 value with one constant. One-way. Provisional, awaiting the editor's review (D-069).",
     "met": ["First construction: six of seven readings met.", "Second construction (post-hoc): hindcast met on the reference run, largest error 9.4% against a 10% tolerance set beforehand; switch-off invariance and bounds met (tests/test_link7_variant_b.py)."],
     "failed": ["First construction: the hindcast FAILED (14 of 55 years outside 10%, largest 27.2% in 2024). The failure stands; the tolerance was not changed.", "Second construction: the step at the join failed for four of six runs (6.2% to 7.3% against 5%), because World3's industrial output is already falling in 2025 in those runs.", "A published recalibration of World3 (Nebel and others, 2023) was tried as reference run, from a partial and unverified copy of its parameters: FAILED all three readings and is not used."],
     "notcompared": ["Everything after 2025: lower emissions in these runs follow from World3's decline in industrial output, which is not a finding about the world.", "The reference run was chosen from six lever settings, not from all 27."],
     "effect": None, "methods": "methods.html#coupling"},
]

STATUS_TEXT = {"built": "Built and tested", "not-built": "Not built", "withheld": "Built, outputs withheld"}   # withheld: tested, off by default, nothing shown on the site
LINE_STYLE = {"built": "solid", "not-built": "dashed", "withheld": "dotted"}


def links_json() -> str:
    return json.dumps({"nodes": NODES, "links": LINKS}, separators=(",", ":"))
