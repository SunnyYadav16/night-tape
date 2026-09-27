# night-tape — Project Plan

**Overnight execution quality measurement for US equities**

Version 2.2 · 22 September 2026

> **Changes from v2.1.**
> 1. **The midpoint-mechanism premise in §6 was invented and is deleted.** BOATS accepts only limit day orders on a price-time-priority book — no midpoint, pegged or market order types. The midpoint handling rule survives on arithmetic alone; the venue story justifying it was fabricated. This was a worse failure than the v1.1 schedule error, which at least came from a stale source.
> 2. **BOATS changed its own rules twice inside the pre-period** (20 July and 10 September 2026). The "stable benchmark" in §8.1 has two known structural breaks before the event even arrives (§2.4).
> 3. **Reg NMS sentence corrected** — the limitation is rule-specific (Rule 611), not a blanket ATS exemption (§2.5).
> 4. **Four unsourced claims deleted:** the "10–20% of retail volume" statistic, the tax/holding-period aside, the IEX directional-bias assertion, and "many venues historically banned stop orders."
> 5. MEMX added to the venue registry. Databento client claim, credit expiry and trade-date wording corrected in v2.1 and retained.
>
> **Verification status of this document.** Directly verified against primary or vendor-primary sources: NSCC go-live, BOATS order types and session mechanics, BOATS rule-change notices, NYSE Arca overnight session hours, SIP hours, Rule 605 covered-order definition, Databento schema semantics. **Not verified: every SEC release number cited below.** They come from a third-party fact-check that was otherwise accurate, but release numbers are easy to get subtly wrong and were not independently opened. Treat each as a citation to check, not a checked citation.
>
> *Provenance of earlier corrections: v1.1's four-regime venue table was factually wrong (stale secondary source describing Arca's superseded 22-hour approval); "single-venue overnight market" was corrected to a BOATS-focused observable panel; the midpoint rule was fixed to preserve the decomposition identity; v2.1 restored a within-night design on a verified schedule asymmetry and added a statistical analysis plan.*

## 1. What this is

A prospective, pre-registered measurement system for US equities overnight execution quality, maintaining a stable venue-level panel across the 23/5 market-structure transition targeted for **6 December 2026**, with Nasdaq regular hours as a replication benchmark.

It measures realized execution cost. It does not predict prices, generate signals, or recommend trades. (Earlier drafts claimed this placed the project "outside investment-adviser territory entirely." That was a categorical legal conclusion this document is not positioned to make. Describe what the tool does; leave classification to counsel — and revisit it if the optional fill-grading layer in Phase 4 is ever built.)

**Where the value actually comes from.** Not from data scarcity — Databento's normalized Blue Ocean history reaches back to 24 August 2025, so the pre-period can be purchased later. The advantage is **prospective design**: freezing the sample, metrics, hypotheses, data-quality rules and event windows *before* the transition. That eliminates hindsight bias in a way no retrospective study can claim, and it is the project's principal methodological asset.

---

## 2. Market structure — verified facts

### 2.1 The transition

**Venue schedules are synchronized, not staggered.** Per NYSE's Extended-Hours FAQ (v4.0, August 2026), NYSE Arca introduces a fourth trading session — the Overnight Session — running **9:00pm to 4:00am ET**, with no opening auction and a distinct `TradingSessionID`. Arca will operate 23 hours a day from 9:00pm through 8:00pm, five days a week; the one-hour break ensures trade clearance, system maintenance, processing of securities operations, and the transition to the next trade date. Target launch is 6 December 2026. Only NYSE Arca members may trade directly during the new hours.

Nasdaq's 23-hour extension was SEC-approved on 10 April 2026, with a 4:00am–8:00pm Day Session and a 9:00pm–4:00am Night Session. **Cboe EDGX** received accelerated approval on 29 May 2026. **24X Exchange** publishes a 9:00pm–4:00am overnight session with the same 6 December target.

**MEMX** filed for 23-hour trading on 9 September 2026 (SR-MEMX-2026-28, release unverified).

All converge on 9:00pm–4:00am. That is why no staggered within-night venue variation exists — and also why the 8–9pm hour matters (§8.2). The venue list is a **versioned registry keyed to actual go-live**, not a frozen set of four; MEMX arriving mid-planning is the argument for that.

**SIP hours.** From 6 December 2026 the equities SIPs operate continuously from **9:00pm ET Sunday through 8:00pm ET Friday**, with a technical maintenance pause each evening between 8:00pm and 9:00pm.

**Clearing is already done.** NSCC went live with 24×5 clearing on **29 June 2026**, running Sundays 8:00pm ET to Fridays 8:00pm ET, after testing that opened in January 2026 and which all firms completed before go-live. Post-trade readiness is no longer a December dependency in the way SIP and exchange go-live are. Note the boundary: NSCC opens at 8:00pm Sunday, an hour before the SIPs — which matches BOATS's 8:00pm start.

Participation requires FIX Tag 715 (`ClearingBusinessDate`) on the UTC real-time output and FIX Tag 336 (`TradingSessionID`) for sending entities.

**December 6 remains a target with real dependencies** — SEC approvals and SIP availability. Do not hard-code it (§8.3).

### 2.2 Trade dates and the four date fields

Trade dates move to a **futures-style convention**: Monday's trading day begins Sunday evening.

**v2.0 overstated the discontinuity.** BOATS already assigns 8:00pm–midnight trades to the following trading day; the exchange convention assigns 9:00pm–midnight trades to the following calendar day's trade date. Over the overlapping **9:00pm–4:00am interval the two substantially align already.** What actually differs is the extra BOATS 8:00–9:00pm hour, plus the distinction between trade date and clearing business date — not a wholesale regime change.

