# S7 social module: one-page document of equations, units, bounds and the source of every parameter (A5.1)

**Status:** written 2026-10-21 on branch `m5-s7`, **before any S7 code**, for the editor's review (plan A5.1: the editor sees this before the code merges). **Nothing in S7 is calibrated, and no result of it is a prediction.** Under D-049 unsourced parameters are allowed as **illustrative**, with that label on every output; this document says, for each parameter, whether it has a source or is illustrative. **Almost every dynamic parameter is illustrative**: there is no F3 reference model for S7, no reading of WID, ILOSTAT or any social-science source has been done (those are STOP items in `docs/m5-plan.md` section 6), and Turchin's structural-demographic theory is a concept, not a parameter source.

**What S7 is, in one sentence.** Four bounded stocks (inequality, trust, tension, well-being) driven by the labour share of income, automation-driven under-employment and warming stress, with a delayed policy response (loop B5) and the reinforcing loop R2 (automation, falling labour share, rising inequality, rising tension, lower well-being). It is a **scenario-structure** module: its purpose at this stage is to make the loops testable, not to say how large any effect is.

**Labels that every S7 output carries (D-008, D-049):** "illustrative parameters"; "tension is a model-internal index, **not validated against history**"; where S3 feeds it, the D-029 label; where S1 results are shown with it, "no health or yield effect of warming". Tension is excluded from the D-024 backtest framework (D-008).

## 1. Interface (names and units; checked by the coupling core)

