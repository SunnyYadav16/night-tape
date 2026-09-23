---
title: "night-tape — Validated Technical Implementation Plan"
technical_plan_version: "2026-09-22-validated-r2.1"
source_project_plan: "night-tape v2.2 — 22 September 2026"
validated_as_of: "2026-09-22"
pre_event_freeze_target: "2026-10-15"
event_target_currently_monitored: "2026-12-06"
status: "IMPLEMENTATION SPEC — factual claims remain versioned, not assumed"
amendment_r2: "Public 23/5 tracker + AI change monitor added (§§23–25). Jev registered as a gated, non-blocking provider dependency."
jev_dependency_status: "WAITLISTED — self-reported by the account owner on 2026-09-22; disabled until gate G7 passes"
amendment_r2_1: "Review corrections to §§23–25: status taxonomy, atomic-change unit, evidence_refs[], holdout wording, broker scope wording, Jev status provenance."
---

> **r2 amendment (22 September 2026).** This revision adds a public-facing layer in front of the research pipeline: a point-in-time tracker of the 23/5 transition (§23), an AI change monitor that proposes registry updates from primary sources (§24), and an evaluation protocol for that monitor (§25).
>
> **Jev (TypeSafe AI) is a registered dependency, not an active component.** Access is waitlisted as of 22 September 2026, as reported by the account owner. Public statements that Jev is in early access say nothing about an individual account, so the owner's report is the operative source until access is granted. The monitor ships behind a provider interface with `manual` as the default provider. Jev is enabled only when access is granted **and** gate G7 passes. Nothing in the research freeze, the tracker launch or the monitor launch depends on Jev.
>
> Sections §§1–22 are unchanged except for scoped additions in §3, §5, §12, §13, §14, §19 and §20, each marked **[r2]**.
>
> **r2.1 corrections (22 September 2026)** after external review of §§23–25: separate `PROPOSED` from approved-not-effective; add `WITHDRAWN` and `ERRONEOUS_DISCLOSURE`; make the atomic rule change (not the document) the unit of proposal and evaluation; replace single-source fields with `evidence_refs[]`; restate the held-out set as prospective relative to a pinned model version; narrow the broker-scope wording; record Jev status provenance. Marked **[r2.1]**.

# night-tape — Validated Technical Implementation Plan

## 0. Freeze policy

This document supersedes the earlier night-tape technical-freeze draft. It incorporates only changes that survived a primary-source verification pass as of 22 September 2026.

**October 15 is the internal pre-event system and preregistration freeze.** It is not the date the December market-transition study can be completed. After the freeze, the system moves into monitoring/collection mode and the research design may change only through contingencies explicitly enumerated in the preregistration.

Two classes of updates remain possible after October 15:

1. **Factual market-structure updates** — enter through the versioned event/rule registry with source snapshot, hash, verification timestamp and effective timestamp. They must never be implemented as silent code edits.
2. **Pre-specified contingencies** — may activate an already-written analysis branch. New analysis branches are not added because post-event results are inconvenient.

Contract/licensing work is a **release gate**, not a blocker for private technical development or the October 15 research freeze. A freeze archive may record licensing status as `PENDING`; a public release may not.

---

# 1. What the verification pass changed

## 1.1 Decisions on the proposed corrections

| Proposed change | Decision | Verified technical-plan treatment |
|---|---|---|
| Restore Broker Priority to current BOATS mechanics | **REJECT** | Broker Priority appears in an older 2023 ATS-N, but a 2024 correcting amendment restored price-time matching and the current 2026 ATS-N describes price-time priority, no current Broker Priority, and no counter-party-selection designation. Preserve the historical rule only in amendment history. |
| Move 20 Jul / 10 Sep break diagnostics before power/universe freeze | **ACCEPT** | These affect displayed-book observability and security availability; run them in the pilot stage before selecting the usable pre-period and estimating power. |
| Split power analysis into wide/shallow then deep pull | **ACCEPT WITH CORRECTION** | The wide pull must include `tbbo`, because `bbo-1s` is interval-sampled and contains only the last sale for an interval; it cannot reproduce the primary trade-level effective-spread population. Use `tbbo` wide/shallow, optionally paired with `bbo-1s` for quote-state diagnostics. |
| Treat 15%→20% band wording as a possible widening / third break | **REJECT AFTER RESOLUTION** | The SEC-filed correcting amendment says 15% was an erroneous disclosure and the correct band was 20%. No 15→20 structural break is created from that text. |
| Delete the ~105-minute bona-fide-order accumulation/opening-auction analogy | **ACCEPT** | Current ATS-N says 6:15 p.m. is for **test** orders; bona-fide orders are accepted and matching starts at 8:00 p.m. |
| Leave “only limit day orders” as FAQ-sourced pending ATS-N | **REPLACE, NOT JUST FLAG** | Current ATS-N is available: BOATS supports one **LIMIT** order type, with `DAY` or `IOC`; orders may be `DISPLAYED` or `NON-DISPLAYED`; `POST-ONLY` is an instruction and is DAY-only; MARKET and PEGGED are unsupported. |
| Add odd-lot priority restrictions | **REJECT** | Current ATS-N says odd lots are handled like round lots and have the same priority treatment; mixed lots also receive the same priority treatment. |
| Add Rule 611 / 610(e) rescission as a contingency | **ACCEPT** | SEC File S7-2026-20, Release 34-105655, issued 11 Jun 2026, proposes rescinding Rule 611 and Rule 610(e); comment deadline was 17 Aug 2026. It remains a proposal in the checked SEC source. |
| Make crossed/locked QC regime-dependent | **ACCEPT, NARROWED** | Apply this contingency to exchange/SIP quote layers if Rule 610(e) changes. BOATS’ own current ATS-N says internally crossing orders execute rather than leaving a locked/crossed BOATS book. |
| Add Form ATS-N and amendment history to highest-tier sources | **ACCEPT** | For ATS mechanics, current Form ATS-N **plus the amendment chain** is the controlling source family. A single old filing is insufficient. |
| Move mechanism narratives out of load-bearing §§1–9 | **ACCEPT** | Core metrics and identification do not depend on venue stories. Mechanism hypotheses live in a clearly labeled non-load-bearing appendix. |
| Add error-history entry saying Broker Priority was correct and nearly deleted | **REJECT** | That would repeat the same amendment-history mistake. Correct entry: an older ATS-N contained Broker Priority, but later/current filings superseded that mechanic. |
| Add schedule slack / extend deadline | **PARTLY ACCEPT** | Keep October 15 as the internal freeze, but reduce what must be complete by then. Public-release/licensing polish and optional outcomes move to `release-required`. |
| State what October 15 means | **ACCEPT** | Internal pre-event research/system freeze unless an external deadline is later specified. |
| Split Make targets into freeze-required and release-required | **ACCEPT** | `permissions-check` is not a dependency of `freeze-required`; unresolved permissions are recorded. It is mandatory for `release-required`. |
| Draft preregistration from Sep 22 | **ACCEPT** | Prereg becomes the implementation spec from day one; only fields dependent on pilot/power may remain `TBD`. |
| Commit replication acceptance rules before first replication run | **ACCEPT** | Acceptance/divergence criteria get a dated signed commit before seeing replication output. |
| Replication as hard gate | **DEMOTE** | Replication is a diagnosis gate. It becomes a hard stop only when divergence reveals a data/metric/implementation defect. |
| Price Nasdaq RTH as a separate decision | **ACCEPT** | Estimate XNAS schema/window cost independently; if too expensive, shorten matched RTH window before substituting comparator. |
| Weekly post-freeze monitoring | **ACCEPT** | Weekly source-registry checks Oct 15→event. Do not assume another BOATS rule change will occur; simply monitor because changes have occurred. |
| Add “BOATS changes again” contingency | **ACCEPT** | Explicit prereg contingency with rule-version handling and trigger-to-action map. |
| Use “two venues ≥5 sessions apart” as stagger threshold | **DO NOT FREEZE 5 WITHOUT DESIGN JUSTIFICATION** | The prereg must contain a numeric rule before the event. Pilot/power work sets and signs that threshold no later than Oct 13. Five sessions is an example, not a verified optimum. |
| Add `load_bearing` to claim register | **ACCEPT** | Claims that alter endpoint, sample, timing, date logic or identification must be verified before freeze; context/citation claims may stay unresolved until publication. |
| Archive-on-fetch | **ACCEPT** | Snapshot every load-bearing primary source at retrieval time and hash it. Save PDF/HTML/raw response; WARC where practical. |
| Change §8.2 8–9pm identification | **NO CHANGE** | Current BOATS 8–4 schedule and planned exchange/SIP 9pm start preserve the factual timing asymmetry. Identification limits remain as already stated. |
| Change metrics / ES split / midpoint arithmetic | **NO CHANGE** | Arithmetic definitions survive. |
| Change stack or four-date contract | **NO CHANGE** | Retain. |

