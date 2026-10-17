# Track A log

## 2026-10-17 IEA boundary: stop, then editor decision (option a)
Plan committed first (`docs/tracks/track-a-plan.md`, aa40a45). IEA numbers and licence verified (see plan section 0); the formal accounting boundary was not. The track stopped and reported; the editor decided option (a) on 2026-10-17 (relayed by the orchestrator). Work continues from step 2. 485 TWh (2025) is a CALIBRATION point and 415 TWh (2024) a reference; neither is validation anywhere. 950 TWh (2030) is a report-only comparison. The crypto-mining exclusion is [unverified] and is labelled so on the page and in the report.

## Provisional decisions (paste-ready blocks)

### P-A1 — Data-centre boundary for the F3 data-centre module (IEA Energy and AI, descriptive)
- **Status:** Provisional (delegated)
- **Date:** 2026-10-17
- **Decision:** "Data centre" means a facility housing servers, storage systems, networking equipment and associated components (cooling, power distribution, UPS, lighting), as the IEA's Energy and AI describes it. The module's `E_dc` is compared with the IEA's totals on that descriptive boundary only. Whether crypto-mining load is excluded from the IEA totals is [unverified] (no IEA text read states it; a secondary source says it is). 485 TWh (2025) is a calibration point, 415 TWh (2024) a reference value, 950 TWh (2030) a report-only comparison; none is called validation.
- **Recommendation followed:** the editor's option (a), 2026-10-17, after the track reported that the formal boundary could not be verified.
- **Alternatives considered:** (b) wait for the IEA methodology or the full Energy and AI PDF before any module code.
- **Cost of reversing it:** low. The boundary only fixes the calibration constant `eta_0` and the labels; a different boundary re-calibrates one constant, re-runs the grid (about 30 to 34 minutes per loop run with 841 members) and changes label text.