The pipeline must carry four separate fields and never conflate them: **wall-clock execution date, venue session/TradeDate, FINRA/TRF reporting date, and NSCC ClearingBusinessDate.** Tag 715 is the clearing field; Tag 75 semantics must be documented per feed. Archive the operative NSCC UTC technical notice before writing any date logic.

(v2.1's aside on tax holding periods is deleted — irrelevant to a TCA study and not verified.)

Blue Ocean runs 8:00pm–4:00am ET Sunday–Thursday, settling T+1, and operates only on calendar days when the NYSE Trade Report Facility is open the following morning.

### 2.3 Overnight price bands are static

A structural feature worth knowing, and possibly a research angle in its own right: the SIPs publish overnight LULD bands **once, at session start (9:00pm)**, using the existing LULD price band message fields. They remain constant for the whole overnight session and **do not respond to overnight trading activity**. They can be republished only to correct an error. At 4:00am the SIPs clear them by publishing zero price band messages, and no bands are in effect from 4:00am to 9:30am.

The 23-hour day therefore has four band regimes: static overnight, none pre-market, dynamic during regular hours, none after close. The SEC approved temporary price band protections for overnight trading on 5 August 2026.

### 2.4 BOATS mechanics — and two rule changes already inside the pre-period

**Order types.** BOATS accepts **only limit day (session) orders**. It operates a fully automated electronic order book with continuous automatic matching, on **price-time priority**, and has no discretion to alter order terms. There is **no midpoint, pegged or market order type.** Orders expire at session end and do not carry over. The ATS does not route to any other market center.

**Broker Priority.** A documented internalization path: subscribers who have not elected Broker Priority and route simultaneous buy and sell orders are matched against each other, but only if no natural pre-existing order sits on the book at the same or better price. This is the plausible source of unusual execution locations relative to the displayed BBO — not midpoint crossing.

**Order entry opens at 6:15pm; matching begins at 8:00pm.** The opening book is built from roughly 105 minutes of accumulated orders. Structurally this resembles an opening auction without being one, and it matters because the 8–9pm hour is the §8.2 comparison window.

**BOATS runs its own 20% price reference bands**, separate from the SIP overnight LULD. Two band regimes interact.

**The market data feed is incomplete.** Since 20 July 2026, passive orders priced outside the 20% bands are accepted and held **non-displayed**, are not marketable unless repriced inside the bands, and are **excluded from Blue Ocean market data feeds**. Any quoted-spread or depth measure therefore captures displayed liquidity only. Say so explicitly in the paper.

**Two known structural breaks before the event:**

| Date | Change |
|---|---|
| **20 July 2026** | Out-of-band passive orders accepted as non-displayed rather than rejected at entry; excluded from market data |
| **10 September 2026** | BOATS ceased halting symbols for Rule 301(b)(5) Fair Access reasons |

§8.1 makes the stable BOATS measure the spine of the study. That stability has already been perturbed twice in three months, so **structural-break sensitivity around both dates is mandatory, not optional** — and BOATS rule-change notices must be monitored continuously through the event window.

### 2.5 Which protections actually differ

Stated by rule, not by regulatory label. **Rule 611's trade-through definition is limited to regular trading hours**, so trading centers need not apply trade-through procedures to transactions outside RTH. **Parts of Rule 610 are not so limited.** This is a rule-specific limitation, not a blanket ATS exemption from Regulation NMS — v2.1's wording was wrong on both counts.

Nasdaq and NYSE Arca amended their halt rules in July 2026 for extended-session issuer and corporate-action events (releases 34-105860 and 34-105862, unverified).

### 2.6 No real-time overnight NBBO

Pre-transition there is **no real-time consolidated overnight SIP quotation or NBBO**. That is narrower than v2.1's claim that venue-direct data is "the only overnight data available" — some overnight executions are subsequently reported through the TRFs and SIPs, and authorized vendors redistribute venue data.

Every pre-transition metric must be labelled against the **BOATS BBO** — a single-venue best bid and offer — never "NBBO."

### 2.7 The overnight market is thin, but not one venue

Four ATSs were already providing overnight trading as of January 2026. BOATS is the dominant and best-instrumented venue; MOON ATS and Bruce ATS also operate. Describe the dataset as a **BOATS-focused observable panel**, not as the overnight market.

**Volume context, with sourcing discipline.** Aggregate overnight ATS trading is **under 1% of total NMS-stock trading**, per SEC staff commentary in September 2026 — write it as an "as of" estimate, not a timeless fact.

v2.1's "10–20% of retail volume in actively traded overnight securities" figure is **deleted**: no primary source defines the securities, the retail classification, the period, or the numerator and denominator. An unsourced number in a pre-registration is worse than no number.

**BOATS share must be measured, not asserted.** Blue Ocean has publicly claimed roughly 90%, but that is issuer-supplied. Compute venue shares from FINRA ATS Transparency over a frozen pre-treatment window and state the measured figure with its dates. Replace "best-instrumented" with the specific data attributes available.

**Time-of-night composition** varies sharply: NYSE research shows a 9:00pm peak near 2.94M shares/day and a second near 3:00am at ~2.35M, with ETP weight shifting through the window. Geographic attribution: Blue Ocean management has stated roughly 75–80% of **BOATS business** comes from Asia-Pacific — a statement about the venue's customer base, not a measured attribution of the US nocturnal market.

Hour fixed effects are mandatory.

## 3. Research baseline

**Primary reference.** Lim, "Overnight Adverse Selection: Evidence from Blue Ocean ATS and NASDAQ Regular Trading Hours" (20 April 2026, SSRN). Nanosecond order-book data, 30 actively-traded symbols, 24 matched sessions, September 2025 – March 2026.

Findings: overnight effective spreads average **7 cents/share higher**; the 10-second price impact component averages **2.4 cents/share higher** (both t > 4, stock fixed effects, clustered SEs). **Only about one-third** of the spread premium reflects adverse selection; the balance reflects wider quoted spreads in a single-venue continuous market operating without the competitive liquidity provision of regular hours. Retail-popular stocks show premia roughly 60% smaller; ETFs show larger impact premia. The premium is not driven by high-volatility days. Conclusion: primarily **structural rather than informational**.

**Calibrate its weight honestly.** This is a 14-page SSRN working paper by an independent researcher, 30 symbols, 24 sessions. It is an excellent replication target and a poor sole foundation. Ground the methodology additionally in the peer-reviewed after-hours microstructure literature, which independently finds materially higher trading costs and different price-discovery properties outside the core session.

Note also the comparison in its title: Blue Ocean against **Nasdaq** regular hours — single venue to single venue, not the consolidated tape. That drives the baseline choice in §4.

**What is and isn't novel.** "BOATS execution costs exceed Nasdaq RTH" is already established by Lim. Replicating it on a new date range is not a contribution. The contribution is prospective measurement across the infrastructure change.

---

## 4. Data resources

### Usable

| Source | Cost | Role |
|---|---|---|
| **Databento `OCEA.MEMOIR`** | $125 signup credit, then usage-based | Primary overnight source; L1/L2/L3, trades, nanosecond PTP timestamps |
| **Databento `XNAS.ITCH`** | usage-based | Nasdaq RTH baseline |
| **FINRA ATS Transparency** | Free | Symbol universe selection, sample representativeness. Tier 1 delayed ≥2 weeks, other NMS stocks ≥4 weeks |
| **Alpaca `feed=boats`** | Paid subscription | Fallback if already subscribed |

### Verified schema facts (resolved from v1.1 open items)

- **`tbbo`** is **trade-space** sampled: one record per trade, carrying the BBO **immediately before the effect of that trade**. Correct for effective spread.
- **`tbbo` has a `side` field** with documented buy/sell aggressor values and `None` where not specified. Lee-Ready is a fallback, not the default.
- **`bbo-1s`** is **time-space** sampled and is **not a dense one-row-per-second clock.** If neither a BBO update nor a trade occurs in an interval, no record is emitted; fields are forward-filled per documented rules when an event does occur. A backward state lookup still works — the last quote remains the state until changed — but do not write code that assumes a row per second.
- **`mbp-1`** is **book-update-space**: contains every BBO-changing event.
- **Prices are fixed-point integers scaled by 1e-9.**
- **`OCEA.MEMOIR` history begins 24 August 2025** (twice-sourced; confirm in Phase 0).

### Schema selection

`tbbo` alone cannot compute post-trade metrics. It emits records only on trades, so in a sparse overnight book there is frequently no record at t+10s — and a backward `ASOF JOIN` then matches the most recent prior record, often the original trade itself. Price impact computes to exactly **zero**, systematically, worst for the thinnest symbols. It fails silently and looks plausible.

**Required combination:**

- `tbbo` — execution-time BBO and trade metadata
- **plus a continuous quote source** for post-trade midpoints:
  - **`mbp-1` — primary**, if cost permits. Preferred for the 10-second headline result, because a one-second sampling convention is a nontrivial fraction of a ten-second horizon.
  - **`bbo-1s` — cost-sensitivity variant**, adequate for 60s and 300s horizons.

Run both where affordable and report the 10s result under each as a sensitivity. **Do not request `mbo`** — L3 generates hundreds of GB per month and will exhaust the credit immediately.

### RTH baseline: Nasdaq, not consolidated, not IEX

Use **`XNAS.ITCH`**. It matches Lim's comparison, it is apples-to-apples single-venue, and it is a fraction of consolidated volume.

**Do not substitute Alpaca's free IEX feed.** The methodological reason is sufficient and defensible: XNAS matches the reference study's comparator, IEX does not. v2.1 additionally asserted that IEX's wider spreads would understate the overnight premium — that direction is plausible but **untested, so it is deleted.** If the claim is ever wanted, §12 specifies the test; until then, "IEX is not the pre-registered comparator" is the whole argument.

### Not usable

- **Alpaca `feed=overnight`** — trades are 15 minutes delayed and *"adjusted to fit the bid-ask spread."* The adjustment destroys the measured signal. Any effective spread from this feed is an artefact.
- **Alpaca free tier** — IEX only, and IEX does not run overnight.
- **SEC Rule 605** — a covered order must be received during regular trading hours while an NBBO is disseminated and, if executed, executed during regular trading hours. The 2024 amendments added certain non-marketable limit orders submitted outside regular hours, but only if they become executable after the open. A 10pm execution fails on all counts. (An NMS ATS *is* in scope of the rule, so Blue Ocean may file 605 reports — its overnight executions are simply not covered orders.)
- **Rule 606** — routing destinations at aggregate percentages, not price or spread quality.
- **Scraping retail broker WebSockets** — entitlements and redistribution rights are provider- and contract-specific, so this **may be prohibited or may require redistribution rights**; v2.1's universal violation claim was too broad. Inspect the actual agreement before relying on it. Independent of licensing, it offers no historical bulk download and therefore cannot produce the pre-period at all.

### Budget and licensing

The $125 signup credit **expires after six months** — signing up now covers the December event, but treat it as an onboarding subsidy, not a project budget. Use the portal's cost estimator on one-symbol-one-day slices and extrapolate before pulling a universe. **The RTH baseline dominates the bill** even restricted to Nasdaq, and `mbp-1` costs materially more than `bbo-1s`. If money is tight, shorten the RTH window rather than degrading the source.

**Stay historical. Do not buy live data.** Databento's licensing distinguishes historical from live commercial display and non-display use, and live BOATS non-display carries material commercial fees. T+1 acquisition after each session is sufficient for this study and dramatically simplifies the licensing position. Live productization is a separate project with a separate licensing conversation.

Publication constraints to settle **in writing** before release: never redistribute raw BOATS ticks or reconstructable extracts; confirm that aggregated spreads, regressions and figures qualify for external publication; commit **synthetic fixtures only** to the repository, never real BOATS messages. "Derived" does not automatically mean "unrestricted."

One publication rule worth adopting now: **no venue-quality ranking unless the venues are measured with comparable timestamps, quote definitions, trade coverage and selection rules.** Comparing a complete direct feed against a sampled or delayed one manufactures false precision.

---

## 5. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Ingestion | Python + `databento` SDK | Research velocity; Databento also ships official C++ and Rust clients if performance ever matters |
| Storage | Parquet, partitioned `date/symbol/schema` | Columnar, compresses ticks well, queryable in place |
| Analysis | **DuckDB** — canonical query and ASOF layer | Native backward temporal join; SQL is reviewable and reproducible |
| Transforms / QC | **Polars** | Expression-heavy reshaping and data-quality checks. DuckDB owns canonical logic; Polars never does |
| Statistics | `statsmodels` for replication; a fixed-effects package (`pyfixest` / `linearmodels`) for the event study | FE-oriented libraries simplify multiway clustering. Cross-check headline estimates in both |
| Figures | matplotlib/plotly, script-generated | Reproducibility over interactivity |
| Orchestration | Makefile or small CLI | One command regenerates every number |

**Production controls — these matter more than adding Spark or Kubernetes:**

- **Data manifest** recording vendor, schema, date range, request hash and checksum for every pull
- **Pinned environment** — `uv.lock` plus a Docker image digest for published replication, since a Python lock file does not pin OS-level libraries
- **Schema contracts** and sequence-gap checks on every ingested batch
- **CI** running the synthetic sparse-book and session-boundary tests on every commit
- **Exclusion dashboard** counting every dropped row by reason

No web framework, no database server, no UI in V1.

---

## 6. Metrics

With `D` = +1 buyer-initiated, −1 seller-initiated; `M_t` = pre-trade BBO midpoint from `tbbo`; `M_{t+τ}` from the continuous quote feed:

- **Quoted spread** — `ask − bid`, plus depth at BBO
- **Effective spread** — `2 × D × (P_trade − M_t)`
- **Realized spread** — `2 × D × (P_trade − M_{t+τ})`
- **Price impact** — `2 × D × (M_{t+τ} − M_t)`, at τ = 10s, 60s, 300s
- **Mark-to-open** — `P_open − P_trade`, signed, **reported separately as timing risk, never as execution cost**

Report in both cents/share and basis points — **basis points is the pre-registered primary scale**, since overnight symbol mixes differ sharply by price level; cents/share is reported alongside because it maps to execution economics.

**Freeze the trade-sign mapping in a unit test**, not in a notebook:

```text
Databento side = Bid   -> buyer aggressor  -> D = +1
Databento side = Ask   -> seller aggressor -> D = -1
Databento side = None  -> direction unresolved
```

**Four fields the pipeline must carry** beyond the metrics themselves:

- **Quote age.** Even `mbp-1` legitimately leaves the BBO unchanged when nothing happens — that is the correct book state, but a 90-minute-old two-sided quote is economically nothing like one updated 50ms ago. In a thin overnight book this is first-order. Report it continuously and stratify on it; do not silently filter.
- **Event sequence.** Nanosecond timestamps can tie. Use venue sequence numbers in addition to timestamps for state reconstruction, or you can manufacture future leakage from a timestamp collision.
- **Timestamp policy.** `ts_event` and `ts_recv` are not interchangeable. Use venue event time for within-venue state reconstruction; validate cross-venue clock comparability explicitly before any opportunity-cost analysis.
- **Halt status and rule version.** Halt as an explicit state, not an exclusion. And a **BOATS rule-version field** — the "stable benchmark" stops being stable if BOATS changes its own matching, bands or session rules near the event.

### Midpoint-priced trades, unknown side, and the decomposition identity

**Correction from v2.1.** The previous version asserted that "Blue Ocean matches internal crossing orders at the midpoint." **That is false and was never sourced** — BOATS accepts only limit day orders on a price-time-priority book, with no midpoint, pegged or market order type (§2.4). The claim was pattern-matched from how dark pools generally work and stated as a fact about this venue. It is deleted.

The handling rule survives untouched, because it was always **arithmetic, not a venue mechanism**:

For any execution where `P = M_t`, effective spread `2D(P − M_t) = 0` for either value of `D`. Direction is irrelevant when the numerator is zero. No matching mechanism needs to exist for this to hold.

**The rule:**

| Metric | Midpoint-priced trades with unknown side |
|---|---|
| `ES_all` | **Include** at effective spread zero. Population-level execution cost |
| `ES_decomp`, `RS`, `PI` | **Exclude.** These involve `M_{t+τ} − M_t`, which is nonzero, so direction genuinely matters |
| `ES = RS + PI` invariant | **Test only on the common signed sample**, row by row |

Report the excluded share of trades and of volume alongside every decomposition result.

**What is actually unknown, and must be measured rather than assumed.** Databento permits `side = None`; its prevalence and its relationship to execution price location on BOATS specifically are empirical questions. Do not assert a causal link between unknown side and midpoint pricing in either direction.

Phase 0 cross-tab: `side = None` against `at_bid`, `at_ask`, `exact_mid`, `inside_spread_other`, `outside_displayed_BBO`, both trade- and share-weighted. Define exact midpoint with integer arithmetic — `2*price == bid_px_00 + ask_px_00` — never floats.

Compute both conditional probabilities separately, because they answer different questions:

```
P(side = None | midpoint)     and     P(midpoint | side = None)
```

A high first probability does not mean most unknown-side trades are midpoint executions. A high second does not establish any midpoint mechanism.

**A better-grounded explanation exists** if unusual price locations do show up: BOATS' Broker Priority path, where subscribers who have not elected it and send simultaneous buy and sell orders are matched against each other when no natural order rests at the same or better price (§2.4). Also note that non-displayed out-of-band orders are excluded from the market data feed, so displayed-BBO-relative location is measured against an incomplete book.

Exclusion thresholds are set **after** inspecting these Phase 0 distributions, then frozen.

---

## 7. Known gotchas

Ranked by how silently they fail:

1. **`tbbo` sparsity zeroes post-trade metrics.** Highest-risk bug in the project. Requires a continuous quote feed and a synthetic sparse-book test fixture.
2. **`bbo-1s` is not dense.** Code assuming a row per second will misalign horizons.
3. **Fixed-point prices scaled 1e-9.** Float-casting gives values a billion times too large.
4. **Decomposition denominators.** See §6.
5. **Never write "NBBO"** for the pre-transition overnight session.
6. **Count every exclusion.** One-sided quotes, crossed books, unclassifiable midpoint trades. Bare `WHERE` clauses bias the sample invisibly.
7. **Two trade-date conventions across the event.** Blue Ocean's 8pm–midnight rule pre-transition; futures-style whole-session post-transition.
8. **Session boundaries.** 8pm open, 4am close, the 8–9pm pause, midnight rollover, and the 4am LULD band clearing.
9. **Hour-of-night composition.** Volume and security mix shift sharply. Hour fixed effects are mandatory.
10. **Corporate actions and halts** mid-session, per the amended Nasdaq 4120 and Arca 7.18-E.
11. **BOATS' own rule changes (20 July, 10 September 2026).** The benchmark is not as stable as v2.1 assumed. Test for breaks at both dates.
12. **Displayed-only liquidity.** Out-of-band non-displayed orders are absent from the feed, so depth and quoted spread measure the displayed book only.

---

## 8. Study design

### 8.1 Benchmark continuity is the central constraint

Pre-transition, BOATS BBO is the only coherent benchmark for BOATS fills. Post-transition, exchange quotations contribute to a consolidated environment conceptually different from an ATS's proprietary book.

**Do not switch benchmarks at the event date.** That creates a measurement-regime discontinuity at exactly the date where you are estimating an economic discontinuity, and the two become inseparable.

**Maintain three parallel outcomes:**

1. **Stable BOATS measure** — BOATS fill against BOATS pre-trade BBO, defined identically before and after. The spine of the study. **Study success depends only on this one.** Caveat: BOATS is *definitionally* stable, not *mechanically* stable — it changed its own rules on 20 July and 10 September 2026 (§2.4). Carry a rule-version field and test for breaks at both dates.
2. **Exchange/consolidated measure** — execution against the contemporaneous exchange or SIP benchmark. *Secondary.* Name the exact dataset, schemas and license before pre-registration, or demote it to exploratory.
3. **Cross-venue opportunity cost** — BOATS fill against the best observable competing quote. *Explicitly contingent* — MOON and Bruce data may not be obtainable at comparable quality.

Every chart labels its benchmark by name: "BOATS BBO," "Nasdaq BBO," "overnight SIP." Never a generic "market spread."

A secondary consolidated-RTH benchmark is worth adding once the Nasdaq replication works. Nasdaq-only answers "is this comparable to Lim?"; consolidated answers "how different is overnight from the best displayed US market in normal hours?" Different questions, both useful.

### 8.2 The 8–9pm window: a real within-night comparison

BOATS runs from 8:00pm. Exchanges, the SIP and overnight LULD protections all begin at 9:00pm. So **the 8–9pm hour stays ATS-only on both sides of the transition** while the 9:00pm–4:00am window receives the full infrastructure package.

That supports a within-night difference-in-differences:

```
Y[i,d,h] = α[i] + λ[d] + θ[i,h] + β·(Post[d] × ExchangeWindow[h]) + ε[i,d,h]
```

`ExchangeWindow = 1` for 9:00pm–4:00am, 0 for 8–9pm. Symbol×hour fixed effects absorb each security's persistent overnight profile; date fixed effects absorb common daily conditions. Pre-event placebo interactions test whether the gap was already moving.

**This is not the v1.1 regime table returning.** That design rested on a schedule that did not exist. This one rests on a verified asymmetry between BOATS's 8:00pm start and everyone else's 9:00pm start.

Three honest limits:

- **8–9pm is not an interchangeable hour.** Volume peaks around 9:00pm (~2.94M shares) with a second peak near 3:00am; security mix shifts sharply by hour. The fixed effects absorb persistent differences, not composition changes.
- **Spillover almost certainly violates SUTVA.** Liquidity providers with new 9:00pm–4:00am exchange obligations may change their 8–9pm behaviour too. If spillover is positive, β is a **lower bound** on the total effect. State this rather than hoping nobody notices.
- **β identifies the infrastructure package, not competition.** Exchange entry, SIP dissemination and overnight LULD all arrive together at 9:00pm. Any claim that competition specifically caused a change needs separate identification.

### 8.3 What can and cannot be identified

If venues launch simultaneously, there is **one common shock and no clean control group.** Realized competitive intensity — venue share, HHI, quoting venue count, depth — is measured post-treatment and jointly determined with spreads: venues quote where spreads are tight, spreads are tight where venues quote. Regressing cost on realized intensity regresses an outcome on another outcome.

**Frozen inferential hierarchy:**

| Level | Design | Claim |
|---|---|---|
| **Primary** | Stable BOATS execution quality, pre vs post | **Descriptive.** Execution quality changed after the transition |
| **Secondary** | 9pm–4am vs 8–9pm gap (§8.2) | Relative effect of the **infrastructure package** |
| **Contingent** | Staggered adoption, only if launches genuinely diverge | Causal, and only if pre-specified conditions are met |
| **Mechanism** | Quote count, HHI, depth, venue presence, SIP price advantage | **Descriptive correlates.** Never causal regressors |

Write-ups must separate three statements: *observed* (execution quality changed), *mechanism evidence* (venue participation changed at the same time), and *causal claim* (justified only if the pre-specified conditions held).

**If launches do stagger**, do not reach for a naive two-way fixed-effects event study with leads and lags — those coefficients are contaminated when treatment effects vary across cohorts or over time. Pre-specify a Sun–Abraham or Callaway–Sant'Anna estimator.

**Market structure as data, not comments.** A single `actual_go_live_date` is too coarse, since exchange, SIP, price-band, testing and routing changes can land separately. Maintain a versioned event table:

```text
venue | event_type | effective_timestamp_utc | session_hours_version
rule_filing_id | quote_feed_status | sip_participation_status
luld_status | routing_status | source_document | source_hash | verified_at
```

### 8.4 Statistical analysis plan

v2.0 said "fixed effects, clustered SEs." That is too vague to pre-register. Freeze all of the following **before** the event:

| Item | Pre-registered default |
|---|---|
| **Primary endpoint** | BOATS effective spread in bps |
| **Key secondary** | 10-second price impact from the decomposition sample |
| **Primary horizon** | **10 seconds.** 60s and 300s are robustness only. Matches Lim's headline; prevents post-hoc horizon selection |
| **Primary weighting** | Equal symbol-night. Trade-weighted and share-weighted as robustness — a handful of large ETF prints otherwise dominate any "average overnight spread" |
| **Inference unit** | Symbol × date × time-bin cells. Millions of prints are not millions of independent observations; trade-level SEs would be grossly understated. Report effective N |
| **Clustering** | Multiway (symbol and date), with a validated bootstrap cross-check |
| **Event windows** | One primary window plus two sensitivity windows, all named in advance |
| **Launch washout** | Report launch night separately; pre-specify a 3–5 session stabilization sensitivity, since early nights carry testing, outages and abnormal participation |
| **Universe** | Deterministic ranking variables, cutoff date, strata quotas and tie-break rules, published as code |
| **Power** | Simulate minimum detectable effect from pre-period symbol-night residual structure **before** freezing N |
| **Multiplicity** | One nominated primary estimand; all subgroup and horizon tests secondary/exploratory with intervals |
| **Exclusions** | Quote-age and crossed/locked thresholds set after inspecting Phase 0 distributions, then frozen. Reason codes preserved; incidence and sensitivity both published |
| **Replication criterion** | Acceptable direction and magnitude bands defined before running, so "explain divergence" cannot become subjective |
| **Pre-registration venue** | Immutable repository with DOI or OSF-style timestamp, plus signed Git commit hash |

**On the universe size:** 30 symbols is inherited from Lim, not dictated by this project's constraints — the BOATS dataset covers far more and starts August 2025. If another 20–70 names can be added at low marginal cost without degrading data quality, external validity improves materially. Let the power analysis decide, not the citation.

### 8.5 Selection discipline

Freeze the universe using **pre-treatment** FINRA ATS volume only. Selecting on post-transition activity conditions on the outcome.

### 8.6 Source hierarchy

This exists because a stale secondary source caused the v1.1 error.

| Priority | Source | Use |
|---|---|---|
| **Highest** | SEC orders, rule filings, NMS plan amendments | Approval status, legal hours, LULD, protections |
| **Highest** | Exchange rulebooks and implementation FAQs | Session definitions, dates, message changes |
| **Highest** | DTCC/NSCC notices | Clearing hours, business dates |
| **Highest** | FINRA rules and transparency datasets | ATS universe, venue volumes |
| **Technical** | Databento / Alpaca documentation | Dataset history, schema semantics, pricing, licensing |
| **Research** | Original papers | Baseline methodology |
| **Secondary only** | News, blogs, commentary | Lead discovery. **Never** final authority on hours or approval status |

## 9. Phases

**Phase 0 — Fact freeze and feasibility (2 weeks).** Build the versioned market-structure event table (§8.3) from primary sources only, per the hierarchy in §8.6. Claim the Databento credit; run one-symbol-one-day queries across `tbbo`, `bbo-1s`, `mbp-1` and `XNAS.ITCH` via the cost estimator. Measure the midpoint-trade share, one-sided-quote rate and quote-age distribution on real data. **Run the power analysis, then freeze the universe** from pre-treatment FINRA volume — let minimum detectable effect set N rather than inheriting Lim's 30.

**Phase 1 — Pipeline (2–3 weeks).** Resumable idempotent ingestion to partitioned Parquet with manifests and checksums. As-of joins at all three horizons. All metrics including `ES_all` / `ES_decomp`. Nasdaq RTH baseline. Test suite covering every item in §7, with the sparse-book fixture in CI.

**Phase 2 — Replication and protocol freeze (1–2 weeks).** Reproduce Lim's findings against the acceptance bands defined in §8.4: the 7-cent and 2.4-cent premia, the one-third adverse-selection share, the retail/ETP cross-section. Then **publish the pre-registration** — the complete §8.4 table, the inferential hierarchy from §8.3, the universe hash, the venue calendar, and the decision rule for selecting among designs. Immutable timestamp plus signed commit hash.

**After this point, stop reopening the design.** Only the enumerated contingencies in §8.3 may change the analysis. That constraint is what the whole project trades on.

**Phase 3 — Pre-period collection and pre-trends (ongoing to launch).** Continuous backfill and collection. Pre-trend plots. No hypothesis testing against the event — that is what the freeze protects.

**Phase 4 — Post-launch collection and analysis.** Record actual per-venue go-live dates. Collect post-period data. Run the pre-specified analysis. Placebos, robustness, sensitivity. Publish aggregated results, methods appendix and code.

**Phase 5 — Optional fill grading. Different product; legal review is a gate, not a disclaimer.**

A fill price alone cannot tell you whether an execution was good. Proper user-level TCA needs order arrival time, arrival midpoint, size, limit price, side, urgency, partial-fill behaviour and routing path — preferably parent-order context. Grade only against an explicit conditional benchmark (relative effective-spread percentile given symbol, hour, size bucket, volatility regime and side), never a generic "your broker executed badly."

Personalized output changes the risk profile: brokerage, best-execution, advertising, contractual and privacy questions all attach. Requirements before any build: counsel review as an explicit go/no-go gate; strip account identifiers; encrypt; define retention and deletion; **never request brokerage credentials**; and require minimum sample sizes with uncertainty intervals before any broker comparison, since sparse samples manufacture reputational conclusions.

---

## 10. What this demonstrates

- **Temporal joins at scale** — millions of trades matched to point-in-time book state plus three post-trade horizons from a separate feed, with out-of-order arrivals and no future leakage. Most candidates have never touched `ASOF JOIN`.
- **Silent-failure engineering** — nothing crashes when `tbbo` sparsity zeroes your price impact or a session boundary is mishandled. The test suite is the deliverable.
- **Research-design judgment** — benchmark continuity, pre-registration, honest identification limits, selection discipline. Rarer in engineering candidates than any pipeline skill, and the thing that makes results trustworthy.
- **Storage and cost architecture** — multi-schema partitioning, the `mbp-1` versus `bbo-1s` tradeoff priced explicitly.
- **Provenance** — manifests, checksums, pinned environments, exclusion accounting.

**Positioning line:** *"A pre-registered, reproducible measurement system for US overnight equity execution quality, maintaining a stable venue-level panel across the 2026 23×5 infrastructure transition, with pre-specified hypotheses committed before the event."*

---

## 11. Risks

Ordered by likelihood × impact. **The top risk is identification, not engineering** — which is a good sign. Pipelines can be engineered around sparse books and timestamp boundaries. A control group cannot be engineered into existence after the fact.

| Risk | Impact | Mitigation |
|---|---|---|
| Common industry shock prevents competition-specific inference | No causal claim available | Primary result is descriptive (§8.3); 8–9pm design estimates the package; staggered design only under pre-specified conditions |
| False precision from clustered trades | Standard errors understated by orders of magnitude | Cell-level inference, multiway clustering, report effective N (§8.4) |
| Sample too small or too selected | Weak power, poor external validity | Power analysis in Phase 0; publish sampling frame and coverage ratios |
| BOATS changes its own mechanics | **Already happened twice** (20 Jul, 10 Sep 2026), inside the pre-period | Rule-version field; mandatory break tests at both known dates; monitor venue notices continuously through the event window |
| Unverified SEC release numbers propagate into the pre-registration | Citations fail under review | Open every release on sec.gov before Phase 2; none in this document has been independently checked |
| Market-structure facts change again | Design invalidated, as in v1.1 | Versioned event table from primary sources per §8.6; re-verify before each phase |
| Cross-venue data unobtainable or impractical | Outcomes 2–3 not computable | Outcome 1 alone is sufficient for study success (§8.1) |
| Spillover into the 8–9pm window | β understates the true effect | Report as a lower bound; state the SUTVA violation explicitly |
| `tbbo` sparsity zeroes post-trade metrics | Decomposition invalid | Continuous quote feed; sparse-book fixture in CI |
| Simultaneous launch leaves no control group | No causal claim available | Pre-registered descriptive event study; intensity reported as correlate only; staggered design if launches diverge |
| RTH baseline or `mbp-1` exhausts credit | Post-period unfunded | Nasdaq-only; shorten window before degrading source; never substitute IEX |
| 6 December slips | Timeline extends | `actual_go_live_date` per venue; pre-period has standalone value; Phase 2 publishes independently |
| Credit expires before launch | Post-period costs money | Verify expiry in Phase 0; budget a paid pull |
| Redistribution limits | Cannot publish data | Publish aggregated statistics, regression tables and code — never raw or per-trade records. Constraint is presumed; read the actual agreement |
| Overnight sample too thin for significance | Weak results | Stratify in Phase 0; extend window rather than symbol count |
| Overlap with `sentimeterllc/blueocean-databento` | Ingestion partly exists | Not a blocker — that repo is fetch-and-store. Cite, don't duplicate |

---

## 12. Open items for Phase 0

**Closed:** EDGX approval (29 May 2026) · 24X hours and target · `OCEA.MEMOIR` start (24 Aug 2025) · credit expiry (six months) · `tbbo` pre-trade quote semantics and `side` field · NSCC 24×5 go-live (29 Jun 2026) · BOATS order types and matching · BOATS rule-change dates · Reg NMS rule-specific scope · FINRA publication lags (Rule 6110(c)) · Lim SSRN ID 6610883, rev. 21 Apr 2026.

**Deleted rather than investigated:** the "10–20% of retail volume" statistic (no primary source) · tax/holding-period aside (irrelevant) · IEX directional-bias claim (untested) · "many venues banned stop orders" (vague; BOATS accepts only limit day orders).

### Document verification (do first)

- [ ] **Open every SEC release number cited in this document on sec.gov.** None has been independently verified. Releases referenced: 34-105199 (Nasdaq), 34-105532 (Arca), 34-105587 (EDGX), 34-105779/105780 (SIPs), 34-105565 (NSCC), 34-106042 (overnight LULD), 34-105860/105862 (halt rules), 34-106310 (MEMX), 34-104086 (24X)
- [ ] Archive the operative overnight LULD amendment (File 4-631) and map each stated rule to a paragraph
- [ ] Archive the NSCC UTC technical specification before writing date logic
- [ ] Pin the Lim PDF revision; verify every non-abstract number against its table
- [ ] Add 2–3 peer-reviewed after-hours papers with DOI and table references
- [ ] Capture per-venue `session_date_rule` from operative rulebook text, not FAQs

### Empirical checks (small, designed to falsify cheaply)

- [ ] **`side = None` cross-tab** — 5 active symbols × 5 sessions, `tbbo`. Both conditional probabilities. Integer midpoint arithmetic
- [ ] **`bbo-1s` staleness** — 3 active + 2 sparse symbols, one session. Emitted rows vs 28,800 intervals; compare 100 random backward lookups against `mbp-1`, record staleness in ms
- [ ] **Cost estimator** over the exact frozen universe for `tbbo`, `mbp-1`, `bbo-1s`, `mbo`, `XNAS` — store JSON quotes with date. Replaces the unverified "hundreds of GB" prose estimate for `mbo`
- [ ] **BOATS venue share** from FINRA over eight fully-published common weeks, Tier-1 and non-Tier-1 on a common end date
- [ ] **Local capacity benchmark** — scan, filter, group-by and ASOF on a 25–50GB extract. Name the machine and RAM
- [ ] **Power analysis**, then freeze N. Do not inherit Lim's 30
- [ ] Quote-age distribution; one-sided and crossed-quote rates
- [ ] Break tests at 20 July and 10 September 2026
- [ ] Pin `sentimeterllc/blueocean-databento` at a commit SHA and inventory it before describing the overlap

### Contractual (longest lead time — start now)

- [ ] Databento account agreement: redistribution of historical, derived and transformed data; survival after termination; academic publication
- [ ] `OCEA.MEMOIR` portal licence section: historical vs live treatment; whether a Blue Ocean subscriber agreement is generated
- [ ] Blue Ocean data agreement: written definitions of Derived Data, Display, Non-Display, Distribution, Redistribution, External Use — and whether regression coefficients, summary statistics, percentiles and figures fall outside them
- [ ] Nasdaq Global Data / TotalView schedule for `XNAS.ITCH`: may derived aggregates be published; attribution requirements
- [ ] Build the permissions matrix — output type × OCEA allowed × XNAS allowed × attribution × redistribution licence — and **fill every cell before Phase 2**

Publishing "only aggregates" does not by itself establish permission. Sufficiently granular derived values may still fall inside a venue's derived-data definitions. Note for contrast that Databento advertises free external redistribution specifically for its `EQUS.MINI` product — which is evidence that rights vary by dataset, not that they carry over to `OCEA.MEMOIR`.

### Still open

- [ ] Exact post-transition consolidated dataset, schemas and licence for Outcome 2 — otherwise demote to exploratory
- [ ] Whether MOON and Bruce data is obtainable at comparable quality for Outcome 3
- [ ] Whether other ATSs also operate 8–9pm, and whether any plan to shift hours (affects §8.2)
- [ ] Whether BOATS has an affirmative Rule 605 reporting obligation — search the current report directory by legal entity and MPID, or delete the "may file" sentence
- [ ] Per-venue actual go-live timing as it becomes known
- [ ] Corporate-action and symbol-change map; security master versioning

---

*Not investment or legal advice. Regulatory details were accurate as of September 2026; several remain subject to pending approvals and active rule changes.*

*Error history, kept deliberately. v1.0 offered Rule 605 as an overnight data source, contradicting its own finding that no overnight NBBO exists. v1.1 built the primary study design on a superseded Arca schedule taken from an October 2025 secondary source. v2.0 described NSCC clearing as a pending December dependency four months after it went live, and misstated Databento's client libraries. v2.1 asserted a BOATS midpoint-crossing mechanism that does not exist and was never sourced. Every error traced to a secondary source or to no source at all. Apply §8.6 before trusting any remaining unmarked claim in this document, and treat the release numbers in §12 as unchecked.*