## 1.2 Additional verified issue discovered during this pass

The 2026 BOATS break list is incomplete if it begins at July 20.

Blue Ocean’s official service-alert history says:

- **1 March 2026:** passive orders outside the 20% reference band began being **rejected immediately**.
- **20 July 2026:** that handling changed: passive out-of-band orders began being **accepted into the order book as non-displayed, non-executable orders and excluded from market-data feeds until repriced inside the band**.
- **10 September 2026:** BOATS stopped halting symbols for Rule 301(b)(5) Fair Access reasons.

Therefore the market-structure registry must contain at least these three dated BOATS operational regimes, plus the Form ATS-N amendment history. Do not assume these are the only changes; enumerate every ATS-N amendment and service alert intersecting the eventual sample.

---

# 2. Primary-source findings that are load-bearing for implementation

## 2.1 Current BOATS matching and order handling

As of the current Form ATS-N reviewed for this document:

- Session: **8:00 p.m.–4:00 a.m. ET**.
- 6:15 p.m.: **test orders only**.
- Bona-fide order acceptance: **8:00 p.m.**
- Matching: continuous **price-time priority**.
- Order type: **LIMIT**.
- TIF: **DAY or IOC**.
- Direction: **DISPLAYED or NON-DISPLAYED**.
- `POST-ONLY`: supported as an instruction, with specified exceptions; DAY-only.
- `MARKET` and `PEGGED`: unsupported.
- Odd lots: handled like round lots with the same priority.
- Counter-party selection: current filing answers **No**.
- Internal marketable contra orders execute rather than leaving a locked/crossed BOATS book.
- Current reference-price band: **20%**, static for the session, using a last national-exchange print reported to the SIP as of **7:30 p.m. ET**.
- Passive orders outside the band may rest but are not executable and are not disseminated in BOATS market-data feeds under the current filing.

**Engineering consequence:** `rule_version` is mandatory on every observation. Do not use “Broker Priority,” “limit-day only,” “105-minute accumulation,” or “odd-lot priority restriction” in code comments, test fixtures, mechanism labels or preregistration.

## 2.2 Historical Broker Priority

The 2023 ATS-N did describe Broker Priority, including the all-transactions election and non-default behavior. That proves the user-supplied text was not fabricated.

It does **not** establish current mechanics.

A 2024 correcting amendment explicitly restored language describing price-time matching, and current filings have pure price-time language plus no counter-party-selection designation.

**Engineering consequence:** preserve Broker Priority only as an amendment-history fact if historical data from a period when it was operative is analyzed. Before applying a historical rule version to data, establish its actual effective interval from the amendment chain.

## 2.3 Band history

The SEC-filed November 2023 correcting amendment states that 15% had been **incorrectly disclosed** and the opening/session band was 20%.

Therefore:

```text
15% text != verified 15% operating regime
```

Do not create a band-width break from that disclosure.

Separate from band **width**, the handling of passive out-of-band orders did change in 2026 (March 1 and July 20) and must be versioned.

## 2.4 Databento implications for the pilot and power analysis

Databento documents:

- `tbbo`: every trade paired with BBO immediately before the effect of that trade.
- `side`: aggressor side may be Bid, Ask or None.
- price fields: fixed-point int64, 1 unit = `1e-9`.
- `bbo-1s`: interval-sampled BBO/last-sale data; no row if there is no trade or BBO update in an interval; trade/BBO fields may be forward-filled.
- `mbp-1`: event-space top-of-book/book updates.

Therefore the cheap wide power pull must use `tbbo` for the **primary effective-spread endpoint**. `bbo-1s` can supplement it for quote-state/staleness diagnostics but cannot replace the trade population.

## 2.5 Rule 611 / 610(e)

SEC S7-2026-20 proposes rescinding:

- Rule 611 — trade-through rule.
- Rule 610(e) — restrictions on locking/crossing quotations.

As of the checked SEC rule page this is still labeled **Proposed**.

Registry state:

```yaml
reg_nms_611_610e:
  status: proposed
  file_number: S7-2026-20
  release_number: 34-105655
  sec_issue_date: 2026-06-11
  comment_due: 2026-08-17
  recheck: weekly
```

If final action lands during the study window, it becomes a dated regulatory regime event. Crossed/locked quote QC for exchange/SIP benchmarks must be stratified by regime. Do not automatically apply that interpretation to BOATS’ own internal order book.

## 2.6 8 p.m. vs 9 p.m. timing asymmetry

Current primary/official material supports:

- BOATS: 8 p.m.–4 a.m.
- Planned SIP schedule: 9 p.m. Sunday–8 p.m. Friday, with 8–9 p.m. maintenance pauses Monday–Thursday.
- Nasdaq: December 6 target for a 9 p.m.–4 a.m. Night Session.
- NYSE Arca: December 6 target for a 9 p.m.–4 a.m. Overnight Session.

Therefore the technical implementation of an 8–9 p.m. indicator remains justified as a **timing definition**. Its causal interpretation remains limited to the infrastructure-package design already described in v2.2.

---

# 3. October 15 definition of done

By October 15, the project must have:

1. Current primary-source registry and archive for all **load-bearing** claims.
2. Reconciled BOATS ATS-N amendment chain over the candidate pre-period.
3. Synthetic fixture suite for temporal joins and metric arithmetic.
4. Real-data pilot validating `tbbo`, `mbp-1`, `bbo-1s`, side semantics, fixed-point scaling and quote-state reconstruction.
5. Early break diagnostics for known BOATS regime dates.
6. Wide/shallow `tbbo` variance/coverage pull and power report.
7. Frozen universe with deterministic selection code and hash.
8. Explicit XNAS RTH cost/window decision.
9. Production ingestion, normalization, ASOF and metric pipeline.
10. First-class QC/exclusion accounting.
11. Replication diagnostic run with precommitted acceptance/divergence rules.
12. Pre-event panel, placebo/fake-event pipeline and pre-trends.
13. Signed preregistration commit and research freeze tag.
14. Archive bundle and source hashes.
15. Licensing matrix whose unresolved cells are explicitly recorded.

Not required for October 15:

- final vendor legal approval for external publication;
- optional consolidated post-transition outcome;
- MOON/Bruce comparable feeds;
- polished public paper/site;
- final December results;
- **[r2]** the public tracker (§23), the AI change monitor (§24) or any non-manual triage provider;
- **[r2]** Jev access, integration or evaluation. Jev is a gated dependency (§24.5, gate G7) and is never on the freeze critical path.

**[r2]** The tracker may launch before October 15 because it publishes only facts already verified for the research registry (Stage B). It adds visibility, not freeze scope.

---

# 4. Architecture

```text
Primary sources ───────────────┐
                              │
ATS-N amendment chain ────────┤
                              v
                    market_structure_registry
                              │
                              v
Databento / FINRA ──> immutable raw data
                              │
                              v
                    canonical normalization
                              │
                ┌─────────────┴──────────────┐
                v                            v
          trade events                 quote state
           (`tbbo`)                    (`mbp-1`)
                │                            │
                └────────── ASOF/state ─────┘
                              │
                              v
                     ES / RS / PI / depth
                              │
                              v
                    QC + exclusion ledger
                              │
                              v
               symbol × date × time-bin panel
                              │
          ┌───────────────────┼──────────────────┐
          v                   v                  v
   replication         pre-event tests      event study
```

Design rule:

> **Facts live in registries/configuration. Computation lives in code. Historical facts are versioned by effective interval.**

Never hard-code December 6, venue launch dates, BOATS rule changes, Rule 611 status or session-date logic in Python.

---

# 5. Repository layout

