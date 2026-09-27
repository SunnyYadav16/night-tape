---
title: "night-tape — Week-by-Week Build Plan"
plan_version: "2026-09-22-weekly-v1"
companion_to:
  - "night-tape v2.2 project plan (22 Sep 2026)"
  - "Validated Technical Implementation Plan r2.1 (22 Sep 2026)"
window: "Tue 22 Sep 2026 → Sat 31 Oct 2026"
internal_freeze_target: "Fri 30 Oct 2026 (Sat 31 Oct buffer)"
event_target_monitored: "Sun 6 Dec 2026 (first 9pm session → trade date Mon 7 Dec)"
---

# night-tape — Week-by-Week Build Plan

This plan covers six working weeks from **Tuesday 22 September to Saturday 31 October 2026**. It ends with the signed `v1.0-preregistered` tag. It turns the r2.1 technical plan (Stages A–R) into weekly work, each week with a hard exit gate. Where this plan departs from r2.1, the difference is listed in §1 and should be folded into r2.2 during Week 1.

## Contents

- §0 How to read this plan
- §1 Changes relative to r2.1
- §2 Timeline at a glance
- §3 Toolchain
- §4 Standing weekly routine
- §5 Weeks 1–6
- §6 Tracker and monitor lane
- §7 Budget checkpoints
- §8 If something slips
- Appendix A: Make-target status by week
- Appendix B: Fixture catalogue
- Appendix C: Decision register
- Appendix D: Key dates

---

## 0. How to read this plan

Every week has the same eight sections:

| Section | What it answers |
|---|---|
| **Goal** | One sentence: what is true at the end of the week that wasn't at the start |
| **Tasks** | Ordered. Earlier tasks unblock later ones |
| **Build** | Modules, files, SQL and make targets that exist by Sunday |
| **Tech & resources** | Libraries, APIs, datasets and documents used that week |
| **Watch out for** | The ways this week's work fails silently |
| **Blockers & dependencies** | What must already be true, and what this week unblocks |
| **Exit gate** | Pass/fail conditions. Don't start the next week's paid work until they pass |
| **Deliverables** | Checklist |

Five rules apply to every week:

1. **Facts live in the registry; computation lives in code.** No date, session schedule, rule version, launch target or regulatory status is ever a Python or SQL literal. Code asks the registry.
2. **One definition.** DuckDB SQL owns the joins and the metric definitions. Pilots, notebooks and Polars transforms call that SQL; they never reimplement it.
3. **Fixtures before data.** No paid data is analysed until the synthetic fixtures covering that code path pass.
4. **Sign before you look.** Any threshold, band, window or rule that could be tuned to results is committed with a signed commit *before* the data that could tune it is examined.
5. **Count every exclusion.** No bare `WHERE`. Every stage emits a reason-coded ledger.

---

## 1. Changes relative to r2.1

### 1.1 Freeze date moves to Friday 30 October

Update r2.1 in these places during Week 1:

- frontmatter `pre_event_freeze_target: "2026-10-15"` → `"2026-10-30"`;
- §0 and the §3 heading ("October 15 definition of done");
- Stage P "by Oct 13" and `minimum_separation_trading_sessions: TBD_BEFORE_2026_10_13` → `TBD_BEFORE_2026_10_28`;
- Stage R and §22 tag message (`"… pre-event freeze — 2026-10-15"`);
- §19 dependency-chain label "OCTOBER 15 INTERNAL FREEZE".

Nothing else in r2.1's scope changes. What changes is that r2.1's compressed stage dates spread across six weeks.

### 1.2 Build order: canonical core before the pilot

r2.1 schedules canonical normalization, the ASOF engine and the metric engine (Stages I–K) **after** the real-data pilot (Stage E). This plan builds them in **Week 2** against synthetic fixtures and runs the Week 3 pilot through that same code. Stages H–K in Week 5 become scale-up and hardening, not first implementation.

The reason: a pilot computed by separate notebook code measures something different from what production computes. That is exactly the "hidden second definition" r2.1 §10 forbids.

### 1.3 Findings from Databento's OCEA.MEMOIR dataset page

Source: `https://databento.com/docs/venues-and-datasets/ocea-memoir`, read 22 Sep 2026. This is vendor documentation, which sits in the technical tier of r2.1 §15. Archive it in Week 1, enter each row as a claim, and test the claims empirically in the Week 3 pilot.

| Vendor-documented behaviour (paraphrased) | Why it matters | Where it lands |
|---|---|---|
| Trades from the MEMOIR *Order Executed* message (a displayed order executed) carry the aggressor side. Trades from the MEMOIR *Trade* message (non-displayed execution) carry `side = N`, because the feed doesn't identify the aggressor | **`side = None` is not random missingness.** Per the vendor, it marks the non-displayed-execution population. Excluding it from `ES_decomp` removes every hidden-liquidity fill from the decomposition. `ES_all` as currently specified only admits `side = None` at exact midpoint, so non-midpoint hidden fills also drop out of the **primary endpoint** | Measured in Week 3; decision **D-1** signed Monday of Week 4 (Appendix C) |
| Records normalized from one native message share the same `sequence` | `(ts_event, sequence)` is **not** a unique ordering key | Week 2: add `record_idx` (position in file) at normalization. Ordering key becomes `(ts_event, sequence, record_idx)` |
| *Broken Trade* and *Corrected Trade* messages are not normalized | Busted or corrected prints stay in the data uncorrected, and normalized schemas can't reveal them | Claim register (known limitation) and paper disclosure. No QC code can fix this |
| Raw symbols use the CMS convention (e.g. `BRK B`) | XNAS and FINRA use different conventions, so universe joins will silently drop suffix symbols | Week 3: symbol-mapping table with tests |
| The native `SecurityID` (→ `raw_instrument_id`) is session-scoped | Never join across sessions on instrument IDs | Week 2 normalization resolves symbols per session |
| One venue timestamp only; `ts_in_delta = 0` | Only `ts_event` and `ts_recv` exist | Timestamp-policy note in `docs/` |
| A `status` schema exposes security trading status (halt, pause, quoting, trading) and session status | Halt state and observed session open/close can come from data, not just the clock | Week 3 pilot pulls `status`; the `HALT` reason code keys off it |
| The dataset covers the Blue Ocean Session, 8pm–4am ET, Sunday–Thursday | Consistent with the current ATS-N | Cross-check in session tests |

Two related points from Databento's MBP-1 page. First, `side = N` can also mark a two-sided BBO change published as one update; that is a book record, not a trade. Second, Databento describes `F_LAST` as needed for MBO book building and ignorable outside MBO. We don't pull MBO, so no `F_LAST` logic is needed.

### 1.4 Reason codes added to r2.1 §11

| Code | Meaning |
|---|---|
| `FEED_ANOMALY` | A BOATS-internal book state that the current ATS-N says shouldn't persist (locked or crossed displayed BBO). Investigate; don't treat as a market state |
| `PRE_SESSION` | Records timestamped before the 8:00pm ET open (e.g. test-order period) |

### 1.5 Calendar facts the code must respect

- **Daylight saving.** US DST ended 2 Nov 2025, began 8 Mar 2026 and **ends again Sun 1 Nov 2026**, which is between the freeze and the event.
  - September pre-period sessions are EDT: 8:00pm ET is 00:00 UTC.
  - December post-period sessions are EST: 8:00pm ET is 01:00 UTC.
  - Hour bins and hour fixed effects must use **ET wall-clock** derived from the tz database, never a fixed offset.
  - No BOATS session straddles a DST switch (both switches happen at 2am Sunday and there is no Saturday-night session), but consecutive weeks map to different UTC hours.
- **A whole BOATS session falls on one UTC calendar date** under both EDT and EST, even though it crosses ET midnight. Derive request windows from the session calendar's UTC start and end, not from a date string.
- **6 December is a Sunday.** The first 9pm exchange session starts Sunday evening and belongs to Monday 7 December's trade date. Define the event by session and trade date, never by calendar date.
- **Thanksgiving (Thu 26 Nov) and Christmas (Fri 25 Dec)** fall inside plausible event windows. Count windows in sessions from the session calendar.

---

