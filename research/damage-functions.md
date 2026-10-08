# F3 — Damage-function sources for D-007 (M0 research note)

**Status:** research note for decision D-007 (Climate damage function), written in M0 of `docs/phase-2-plan.md` on 2026-10-08. It collects candidate sources for the **low, central and high** options D-007 proposes. **It chooses nothing**; D-007 is decided by the editor-in-chief before the damage part of M2.

**How the sources were read.** Publisher pages (PNAS, Nature, Springer, Science) refused automated access or returned a login redirect. What was read, and where: the **abstracts**, from Europe PMC's metadata service (europepmc.org REST API, queried by DOI on 2026-10-08), which returns the abstract text, journal reference and publication-type flags. **No full text was read** and no damage-function coefficient was taken from a primary document. Every coefficient or percentage below that is not in an abstract is marked *unverified* and comes from search-result summaries, which are secondary. Do not use an unverified number in the model; read the paper first.

## 1. Sources whose abstracts were read

| Source | What the abstract says (short quotes) | What it is | Use |
|---|---|---|---|
| Nordhaus (2017), *Revisiting the social cost of carbon*, PNAS 114, 1518–1523, DOI 10.1073/pnas.1609244114 | Updated estimates from "a revised DICE model"; "the SCC is $31 per ton of CO2 in 2010 US$ for the current period (2015)" | The DICE-2016R damage function. **The abstract states no damage-function coefficient.** | Low candidate (see section 2: its damage coefficient is *unverified*) |
| Barrage and Nordhaus (2024), *Policies, projections, and the social cost of carbon: Results from the DICE-2023 model*, PNAS 121, e2312030121, DOI 10.1073/pnas.2312030121 (open access, CC BY) | "major changes in the treatment of risk, the carbon and climate modules ... as well as updates on all the major components"; "a major increase in the estimated social cost of carbon" | The updated DICE. **The abstract does not give the damage function**; the NBER working-paper page (version 31112) was also read and says nothing about it either | Low-to-central candidate; the damage coefficient is *unverified* |
| Hsiang et al. (2017), *Estimating economic damage from climate change in the United States*, Science 356, 1362–1369, DOI 10.1126/science.aal4369 | Damage "increases quadratically in global mean temperature, costing roughly 1.2% of gross domestic product per +1°C on average" (United States only) | Bottom-up, empirical, US. **Not a global damage function** | Evidence on the *form* (quadratic) and the order of magnitude per degree for one economy; not usable as the global function |
| Burke, Hsiang and Miguel (2015), *Global non-linear effect of temperature on economic production*, Nature 527, 235–239, DOI 10.1038/nature15725 | Productivity "peaking at an annual average temperature of 13 °C and declining strongly at higher temperatures"; "unmitigated warming is expected to reshape the global economy by reducing average global incomes roughly 23% by 2100 and widening global income inequality, relative to scenarios without climate change" | Panel regression of growth on temperature; the damage persists (a growth effect). The abstract's 23% is for 2100 under unmitigated warming "if future adaptation mimics past adaptation" | High candidate (a growth-effect function). The paper's own scenario and the function needed to apply it to an arbitrary temperature path were not read |

## 2. A source that has been retracted

| Source | Status | Consequence |
|---|---|---|
| Kotz, Levermann and Wenz (2024), *The economic commitment of climate change*, Nature 628, 551–557, DOI 10.1038/s41586-024-07219-0 | **Retracted.** Europe PMC lists the publication types as "Retracted Publication"; a web search found a Nature retraction note dated December 2025 and an earlier correction in June 2024. The abstract's headline ("an income reduction of 19% within the next 26 years independent of future emission choices") is therefore not a reliable result. **The reasons for the retraction were not found.** | **Do not use as a source for any option.** Cited here only so that nobody adopts it by accident. Any later work building on its numbers is also in doubt |

## 3. Sources found only through secondary summaries (all *unverified*)

A search summary (a secondary source, not read at the primary documents) attributed these figures, which must be checked against the papers before any use:

- **Howard and Sterner (2017)**, *Few and Not So Far Between: A Meta-analysis of Climate Damage Estimates*, Environmental and Resource Economics 68(1) (DOI 10.1007/s10640-017-0166-z). Europe PMC has no record of it; the Springer page redirected to a login. Reported (unverified): damage at 3 °C of about 1.9% to 6.7% of global GDP across the meta-regression variants of that and neighbouring work; a quadratic form with a coefficient on T² of about 0.0074 when productivity studies are excluded, "about twice" the DICE value. Reported (unverified): a 2025 update with non-catastrophic damage at 3 °C of 3.2% to 9.2%, depending on whether growth effects are included.
- **Nordhaus DICE damage coefficient**: reported (unverified) as about 0.236% of output times T², giving about 2.1% at 3 °C; reported (unverified) that DICE-2023's non-catastrophic damage at 3 °C is about 1.5% to 2% and 3.1% after an adjustment for tipping points and omitted impacts.
- **Weitzman (2012)**, a polynomial or exponential form that gives much higher damages at high warming than a quadratic form: the form was described in a search summary; no figure at any temperature was verified.
- **En-ROADS technical reference** (Climate Interactive), which digitised Burke et al. and fitted a cubic: reported (unverified) as the source of a cubic fit, and as listing Howard and Sterner's preferred form as 1.145 times T² (units unclear). Not read.

## 4. What this suggests for D-007, without choosing

- The three **kinds** of function in the literature are: (a) a **level-effect quadratic** (DICE and the Howard-Sterner meta-regression: output is lowered by a share that grows with the square of warming); (b) a **steeper form** at high warming (Weitzman); (c) a **growth-effect** function (Burke et al.: warming lowers the growth rate, so losses compound). A low, central and high set could be built from one of each, but **which source supplies which option, and the coefficients, is not established by anything verified here**.
- The **effect-size ordering the abstracts support**: DICE-style level effects are the lowest, the Howard-Sterner meta-regression is higher (unverified numbers), Burke et al. is highest (23% by 2100 under unmitigated warming, verified in the abstract). That ordering follows from the abstracts only for Burke et al.; the other two numbers are unverified.
- **Scope.** All of these apply damages to **output**. F3's reused Earth4All sectors have their own warming effects on productivity and capital (the seven warming channels, `MODEL_SPEC.md` section 4); D-007 must say whether the damage function **replaces** those channels or **adds** to them. Applying both would count the same damage twice.
- **What was not found:** a damage function calibrated to F3's other drivers; the damage at a given temperature for any option, from a primary document; and the reasons for the Kotz et al. retraction.

## 5. What is needed before D-007 can be decided

1. The full text, or at least the damage-function section, of Nordhaus (2017) or Barrage and Nordhaus (2024), Howard and Sterner (2017), and Burke et al. (2015), read from the publisher or an author's copy (the automated route is blocked). The editor-in-chief may be able to open these.
2. A decision on whether the damage function replaces or adds to Earth4All's warming channels (above).
3. A decision whether a growth-effect option is acceptable in a model whose economy sector (Earth4All's) has its own growth structure.