```text
night-tape/
├── config/
│   ├── datasets.yaml
│   ├── sessions.yaml
│   ├── venues.yaml
│   ├── metrics.yaml
│   ├── analysis.yaml
│   ├── universe.yaml
│   ├── licensing.yaml
│   ├── monitoring.yaml
│   ├── providers.yaml          # [r2] triage provider flags; Jev disabled
│   └── tracker.yaml            # [r2] tracked entities, public fields
│
├── contracts/
│   ├── trade.schema.json
│   ├── quote.schema.json
│   ├── event_registry.schema.json
│   ├── claim_registry.schema.json
│   ├── tracker_entry.schema.json      # [r2]
│   └── triage_proposal.schema.json    # [r2]
│
├── evidence/
│   ├── sec/
│   │   ├── ats-n/
│   │   ├── reg-nms/
│   │   └── exchanges/
│   ├── sip/
│   ├── finra/
│   ├── nscc/
│   ├── vendors/
│   ├── papers/
│   └── manifest.jsonl
│
├── data/
│   ├── raw/
│   ├── normalized/
│   ├── panels/
│   ├── pilot/
│   └── manifests/
│
├── src/night_tape/
│   ├── evidence/
│   ├── ingest/
│   ├── normalize/
│   ├── sessions/
│   ├── books/
│   ├── joins/
│   ├── metrics/
│   ├── qc/
│   ├── panels/
│   ├── stats/
│   ├── replication/
│   ├── reports/
│   ├── tracker/                # [r2] registry → static site renderer
│   └── monitor/                # [r2] AI change monitor
│       ├── fetch.py            #   archive-on-fetch (reuses evidence/)
│       ├── segment.py          #   document → addressable spans
│       ├── prefilter.py        #   deterministic candidate-span selection
│       ├── parse.py            #   value extraction from a selected span
│       ├── validate.py         #   citation + hash + supersession checks
│       └── providers/
│           ├── base.py         #   TriageProvider interface
│           ├── manual.py       #   default: human labeling queue
│           ├── structured_llm.py  # optional interim provider
│           └── jev.py          #   stub; disabled until G7
│
├── tests/
│   ├── fixtures/
│   ├── unit/
│   ├── integration/
│   └── golden/
│
├── evals/                      # [r2]
│   └── triage/
│       ├── protocol.md         #   signed before any provider run
│       ├── labeled/            #   frozen historical set + hash
│       ├── heldout/            #   documents first published after 2026-09-22
│       └── reports/
│
├── site/                       # [r2] generated static tracker; never hand-edited
├── benchmarks/
├── preregistration/
│   ├── prereg.md
│   ├── decision_rules.yaml
│   └── acceptance_bands.yaml
├── reports/
├── docs/
├── scripts/
├── Makefile
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# 6. Archive-on-fetch and claim registry

## 6.1 Evidence manifest

Every load-bearing source fetch writes:

```json
{
  "source_id": "boats-atsn-current",
  "source_class": "SEC_FORM_ATS_N",
  "canonical_url": "...",
  "retrieved_at_utc": "...",
  "published_or_filed_at": "...",
  "edgar_accession": "...",
  "local_path": "evidence/sec/ats-n/...",
  "sha256": "...",
  "content_type": "text/html",
  "supersedes": "...",
  "notes": "..."
}
```

Store the fetched representation itself:

- PDF when the regulator/vendor publishes a PDF;
- HTML/XML/raw response when that is the authoritative representation;
- WARC when practical;
- always a SHA-256.

Do not rely on a bookmarked URL as the archive.

## 6.2 Claim register

Minimum columns:

```text
claim_id
claim_text
claim_type
load_bearing
affects
status
source_class
source_id
source_version_or_accession
effective_from
effective_to
retrieved_at
sha256
recheck_trigger
notes
```

Allowed `affects` values:

```text
primary_endpoint
identification
sample
session_logic
date_logic
metric_semantics
data_quality
cost
publication
context_only
```

Freeze rule:

- `load_bearing=true` claims must be `VERIFIED` or explicitly converted into a preregistered contingency before Oct 15.
- `context_only` claims may remain `UNVERIFIED` in working notes but must not be stated as fact in the preregistration.
- `publication` claims may be `PENDING` at research freeze but block public release.

---

# 7. Four-date and rule-version contract

Each observation must carry:

```text
wall_clock_execution_date
venue_trade_date
finra_reporting_date
nscc_clearing_business_date
session_id
rule_version
```

Never collapse these into a generic `date`.

Rule-version examples include, at minimum:

```text
BOATS_PRE_2026_03_01
BOATS_2026_03_01_TO_2026_07_19
BOATS_2026_07_20_TO_2026_09_09
BOATS_POST_2026_09_10
```

These labels are **provisional technical names**, not claims that no other amendments occurred. The ATS-N/service-alert history scan may split them further before freeze.

---

# 8. Canonical schemas

## 8.1 Trade

```text
symbol
venue
instrument_id
ts_event
ts_recv
sequence
price_int
size
side_raw
aggressor_direction
bid_px_pre_int
ask_px_pre_int
wall_clock_execution_date
venue_trade_date
finra_reporting_date
clearing_business_date
session_id
rule_version
source_dataset
source_schema
manifest_id
```

## 8.2 Quote state

```text
symbol
venue
instrument_id
ts_event
ts_recv
sequence
bid_px_int
ask_px_int
bid_sz
ask_sz
midpoint_x2_int
quote_age_ns
book_state
session_id
rule_version
source_dataset
source_schema
manifest_id
```

Use fixed-point integers. Exact midpoint test:

```python
2 * trade_price_int == bid_px_int + ask_px_int
```

Do not use float equality.

For within-venue event ordering use:

```text
(ts_event, sequence)
```

not timestamp alone.

---

# 9. Metrics contract

With `D = +1` for buyer-initiated and `D = -1` for seller-initiated:

```text
QuotedSpread = Ask - Bid

ES = 2 * D * (P - M_t)

RS_tau = 2 * D * (P - M_t+tau)

PI_tau = 2 * D * (M_t+tau - M_t)

ES = RS_tau + PI_tau
```

Horizons:

```text
10s  = primary
60s  = robustness
300s = robustness
```

Primary reporting scale:

```text
basis points
```

Secondary:

```text
cents/share
```

Populations:

- `ES_all`: includes exact-midpoint executions at zero ES even when direction is unresolved.
- `ES_decomp`: common signed sample with valid horizon state.
- `RS` / `PI`: signed common sample only.

Do not infer “midpoint mechanism” from an exact midpoint execution.

---

# 10. Quote-state semantics

Canonical logic:

```text
trade at T
  ├─ execution-time pre-trade BBO from TBBO
  └─ quote state at T+τ from event-driven quote source
          ├─ τ = 10s
          ├─ τ = 60s
          └─ τ = 300s
