# Proposal: a data-centre electricity module limited by how fast power can be built (D-066, Proposed)

**Status:** proposal, written 2026-11-25. Nothing here is built, tested or approved, except the exploratory prototype named in section 4, which is not a model component. Only the editor approves decisions.

## 1. The problem, as measured
Source: `audit/s3-default-composite.md` (S3 under R3, central levers, default composite).

- **The module asks for electricity that cannot exist.** With the limit on, S3's installed compute would draw about 37,000 to 39,000 TWh in 2030 and 440,000 to 620,000 TWh in 2040. The module then grants 5% of total supply (about 1,750 TWh in 2030), so less than 0.5% of the demand is served by 2040.
- **S3 keeps buying compute it cannot power.** The investment rule R3 does not see the shortfall. This is the counter-loop recorded as the B1 sign failure (Track A): halving supply gave more compute, not less.
- **The limit is a fixed share of supply**, reached within two to three years. After that the module has no dynamics of its own.
- **Energy efficiency follows hardware price-performance** (`eta = eta_0 × H(t)/H(2025)`, D-033, labelled an assumption). FLOP per dollar and FLOP per joule are different quantities.

## 2. What the world looks like (context, not calibration)
Read on 2026-11-25 from press reports of the IEA's World Energy Outlook 2026 (published 2026-11-19) and other news; **the primary documents were not read** and none of these figures is in the source register yet.

- Data-centre electricity use: about 500 TWh today, about 1,000 TWh in 2030 and 1,500 TWh in 2035 in the IEA's Stated Policies Scenario; up 17% in 2025 against 3% for all electricity.
- 93 large AI facilities under construction or expansion, about 50 GW when complete; their combined capacity went from under 2 GW to about 17 GW in two years.
- Building a data centre takes 2 to 3 years; grid and generation take 4 to 8. Operators install their own gas generation to avoid the wait. Some announced expansions have been dropped.

**Reading (mine):** the binding constraint in the real system is the rate at which powered capacity can be added, not a share of existing supply.

## 3. Proposed design
Four steps, each usable alone. Every new parameter is a labelled lever or a labelled assumption with a source to find.

### Step E1: powered capacity as a stock with a build-rate limit (the core)
- New state: **powered capacity `P`** (TWh/year that data centres can draw), starting at the 2025 calibration point.
- `P` grows only when demand exceeds it, and **at most `g_max` per year** (lever; a first range of 15% to 50% a year to be justified from the capacity histories in the registered Epoch AI data-centre dataset and the IEA series, licences permitting).
- Electricity available = min(`P`, `outer_share` × total supply). `outer_share` replaces today's 5% cap and stays a lever.
- S3's usable compute is scaled by available / demanded, as today (`supply_ratio`), so the interface to S3 does not change.
- With `g_max` infinite and `outer_share` = 5% the module must equal today's module to 1e-9 (test).

### Step E2: the investment rule sees the shortfall
- R3's compute share is reduced in proportion to the unpowered part of the compute stock, and the freed share goes to consumption (first form) or to building power (second form, a new stock-flow link; needs a cost of power capacity, a parameter to source).
- Purpose: remove the counter-loop behind the B1 failure. This changes R3, which is the editor's rule (D-028): a labelled variant, default off, until reviewed.

### Step E3: energy efficiency on its own path
- `eta` (FLOP/J) gets its own growth path and ceiling, separate from `H` (FLOP/USD), fitted to hardware efficiency data (the registered Epoch ML-hardware dataset has release dates and power figures) and bounded by the D-055 cap.
- Purpose: stop the module from assuming that every gain in price-performance is also a gain in energy efficiency.

