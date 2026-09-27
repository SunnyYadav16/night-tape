# night-tape preregistration — working draft

Status: DRAFT. Becomes final at signed tag `v1.0-preregistered` (Fri 30 Oct 2026).
Every `TBD` names the decision (weekly-build-plan App. C) and the latest week it is signed.
`make prereg-check` (Week 6) fails while any `TBD` remains.

## 1. Estimand and endpoints
- **Primary endpoint:** BOATS effective spread in basis points, against the BOATS pre-trade BBO from `tbbo`. Never "NBBO".
- **Execution population of the primary endpoint:** TBD (D-1, W4 Mon). `side = N` marks non-displayed executions per vendor docs; the endpoint must name which executions it covers.
- **Key secondary:** 10-second price impact on the common signed decomposition sample.
- **Primary horizon:** 10 s. 60 s and 300 s are robustness only.
- **bps denominator:** TBD (D-10, W2). Default: pre-trade midpoint.
- **Mark-to-open:** reported separately as timing risk, never as execution cost.
- **Identity:** `ES_int = RS_int + PI_int` holds exactly on the common signed sample.

## 2. Inferential hierarchy (project plan §8.3)
- **Primary (descriptive):** stable BOATS execution quality, pre vs post.
- **Secondary (infrastructure package):** 9pm–4am vs 8–9pm gap:
  `Y[i,d,h] = α[i] + λ[d] + θ[i,h] + β·post_x_exchange_window[d,h] + ε`. β is a lower bound if spillover is positive.
- **Contingent (causal):** staggered adoption only if the stagger trigger fires. Trigger: TBD (D-12, W6 Wed 28 Oct). Estimators: Sun–Abraham, Callaway–Sant'Anna.
- **Mechanism:** quote count, HHI, depth and venue presence are descriptive correlates only, never regressors.

## 3. Sample
- **Universe and SHA-256:** TBD (D-7, W4).
- **Selection:** deterministic ranking from a frozen pre-treatment FINRA snapshot; strata quotas and tie-breaks TBD (D-7, W4).
- **Suffix symbols, corporate actions, survivorship:** TBD (D-9, W4).
- **Pre-period regimes (primary / sensitivity / excluded):** TBD (D-2, W3), from `preregistration/preperiod-regimes.yaml`.

## 4. Event definition and windows
- **Event session:** the first session with a registry `go_live_actual` entry. Never the target date, never a calendar date.
- **Windows:** one primary + two sensitivity windows, counted in sessions from the session calendar. TBD (D-4, W4).
- **Launch washout:** 3–5 sessions; exact length TBD (D-4, W4). Launch night reported separately.

## 5. Weighting and inference
- **Primary weighting:** equal symbol-night. Trade- and share-weighted are robustness only.
- **Inference unit:** symbol × date × time-bin cells; report effective N.
- **Clustering:** multiway (symbol, date), with a wild cluster bootstrap cross-check. Bootstrap procedure: TBD (W5 Stage N; frozen W6).
- **Multiplicity:** one primary estimand; every subgroup and horizon test is secondary or exploratory, reported with intervals.
- **Power / minimum detectable effect at the chosen N:** TBD (W4 power report).

## 6. Data quality and exclusions
- **Reason codes:** technical plan §11 plus `FEED_ANOMALY` and `PRE_SESSION`. Every stage publishes a ledger; no silent exclusions.
- **Quote-age, stale-quote and locked/crossed thresholds:** TBD (D-3, W4).
- **Post-trade quote source (`mbp-1` vs `bbo-1s`):** TBD (D-5, W4).
- **Structural-break handling:** TBD (D-2, W3; full sensitivities W6 Mon 26 Oct).
- **Known limitation:** Broken/Corrected Trade messages are not normalized by the vendor; busted prints stay in the data.

## 7. Replication (a diagnosis gate, not a hard gate)
- **Target:** Lim, SSRN 6610883, revision 21 Apr 2026.
- **Acceptance bands and divergence taxonomy:** TBD (D-8, W4). Signed before any replication run.
- **XNAS schema and matched RTH window:** TBD (D-6, W4). **XNAS auction-print handling:** TBD (D-10, W4).
- **Statuses:** MATCH, EXPLAINED_DIVERGENCE, MEASUREMENT_DEFECT, UNRESOLVED. Only MEASUREMENT_DEFECT blocks the freeze.

## 8. Placebos and pre-trends
- **Fake-event runner:** the rejection rate at 5% must be close to 5%. Placebo rules: TBD (W5; frozen W6).
- **A failed pre-trend** changes interpretation by these rules; it never adds a specification.

## 9. Contingencies (`preregistration/decision_rules.yaml`)
- **Seven numeric triggers with pre-written actions:** TBD (D-11, W6 Tue 27 Oct). They cover:
  - launch slip;
  - staggered launch;
  - BOATS rule change after freeze;
  - SIP implementation change;
  - Rule 611/610(e) final action;
  - load-bearing schema change;
  - primary feed unavailable.

## 10. Evidence, licensing, venue
- **Load-bearing evidence hashes:** generated from `evidence/manifest.jsonl` at freeze (W6).
- **Licensing status:** `config/licensing.yaml`. PENDING cells are allowed at freeze and recorded as such.
- **Prereg venue and embargo:** TBD (D-0, W1).