```

`mbp-1` is the primary event-driven quote-state source for the 10-second result if cost is acceptable.

`bbo-1s` is a cost/sampling sensitivity source. It is **not** a dense second-by-second table.

Every horizon lookup stores:

```text
matched_quote_timestamp
quote_age_ns
source_schema
lookup_direction
sequence_used
```

DuckDB owns the canonical ASOF implementation. If Polars is used for transforms, it must not become an independent hidden definition of the research join.

---

# 11. QC and exclusion ledger

Never hide exclusions in `WHERE` clauses.

Reason codes:

```text
VALID
ONE_SIDED
LOCKED
CROSSED
UNKNOWN_SIDE
NO_EXECUTION_BBO
NO_FUTURE_QUOTE
SESSION_BOUNDARY
HALT
CORPORATE_ACTION
STALE_QUOTE
INVALID_FIXED_POINT
SEQUENCE_GAP
OUTSIDE_RULE_VERSION
UNKNOWN_SESSION_DATE
```

Outputs for every stage:

```text
symbol
trade_date
hour
rule_version
reason
trade_count
share_volume
notional
percent_of_input
```

Crossed/locked handling must distinguish:

```text
boats_internal_book
exchange_direct_book
sip_or_consolidated_book
```

If Rule 610(e) changes, update the regulatory-regime label for exchange/SIP diagnostics. Do not silently change exclusion thresholds.

---

# 12. Revised implementation order to October 15

**[r2]** Tracker/monitor tracks T0–T4 (§23.6) run in parallel with Stages A–R. They are keyed to stage completion, not calendar dates. None of them is a prerequisite of Stage R or of `freeze-required`. If time is short, T-tracks slip; Stages A–R do not.

## Stage A — Sep 22–23: repository, prereg skeleton and load-bearing claim register

Deliver:

- repository structure;
- config contracts;
- `preregistration/prereg.md` skeleton;
- claim registry with `load_bearing`;
- initial event/rule registry;
- evidence manifest tooling;
- source-archive command.

Preregistration is now the working specification, not a final two-day writing task.

Allowed `TBD` fields at this stage:

- N/universe hash;
- exact primary/sensitivity event-window lengths;
- numeric stagger-activation rule;
- replication acceptance bands;
- quote-age thresholds;
- exact XNAS matched-RTH window.

**Blocker:** no final session/date classifier may be written until the load-bearing session/trade-date sources have been archived and reconciled.

---

## Stage B — Sep 22–26: ATS-N amendment-chain and primary-source fact freeze

Build the BOATS amendment timeline, not just a “current rules” snapshot.

Mandatory verified entries:

- old Broker Priority filing;
- 2024 correcting amendment returning price-time wording;
- 2025 amendments introducing IOC/display/non-display directions;
- 2026 price-band handling/service alerts;
- current Post-Only amendment;
- Fair Access handling change;
- current Form ATS-N.

Also archive:

- SIP schedule source;
- Nasdaq/Arca current implementation notices;
- Rule 611/610(e) proposal;
- NSCC/date-logic sources used by the pipeline;
- current Databento schema docs.

**Blocker:** any load-bearing conflict between two primary sources must be resolved by amendment/effective-date history, not by choosing the newer-looking sentence.

---

## Stage C — Sep 22 onward: licensing in parallel

Maintain:

```text
output_type × OCEA permission × XNAS permission × attribution × release_status
```

Do not block private research freeze on vendor legal response.

Do block public release if permission for an intended output is unknown.

---

## Stage D — Sep 24–26: synthetic fixtures

Required fixtures:

```text
buyer trade
seller trade
exact-midpoint known-side
exact-midpoint side=None
side=None away from midpoint
no quote update for >10s
stale quote
one-sided quote
locked quote
crossed quote
same timestamp / different sequence
8pm boundary
midnight boundary
4am boundary
halt state
missing future midpoint
rule-version boundary
```

Hard assertions include:

```text
ES == RS + PI
```

on the common signed sample and zero future leakage.

**Hard gate:** real-data scale-up does not proceed if canonical fixtures fail.

---

## Stage E — Sep 25–27: pilot + early structural-break diagnostics

Pilot sample:

- small active/sparse mix;
- `tbbo`;
- `mbp-1`;
- `bbo-1s`;
- small XNAS sample.

Measure:

```text
side=None frequency
midpoint frequency
P(side=None | midpoint)
P(midpoint | side=None)
one-sided rate
locked/crossed rate
quote-age distribution
10/60/300s future-state coverage
mbp-1 vs bbo-1s lookup disagreement
rows / bytes / cost per symbol-night
```

### Break diagnostics move here

Evaluate known regime boundaries **before** power/universe freeze:

- 1 Mar 2026 — passive out-of-band rejection begins.
- 20 Jul 2026 — passive out-of-band acceptance as non-displayed begins.
- 10 Sep 2026 — Fair Access halt practice changes.
- any additional operative ATS-N amendment effective inside candidate pre-period.

Diagnostics must include:

```text
primary ES mean/distribution
symbol-night residual variance
quote age
displayed spread/depth
trade/volume coverage
exclusion rates
symbol availability
```

The purpose is not to “find significant breaks” after trying many specifications. It is to determine whether the power model and primary pre-period cross incompatible documented rule regimes.

**Decision output:** a signed `preperiod-regimes.yaml` describing which periods are primary, sensitivity-only or excluded and why.

---

## Stage F — Sep 26–29: wide/shallow variance pull, capacity, XNAS pricing and power

### F1. Wide/shallow pull

Do **not** use `bbo-1s` alone.

Default planning envelope:

```text
~100–150 candidate symbols
~15–20 nights
tbbo required
bbo-1s optional companion
```

Actual size is chosen from the vendor estimator before purchase.

Purpose:

- primary effective-spread variance;
- symbol-night coverage;
- missing-side rate;
- rough liquidity strata;
- residual dependence needed for power.

### F2. XNAS RTH decision

Price separately:

```text
dataset
schema
symbols
matched days
intraday window
estimated bytes
estimated dollars
```

Commit the decision.

If XNAS cost is excessive:

1. shorten matched RTH window;
2. reduce robustness pulls;
3. only then reconsider optional scope.

Do not silently swap IEX for the preregistered comparator.

### F3. Capacity benchmark

Run a representative 25–50 GB scan/group/ASOF benchmark and record:

```text
machine
CPU
RAM
disk
DuckDB version
elapsed time
peak memory
output size
```

### F4. Power

Power uses the wide `tbbo` panel after break-regime decision.

Candidate N values may include:

```text
30
50
75
100
```

but are not inherited automatically from Lim.

**Gate:** universe freeze happens only after power + cost + coverage are jointly acceptable.

---

## Stage G — Sep 28–30: freeze universe and replication rules

Freeze:

```text
universe.csv
universe.sha256
selection_method.md
sampling_frame.csv
coverage_report.md
```

Selection uses pre-treatment data only.

Before the first replication run, commit:

```text
preregistration/acceptance_bands.yaml
preregistration/divergence_taxonomy.yaml
```

with a signed, dated commit.

Divergence taxonomy:

```text
SAMPLE_MISMATCH
DATE_RANGE_MISMATCH
METRIC_DEFINITION
TRADE_SIGNING
QUOTE_STATE_SEMANTICS
SESSION_DEFINITION
VENDOR_DATA_REVISION
PAPER_AMBIGUITY
IMPLEMENTATION_BUG
UNEXPLAINED
```

Replication does not block the project merely because estimates differ. It blocks freeze only if diagnosis reveals unresolved implementation/measurement defects.

---

## Stage H — Sep 29–Oct 3: production ingestion

Requirements:

- resumable;
- idempotent;
- checksummed;
- request-manifested;
- partitioned Parquet;
- no silent overwrite.

Partition example:

```text
dataset=OCEA.MEMOIR/
  schema=tbbo/
    date=YYYY-MM-DD/
      symbol=XYZ/
```

Manifest example:

```json
{
  "vendor": "databento",
  "dataset": "OCEA.MEMOIR",
  "schema": "tbbo",
  "symbol": "XYZ",
  "start": "...",
  "end": "...",
  "request_hash": "...",
  "file_sha256": "...",
  "downloaded_at": "...",
  "sdk_version": "..."
}
```

---

## Stage I — Oct 2–5: canonical normalization

Build canonical trade/quote schemas.

Required checks:

- fixed-point units;
- timestamp ordering;
- sequence monotonicity/gaps;
- side enum mapping;
- session classification;
- rule-version assignment;
- all four date fields.

Fail closed on schema drift.

---

## Stage J — Oct 4–7: quote-state + ASOF engine

Implement:

```text
M_t
M_t+10
M_t+60
M_t+300
```

Use event time plus sequence ordering.

Record quote age for every lookup.

Golden tests compare expected hand-calculated state with DuckDB results.

**Hard gate:** no metric/report code is accepted until future leakage and sparse-state fixtures pass.

---

## Stage K — Oct 6–8: metric engine

Implement one authoritative module for:

```text
quoted spread
depth
ES
RS_10 / PI_10
RS_60 / PI_60
RS_300 / PI_300
mark-to-open (separate)
```

Output bps + cents/share.

Preserve `ES_all` and `ES_decomp`.

---

## Stage L — Oct 7–9: QC/exclusion dashboard

Produce exclusion and coverage reports by:

```text
symbol
night
hour
rule_version
reason
```

Thresholds set using pilot distributions and then frozen.

If Rule 610(e) status changes, use regulatory-regime labels for exchange/SIP crossed/locked diagnostics; do not retroactively redefine BOATS QC.

---

## Stage M — Oct 8–10: replication diagnostic

Run Lim replication only after the signed acceptance/divergence commit exists.

Outputs:

```text
paper estimate
our estimate
difference
precommitted band
diagnosis code
status
```

Possible statuses:

```text
MATCH
EXPLAINED_DIVERGENCE
MEASUREMENT_DEFECT
UNRESOLVED
```

Only `MEASUREMENT_DEFECT` is automatically a hard freeze blocker.

`UNRESOLVED` requires a documented bounded investigation and explicit prereg disclosure; Lim is a validation target, not the object of the study.

---

## Stage N — Oct 9–11: statistical layer and fake-event runner

Inference unit:

```text
symbol × date × time-bin
```

Primary:

```text
BOATS effective spread, bps
equal symbol-night weighting
multiway cluster: symbol + date
```

Secondary:

```text
10-second PI
```

Robustness:

```text
60s
300s
trade-weighted
share-weighted
bootstrap cross-check
```

Implement the 8–9 p.m. vs 9 p.m.–4 a.m. timing design under fake historical event dates.

Variable names must not encode a competition-specific causal story. Prefer:

```text
post_x_exchange_window
```

not:

```text
competition_effect
```

---

## Stage O — Oct 10–13: full break sensitivities, pre-event panel and pre-trends

Re-run the early break logic on the fuller sample.

Generate:

```text
coverage
ES
PI
quote age
side=None
exclusions
rule-version mix
8–9 vs 9–4 gap
pre-trends
placebos
```

A failure of pre-trend assumptions changes interpretation according to preregistered rules; it does not invite a new hand-picked specification.

---

## Stage P — by Oct 13: finalize contingency decision rules

Must contain numeric/operational triggers for:

1. launch-date slip;
2. genuinely staggered launches;
3. BOATS rule change after freeze;
4. SIP implementation change;
5. Rule 611/610(e) final action;
6. load-bearing data-schema change;
7. primary feed unavailable.

### Stagger threshold

A numeric activation rule must be committed before the event.

Do **not** adopt “≥5 sessions” merely because it was suggested in review. Use pilot/power/design review to choose and sign:

```yaml
staggered_design:
  minimum_separation_trading_sessions: TBD_BEFORE_2026_10_13
  estimator_branch:
    - sun_abraham
    - callaway_santanna
