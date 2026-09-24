# Targets from technical-plan r2.1 §13. A stub exits non-zero with "NOT IMPLEMENTED: <target>".
# That is the correct state until weekly-build-plan App. A makes the target real.
.DEFAULT_GOAL := test

FREEZE_STEPS := evidence-load-bearing source-archive-verify test pilot-report break-report \
	power-report universe-verify xnas-cost-decision manifest-verify qc-report \
	replication-diagnostic preevent-report prereg-check freeze-archive
RELEASE_STEPS := permissions-check attribution-check public-data-scan release-docs release-bundle

STUBS := source-archive-verify pilot-report break-report power-report \
	universe-verify xnas-cost-decision manifest-verify qc-report replication-diagnostic \
	preevent-report prereg-check freeze-archive $(RELEASE_STEPS)

.PHONY: freeze-required release-required $(FREEZE_STEPS) $(RELEASE_STEPS)

test:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src
	uv run pytest

freeze-required:
	@for t in $(FREEZE_STEPS); do $(MAKE) --no-print-directory $$t || exit 1; done

release-required: freeze-required
	@for t in $(RELEASE_STEPS); do $(MAKE) --no-print-directory $$t || exit 1; done

evidence-load-bearing:
	uv run night-tape registry load-bearing

$(STUBS):
	@echo "NOT IMPLEMENTED: $@" >&2; exit 1
