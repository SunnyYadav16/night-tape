# CLAUDE.md map + Week 1 plan — design

Date: 2026-09-22 · Status: approved by user in brainstorming

## Goal

Give every future session a small, accurate map of night-tape: the rules the code can't show, the traps that fail silently, and pointers into the right section of the three planning docs. Then produce an executable Week 1 implementation plan.

## Decisions

1. **One root `CLAUDE.md`; no per-directory files yet.**
   - Under 200 lines (target about 100).
   - Content is un-inferable truth only: invariants, silent-failure traps, data/money/secret rules, commands, workflow, and a doc index.
   - No style rules, because ruff owns style.
   - Detail stays in the plan docs; `CLAUDE.md` links to sections (progressive disclosure).
   - Per-directory files get added only when a directory builds up its own traps (e.g. `sql/` in Week 2).
2. **Doc layout.**

   | Path | Role | Was |
   |---|---|---|
   | `docs/plans/project-plan-v2.2.md` | Research design (why) | `nocturn-audit-plan.md` |
   | `docs/plans/technical-plan-r2.1.md` | Implementation spec (what) | `techincal-docx.md` |
   | `docs/plans/weekly-build-plan.md` | Schedule, gates, decisions (when) | `nocturn-audit-weekly-build-plan.md` |
   | `docs/superpowers/specs/` | Design records like this one | — |
   | `docs/superpowers/plans/` | Executable implementation plans, one per week | — |

3. **Precedence when the docs conflict.** The weekly plan's §1 wins over r2.1, and r2.1 wins over v2.2. Known overrides:
   - the freeze moves from 15 Oct to 30 Oct;
   - the ordering key becomes `(ts_event, sequence, record_idx)`;
   - the canonical core is built before the pilot;
   - Broker Priority, "limit-day only" and the 105-minute accumulation are all superseded (r2.1 §1.1, §2.1).
4. **Project name is `night-tape`.**
   - Package `night_tape` (`src/night_tape/`); CLI `night-tape`.
   - Every `Nocturn-Audit`, `nocturn-audit`, `nocturn_audit` and `nocturn` CLI reference in the docs has been renamed. The English word "nocturnal" is untouched.
   - Any old name found later gets renamed on sight.
5. **Week 1 plan scope.**
   - Code tasks from the weekly plan's Week 1, written as TDD steps: scaffold and CI, Makefile with loud stubs, the five contracts, evidence fetch/verify, registry load/validate, config skeletons, the fixture-guard hook, the prereg skeleton, and the cost-baseline script.
   - Manual tasks go in a checklist, not code tasks: Databento signup, licensing emails, r2.1 date edits, D-0, and the actual source-archiving runs.
6. **No commits** until the user asks.

## Out of scope

- Plans for Weeks 2–6. Each is written at the start of its week, informed by the previous gate.
- Tracker/monitor code beyond the T0 schema.

## Risks

- **r2.1 schemas may be incomplete.** The contract fields come from r2.1 §6–§8 plus weekly §1.3. If fields turn out to be missing, the schemas evolve through the tests and are never loosened silently.
- **Evidence tooling is the largest Week 1 code item.** EDGAR folder capture and Playwright render must work before the source archive can be verified.