```

Once signed, it cannot be altered after observing launch outcomes.

---

## Stage Q — Oct 13–14: prereg completion

Freeze:

| Field | Required |
|---|---|
| primary endpoint | yes |
| horizon | yes |
| universe + hash | yes |
| primary weighting | yes |
| event windows | yes |
| quote-age rules | yes |
| exclusions | yes |
| clustering | yes |
| bootstrap procedure | yes |
| structural-break handling | yes |
| 8–9pm specification | yes |
| placebo rules | yes |
| stagger trigger | yes |
| BOATS-rule-change trigger | yes |
| replication diagnostics | yes |
| load-bearing evidence hashes | yes |

---

## Stage R — Oct 15: internal pre-event freeze

Tag:

```text
v1.0-preregistered
```

Archive:

```text
Git commit
signed tag
uv.lock
Docker digest
universe hash
analysis config
market-structure registry
claim register
source snapshots + hashes
test results
pilot report
break report
power report
XNAS cost decision
replication diagnostic
pre-event QC report
pre-trend/placebo report
preregistration
licensing-status matrix
```

---

# 13. Make targets

## 13.1 Freeze-required

```make
freeze-required:
	$(MAKE) evidence-load-bearing
	$(MAKE) source-archive-verify
	$(MAKE) test
	$(MAKE) pilot-report
	$(MAKE) break-report
	$(MAKE) power-report
	$(MAKE) universe-verify
	$(MAKE) xnas-cost-decision
	$(MAKE) manifest-verify
	$(MAKE) qc-report
	$(MAKE) replication-diagnostic
	$(MAKE) preevent-report
	$(MAKE) prereg-check
	$(MAKE) freeze-archive
```

`freeze-required` may pass with:

```text
licensing_status = PENDING
```

provided the unresolved permissions are explicitly recorded and no public restricted data is released.

## 13.2 Release-required

```make
release-required:
	$(MAKE) freeze-required
	$(MAKE) permissions-check
	$(MAKE) attribution-check
	$(MAKE) public-data-scan
	$(MAKE) release-docs
	$(MAKE) release-bundle
```

## 13.3 Archive

`make archive` must archive the **state of knowledge**, not pretend unresolved legal/licensing items are resolved.

## 13.4 [r2] Tracker and monitor targets

```make
tracker-validate:        # gate G6 on every entry (§20)
	python -m night_tape.tracker.validate

tracker-build: tracker-validate
	python -m night_tape.tracker.render --out site/

tracker-publish: tracker-build
	python -m night_tape.tracker.publish --no-market-data

monitor-run:             # fetch → archive → segment → prefilter → propose
	python -m night_tape.monitor.run   # provider read from config/providers.yaml

triage-eval:             # score a provider on the frozen labeled + held-out sets
	python -m night_tape.monitor.eval --protocol evals/triage/protocol.md

jev-activation-check:    # gate G7; exits non-zero while Jev is WAITLISTED
	python -m night_tape.monitor.providers.jev --check-gate
```

Rules:

- **None of these targets is a prerequisite of `freeze-required` or `release-required`.**
- `tracker-publish` must refuse any entry derived from Databento or other licensed market data. The tracker publishes public primary-source facts only; licensed-data outputs stay behind gate G5.
- `jev-activation-check` is expected to **fail** today. That is the correct state, not a broken build.

---

# 14. Post-freeze monitoring: Oct 15 → event

Run once per week and additionally after any known filing/service alert.

Check:

```text
BOATS Form ATS-N filings/amendments
Blue Ocean service alerts
NYSE Arca implementation notices
Nasdaq implementation alerts
EDGX / 24X / MEMX go-live updates
SIP implementation/testing notices
Rule 611 / 610(e) docket status
LULD plan changes
NSCC/clearing notices affecting date logic
Databento schema/dataset notices
```

Trigger-to-action map:

| Trigger | Action |
|---|---|
| BOATS mechanics change | archive source; new `rule_version`; run pre-specified break diagnostics; do not alter metric formulas |
| BOATS session hours change | update event registry; re-run session-boundary tests; activate prereg contingency |
| exchange/SIP go-live moves | update actual go-live registry; select precommitted event-date branch |
| Rule 611/610(e) final action | new regulatory regime; stratify relevant exchange/SIP QC; preserve BOATS-internal logic |
| SIP hours change | re-evaluate factual 8–9/9–4 timing indicator under prereg contingency |
| vendor schema changes | pin old version if possible; otherwise schema migration + golden-test proof before new data |
| licensing answer received | update release matrix only; do not change research results |

No trigger permits changing the primary outcome because the observed effect is inconvenient.

**[r2]** Once the change monitor (§24) is running, it executes this checklist on schedule. The checklist above remains the authoritative source list, and the trigger-to-action map is unchanged. A monitor proposal is never itself a trigger: a trigger fires only when a human-approved registry entry exists. Which provider is active (manual, interim LLM or Jev) never changes what a trigger does.

---

# 15. Source hierarchy after verification

## Highest tier — ATS mechanics

1. Current **Form ATS-N**.
2. Full Form ATS-N amendment history and redlines.
3. ATS official service alerts for effective operational dates.
4. FAQ only when the above do not answer the question; mark FAQ-only claims as such.

## Highest tier — exchange/regulatory structure

1. SEC orders / NMS-plan amendments / operative rule filings.
2. Current exchange rulebook.
3. Official implementation/trader notices.
4. FAQ.
5. Secondary reporting only for discovery.

## Technical schemas

1. Databento current schema documentation.
2. Dataset-specific vendor documentation.
3. Empirical real-data pilot for venue-specific behavior that generic docs do not establish.

---

# 16. Mechanism appendix policy

The core implementation and preregistration may state verified mechanics.

It may not state an unverified explanation for *why* spreads/impacts change as though the explanation were established.

Examples that belong in a non-load-bearing appendix unless directly identified:

```text
liquidity-provider response
internalization mechanism
customer geographic mix causing a result
specific venue competition channel
broker-priority explanation
```

The metrics remain arithmetic. Mechanism stories do not define them.

---

# 17. Updated error-history entry

Add this entry to the project’s internal error log:

> **2026-09-22 technical verification:** an older 2023 BOATS Form ATS-N contained a Broker Priority election, but treating that filing as current would have been another version-control error. A 2024 correcting amendment and the current 2026 ATS-N describe price-time priority, and the current filing does not support counter-party selection. The resolution is not “the old claim was right”; it is that ATS mechanics require the current Form ATS-N **and its amendment history**. The same review showed the historical 15% price-band text was explicitly corrected as an erroneous disclosure, not a verified 15% operating regime.

---

# 18. Primary-source register used for this validation

These are source identifiers for the technical freeze. Archive them locally before Oct 15.

1. **Current BOATS Form ATS-N / Material Amendment (2026)** — SEC accession `0000902664-26-003296`; current order types, price-time priority, hours, price bands, odd lots, counter-party-selection answer, Post-Only.
   - https://www.sec.gov/Archives/edgar/data/1795131/000090266426003296/xslATS-N_X01/primary_doc.xml

2. **BOATS Correcting Amendment (2024)** — restores price-time-priority wording and order-type disclosures; no Broker Priority in the restored mechanics.
   - https://www.sec.gov/Archives/edgar/data/1795131/000179513124000022/xslATS-N_X01/primary_doc.xml

3. **Historical BOATS ATS-N (2023)** — contains Broker Priority election text; historical only unless its effective interval is established.
   - https://www.sec.gov/Archives/edgar/data/1795131/000153949723000091/xslATS-N_X01/primary_doc.xml

4. **BOATS 2023 correcting redline** — states the previously disclosed 15% band was incorrect and corrects it to 20%.
   - https://www.sec.gov/Archives/edgar/data/1795131/000153949723001938/ex3redline.pdf

5. **Blue Ocean ATS Service Alerts** — March 1 passive-band rejection, July 20 non-displayed acceptance, September 10 Fair Access halt change.
   - https://blueocean-tech.io/blue-ocean-ats-service-status/

6. **SEC S7-2026-20 / Release 34-105655** — proposed rescission of Rule 611 and Rule 610(e).
   - https://www.sec.gov/rules-regulations/2026/06/s7-2026-20

7. **Databento TBBO documentation** — every trade + pre-effect BBO, side and fixed-point price semantics.
   - https://databento.com/docs/schemas-and-data-formats/tbbo

8. **Databento BBO documentation** — interval-space semantics and non-density of `bbo-1s`.
   - https://databento.com/docs/schemas-and-data-formats/bbo

9. **Databento MBP-1 documentation** — event-driven top-of-book fields.
   - https://databento.com/docs/schemas-and-data-formats/mbp-1

10. **SEC Staff Memorandum on 24-Hour Trading, Sep 2026** — planned SIP schedule and 8–9 p.m. maintenance window.
    - https://www.sec.gov/files/2026_TM_Overnight_Trading_Roundtable_Memo_090926.pdf

11. **NYSE Arca SR-NYSEARCA-2026-53 / Release 34-105532** — overnight session framework.
    - https://www.sec.gov/rules-regulations/self-regulatory-organization-rulemaking/sr-nysearca-2026-53

12. **Nasdaq Release 34-105199** — approved 23-hour framework.
    - https://www.sec.gov/rule-release/34-105199

13. **Nasdaq Equity Trader Alert 2026-46** — December 6 implementation alert and 9 p.m.–4 a.m. Night Session.
    - https://www.nasdaqtrader.com/TraderNews.aspx?id=ETA2026-46

---

# 19. Final dependency chain

```text
PREREG SKELETON + CLAIM REGISTER
                ↓
