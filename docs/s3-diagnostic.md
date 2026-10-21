# S3 diagnostic: where do the implausible outputs come from? (D-053, Provisional; written 2026-10-21)

**Status:** method and pre-registered criteria, **committed before the diagnostic script was run**. Results are added below by dated sections; nothing above is edited afterwards. **Diagnostic only: no sector, no validated test and no label is changed.** Script: `audit/t0/s3_diagnostic.py`; figures: `audit/data/s3-diagnostic.json` (comparison figures only; no series from Epoch's bundle, D-026).

## 1. Question and hypothesis

The recorded S3 outputs leave any plausible range (modelled data-centre demand about 7 billion TWh a year by 2100 against 485 TWh in 2025; raw compute stock about 1.4e40 FLOP/year). Which stage first leaves a plausible range, and by how much?

**Hypothesis to test, not assumed (editor):** the implausibility comes from the data-centre module (D-032 to D-036) or from R3 (D-028), **not from S3's core.** The result may refute it: the A1.3 failure already shows that S3's own task-allocation composite differs from Epoch's, and the composite is part of S3.

## 2. Method and pre-registered criteria (fixed before the run)

**Stages** (each for the three shipped settings B0 default, B1 conservative, B2 aggressive, D-005 amendment B; periods 2025 to 2100, index k = year - 2025 = end of that year, the stored-index convention):

| stage | what runs | what it isolates |
|---|---|---|
| A0 | S3 on GATE's own investment path, Epoch's stored composite `T` supplied (diagnostic input) | S3's laws of motion alone (the A1.3 diagnostic already passed: 3e-16 to 1.5e-3) |
| A1 | S3 on GATE's own investment path, S3's own composite (the A1.3 configuration) | the composite (the A1.3 gap) |
| R0 | S3 under R3, stored `T` supplied | R3's own error (A1.4 set b) |
| R1 | S3 under R3, own composite | the configuration F3 uses (A1.4 set a) |
| each of the above, through the data-centre module | `E = Q / eta * PUE`, `eta` proportional to hardware, calibrated to 485 TWh in 2025 (D-033), applied post hoc to the series, **no supply limit, no loop** | the module's mapping |
| STORED | Epoch's stored run itself (its `compute`, `hardware`) through the same module | is the electricity figure a property of GATE's own path? |
| SLICE | the coupled M2 slice (R3 + module + damage central, recorded FaIR replay), default setting only | the loop with supply limit |

**Quantities per decade** (2025, 2030, then every decade to 2100): compute stock `Q` (FLOP/year), effective compute `g(Q) x S` (eFLOP/year), output `gwp` (USD/year), modelled data-centre electricity (TWh/year).

**What the paper itself reports (read 2026-10-21, full text, arXiv:2503.04941 v2).** **No scenario result in any requested category**: the text states no GWP growth rate, no year at which automation reaches a level, no compute or training-run trajectory, no share of output invested, and no electricity figure; Figure 5 is "illustrative outputs" without numbers in text or caption. It gives **inputs and physical bounds only**: `C_L = 2.0e38` FLOP/year from a CMOS efficiency of 4e15 FLOP/J and about **1% of Earth's energy dissipation (about 5e22 J/year)**; today's energy consumption about **5e20 J/year** (low end of the range of `C_L`); initial GWP about 110 trillion USD, initial capital 450 trillion, initial largest training run 5e25 eFLOP. Section 9 of the paper lists "energy requirements and electricity provision" as **not captured**. So the comparison with the paper is by **physical bounds**, and the comparison of trajectories is **with Epoch's three stored runs** (read at test time, D-026).

**Pre-registered plausibility criteria** (all stated here before any result):
1. **Against Epoch's stored run with the same parameter setting:** a quantity "differs" at the first year its ratio to the stored value is outside a factor of 2 (|log10 ratio| >= 0.301), and "leaves the plausible range" at the first year it is outside a factor of 10 (|log10 ratio| >= 1). The stored runs are the only independent trajectory; they are not truth, they are what Epoch's own model produced.
2. **Electricity, absolute bounds** (modelled demand, TWh/year), first year above: (i) 5% of the Earth4All TLTL electricity supply (the module's own cap, D-033); (ii) 100% of that supply (about 32,600 TWh in 2025, 44,600 in 2050, 35,400 in 2100); (iii) today's world energy use, 5e20 J = **about 1.4e5 TWh/year** (paper, D.3.2); (iv) the paper's 1%-of-Earth-dissipation bound, 5e22 J = **about 1.4e7 TWh/year**. Exceeding (iii) or (iv) is not a finding about the world; it marks the module or S3's compute path as outside any physical range.
3. **"First stage that leaves the range"** is the earliest stage, in the order A0, A1, R0, R1, then the module, that crosses criterion 1 (factor of 10) for any of the four quantities, or criterion 2 (iii).
4. **The hypothesis is judged supported** only if A0 and A1 stay inside a factor of 10 of the stored run for all four quantities **and** the first stage that crosses is R0, R1 or the module. It is judged **refuted** if A1 (S3 with its own composite on GATE's path) already crosses; and **mixed** otherwise, with the sizes stated.
5. **What the result cannot say:** that any stored value is correct; that any year after about 2027 means anything for S3's absolute level (D-029); that the module is wrong in form rather than in input (the module takes S3's raw `Q` and hardware, so it inherits S3's errors).

## 3. Results

(to be added after the run, in a dated section)
