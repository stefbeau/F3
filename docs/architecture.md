# F3 architecture: links between sectors

**Status of this page:** a list of proposed links from the D-060 gap analysis, written before any code or test. Nothing here is implemented, tested or approved. Only the editor approves decisions (CLAUDE.md); this page records proposals for his review.

## Existing links
The links already built, and the campaign's own numbering L3 to L7, DC and M5 used for data planning, are described in `docs/coupling-interface.md`, `docs/m6-minimal-plan.md` and `docs/links/` (`L3.md` to `L7.md`, `DC.md`). The campaign numbering is **not** the numbering of the seven links on the Explorer connections page (`site_src/links.py`); the two schemes have not been reconciled. The electricity link from the data-centre module into World3 is D-059 in `DECISIONS.md` (merged).

## Proposed new links (D-060 gap analysis)
Each is **proposed, not yet implemented**. The one-line rationale says why the link might matter, not that it has been shown to.

| Code | Name | Proposed link | Status | Rationale |
|---|---|---|---|---|
| L8 | Disaster-economy | extreme weather event damage to GDP and food loss | proposed, not yet implemented | Warming changes the frequency and cost of disasters, a loss channel that the smooth damage function (D-007) does not represent. |
| L9 | Climate-migration-labour | displacement to labour supply and skill mix | proposed, not yet implemented | Displacement from climate and conflict shifts who is in the labour force, which S3's labour input currently takes as given. |
| L_BIO | Ecosystem services | biodiversity, soil and ocean condition to food, water and carbon | proposed, not yet implemented | Food, water and carbon sinks depend on ecosystem condition, which no current sector models. |
| L_OCN | Marine food | ocean acidification and warming to fishery output | proposed, not yet implemented | Fisheries are a food source outside the land-yield link (L3) and are affected by ocean chemistry and temperature. |
| L_PAN | Pandemic | climate-driven range expansion of disease vectors to health burden | proposed, not yet implemented | Changing vector ranges could change the health burden in ways the heat-mortality channel alone does not capture. |
| L_MH | Mental health | AI displacement and climate stress to productivity | proposed, not yet implemented | Mental-health burden is a candidate path from labour disruption and climate stress back to output. |
| L_CONF | Conflict | resource and climate stress to armed conflict to the economy | proposed, not yet implemented | Armed conflict is a large economic and displacement driver and a possible consequence of resource stress. |
| L_FIN | Financial stability | AI shock and debt to systemic financial risk | proposed, not yet implemented | A fast AI-driven shock could propagate through leverage, a channel absent from the real-economy sectors. |
| L_SOC | Governance and cohesion | disinformation and inequality to policy capacity | proposed, not yet implemented | Policy response depends on social cohesion and state capacity, which F3 treats as exogenous (levers). |
| L_RISK | AI safety | incident rate and capability to catastrophic risk probability | proposed, not yet implemented | The scope includes AI's own risks, which no sector currently carries; any probability would be a labelled judgement, not a measurement. |

## Notes
- **Data.** Candidate sources for these links are registered in `audit/data/sources-register.json` under campaign wave "D-060 P1 gap" and "D-060 P2 gap". Their licences are mostly unread or unconfirmed; see each entry. Obtaining a source is not a decision to use it.
- **Schema.** The register schema's `supports` enum covers only L3 to L7, DC, AI and M5. For the new codes the register keeps the valid codes in `supports` and the full proposed list in `supports_proposed`, so the schema was not changed.
- **No labels removed.** None of this changes D-029, D-030 or any validation label.