CURRENT SOURCE + AMENDMENT-HISTORY ARCHIVE
                ↓
SYNTHETIC TEMPORAL/METRIC TESTS
                ↓
SMALL REAL-DATA PILOT
                ↓
EARLY BOATS BREAK DIAGNOSTICS
                ↓
WIDE TBBO VARIANCE/COVERAGE PULL
                ↓
POWER + COST + XNAS DECISION
                ↓
UNIVERSE FREEZE
                ↓
SIGNED REPLICATION ACCEPTANCE RULES
                ↓
PRODUCTION INGESTION
                ↓
NORMALIZATION
                ↓
QUOTE-STATE / ASOF ENGINE
                ↓
METRIC ENGINE
                ↓
QC / EXCLUSION ACCOUNTING
                ↓
REPLICATION DIAGNOSIS
                ↓
STATISTICS / PLACEBOS
                ↓
PRE-EVENT PANEL + PRE-TRENDS
                ↓
NUMERIC CONTINGENCY RULES
                ↓
PREREGISTRATION FINAL
                ↓
OCTOBER 15 INTERNAL FREEZE
                ↓
WEEKLY MARKET-STRUCTURE MONITORING
                ↓
DECEMBER EVENT / ACTUAL GO-LIVE
```

**[r2] Parallel branch — tracker and monitor (off the critical path):**

```text
Stage A claim register ──► T0 tracker entry schema (same registry)
                                   │
Stage B verified facts ──► T1 PUBLIC TRACKER LAUNCH (manual provider)
                                   │
                           T2 LABELED EVAL UNIVERSE (hand-labeled, hashed)
                                   │
                           T3 CHANGE MONITOR ON (manual → optional interim LLM, via G7)
                                   │
                  ┌────────────────┴────────────────┐
                  │                                 │
      Jev WAITLISTED: stay on T3          Jev ACCESS GRANTED
      (no action, no blocker)                       │
                                           T4 G7 ACTIVATION GATE
                                                    │
                                   pass ──► active_provider: jev
                                   fail ──► status REJECTED, keep fallback
```

The branch reads from the research registry and writes to it only through human approval. It never writes into §§4–11 computation.

---

# 20. Gate definitions

## G0 — load-bearing fact gate

Blocks **freeze**, not ordinary coding.

Must verify current BOATS/session/feed facts and archive them. Historical mechanics must be versioned by effective interval.

## G1 — data semantics gate

Blocks full pull/metric freeze if:

- fixed-point handling fails;
- quote-state reconstruction leaks future information;
- `tbbo` pre-trade state is misread;
- sequence/timestamp ties are unresolved;
- real-data pilot contradicts assumed side/state semantics.

## G2 — regime/power/universe gate

Known BOATS rule changes are diagnosed before variance estimation and universe freeze.

Blocks universe freeze if the power model uses an incompatible or undefined pre-period.

## G3 — cost/capacity gate

Blocks full backfill if projected storage/cost/runtime is outside budget/capacity.

XNAS RTH is priced separately.

## G4 — replication diagnosis gate

Not automatically blocking.

Becomes blocking only when divergence reveals a data, metric, session, signing or implementation defect that also threatens the primary study.

## G5 — public-release permission gate

Does not block October 15 private research freeze.

Blocks external release of any output class whose rights remain unknown.

## G6 — [r2] tracker publication gate

Does not block the research freeze.

Blocks publication of any single tracker entry unless:

- **[r2.1]** every reference in `evidence_refs[]` points to a source archived with a SHA-256 in `evidence/manifest.jsonl`;
- every referenced span ID exists in its archived snapshot at the recorded offsets;
- every published component (value, each non-null date, status) is covered by at least one reference whose `supports[]` includes it, and the supported value appears in that span or was entered by a human who recorded the span;
- a status from §23.3 is assigned (never `PENDING_VERIFICATION` on a public entry);
- a human approval is recorded with timestamp.

Also blocks any entry derived from licensed market data. Those outputs belong to G5.

## G7 — [r2] triage provider activation gate (Jev is the registered case)

Does not block the research freeze, the tracker or the monitor. The `manual` provider never needs G7.

Blocks setting `active_provider` to any non-manual provider until the §24.5 checklist passes. For Jev, the gate cannot open while `jev.status = WAITLISTED`.

---

# 21. What remains deliberately unchanged

The verification pass found no reason to redesign:

- Python + Databento ingestion;
- Parquet partitioning;
- DuckDB canonical ASOF layer;
- Polars for transforms/QC;
- fixed-point arithmetic;
- four-date contract;
- `ES_all` / `ES_decomp`;
- 10s primary horizon;
- quote-age tracking;
- exclusion ledger;
- symbol×date×time-bin inference;
- 8–9 p.m. factual timing indicator.

These stay frozen unless a future load-bearing source change activates a preregistered contingency.

---

# 22. Final freeze command

```bash
make freeze-required

git status --porcelain
# must contain no unintended changes

git commit -S -m "Freeze night-tape pre-event research protocol"
git tag -s v1.0-preregistered -m "night-tape pre-event freeze — 2026-10-15"
```

A later public release requires:

```bash
make release-required
```

The two commands intentionally represent different gates.

---

# 23. [r2] Public 23/5 tracker

## 23.1 Purpose

A public, point-in-time tracker of the rules governing the US transition to 23/5 equities trading, built only from versioned primary sources. It answers three questions for each tracked entity:

1. **What is in force now?**
2. **What was in force on date X?**
3. **What changed, when, and per which filing?**

It is the §8.3 market-structure event registry rendered publicly. There is **one registry**, not a research copy and a public copy. Entries flagged `load_bearing` feed the research pipeline exactly as before; post-freeze changes still enter only through the §0 channel.

Call it a **tracker**, never a "source of truth" or "official" record. Every page carries the not-investment-or-legal-advice notice from the project plan.

## 23.2 v1 scope

Tracked entities:

```text
NASDAQ        NYSE_ARCA     CBOE_EDGX     24X       MEMX
BOATS         SIP           LULD          NSCC
```

Tracked fields per entity, where applicable:

```text
session_hours          go_live_target        go_live_actual
order_types            time_in_force         trade_date_rule
price_band_rule        halt_rule             clearing_hours
market_data_status     reg_status            (Reg NMS 611/610(e), proposals)
```

**Out of scope for v1: broker documentation.** **[r2.1]** Broker-dealers do have regulatory filing and disclosure obligations (for example Form BD and Rule 606 routing reports), but their customer-facing overnight order policies have no standardized public rule-filing framework comparable to exchange rule filings or Form ATS-N. Those policies can change without a filed, versioned record, and there are many brokers. If added later, broker facts go in a separate, clearly labeled lower tier, never mixed with venue or infrastructure entries.

## 23.3 Entry status values

**[r2.1]** Regulatory stage and publication state are kept distinct:

```text
PROPOSED                 filed or proposed, not approved (e.g. a proposed SEC rule)
APPROVED_NOT_EFFECTIVE   approved, effective date not yet reached
CURRENT                  in force now per the latest operative source
SUPERSEDED               replaced by a later operative source; effective_to set if it was
                         ever in force, both dates null if it never took effect
