# Links 3 and 4: readings and tests, written before the code

Written 2026-11-26, after links 6 and 7. The editor wrote: "Try and find additional data to make it work and unblock anything else. All links need to work properly." Both links below are **switches that are off by default**; both rest on choices recorded as **Provisional (delegated)** for the editor's review. Plan: `docs/links-3-4-6-7-plan.md`.

## Link 3: warming to World3 land yield (health NOT built)

**Additional data, read on 2026-11-26.** Zhao et al. (2017), PNAS 114, 9326: the abstract (read on PubMed Central) says that, without CO2 fertilisation, effective adaptation and genetic improvement, each degree Celsius of global mean warming reduces global yields of wheat by 6.0%, rice by 3.2%, maize by 7.4% and soybean by 3.1%. Only the abstract was read. The other three papers of `audit/data/needs-user.json` were not read.

**What was seen before these tests:** those four numbers; the recorded FaIR warming (1.35 K in 2025, 2.86 K in 2100). No result of this link.

**The link.** From 2025, World3's land yield is multiplied by `1 - c x (T(t) - T(2025))`, never below zero, with `T` the recorded FaIR ensemble-mean warming at the start of the loop step. Three options (Provisional): **low** `c` = 3.1% per K (the smallest of the four crops), **central** 4.925% per K (the plain mean of the four; my arithmetic, not a figure from the paper), **high** 7.4% per K (the largest). Warming is counted from 2025 because World3's yields are today's yields: warming so far is already in them.

**What it leaves out, and says so:** CO2 fertilisation, adaptation and breeding (so the loss is an upper reading for these crops); crops other than the four; regional differences; **health**. A global mean temperature gives no defensible mortality function, so the health half of link 3 stays not built and stays labelled (D-049).

**Readings (`tests/test_link3_yield.py`)**
- **L3-T1 switch-off invariance:** without the option, all 29 states equal the group alone to 1e-9, and the existing World3 tests pass unchanged.
- **L3-T2 no extra warming, no effect:** with a warming path held at its 2025 value, the option on equals the option off to 1e-9.
- **L3-T3 the multiplier is the stated one:** on a constructed path with +1 K after 2025 the multiplier is `1 - c` for each option, to 1e-12.
- **L3-T4 sign and order:** with the recorded warming, land yield in 2100 is lower with the link on than off, and lower for high than central than low. Control: with the multiplier forced to 1 the comparison must fail.
- **L3-T5 before 2025 nothing changes:** all states up to 1 January 2025 equal the stand-alone run to 1e-9 (so the 1961 to 2024 bound of the link note holds by construction; stated, not claimed as a hindcast).
- **L3-T6 with the output damage on as well:** finite and non-negative; the two channels are reported separately.
- **Report only:** land yield, food per person and population in 2050 and 2100 for the three options, standard levers.

## Link 4: S3 output to World3 industrial output, bounded by a growth cap

**New measurement (2026-11-26, seen before these tests).** With steps E1 and E2 on, S3's uplift factor (output with AI investment over output without) is still about 1.9 in 2030, 9 to 14 in 2040, 160 to 310 in 2050 and millions later. The electricity limits do not bound it. Applied as measured it is not a link.

**The link (Provisional, and the weakest of the seven).** From 2026, World3's industrial output is multiplied by a bounded uplift `U_b(t)`: it follows S3's measured uplift but may grow by at most `cap` a year (`U_b(t) = min(U(t), U_b(t-1) x (1 + cap))`, `U_b(2025) = 1`). **The cap is a scenario assumption, not data.** It has no default: the caller must give it. Values run for the report: 1%, 2% and 5% a year of extra growth. S3's uplift comes from one fixed run (R3 central, build rate 30%, outer share 25%, E2 on). One-way: World3 does not feed back on S3.

**What it is not:** a reconciliation of the two economies; a validated effect. S3's level is unvalidated under F3's own investment rule, so with any cap that binds, **the result is the cap** and S3 only decides when it starts to bind. The report says in which years the cap binds.

**Readings (`tests/test_link4_ai_uplift.py`)**
- **L4-T1 switch-off invariance:** without the uplift, all 29 states equal the group alone to 1e-9.
- **L4-T2 an uplift of 1 changes nothing** (1e-9).
- **L4-T3 the cap is respected:** `U_b` never grows by more than the cap in a year, never falls below 1 when `U` is at least 1, and equals `U` where `U` grows more slowly than the cap.
- **L4-T4 sign and order:** industrial output in 2030 and 2040 is higher with the link on than off, and not lower with a 5% cap than with 1%. Control: with S3's AI investment off the uplift is 1 and the comparison must fail.
- **L4-T5 bounds:** every state finite and non-negative over the three caps.
- **Report only:** the years in which the cap binds; World3 industrial output and population in 2050 and 2100 for the three caps.