## 2. Timeline at a glance

| Week | Dates | Theme | r2.1 stages | Gates | Make targets green by Sunday |
|---|---|---|---|---|---|
| **1** | Tue 22 – Sun 27 Sep | Foundations, evidence, clocks started | A, B (start), C (start) | — | CI, `test` (scaffold), `source-archive-verify` |
| **2** | Mon 28 Sep – Sun 4 Oct | Canonical core on synthetic data | B (close), D, I/J/K (core) | Fixture hard gate | `test` (full fixture suite) |
| **3** | Mon 5 – Sun 11 Oct | Ingestion, pilot, break diagnostics | E, H (core), L (v1) | **G1** | `pilot-report`, `break-report`, `manifest-verify` |
| **4** | Mon 12 – Sun 18 Oct | Power, cost, universe freeze, signed rules | F, G | **G2, G3** | `power-report`, `universe-verify`, `xnas-cost-decision` |
| **5** | Mon 19 – Sun 25 Oct | Backfill, QC, replication, statistics | H (scale), L, M, N | **G4** | `qc-report`, `replication-diagnostic` |
| **6** | Mon 26 – Sat 31 Oct | Pre-trends, contingencies, prereg, freeze | O, P, Q, R | **G0** final | `preevent-report`, `prereg-check`, `freeze-archive`, **`freeze-required`** |

Week 2 and Week 5 are the most likely to overrun. Week 2 because the ASOF engine and fixtures are where silent bugs live; Week 5 because backfill time depends on the Week 4 cost decision.

---

## 3. Toolchain