WITHDRAWN                proposed or filed, then withdrawn; never in force
ERRONEOUS_DISCLOSURE     a disclosure later corrected as wrong; never an operating regime
CONFLICTED               two sources of equal tier disagree; both shown, neither chosen
PENDING_VERIFICATION     internal only: awaiting approval; never public
```

Mapping from the triage `change_status` (§24.2) to a proposed tracker status:

| Triage `change_status` | Proposed tracker status |
|---|---|
| `PROPOSED` | `PROPOSED` |
| `APPROVED` | `APPROVED_NOT_EFFECTIVE` if effective date is in the future, else `CURRENT` |
| `EFFECTIVE` | `CURRENT`; prior entry for the same field → `SUPERSEDED` |
| `WITHDRAWN` | `WITHDRAWN` |
| `CORRECTION_OF_PRIOR_DISCLOSURE` | new entry `CURRENT`; corrected entry → `ERRONEOUS_DISCLOSURE` |
| `UNKNOWN` | human queue; no proposed status |

The mapping is code; the human approves the result.

**Target dates are fields, not statuses.** A venue's announced launch target (for example December 6) is recorded in `go_live_target`, with its own evidence. That entry is `CURRENT` when it is the latest announced target; the underlying rule can simultaneously be `APPROVED_NOT_EFFECTIVE`. When the launch happens, `go_live_actual` is recorded separately.

`CONFLICTED` exists because a single organization's own pages can disagree with each other. Resolution follows the Stage B rule: effective-date and amendment history, never "the newer-looking sentence." Until resolved, the public page shows both sources and says so.

A **correcting amendment** is not a regime change. When a filing states that a prior disclosure was wrong (the BOATS 15%→20% band redline is the reference case), the prior entry becomes `ERRONEOUS_DISCLOSURE` with `effective_from`/`effective_to` left null, and **no** structural break is created.

## 23.4 Entry schema

Extends the §6.2 claim register:

```text
entry_id
entity
field
value                     typed (time range, date, enum, percentage)
status                    §23.3
effective_from
effective_to
evidence_refs[]           [r2.1] one or more; see below
supersedes                entry_id | null
conflicts_with            entry_id[] | null
correction_of             entry_id | null
proposed_by               manual | structured_llm | jev
provider_version          pinned identifier | null (manual)
approved_by
approved_at
load_bearing              bool (research relevance)
```

**[r2.1] `evidence_refs[]`.** The operative rule and its effective date often come from different documents: a rule filing sets the session, a later trader notice sets the date. Forcing one span to support the whole entry recreates the source-conflation problem the tracker exists to prevent. Each reference is:

```text
source_id                 → evidence/manifest.jsonl
source_version_or_accession
span_id                   → segment of the archived snapshot
span_excerpt              short excerpt only (see §23.5)
sha256
retrieved_at
supports[]                value | effective_from | effective_to | status
```

Every published component of an entry (value, each non-null date, status) must be covered by at least one reference whose `supports[]` includes it. G6 enforces this.

`proposed_by` and `provider_version` are kept on every entry so the public history shows which entries originated from a model proposal, and from which model version.

## 23.5 Publication policy

Public:

- entity, field, value, status, effective interval;
- a **short** supporting excerpt, the canonical link, retrieval timestamp and SHA-256;
- the change history per field;
- the weekly changelog;
- the monitor's evaluation page and failure log (§25).

Private (repository only, not deployed):

- full archived snapshots of filings, notices and PDFs.

Quoting a line with a link is different from rehosting an exchange's documents wholesale, and exchange site terms vary. Publish the hash so anyone can verify against their own copy.

Never published on the tracker: anything derived from Databento or other licensed or terms-restricted market data, including FINRA datasets until their terms are recorded in the licensing matrix. That stays behind G5.

Rendering: static HTML generated from the registry by `make tracker-build`. No web framework, no database server — consistent with the V1 stack rule.

## 23.6 Tracks

| Track | Starts after | Deliverable | Provider |
|---|---|---|---|
| **T0** | Stage A | `tracker_entry.schema.json`; registry shared with research | — |
| **T1** | Stage B | Public tracker launch, seeded from Stage B verified facts; first changelog | `manual` |
| **T2** | T1 (continuous) | Labeled eval universe (§25.1); historical set frozen with hash | `manual` |
| **T3** | T2 historical set frozen | Change monitor running the §14 checklist; weekly changelog drafted from approved entries | `manual`, or `structured_llm` if G7 passed |
| **T4** | Jev access granted | G7 activation run for Jev (§24.5) | `jev` only if G7 passes |

The manual weeks (T1–T2) are not a delay. Hand-curating the history for the tracked entities is how the labeled eval set gets built. T3 turns the monitor on once there is something to measure it against.

---

# 24. [r2] AI change monitor and provider dependencies

## 24.1 Division of labor

The model never produces a published value. It classifies and points; code extracts and checks; a human approves.

| Step | Owner | Output |
|---|---|---|
| Fetch, archive, hash | code | manifest record (§6.1) |
| Segment document into addressable spans | code | `span_id` + character offsets |
| Pre-filter candidate spans (section rules, keywords, ATS-N Part/Item addressing) | code | candidate spans |
| Typed triage questions **per candidate span** (§24.2) **[r2.1]** | **provider** | span-level answers + confidence |
| Group span-level answers into **atomic rule changes** **[r2.1]** | code | `list[TriageProposal]` (zero or more per document) |
| Extract values (times, dates, band %, enums) from each change's spans | code (`parse.py`) | typed values or `PARSE_FAIL` |
| Citation validation (each `evidence_refs[]` span exists, hash matches, each supported component appears in its span) | code (`validate.py`) | pass / reject with reason |
| Supersession, correction and conflict detection against the registry | code | proposed status |
| Approval | **human** | registry entry (G6) |

Anything that is `UNKNOWN`, below the routing threshold, `PARSE_FAIL` or a validator rejection goes to the human queue. In v1 **every** entry needs human approval regardless of confidence. Confidence orders the queue; it never publishes.

## 24.2 Triage schema (`triage_proposal.schema.json`)

**[r2.1] Unit of work: the atomic rule change, not the document.** A single filing can amend several independent items. The provider is asked the questions below **once per candidate span**; code groups the answers into zero or more atomic changes per document. Asking per span also keeps every question a small closed choice, which suits a decision-style model and avoids asking it to choose among a large set of span IDs.

Per-span questions:

```text
states_rule_change:   YES | NO | UNKNOWN

affected_entity:      NASDAQ | NYSE_ARCA | CBOE_EDGX | 24X | MEMX
                      | BOATS | SIP | LULD | NSCC | OTHER | NONE

change_type:          SESSION_HOURS | ORDER_TYPE | TIME_IN_FORCE
                      | TRADE_DATE | PRICE_BAND | GO_LIVE_DATE
                      | HALT_RULE | CLEARING | MARKET_DATA | REG_NMS | OTHER

change_status:        PROPOSED | APPROVED | EFFECTIVE
                      | CORRECTION_OF_PRIOR_DISCLOSURE | WITHDRAWN | UNKNOWN

research_relevance:   LOAD_BEARING | CONTEXT_ONLY | NONE
                      (proposal only — a human sets the final `affects` value)