### Not in this proposal
- **Emissions from data-centre power stay reported, not fed to the climate sector** (D-021: emissions prescribed; D-035's exact replay depends on it).
- **Own generation adding to total supply**, minerals and water for data centres (S5), and the electricity link to World3 (D-059) are untouched.

### Step E4 (added the same day at the editor's request): water and land as reported outputs
F3's spec has a materials and water sector (S5) that is not built. Without waiting for it, the electricity module can report two derived quantities, both labelled diagnostics that nothing reads:
- **Water consumed by data centres** = electricity used × a direct intensity (cooling, litres per kWh) + electricity used × an indirect intensity (water consumed generating the electricity, by supply mix). Both intensities are parameters to source, with ranges.
- **Land taken** = powered capacity × an area intensity (hectares per MW of campus), a parameter to source from campus records.
- **What F3 cannot do:** say *where*. F3 is a global model with no geography. Regional exposure (which basins, which farmland or forest) can be shown on the site as **context maps built from published data**, clearly separate from model output.

Context read on 2026-11-25 from secondary reports (primary documents not read; none in the source register yet):
- The IEA's Energy and AI (2025) is reported to put data-centre water consumption at about 560 billion litres a year (2023), rising to about 1,200 billion by 2030, about a quarter of it direct cooling.
- A 2026 study in *Environmental Science & Technology* (Stanford, Carnegie and others) is reported to find 2,315 of 9,347 data centres in regions where water demand exceeds supply for at least one month a year, rising to about one in three at 3 °C of warming.
- Land: the one large figure found is about 3,650 acres of former farmland for Meta's Hyperion campus in Louisiana. **No sourced figure for forest clearing was found**; the claim that large areas of trees are cut is not supported by what was read and needs its own search before anything says so.

A first context infographic with a world map was drawn outside the repository on 2026-11-25 (not model output, not on the site).

## 4. What an exploratory prototype shows (seen before any test below was written)
`audit/t0/dc_build_rate_prototype.py` (not a model component; default composite P; TLTL supply; `outer_share` 25%; no damage). Step E1 with three build rates, and the first form of step E2 ("aware").

| `g_max` | Data-centre use 2030 (TWh) | 2035 | 2040 | Share of supply 2030 | Demand / use in 2040, E1 only | with E2 |
|---|---|---|---|---|---|---|
| 15% a year | 976 | 1,962 | 3,946 | 2.8% | 153× | 12× |
| 30% a year | 1,801 | 6,686 | 10,440 | 5.1% | 52× | 8× |
| 50% a year | 3,683 | 9,975 | 10,440 | 10.5% | 52× | 8× |

- **Electricity use becomes describable.** At 15% a year the 2030 figure (976 TWh, 2.8% of supply) is of the size of the IEA's (about 1,000 TWh, just under 3%). This is a coincidence of a first guess with a published scenario, **not a validation**: `g_max` was not fitted to anything.
- **Step E2 cuts the unpowered overhang** by a factor of 6 to 13 in 2040.
- **Long-run output stays implausible.** Output still reaches about 2.4e7 trillion USD in 2099 with E1 alone and more with E2 (2.9e8; why E2 raises it was not investigated). Electricity use is bounded, but compute per unit of electricity is not: S3's hardware and software efficiency can each still rise by four to five orders of magnitude.

**So this proposal makes the electricity side work; it does not by itself make S3's output plausible.** That needs step E3 and, beyond this proposal, the reconciliation of S3's economy with the World3 economy (`docs/s3-world3-reconciliation.md`), which is where material limits enter.

## 5. Acceptance tests (to be fixed in a test document before any code; drafted here knowing the prototype's figures)
- **E-T1 OFF equals recorded:** with the new options at their neutral values, every recorded slice and M6 result to 1e-9.
- **E-T2 conservation:** electricity used never exceeds `P` nor `outer_share` × supply; `P` never falls; all outputs finite and non-negative over the lever grid.
- **E-T3 extremes:** `g_max` = 0 holds use at the 2025 level; `g_max` infinite reproduces the share-cap module.
- **E-T4 sign, B1:** halving supply or `g_max` never raises usable compute (the reading that failed in Track A), with a control that fails as required. With step E2 on, it also never raises the compute stock.
- **E-T5 step halving:** the A2.6 reading (0.1%) re-run and reported; a failure is recorded.
- **E-T6 hindcast, report only:** modelled use for 2024 to 2026 beside the IEA figures, once their licence is read. No tolerance is set until the editor sets one before the data are used.
- **E-T7 comparison, report only:** 2030 and 2035 beside the IEA scenario figures. **Never a target** (plan A2.2).
- **Mutation check** on each sign test, as for S7.

## 6. Data and decisions needed
- **Sources to register and read** (licence first, A5.6): IEA World Energy Outlook 2026; the IEA's facility tracking behind the "93 facilities" figure; Epoch AI data-centre and ML-hardware datasets (registered, CC BY).
- **For the editor:** approve D-066 (scope and order of the steps); the first range of `g_max` and `outer_share`; whether step E2 may change R3 as a labelled variant; the labels the new outputs carry. The withheld outputs stay withheld until he decides otherwise.

## 7. Size (estimates, not measurements)
Step E1 with its tests: one to two sessions. Step E2: one to two. Step E3: two to three, mostly data work.
