# Batch review for the editor (prepared 2026-11-25)

Thirteen decisions are recorded as "Provisional (delegated)" and wait for the editor. **The recommendations below come from reading each decision's text and its stated cost of reversing; I did not re-run or re-audit the work behind them.** A reply of "approve all as recommended" is enough; any line can be taken out.

| ID | What it decides | Cost of reversing (as recorded) | Recommendation |
|---|---|---|---|
| D-032 | What counts as a data centre for the module (the IEA's descriptive boundary) | Low | Approve |
| D-033 | The module's form: electricity = compute / efficiency × PUE, efficiency following hardware price-performance, 5% share cap | Low to medium | Approve as the record of what was built. **D-066 proposes to replace its cap and its efficiency assumption.** |
| D-034 | How climate damage acts on S3's output | Low | Approve |
| D-035 | One exact climate recording reused for every run | None | Approve. Stops being exact if emissions are ever coupled. |
| D-036 | The Demo 0 scenario grid and levers | Low | Approve |
| D-045 | Test fixtures re-exported on a finer grid, no criterion change | None | Approve |
| D-053 | S3 diagnostic and reconciliation study (documents and scripts only) | None | Approve. Its figures are for variant A (noted in the documents). |
| D-055 | Optional efficiency cap in the data-centre module, default off | None | Approve |
| D-056 | Explorer v0.2 redesign | Low | Approve. Published; its S3 results are for variant A. |
| D-057 | Explorer history overlay and warming map | Low | Approve |
| D-058 | Data retrieval campaign (sources, licences, derived series) | None for the model | Approve. 33 items still need the editor (`audit/data/needs-user.json`). |
| D-059 | Electricity link from data centres to World3 industrial output, default off | None | Approve |
| D-065 | Variant P as S3's default; notice reworded | One default and three notices | **Confirm.** It touches a validation label, which is the editor's to decide. |

## Also open
- **Proposed, not provisional:** D-006 (critical minerals granularity), D-008 (social-tension proxy), D-066 (electricity module by build rate).
- **Documents written for variant A**, now carrying a dated note and not revised: `docs/s3-world3-reconciliation.md`, `docs/s3-supply-limited.md`, `docs/s3-diagnostic.md`, `docs/s3-investment-rule-r3.md`, `docs/tracks/track-a.md`. The statement that the labour effect "persists" (D-054) is true of variant A; with variant P the original fading reading holds.
- **The published site** shows variant A results with the earlier notice. A rebuild needs the 841-member climate recording and the editor's approval to publish.
- **D-024:** the editor sets the backtest thresholds before the hindcast.
