# night-tape

Preregistered measurement of US overnight execution quality on BOATS (Blue Ocean ATS) across the 23/5 transition targeted for Sun 6 Dec 2026. It measures realized cost only; it never predicts, signals or recommends. Primary endpoint: BOATS effective spread, bps, 10s horizon, equal symbol-night weights.

**Now:** Week 1 (Tue 22 – Sun 27 Sep 2026), foundations. Active plan: [docs/superpowers/plans/2026-09-22-week1-foundations.md](docs/superpowers/plans/2026-09-22-week1-foundations.md). Freeze tag `v1.0-preregistered` lands Fri 30 Oct 2026. *(Update this line when each week starts.)*

## Docs: read the section, not the whole file

| Need | Go to |
|---|---|
| This week's tasks, exit gate, deliverables | [weekly-build-plan.md](docs/plans/weekly-build-plan.md) §5 |
| Fixture catalogue F01–F25, property tests P1–P5 | weekly App. B |
| Decisions D-0…D-12: inputs, deadline, file path | weekly App. C |
| Which make target should be green this week | weekly App. A |
| Repo layout | [technical-plan-r2.2.md](docs/plans/technical-plan-r2.2.md) §5 (+ `registry/` from weekly W1 task 1) |
| Evidence manifest and claim-register fields | r2.2 §6 |
| Four-date and rule-version contract | r2.2 §7 |
| Canonical trade/quote schemas | r2.2 §8 (+ `record_idx`, `trade_id` from weekly §1.3) |
| Metric formulas, populations | r2.2 §9, §10 |
| Reason codes | r2.2 §11 + weekly §1.4 |
| Make targets (`freeze-required` vs `release-required`) | r2.2 §13 |
| Primary sources to archive | r2.2 §18 + weekly W1 task 5 |
| Gates G0–G7 | r2.2 §20 |
| Tracker/monitor (optional lane) | r2.2 §23–25, weekly §6 |
| Why the design is what it is; stats plan | [project-plan-v2.3.md](docs/plans/project-plan-v2.3.md) §8, §8.4 |
| Vendor-doc findings about OCEA.MEMOIR | weekly §1.3 |

**When docs conflict:** weekly §1 beats r2.2, which beats v2.3.

## Five rules (every week)

1. **Facts in the registry, computation in code.** No date, session time, rule version, launch target or regulatory status appears as a Python or SQL literal, and that includes 6 Dec. Code asks the registry (`registry/events.yaml`, `registry/claims.yaml`) or config (`config/*.yaml`).
2. **One definition.** Joins and metrics live only in `sql/*.sql` (DuckDB). Python, Polars and notebooks call that SQL and never reimplement it.
3. **Fixtures before data.** A code path touches paid data only after its synthetic fixtures pass.
4. **Sign before you look.** Any threshold, band, window or rule that data could tune gets a signed commit *before* that data is examined.
5. **Count every exclusion.** No `WHERE` that silently drops rows. Every stage returns `(output, ledger)` with reason codes.

## Silent-failure traps

- **Prices are int64 fixed-point, 1 unit = 1e-9 USD.**
  - Stay integer until the final division; cents = units / 1e7.
  - Converting to float upstream is the 1e9 bug.
- **`UNDEF_PRICE` is the int64 max.**
  - NULL it before any arithmetic, and classify `ONE_SIDED` before summing bid + ask.
  - DuckDB raises on overflow; NumPy wraps silently.
- **Exact midpoint is `2*price_int == bid_px_int + ask_px_int`.** Never float equality. Half-tick midpoint prints are valid (F20).
- **`side = N` on OCEA marks non-displayed executions** (a vendor claim, verified in W3), not random missingness. Dropping it changes the endpoint population; D-1 decides how it's treated.
- **The ordering key is `(ts_event, sequence, record_idx)`.** One native message can yield several records with the same `sequence`.
- **ASOF joins need equality on `symbol` AND `session_id`.**
  - Precompute the lookup-timestamp columns, and collapse quote state to one row per `(symbol, session_id, ts_event)` first.
  - Without `session_id`, 8:00:01pm matches last night's quote.
- **`tbbo` alone zeroes price impact**, because the ASOF lookup finds the trade's own record.
  - Post-trade midpoints come from `mbp-1` (primary) or `bbo-1s`.
  - `bbo-1s` is not one row per second. Never pull `mbo`.
