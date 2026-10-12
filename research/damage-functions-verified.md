# F3: damage-function sources, read and verified (M2, for D-007)

**Status:** written 2026-10-12. Supersedes nothing: the earlier note `research/damage-functions.md` is left unedited (one dated pointer line added there). **It chooses nothing**; D-007 is the editor's. Every number is marked **[read]** (seen in the document text, with where) or **[derived]** (computed here from [read] numbers, arithmetic shown) or **[unverified]** (not seen in a document). Nothing marked [unverified] is used in the options of D-007.

**How read.** Documents were fetched by a delegated reading agent and the key passages **re-checked by me against the saved text** (the agent's report is its claim, not evidence). Local copies are held **outside the repository** (`C:\Users\sbeau\dev\_damage_sources\`, never committed) with the sha256 below. All routes were open access; no paywall was circumvented. **Kotz et al. (2024) is not used (retracted).**

| Source | Route | Local copy (sha256, first 16 hex) |
|---|---|---|
| Barrage and Nordhaus (2024), PNAS 121(13), e2312030121, doi 10.1073/pnas.2312030121 (CC BY) | Europe PMC XML of PMC10990119, main text only | `barrage2024_PMC10990119.xml` `8faa5b9610257ab7` |
| Nordhaus (2017), PNAS 114(7), 1518-1523, doi 10.1073/pnas.1609244114 (open access) | PMC5321009 HTML, main text only | `nordhaus2017_PMC5321009.html` `7a07d0fd58d8ee41` |
| Howard and Sterner (2017), Environ. Resour. Econ. 68, 197-225, doi 10.1007/s10640-017-0166-z (CC BY 4.0 per the agent; not re-checked by me) | Springer open-access PDF, full text; online appendix not obtained | `howard2017_springer.pdf` `748f12f1eb8418c1` |
| Burke, Hsiang and Miguel (2015), Nature 527, 235-239, doi 10.1038/nature15725 | author copy (Miguel's Berkeley site): letter and Extended Data; Supplementary Information not obtained | `burke2015_miguel_site.pdf` `dbaaa1e8a8a02d51` |
| Newell, Prest and Sexton (2021), JEEM 108, doi 10.1016/j.jeem.2021.102445 (as RFF WP 18-17) | RFF working paper; abstract, introduction, conclusion only | `newell_rff_WP18-17.pdf` `07eaeb68983c8d50` |
| Barker (2024), Econ Journal Watch (context) | first pages only; its simulations not read | `barker2024_econjwatch.pdf` `a3e894dfafe7a4b0` |

**Blocked or not obtained (not filled from memory):** Hsiang et al. (2017, Science 356): science.org returned 403 and Europe PMC marks it not open access, so **nothing of it was read**. The SI of Barrage and Nordhaus (pnas.org 403; the PMC SI link returned an HTML page). The DICE-2013R manual. The Howard and Sterner online appendix. Burke et al.'s SI and Fig. 5d values. Kalkuhl and Wenz (2020) was not attempted.

## 1. Barrage and Nordhaus (2024), DICE-2023

- **Equation [read]:** Eq. 3, `Omega(t) = psi1 T_AT(t) + psi2 [T_AT(t)]^2`; Eq. 2 applies `Omega` as a fraction of gross output (damages scale with output).
- **Temperature [read]:** "quadratic function of global temperature increase since preindustrial times (1765)", global mean surface temperature.
- **Printed anchors [read]:** "damages are estimated to be 3.1% of output at 3 °C warming and 7.0% of output at 4.5 °C warming". Three components, each quadratic and proportional to output: literature synthesis 1.6% at 3 °C (up from 1.2% in DICE-2016), tipping points 1.0% at 3 °C, judgemental adjustment for omitted impacts 0.5% at 3 °C. "calibrated for damage estimates with temperature increases up to 4 °C and is not well-suited for temperature increases above that range".
- **Coefficients psi1, psi2: [unverified]** (they are in the SI, not obtained). **Derived from the two printed anchors** with `psi1 = 0`: 3.1/9 = 0.344% per °C²; check 0.344 x 4.5² = 6.97% [derived], which matches the printed 7.0%. So the printed anchors are consistent with a pure quadratic, but the pure-quadratic form itself is [derived].
- **Damage, % of output (level effect) [derived from the pure quadratic fitted to the [read] anchors]:** 1.5 °C 0.77; 2 °C 1.38; 3 °C **3.1 [read]**; 4 °C 5.5.
- **Alternative damage function [read]:** DICE-2023 itself runs "an alternative damage function based on Howard and Sterner ... a reasonable middle ground of their preferred estimates is a 9% damage/output ratio at a 3 °C increase ... 3 times larger than the one used in the current DICE model".

## 2. Nordhaus (2017), DICE-2016R

- **Equation [read]:** `Omega = D/(1+D)`, `D = phi1 T_AT + phi2 T_AT^2`. The text: "an equation with a parameter of -0.236% loss in global income per degree Celsius squared; this leads to a damage of 2.1% of income at 3 °C, and 8.5% of global income at a global temperature rise of 6 °C"; "A specification with both linear and quadratic terms was extremely unstable and was rejected" (so the linear term is zero [read]); the DICE-2013R parameter was -0.267% [read]; the uncertainty analysis uses mean 0.236 and SD 0.118 (% per °C²) [read, as quoted by the fetch tool].
- **Temperature:** `T_AT` is "the global mean surface temperature" [read]; **the reference year is not stated** in the main text (a statement that the baseline is pre-industrial was not found in this document) [unverified].
- **Damage, % of income (level effect):** 0.236 x T²: 1.5 °C 0.53; 2 °C 0.94; 3 °C **2.1 [read]** (0.236 x 9 = 2.12); 4 °C 3.8 [derived]; 6 °C 8.5 [read] (0.236 x 36 = 8.50). With `D/(1+D)` the figures are marginally smaller (4 °C: 3.64).

## 3. Howard and Sterner (2017)

- **Specification [read]:** the preferred regression is **regression (4) in Table 2** (excluding duplicate estimates, with the above-4 °C estimates dropped as the paper's "Replacing the DICE-2013R damage function with our preferred estimate" refers to). Coefficient on `t2` **0.595** (standard error 0.190), a `cat_t2` coefficient **0.260** (SE 0.267), `mkt_t2` -0.622, `prod_t2` 0.398 (unit: % of GDP per °C², the dependent variable being damage as % of GDP). Table text read from the saved PDF (the column assignment of 0.595 to specifications (3) and (4) is as the text extraction prints it).
- **Method [read]:** "we multiply the coefficients of the preferred regression specification corresponding to non-catastrophic impacts (t2 and prod_t2) by 25% when constructing the damage functions" (Nordhaus's adjustment for omitted non-catastrophic impacts).
- **Temperature [read]:** "global average mean surface temperature increase in degrees Celsius relative to the pre-industrial or current time", with each study's reference period adjusted to pre-industrial.
- **Damage, % of GDP (level effect), [derived] from the printed coefficients:** non-catastrophic only, `0.595 x 1.25 x T²`: 1.5 °C 1.67; 2 °C 2.97; 3 °C 6.69; 4 °C 11.90. Adding the catastrophic term `0.260 T²` (my sum; the paper prints no such table): 2 °C 4.01; 3 °C 9.03; 4 °C 16.06. The 3 °C figure 9.03 equals the "9% damage/output at 3 °C" that Barrage and Nordhaus attribute to Howard and Sterner [read in B&N], which is evidence that B&N used the catastrophic-included version. The exact Howard and Sterner figure at 3 °C was not seen as a printed number in the text I re-checked [unverified as printed].
- **Not obtained:** the online appendix.

## 4. Burke, Hsiang and Miguel (2015)

- **What it is [read]:** a **growth-rate** response: temperature affects the growth of GDP per capita, with a smooth, non-linear, concave response and a maximum at about 13 °C ("with a maximum at 13 °C", main text). It uses **each country's own annual mean temperature**, not a global anomaly.
- **Headline [read]:** "unmitigated warming is expected to reshape the global economy by reducing average global incomes roughly 23% by 2100 ... relative to scenarios without climate change"; "expected global losses are approximately linear in global mean temperature". Extended Data Table 3 (projections under four response functions and three scenarios) exists, but its numbers are in an image in the PDF I have and were **not read**; the agent's quoted -36% and -74% figures are [unverified].
- **Coefficients:** the agent reported Extended Data Table 1 column 1 as Temp 0.0127 (SE 0.0038), Temp² -0.0005 (SE 0.0001), optimum 13.06 °C. **These sit in an image in the PDF and I could not confirm them from the text layer; they are [unverified]**, though the "13 °C" optimum is [read] in the main text.
- **Damage at 1.5, 2, 3, 4 °C of global mean warming: [unverified].** The paper gives global damage against temperature only in Fig. 5d (described as approximately linear); no number at these temperatures is printed in the text. A growth-rate effect also compounds over time, so there is no horizon-free "damage at 3 °C"; the quoted -23% is a 2100 result under RCP8.5.

## 5. Robustness of the Burke specification (context, partly read)

- **Newell, Prest and Sexton [read, abstract and conclusions only, as reported by the agent and not re-checked by me]:** across 800 model variants, growth models give a 95% confidence interval for GDP impacts in 2100 of -84% to +359%; levels models give a much narrower -8.5% to +1.8%, centred on losses of 1% to 3%; no statistically significant temperature effect on growth. Reading consequence: the growth-versus-level question moves the result by orders of magnitude and the data cannot settle it.
- **Barker (2024):** only its first pages were read; it argues the Burke results may be an artefact; its simulations were not read. **Not used as evidence.**

## 6. Summary of what is verified, by source and temperature (% of output)

| source | form | 1.5 °C | 2 °C | 3 °C | 4 °C | verified status |
|---|---|---|---|---|---|---|
| Nordhaus 2017 (DICE-2016R) | level, pure quadratic | 0.53 | 0.94 | **2.1 [read]** | 3.8 | coefficient 0.236 [read]; 3 and 6 °C [read]; 1.5, 2, 4 °C [derived] |
| Barrage and Nordhaus 2024 (DICE-2023) | level, quadratic | 0.77 | 1.38 | **3.1 [read]** | 5.5 | 3 and 4.5 °C [read]; coefficient [unverified] (derived 0.344); 1.5, 2, 4 °C [derived] |
| Howard and Sterner 2017, non-catastrophic x 1.25 | level, quadratic | 1.67 | 2.97 | 6.69 | 11.90 | coefficient 0.595 and 1.25 [read]; all damages [derived] |
| Howard and Sterner, with catastrophic term (= B&N's "9% at 3 °C") | level, quadratic | 2.26 | 4.01 | **9.03 [derived; B&N read: 9%]** | 16.06 | coefficients [read]; sum [derived] |
| Burke et al. 2015 | growth rate, local temperature | not comparable | | | | -23% by 2100 [read]; temperature-specific damages [unverified] |

## 7. What cannot be verified here

The psi1 and psi2 values of DICE-2023; the baseline year of DICE-2016R's temperature; Howard and Sterner's online appendix and any damage printed at 3 °C; the numerical content of Burke's Extended Data Tables 1 and 3 and Fig. 5d; Hsiang et al. (2017), which was blocked; the reasons for the Kotz et al. retraction (not needed). The editor may be able to open the SI files and Hsiang et al. (2017) from a library.

## 8. Which warming channels F3 actually has after D-016 (evidence from the repo; for the replace-versus-add question)

Read from Earth4All.jl at commit `16f37d0` (`src/*/subsystems.jl`, `src/*/parameters.jl`) and `audit/earth4all-time-driven-equations.csv`; D-016 verdicts from `DECISIONS.md`. All seven switches have the form `1 + coefficient x (OW / OW2022 - 1)` for `t > 2022` and 1 before, with `OW2022 = 1.35` (a constant, D-023). `OW` is observed warming, which F3 would take from FaIR.

| Switch | Sector (D-016 verdict) | What it changes (source line) | Coefficient | In F3? |
|---|---|---|---|---|
| `OWECC` | output (**reuse**) | cost of capacity: `COCA = CC1980 x OWECC` (`output/subsystems.jl:112,127`) | OWECCM = 0.2 | **yes** |
| `OWELC` | output (**reuse**) | life of capacity, i.e. loss of capital: `LCPIS = (LCPIS1980 x OWELC)/EDELC` (`:139,128`) | OWELCM = -0.1 | **yes** |
| `OWTFP` | public (**reuse with changes**) | indicated TFP: `ITFP = TFPEE5TA x OWTFP` (`public/subsystems.jl:67-68`), which feeds output's `ECR = (ITFP - ETFP) x CRR` (`output/subsystems.jl:120`) | OWETFP = -0.1 | **yes** |
| `OWLCO2` | climate (**replace**, FaIR) | warming effect on CO2 | | no |
| `WELY` | foodland (**replace**) | warming effect on land yield (OWEACY = -0.3) | | no |
| `CO2ELY` | foodland (**replace**) | CO2 effect on land yield | | no |
| `WELE` | population (**replace**) | warming effect on life expectancy (OWELE = -0.02) | | no |

**What this establishes (measured from the source, not assumed):**
1. After D-016 F3 keeps **three** warming channels, all inside reused sectors, all acting on the **economy's capital and productivity**: cost of capacity (+20% per unit of `OW/OW2022 - 1`), loss of capital (shorter life, -10%), and TFP (-10%). The other four are in replaced sectors and disappear.
2. These three act on **different variables** from an output-level damage function (capital cost, capital life, TFP growth input), and **their coefficients are small**: a warming of 2.7 K (twice `OW2022`) multiplies capacity cost by 1.2, capacity life by 0.9, indicated TFP by 0.9. Whether that is smaller or larger than a DICE-type output loss was **not computed** (it requires running the reused sectors, which is M4).
3. **So the double-counting question is real, not hypothetical, but its size is unknown today.** If D-007's damage function is applied to output **and** the three channels are kept, damages to capital and TFP are counted twice in part (the channels already lower capital and TFP, which lower output). If the damage function replaces the channels, F3 must switch the three switches off (set their coefficients to zero: a parameter change in reused sectors, not a code change) and say so.
4. **Until M4 ports the output and public sectors, F3 has no economy that contains these channels:** the slice's economy is S3's (GATE's), which has **no warming channel at all**, so in M2 the damage function would be the **only** warming-to-economy link. The replace-versus-add choice therefore bites from M4, not M2.
5. The baseline question of D-023 applies to all three: the switches divide FaIR's anomaly by the constant 1.35, and the baseline of FaIR's anomaly against Earth4All's `OW` is **not checked**.