```

Every field is a closed set. That is deliberate: it fits a decision-style model such as Jev, and it keeps the interim provider honest too.

A `TriageProposal` (one atomic change) is assembled by code from one or more `YES` spans sharing entity and change type, and carries their span IDs as draft `evidence_refs[]`. Grouping rules are deterministic and unit-tested; an ambiguous grouping goes to the human queue rather than being merged.

## 24.3 Provider interface

```python
class TriageProvider(Protocol):
    name: str                      # "manual" | "structured_llm" | "jev"

    def classify_span(
        self,
        doc: ArchivedDocument,     # provides document-level context header
        span: Span,                # one pre-filtered candidate
    ) -> SpanAnswer:               # validated against the JSON schema
        ...

# [r2.1] Code, not the provider, turns span answers into changes:
def propose(doc: ArchivedDocument, provider: TriageProvider) -> list[TriageProposal]:
    answers = [provider.classify_span(doc, s) for s in prefilter(doc)]
    return group_into_atomic_changes(answers)   # zero or more per document
```

Rules:

- Providers are swappable by config. Swapping a provider must not change registry semantics, validator behavior or the §14 trigger map.
- Every proposal records provider name, provider/model version, request hash and latency.
- **[r2.1]** Scored evaluation requires a **pinned** model version. If a provider cannot pin versions, its results are labeled `version_unpinned` and are not compared across time or used for G7.
- Only **public** documents are ever sent to a non-manual provider. No private data, credentials or licensed market data.

## 24.4 Provider configuration (`config/providers.yaml`)

```yaml
triage:
  active_provider: manual        # manual | structured_llm | jev
  routing_confidence_floor: TBD  # set in evals/triage/protocol.md before any run
  max_candidate_spans_per_doc: TBD  # cost/latency cap; not a provider output limit

  providers:
    manual:
      enabled: true

    structured_llm:              # optional interim AI provider
      enabled: false
      model: TBD                 # any general-purpose model with schema-constrained output
      activation_gate: G7

    jev:
      enabled: false
      vendor: TypeSafe AI
      status: WAITLISTED         # WAITLISTED | ACCESS_GRANTED | EVALUATING | ACTIVE | REJECTED
      status_source: self_reported_by_account_owner
      status_reported_at: 2026-09-22
      pinned_version: null       # set at G7 step 6; required for scoring
      activation_gate: G7
```

## 24.5 Jev — registered dependency

```text
dependency_id:     jev_triage_provider
vendor:            TypeSafe AI
component:         AI change monitor — triage (§24.2) and span selection
status:            WAITLISTED (self-reported by account owner, 2026-09-22)
blocking_for:      nothing
                   (freeze-required: no · tracker launch: no · monitor launch: no)
enables:           Jev-backed triage; provider comparison; calibration analysis
fallback:          manual (default); structured_llm (optional, via G7)
rollback:          set active_provider back; no registry migration needed
```

**Vendor facts are unverified until activation.** Launch-week material (September 2026) described Jev as returning typed decisions with confidence scores, served as hosted inference, with early access by waitlist. Treat all of it as launch-week vendor claims to re-verify from primary vendor documentation at T4. The account's waitlist status is the owner's report, not a vendor fact. Do not state Jev pricing, latency or accuracy anywhere in this project until then.

**G7 activation checklist (run at T4, in order):**

1. **Access.** Confirm access on the account itself; record the date; set `status: ACCESS_GRANTED` and `status_source: account_console`.
2. **Archive vendor docs.** Snapshot and hash the current API documentation, the master customer agreement (https://typesafe.ai/legal/mca) and any usage policy into `evidence/vendors/typesafe/`.
3. **Verify output primitives against §24.2.** Confirm which output types exist and the maximum number of choices per question. The largest §24.2 enum has 11 values; if that exceeds the limit, split the question (e.g. exchange vs. non-exchange first). Do not widen the schema to free text.
4. **Verify operating limits.** Input size limits, rate limits, latency and pricing at time of use, recorded with source hashes.
5. **Review terms.** Data handling and retention for submitted documents (public filings only, per §24.3). Whether results that name the vendor may be published. If they may not, run the evaluation internally and publish only what the terms allow — possibly nothing vendor-named.
6. **Implement the adapter and pin the version.** `providers/jev.py` against `TriageProvider`; schema-validate every response; log version and request hash; set `pinned_version` and record that version's release date.
7. **Sign the evaluation protocol before the first scored run.** Metrics, thresholds, dataset hashes and comparison baselines go into `evals/triage/protocol.md` with a signed commit. The same discipline as the research preregistration: thresholds are not tuned after seeing results.
8. **Run `make triage-eval`** on the frozen historical set and the held-out set (§25.1), against `manual` and against `structured_llm` if it is active.
9. **Decide.** Pass → `status: ACTIVE`, `active_provider: jev`. Fail → `status: REJECTED` with the report archived; the fallback stays active. Either outcome is publishable, subject to step 5.

Set `status: EVALUATING` between steps 6 and 9.

The same checklist, minus the Jev-specific items, applies to `structured_llm` before it can be activated.

---

# 25. [r2] Monitor evaluation

## 25.1 Labeled universe

Recall cannot be measured from what the monitor happened to find. It needs an independently enumerated universe.

1. **Enumerate** every document published by the §14 sources within a stated window.
2. **[r2.1] Label every atomic rule change in each document by hand**, blind to any provider output: entity, field, change type, change status, value, effective dates and the supporting spans for each. A document may contain zero, one or several changes; documents with zero are kept as negatives.
3. **Freeze** the historical set with a SHA-256 before any non-manual provider is scored on it.
4. **[r2.1] Held-out set:** documents first published **after 2026-09-22**, labeled blind as they arrive — the human labels first, then sees the provider proposal. This is **prospective relative to the evaluation harness**: the protocol, labels and thresholds were fixed before these documents existed.

**[r2.1] What the held-out set does and does not establish about training contamination.** A document published after a pinned model version was released cannot be in that version's training data. It can still reach the model through retrieval or tools if the provider uses them, and a provider can change weights behind an unchanged name. So:

- score only against a `pinned_version` with a recorded release date;
- count a document as `post_release` only if it was published after that date;
- record whether the provider uses retrieval or tools; if unknown, report contamination as **unknown**, not absent;
- never describe any set as "uncontaminated" without those three facts.

Mandatory trap fixtures, drawn from this project's own history:

```text
BOATS 2023 redline: 15% band disclosed in error        → CORRECTION_OF_PRIOR_DISCLOSURE, no break
BOATS 2023 ATS-N Broker Priority                        → historical; SUPERSEDED by 2024 correction
NYSE Arca 22-hour framework                             → approved, never effective; SUPERSEDED by 23/5, null interval
NSCC 24×5 clearing                                      → CURRENT since 2026-06-29, not "pending"
BOATS 2026-03-01 out-of-band rejection                  → separate regime from 2026-07-20
Synthetic same-tier contradiction                       → CONFLICTED, neither source chosen
Synthetic unsupported value (e.g. wrong go-live date)   → rejected by validator
```

## 25.2 Metrics

**Model-level** — measured on proposals **before** human approval:

- **[r2.1]** change-detection precision and recall over **atomic change events**, not documents. A proposal matches a labeled change when entity, field and change status agree and at least one proposed span overlaps a labeled supporting span. Each labeled change can be matched at most once. A model that finds one of three changes in a filing scores one true positive and two misses;
- document-level detection (does this document contain any change?) reported separately, as a secondary metric;
- entity, change-type and change-status accuracy, with `CORRECTION_OF_PRIOR_DISCLOSURE` reported separately;
- supporting-span selection accuracy;
- abstention rate (`UNKNOWN` / `NONE` / below routing floor);
- `PARSE_FAIL` rate on selected spans;
- false-break proposals (proposals that would have created a regime change that is not real);
- calibration by confidence bin, only if the sample supports it.

**Pipeline guarantees** — reported as guarantees, **not** as model performance:

- uncited claims published: zero by construction (validator + G6 approval);
- validator rejections: count and reasons.

Keep the two groups visually separate on the public page. A zero produced by the approval step says nothing about model quality.

**Reporting rule:** publish counts with Wilson 95% intervals, never bare percentages. Example of why: 35 correct out of 41 is 85%, but the interval is roughly 72%–93%.

## 25.3 Public failure log

Every validator rejection and every human override of a provider proposal gets an entry:

```text
FAILURE #<n>
provider:        <name, version>
document:        <source_id, accession>
proposal:        <field = value, status>
result:          REJECTED | OVERRIDDEN
reason:          <e.g. value not present in cited span>
correct entry:   <entry_id>
caught by:       validator | human review
```

Publish the log alongside the metrics. The failures are part of the evidence that the system works.