- **`raw_instrument_id` is session-scoped.** Never join across sessions on it. OCEA uses CMS symbols (`BRK B`); map to XNAS/FINRA explicitly.
- **Time.**
  - Hour bins and fixed effects use ET wall-clock via `zoneinfo`, never a fixed offset. DST ends Sun 1 Nov 2026, between the freeze and the event.
  - A BOATS session sits on one UTC date. Build request windows from the session calendar's UTC bounds, never from date strings.
- **Four dates, never one `date`:** `wall_clock_execution_date`, `venue_trade_date`, `finra_reporting_date`, `nscc_clearing_business_date`.
  - BOATS 8pm–midnight trades belong to the next trading day.
  - The event is the first session with a registry `go_live_actual`, not a calendar date.
- **Naming.** Pre-transition quotes are the "BOATS BBO", never "NBBO". Variable names don't encode causal stories (`post_x_exchange_window`, not `competition_effect`).
- **YAML dates and times.**
  - PyYAML turns `2026-07-20` into a `date` object. Load YAML only through `night_tape.config.load_yaml`, which keeps dates as strings.
  - Unquoted `20:00` parses as the integer 1200 (base-60), so always quote clock times.
- **Golden values are hand-computed from the formulas**, never generated by the code under test.
- **`ES_int == RS_int + PI_int` is exact integer equality**, not a tolerance check.
- **Source conflicts.**
  - A correcting amendment is not a regime change (the 15%→20% band redline is `ERRONEOUS_DISCLOSURE`).
  - When two same-tier sources disagree, mark it `CONFLICTED`. Never pick the newer-looking sentence.

## Data, money, secrets

- `data/` is git-ignored. Raw `.dbn.zst` is immutable and never overwritten. Parquet can always be rebuilt from raw.
- `evidence/` is byte-exact, and `evidence/manifest.jsonl` holds its SHA-256s.
  - Write snapshots only through `night_tape.evidence.manifest.store`. Never edit or reformat them.
  - pre-commit excludes `evidence/`, and `.gitattributes` marks it `-text`.
- Files under `tests/fixtures/` must carry `synthetic: true`, and pre-commit rejects any that don't. Real BOATS messages never enter the repo.
- **Paid Databento calls:**
  - require a recorded `get_cost` quote that fits under the cap in `config/datasets.yaml`;
  - never run in CI;
  - never use live data.
- `DATABENTO_API_KEY` lives in the environment only.
- The XNAS comparator is never swapped for IEX. If cost forces it, shorten the RTH window instead.
- Licensed data (Databento; FINRA until its terms are recorded) never reaches the tracker or any public output. Nothing per-trade or reconstructable goes in the prereg.
- EDGAR requests send a declared User-Agent with contact details and stay under 10 req/s.
- Market-structure changes go through archive-on-fetch → claim register → registry. They are never a code edit.

## Commands

```bash
uv sync --frozen          # env; lockfile is authoritative
make test                 # lint + types + pytest
make freeze-required      # FAILS until Week 6 — stubs exit non-zero with "NOT IMPLEMENTED: <target>"
make release-required     # fails through freeze by design (licensing PENDING)
```

A failing stub target is the correct state, not a broken build. Check weekly App. A before "fixing" one.

## Workflow

- Commits on `main` are signed (`git commit -S`). Commit only when asked.
- A decision is a file plus a signed commit, at the path given in weekly App. C.
- Weekly note: `docs/weekly/2026-Wnn.md`. Gate records: `docs/gates/Gn.md`.
- **If the schedule slips,** cut in the order in weekly §8. Never cut:
  - the fixture gate;
  - G1;
  - sign-before-look;
  - the ledger;
  - archive-and-hash;
  - the clean-room freeze dry run.
- The tracker/monitor lane is off the critical path and pauses first.
- Design records live in `docs/superpowers/specs/`; executable weekly plans in `docs/superpowers/plans/`.

## Name

The project is **night-tape**: package `night_tape` (`src/night_tape/`), CLI `night-tape`. The old name was Nocturn-Audit (`nocturn_audit`); rename it on sight.

## Keeping this file useful

Stay under 200 lines. Add a trap only after it has bitten or a plan names it. Link to sections instead of copying them. When a directory accumulates its own traps, give it its own `CLAUDE.md`.
