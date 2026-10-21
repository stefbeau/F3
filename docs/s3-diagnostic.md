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

## 3. Results (run 2026-10-21; figures in `audit/data/s3-diagnostic.json`; bundle hash checked, sha256 `3afe8e4d...`)

Nothing in sections 1 and 2 was changed after the run. Values are at index k = year - 2025, i.e. the end of that year (1 January of the next); "x2" and "x10" are the first years a quantity is outside a factor of 2 and of 10 of Epoch's stored run for the same setting.

### 3.1 Default setting (B0), log10 of the value (decimal exponent)

| | 2025 | 2030 | 2040 | 2050 | 2060 | 2080 | 2100 |
|---|---|---|---|---|---|---|---|
| **compute stock Q (FLOP/year)**, stored run | 28.7 | 31.2 | 35.2 | 41.9 | 44.6 | 45.2 | 45.2 |
| A1: S3 on GATE's path, own composite | 28.7 | 31.2 | 33.8 | 35.1 | 37.0 | 39.2 | 39.3 |
| R0: S3 under R3, stored composite | 28.7 | 31.2 | 35.2 | 42.1 | 44.8 | 45.4 | 45.5 |
| R1: S3 under R3, own composite | 28.7 | 31.2 | 33.8 | 36.7 | 38.6 | 39.8 | 40.2 |
| **output gwp (USD/year)**, stored | 14.1 | 14.5 | 18.2 | 24.1 | 24.8 | 25.0 | 25.0 |
| A1 | 14.1 | 14.4 | 15.8 | 17.3 | 19.0 | 19.6 | 19.7 |
| R0 | 14.1 | 14.5 | 18.2 | 24.1 | 24.8 | 25.0 | 25.0 |
| R1 | 14.1 | 14.4 | 15.7 | 18.2 | 19.3 | 19.7 | 19.8 |
| **data-centre electricity (TWh/year)**, the stored run through the module | 3.2 | 4.9 | 7.4 | 11.9 | 14.3 | 14.9 | 14.9 |
| A1 | 3.2 | 4.8 | 6.4 | 6.8 | 7.9 | 9.5 | 9.6 |
| R0 | 3.2 | 4.9 | 7.5 | 12.0 | 14.4 | 15.1 | 15.2 |
| R1 | 3.2 | 4.8 | 6.4 | 8.2 | 9.2 | 9.7 | 9.9 |

(The 2025 electricity entry, 10^3.2 = about 1,600 TWh, is the end of 2025, after one period of growth from the 485 TWh calibration point. Effective compute, `g(Q) x S`, is in the JSON: stored 29.6, 33.2, 38.0, 42.2, 42.3, 42.3, 42.3; it saturates because `g(Q)` is capped at `C_L = 2e38`. Conservative and aggressive settings are in the JSON and agree in kind.)

### 3.2 Which stage differs from Epoch's stored run, and by how much (criterion 1)

| stage | B0 default | B1 conservative | B2 aggressive |
|---|---|---|---|
| **A0** S3 on GATE's path, stored composite | **none**: all four quantities equal the stored run (max abs log10 ratio 0.0 to 0.001) | none | none |
| **A1** same, S3's own composite | x2 2034 (gwp); x10 **2038** (gwp); effective compute 2039, Q 2040, electricity 2040; largest gap 7.9 orders (Q, 2056) | x10 **2044** (gwp); largest 9.2 (Q, 2073) | x10 **2033** (gwp); largest 9.1 (Q, 2053) |
| **R0** S3 under R3, stored composite | x2 2034 (Q and effective compute), **never x10**; largest 0.35 orders (a factor 2.2); gwp within 0.08 orders (a factor 1.2) | never x10; largest 0.56 (a factor 3.6, Q, 2041); gwp within 0.06 | never x10; largest 0.38 (a factor 2.4); gwp within 0.06 |
| **R1** S3 under R3, own composite | x10 **2037** (gwp); Q 2039; largest 6.0 orders | x10 **2043** (gwp); largest 6.8 | x10 **2033** (gwp); largest 6.3 |

### 3.3 Electricity against absolute bounds (criterion 2), default setting