| Input | Unit | Where it comes from | Note |
|---|---|---|---|
| `labor_share` | 1 | S3 (`labor_share`, GATE's labour share of output) | **S3's level is unvalidated (D-029).** S7 uses only changes in it relative to its start (see 2.1), and the module test uses a **given** path |
| `unemployment` | 1 | S3-side proxy (1 - labour used / labour available) or a given path | not produced by S3 today; **illustrative input** in M5 step 2 |
| `warming` | K | S6 (`warming`) | FaIR starts 0.04 to 0.07 K low (D-030) |
| `gdp_per_capita_growth` | 1/year | S3 `gwp` and S1 population, or a given path | S3 level unvalidated; only the **sign and size relative to a given path** are used in tests |
| `redistribution` | 1 | scenario lever | 0 to 1, default 0 |

| Output | Unit | Meaning |
|---|---|---|
| `inequality` | 1 | income share of the top 10% (stock, bounds 0.10 to 0.90) |
| `trust` | 1 | social trust index (stock, bounds 0 to 1) |
| `tension` | 1 | social tension index (stock, bounds 0 to 1) |
| `wellbeing` | 1 | well-being index (stock, bounds 0 to 1) |
| `policy_response` | 1 | delayed redistribution pressure (stock, bounds 0 to 1) |

## 2. Equations

Time in years, step 0.25 year (D-003, explicit coupling D-022). All stocks use first-order relaxation toward a target, bounded by clipping; "clip(x, a, b)" = min(max(x, a), b).

### 2.1 Drivers (algebraic)
- **Labour-share pressure** `LSP = clip((LS0 - labor_share) / LS0, 0, 1)` where `LS0` = the labour share at the start of the run (so the driver is the **relative fall** from the start, which does not depend on the absolute level of S3's labour share).
- **Under-employment pressure** `UEP = clip(unemployment / UEmax, 0, 1)`.
- **Temperature stress** `TS = clip(warming / TSref, 0, 2)` / 2 (0 at no warming, 1 at `2 x TSref`).

### 2.2 Stocks
1. **Inequality** `dI/dt = (I_target - I) / tau_I`, with `I_target = clip(I0 + gI_LS * LSP + gI_UE * UEP - gI_R * R, 0.10, 0.90)`, where `R = redistribution` (the lever) plus `policy_response`.
2. **Trust** `dTr/dt = (Tr_target - Tr) / tau_Tr`, `Tr_target = clip(Tr0 - gTr_I * (I - I0) - gTr_T * Te, 0, 1)` (inequality and tension erode trust).
3. **Tension** `dTe/dt = (Te_target - Te) / tau_Te`, `Te_target = clip(Te0 + gTe_I * (I - I0) + gTe_UE * UEP + gTe_TS * TS - gTe_Tr * (Tr - Tr0) - gTe_W * (W - W0), 0, 1)`.
4. **Well-being** `dW/dt = (W_target - W) / tau_W`, `W_target = clip(W0 - gW_I * (I - I0) - gW_Te * (Te - Te0) - gW_TS * TS + gW_g * clip(gdp_per_capita_growth / gref, -1, 1), 0, 1)`.
5. **Policy response** (loop B5, **delayed**) `dP/dt = (P_target - P) / tau_P`, `P_target = clip(kP * max(Te - Te_threshold, 0), 0, 1)` with `tau_P` long (the delay).

Loops this gives: **R2** (LSP up, I up, Te up, W down) and **B5** (Te up, P up after the delay, R up, I down); the effect of tension on governance and investment efficiency in S2 (spec S7 "feedback to the system") is **not built** in M5 step 2 (no S2 coupling yet).

## 3. Parameters: value, unit, and source (or "illustrative")

**Every value below is illustrative unless the Source column names a document that has been read.** None has. "Starting values" are normalised to a neutral reference, **not** to observed data. They are chosen so that tests have room to move, and each sets only a scale, not a claim about the world.

| Parameter | Value | Unit | Source | Notes |
|---|---|---|---|---|
| `I0` start income share of top 10% | 0.40 | 1 | **illustrative** (an order of magnitude from general knowledge; **WID not read**) | not used as a calibration target |
| `Tr0` start trust | 0.50 | 1 | illustrative | normalised neutral |
| `Te0` start tension | 0.30 | 1 | illustrative | normalised; **not validated against history** (D-008) |
| `W0` start well-being | 0.60 | 1 | illustrative | normalised; Earth4All's indices are a comparison output, not a source |
| `P0` start policy response | 0 | 1 | illustrative | |
| `LS0` | taken from the input at the first step | 1 | n/a | makes the driver relative |
| `UEmax` | 0.30 | 1 | illustrative | unemployment at which the pressure saturates |
| `TSref` | 1.5 | K | illustrative | warming at which temperature stress is half of its maximum |
| `gref` | 0.03 | 1/year | illustrative | growth rate at which the growth term saturates |
| `tau_I` | 30 | years | illustrative | inequality adjusts slowly |
| `tau_Tr` | 15 | years | illustrative | |
| `tau_Te` | 5 | years | illustrative | tension adjusts faster |
| `tau_W` | 8 | years | illustrative | |
| `tau_P` | 10 | years | illustrative | **the delay of B5** |
| `gI_LS` | 0.30 | 1 | illustrative | gain: relative labour-share fall to target inequality |
| `gI_UE` | 0.10 | 1 | illustrative | |
| `gI_R` | 0.25 | 1 | illustrative | redistribution lowers the target |
| `gTr_I`, `gTr_T` | 0.60, 0.40 | 1 | illustrative | |
| `gTe_I`, `gTe_UE`, `gTe_TS` | 1.0, 0.30, 0.15 | 1 | illustrative | |
| `gTe_Tr`, `gTe_W` | 0.50, 0.30 | 1 | illustrative | |
| `gW_I`, `gW_Te`, `gW_TS` | 0.50, 0.40, 0.10 | 1 | illustrative | |
| `gW_g` | 0.10 | 1 | illustrative | |
| `Te_threshold` | 0.40 | 1 | illustrative | tension above which policy responds |
| `kP` | 2.0 | 1 | illustrative | |
| bounds | stocks 0 to 1 (inequality 0.10 to 0.90) | 1 | declared here | A5.2 tests these |

**Count:** 33 parameters, **0 sourced, 33 illustrative.** If you prefer fewer, the largest simplifications are: drop trust (3 parameters plus its gains) or drop well-being's growth term.

## 4. What this document deliberately does not do
- It does not read or use WID, ILOSTAT, the Penn World Table or any social-science source (STOP items).
- It does not calibrate to or compare with any observed series (A5.4 is deferred until after M6, D-049).
- It does not build the S7-to-S2 feedback, the unemployment proxy from S3, or the Earth4All index comparison output.
- It does not say how large R2 or B5 are in the world: the sign tests fix only the direction of each effect.

## 5. Questions for the editor before code merges
1. Is this set of stocks and drivers the right scope for a skeleton (inequality, trust, tension, well-being, delayed policy response)?
2. Is "illustrative with the label everywhere" acceptable for all 33 parameters at this stage, or should some be dropped to reduce how much is invented?
3. Is `labor_share` from S3 acceptable as the main driver while S3 is unvalidated (S7 uses only its relative fall from the start, and every S7 test uses a given path), or should S7 wait for a different labour-share source?