| Layer | Tool | Notes |
|---|---|---|
| Python | 3.12 | Pin in `.python-version` |
| Environment | `uv` + `uv.lock` | `uv sync --frozen` in CI and Docker |
| Container | Docker, base image pinned **by digest** | Digest recorded in the freeze archive |
| Market data | `databento` Python SDK | Pin the exact version at scaffold time (Databento's release notes list 0.86.0 on 1 Sep 2026 as the latest release at the time of writing). Calls used: `metadata.get_cost`, `get_billable_size` and `get_record_count` before every pull; `metadata.get_dataset_range` to confirm OCEA history start; `timeseries.get_range` for small pulls; `batch.submit_job` for large ones; `DBNStore` plus its symbology helpers for reading and mapping |
| Raw storage | `.dbn.zst` files, immutable | Raw is the source of truth |
| Derived storage | Parquet via `pyarrow` | Always rebuildable from raw |
| Query | DuckDB | Canonical joins and metrics live in versioned `sql/*.sql` files |
| Transforms / QC | Polars | Never owns a research definition |
| Statistics | `pyfixest` (primary); `linearmodels` + `statsmodels` (cross-check) | Wild cluster bootstrap when date clusters are few |
| Staggered DiD | Check Python coverage in Week 5; R `did` and `fixest::sunab` in a pinned container are the reference implementations | Dormant branch only |
| Tests | `pytest`, `hypothesis` | Property tests for leakage, identity and conservation |
| Lint / types | `ruff`, `mypy` (or `pyright`) | |
| Contracts | `jsonschema` | `contracts/*.schema.json` |
| Config | `ruamel.yaml` or `PyYAML` | |
| Evidence fetch | `httpx`; `warcio` for WARC; Playwright for JS-rendered pages | SEC EDGAR fair access: send a declared User-Agent with contact details and stay under 10 requests/second |
| Calendars | stdlib `zoneinfo`; `exchange_calendars` as a cross-check only | The registry is authoritative |
| Secrets / hygiene | `pre-commit`, `gitleaks` or `detect-secrets` | The API key never enters the repo or CI |
| Figures | `matplotlib` | Script-generated only |
| Tracker (optional lane) | Jinja2 → static HTML | No server |
| Signing | `git commit -S`, `git tag -s` (GPG or SSH signing) | Set up in Week 1 |
| Prereg timestamp | OSF registration (supports embargo) or Zenodo DOI | Decide in Week 1 (D-0). An embargo timestamps without publishing |

---

## 4. Standing weekly routine

Every week, roughly half a day:

1. **§14 source check** (manual until the T3 monitor exists). Cover:
   - BOATS Form ATS-N filings (EDGAR CIK 1795131) and Blue Ocean service alerts;
   - Nasdaq, Arca, EDGX, 24X and MEMX notices; SIP notices;
   - the S7-2026-20 docket; LULD plan changes; NSCC notices;
   - Databento data and SDK release notes.

   Every new or changed source → archive-on-fetch → claim register → registry entry if load-bearing.
2. **Licensing follow-ups.** Chase every open cell in `config/licensing.yaml`.
3. **Spend check.** Cumulative Databento spend against the cap in `config/datasets.yaml`.
4. **Weekly note** in `docs/weekly/2026-Wnn.md`: gates passed, what slipped, decisions signed, open claims.
5. **Hygiene.** `make test` green on `main`; no unsigned commits on `main`.

---

## 5. Weeks 1–6

### Week 1 · Tue 22 – Sun 27 Sep · Foundations and evidence

**Goal.** By Sunday:
- the repository exists, and the freeze checklist exists as code that fails loudly;
- every load-bearing primary source is archived with a hash;
- the two long-lead clocks (paid data and licensing) have started.

No market-data code is written this week.

#### Tasks

1. **Scaffold the repository** to the r2.1 §5 layout, plus a `src/night_tape/registry/` module for claim and event registry code. Set up the `uv` project, `ruff`, `mypy`, `pytest` and `pre-commit`, plus CI running lint and tests on every push. Enable commit signing and protect `main`.
2. **Makefile with every target stubbed.** Every `freeze-required` and `release-required` target exists and exits non-zero with `NOT IMPLEMENTED: <target>`. A loudly failing `make freeze-required` is the correct Week 1 state; the checklist can't be forgotten if it's code.
3. **Contracts.** Write `trade.schema.json`, `quote.schema.json`, `event_registry.schema.json`, `claim_registry.schema.json` and `tracker_entry.schema.json` (the last one is T0, cheap because it's the same registry).
   - Add two fields to the r2.1 §8 trade and quote schemas: `record_idx` (§1.3) and a deterministic `trade_id`.
   - Write tests with valid and invalid examples for each schema.
4. **Evidence tooling.** `night-tape evidence fetch <url> --source-id … --source-class …` writes the fetched bytes, a SHA-256 and a `manifest.jsonl` line. `night-tape evidence verify` re-hashes everything. It must handle:
   - plain HTTP responses and PDFs;
   - **whole EDGAR accession folders** (index plus every document, not just the XSL-rendered view);
   - Playwright renders (HTML and printed PDF) for JS-rendered pages;
   - WARC where practical.
5. **Archive the sources:**
   - the 13 r2.1 §18 sources;
   - **every** BOATS Form ATS-N filing and amendment listed in EDGAR's submissions index for CIK 1795131, not just the three named;
   - the Databento OCEA.MEMOIR, TBBO, BBO, MBP-1 and status pages;
   - the pinned Lim PDF revision (SSRN 6610883, rev. 21 Apr 2026);
   - the SEC staff memo and Nasdaq ETA 2026-46.
6. **Seed the claim register** from v2.2, r2.1 and §1.3 of this plan. Each claim gets `load_bearing`, `affects` and `status`. Everything starts `UNVERIFIED` unless an archived source is attached.
7. **Seed the event registry.** Venues and their launch targets; the SIP schedule; the Rule 611/610(e) proposal; the BOATS regimes with provisional labels, including a placeholder for the 2025 IOC/display amendments.
8. **Draft `preregistration/prereg.md`** with every r2.1 §8.4 and Stage Q field. Mark each TBD with the week it will be resolved (Appendix C).
9. **Databento account and cost baseline.**
   - Sign up, claim the credit, and record the signup date and actual credit expiry in `config/datasets.yaml`.
   - Run `get_cost` for one symbol × one session on OCEA (`tbbo`, `mbp-1`, `bbo-1s`, `status`) and on XNAS for one RTH day (`tbbo`, `mbp-1`).
   - Save the JSON quotes, timestamped, under `benchmarks/cost/`.
10. **Licensing (Stage C).** Send written questions to Databento, Blue Ocean and Nasdaq covering derived-data publication, attribution, and survival after termination. Create `config/licensing.yaml` with every permissions-matrix cell set to `PENDING`.
11. **Documents.**
    - Apply the §1.1 date changes to r2.1.
    - Start v2.3 of the project plan, reconciling Broker Priority, the 6:15pm test period, order types, the three-break list and the `side = None` mechanism.
12. **Decide D-0:** preregistration venue (OSF vs Zenodo) and whether to embargo.

#### Build

```text
src/night_tape/
  cli.py
  evidence/{fetch.py, manifest.py, verify.py, edgar.py, render.py}
  registry/{claims.py, events.py, load.py, rule_versions.py}   # rule_versions: interface only this week
contracts/*.schema.json
config/{datasets,sessions,venues,licensing,monitoring}.yaml
evidence/manifest.jsonl + archived sources
preregistration/prereg.md (skeleton)
Makefile · pyproject.toml · uv.lock · Dockerfile · .pre-commit-config.yaml · .github/workflows/ci.yml
tests/unit/{test_contracts.py, test_manifest.py, test_registry_load.py}
```

Make targets that become real: `test`, `source-archive-verify`, and `evidence-load-bearing`. The last one reports which load-bearing claims still lack evidence; it is expected to list many this week.

#### Tech & resources

- EDGAR submissions JSON for CIK 1795131 (enumerates every ATS-N filing) and the accession folder indexes.
- Blue Ocean service-status page. If it is JS-rendered, archive with Playwright and keep both the HTML and a PDF print.
- Databento portal and `metadata.get_cost`.
- The r2.1 §18 URL list.

#### Watch out for

- **Archiving the rendered view instead of the filing.** The `xslATS-N_X01/…` URL is a stylesheet rendering. Archive the accession folder too.
- **Mutable pages.** Service alerts, FAQs and vendor docs change in place. The manifest is the only record of what you saw and when. Re-fetch weekly; a new hash means a new snapshot. Never overwrite.
- **Secrets.** Keep `DATABENTO_API_KEY` in the environment only, with `.env` git-ignored and a secret scanner in pre-commit. CI never calls a paid API.
- **Real data in the repo.** `data/` is git-ignored. A pre-commit hook rejects any file under `tests/fixtures/` without a `synthetic: true` header.
- **Scope creep.** Writing metric code before the contracts exist, or starting the tracker site.

#### Blockers & dependencies

- **Hard blockers:** none.
- **Soft dependencies:** Databento signup; EDGAR availability.
- **Creates a blocker for Week 2:** the final session/date classifier can't be written until Stage B (the amendment chain) is reconciled.

#### Exit gate

- CI green on `main` with signed commits.
- Every §18 source and the full BOATS ATS-N chain are in the manifest with SHA-256, and `source-archive-verify` passes.
- The claim register and event registry load and validate against their contracts.
- Cost quotes stored; licensing questions sent.

#### Deliverables

- [ ] Repo scaffold, CI, signing, branch protection
- [ ] Stubbed Makefile (all freeze/release targets present)
- [ ] Five contracts with tests; `record_idx` and `trade_id` added
- [ ] Evidence fetch/verify CLI; EDGAR folder capture; Playwright capture
- [ ] Full BOATS ATS-N chain plus §18 sources archived and hashed
- [ ] Claim register and event registry seeded
- [ ] Prereg skeleton with dated TBDs
- [ ] Databento account; credit expiry recorded; cost JSON saved
- [ ] Licensing questions sent; matrix at `PENDING`
- [ ] r2.1 date edits; v2.3 plan draft started; D-0 decided

---

### Week 2 · Mon 28 Sep – Sun 4 Oct · Canonical core on synthetic data

**Goal.** The whole computation path exists and passes a synthetic fixture suite, before any paid data is analysed:

```text
normalize → session/date → quote state → ASOF → metrics → exclusion ledger
```

#### Tasks

1. **Close Stage B (Mon–Tue).** Build the BOATS amendment timeline in the event registry. For each filing record the filed date, effective date (from the filing or a service alert), what it changed, and what it supersedes.
   - Must resolve: the 2025 IOC and display/non-display amendments, the 2024 correcting amendment, the Post-Only amendment, and the Fair Access change.
   - A same-tier conflict becomes `CONFLICTED` with a blocker note. It is never resolved by picking the newer-looking sentence.
2. **Rule versions from the registry.** Implement `rule_version_for(venue, session_id)` as a lookup over effective intervals, not constants.
   - Where a source gives only a date, record `effective_granularity: day` plus the first session it applies to.
   - Flag ambiguous boundary sessions so they can be excluded from break estimates or tested both ways.
3. **`sessions/`.** The session calendar (registry plus holiday rules, cross-checked against observed `status` data from Week 3). It provides:
   - `session_id` and UTC start/end;
   - all four r2.1 §7 date fields;
   - the ET hour bin;
   - boundary flags for 8pm, midnight and 4am;
   - the `exchange_window` indicator (9pm–4am).
4. **`normalize/`.** Convert DBN to canonical Parquet.
   - Keep int64 fixed-point prices and assign `record_idx` in file order.
   - Map `side` to direction through a frozen macro.
   - Map `UNDEF_PRICE` to NULL **before** any arithmetic.
   - Resolve symbols per session.
   - Fail closed on unexpected fields or schema versions.
5. **`books/`.** Build the quote-state table from `mbp-1`, with a `bbo-1s` variant.
   - Collapse to one row per `(symbol, session_id, ts_event)`: the last record by `(sequence, record_idx)`.
   - Compute `midpoint_x2_int` and `book_state` (`EMPTY`, `ONE_SIDED`, `LOCKED`, `CROSSED`, `TWO_SIDED`).
6. **`joins/`.** DuckDB ASOF lookups at t+10s, t+60s and t+300s.
   - Equality on `symbol` **and** `session_id`, using `ASOF LEFT JOIN`.
   - Store the matched timestamp, `quote_age_ns`, `sequence_used` and `source_schema`.
   - Tag `SESSION_BOUNDARY` when t+τ is past session end.
7. **`metrics/`.** Quoted spread, depth, ES, RS_τ and PI_τ; the `ES_all` and `ES_decomp` populations; bps and cents. Mark-to-open goes in its own module.
   - **Sign D-10 this week:** the bps denominator (pre-trade midpoint is the default).
8. **`qc/` ledger skeleton.** Each stage function returns `(output, ledger)`. The ledger is a side output of the computation, not a separate pass.
9. **Fixture generator and suite.** Build all of Appendix B. Expected values are **hand-written from the formulas** into golden files, never produced by running the code under test.
10. **Property tests** (Appendix B, P1–P5).

#### Build

```text
src/night_tape/{sessions,normalize,books,joins,metrics,qc}/
sql/
  macros.sql                 # direction_from_side, book_state, es_int …
  books/quote_state.sql
  joins/pre_trade.sql
  joins/future_state.sql
  metrics/spreads.sql
tests/fixtures/*.yaml        # synthetic: true
tests/golden/*.csv           # hand-computed expectations
tests/unit/ · tests/integration/ · tests/property/
```

Two sketches of the canonical SQL follow. They are illustrative, not final.

```sql
-- sql/macros.sql
CREATE OR REPLACE MACRO direction_from_side(s) AS
  CASE s WHEN 'B' THEN 1 WHEN 'A' THEN -1 ELSE NULL END;

-- sql/books/quote_state.sql : one state row per (symbol, session, ts_event)
CREATE OR REPLACE TABLE quote_state AS
SELECT
  symbol, session_id, ts_event, sequence, record_idx,
  bid_px_int, ask_px_int, bid_sz, ask_sz,
  CASE
    WHEN bid_px_int IS NULL AND ask_px_int IS NULL THEN 'EMPTY'
    WHEN bid_px_int IS NULL OR  ask_px_int IS NULL THEN 'ONE_SIDED'
    WHEN bid_px_int =  ask_px_int THEN 'LOCKED'
    WHEN bid_px_int >  ask_px_int THEN 'CROSSED'
    ELSE 'TWO_SIDED'
  END AS book_state,
  CASE WHEN bid_px_int < ask_px_int THEN bid_px_int + ask_px_int END AS midpoint_x2_int
FROM quote_events
QUALIFY row_number() OVER (
  PARTITION BY symbol, session_id, ts_event
  ORDER BY sequence DESC, record_idx DESC) = 1;

-- sql/joins/future_state.sql : lookup_ts_10s = ts_event + 10000000000, precomputed
CREATE OR REPLACE TABLE trade_state_10s AS
SELECT
  t.trade_id,
  q.ts_event              AS matched_ts_10s,
  q.midpoint_x2_int       AS mid_x2_10s,
  q.book_state            AS book_state_10s,
  t.lookup_ts_10s - q.ts_event AS quote_age_ns_10s,
  q.sequence              AS sequence_used_10s
FROM trades t
ASOF LEFT JOIN quote_state q
  ON  t.symbol     = q.symbol
  AND t.session_id = q.session_id
  AND t.lookup_ts_10s >= q.ts_event;
```

The metric arithmetic stays in integers until the final division. With `mid_x2 = 2M`:

```sql
-- ES in 1e-9 USD units: 2·D·(P − M) = D·(2P − mid_x2)
direction * (2 * price_int - mid_x2_pre)                     AS es_int,
direction * (2 * price_int - mid_x2_pre) / 1e7               AS es_cents,
2e4 * direction * (2 * price_int - mid_x2_pre) / mid_x2_pre  AS es_bps,
-- ES_all: exact midpoint is zero regardless of direction
CASE WHEN 2 * price_int = mid_x2_pre THEN 0
     ELSE direction * (2 * price_int - mid_x2_pre) END       AS es_all_int
```

`RS_int = D·(2P − mid_x2_τ)` and `PI_int = D·(mid_x2_τ − mid_x2_pre)`, so `ES_int = RS_int + PI_int` holds **exactly** in integers. That makes it a hard equality assertion, not a tolerance check.

A frozen side-mapping test:

```python
@pytest.mark.parametrize("side_raw, expected", [("B", 1), ("A", -1), ("N", None)])
def test_side_mapping_is_frozen(duck, side_raw, expected):
    assert duck.execute("SELECT direction_from_side(?)", [side_raw]).fetchone()[0] == expected
```

Make target that becomes real: `test` with the full suite. `pilot-report` and `break-report` remain stubs.

#### Tech & resources

- DuckDB documentation on ASOF joins, macros and `QUALIFY`.
- `hypothesis` for property tests.
- Databento TBBO, MBP-1, BBO and "common fields, enums and types" pages for field names, `side` values and `UNDEF_PRICE`.
- The archived ATS-N chain and service alerts for Stage B.

#### Watch out for

- **ASOF has one inequality.** Precompute lookup timestamps as columns. Pre-collapse quote state so each `(symbol, session, ts_event)` has one row; otherwise the join's choice among tied rows is undefined.
- **Cross-session leakage.** Without `session_id` in the equality, a trade at 8:00:01pm can match the previous night's last quote. Fixture F22 exists for this.
- **Integer overflow.** `UNDEF_PRICE` is the int64 maximum, so `bid + ask` overflows if either side is undefined. DuckDB raises an error on BIGINT overflow; NumPy silently wraps. Classify `ONE_SIDED` first, and never do arithmetic on sentinel values.
- **Midpoint prices are legitimate half-ticks.** A midpoint print inside a one-cent spread lands on a half cent. The `INVALID_FIXED_POINT` check must allow exact-midpoint prices (fixtures F20 and F21).
- **Unit conversions.** 1 unit = 1e-9 USD, so cents = units / 1e7. Converting to float anywhere upstream of the final division is the 1e-9 bug in disguise.
- **Circular fixtures.** Golden values generated by the code under test prove nothing.
- **Slow property tests.** Cap `hypothesis` examples in CI and run a deeper profile nightly.

#### Blockers & dependencies

- **Needs:** the Week 1 contracts and the archived ATS-N chain.
- **Stage B slipping:** if a 2025 amendment's effective date can't be established from primary sources by Wednesday, mark the interval `UNKNOWN_EFFECTIVE`. Carry it into the Week 3 break diagnostics as a candidate boundary rather than blocking the week.
- **Unblocks:** all real-data work. Nothing in Week 3 runs until this week's gate passes.

#### Exit gate (hard: r2.1 Stage D and Stage J gates)

- `make test` is green on every Appendix B fixture and property test.
- `ES_int == RS_int + PI_int` holds exactly on the signed sample, and the zero-future-leakage property passes.
- Session tests pass, including DST-adjacent sessions and midnight rollover.
- D-10 is signed.

#### Deliverables

- [ ] BOATS amendment timeline in the registry; conflicts marked, not resolved by preference
- [ ] `rule_version_for()` driven by effective intervals
- [ ] Session calendar with four dates, ET hour bins and boundary flags
- [ ] Normalization with `record_idx`, sentinel handling and fail-closed schema checks
- [ ] Quote-state, ASOF and metric SQL; ledger side-outputs
- [ ] Full fixture suite plus property tests, all green
- [ ] D-10 (bps denominator) signed

---

### Week 3 · Mon 5 – Sun 11 Oct · Ingestion, pilot, break diagnostics

**Goal.** Real Databento data flows through the Week 2 code *unchanged*. The pilot confirms or refutes every data-semantics assumption (gate **G1**), and the week ends with a signed decision on which pre-period regimes the study uses.

#### Tasks

1. **`ingest/`: a resumable, idempotent downloader.**
   - Request hash = hash of (dataset, schema, symbols, start, end, `stype_in`, SDK version).
   - If the manifest already holds that request hash and the file hash verifies, skip.
   - Write raw `.dbn.zst` under `data/raw/dataset=/schema=/date=/…` and never overwrite.
   - **Cost guard:** refuse any pull without a recorded `get_cost` quote, or where cumulative spend plus the quote would exceed the cap in `config/datasets.yaml`.
2. **Request windows from the session calendar.** Each request covers the session's UTC start and end plus a margin, never a bare date string (§1.5).
3. **FINRA ATS Transparency ingestion** (free, weekly ATS volume by symbol).
   - Identify BOATS by the MPID as it appears in FINRA's own data; record the value, don't assume it.
   - Record FINRA's terms in the licensing matrix. FINRA-derived numbers stay off the public tracker until those terms are recorded.
4. **`symbols/` mapping table.** Map between the OCEA CMS convention, XNAS and FINRA, with tests for each suffix class (share classes, warrants, units, rights). Decide **D-9** in draft: map suffix symbols, or exclude them with a reason code.
5. **Deterministic candidate ranking** from a frozen FINRA snapshot, stored with its hash. It produces the pilot symbols now and the wide-pull candidate list for Week 4.
6. **Pilot pull.**
   - Core: about 10 symbols (6 active, 4 sparse) × 5 recent sessions, with `tbbo`, `mbp-1`, `bbo-1s` and `status`.
   - XNAS: `tbbo` and `mbp-1` for 2 symbols × 1 RTH day.
   - **Break-window pulls:** `tbbo` and `status` only, for the pilot symbols, 5 sessions either side of each boundary: 1 Mar 2026, 20 Jul 2026, 10 Sep 2026, and the 2025 amendment dates if they fall on or after the 24 Aug 2025 history start.
   - Confirm the OCEA history start with `metadata.get_dataset_range`.
7. **Pilot report (`make pilot-report`).** It covers r2.1 Stage E plus:
   - `tbbo` record count vs `trades` count per symbol-session;
   - **`side = None` share**, trade- and share-weighted, cross-tabbed by price location (at bid, at ask, exact mid, inside other, outside displayed BBO);
   - both conditional probabilities: `P(side=None | midpoint)` and `P(midpoint | side=None)`;
   - **non-displayed check:** for `side = None` trades, whether displayed BBO prices and sizes are unchanged across the trade in `mbp-1`. Per §1.3 they should be. This is a cheap falsification test of the vendor claim;
   - agreement between the `tbbo` pre-trade BBO and the `mbp-1` state reconstructed immediately before the trade;
   - one-sided rate; locked/crossed rate for the BOATS book (the expectation is roughly zero, and any hit becomes a `FEED_ANOMALY` investigation);
   - quote-age distribution, 10/60/300s future-state coverage, and `mbp-1` vs `bbo-1s` lookup disagreement (`bbo-1s` staleness in ms);
   - any records before 8:00pm ET (`PRE_SESSION`);
   - observed halts, and session open/close times from `status` compared with the registry;
   - rows, bytes and dollars per symbol-session per schema.
8. **Break diagnostics (`make break-report`).** For each boundary, report:
   - symbol availability, trade and volume coverage, and exclusion rates;
   - displayed spread and depth, and quote age;
   - `side = None` share (the 20 July change affects what is displayed);
   - symbol-night residual variance, and primary ES mean and distribution.

   The report is descriptive. It is not a hunt for significant breaks.
9. **Decide and sign D-2**, `preperiod-regimes.yaml`: for each regime, whether it is primary, sensitivity-only or excluded, and why.
10. **QC ledger v1 on real data** and a first exclusion dashboard (static markdown or HTML tables).
11. **Record the G1 decision** in `docs/gates/G1.md`.

#### Build

```text
src/night_tape/ingest/{client.py, request.py, cost_guard.py, batch.py, manifest.py}
src/night_tape/finra/{fetch.py, parse.py}
src/night_tape/symbols/{mapping.py}           + tests/unit/test_symbol_mapping.py
src/night_tape/universe/{rank.py}             # candidate ranking only this week
src/night_tape/reports/{pilot.py, breaks.py, qc.py}
reports/pilot/  reports/breaks/  reports/qc/
preregistration/preperiod-regimes.yaml           # signed
docs/gates/G1.md
```

A cost-guard sketch (confirm parameter names against the pinned SDK):

```python
quote = client.metadata.get_cost(
    dataset=req.dataset, schema=req.schema, symbols=req.symbols,
    start=req.start_utc, end=req.end_utc, stype_in=req.stype_in,
)
ledger.record_quote(req.request_hash, quote)
if ledger.spent() + quote > cfg.spend_cap_usd:
    raise CostCapExceeded(req.request_hash, quote, ledger.spent(), cfg.spend_cap_usd)
```

Make targets that become real: `pilot-report`, `break-report`, `manifest-verify`, and `qc-report` (v1).

#### Tech & resources

- The `databento` SDK (`get_cost`, `get_dataset_range`, `timeseries.get_range`, `DBNStore`, symbology helpers).
- FINRA OTC/ATS Transparency data (web download or FINRA's API platform; confirm access method and terms).
- DuckDB for all report queries.

#### Watch out for

- **First-contact surprises.** Expect instrument IDs that change between sessions, symbols absent on some nights, empty sessions, holiday nights, and extra fields. Fail closed, fix normalization, re-run the fixtures, then re-run the pilot.
- **Reading effect sizes into pilot data.** The pilot answers "does the code and data behave?", not "is the premium there?".
- **Tuning the pre-period to the numbers.** Order the break report so availability, coverage and observability come first and ES levels last. Write D-2's reasons against documented regime compatibility.
- **Cost creep.** Keep `mbp-1` to the core pilot only. Break windows are `tbbo` + `status`.
- **XNAS specifics.** Decide how the RTH baseline handles opening and closing cross prints, and note it as replication-relevant, since Lim's convention may differ.
- **FINRA publication lag.** Tier 1 is delayed at least two weeks and other NMS stocks at least four. Ranking windows use a common end date at least four weeks back.

#### Blockers & dependencies

- **Needs:** the Week 2 fixture gate green; Databento credit active.
- **If G1 fails, stop.** Examples: `tbbo` pre-trade BBO disagrees with `mbp-1`; `side` semantics differ from the vendor docs; `UNDEF_PRICE` shows up somewhere unexpected. Fix before Week 4, because Week 4 pulls are the expensive ones.
- **Unblocks:** the wide pull, power, and every Week 4 signed decision.

#### Exit gate (G1 data-semantics gate)

- The pilot shows correct fixed-point handling, no future leakage, correct `tbbo` pre-trade semantics, resolved timestamp/sequence ties, and `side` semantics consistent with docs and data.
- `preperiod-regimes.yaml` is signed.
- The pilot, break, manifest and QC v1 targets are green.

#### Deliverables

- [ ] Idempotent, cost-guarded ingestion with manifests
- [ ] FINRA ingestion, frozen snapshot, candidate ranking
- [ ] Symbol-mapping table plus tests; D-9 drafted
- [ ] Pilot report, including the `side = None` non-displayed check
- [ ] Break report at every documented boundary
- [ ] D-2 `preperiod-regimes.yaml` signed
- [ ] QC ledger v1; G1 recorded

---

### Week 4 · Mon 12 – Sun 18 Oct · Power, cost, universe freeze, signed rules

**Goal.** Decide how big the study is. Before the full backfill, sign every rule that could otherwise be tuned to results: endpoint population, QC thresholds, event windows, universe, and replication bands.

#### Tasks

1. **Monday: sign D-1, the endpoint population for `side = None`.** Use the Week 3 prevalence and location numbers. Write down every option, pick one primary, and keep the rest as sensitivities:
   - **(a) r2.1 as written.** Non-midpoint `side = None` is excluded from `ES_all` and the decomposition. The primary endpoint is then effectively a **displayed-execution** measure and must be named as such.
   - **(b) Quote-rule signing.** Non-midpoint `side = None` is signed by location (above mid → D = +1, below → D = −1). Exact midpoint stays at zero in `ES_all` and is excluded from the decomposition.
   - **(c) Stratified.** Displayed and non-displayed executions are reported as separate co-primary descriptive strata.

   Whichever is primary, the prereg must state which execution population the endpoint covers. Lim's signing convention goes into the replication notes; if the paper doesn't state it, record `PAPER_AMBIGUITY`.
2. **Wide/shallow `tbbo` pull (F1).** About 100–150 candidates × 15–20 sessions, restricted to D-2 primary regimes and sized with `get_cost` first. Add an optional `bbo-1s` companion for quote-age diagnostics.
3. **Sign D-3, the QC thresholds** (quote age, stale quote, locked/crossed handling), from the Week 3 pilot distributions, into `config/qc_thresholds.yaml`. This is earlier than r2.1 Stage L, so the backfill can't be used to tune them.
4. **Sign D-4, the event windows.** One primary window plus two sensitivity windows, counted in sessions from the calendar, with a 3–5 session launch washout and the launch night reported separately. These are power inputs.
5. **Power simulation (`stats/power.py`).** Grid over N ∈ {30, 50, 75, 100} × window lengths × effect sizes. Run the primary design and the 8–9pm design separately.
   - Report the minimum detectable effect at 80% power and α = 0.05, effective N, and cluster counts.
   - If date clusters are few, the wild cluster bootstrap is mandatory.
6. **XNAS cost decision (F2 → D-6).** Price `tbbo` plus the post-trade quote schema for the matched RTH window. Commit `docs/decisions/xnas_cost.md` with the numbers and quote JSON. If it's too expensive, shorten the window; never substitute IEX.
7. **D-5, the post-trade quote source.** `mbp-1` or `bbo-1s` for the backfill, based on pilot disagreement plus cost.
8. **Capacity benchmark (F3).** A representative 25–50 GB scan/group/ASOF run. Record machine, CPU, RAM, disk, DuckDB version, elapsed time, peak memory and output size. If you use a synthetic upscale because real extracts are smaller, label it as such.
9. **Universe freeze (Stage G → D-7).**
   - Deterministic selection code with strata quotas and tie-breaks, reading the frozen FINRA snapshot.
   - Outputs: `universe.csv`, `universe.sha256`, `selection_method.md`, `sampling_frame.csv`, `coverage_report.md`.
   - Measure BOATS venue share over eight fully published common FINRA weeks.
   - Finalise D-9 (suffix symbols, corporate actions, symbol changes, survivorship).
10. **Replication rules (D-8), signed before any replication code touches real data.**
    - Verify every Lim number against its table in the pinned PDF.
    - List Lim's symbols and sessions (or record `PAPER_AMBIGUITY`).
    - Write `acceptance_bands.yaml` and `divergence_taxonomy.yaml`.
    - Specify stratification by `rule_version` and DST, since Lim's window may cross 2 Nov 2025, 1 Mar 2026 and 8 Mar 2026.
11. **Backfill forecast.** Price the Week 5 backfill from quotes. If it exceeds the remaining credit, decide the paid spend now, or shrink in r2.1 F2 order: shorten the XNAS window, then drop robustness pulls.

#### Build

```text
src/night_tape/stats/{power.py, specs.py}
src/night_tape/universe/{select.py, coverage.py}
config/qc_thresholds.yaml                      # signed (D-3)
preregistration/decision_rules.yaml            # side_none (D-1), windows (D-4)
preregistration/acceptance_bands.yaml          # signed (D-8)
preregistration/divergence_taxonomy.yaml       # signed (D-8)
universe/{universe.csv, universe.sha256, selection_method.md, sampling_frame.csv, coverage_report.md}
docs/decisions/{xnas_cost.md, quote_source.md}
benchmarks/capacity/<machine>.json
reports/power/
```

A power-loop sketch. The formula syntax is fixest-style; confirm it against the pinned `pyfixest`.

```python
PRIMARY = "es_bps ~ post | symbol"                                  # descriptive pre/post
WITHIN  = "es_bps ~ post:exchange_window | symbol^hour + date"      # 8–9pm design
VCOV    = {"CRV1": "symbol+date"}

for n in N_GRID:
    for w in WINDOW_GRID:
        for delta in DELTA_GRID:
            hits = 0
            for r in range(R):
                panel = resample(pre_panel, n_symbols=n, window=w, rng=rng)   # symbol + date-block resampling
                panel = inject(panel, delta, mask=fake_post(panel, w))
                fit = pf.feols(PRIMARY, data=panel, vcov=VCOV)
                hits += fit.pvalue()["post"] < 0.05
            record(n, w, delta, hits / R)
```

In the primary design, date fixed effects would absorb `post`, because every symbol is treated on the same date. That is why that design is descriptive and depends on date-clustered, bootstrap-checked inference.

Make targets that become real: `power-report`, `universe-verify`, `xnas-cost-decision`.

#### Tech & resources

- `pyfixest` (with its wild-bootstrap support), `numpy`.
- `get_cost` quotes and the capacity machine.
- The pinned Lim PDF.
- The frozen FINRA snapshot.

#### Watch out for

- **Power that assumes independence.** Simulate with the exact clustered specification you will run.
- **Peeking disguised as planning.** The wide pull estimates variance. Don't compute or plot pre/post "effects" from it.
- **Universe drift.** Selection must read the hashed FINRA snapshot, never re-download.
- **Survivorship and symbol changes** between the pre-period and December. Decide the rule now (D-9).
- **Bands signed after a peek are worthless.** Replication code stays unrun until D-8 is committed.
- **Lim ambiguity.** If the paper doesn't give symbols, sessions, signing or denominators, record `PAPER_AMBIGUITY` now, not after divergence appears.

#### Blockers & dependencies

- **Needs:** G1; D-2; the FINRA snapshot; budget approval if the backfill exceeds the credit.
- **Unblocks:** the backfill and replication (Week 5).

#### Exit gate (G2 regime/power/universe; G3 cost/capacity)

- The power model uses only D-2 primary regimes.
- MDE is acceptable at the chosen N; cost and capacity fit.
- D-1, D-3, D-4, D-5, D-6, D-7, D-8 and D-9 each have a signed commit.

#### Deliverables

- [ ] D-1 endpoint-population decision signed
- [ ] Wide `tbbo` pull; variance and coverage panel
- [ ] D-3 thresholds and D-4 windows signed
- [ ] Power report (primary and 8–9pm designs)
- [ ] XNAS cost decision; quote-source decision; capacity benchmark
- [ ] Frozen universe with hash and coverage report; BOATS share measured
- [ ] Acceptance bands and divergence taxonomy signed before any replication run
- [ ] Backfill cost forecast and spend decision

---

### Week 5 · Mon 19 – Sun 25 Oct · Backfill, QC, replication, statistics

**Goal.** The full pre-period panel for the frozen universe is computed by the Week 2 code. Replication has been diagnosed. The complete statistical layer runs on fake events with acceptable size.

#### Tasks

1. **Backfill.**
   - Submit batch jobs for the frozen universe × the D-2 primary pre-period × the D-5 schemas, plus the D-6 XNAS window.
   - Verify every checksum and manifest entry.
   - Test resumability by killing a job partway and re-running it: the result must be byte-identical with no duplicate downloads.
2. **Scale hardening of Stages H–K.**
   - Sort Parquet by `(symbol, ts_event)` and check that partition pruning actually happens.
   - Set DuckDB `memory_limit` and `temp_directory`.
   - Re-run the golden tests on the production build.
   - No definition changes: any SQL change reopens the Week 2 gate.
3. **`panels/`.** Build the symbol × session × ET time-bin panel with equal symbol-night, trade and share weights, and report effective N per cell.
4. **Full QC dashboard (Stage L)** using the frozen D-3 thresholds. Show exclusion incidence by symbol, night, hour, `rule_version` and reason, with both trade and volume shares.
5. **Replication (Stage M).**
   - Pull Lim's symbols and sessions if they sit outside the universe.
   - Run the replication and output: paper estimate, our estimate, difference, band, diagnosis code, status.
   - Only `MEASUREMENT_DEFECT` blocks the freeze. `UNRESOLVED` requires a documented, bounded investigation and disclosure in the prereg.
6. **Statistics (Stage N).**
   - The primary specification in `pyfixest`.
   - The 8–9pm design with symbol×hour and date fixed effects.
   - Multiway clustering (symbol and date), plus a wild cluster bootstrap cross-check.
   - `linearmodels`/`statsmodels` cross-checks of the headline estimates.
   - Robustness runs: 60s and 300s horizons; trade- and share-weighted versions.
7. **Fake-event runner.** Place pseudo-events on many pre-period dates and produce the distribution of placebo estimates.
   - **Size check:** the rejection rate at 5% should be close to 5%.
   - If it isn't, fix inference now (bootstrap choice, cluster level), not after December.
8. **Staggered branch.** Implement Sun–Abraham and Callaway–Sant'Anna (Python if coverage is adequate, otherwise the pinned R container). Test on synthetic staggered data and leave disabled.

#### Build

```text
src/night_tape/panels/{build.py, weights.py}
src/night_tape/replication/{lim.py, compare.py}
src/night_tape/stats/{estimate.py, bootstrap.py, placebo.py, staggered.py}
reports/{qc,replication,stats,placebo}/
docs/gates/G4.md
```

Make targets that become real: `qc-report` (full) and `replication-diagnostic`.

#### Tech & resources

- Databento `batch.submit_job`, `batch.list_files` and `batch.download`.
- DuckDB at scale, `pyfixest`, `linearmodels`, `statsmodels`.
- Optionally R `did` and `fixest` in a pinned container.

#### Watch out for

- **Cost overrun mid-backfill.** The cost guard is always on, and the batch plan is priced before submission.
- **Disk.** Parquet can be larger than compressed DBN. Check free space before each job.
- **Vendor changes mid-backfill.** If Databento publishes a data or SDK release note affecting OCEA or XNAS during the backfill, stop and assess before mixing versions. The SDK version is in every manifest line.
- **The replication rabbit hole.** Timebox each divergence investigation, classify it with the D-8 taxonomy, and move on.
- **Size distortion.** A placebo rejection rate well above 5% means the reported standard errors are wrong. That is a freeze blocker for the inference layer, not a footnote.
- **Weighting.** A handful of large ETF prints dominates trade-weighted means. Equal symbol-night weighting stays primary.
- **Quiet definition drift.** Performance work that changes a join's semantics. Any SQL diff triggers the full golden suite.

#### Blockers & dependencies

- **Needs:** every Week 4 signed decision, budget, and replication-symbol data.
- **Unblocks:** pre-trends and placebos (Week 6), and the numbers the prereg references.

#### Exit gate (G4 replication diagnosis)

- `qc-report` and `replication-diagnostic` are green.
- No `MEASUREMENT_DEFECT` is open, and every `UNRESOLVED` item is documented.
- Placebo size is acceptable.
- The staggered branch is tested and disabled.

#### Deliverables

- [ ] Frozen universe backfilled; manifests verified; resumability proven
- [ ] Panel with weights and effective N
- [ ] Full QC dashboard
- [ ] Replication table with diagnosis codes; G4 recorded
- [ ] Primary and 8–9pm estimators, clustering, bootstrap, cross-checks
- [ ] Fake-event runner with a size check
- [ ] Staggered estimator branch (dormant, tested)

---

### Week 6 · Mon 26 – Sat 31 Oct · Pre-trends, contingencies, preregistration, freeze

**Goal.** Everything the preregistration references exists, is hashed and is signed. `make freeze-required` passes in a clean environment, and `v1.0-preregistered` is tagged on Friday.

#### Tasks by day

| Day | Work |
|---|---|
| **Mon 26** | **Stage O.** Full break sensitivities on the full sample. Pre-trend plots: ES, PI, quote age, `side = None` share, exclusions, rule-version mix, and the 8–9 vs 9–4 gap. Placebo report. → `make preevent-report` |
| **Tue 27** | **Stage P (D-11).** `decision_rules.yaml` gets a numeric trigger and a pre-written action and branch for each of: launch slip, staggered launch, BOATS rule change after freeze, SIP implementation change, Rule 611/610(e) final action, load-bearing schema change, and primary feed unavailable. Example: the event session is the first session with a registry `go_live_actual` entry, never the target date |
| **Wed 28** | **D-12: stagger threshold** signed as a number of trading sessions, with its design justification. Replaces the 13 October deadline in r2.1 |
| **Wed 28 – Thu 29** | **Stage Q.** Fill every prereg field. `prereg-check` fails if any TBD remains, any load-bearing claim is neither `VERIFIED` nor converted to a contingency, any referenced evidence hash is missing, or any decision file lacks a signed commit |
| **Thu 29** | **Dry-run freeze.** Run `make freeze-required` from a fresh clone inside the pinned Docker image and fix anything non-reproducible |
| **Fri 30** | **Stage R.** Record the Docker digest; `make freeze-archive`; signed commit; `git tag -s v1.0-preregistered`. Upload the prereg and archive hashes to the D-0 venue (embargoed if chosen) |
| **Sat 31** | **Buffer.** Nothing new starts |

#### Build

```text
reports/preevent/{pretrends, placebos, breaks_full}/
preregistration/{prereg.md (final), decision_rules.yaml (final)}
src/night_tape/reports/preevent.py
src/night_tape/prereg/check.py
scripts/freeze_archive.sh
archive/v1.0-preregistered/  (bundle + SHA256SUMS)
```

The freeze commands, as in r2.1 §22:

```bash
make freeze-required
git status --porcelain            # must be empty
git commit -S -m "Freeze night-tape pre-event research protocol"
git tag -s v1.0-preregistered -m "night-tape pre-event freeze — 2026-10-30"
```

Make targets that become real: `preevent-report`, `prereg-check`, `freeze-archive` and `freeze-required`. `release-required` still fails because permissions are `PENDING`, and that is correct.

#### Tech & resources

- The pinned Docker image, GPG or SSH signing, and the OSF or Zenodo account from D-0.

#### Watch out for

- **Late source changes.** Anything found Monday–Thursday goes in through the registry and re-runs the affected targets. Anything found after Thursday evening goes through a post-freeze contingency; don't reopen the design.
- **A failed pre-trend.** Interpret it by the prereg rules. Don't add a specification.
- **Licensed data in the prereg.** No per-trade or reconstructable values. Aggregates only, and check the licensing matrix before uploading anything, embargoed or not.
- **Non-reproducible freeze.** Paths, locale, time zone and unpinned system libraries. That is why the dry run happens inside Docker on Thursday.
- **1 November DST.** The first post-freeze task is to check that the Sunday 1 Nov session's UTC times match the session calendar.

#### Blockers & dependencies

- **Needs:** gates G1–G4, D-11 and D-12, and the licensing matrix recorded (`PENDING` is allowed).
- **Unblocks:** post-freeze monitoring (r2.1 §14) and the T3 monitor.

#### Exit gate (G0 final, freeze)

- `make freeze-required` passes from a clean clone in the pinned image.
- `v1.0-preregistered` is a signed tag.
- The archive bundle and hashes are stored, and the prereg is timestamped at the D-0 venue.

#### Deliverables

- [ ] Pre-event report (breaks, pre-trends, placebos)
- [ ] `decision_rules.yaml` with seven numeric triggers (D-11)
- [ ] Stagger threshold signed by 28 Oct (D-12)
- [ ] `prereg-check` green; prereg final
- [ ] Clean-room dry run passed
- [ ] Signed freeze tag; archive; external timestamp

---

## 6. Tracker and monitor lane

This lane is optional and never on the critical path. If a weekly exit gate is late, this lane pauses first.

| When | Track | Work | Condition |
|---|---|---|---|
| Week 1 | **T0** | `tracker_entry.schema.json` in the shared registry | Always (cheap) |
| Week 2 | — | Nothing new. Stage B entries accumulate with `evidence_refs[]` | — |
| Weeks 3–4 | **T1** | `tracker/validate.py` (gate G6); `tracker/render.py` (Jinja2 → `site/`); `tracker-publish --no-market-data` seeded from Stage B verified facts | Only if Week 3 and Week 4 gates are on time |
| Weeks 5–6 | **T2** | Label atomic changes in documents you are archiving anyway; add the r2.1 §25.1 trap fixtures; freeze the historical set hash when complete | Passive |
| First week of November | **T3** | Change monitor: fetch → segment → prefilter → `manual` provider queue, running the §14 checklist weekly through 6 December | After the freeze. This is when it earns its keep |
| — | **T4 / Jev** | Nothing scheduled. G7 stays closed while `WAITLISTED` | — |

---

## 7. Budget checkpoints

| Week | Expected spend | Control |
|---|---|---|
| 1 | $0 (estimates only) | Record credit amount and actual expiry |
| 2 | $0 | Synthetic fixtures only |
| 3 | Small: pilot plus break windows | `mbp-1` only on the core pilot; break windows `tbbo` + `status` |
| 4 | Wide `tbbo` pull (largest discretionary item) plus XNAS quotes | Price the Week 5 backfill; approve paid spend here if needed |
| 5 | Backfill (likely the largest total) | Cost guard always on. Over budget → shorten the XNAS window, then drop robustness pulls |
| 6 | ~$0 | — |

The cap in `config/datasets.yaml` is enforced in code by the Week 3 cost guard, not by memory.

---

## 8. If something slips

**Cut in this order:**

1. The tracker/monitor lane (§6).
2. Robustness pulls: the 300s horizon, share-weighted variants, the `bbo-1s` sensitivity.
3. XNAS matched-window length (shorten it; never substitute IEX).
4. Depth of the 8–9pm secondary design (keep the specification, coarsen the hour granularity).
5. Wide-pull nights, before wide-pull symbols.

**Never cut:**
- the Week 2 fixture gate;
- G1;
- sign-before-look ordering (D-1, D-3, D-4, D-8);
- the exclusion ledger;
- archive-and-hash of load-bearing sources;
- the clean-room freeze dry run.

**If the freeze itself slips past 31 October**, the only hard limit is that it precedes the first event session (Sunday 6 December, 9pm). The practical limit is mid-November. After that, the pre-event monitoring window gets short and venue/SIP testing notices start landing while the design is still open.

---

## Appendix A: Make-target status by week

`stub` = present, exits non-zero · `partial` = runs, incomplete · `green` = passes its contract.

| Target | W1 | W2 | W3 | W4 | W5 | W6 |
|---|---|---|---|---|---|---|
| `test` | green (scaffold) | **green (full suite)** | green | green | green | green |
| `evidence-load-bearing` | partial | partial | partial | partial | partial | **green** |
| `source-archive-verify` | **green** | green | green | green | green | green |
| `manifest-verify` | stub | stub | **green** | green | green | green |
| `pilot-report` | stub | stub | **green** | green | green | green |
| `break-report` | stub | stub | **green** | green | green | green |
| `power-report` | stub | stub | stub | **green** | green | green |
| `universe-verify` | stub | stub | stub | **green** | green | green |
| `xnas-cost-decision` | stub | stub | stub | **green** | green | green |
| `qc-report` | stub | stub | partial (v1) | partial | **green** | green |
| `replication-diagnostic` | stub | stub | stub | stub | **green** | green |
| `preevent-report` | stub | stub | stub | stub | partial | **green** |
| `prereg-check` | stub | stub | stub | stub | stub | **green** |
| `freeze-archive` | stub | stub | stub | stub | stub | **green** |
| **`freeze-required`** | fails | fails | fails | fails | fails | **green** |
| `release-required` | fails | fails | fails | fails | fails | fails (expected: permissions `PENDING`) |

---

## Appendix B: Fixture catalogue

All fixtures are synthetic, carry a `synthetic: true` header, and have hand-computed golden expectations.

| ID | Fixture | Expected outcome |
|---|---|---|
| F01 | Buyer-initiated trade (`side = B`) above mid | D = +1; ES > 0 |
| F02 | Seller-initiated trade (`side = A`) below mid | D = −1; ES > 0 |
| F03 | Exact-midpoint trade, known side | ES = 0; included in decomposition |
| F04 | Exact-midpoint trade, `side = N` | `ES_all` = 0; excluded from `ES_decomp`/RS/PI |
| F05 | `side = N` inside spread, not at mid (non-displayed execution) | Handled per D-1; ledger reason recorded |
| F06 | No quote update for >300s after trade | M(t+τ) = last state; large quote age; `STALE_QUOTE` per D-3 |
| F07 | Stale pre-trade quote | Quote age recorded; stratifiable, not silently dropped |
| F08 | One side `UNDEF_PRICE` | `ONE_SIDED`; no arithmetic, no overflow |
| F09 | Locked displayed BOATS BBO | `LOCKED` + `FEED_ANOMALY` |
| F10 | Crossed displayed BOATS BBO | `CROSSED` + `FEED_ANOMALY` |
| F11 | Same `ts_event`, different `sequence` | Ordered by sequence; last state wins |
| F12 | Same `ts_event` and `sequence`, several records from one native message | Ordered by `record_idx` |
| F13 | First trade at 8:00pm open with an empty book | `NO_EXECUTION_BBO` |
| F14 | Trade at 11:59pm and 12:01am ET | Same venue trade date (next trading day); wall-clock dates differ |
| F15 | Trade at 3:59:00am; t+300s past 4:00am | `SESSION_BOUNDARY` for 300s; 10s/60s valid |
| F16 | Halt from a `status` record mid-session | `HALT` state carried; not a silent exclusion |
| F17 | One-sided book at t+τ | `NO_FUTURE_QUOTE` for that horizon |
| F18 | Session on a `rule_version` boundary | Correct version from registry intervals |
| F19 | Sessions before and after a DST change | Same ET hour bins; different UTC offsets; correct session UTC bounds |
| F20 | Midpoint print at a half-tick | Passes fixed-point validity |
| F21 | Off-grid price that is not a midpoint | `INVALID_FIXED_POINT` |
| F22 | Trade at 8:00:01pm; only quote is from the prior session | No match (session equality) |
| F23 | Holiday night with no session | No `session_id`; stray records → `UNKNOWN_SESSION_DATE` |
| F24 | Records before 8:00pm ET | `PRE_SESSION` |
| F25 | Clear Book at session start | `EMPTY` book state until first add |

**Property tests:**

| ID | Property |
|---|---|
| P1 | No future leakage: every matched quote timestamp ≤ lookup timestamp. The pre-trade state never includes the trade's own effect |
| P2 | `ES_int == RS_int + PI_int` exactly on the signed sample, for every horizon |
| P3 | Exclusion conservation: input rows = VALID + Σ(excluded by reason) at every stage |
| P4 | Order invariance: shuffling input rows after `record_idx` is assigned doesn't change results |
| P5 | Idempotence: re-running normalization yields byte-identical Parquet and the same hashes |

---

## Appendix C: Decision register

Every decision is a file with a signed commit. The week shown is the latest it may be signed.

| ID | Decision | Inputs | Signed by | File |
|---|---|---|---|---|
| D-0 | Prereg venue and embargo | — | W1 | `docs/decisions/prereg_venue.md` |
| D-1 | `side = None` treatment in `ES_all` and the decomposition (endpoint population) | Week 3 prevalence and location | **W4 Mon** | `preregistration/decision_rules.yaml#side_none` |
| D-2 | Pre-period regimes: primary / sensitivity / excluded | Break report | W3 | `preregistration/preperiod-regimes.yaml` |
| D-3 | QC thresholds (quote age, stale, locked/crossed) | Pilot distributions | W4 | `config/qc_thresholds.yaml` |
| D-4 | Event windows, washout, launch-night handling | Session calendar, power | W4 | `preregistration/decision_rules.yaml#windows` |
| D-5 | Post-trade quote source (`mbp-1` vs `bbo-1s`) | Pilot disagreement, cost | W4 | `docs/decisions/quote_source.md` |
| D-6 | XNAS schema and matched RTH window | Cost quotes | W4 | `docs/decisions/xnas_cost.md` |
| D-7 | Universe and N | Power, coverage, cost | W4 | `universe/*` |
| D-8 | Replication acceptance bands and divergence taxonomy | Lim tables | W4 (before any replication run) | `preregistration/acceptance_bands.yaml`, `divergence_taxonomy.yaml` |
| D-9 | Suffix symbols, corporate actions, survivorship | Symbol map, FINRA snapshot | W4 | `universe/selection_method.md` |
| D-10 | bps denominator; XNAS auction-print handling | Metric definitions, Lim methods | W2 (denominator) / W4 (auction prints) | `config/metrics.yaml` |
| D-11 | Seven contingency triggers and actions | Registry | W6 Tue 27 Oct | `preregistration/decision_rules.yaml#contingencies` |
| D-12 | Stagger activation threshold | Power and design review | **W6 Wed 28 Oct** | `preregistration/decision_rules.yaml#staggered_design` |

---

## Appendix D: Key dates

Reference only. The registry, not this table, is what code reads.

| Date | Event | Relevance |
|---|---|---|
| 24 Aug 2025 | `OCEA.MEMOIR` history begins | Confirm with `get_dataset_range` in W3 |
| Sep 2025 – Mar 2026 | Lim sample window | Replication; may cross the three rows below |
| Sun 2 Nov 2025 | US DST ends | UTC offset change inside pre-period |
| 2025 (TBD, Stage B) | BOATS IOC / display / non-display amendments | Candidate rule-version boundary |
| Sun 1 Mar 2026 | BOATS: passive out-of-band orders rejected | Rule-version boundary |
| Sun 8 Mar 2026 | US DST begins | UTC offset change |
| 29 Jun 2026 | NSCC 24×5 clearing live | Date logic |
| 20 Jul 2026 | BOATS: out-of-band passive orders accepted non-displayed | Rule-version boundary |
| 10 Sep 2026 | BOATS: Fair Access halts cease | Rule-version boundary |
| Tue 22 Sep 2026 | This plan; start of monitor held-out window | — |
| Wed 28 Oct 2026 | D-12 stagger threshold deadline | Freeze input |
| **Fri 30 Oct 2026** | **Freeze: `v1.0-preregistered`** | — |
| Sun 1 Nov 2026 | US DST ends | First post-freeze session check |
| Thu 26 Nov 2026 | Thanksgiving | Session calendar inside pre-event window |
| **Sun 6 Dec 2026** | **Target launch; first 9pm session → trade date Mon 7 Dec** | Event defined by session, not calendar date |
| Fri 25 Dec 2026 | Christmas | Session calendar inside post window |
| Signup + 6 months | Databento credit expiry | Record the actual date in W1 |

---

*Not investment or legal advice. Market-structure facts in this plan inherit the verification status of the registry. Anything not yet `VERIFIED` there is a claim to check, not a checked fact.*