Modelled demand, no supply limit, first year above: 5% of the Earth4All supply, **2026**; the supply itself (about 33,600 TWh in 2025), **2029**; today's world energy use (5e20 J, about 1.4e5 TWh), **2032**; the paper's 1%-of-Earth-dissipation bound (5e22 J, about 1.4e7 TWh), **2040**. **These are the same years for the stored run itself and for A0**, and similar for the other two settings (2031 to 2037 for today's energy use and the paper's bound in 2037 to 2043). With S3's own composite (A1, R1) the paper's bound is crossed later (2045 to 2060) and demand reaches 4e9 TWh (A1) or 8e9 TWh (R1) in 2100, about 300 to 600 times the paper's bound. The coupled slice (supply limit on, damage central) holds S3 far below those figures: S3 output 2.1e14 USD/year in 2030 and 9.6e14 in 2050 (the unlimited R1 run has 6e14 and 6e18), `supply_ratio` 0.048 in 2030, 0.0019 in 2050 and 0.00013 in 2100.

Also: the stored run's own raw compute stock reaches 10^45 FLOP/year, seven orders above `C_L` (the stock is not capped; `g(Q)` is), and its output reaches 10^25 USD/year (about 10^11 times 2025's), so **Epoch's own shipped run is outside any range for which the paper gives a bound**. Its 2030 demand through the module is about 7e4 TWh against the IEA's 950 TWh projection (a comparison of magnitude only; the IEA figure is a projection under its own assumptions).

### 3.4 Verdict against the pre-registered criteria

- **Criterion 4: the hypothesis is REFUTED as stated**, because A1 (S3 with its own composite on GATE's path) crosses a factor of 10 in 2033 to 2044. It is also not wholly wrong, so the picture is split in four:
  1. **S3's laws of motion are not the source.** A0 equals the stored run to 1e-3 or better in all four quantities in all three settings (this repeats the A1.3 diagnostic).
  2. **R3 is not the source of the magnitudes.** With the stored composite it stays within a factor of 2.2 to 3.6 on compute and 1.2 on output (R0); the A1.4 share errors do not produce the implausible values.
  3. **S3's own composite is the only place S3 departs from GATE, and it moves the result DOWN**, by 5 to 6 orders in output by 2050 to 2100 and by 5 to 9 orders in compute stock. It does not create the implausible highs; it makes S3 less extreme than GATE and still outside any bounded range (output 10^19.7 USD/year in 2100).
  4. **The data-centre module is the first physically bounded failure, and it fails on GATE's own path.** The stored run through the module crosses the paper's own physical bound (criterion 2 iv) in 2037 to 2043 and the total electricity supply in 2029. The module takes the raw, uncapped compute stock `Q` and scales efficiency with S3's hardware price-performance, with no cap from `C_L` and no energy bound.
- **Criterion 3 as written is ambiguous, and I report both readings.** Applied literally, the first stage to cross criterion 2 (iii) is A0 (2031 to 2032), because the module is applied to every stage. The first stage in which an S3 stage departs from the stored run by a factor of 10 is R1 in B0 (2037) and A1 in B2 (2033), that is the composite. The pre-registered rule was not changed to choose between them.
- **Arithmetic note, not run:** `eta_0` is about 8e9 FLOP/J (485 TWh at 1e28 FLOP/year, PUE 1.4). With hardware at the paper's `H_max` (1e5 times `H0`), efficiency would be about 8e14 FLOP/J, below the 4e15 FLOP/J behind `C_L`. Demand at `g(Q) = C_L` would then be about 1e8 TWh, about 7 times the paper's own bound. So capping the module's input at `g(Q)` would not by itself bound electricity. This is a hand calculation from the module's formula, not the result of a run.

### 3.5 What this means for the next step (not decided)

The implausible electricity figures come from the data-centre module's mapping, and they would persist if S3's composite were fixed (A0 and the stored run show it). S3's departure from GATE comes from the composite alone (the blind brief, `docs/s3-composite-blind.md`). Making S3 match GATE better would push output and compute **up** toward Epoch's astronomical values, so fixing the composite would make the module's problem worse, not better. Epoch's own run leaves the plausible range, so "validating S3" can only mean reproducing GATE (a statement about GATE), not producing plausible magnitudes. The options are the editor's to choose; nothing was changed.

### 3.6 Limits of this diagnostic

The comparison is with Epoch's three stored runs only (the paper reports no result series). No module variant, composite variant or cap was run. The module was applied post hoc to series (no supply limit, no loop) except in the SLICE row. The 2025 entry is the end of 2025, after one period of growth, not the calibration instant.
