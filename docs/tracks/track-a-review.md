# Track A review (for the editor's batch review and the A2.7 decision)

## Provisional decisions (blocks in docs/tracks/track-a.md)
P-A1 data-centre boundary (editor's option a); P-A2 module form, PUE 1.4, 5% supply share cap, Earth4All.jl TLTL supply; P-A3 damage action (central default, no offset); P-A4 one exact 841-member climate recording replayed (valid only while emissions are prescribed); P-A5 grid (3 AI settings x 3 damage options + 2 supply cases). Recommend approving all; P-A2's 5% cap and PUE are assumptions the editor may want to set.

## Failures (nothing relaxed; 20-member development climate, `audit/data/m2-slice-results-dev20.json`)
- A2.6 step halving: FAILS. Largest difference 0.565% (data-centre electricity used, 2036; first above 0.1% in 2028); gwp 0.197% (2099; first 2080); compute 0.108% (2049).
- B1 sign as written: FAILS. Half supply gives up to 17.8% MORE compute than base in 2038-2045 (first 2038); growth is lower only in the five years after the cap binds (2027). Probable cause (inference): R3 shares depend on usable compute.
- R1 sign: FAILS on automation at 2065 (both 1.0); compute higher; automation higher at 2035 and 2045.
- Passes: A2.2 consistency (by construction), A2.4 (both readings, 1e-9), A2.5 (both), B2, damage anchors. Existing suite: 56 passed, 15 skipped, 1 xfailed.
- Finding: supply binds from 2027-2028; modelled data-centre demand reaches 20,000 TWh in 2030 and 414,000 TWh in 2040, i.e. S3's compute path (unvalidated, D-029) leaves any plausible range. The page says so. The 950 TWh figure is shown as the IEA projection only.

## Labels on the page (all present)
conditional scenarios not forecasts; D-029 (S3 status text from `S3AI.validation_status`); GATE re-implemented from the paper; Epoch near-full-automation warning; D-030/D-021 (from `S6Climate.validation_status`) and non-CO2 prescribed; D-007 level effects, high not the upper end; D-028 with A1.4 numbers; not shown list; plan section 10 caveats; 485 calibration, 415 reference, 950 projection; crypto exclusion [unverified]; attributions (HadCRUT5 OGL text, GCB, IEA, FaIR, GATE, Earth4All.jl) and sha256 provenance.

## Recommendation
Approve the Provisional blocks. Do not approve Demo 0 yet: three recorded test failures (A2.6, B1, R1-automation) and the electricity demand runaway are on the page's own admission. The editor decides whether to accept these as recorded, or to propose labelled post-hoc changes (not applied here).

## A2.7 checklist
1. Page opens offline in light and dark and at phone width (JS checked by a headless run; not viewed in a browser by me).
2. All labels above read as acceptable; the failed-test section is acceptable.
3. Climate is the 841-member exact recording (2100 warming 2.858 K; 1450 s).
4. Decide on the three failures and on the 5%/PUE assumptions.
5. Nothing is published; no deployment done.
