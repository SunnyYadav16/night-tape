# Week 1 Foundations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver weekly-build-plan Week 1 (Tue 22 – Sun 27 Sep 2026). By Sunday:
- the repo has CI and signed commits;
- the freeze checklist exists as make targets that fail loudly;
- the five contracts exist;
- an archive-on-fetch evidence tool exists;
- the claim and event registries are seeded and validated;
- every load-bearing primary source is archived with a SHA-256;
- the paid-data and licensing clocks have started.

**Architecture:**
- **Package and CLI.** One package, `night_tape` (src layout, uv), with an argparse CLI called `night-tape`.
- **Contracts.** JSON Schema 2020-12 files in `contracts/`, all loaded through one module (`night_tape.contracts`).
- **Evidence.** Stored as immutable snapshot files plus an append-only `evidence/manifest.jsonl`. Every capture path writes through a single `store()` function: HTTP, EDGAR accession folders, Playwright renders and hand-downloaded files.
- **Registries.** YAML under `registry/`. They are validated against the contracts, and code checks the cross-references.
- **Makefile.** Wraps the CLI and stubs every later-week target.

**Tech Stack:**
- Runtime: Python 3.12, uv, httpx, jsonschema (+ `referencing`, format extras), PyYAML, Playwright (Chromium), and the `databento` SDK (metadata calls only).
- Dev: pytest, ruff, mypy, pre-commit, detect-secrets.
- Infra: GitHub Actions, Docker.

**Spec:** [docs/superpowers/specs/2026-09-22-claude-md-and-week1-design.md](../specs/2026-09-22-claude-md-and-week1-design.md).
- The requirements come from [weekly-build-plan.md](../../plans/weekly-build-plan.md) §5 Week 1.
- Field lists come from [technical-plan-r2.1.md](../../plans/technical-plan-r2.1.md) §5–§8, §11, §13 and §18. Task 11 renames that file to r2.2; section numbers stay the same.

## Global Constraints

- **Language and tooling.**
  - Python 3.12, pinned in `.python-version`.
  - uv 0.7.x, with `uv sync --frozen` in CI and in Docker.
  - Package `night_tape` in `src/night_tape/`; CLI `night-tape` (stdlib `argparse` only).
- **Dependencies.** Week 1 adds only these:
  - Runtime: `httpx`, `jsonschema[format-nongpl]`, `pyyaml`, `playwright`, and `databento` pinned to an exact version.
  - Dev: `pytest`, `ruff`, `mypy`, `pre-commit`, `detect-secrets`, `types-PyYAML`, `types-jsonschema`.
  - DuckDB, Polars, pyarrow and hypothesis arrive in Week 2.
- **No literals for facts.** No date, session time, rule version or launch target appears as a literal in `src/`. Those facts live in `registry/*.yaml` or `config/*.yaml`. Test data may contain dates.
- **Evidence is immutable.**
  - Never overwrite a snapshot. The manifest is append-only.
  - pre-commit fixers never touch `evidence/`.
- **Outbound requests.**
  - Every HTTP request and Playwright render sends `User-Agent` from the `NIGHT_TAPE_USER_AGENT` env var, and fails if it is unset.
  - SEC requests stay under 10 req/s (a fixed 0.12 s sleep before each one).
- **Tests make no network calls.** Use `httpx.MockTransport` and a local `http.server`. CI never calls a paid API, and `DATABENTO_API_KEY` lives in the environment only.
- **Fixtures.** Every file under `tests/fixtures/` has `synthetic: true` as its first line.
- **Before `make test`.** After editing any Python file, run `uv run ruff check --fix . && uv run ruff format .`. This merges the import lines that later tasks add to `cli.py`.
- **Commits.**
  - Every commit is signed (`git commit -S`). Work happens on branch `week1-foundations`.
  - Commit steps run only while executing this plan with the user's go-ahead.
  - Ask the user before any `git push` or GitHub settings change.

## Deliberate deviations from the weekly Build list

These are left out on purpose, not forgotten:

- **`registry/events.py` and `registry/rule_versions.py`: not created.** Nothing belongs in them until Week 2's `rule_version_for()`.
- **`config/sessions.yaml` and `config/venues.yaml`: not created.**
  - Session hours are versioned facts, so they live in `registry/events.yaml`.
  - The entity list is the `entity` enum in the event-registry contract.
  - Holiday rules arrive with the Week 2 session calendar.
- **WARC: skipped.** Raw HTTP bytes plus Playwright HTML/PDF cover every Week 1 source. Add `warcio` when a source needs replayable capture.
- **Evidence layout.** Snapshots go under `evidence/<SOURCE_CLASS>/<source_id>/`, not r2.1 §5's hand-named tree. The layout is deterministic and needs no mapping table.
- **Clearing-date field name.** The trade contract uses `nscc_clearing_business_date` (the r2.1 §7 name), not r2.1 §8.1's `clearing_business_date`. Task 11 fixes r2.1 to match.
- **Tracker/monitor make targets (r2.1 §13.4): not added.** They are not freeze prerequisites and belong to track T1.

## Review Focus

These are the input classes most likely to bite, each with a behaviour a reasonable person would expect and a test in the owning task:

1. **A mutable page changes between fetches** (service alerts, vendor docs). Expected: a new snapshot, no overwrite, and no duplicate when the bytes are unchanged. Test: Task 4, `test_refetch_*`.
2. **The server answers 404/403, or redirects.** Expected: an error page is never archived as evidence, and a redirect is recorded. Tests: Task 4, `test_http_error_is_not_archived` and `test_redirect_is_recorded`; Task 6, `test_render_refuses_error_page`.
3. **The EDGAR submissions JSON is paginated** (`filings.files` non-empty). Expected: fail closed. Never silently archive a partial ATS-N chain. Test: Task 5, `test_paginated_submissions_fail_closed`.
4. **YAML auto-parses `2026-07-20` into a `date`.** Expected: registry values stay strings and still validate. Test: Task 7, `test_yaml_dates_stay_strings`.
5. **A claim is marked VERIFIED, but its sha256 is not in the manifest.** Expected: `evidence-load-bearing` flags it. Test: Task 7, `test_verified_claim_with_unarchived_hash_is_a_gap`.

## File map

| Path | Responsibility | Task |
|---|---|---|
| `pyproject.toml`, `.python-version`, `uv.lock` | Project, dependencies, tool config | 1 |
| `src/night_tape/cli.py` | argparse entry point; one `_add_*` function per command group | 1, 4–8, 10 |
| `Makefile` | r2.1 §13 targets; stubs fail loudly | 1, 7, 8 |
| `src/night_tape/fixture_guard.py` | Rejects non-synthetic fixtures | 2 |
| `.pre-commit-config.yaml`, `.secrets.baseline`, `.gitattributes` | Hygiene; `evidence/` byte-safety | 2 |
| `.github/workflows/ci.yml`, `Dockerfile`, `.dockerignore` | CI; freeze image | 2 |
| `contracts/*.schema.json` (5) | Trade, quote, claim register, event registry, tracker entry | 3 |
| `src/night_tape/contracts.py` | Load, cross-reference and validate contracts | 3 |
| `src/night_tape/evidence/manifest.py` | `Entry`, `read`, `store`, hashing | 4 |
| `src/night_tape/evidence/fetch.py` | HTTP client with User-Agent; `fetch`; `add_file` | 4 |
| `src/night_tape/evidence/verify.py` | Re-hash; detect missing files, orphans and unarchived sources | 4, 8 |
| `src/night_tape/evidence/edgar.py` | Whole ATS-N chain for one CIK | 5 |
| `src/night_tape/evidence/render.py` | Playwright HTML and PDF capture | 6 |
| `src/night_tape/config.py` | `load_yaml` that keeps dates as strings | 7 |
| `src/night_tape/registry/load.py`, `claims.py` | Registry validation; load-bearing gaps | 7 |
| `src/night_tape/evidence/sources.py`, `config/monitoring.yaml` | Source list; `sync` | 8 |
| `registry/claims.yaml`, `registry/events.yaml` | Seeded registries | 9 |
| `config/datasets.yaml`, `config/licensing.yaml` | Spend cap and credit; permissions matrix | 9 |
| `src/night_tape/cost.py` | Databento cost/size/count quotes | 10 |
| `preregistration/prereg.md`, `docs/plans/*` | Prereg skeleton; r2.2; v2.3 | 11 |
| `docs/decisions/prereg_venue.md`, `docs/weekly/2026-W39.md` | D-0; weekly note | 12 |

---

### Task 1: Scaffold, signing, CLI entry point, Makefile with loud stubs

**Files:**
- Create: `pyproject.toml`, `.python-version`, `uv.lock`, `src/night_tape/__init__.py`, `src/night_tape/cli.py`, `Makefile`, `tests/unit/test_cli.py`, `tests/unit/test_makefile.py`
- Modify: `.gitignore` (append)

**Interfaces:**
- Produces:
  - `night_tape.cli.build_parser() -> argparse.ArgumentParser`
  - `night_tape.cli.main(argv: Sequence[str] | None = None) -> int`
- Every subcommand sets `handler=<fn(args) -> int>` via `set_defaults`.
- The Makefile variables `FREEZE_STEPS`, `RELEASE_STEPS` and `STUBS` are read by `tests/unit/test_makefile.py`.

- [ ] **Step 1: Branch and SSH commit signing** (gpg is not installed; use SSH signing)

```bash
cd /Users/sunnyyadav/Projects/night-tape
git switch -c week1-foundations
test -f ~/.ssh/id_ed25519.pub || ssh-keygen -t ed25519 -C "night-tape signing"
git config gpg.format ssh
git config user.signingkey ~/.ssh/id_ed25519.pub
git config commit.gpgsign true
git config tag.gpgsign true
mkdir -p ~/.config/git
echo "$(git config user.email) $(cat ~/.ssh/id_ed25519.pub)" >> ~/.config/git/allowed_signers
git config gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers
```

Ask the user before running `gh ssh-key add ~/.ssh/id_ed25519.pub --type signing --title night-tape-signing`. That command registers the key with GitHub, which is what shows commits as "Verified".

- [ ] **Step 2: Write `pyproject.toml` and the package marker**

```toml
[project]
name = "night-tape"
version = "0.1.0"
description = "Preregistered measurement of US overnight execution quality on BOATS"
requires-python = ">=3.12,<3.13"
dependencies = []

[project.scripts]
night-tape = "night_tape.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/night_tape"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]

[tool.mypy]
strict = true
python_version = "3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers --import-mode=importlib"
```

`src/night_tape/__init__.py`:

```python
"""night-tape: preregistered measurement of BOATS overnight execution quality."""
```

- [ ] **Step 3: Pin Python and add dependencies**

```bash
uv python pin 3.12
uv add httpx "jsonschema[format-nongpl]" pyyaml playwright databento
uv add --dev pytest ruff mypy pre-commit detect-secrets types-PyYAML types-jsonschema
V=$(uv tree --depth 1 | sed -n 's/.*databento v\([0-9][0-9.]*\).*/\1/p' | head -1)
uv add "databento==$V"
grep databento pyproject.toml
```

Expected: `"databento==X.Y.Z"` (weekly §3: pin the exact SDK version at scaffold time).

- [ ] **Step 4: Write the failing CLI test** — `tests/unit/test_cli.py`

```python
import pytest

from night_tape.cli import main


def test_help_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "night-tape" in capsys.readouterr().out


def test_a_command_is_required() -> None:
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
```

- [ ] **Step 5: Run it and watch it fail**

Run: `uv run pytest tests/unit/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'night_tape.cli'`

- [ ] **Step 6: Write `src/night_tape/cli.py`**

```python
"""night-tape command line. Each command group is registered by one _add_* function."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from importlib.metadata import version

Handler = Callable[[argparse.Namespace], int]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="night-tape", description="night-tape research pipeline")
    parser.add_argument("--version", action="version", version=version("night-tape"))
    parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Handler = args.handler
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 7: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_cli.py -v`
Expected: 2 passed

- [ ] **Step 8: Write the failing Makefile test** — `tests/unit/test_makefile.py`

```python
"""The freeze checklist is code (weekly W1 task 2). Stubs must fail loudly."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# r2.1 §13.1 and §13.2, in order. Dropping a step from the Makefile must fail this test.
R21_FREEZE = [
    "evidence-load-bearing", "source-archive-verify", "test", "pilot-report", "break-report",
    "power-report", "universe-verify", "xnas-cost-decision", "manifest-verify", "qc-report",
    "replication-diagnostic", "preevent-report", "prereg-check", "freeze-archive",
]
R21_RELEASE = [
    "permissions-check", "attribution-check", "public-data-scan", "release-docs", "release-bundle",
]


def make_var(name: str) -> list[str]:
    """Read a Makefile variable by feeding make a one-line helper rule on stdin."""
    result = subprocess.run(
        ["make", "-s", "--no-print-directory", "-f", "Makefile", "-f", "-", f"print-{name}"],
        input="print-%:\n\t@echo $($*)\n",
        capture_output=True, text=True, cwd=ROOT, check=True,
    )
    return result.stdout.split()


def test_freeze_and_release_steps_match_r21() -> None:
    assert make_var("FREEZE_STEPS") == R21_FREEZE
    assert make_var("RELEASE_STEPS") == R21_RELEASE


@pytest.mark.parametrize("target", R21_FREEZE + R21_RELEASE + ["freeze-required", "release-required"])
def test_every_target_exists(target: str) -> None:
    dry = subprocess.run(["make", "-n", "--no-print-directory", target], cwd=ROOT, capture_output=True)
    assert dry.returncode == 0, dry.stderr


def test_stubs_fail_loudly() -> None:
    stubs = make_var("STUBS")
    assert stubs and "test" not in stubs
    for target in stubs:
        result = subprocess.run(
            ["make", "--no-print-directory", target], cwd=ROOT, capture_output=True, text=True
        )
        assert result.returncode != 0, target
        assert f"NOT IMPLEMENTED: {target}" in result.stderr
```

- [ ] **Step 9: Run it and watch it fail**

Run: `uv run pytest tests/unit/test_makefile.py -v`
Expected: FAIL. Without a Makefile, `make` exits 2 with `No targets specified and no makefile found` (or `CalledProcessError`).

- [ ] **Step 10: Write `Makefile`** (recipe lines start with a TAB)

```make
# Targets from technical-plan r2.1 §13. A stub exits non-zero with "NOT IMPLEMENTED: <target>".
# That is the correct state until weekly-build-plan App. A makes the target real.
.DEFAULT_GOAL := test

FREEZE_STEPS := evidence-load-bearing source-archive-verify test pilot-report break-report \
	power-report universe-verify xnas-cost-decision manifest-verify qc-report \
	replication-diagnostic preevent-report prereg-check freeze-archive
RELEASE_STEPS := permissions-check attribution-check public-data-scan release-docs release-bundle

STUBS := evidence-load-bearing source-archive-verify pilot-report break-report power-report \
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

$(STUBS):
	@echo "NOT IMPLEMENTED: $@" >&2; exit 1
```

- [ ] **Step 11: Run the tests and the checklist**

Run: `uv run pytest tests/unit/test_makefile.py -v`
Expected: all pass.

Run: `make test`
Expected: ruff, format and mypy clean; all tests pass.

Run: `make freeze-required; echo "exit=$?"`
Expected: `NOT IMPLEMENTED: evidence-load-bearing`, then `exit=2`. That is the correct Week 1 state.

- [ ] **Step 12: Confirm the ignore rules.** The project section at the end of `.gitignore` already exists; it was added before the build.

Run: `git check-ignore -v data/raw/x.dbn.zst out.parquet .env.local key.pem .DS_Store .claude/settings.local.json`
Expected: every path is reported as ignored.

Run: `git check-ignore uv.lock .python-version .secrets.baseline evidence/manifest.jsonl; echo "exit=$?"`
Expected: no output and `exit=1`, which means none of them is ignored.

- [ ] **Step 13: Commit (signed)**

```bash
git add .gitignore pyproject.toml uv.lock .python-version Makefile src tests CLAUDE.md docs
git commit -S -m "chore: scaffold night-tape package, CLI entry point and loud freeze stubs"
git log --show-signature -1 | head -3
```

Expected: `Good "git" signature`.

---

### Task 2: Hygiene: fixture guard, pre-commit, secrets, CI, Docker

**Files:**
- Create: `src/night_tape/fixture_guard.py`, `tests/unit/test_fixture_guard.py`, `.pre-commit-config.yaml`, `.secrets.baseline`, `.gitattributes`, `.github/workflows/ci.yml`, `Dockerfile`, `.dockerignore`

**Interfaces:**
- Produces:
  - `night_tape.fixture_guard.is_synthetic(path: Path) -> bool`
  - `night_tape.fixture_guard.main(argv: Sequence[str] | None = None) -> int`
  - A GitHub Actions job named `test`, which becomes the required status check.

- [ ] **Step 1: Write the failing guard tests** — `tests/unit/test_fixture_guard.py`

```python
from pathlib import Path

import pytest

from night_tape.fixture_guard import is_synthetic, main

ROOT = Path(__file__).resolve().parents[2]


def test_header_on_first_line_is_accepted(tmp_path: Path) -> None:
    f = tmp_path / "f01.yaml"
    f.write_text("synthetic: true\ntrades: []\n")
    assert is_synthetic(f)


def test_header_anywhere_else_is_rejected(tmp_path: Path) -> None:
    f = tmp_path / "real.yaml"
    f.write_text("trades: []\nsynthetic: true\n")
    assert not is_synthetic(f)


def test_empty_and_binary_files_are_rejected(tmp_path: Path) -> None:
    empty = tmp_path / "empty.yaml"
    empty.write_text("")
    raw = tmp_path / "raw.dbn.zst"
    raw.write_bytes(b"\x28\xb5\x2f\xfd\x00\xff")  # zstd magic: real market data never passes
    assert not is_synthetic(empty)
    assert not is_synthetic(raw)


def test_main_reports_every_bad_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = tmp_path / "good.yaml"
    good.write_text("synthetic: true\n")
    bad = tmp_path / "bad.yaml"
    bad.write_text("x: 1\n")
    assert main([str(good), str(bad)]) == 1
    err = capsys.readouterr().err
    assert "bad.yaml" in err and "good.yaml" not in err


def test_repo_fixture_tree_is_synthetic() -> None:
    fixtures = ROOT / "tests" / "fixtures"
    files = [p for p in fixtures.rglob("*") if p.is_file()] if fixtures.exists() else []
    assert [str(p) for p in files if not is_synthetic(p)] == []
```

- [ ] **Step 2: Run them and watch them fail**

Run: `uv run pytest tests/unit/test_fixture_guard.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'night_tape.fixture_guard'`

- [ ] **Step 3: Write `src/night_tape/fixture_guard.py`**

```python
"""Reject any tests/fixtures file whose first line is not `synthetic: true`.

Real BOATS/Databento messages must never enter the repository (licensing, weekly W1).
Runs as a pre-commit hook and, via tests/unit/test_fixture_guard.py, in CI.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

HEADER = "synthetic: true"


def is_synthetic(path: Path) -> bool:
    try:
        with path.open(encoding="utf-8") as f:
            return f.readline().rstrip("\r\n") == HEADER
    except UnicodeDecodeError:
        return False  # binary files (e.g. .dbn.zst) can never carry the header


def main(argv: Sequence[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else list(argv)
    bad = [p for p in paths if not is_synthetic(Path(p))]
    for p in bad:
        print(f"{p}: first line must be '{HEADER}' (tests/fixtures is synthetic-only)", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_fixture_guard.py -v`
Expected: 5 passed

- [ ] **Step 5: Write `.gitattributes`**

```gitattributes
# Archived evidence is byte-exact (SHA-256 in evidence/manifest.jsonl): no EOL conversion, no text diffs.
evidence/** -text -diff
```

- [ ] **Step 6: Write `.pre-commit-config.yaml`.** Ruff and detect-secrets run through `uv run`, so there is exactly one version of each: the one pinned in `uv.lock`.

```yaml
# evidence/ is never touched: fixers would change archived bytes and break their SHA-256.
exclude: ^evidence/
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-added-large-files
        args: ["--maxkb=1024"]
      - id: check-yaml
      - id: check-json
      - id: end-of-file-fixer
      - id: trailing-whitespace
        exclude: \.md$
  - repo: local
    hooks:
      - id: ruff
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]
      - id: detect-secrets
        name: detect-secrets
        entry: uv run detect-secrets-hook --baseline .secrets.baseline
        language: system
        exclude: ^(uv\.lock|registry/.*)$  # registry holds sha256 evidence hashes, not secrets
      - id: synthetic-fixtures
        name: tests/fixtures must be synthetic
        entry: uv run python -m night_tape.fixture_guard
        language: system
        files: ^tests/fixtures/
```

- [ ] **Step 7: Write `.github/workflows/ci.yml`**

```yaml
name: ci
on:
  push:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          version: "0.7.12"
      - run: uv sync --frozen
      - run: uv run playwright install --with-deps chromium
      - run: uv run pre-commit run --all-files --show-diff-on-failure
      - run: make test
```

The job has no secrets. CI never calls a paid API.

- [ ] **Step 8: Pin the Docker base image by digest**

```bash
docker pull python:3.12-slim-bookworm
docker inspect --format '{{index .RepoDigests 0}}' python:3.12-slim-bookworm
```

Expected: `python@sha256:<64 hex>`. Copy that `sha256:…` value into the `FROM` line in the next step.

- [ ] **Step 9: Write `Dockerfile` and `.dockerignore`**

`Dockerfile`:

```dockerfile
# Freeze image for the Week 6 clean-room dry run. Record this digest in the freeze archive.
FROM python:3.12-slim-bookworm@sha256:PASTE_DIGEST_FROM_STEP_8
COPY --from=ghcr.io/astral-sh/uv:0.7.12 /uv /uvx /bin/
ENV TZ=UTC LANG=C.UTF-8 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_PROJECT_ENVIRONMENT=/opt/venv
RUN apt-get update && apt-get install -y --no-install-recommends make git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project
RUN uv run --no-sync playwright install --with-deps chromium
COPY . .
RUN uv sync --frozen
CMD ["make", "test"]
```

`.dockerignore`:

```text
.venv/
data/
site/
.env
.envrc
```

- [ ] **Step 10: Build and run the image**

Run: `docker build -t night-tape:w1 . && docker run --rm night-tape:w1`
Expected: `make test` passes inside the container. Before building, grep the Dockerfile for `PASTE_DIGEST`; there must be no match.

- [ ] **Step 11: Create the secrets baseline (after the Dockerfile digest exists) and install the hooks**

```bash
uv run detect-secrets scan --exclude-files '^(uv\.lock|registry/.*|evidence/.*)$' > .secrets.baseline
uv run pre-commit autoupdate
uv run pre-commit install
uv run pre-commit run --all-files
```

Expected: every hook passes. If `end-of-file-fixer` rewrote files, re-run it; the second run passes. Open `.secrets.baseline` and confirm that every entry under `results` is a false positive, such as the Dockerfile digest or a hash in a doc. If any entry is a real secret, stop and tell the user.

- [ ] **Step 12: Commit (signed)**

```bash
git add src/night_tape/fixture_guard.py tests/unit/test_fixture_guard.py .gitattributes \
  .pre-commit-config.yaml .secrets.baseline .github Dockerfile .dockerignore
git commit -S -m "chore: add fixture guard, pre-commit, secret scan, CI and pinned freeze image"
```

- [ ] **Step 13: Push the branch and protect `main`.** Ask the user first: this publishes to GitHub.

```bash
git push -u origin week1-foundations
```

Then, in GitHub → Settings → Branches (or Rules) → add a rule for `main` with these settings:
- require a pull request;
- require status check `test`;
- require signed commits;
- block force pushes.

---

### Task 3: Contracts

**Files:**
- Create: `contracts/trade.schema.json`, `contracts/quote.schema.json`, `contracts/claim_registry.schema.json`, `contracts/event_registry.schema.json`, `contracts/tracker_entry.schema.json`, `src/night_tape/contracts.py`, `tests/unit/test_contracts.py`

**Interfaces:**
- Produces:
  - `night_tape.contracts.CONTRACTS_DIR: Path`
  - `schema(name: str) -> dict[str, Any]`
  - `validator(name: str) -> Draft202012Validator` (cached; checks the schema itself)
  - `errors(name: str, instance: object) -> list[str]` (sorted `"<json_path>: <message>"`)
  - `validate(name: str, instance: object) -> None` (raises `ContractError`)
  - `source_classes() -> list[str]`
  - `class ContractError(ValueError)` with attributes `.name` and `.errors`
- Contract names: `trade`, `quote`, `claim_registry`, `event_registry`, `tracker_entry`.

- [ ] **Step 1: Write the failing contract tests** — `tests/unit/test_contracts.py`

```python
from typing import Any

import pytest

from night_tape import contracts

INT64_MAX = 2**63 - 1
NAMES = ["trade", "quote", "claim_registry", "event_registry", "tracker_entry"]


def trade(**over: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "trade_id": "OCEA.MEMOIR:S1:SPY:1:7:0", "symbol": "SPY", "venue": "BOATS",
        "instrument_id": 1, "ts_event": 1_790_000_000_000_000_000,
        "ts_recv": 1_790_000_000_000_000_100, "sequence": 7, "record_idx": 0,
        "price_int": 500_010_000_000, "size": 100, "side_raw": "B", "aggressor_direction": 1,
        "bid_px_pre_int": 500_000_000_000, "ask_px_pre_int": 500_020_000_000,
        "wall_clock_execution_date": "2026-09-21", "venue_trade_date": "2026-09-21",
        "finra_reporting_date": "2026-09-21", "nscc_clearing_business_date": "2026-09-21",
        "session_id": "S1", "rule_version": "BOATS_POST_2026_09_10",
        "source_dataset": "OCEA.MEMOIR", "source_schema": "tbbo", "manifest_id": "m1",
    }
    row.update(over)
    return row


def quote(**over: Any) -> dict[str, Any]:
    q: dict[str, Any] = {
        "symbol": "SPY", "venue": "BOATS", "instrument_id": 1,
        "ts_event": 1_790_000_000_000_000_000, "ts_recv": 1_790_000_000_000_000_100,
        "sequence": 7, "record_idx": 0, "bid_px_int": 500_000_000_000,
        "ask_px_int": 500_020_000_000, "bid_sz": 100, "ask_sz": 200,
        "midpoint_x2_int": 1_000_020_000_000, "quote_age_ns": None, "book_state": "TWO_SIDED",
        "session_id": "S1", "rule_version": "BOATS_POST_2026_09_10",
        "source_dataset": "OCEA.MEMOIR", "source_schema": "mbp-1", "manifest_id": "m1",
    }
    q.update(over)
    return q


def claim(**over: Any) -> dict[str, Any]:
    c: dict[str, Any] = {
        "claim_id": "C-OCEA-SHARED-SEQUENCE",
        "claim_text": "Records normalized from one native MEMOIR message share the same sequence.",
        "claim_type": "data_semantics", "load_bearing": True,
        "affects": ["metric_semantics"], "status": "UNVERIFIED",
    }
    c.update(over)
    return c


def event(**over: Any) -> dict[str, Any]:
    ev: dict[str, Any] = {
        "event_id": "E-BOATS-OOB-NONDISPLAYED-2026-07-20", "entity": "BOATS",
        "field": "price_band_rule",
        "value": {"aspect": "out_of_band_passive_handling", "action": "ACCEPT_NON_DISPLAYED"},
        "status": "CURRENT", "effective_granularity": "day",
        "effective_from": "2026-07-20", "effective_to": None,
        "claim_ids": ["C-BOATS-2026-07-20-OOB-NONDISPLAYED"], "load_bearing": True,
    }
    ev.update(over)
    return ev


def tracker(**over: Any) -> dict[str, Any]:
    t = event(
        evidence_refs=[{
            "source_id": "blue-ocean-service-status", "span_id": "s-12", "sha256": "a" * 64,
            "retrieved_at": "2026-09-22T12:00:00Z", "supports": ["value", "effective_from", "status"],
        }],
        proposed_by="manual", provider_version=None,
        approved_by="SY", approved_at="2026-09-23T09:00:00Z",
    )
    t.update(over)
    return t


def events(*evs: dict[str, Any]) -> dict[str, Any]:
    return {"events": list(evs), "rule_versions": []}


@pytest.mark.parametrize("name", NAMES)
def test_every_contract_is_a_valid_2020_12_schema(name: str) -> None:
    contracts.validator(name)  # raises SchemaError if the schema itself is malformed


def test_valid_examples_pass() -> None:
    assert contracts.errors("trade", trade()) == []
    assert contracts.errors("quote", quote()) == []
    assert contracts.errors("claim_registry", {"claims": [claim()]}) == []
    assert contracts.errors("event_registry", events(event())) == []
    assert contracts.errors("tracker_entry", tracker()) == []


def test_trade_rejects_undef_price_sentinel() -> None:
    assert any("price_int" in e for e in contracts.errors("trade", trade(price_int=INT64_MAX)))


@pytest.mark.parametrize("side, direction", [("B", -1), ("A", 1), ("N", 1), ("B", None)])
def test_trade_side_and_direction_must_agree(side: str, direction: int | None) -> None:
    assert contracts.errors("trade", trade(side_raw=side, aggressor_direction=direction))


def test_trade_requires_all_four_dates_and_no_generic_date() -> None:
    row = trade()
    del row["nscc_clearing_business_date"]
    assert contracts.errors("trade", row)
    assert contracts.errors("trade", trade(date="2026-09-21"))


def test_quote_book_state_rules() -> None:
    assert contracts.errors("quote", quote(book_state="ONE_SIDED", ask_px_int=None))  # midpoint set
    ok_one_sided = quote(book_state="ONE_SIDED", ask_px_int=None, midpoint_x2_int=None)
    assert contracts.errors("quote", ok_one_sided) == []
    both_null = quote(book_state="ONE_SIDED", bid_px_int=None, ask_px_int=None, midpoint_x2_int=None)
    assert contracts.errors("quote", both_null)
    assert contracts.errors("quote", quote(book_state="EMPTY", midpoint_x2_int=None))  # prices set
    assert contracts.errors("quote", quote(midpoint_x2_int=None))  # TWO_SIDED needs a midpoint


def test_claim_rules() -> None:
    assert contracts.errors("claim_registry", {"claims": [claim(status="VERIFIED")]})
    contradictory = claim(affects=["context_only"], load_bearing=True)
    assert contracts.errors("claim_registry", {"claims": [contradictory]})
    assert contracts.errors("claim_registry", {"claims": [claim(affects=["vibes"])]})
    verified = claim(
        status="VERIFIED", source_class="VENDOR_DOC", source_id="databento-ocea-memoir",
        retrieved_at="2026-09-22T12:00:00Z", sha256="b" * 64,
    )
    assert contracts.errors("claim_registry", {"claims": [verified]}) == []


def test_event_rules() -> None:
    reg = "event_registry"
    assert contracts.errors(reg, events(event(effective_from="2026-07-20T00:00:00Z")))  # day gran.
    erroneous = event(status="ERRONEOUS_DISCLOSURE")  # must be granularity never, null dates
    assert contracts.errors(reg, events(erroneous))
    assert contracts.errors(reg, events(event(status="CONFLICTED")))  # needs conflicts_with
    assert contracts.errors(reg, events(event(colour="blue")))  # closed object
    assert contracts.errors(reg, events(event(entity="NYSE")))


def test_tracker_rules() -> None:
    assert contracts.errors("tracker_entry", tracker(status="PENDING_VERIFICATION"))
    no_span = tracker()
    no_span["evidence_refs"][0].pop("span_id")
    assert contracts.errors("tracker_entry", no_span)
    assert contracts.errors("tracker_entry", tracker(provider_version="v1"))  # manual → null
    assert contracts.errors("tracker_entry", tracker(colour="blue"))
    assert contracts.errors("tracker_entry", tracker(evidence_refs=[]))


def test_formats_are_enforced() -> None:
    assert contracts.errors("tracker_entry", tracker(approved_at="yesterday"))
    assert contracts.errors("trade", trade(venue_trade_date="21/09/2026"))


def test_validate_raises_with_paths() -> None:
    with pytest.raises(contracts.ContractError) as exc:
        contracts.validate("trade", trade(size=0))
    assert exc.value.name == "trade"
    assert any("size" in e for e in exc.value.errors)


def test_source_classes_come_from_the_claim_contract() -> None:
    assert "SEC_FORM_ATS_N" in contracts.source_classes()
```

- [ ] **Step 2: Run them and watch them fail**

Run: `uv run pytest tests/unit/test_contracts.py -v`
Expected: FAIL with `ImportError: cannot import name 'contracts'`

- [ ] **Step 3: Write `contracts/trade.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://night-tape.invalid/contracts/trade.schema.json",
  "title": "Canonical trade row (r2.1 §7, §8.1 + weekly §1.3 record_idx, trade_id)",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "trade_id", "symbol", "venue", "instrument_id", "ts_event", "ts_recv", "sequence",
    "record_idx", "price_int", "size", "side_raw", "aggressor_direction", "bid_px_pre_int",
    "ask_px_pre_int", "wall_clock_execution_date", "venue_trade_date", "finra_reporting_date",
    "nscc_clearing_business_date", "session_id", "rule_version", "source_dataset",
    "source_schema", "manifest_id"
  ],
  "properties": {
    "trade_id": {"type": "string", "minLength": 1, "description": "Deterministic; defined by Week 2 normalization"},
    "symbol": {"type": "string", "minLength": 1},
    "venue": {"type": "string", "minLength": 1},
    "instrument_id": {"$ref": "#/$defs/nonneg_int64", "description": "Session-scoped on OCEA; never join across sessions"},
    "ts_event": {"$ref": "#/$defs/nonneg_int64", "description": "ns since Unix epoch, venue event time"},
    "ts_recv": {"$ref": "#/$defs/nonneg_int64"},
    "sequence": {"$ref": "#/$defs/nonneg_int64"},
    "record_idx": {"$ref": "#/$defs/nonneg_int64", "description": "Position in source file; breaks (ts_event, sequence) ties"},
    "price_int": {"$ref": "#/$defs/px"},
    "size": {"type": "integer", "minimum": 1},
    "side_raw": {"enum": ["A", "B", "N"]},
    "aggressor_direction": {"enum": [1, -1, null]},
    "bid_px_pre_int": {"anyOf": [{"$ref": "#/$defs/px"}, {"type": "null"}]},
    "ask_px_pre_int": {"anyOf": [{"$ref": "#/$defs/px"}, {"type": "null"}]},
    "wall_clock_execution_date": {"type": "string", "format": "date"},
    "venue_trade_date": {"type": "string", "format": "date"},
    "finra_reporting_date": {"type": "string", "format": "date"},
    "nscc_clearing_business_date": {"type": "string", "format": "date"},
    "session_id": {"type": "string", "minLength": 1},
    "rule_version": {"type": "string", "minLength": 1},
    "source_dataset": {"type": "string", "minLength": 1},
    "source_schema": {"type": "string", "minLength": 1},
    "manifest_id": {"type": "string", "minLength": 1}
  },
  "allOf": [
    {"if": {"properties": {"side_raw": {"const": "B"}}}, "then": {"properties": {"aggressor_direction": {"const": 1}}}},
    {"if": {"properties": {"side_raw": {"const": "A"}}}, "then": {"properties": {"aggressor_direction": {"const": -1}}}},
    {"if": {"properties": {"side_raw": {"const": "N"}}}, "then": {"properties": {"aggressor_direction": {"const": null}}}}
  ],
  "$defs": {
    "nonneg_int64": {"type": "integer", "minimum": 0, "maximum": 9223372036854775807},
    "px": {
      "type": "integer",
      "minimum": -9223372036854775808,
      "exclusiveMaximum": 9223372036854775807,
      "description": "Fixed-point, 1 unit = 1e-9 USD. UNDEF_PRICE (int64 max) must be NULL before this layer"
    }
  }
}
```

- [ ] **Step 4: Write `contracts/quote.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://night-tape.invalid/contracts/quote.schema.json",
  "title": "Canonical quote-state row (r2.1 §8.2 + weekly §1.3 record_idx)",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "symbol", "venue", "instrument_id", "ts_event", "ts_recv", "sequence", "record_idx",
    "bid_px_int", "ask_px_int", "bid_sz", "ask_sz", "midpoint_x2_int", "quote_age_ns",
    "book_state", "session_id", "rule_version", "source_dataset", "source_schema", "manifest_id"
  ],
  "properties": {
    "symbol": {"type": "string", "minLength": 1},
    "venue": {"type": "string", "minLength": 1},
    "instrument_id": {"$ref": "#/$defs/nonneg_int64"},
    "ts_event": {"$ref": "#/$defs/nonneg_int64"},
    "ts_recv": {"$ref": "#/$defs/nonneg_int64"},
    "sequence": {"$ref": "#/$defs/nonneg_int64"},
    "record_idx": {"$ref": "#/$defs/nonneg_int64"},
    "bid_px_int": {"anyOf": [{"$ref": "#/$defs/px"}, {"type": "null"}]},
    "ask_px_int": {"anyOf": [{"$ref": "#/$defs/px"}, {"type": "null"}]},
    "bid_sz": {"$ref": "#/$defs/nonneg_int64"},
    "ask_sz": {"$ref": "#/$defs/nonneg_int64"},
    "midpoint_x2_int": {"type": ["integer", "null"], "description": "bid + ask; set only when bid < ask"},
    "quote_age_ns": {"anyOf": [{"$ref": "#/$defs/nonneg_int64"}, {"type": "null"}]},
    "book_state": {"enum": ["EMPTY", "ONE_SIDED", "LOCKED", "CROSSED", "TWO_SIDED"]},
    "session_id": {"type": "string", "minLength": 1},
    "rule_version": {"type": "string", "minLength": 1},
    "source_dataset": {"type": "string", "minLength": 1},
    "source_schema": {"type": "string", "minLength": 1},
    "manifest_id": {"type": "string", "minLength": 1}
  },
  "allOf": [
    {
      "if": {"properties": {"book_state": {"const": "EMPTY"}}},
      "then": {"properties": {"bid_px_int": {"type": "null"}, "ask_px_int": {"type": "null"}}}
    },
    {
      "if": {"properties": {"book_state": {"const": "ONE_SIDED"}}},
      "then": {"oneOf": [
        {"properties": {"bid_px_int": {"type": "null"}, "ask_px_int": {"$ref": "#/$defs/px"}}},
        {"properties": {"bid_px_int": {"$ref": "#/$defs/px"}, "ask_px_int": {"type": "null"}}}
      ]}
    },
    {
      "if": {"properties": {"book_state": {"enum": ["LOCKED", "CROSSED", "TWO_SIDED"]}}},
      "then": {"properties": {"bid_px_int": {"$ref": "#/$defs/px"}, "ask_px_int": {"$ref": "#/$defs/px"}}}
    },
    {
      "if": {"properties": {"book_state": {"const": "TWO_SIDED"}}},
      "then": {"properties": {"midpoint_x2_int": {"type": "integer"}}},
      "else": {"properties": {"midpoint_x2_int": {"type": "null"}}}
    }
  ],
  "$defs": {
    "nonneg_int64": {"type": "integer", "minimum": 0, "maximum": 9223372036854775807},
    "px": {"type": "integer", "minimum": -9223372036854775808, "exclusiveMaximum": 9223372036854775807}
  }
}
```

- [ ] **Step 5: Write `contracts/claim_registry.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://night-tape.invalid/contracts/claim_registry.schema.json",
  "title": "Claim register (r2.1 §6.2)",
  "type": "object",
  "additionalProperties": false,
  "required": ["claims"],
  "properties": {"claims": {"type": "array", "items": {"$ref": "#/$defs/claim"}}},
  "$defs": {
    "claim": {
      "type": "object",
      "additionalProperties": false,
      "required": ["claim_id", "claim_text", "claim_type", "load_bearing", "affects", "status"],
      "properties": {
        "claim_id": {"type": "string", "pattern": "^C-[A-Z0-9-]+$"},
        "claim_text": {"type": "string", "minLength": 1},
        "claim_type": {"enum": ["venue_mechanics", "schedule", "regulatory_status", "data_semantics", "statistic", "citation"]},
        "load_bearing": {"type": "boolean"},
        "affects": {
          "type": "array", "minItems": 1, "uniqueItems": true,
          "items": {"enum": [
            "primary_endpoint", "identification", "sample", "session_logic", "date_logic",
            "metric_semantics", "data_quality", "cost", "publication", "context_only"
          ]}
        },
        "status": {"enum": ["UNVERIFIED", "VERIFIED", "CONFLICTED", "CONTINGENCY", "PENDING", "REFUTED"]},
        "source_class": {"$ref": "#/$defs/source_class"},
        "source_id": {"type": ["string", "null"], "description": "A config/monitoring.yaml source_id"},
        "source_version_or_accession": {"type": ["string", "null"]},
        "effective_from": {"type": ["string", "null"], "format": "date"},
        "effective_to": {"type": ["string", "null"], "format": "date"},
        "retrieved_at": {"type": ["string", "null"], "format": "date-time"},
        "sha256": {"type": ["string", "null"], "pattern": "^[0-9a-f]{64}$"},
        "recheck_trigger": {"type": ["string", "null"]},
        "notes": {"type": ["string", "null"]}
      },
      "allOf": [
        {
          "if": {"properties": {"status": {"const": "VERIFIED"}}},
          "then": {
            "required": ["source_class", "source_id", "retrieved_at", "sha256"],
            "properties": {"source_id": {"type": "string"}, "retrieved_at": {"type": "string"}, "sha256": {"type": "string"}}
          }
        },
        {
          "if": {"properties": {"affects": {"contains": {"const": "context_only"}}}},
          "then": {"properties": {"load_bearing": {"const": false}}}
        }
      ]
    },
    "source_class": {"enum": [
      "SEC_FORM_ATS_N", "SEC_RULE", "SEC_ORDER", "SEC_STAFF", "EXCHANGE_RULE", "EXCHANGE_NOTICE",
      "ATS_SERVICE_ALERT", "SIP_NOTICE", "NSCC_NOTICE", "FINRA", "VENDOR_DOC", "PAPER", "SECONDARY"
    ]}
  }
}
```

- [ ] **Step 6: Write `contracts/event_registry.schema.json`.** Events use `unevaluatedProperties` at the use site, so `tracker_entry` can extend `event` without the extension being rejected as an unknown property.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://night-tape.invalid/contracts/event_registry.schema.json",
  "title": "Market-structure event registry (v2.2 §8.3, r2.1 §7, §23.3-23.4). One registry for research and tracker",
  "type": "object",
  "additionalProperties": false,
  "required": ["events", "rule_versions"],
  "properties": {
    "events": {"type": "array", "items": {"$ref": "#/$defs/event", "unevaluatedProperties": false}},
    "rule_versions": {"type": "array", "items": {"$ref": "#/$defs/rule_version"}}
  },
  "$defs": {
    "entity": {"enum": ["NASDAQ", "NYSE_ARCA", "CBOE_EDGX", "24X", "MEMX", "BOATS", "SIP", "LULD", "NSCC", "REG_NMS"]},
    "field": {"enum": [
      "session_hours", "go_live_target", "go_live_actual", "order_types", "time_in_force",
      "trade_date_rule", "price_band_rule", "halt_rule", "clearing_hours", "market_data_status", "reg_status"
    ]},
    "status": {"enum": [
      "PROPOSED", "APPROVED_NOT_EFFECTIVE", "CURRENT", "SUPERSEDED", "WITHDRAWN",
      "ERRONEOUS_DISCLOSURE", "CONFLICTED", "PENDING_VERIFICATION"
    ]},
    "evidence_ref": {
      "type": "object",
      "additionalProperties": false,
      "required": ["source_id", "sha256", "retrieved_at", "supports"],
      "properties": {
        "source_id": {"type": "string", "minLength": 1},
        "source_version_or_accession": {"type": ["string", "null"]},
        "span_id": {"type": ["string", "null"]},
        "span_excerpt": {"type": ["string", "null"], "maxLength": 500},
        "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "retrieved_at": {"type": "string", "format": "date-time"},
        "supports": {
          "type": "array", "minItems": 1, "uniqueItems": true,
          "items": {"enum": ["value", "effective_from", "effective_to", "status"]}
        }
      }
    },
    "event": {
      "type": "object",
      "required": [
        "event_id", "entity", "field", "value", "status", "effective_granularity",
        "effective_from", "effective_to", "claim_ids", "load_bearing"
      ],
      "properties": {
        "event_id": {"type": "string", "pattern": "^E-[A-Z0-9-]+$"},
        "entity": {"$ref": "#/$defs/entity"},
        "field": {"$ref": "#/$defs/field"},
        "value": {"description": "Typed per field: object, date string or enum"},
        "status": {"$ref": "#/$defs/status"},
        "effective_granularity": {"enum": ["timestamp", "day", "unknown", "never"]},
        "effective_from": {"type": ["string", "null"]},
        "effective_to": {"type": ["string", "null"], "description": "Exclusive: the next regime's effective_from"},
        "first_session_applies": {"type": ["string", "null"], "description": "session_id; set in Week 2 when a source gives only a day"},
        "evidence_refs": {"type": "array", "items": {"$ref": "#/$defs/evidence_ref"}},
        "claim_ids": {"type": "array", "minItems": 1, "uniqueItems": true, "items": {"type": "string", "pattern": "^C-[A-Z0-9-]+$"}},
        "supersedes": {"type": ["string", "null"]},
        "conflicts_with": {"type": ["array", "null"], "items": {"type": "string"}},
        "correction_of": {"type": ["string", "null"]},
        "load_bearing": {"type": "boolean"},
        "notes": {"type": ["string", "null"]}
      },
      "allOf": [
        {
          "if": {"properties": {"effective_granularity": {"const": "timestamp"}}},
          "then": {"properties": {
            "effective_from": {"type": "string", "format": "date-time"},
            "effective_to": {"anyOf": [{"type": "null"}, {"type": "string", "format": "date-time"}]}
          }}
        },
        {
          "if": {"properties": {"effective_granularity": {"const": "day"}}},
          "then": {"properties": {
            "effective_from": {"type": "string", "format": "date"},
            "effective_to": {"anyOf": [{"type": "null"}, {"type": "string", "format": "date"}]}
          }}
        },
        {
          "if": {"properties": {"effective_granularity": {"enum": ["unknown", "never"]}}},
          "then": {"properties": {"effective_from": {"type": "null"}, "effective_to": {"type": "null"}}}
        },
        {
          "if": {"properties": {"status": {"enum": ["ERRONEOUS_DISCLOSURE", "WITHDRAWN"]}}},
          "then": {"properties": {"effective_granularity": {"const": "never"}}}
        },
        {
          "if": {"properties": {"status": {"const": "CONFLICTED"}}},
          "then": {"required": ["conflicts_with"], "properties": {"conflicts_with": {"type": "array", "minItems": 1}}}
        }
      ]
    },
    "rule_version": {
      "type": "object",
      "additionalProperties": false,
      "required": ["rule_version", "venue", "effective_granularity", "effective_from", "effective_to", "basis_event_ids", "provisional"],
      "properties": {
        "rule_version": {"type": "string", "pattern": "^[A-Z0-9_]+$"},
        "venue": {"$ref": "#/$defs/entity"},
        "effective_granularity": {"enum": ["timestamp", "day", "unknown"]},
        "effective_from": {"anyOf": [{"type": "null"}, {"type": "string", "format": "date"}, {"type": "string", "format": "date-time"}], "description": "null = unbounded below"},
        "effective_to": {"anyOf": [{"type": "null"}, {"type": "string", "format": "date"}, {"type": "string", "format": "date-time"}], "description": "Exclusive; null = open"},
        "basis_event_ids": {"type": "array", "items": {"type": "string"}},
        "provisional": {"type": "boolean"},
        "notes": {"type": ["string", "null"]}
      }
    }
  }
}
```

- [ ] **Step 7: Write `contracts/tracker_entry.schema.json`** (T0: the same registry event, plus provenance and approval)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://night-tape.invalid/contracts/tracker_entry.schema.json",
  "title": "Public tracker entry (r2.1 §23.4): a registry event + provenance + approval; shape half of gate G6",
  "type": "object",
  "allOf": [{"$ref": "event_registry.schema.json#/$defs/event"}],
  "required": ["proposed_by", "provider_version", "approved_by", "approved_at", "evidence_refs"],
  "properties": {
    "proposed_by": {"enum": ["manual", "structured_llm", "jev"]},
    "provider_version": {"type": ["string", "null"]},
    "approved_by": {"type": "string", "minLength": 1},
    "approved_at": {"type": "string", "format": "date-time"},
    "status": {"not": {"const": "PENDING_VERIFICATION"}},
    "evidence_refs": {
      "type": "array", "minItems": 1,
      "items": {"required": ["span_id"], "properties": {"span_id": {"type": "string", "minLength": 1}}}
    }
  },
  "if": {"properties": {"proposed_by": {"const": "manual"}}},
  "then": {"properties": {"provider_version": {"type": "null"}}},
  "else": {"properties": {"provider_version": {"type": "string", "minLength": 1}}},
  "unevaluatedProperties": false
}
```

- [ ] **Step 8: Write `src/night_tape/contracts.py`**

```python
"""Load JSON-Schema contracts from contracts/ and validate instances against them.

All schemas are registered by $id, so cross-file $refs (tracker_entry → event_registry)
resolve locally; nothing is ever fetched over the network.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# src/night_tape/contracts.py → repo root. Valid for the editable install uv creates.
CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "contracts"


class ContractError(ValueError):
    def __init__(self, name: str, errors: list[str]) -> None:
        super().__init__(f"{name}: " + "; ".join(errors))
        self.name = name
        self.errors = errors


@cache
def schema(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((CONTRACTS_DIR / f"{name}.schema.json").read_text("utf-8"))
    return data


@cache
def _registry() -> Registry[Any]:
    names = sorted(p.name.removesuffix(".schema.json") for p in CONTRACTS_DIR.glob("*.schema.json"))
    return Registry().with_resources(
        (schema(n)["$id"], Resource.from_contents(schema(n), default_specification=DRAFT202012))
        for n in names
    )


@cache
def validator(name: str) -> Draft202012Validator:
    s = schema(name)
    Draft202012Validator.check_schema(s)
    return Draft202012Validator(
        s, registry=_registry(), format_checker=Draft202012Validator.FORMAT_CHECKER
    )


def errors(name: str, instance: object) -> list[str]:
    return sorted(f"{e.json_path}: {e.message}" for e in validator(name).iter_errors(instance))


def validate(name: str, instance: object) -> None:
    if errs := errors(name, instance):
        raise ContractError(name, errs)


def source_classes() -> list[str]:
    return list(schema("claim_registry")["$defs"]["source_class"]["enum"])
```

- [ ] **Step 9: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_contracts.py -v`
Expected: all pass.

If `test_formats_are_enforced` fails on `approved_at`, the `format-nongpl` extra isn't installed. Run `uv add "jsonschema[format-nongpl]"`. If mypy rejects the `Registry[Any]` annotation, keep the annotation and add `# type: ignore[type-arg]` only on that line.

- [ ] **Step 10: Full check and commit**

```bash
make test
git add contracts src/night_tape/contracts.py tests/unit/test_contracts.py
git commit -S -m "feat: add trade, quote, claim, event and tracker contracts"
```

---

### Task 4: Evidence core: manifest, HTTP fetch, manual add, verify

**Files:**
- Create: `src/night_tape/evidence/__init__.py`, `src/night_tape/evidence/manifest.py`, `src/night_tape/evidence/fetch.py`, `src/night_tape/evidence/verify.py`, `tests/unit/test_manifest.py`
- Modify: `src/night_tape/cli.py`

**Interfaces:**
- Consumes: `night_tape.contracts.source_classes()`
- Produces:
  - `manifest.MANIFEST = "manifest.jsonl"`, `manifest.METHODS`
  - `@dataclass(frozen=True) manifest.Entry` with fields `source_id`, `source_class`, `canonical_url`, `retrieved_at_utc`, `local_path`, `sha256`, `content_type`, `method`, `published_or_filed_at`, `edgar_accession`, `supersedes`, `notes`
  - `manifest.read(evidence_dir: Path) -> list[Entry]`
  - `manifest.sha256_file(path: Path) -> str`
  - `manifest.store(evidence_dir, data: bytes, *, source_id, source_class, canonical_url, content_type, method, filename, subdir=None, edgar_accession=None, published_or_filed_at=None, supersedes=None, notes=None) -> tuple[Entry, bool]`
  - `fetch.USER_AGENT_ENV`
  - `fetch.user_agent() -> str`
  - `fetch.make_client(transport: httpx.BaseTransport | None = None) -> httpx.Client`
  - `fetch.fetch_bytes(client, url) -> httpx.Response`
  - `fetch.content_type(resp) -> str`
  - `fetch.fetch(evidence_dir, client, url, *, source_id, source_class, supersedes=None, notes=None) -> tuple[Entry, bool]`
  - `fetch.add_file(evidence_dir, path, *, url, source_id, source_class, content_type=None, notes=None) -> tuple[Entry, bool]`
  - `verify.Report` with fields `missing`, `mismatched`, `orphans` and `unarchived_sources`, plus `.ok`
  - `verify.verify(evidence_dir: Path, required_source_ids: Iterable[str] = ()) -> Report`
- Rules:
  - `local_path` is relative to `evidence_dir.parent`, e.g. `evidence/VENDOR_DOC/databento-tbbo/20260922T120000Z-ab12cd34ef56-tbbo.html`.
  - A re-fetch is a no-op when the latest entry for the same `(canonical_url, method)` has the same sha256.

- [ ] **Step 1: Write the failing tests** — `tests/unit/test_manifest.py`

```python
import json
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest

from night_tape.cli import main
from night_tape.evidence import fetch, manifest, verify

URL = "https://databento.com/docs/schemas-and-data-formats/tbbo"


def client_for(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def serve(*bodies: bytes) -> httpx.Client:
    it = iter(bodies)
    return client_for(lambda r: httpx.Response(200, content=next(it), headers={"content-type": "text/html; charset=utf-8"}))


def do_fetch(ev: Path, client: httpx.Client, url: str = URL) -> tuple[manifest.Entry, bool]:
    return fetch.fetch(ev, client, url, source_id="databento-tbbo", source_class="VENDOR_DOC")


def test_fetch_archives_exact_bytes_and_one_manifest_line(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    entry, created = do_fetch(ev, serve(b"<html>v1</html>"))
    assert created
    stored = tmp_path / entry.local_path
    assert stored.read_bytes() == b"<html>v1</html>"
    assert entry.sha256 == manifest.sha256_file(stored)
    assert entry.local_path.startswith("evidence/VENDOR_DOC/databento-tbbo/")
    assert (entry.content_type, entry.method, entry.canonical_url) == ("text/html", "http", URL)
    lines = (ev / manifest.MANIFEST).read_text().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["sha256"] == entry.sha256


def test_refetch_with_same_bytes_is_a_noop(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    first, _ = do_fetch(ev, serve(b"same"))
    second, created = do_fetch(ev, serve(b"same"))
    assert not created and second == first
    assert len(manifest.read(ev)) == 1


def test_refetch_with_changed_bytes_adds_a_snapshot_and_keeps_the_old_one(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    old, _ = do_fetch(ev, serve(b"alert v1"))
    new, created = do_fetch(ev, serve(b"alert v2"))
    assert created and old.local_path != new.local_path
    assert (tmp_path / old.local_path).read_bytes() == b"alert v1"
    assert (tmp_path / new.local_path).read_bytes() == b"alert v2"
    assert [e.sha256 for e in manifest.read(ev)] == [old.sha256, new.sha256]


def test_http_error_is_not_archived(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    with pytest.raises(httpx.HTTPStatusError):
        do_fetch(ev, client_for(lambda r: httpx.Response(404, text="not found")))
    assert manifest.read(ev) == []
    assert not ev.exists() or not any(p.is_file() for p in ev.rglob("*"))


def test_redirect_is_recorded(tmp_path: Path) -> None:
    def handler(r: httpx.Request) -> httpx.Response:
        if r.url.path == "/old":
            return httpx.Response(301, headers={"location": "https://example.org/new.pdf"})
        return httpx.Response(200, content=b"%PDF-1.7", headers={"content-type": "application/pdf"})

    entry, _ = do_fetch(tmp_path / "evidence", client_for(handler), "https://example.org/old")
    assert entry.canonical_url == "https://example.org/old"
    assert entry.notes is not None and "redirected to https://example.org/new.pdf" in entry.notes
    assert entry.local_path.endswith("new.pdf")


def test_add_file_registers_a_hand_download(tmp_path: Path) -> None:
    pdf = tmp_path / "lim-2026.pdf"
    pdf.write_bytes(b"%PDF-1.5 lim")
    entry, created = fetch.add_file(
        tmp_path / "evidence", pdf, url="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6610883",
        source_id="lim-ssrn-6610883-rev-2026-04-21", source_class="PAPER",
    )
    assert created and entry.method == "manual" and entry.content_type == "application/pdf"


def test_make_client_requires_a_declared_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(fetch.USER_AGENT_ENV, raising=False)
    with pytest.raises(RuntimeError, match=fetch.USER_AGENT_ENV):
        fetch.make_client()
    monkeypatch.setenv(fetch.USER_AGENT_ENV, "night-tape research test@example.org")
    seen: list[str] = []

    def handler(r: httpx.Request) -> httpx.Response:
        seen.append(r.headers["user-agent"])
        return httpx.Response(200)

    fetch.make_client(httpx.MockTransport(handler)).get("https://www.sec.gov/")
    assert seen == ["night-tape research test@example.org"]


def test_verify_clean_tampered_missing_and_orphans(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    a, _ = do_fetch(ev, serve(b"a"), "https://example.org/a.html")
    b, _ = do_fetch(ev, serve(b"b"), "https://example.org/b.html")
    assert verify.verify(ev).ok

    (tmp_path / a.local_path).write_bytes(b"tampered")
    (tmp_path / b.local_path).unlink()
    (ev / "VENDOR_DOC" / "stray.html").write_bytes(b"?")
    (ev / "VENDOR_DOC" / "half.html.part").write_bytes(b"?")
    (ev / ".DS_Store").write_bytes(b"")
    report = verify.verify(ev, required_source_ids=["databento-tbbo", "never-fetched"])
    assert report.mismatched == [a.local_path]
    assert report.missing == [b.local_path]
    assert report.orphans == ["evidence/VENDOR_DOC/half.html.part", "evidence/VENDOR_DOC/stray.html"]
    assert report.unarchived_sources == ["never-fetched"]
    assert not report.ok


def test_cli_verify_exit_codes(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    ev.mkdir()
    assert main(["evidence", "--evidence-dir", str(ev), "verify"]) == 0
    (ev / "stray.bin").write_bytes(b"?")
    assert main(["evidence", "--evidence-dir", str(ev), "verify"]) == 1
```

- [ ] **Step 2: Run them and watch them fail**

Run: `uv run pytest tests/unit/test_manifest.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'night_tape.evidence'`

- [ ] **Step 3: Write `src/night_tape/evidence/__init__.py`**

```python
"""Archive-on-fetch evidence store (r2.1 §6.1): immutable snapshots + append-only manifest."""
```

- [ ] **Step 4: Write `src/night_tape/evidence/manifest.py`**

```python
"""Append-only evidence manifest. One JSON object per line in evidence/manifest.jsonl.

Every capture path (HTTP, EDGAR, render, manual) writes through store(). A snapshot file is
never overwritten; a changed source becomes a new file and a new line.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

MANIFEST = "manifest.jsonl"
METHODS = ("http", "edgar", "render-html", "render-pdf", "manual")


@dataclass(frozen=True)
class Entry:
    source_id: str
    source_class: str
    canonical_url: str
    retrieved_at_utc: str
    local_path: str  # relative to evidence_dir.parent, e.g. "evidence/VENDOR_DOC/x/..."
    sha256: str
    content_type: str
    method: str
    published_or_filed_at: str | None = None
    edgar_accession: str | None = None
    supersedes: str | None = None
    notes: str | None = None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(evidence_dir: Path) -> list[Entry]:
    path = evidence_dir / MANIFEST
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [Entry(**json.loads(line)) for line in lines if line.strip()]


def store(
    evidence_dir: Path,
    data: bytes,
    *,
    source_id: str,
    source_class: str,
    canonical_url: str,
    content_type: str,
    method: str,
    filename: str,
    subdir: str | None = None,
    edgar_accession: str | None = None,
    published_or_filed_at: str | None = None,
    supersedes: str | None = None,
    notes: str | None = None,
) -> tuple[Entry, bool]:
    """Write `data` as a new snapshot. Returns (entry, created); created=False if unchanged."""
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}")
    digest = hashlib.sha256(data).hexdigest()
    previous = [e for e in read(evidence_dir) if (e.canonical_url, e.method) == (canonical_url, method)]
    if previous and previous[-1].sha256 == digest:
        return previous[-1], False

    now = datetime.now(UTC)
    folder = evidence_dir / source_class / source_id
    if subdir:
        folder = folder / subdir
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    target = folder / f"{now:%Y%m%dT%H%M%SZ}-{digest[:12]}-{safe_name}"
    if target.exists():
        raise FileExistsError(target)  # never overwrite evidence
    folder.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    part.write_bytes(data)
    part.replace(target)  # the manifest line is written only after the file is complete

    entry = Entry(
        source_id=source_id,
        source_class=source_class,
        canonical_url=canonical_url,
        retrieved_at_utc=now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        local_path=str(target.relative_to(evidence_dir.parent)),
        sha256=digest,
        content_type=content_type,
        method=method,
        published_or_filed_at=published_or_filed_at,
        edgar_accession=edgar_accession,
        supersedes=supersedes,
        notes=notes,
    )
    with (evidence_dir / MANIFEST).open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(entry), sort_keys=True) + "\n")
    return entry, True
```

- [ ] **Step 5: Write `src/night_tape/evidence/fetch.py`**

```python
"""HTTP archive-on-fetch. Stores the bytes the server sent, never a rendering or an error page."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

import httpx

from night_tape.evidence.manifest import Entry, store

USER_AGENT_ENV = "NIGHT_TAPE_USER_AGENT"
_EXT = {
    "text/html": ".html", "application/pdf": ".pdf", "application/json": ".json",
    "application/xml": ".xml", "text/xml": ".xml", "text/plain": ".txt",
}


def user_agent() -> str:
    ua = os.environ.get(USER_AGENT_ENV, "").strip()
    if not ua:
        raise RuntimeError(
            f"set {USER_AGENT_ENV}='night-tape research <contact email>' "
            "(SEC fair access requires a declared contact)"
        )
    return ua


def make_client(transport: httpx.BaseTransport | None = None) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": user_agent()}, follow_redirects=True, timeout=60.0, transport=transport
    )


def fetch_bytes(client: httpx.Client, url: str) -> httpx.Response:
    resp = client.get(url)
    resp.raise_for_status()
    return resp


def content_type(resp: httpx.Response) -> str:
    return resp.headers.get("content-type", "application/octet-stream").split(";")[0].strip()


def _filename(url: str, ctype: str) -> str:
    name = PurePosixPath(urlsplit(url).path).name
    return name if "." in name else (name or "index") + _EXT.get(ctype, ".bin")


def fetch(
    evidence_dir: Path,
    client: httpx.Client,
    url: str,
    *,
    source_id: str,
    source_class: str,
    supersedes: str | None = None,
    notes: str | None = None,
) -> tuple[Entry, bool]:
    resp = fetch_bytes(client, url)
    final = str(resp.url)
    if final != url:
        notes = f"redirected to {final}" + (f"; {notes}" if notes else "")
    ctype = content_type(resp)
    return store(
        evidence_dir, resp.content, source_id=source_id, source_class=source_class,
        canonical_url=url, content_type=ctype, method="http", filename=_filename(final, ctype),
        supersedes=supersedes, notes=notes,
    )


def add_file(
    evidence_dir: Path,
    path: Path,
    *,
    url: str,
    source_id: str,
    source_class: str,
    content_type: str | None = None,
    notes: str | None = None,
) -> tuple[Entry, bool]:
    ctype = content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return store(
        evidence_dir, path.read_bytes(), source_id=source_id, source_class=source_class,
        canonical_url=url, content_type=ctype, method="manual", filename=path.name, notes=notes,
    )
```

- [ ] **Step 6: Write `src/night_tape/evidence/verify.py`**

```python
"""Re-hash every manifest entry and find files the manifest does not know about."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from night_tape.evidence.manifest import MANIFEST, read, sha256_file

_IGNORED = {MANIFEST, ".DS_Store"}


@dataclass(frozen=True)
class Report:
    missing: list[str]
    mismatched: list[str]
    orphans: list[str]
    unarchived_sources: list[str]

    @property
    def ok(self) -> bool:
        return not (self.missing or self.mismatched or self.orphans or self.unarchived_sources)


def verify(evidence_dir: Path, required_source_ids: Iterable[str] = ()) -> Report:
    root = evidence_dir.parent
    entries = read(evidence_dir)
    known: set[Path] = set()
    missing: list[str] = []
    mismatched: list[str] = []
    for e in entries:
        path = root / e.local_path
        known.add(path.resolve())
        if not path.is_file():
            missing.append(e.local_path)
        elif sha256_file(path) != e.sha256:
            mismatched.append(e.local_path)
    files = evidence_dir.rglob("*") if evidence_dir.exists() else iter(())
    orphans = sorted(
        str(p.relative_to(root))
        for p in files
        if p.is_file() and p.name not in _IGNORED and p.resolve() not in known
    )
    archived = {e.source_id for e in entries}
    unarchived = sorted(set(required_source_ids) - archived)
    return Report(missing, mismatched, orphans, unarchived)
```

- [ ] **Step 7: Add the `evidence` command group to `src/night_tape/cli.py`**

Add these imports:

```python
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from night_tape import contracts
from night_tape.evidence import fetch, verify
from night_tape.evidence.manifest import Entry

if TYPE_CHECKING:
    Subparsers = argparse._SubParsersAction[argparse.ArgumentParser]
```

In `build_parser`, replace `parser.add_subparsers(dest="command", required=True, metavar="COMMAND")` with:

```python
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    _add_evidence(sub)
```

Add these functions:

```python
def _source_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--source-id", required=True)
    p.add_argument("--source-class", required=True, choices=contracts.source_classes())


def _add_evidence(sub: Subparsers) -> None:
    ev = sub.add_parser("evidence", help="archive-on-fetch and verify primary sources")
    ev.add_argument("--evidence-dir", type=Path, default=Path("evidence"))
    evs = ev.add_subparsers(dest="evidence_command", required=True, metavar="ACTION")

    p = evs.add_parser("fetch", help="archive the raw HTTP response for one URL")
    p.add_argument("url")
    _source_args(p)
    p.add_argument("--supersedes")
    p.add_argument("--notes")
    p.set_defaults(handler=_evidence_fetch)

    p = evs.add_parser("add", help="register a file downloaded by hand (e.g. an SSRN PDF)")
    p.add_argument("path", type=Path)
    p.add_argument("--url", required=True, help="where the file was downloaded from")
    _source_args(p)
    p.add_argument("--content-type")
    p.add_argument("--notes")
    p.set_defaults(handler=_evidence_add)

    p = evs.add_parser("verify", help="re-hash every snapshot; report missing files and orphans")
    p.set_defaults(handler=_evidence_verify)


def _print_stored(results: Iterable[tuple[Entry, bool]]) -> None:
    for entry, created in results:
        print(f"{'archived ' if created else 'unchanged'} {entry.local_path}")


def _evidence_fetch(args: argparse.Namespace) -> int:
    with fetch.make_client() as client:
        _print_stored([fetch.fetch(
            args.evidence_dir, client, args.url, source_id=args.source_id,
            source_class=args.source_class, supersedes=args.supersedes, notes=args.notes,
        )])
    return 0


def _evidence_add(args: argparse.Namespace) -> int:
    _print_stored([fetch.add_file(
        args.evidence_dir, args.path, url=args.url, source_id=args.source_id,
        source_class=args.source_class, content_type=args.content_type, notes=args.notes,
    )])
    return 0


def _report_verify(report: verify.Report) -> int:
    for label, items in (
        ("missing", report.missing), ("hash mismatch", report.mismatched),
        ("orphan", report.orphans), ("never archived", report.unarchived_sources),
    ):
        for item in items:
            print(f"{label}: {item}")
    print("evidence ok" if report.ok else "evidence FAILED", file=sys.stderr)
    return 0 if report.ok else 1


def _evidence_verify(args: argparse.Namespace) -> int:
    return _report_verify(verify.verify(args.evidence_dir))
```

- [ ] **Step 8: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_manifest.py -v`
Expected: all pass.

- [ ] **Step 9: Full check and commit**

```bash
make test
git add src/night_tape/evidence src/night_tape/cli.py tests/unit/test_manifest.py
git commit -S -m "feat: add archive-on-fetch evidence store, manual add and verify"
```

---

### Task 5: EDGAR: the whole BOATS ATS-N chain

**Files:**
- Create: `src/night_tape/evidence/edgar.py`, `tests/unit/test_edgar.py`
- Modify: `src/night_tape/cli.py`

**Interfaces:**
- Consumes: `fetch.fetch_bytes` and `fetch.content_type`; `manifest.store` and `manifest.Entry`
- Produces:
  - `edgar.MIN_INTERVAL_S = 0.12`
  - `@dataclass(frozen=True) edgar.Filing` with fields `accession`, `form`, `filing_date`
  - `class edgar.PaginatedSubmissions(RuntimeError)`
  - `edgar.parse_filings(submissions: dict[str, Any], form_prefix: str) -> list[Filing]`
  - `edgar.archive_chain(evidence_dir, client, *, cik: str, form_prefix: str, source_id: str, source_class: str, sleep: Callable[[float], None] = time.sleep) -> list[tuple[Entry, bool]]`

- [ ] **Step 1: Write the failing tests** — `tests/unit/test_edgar.py`

```python
from pathlib import Path
from typing import Any

import httpx
import pytest

from night_tape.evidence import edgar, manifest

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK0001795131.json"
BASE = "https://www.sec.gov/Archives/edgar/data/1795131/"
FOLDERS = {
    BASE + "000090266426003296/index.json": ["primary_doc.xml", "ex3redline.pdf"],
    BASE + "000179513124000022/index.json": ["primary_doc.xml"],
}


def submissions(files: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {"cik": "1795131", "filings": {
        "recent": {
            "accessionNumber": ["0000902664-26-003296", "0001795131-24-000022", "0000000000-25-000001"],
            "form": ["ATS-N/MA", "ATS-N/CA", "D"],
            "filingDate": ["2026-05-01", "2024-03-01", "2025-01-01"],
        },
        "files": files or [],
    }}


def edgar_client(subs: dict[str, Any]) -> httpx.Client:
    def handler(r: httpx.Request) -> httpx.Response:
        url = str(r.url)
        if url == SUBMISSIONS_URL:
            return httpx.Response(200, json=subs)
        if url in FOLDERS:
            items = [{"name": n, "type": "text.gif"} for n in FOLDERS[url]]
            return httpx.Response(200, json={"directory": {"item": items}})
        if url.startswith(BASE):
            return httpx.Response(200, content=f"bytes of {url}".encode(), headers={"content-type": "application/xml"})
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


def run(ev: Path, client: httpx.Client, sleeps: list[float]) -> list[tuple[manifest.Entry, bool]]:
    return edgar.archive_chain(
        ev, client, cik="1795131", form_prefix="ATS-N", source_id="boats-atsn-chain",
        source_class="SEC_FORM_ATS_N", sleep=sleeps.append,
    )


def test_parse_filings_keeps_the_form_family_oldest_first() -> None:
    filings = edgar.parse_filings(submissions(), "ATS-N")
    assert [(f.form, f.filing_date) for f in filings] == [("ATS-N/CA", "2024-03-01"), ("ATS-N/MA", "2026-05-01")]


def test_archive_chain_stores_the_listing_and_every_file(tmp_path: Path) -> None:
    sleeps: list[float] = []
    results = run(tmp_path / "evidence", edgar_client(submissions()), sleeps)
    entries = [e for e, created in results if created]
    assert len(entries) == 4  # submissions JSON + 3 filing files
    assert entries[0].canonical_url == SUBMISSIONS_URL and entries[0].edgar_accession is None
    files = entries[1:]
    assert {e.edgar_accession for e in files} == {"0000902664-26-003296", "0001795131-24-000022"}
    assert all(e.method == "edgar" and e.source_id == "boats-atsn-chain" for e in files)
    assert all(f"/{e.edgar_accession}/" in e.local_path for e in files)
    assert len(sleeps) == 6 and set(sleeps) == {edgar.MIN_INTERVAL_S}  # one sleep per request


def test_second_run_is_a_noop(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    run(ev, edgar_client(submissions()), [])
    assert not any(created for _, created in run(ev, edgar_client(submissions()), []))


def test_paginated_submissions_fail_closed(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    subs = submissions(files=[{"name": "CIK0001795131-submissions-001.json"}])
    with pytest.raises(edgar.PaginatedSubmissions):
        run(ev, edgar_client(subs), [])
    assert manifest.read(ev) == []
```

- [ ] **Step 2: Run them and watch them fail**

Run: `uv run pytest tests/unit/test_edgar.py -v`
Expected: FAIL with `ImportError: cannot import name 'edgar'`

- [ ] **Step 3: Write `src/night_tape/evidence/edgar.py`**

```python
"""Archive every file of every filing in one form family for one CIK (e.g. all BOATS ATS-N).

Archive the accession folders, not only the XSL-rendered view (weekly W1 "Watch out for").
The submissions listing is archived too, so "the full chain" is itself evidenced.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from night_tape.evidence.fetch import content_type, fetch_bytes
from night_tape.evidence.manifest import Entry, store

SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
FOLDER = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/"
# ponytail: fixed sleep keeps one client under SEC's 10 req/s; token bucket if we ever parallelize
MIN_INTERVAL_S = 0.12


@dataclass(frozen=True)
class Filing:
    accession: str
    form: str
    filing_date: str


class PaginatedSubmissions(RuntimeError):
    """Older filings live in extra submission files; archiving only `recent` would be partial."""


def parse_filings(submissions: dict[str, Any], form_prefix: str) -> list[Filing]:
    filings = submissions["filings"]
    if filings.get("files"):
        names = [f["name"] for f in filings["files"]]
        raise PaginatedSubmissions(f"older filings in {names}; extend edgar.py before trusting the chain")
    recent = filings["recent"]
    rows = zip(recent["accessionNumber"], recent["form"], recent["filingDate"], strict=True)
    found = [Filing(a, f, d) for a, f, d in rows if f.startswith(form_prefix)]
    return sorted(found, key=lambda f: (f.filing_date, f.accession))


def archive_chain(
    evidence_dir: Path,
    client: httpx.Client,
    *,
    cik: str,
    form_prefix: str,
    source_id: str,
    source_class: str,
    sleep: Callable[[float], None] = time.sleep,
) -> list[tuple[Entry, bool]]:
    def get(url: str) -> httpx.Response:
        sleep(MIN_INTERVAL_S)
        return fetch_bytes(client, url)

    listing_url = SUBMISSIONS.format(cik=cik.zfill(10))
    listing = get(listing_url)
    filings = parse_filings(listing.json(), form_prefix)  # fail closed before storing anything
    results = [store(
        evidence_dir, listing.content, source_id=source_id, source_class=source_class,
        canonical_url=listing_url, content_type="application/json", method="edgar",
        filename=f"CIK{cik.zfill(10)}.json", notes=f"{len(filings)} {form_prefix}* filings listed",
    )]
    for filing in filings:
        base = FOLDER.format(cik=int(cik), acc=filing.accession.replace("-", ""))
        names = sorted(item["name"] for item in get(base + "index.json").json()["directory"]["item"])
        for name in names:
            resp = get(base + name)
            results.append(store(
                evidence_dir, resp.content, source_id=source_id, source_class=source_class,
                canonical_url=base + name, content_type=content_type(resp), method="edgar",
                filename=name, subdir=filing.accession, edgar_accession=filing.accession,
                published_or_filed_at=filing.filing_date, notes=filing.form,
            ))
    return results
```

- [ ] **Step 4: Add `evidence edgar` to `src/night_tape/cli.py`**

Change the import to `from night_tape.evidence import edgar, fetch, verify`. Then, inside `_add_evidence`, before the `verify` parser:

```python
    p = evs.add_parser("edgar", help="archive every file of every filing in a form family for one CIK")
    p.add_argument("--cik", required=True)
    p.add_argument("--form-prefix", required=True, help="e.g. ATS-N (matches ATS-N, ATS-N/MA, ATS-N/CA ...)")
    _source_args(p)
    p.set_defaults(handler=_evidence_edgar)
```

Add this handler:

```python
def _evidence_edgar(args: argparse.Namespace) -> int:
    with fetch.make_client() as client:
        _print_stored(edgar.archive_chain(
            args.evidence_dir, client, cik=args.cik, form_prefix=args.form_prefix,
            source_id=args.source_id, source_class=args.source_class,
        ))
    return 0
```

- [ ] **Step 5: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_edgar.py -v`
Expected: 4 passed

- [ ] **Step 6: Full check and commit**

```bash
make test
git add src/night_tape/evidence/edgar.py src/night_tape/cli.py tests/unit/test_edgar.py
git commit -S -m "feat: archive whole EDGAR accession folders for a form family"
```

---

### Task 6: Playwright render for JS-rendered pages

**Files:**
- Create: `src/night_tape/evidence/render.py`, `tests/unit/test_render.py`
- Modify: `src/night_tape/cli.py`

**Interfaces:**
- Consumes: `fetch.user_agent()`; `manifest.store`
- Produces: `render.render(evidence_dir: Path, url: str, *, source_id: str, source_class: str, notes: str | None = None) -> list[tuple[Entry, bool]]`. It returns two results in order: `[html (method "render-html"), pdf (method "render-pdf")]`.

- [ ] **Step 1: Install Chromium locally**

Run: `uv run playwright install chromium`
Expected: Chromium downloads, or it is already present.

- [ ] **Step 2: Write the failing tests** — `tests/unit/test_render.py`

```python
import functools
import threading
from collections.abc import Iterator
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from night_tape.evidence import manifest
from night_tape.evidence.render import render

PAGE = (
    "<html><body><div id='x'></div>"
    "<script>document.getElementById('x').textContent='rendered-by-js'</script></body></html>"
)


@pytest.fixture
def site(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    monkeypatch.setenv("NIGHT_TAPE_USER_AGENT", "night-tape test")
    root = tmp_path / "site"
    root.mkdir()
    (root / "alerts.html").write_text(PAGE)
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def test_render_archives_the_js_dom_and_a_pdf(site: str, tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    (html, _), (pdf, _) = render(ev, f"{site}/alerts.html", source_id="blue-ocean-service-status", source_class="ATS_SERVICE_ALERT")
    assert (html.method, pdf.method) == ("render-html", "render-pdf")
    assert b"rendered-by-js" in (tmp_path / html.local_path).read_bytes()
    assert (tmp_path / pdf.local_path).read_bytes().startswith(b"%PDF")
    assert html.canonical_url == pdf.canonical_url == f"{site}/alerts.html"


def test_render_refuses_error_page(site: str, tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    with pytest.raises(RuntimeError, match="HTTP 404"):
        render(ev, f"{site}/missing.html", source_id="x", source_class="VENDOR_DOC")
    assert manifest.read(ev) == []
```

- [ ] **Step 3: Run them and watch them fail**

Run: `uv run pytest tests/unit/test_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'night_tape.evidence.render'`

- [ ] **Step 4: Write `src/night_tape/evidence/render.py`**

```python
"""Archive JS-rendered pages: the DOM after load (HTML) plus a printed PDF.

Use only when the raw HTTP bytes don't contain what a reader sees (e.g. the Blue Ocean
service-status page). page.pdf() is Chromium-only.
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

from night_tape.evidence.fetch import user_agent
from night_tape.evidence.manifest import Entry, store


def render(
    evidence_dir: Path, url: str, *, source_id: str, source_class: str, notes: str | None = None
) -> list[tuple[Entry, bool]]:
    ua = user_agent()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(user_agent=ua)
            resp = page.goto(url, wait_until="networkidle", timeout=60_000)
            if resp is None or not resp.ok:
                raise RuntimeError(f"render {url}: HTTP {resp.status if resp else 'no response'}")
            html = page.content().encode("utf-8")
            pdf = page.pdf(format="Letter", print_background=True)
        finally:
            browser.close()
    return [
        store(
            evidence_dir, html, source_id=source_id, source_class=source_class, canonical_url=url,
            content_type="text/html", method="render-html", filename="render.html", notes=notes,
        ),
        store(
            evidence_dir, pdf, source_id=source_id, source_class=source_class, canonical_url=url,
            content_type="application/pdf", method="render-pdf", filename="render.pdf", notes=notes,
        ),
    ]
```

- [ ] **Step 5: Add `evidence render` to `src/night_tape/cli.py`**

Add the import `from night_tape.evidence import render as render_mod`. Then, inside `_add_evidence`, before `verify`:

```python
    p = evs.add_parser("render", help="archive a JS-rendered page as DOM HTML + printed PDF")
    p.add_argument("url")
    _source_args(p)
    p.add_argument("--notes")
    p.set_defaults(handler=_evidence_render)
```

Add this handler:

```python
def _evidence_render(args: argparse.Namespace) -> int:
    _print_stored(render_mod.render(
        args.evidence_dir, args.url, source_id=args.source_id,
        source_class=args.source_class, notes=args.notes,
    ))
    return 0
```

- [ ] **Step 6: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_render.py -v`
Expected: 2 passed

- [ ] **Step 7: Full check and commit**

```bash
make test
git add src/night_tape/evidence/render.py src/night_tape/cli.py tests/unit/test_render.py
git commit -S -m "feat: archive JS-rendered pages as DOM HTML and printed PDF"
```

---

### Task 7: Registry loading, validation and load-bearing report

**Files:**
- Create: `src/night_tape/config.py`, `src/night_tape/registry/__init__.py`, `src/night_tape/registry/load.py`, `src/night_tape/registry/claims.py`, `tests/unit/test_registry_load.py`
- Modify: `src/night_tape/cli.py`, `Makefile`

**Interfaces:**
- Consumes: `contracts.validate`, `contracts.ContractError`; `manifest.read`
- Produces:
  - `config.load_yaml(path: Path) -> Any` (dates stay `str`)
  - `@dataclass(frozen=True) registry.load.Registry` with fields `claims: dict[str, dict]`, `events: dict[str, dict]` and `rule_versions: dict[str, dict]`
  - `registry.load.RegistryError(ValueError)`
  - `registry.load.load(claims_path: Path, events_path: Path) -> Registry`
  - `registry.claims.OK_STATUSES`
  - `registry.claims.load_bearing_gaps(reg: Registry, archived_sha256: set[str]) -> list[str]`
- CLI: `night-tape registry [--claims P] [--events P] check | load-bearing [--evidence-dir P]`
- Make: `evidence-load-bearing` becomes real.

- [ ] **Step 1: Write the failing tests** — `tests/unit/test_registry_load.py`

```python
from pathlib import Path
from typing import Any

import pytest
import yaml

from night_tape.cli import main
from night_tape.config import load_yaml
from night_tape.contracts import ContractError
from night_tape.registry.claims import load_bearing_gaps
from night_tape.registry.load import RegistryError, load

SHA = "c" * 64


def claim(cid: str, **over: Any) -> dict[str, Any]:
    c: dict[str, Any] = {
        "claim_id": cid, "claim_text": "t", "claim_type": "schedule", "load_bearing": True,
        "affects": ["identification"], "status": "UNVERIFIED",
    }
    c.update(over)
    return c


def event(eid: str, **over: Any) -> dict[str, Any]:
    e: dict[str, Any] = {
        "event_id": eid, "entity": "BOATS", "field": "halt_rule", "value": "none",
        "status": "CURRENT", "effective_granularity": "day", "effective_from": "2026-09-10",
        "effective_to": None, "claim_ids": ["C-A"], "load_bearing": True,
    }
    e.update(over)
    return e


def write(tmp: Path, claims: list[dict[str, Any]], events: list[dict[str, Any]], rvs: list[dict[str, Any]] | None = None) -> tuple[Path, Path]:
    c, e = tmp / "claims.yaml", tmp / "events.yaml"
    c.write_text(yaml.safe_dump({"claims": claims}))
    e.write_text(yaml.safe_dump({"events": events, "rule_versions": rvs or []}))
    return c, e


def test_yaml_dates_stay_strings(tmp_path: Path) -> None:
    f = tmp_path / "d.yaml"
    f.write_text("effective_from: 2026-07-20\nat: 2026-09-22T12:00:00Z\n")
    assert load_yaml(f) == {"effective_from": "2026-07-20", "at": "2026-09-22T12:00:00Z"}


def test_unquoted_dates_validate_through_the_loader(tmp_path: Path) -> None:
    c = tmp_path / "claims.yaml"
    e = tmp_path / "events.yaml"
    e.write_text(
        "events:\n- event_id: E-X\n  entity: BOATS\n  field: halt_rule\n  value: none\n"
        "  status: CURRENT\n  effective_granularity: day\n  effective_from: 2026-09-10\n"
        "  effective_to: null\n  claim_ids: [C-A]\n  load_bearing: true\nrule_versions: []\n"
    )
    c.write_text("claims:\n- {claim_id: C-A, claim_text: t, claim_type: schedule, load_bearing: true, affects: [identification], status: UNVERIFIED}\n")
    assert load(c, e).events["E-X"]["effective_from"] == "2026-09-10"


def test_valid_registry_loads(tmp_path: Path) -> None:
    rv = {"rule_version": "BOATS_POST_2026_09_10", "venue": "BOATS", "effective_granularity": "day",
          "effective_from": "2026-09-10", "effective_to": None, "basis_event_ids": ["E-X"], "provisional": True}
    reg = load(*write(tmp_path, [claim("C-A")], [event("E-X")], [rv]))
    assert list(reg.claims) == ["C-A"] and list(reg.events) == ["E-X"]
    assert list(reg.rule_versions) == ["BOATS_POST_2026_09_10"]


@pytest.mark.parametrize("claims, events, fragment", [
    ([claim("C-A"), claim("C-A")], [], "duplicate claim_id C-A"),
    ([claim("C-A")], [event("E-X", claim_ids=["C-NOPE"])], "unknown claim C-NOPE"),
    ([claim("C-A")], [event("E-X", supersedes="E-GHOST")], "supersedes -> unknown event E-GHOST"),
])
def test_cross_reference_errors(tmp_path: Path, claims: list[dict[str, Any]], events: list[dict[str, Any]], fragment: str) -> None:
    with pytest.raises(RegistryError, match=fragment):
        load(*write(tmp_path, claims, events))


def test_contract_violation_surfaces_the_path(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match=r"claims\[0\]"):
        load(*write(tmp_path, [claim("C-A", status="VERIFIED")], []))


def test_load_bearing_gaps(tmp_path: Path) -> None:
    claims = [
        claim("C-OPEN"),
        claim("C-OK", status="VERIFIED", source_class="VENDOR_DOC", source_id="s", retrieved_at="2026-09-22T12:00:00Z", sha256=SHA),
        claim("C-PLAN", status="CONTINGENCY"),
        claim("C-CTX", load_bearing=False, affects=["context_only"]),
    ]
    reg = load(*write(tmp_path, claims, []))
    assert load_bearing_gaps(reg, {SHA}) == ["C-OPEN: status UNVERIFIED"]


def test_verified_claim_with_unarchived_hash_is_a_gap(tmp_path: Path) -> None:
    ok = claim("C-OK", status="VERIFIED", source_class="VENDOR_DOC", source_id="s", retrieved_at="2026-09-22T12:00:00Z", sha256=SHA)
    reg = load(*write(tmp_path, [ok], []))
    gaps = load_bearing_gaps(reg, archived_sha256=set())
    assert len(gaps) == 1 and gaps[0].startswith("C-OK: VERIFIED but sha256")


def test_cli_load_bearing_exit_code(tmp_path: Path) -> None:
    c, e = write(tmp_path, [claim("C-OPEN")], [])
    args = ["registry", "--claims", str(c), "--events", str(e)]
    assert main([*args, "check"]) == 0
    assert main([*args, "load-bearing", "--evidence-dir", str(tmp_path / "evidence")]) == 1
```

- [ ] **Step 2: Run them and watch them fail**

Run: `uv run pytest tests/unit/test_registry_load.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'night_tape.config'`

- [ ] **Step 3: Write `src/night_tape/config.py`**

```python
"""YAML loading for registries and config.

PyYAML's default resolver turns `2026-07-20` into datetime.date and `...T12:00:00Z` into
datetime. Registry facts must stay strings: JSON Schema validates strings, and implicit
datetime objects invite naive-timezone bugs. Load every repo YAML through load_yaml().
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class _StringDateLoader(yaml.SafeLoader):
    pass


_StringDateLoader.yaml_implicit_resolvers = {
    first_char: [(tag, rx) for tag, rx in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for first_char, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.load(f, Loader=_StringDateLoader)
```

- [ ] **Step 4: Write `src/night_tape/registry/__init__.py` and `src/night_tape/registry/load.py`**

`__init__.py`:

```python
"""Claim register and market-structure event registry: facts the code asks for."""
```

`load.py`:

```python
"""Load registry/claims.yaml and registry/events.yaml, validate both, check cross-references."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from night_tape import contracts
from night_tape.config import load_yaml

Record = dict[str, Any]


class RegistryError(ValueError):
    pass


@dataclass(frozen=True)
class Registry:
    claims: dict[str, Record]
    events: dict[str, Record]
    rule_versions: dict[str, Record]


def _index(items: list[Record], key: str, problems: list[str]) -> dict[str, Record]:
    out: dict[str, Record] = {}
    for item in items:
        if item[key] in out:
            problems.append(f"duplicate {key} {item[key]}")
        out[item[key]] = item
    return out


def load(claims_path: Path, events_path: Path) -> Registry:
    claims_doc = load_yaml(claims_path)
    events_doc = load_yaml(events_path)
    contracts.validate("claim_registry", claims_doc)
    contracts.validate("event_registry", events_doc)

    problems: list[str] = []
    claims = _index(claims_doc["claims"], "claim_id", problems)
    events = _index(events_doc["events"], "event_id", problems)
    rule_versions = _index(events_doc["rule_versions"], "rule_version", problems)

    for eid, ev in events.items():
        problems += [f"{eid}: unknown claim {c}" for c in ev["claim_ids"] if c not in claims]
        for key in ("supersedes", "correction_of"):
            if ev.get(key) and ev[key] not in events:
                problems.append(f"{eid}: {key} -> unknown event {ev[key]}")
        problems += [
            f"{eid}: conflicts_with -> unknown event {x}"
            for x in ev.get("conflicts_with") or []
            if x not in events
        ]
    for rv, r in rule_versions.items():
        problems += [f"{rv}: unknown basis event {x}" for x in r["basis_event_ids"] if x not in events]

    if problems:
        raise RegistryError("; ".join(problems))
    return Registry(claims, events, rule_versions)
```

- [ ] **Step 5: Write `src/night_tape/registry/claims.py`**

```python
"""Load-bearing claims that would block the freeze (r2.1 §6.2 freeze rule)."""

from __future__ import annotations

from night_tape.registry.load import Registry

OK_STATUSES = {"VERIFIED", "CONTINGENCY"}


def load_bearing_gaps(reg: Registry, archived_sha256: set[str]) -> list[str]:
    gaps: list[str] = []
    for cid, c in sorted(reg.claims.items()):
        if not c["load_bearing"]:
            continue
        if c["status"] not in OK_STATUSES:
            gaps.append(f"{cid}: status {c['status']}")
        elif c["status"] == "VERIFIED" and c["sha256"] not in archived_sha256:
            gaps.append(f"{cid}: VERIFIED but sha256 {c['sha256'][:12]}... not in evidence manifest")
    return gaps
```

- [ ] **Step 6: Add the `registry` command group to `src/night_tape/cli.py`**

Add these imports:

```python
from night_tape.contracts import ContractError
from night_tape.evidence import manifest
from night_tape.registry import claims as registry_claims
from night_tape.registry.load import Registry, RegistryError, load as load_registry
```

In `build_parser`, after `_add_evidence(sub)`, add `_add_registry(sub)`. Then add:

```python
def _add_registry(sub: Subparsers) -> None:
    rg = sub.add_parser("registry", help="claim register and event registry")
    rg.add_argument("--claims", type=Path, default=Path("registry/claims.yaml"))
    rg.add_argument("--events", type=Path, default=Path("registry/events.yaml"))
    rgs = rg.add_subparsers(dest="registry_command", required=True, metavar="ACTION")

    p = rgs.add_parser("check", help="validate both registries and their cross-references")
    p.set_defaults(handler=_registry_check)

    p = rgs.add_parser("load-bearing", help="list load-bearing claims that block the freeze")
    p.add_argument("--evidence-dir", type=Path, default=Path("evidence"))
    p.set_defaults(handler=_registry_load_bearing)


def _registry_or_none(args: argparse.Namespace) -> Registry | None:
    try:
        return load_registry(args.claims, args.events)
    except (ContractError, RegistryError) as exc:
        print(exc, file=sys.stderr)
        return None


def _registry_check(args: argparse.Namespace) -> int:
    reg = _registry_or_none(args)
    if reg is None:
        return 1
    print(f"ok: {len(reg.claims)} claims, {len(reg.events)} events, {len(reg.rule_versions)} rule versions")
    return 0


def _registry_load_bearing(args: argparse.Namespace) -> int:
    reg = _registry_or_none(args)
    if reg is None:
        return 1
    gaps = registry_claims.load_bearing_gaps(reg, {e.sha256 for e in manifest.read(args.evidence_dir)})
    for gap in gaps:
        print(gap)
    total = sum(1 for c in reg.claims.values() if c["load_bearing"])
    print(f"{total} load-bearing claims, {len(gaps)} block the freeze", file=sys.stderr)
    return 1 if gaps else 0
```

- [ ] **Step 7: Make `evidence-load-bearing` real in the `Makefile`.** Remove `evidence-load-bearing` from `STUBS := …` and add:

```make
evidence-load-bearing:
	uv run night-tape registry load-bearing
```

- [ ] **Step 8: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_registry_load.py tests/unit/test_makefile.py -v`
Expected: all pass. `test_stubs_fail_loudly` no longer includes `evidence-load-bearing`.

- [ ] **Step 9: Full check and commit**

```bash
make test
git add src/night_tape/config.py src/night_tape/registry src/night_tape/cli.py Makefile tests/unit/test_registry_load.py
git commit -S -m "feat: validate claim and event registries; report load-bearing gaps"
```

---

### Task 8: Source list and `evidence sync`

**Files:**
- Create: `src/night_tape/evidence/sources.py`, `config/monitoring.yaml`, `tests/unit/test_sources.py`
- Modify: `src/night_tape/cli.py`, `Makefile`

**Interfaces:**
- Consumes: `config.load_yaml`, `contracts.source_classes()`, `fetch.fetch`, `render.render`, `edgar.archive_chain`, `edgar.MIN_INTERVAL_S`, `manifest.read`, `verify.verify`
- Produces:
  - `@dataclass(frozen=True) sources.Source` with fields `source_id`, `source_class`, `method`, `url=None`, `cik=None`, `form_prefix=None`, `notes=None`
  - `sources.METHODS = ("http", "render", "edgar", "manual")`
  - `sources.load_sources(path: Path) -> list[Source]`
  - `@dataclass sources.SyncReport` with fields `stored`, `failed: list[tuple[str, str]]` and `manual_missing: list[str]`
  - `sources.sync(evidence_dir, srcs, client, *, render_fn=render.render, edgar_fn=edgar.archive_chain, sleep=time.sleep) -> SyncReport`
- CLI:
  - `night-tape evidence sync [--sources config/monitoring.yaml]`
  - `night-tape evidence verify` now also requires every configured `source_id` to be archived.
- Make: `source-archive-verify` becomes real.

- [ ] **Step 1: Write the failing tests** — `tests/unit/test_sources.py`

```python
from pathlib import Path
from typing import Any

import httpx
import pytest

from night_tape.evidence import manifest, sources
from night_tape.evidence.sources import Source, load_sources, sync

ROOT = Path(__file__).resolve().parents[2]


def http_client(status: int = 200) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(
        lambda r: httpx.Response(status, content=b"doc", headers={"content-type": "text/html"})
    ))


def test_repo_source_list_loads() -> None:
    srcs = load_sources(ROOT / "config" / "monitoring.yaml")
    ids = {s.source_id for s in srcs}
    assert "boats-atsn-chain" in ids and "blue-ocean-service-status" in ids
    assert len(ids) == len(srcs)


@pytest.mark.parametrize("bad, fragment", [
    ({"source_id": "x", "source_class": "VENDOR_DOC", "method": "http"}, "needs url"),
    ({"source_id": "x", "source_class": "VENDOR_DOC", "method": "ftp", "url": "u"}, "method"),
    ({"source_id": "x", "source_class": "BLOG", "method": "http", "url": "u"}, "source_class"),
    ({"source_id": "x", "source_class": "SEC_FORM_ATS_N", "method": "edgar"}, "needs cik"),
])
def test_bad_sources_fail_closed(tmp_path: Path, bad: dict[str, Any], fragment: str) -> None:
    import yaml
    f = tmp_path / "m.yaml"
    f.write_text(yaml.safe_dump({"sources": [bad]}))
    with pytest.raises(ValueError, match=fragment):
        load_sources(f)


def test_sync_dispatches_by_method_and_keeps_going_after_a_failure(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    calls: list[str] = []

    def fake_render(evidence_dir: Path, url: str, **kw: Any) -> list[tuple[manifest.Entry, bool]]:
        calls.append(f"render {url}")
        raise RuntimeError("render http://r: HTTP 404")

    def fake_edgar(evidence_dir: Path, client: httpx.Client, **kw: Any) -> list[tuple[manifest.Entry, bool]]:
        calls.append(f"edgar {kw['cik']}")
        return []

    srcs = [
        Source("r", "VENDOR_DOC", "render", url="http://r"),
        Source("h", "SEC_RULE", "http", url="https://www.sec.gov/x"),
        Source("e", "SEC_FORM_ATS_N", "edgar", cik="1795131", form_prefix="ATS-N"),
        Source("m", "PAPER", "manual", url="https://papers.ssrn.com/x"),
    ]
    report = sync(ev, srcs, http_client(), render_fn=fake_render, edgar_fn=fake_edgar, sleep=lambda s: None)
    assert calls == ["render http://r", "edgar 1795131"]
    assert [e.source_id for e, _ in report.stored] == ["h"]
    assert report.failed == [("r", "RuntimeError: render http://r: HTTP 404")]
    assert report.manual_missing == ["m"]


def test_manual_source_already_archived_is_not_reported(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    manifest.store(ev, b"%PDF", source_id="m", source_class="PAPER", canonical_url="u",
                   content_type="application/pdf", method="manual", filename="lim.pdf")
    report = sync(ev, [Source("m", "PAPER", "manual", url="u")], http_client(), sleep=lambda s: None)
    assert report.manual_missing == []


def test_methods_constant_matches_loader() -> None:
    assert sources.METHODS == ("http", "render", "edgar", "manual")
```

- [ ] **Step 2: Run them and watch them fail**

Run: `uv run pytest tests/unit/test_sources.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'night_tape.evidence.sources'`

- [ ] **Step 3: Write `src/night_tape/evidence/sources.py`**

```python
"""The list of load-bearing sources to archive (config/monitoring.yaml) and `sync` over it.

Re-run weekly (weekly §4): unchanged bytes are a no-op, changed bytes become a new snapshot.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from playwright.sync_api import Error as PlaywrightError

from night_tape import contracts
from night_tape.config import load_yaml
from night_tape.evidence import edgar, fetch, manifest, render
from night_tape.evidence.manifest import Entry

METHODS = ("http", "render", "edgar", "manual")
# One bad source must not hide the rest. PlaywrightError covers render timeouts.
_SOURCE_ERRORS = (httpx.HTTPError, PlaywrightError, RuntimeError, OSError)
Stored = list[tuple[Entry, bool]]


@dataclass(frozen=True)
class Source:
    source_id: str
    source_class: str
    method: str
    url: str | None = None
    cik: str | None = None
    form_prefix: str | None = None
    notes: str | None = None


def _check(s: Source) -> None:
    if s.method not in METHODS:
        raise ValueError(f"{s.source_id}: method {s.method!r} not in {METHODS}")
    if s.source_class not in contracts.source_classes():
        raise ValueError(f"{s.source_id}: unknown source_class {s.source_class!r}")
    if s.method == "edgar" and not (s.cik and s.form_prefix):
        raise ValueError(f"{s.source_id}: edgar source needs cik and form_prefix")
    if s.method != "edgar" and not s.url:
        raise ValueError(f"{s.source_id}: {s.method} source needs url")


def load_sources(path: Path) -> list[Source]:
    srcs = [Source(**raw) for raw in load_yaml(path)["sources"]]  # unknown keys → TypeError
    for s in srcs:
        _check(s)
    ids = [s.source_id for s in srcs]
    if dupes := sorted({i for i in ids if ids.count(i) > 1}):
        raise ValueError(f"duplicate source_id {dupes}")
    return srcs


@dataclass
class SyncReport:
    stored: Stored = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)
    manual_missing: list[str] = field(default_factory=list)


def sync(
    evidence_dir: Path,
    srcs: list[Source],
    client: httpx.Client,
    *,
    render_fn: Callable[..., Stored] = render.render,
    edgar_fn: Callable[..., Stored] = edgar.archive_chain,
    sleep: Callable[[float], None] = time.sleep,
) -> SyncReport:
    report = SyncReport()
    archived = {e.source_id for e in manifest.read(evidence_dir)}
    for s in srcs:
        ids: dict[str, Any] = {"source_id": s.source_id, "source_class": s.source_class}
        try:
            if s.method == "manual":
                if s.source_id not in archived:
                    report.manual_missing.append(s.source_id)
            elif s.method == "http":
                assert s.url is not None
                sleep(edgar.MIN_INTERVAL_S)
                report.stored.append(fetch.fetch(evidence_dir, client, s.url, notes=s.notes, **ids))
            elif s.method == "render":
                report.stored.extend(render_fn(evidence_dir, s.url, notes=s.notes, **ids))
            else:
                report.stored.extend(edgar_fn(
                    evidence_dir, client, cik=s.cik, form_prefix=s.form_prefix, sleep=sleep, **ids
                ))
        except _SOURCE_ERRORS as exc:
            report.failed.append((s.source_id, f"{type(exc).__name__}: {exc}"))
    return report
```

- [ ] **Step 4: Write `config/monitoring.yaml`.** URLs marked *unverified* are best guesses at Databento doc paths. If `sync` reports a 404 for one, find the real page and fix the URL.

```yaml
# Load-bearing primary sources archived on fetch (weekly W1 task 5; r2.1 §18; weekly §1.3).
# `night-tape evidence sync` fetches every non-manual source. Re-run weekly (weekly §4):
# unchanged bytes are a no-op; changed bytes become a new snapshot, never an overwrite.
# method: http | render | edgar | manual  (manual: download by hand, then `night-tape evidence add`)
sources:
  # Every BOATS Form ATS-N filing and amendment, whole accession folders (not only the XSL view).
  - source_id: boats-atsn-chain
    source_class: SEC_FORM_ATS_N
    method: edgar
    cik: "1795131"
    form_prefix: ATS-N

  # r2.1 §18 — readable XSL views of the named filings (the chain above holds the filings).
  - source_id: boats-atsn-2026-current-view
    source_class: SEC_FORM_ATS_N
    method: http
    url: https://www.sec.gov/Archives/edgar/data/1795131/000090266426003296/xslATS-N_X01/primary_doc.xml
    notes: "r2.1 §18 #1 — current Form ATS-N / material amendment (2026)"
  - source_id: boats-atsn-2024-correcting-view
    source_class: SEC_FORM_ATS_N
    method: http
    url: https://www.sec.gov/Archives/edgar/data/1795131/000179513124000022/xslATS-N_X01/primary_doc.xml
    notes: "r2.1 §18 #2 — 2024 correcting amendment restoring price-time wording"
  - source_id: boats-atsn-2023-broker-priority-view
    source_class: SEC_FORM_ATS_N
    method: http
    url: https://www.sec.gov/Archives/edgar/data/1795131/000153949723000091/xslATS-N_X01/primary_doc.xml
    notes: "r2.1 §18 #3 — historical 2023 ATS-N with Broker Priority"
  - source_id: boats-atsn-2023-band-redline
    source_class: SEC_FORM_ATS_N
    method: http
    url: https://www.sec.gov/Archives/edgar/data/1795131/000153949723001938/ex3redline.pdf
    notes: "r2.1 §18 #4 — 15% band was an erroneous disclosure; correct band 20%"
  - source_id: blue-ocean-service-status
    source_class: ATS_SERVICE_ALERT
    method: render
    url: https://blueocean-tech.io/blue-ocean-ats-service-status/
    notes: "r2.1 §18 #5 — 1 Mar / 20 Jul / 10 Sep 2026 alerts; mutable, re-fetch weekly"
  - source_id: sec-s7-2026-20
    source_class: SEC_RULE
    method: http
    url: https://www.sec.gov/rules-regulations/2026/06/s7-2026-20
    notes: "r2.1 §18 #6 — proposed rescission of Rule 611 and Rule 610(e)"
  - source_id: databento-tbbo
    source_class: VENDOR_DOC
    method: render
    url: https://databento.com/docs/schemas-and-data-formats/tbbo
  - source_id: databento-bbo
    source_class: VENDOR_DOC
    method: render
    url: https://databento.com/docs/schemas-and-data-formats/bbo
  - source_id: databento-mbp-1
    source_class: VENDOR_DOC
    method: render
    url: https://databento.com/docs/schemas-and-data-formats/mbp-1
  - source_id: sec-staff-memo-24h-2026-09
    source_class: SEC_STAFF
    method: http
    url: https://www.sec.gov/files/2026_TM_Overnight_Trading_Roundtable_Memo_090926.pdf
    notes: "r2.1 §18 #10 — planned SIP schedule and 8–9pm maintenance window"
  - source_id: nysearca-sr-2026-53
    source_class: EXCHANGE_RULE
    method: http
    url: https://www.sec.gov/rules-regulations/self-regulatory-organization-rulemaking/sr-nysearca-2026-53
  - source_id: nasdaq-34-105199
    source_class: SEC_ORDER
    method: http
    url: https://www.sec.gov/rule-release/34-105199
  - source_id: nasdaq-eta-2026-46
    source_class: EXCHANGE_NOTICE
    method: http
    url: https://www.nasdaqtrader.com/TraderNews.aspx?id=ETA2026-46

  # weekly §1.3 — OCEA.MEMOIR dataset page and schemas the pilot depends on.
  - source_id: databento-ocea-memoir
    source_class: VENDOR_DOC
    method: render
    url: https://databento.com/docs/venues-and-datasets/ocea-memoir
  - source_id: databento-status-schema
    source_class: VENDOR_DOC
    method: render
    url: https://databento.com/docs/schemas-and-data-formats/status
    notes: "URL unverified — fix if sync reports 404"
  - source_id: databento-common-fields
    source_class: VENDOR_DOC
    method: render
    url: https://databento.com/docs/standards-and-conventions/common-fields-enums-types
    notes: "URL unverified — fix if sync reports 404. Fixed-point scale, UNDEF_PRICE, side values"

  # Research baseline — SSRN blocks scripted downloads; fetch the pinned revision by hand.
  - source_id: lim-ssrn-6610883-rev-2026-04-21
    source_class: PAPER
    method: manual
    url: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6610883
    notes: "Pin revision 21 Apr 2026; verify every number against its table (D-8, W4)"
```

- [ ] **Step 5: Wire `sync` and the source-aware `verify` into `src/night_tape/cli.py`**

Add the import `from night_tape.evidence import sources`. In `_add_evidence`, add `ev.add_argument("--sources", type=Path, default=Path("config/monitoring.yaml"))` next to `--evidence-dir`. Then, before `verify`:

```python
    p = evs.add_parser("sync", help="archive every source in --sources (weekly re-fetch)")
    p.set_defaults(handler=_evidence_sync)
```

Add this handler, and replace `_evidence_verify` with the version below it:

```python
def _evidence_sync(args: argparse.Namespace) -> int:
    srcs = sources.load_sources(args.sources)
    with fetch.make_client() as client:
        report = sources.sync(args.evidence_dir, srcs, client)
    _print_stored(report.stored)
    for source_id in report.manual_missing:
        print(f"manual: {source_id} not archived yet — download it, then `night-tape evidence add`")
    for source_id, error in report.failed:
        print(f"FAILED {source_id}: {error}", file=sys.stderr)
    return 1 if report.failed else 0


def _evidence_verify(args: argparse.Namespace) -> int:
    required = [s.source_id for s in sources.load_sources(args.sources)] if args.sources.exists() else []
    return _report_verify(verify.verify(args.evidence_dir, required))
```

Update `test_cli_verify_exit_codes` in `tests/unit/test_manifest.py` so it never reads the repo's source list. Pass `"--sources", str(tmp_path / "none.yaml")` after `"--evidence-dir", str(ev)` in both calls.

- [ ] **Step 6: Make `source-archive-verify` real in the `Makefile`.** Remove it from `STUBS := …` and add:

```make
source-archive-verify:
	uv run night-tape evidence verify
```

- [ ] **Step 7: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_sources.py tests/unit/test_manifest.py tests/unit/test_makefile.py -v`
Expected: all pass.

Run: `make source-archive-verify; echo "exit=$?"`
Expected: `never archived: …` lines and `exit=2`. Nothing has been fetched yet; that is correct until Task 12.

- [ ] **Step 8: Full check and commit**

```bash
make test
git add src/night_tape/evidence/sources.py config/monitoring.yaml src/night_tape/cli.py Makefile tests/unit/test_sources.py tests/unit/test_manifest.py
git commit -S -m "feat: add load-bearing source list, evidence sync and source-aware verify"
```

---

### Task 9: Seed the registries and the money/licensing config

**Files:**
- Create: `registry/claims.yaml`, `registry/events.yaml`, `config/datasets.yaml`, `config/licensing.yaml`, `tests/unit/test_repo_data.py`

**Interfaces:**
- Consumes: `registry.load.load`, `sources.load_sources`, `config.load_yaml`
- Produces: the real registry files. Weeks 2–6 read them: `rule_version_for()` reads `rule_versions`, the W3 cost guard reads `spend_cap_usd`, and the W6 `permissions-check` reads `permissions`.

- [ ] **Step 1: Write the failing tests** — `tests/unit/test_repo_data.py`

```python
from pathlib import Path

from night_tape.config import load_yaml
from night_tape.evidence.sources import load_sources
from night_tape.registry.load import load

ROOT = Path(__file__).resolve().parents[2]
CELL = {"PENDING", "ALLOWED", "ALLOWED_WITH_ATTRIBUTION", "PROHIBITED", "NOT_APPLICABLE"}


def test_repo_registry_is_valid() -> None:
    reg = load(ROOT / "registry" / "claims.yaml", ROOT / "registry" / "events.yaml")
    assert len(reg.claims) >= 30 and len(reg.events) >= 20 and len(reg.rule_versions) == 5


def test_every_claim_source_is_a_configured_source() -> None:
    configured = {s.source_id for s in load_sources(ROOT / "config" / "monitoring.yaml")}
    reg = load(ROOT / "registry" / "claims.yaml", ROOT / "registry" / "events.yaml")
    unknown = sorted(c["source_id"] for c in reg.claims.values() if c.get("source_id") and c["source_id"] not in configured)
    assert unknown == []


def test_licensing_matrix_cells_are_known_values() -> None:
    doc = load_yaml(ROOT / "config" / "licensing.yaml")
    cells = {v for row in doc["permissions"] for k, v in row.items() if k != "output_type"}
    assert cells <= CELL


def test_spend_cap_is_set() -> None:
    doc = load_yaml(ROOT / "config" / "datasets.yaml")
    assert doc["spend_cap_usd"] > 0
```

- [ ] **Step 2: Run them and watch them fail**

Run: `uv run pytest tests/unit/test_repo_data.py -v`
Expected: FAIL with `FileNotFoundError: … registry/claims.yaml`

- [ ] **Step 3: Write `registry/claims.yaml`.** Every claim starts `UNVERIFIED`; Task 12 verifies them against archived evidence. A `source_id` of `null` means the source has not been located yet.

```yaml
# Claim register (r2.1 §6.2). Seeded Week 1 from project-plan v2.2, technical-plan r2.1 and
# weekly-build-plan §1.3. source_id = the config/monitoring.yaml source expected to verify it.
claims:
  # --- Databento schema semantics -------------------------------------------------------------
  - claim_id: C-DBN-TBBO-PRETRADE-BBO
    claim_text: "tbbo emits one record per trade carrying the BBO immediately before that trade's effect."
    claim_type: data_semantics
    load_bearing: true
    affects: [primary_endpoint, metric_semantics]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-tbbo
  - claim_id: C-DBN-FIXED-POINT-1E-9
    claim_text: "Price fields are int64 fixed-point with 1 unit = 1e-9 USD; UNDEF_PRICE is the int64 maximum."
    claim_type: data_semantics
    load_bearing: true
    affects: [metric_semantics]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-common-fields
  - claim_id: C-DBN-BBO1S-NOT-DENSE
    claim_text: "bbo-1s emits no record for an interval with neither a trade nor a BBO update."
    claim_type: data_semantics
    load_bearing: true
    affects: [metric_semantics]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-bbo
  - claim_id: C-DBN-MBP1-EVENT-SPACE
    claim_text: "mbp-1 contains every top-of-book-changing event."
    claim_type: data_semantics
    load_bearing: true
    affects: [metric_semantics]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-mbp-1
  - claim_id: C-DBN-CREDIT-EXPIRY
    claim_text: "The $125 Databento signup credit expires six months after signup."
    claim_type: statistic
    load_bearing: true
    affects: [cost]
    status: UNVERIFIED
    notes: "Record the actual expiry from the portal in config/datasets.yaml at signup."

  # --- OCEA.MEMOIR dataset (weekly §1.3) ------------------------------------------------------
  - claim_id: C-OCEA-SIDE-N-NONDISPLAYED
    claim_text: "Trades from the MEMOIR Trade message (non-displayed executions) carry side = N; trades from Order Executed carry the aggressor side."
    claim_type: data_semantics
    load_bearing: true
    affects: [primary_endpoint, metric_semantics]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-ocea-memoir
    recheck_trigger: "Week 3 pilot non-displayed check; D-1 signed W4 Mon"
  - claim_id: C-OCEA-SHARED-SEQUENCE
    claim_text: "Records normalized from one native MEMOIR message share the same sequence."
    claim_type: data_semantics
    load_bearing: true
    affects: [metric_semantics]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-ocea-memoir
  - claim_id: C-OCEA-NO-BUST-CORRECT
    claim_text: "MEMOIR Broken Trade and Corrected Trade messages are not normalized."
    claim_type: data_semantics
    load_bearing: true
    affects: [data_quality, publication]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-ocea-memoir
  - claim_id: C-OCEA-CMS-SYMBOLS
    claim_text: "OCEA raw symbols use the CMS convention (e.g. 'BRK B')."
    claim_type: data_semantics
    load_bearing: true
    affects: [sample]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-ocea-memoir
  - claim_id: C-OCEA-SESSION-SCOPED-ID
    claim_text: "The native SecurityID (raw_instrument_id) is session-scoped."
    claim_type: data_semantics
    load_bearing: true
    affects: [metric_semantics]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-ocea-memoir
  - claim_id: C-OCEA-TIMESTAMPS
    claim_text: "OCEA has one venue timestamp: only ts_event and ts_recv exist; ts_in_delta = 0."
    claim_type: data_semantics
    load_bearing: true
    affects: [metric_semantics]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-ocea-memoir
  - claim_id: C-OCEA-STATUS-SCHEMA
    claim_text: "The status schema exposes security trading status (halt, pause, quoting, trading) and session status."
    claim_type: data_semantics
    load_bearing: true
    affects: [data_quality, session_logic]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-status-schema
  - claim_id: C-OCEA-HISTORY-START
    claim_text: "OCEA.MEMOIR history begins 24 Aug 2025."
    claim_type: data_semantics
    load_bearing: true
    affects: [sample]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-ocea-memoir
    recheck_trigger: "metadata.get_dataset_range in the Week 3 pilot"
  - claim_id: C-OCEA-COVERAGE-HOURS
    claim_text: "OCEA.MEMOIR covers the Blue Ocean Session, 8pm-4am ET, Sunday-Thursday."
    claim_type: schedule
    load_bearing: true
    affects: [session_logic]
    status: UNVERIFIED
    source_class: VENDOR_DOC
    source_id: databento-ocea-memoir

  # --- BOATS mechanics (current Form ATS-N + amendment chain; r2.1 §2) -----------------------
  - claim_id: C-BOATS-SESSION-HOURS
    claim_text: "BOATS session is 8:00pm-4:00am ET; bona-fide orders accepted from 8:00pm; 6:15pm is for test orders only."
    claim_type: schedule
    load_bearing: true
    affects: [session_logic]
    status: UNVERIFIED
    source_class: SEC_FORM_ATS_N
    source_id: boats-atsn-2026-current-view
  - claim_id: C-BOATS-TRADE-DATE
    claim_text: "BOATS assigns 8:00pm-midnight executions to the following trading day."
    claim_type: schedule
    load_bearing: true
    affects: [date_logic]
    status: UNVERIFIED
    source_class: SEC_FORM_ATS_N
    source_id: boats-atsn-2026-current-view
    notes: "If only an FAQ states this, mark it FAQ-only (r2.1 §15)."
  - claim_id: C-BOATS-OPERATING-DAYS
    claim_text: "BOATS operates only on days when the NYSE TRF is open the following morning; trades settle T+1."
    claim_type: schedule
    load_bearing: true
    affects: [session_logic, date_logic]
    status: UNVERIFIED
    source_class: SEC_FORM_ATS_N
    source_id: boats-atsn-2026-current-view
  - claim_id: C-BOATS-ORDER-TYPES
    claim_text: "BOATS supports one LIMIT order type, DAY or IOC, displayed or non-displayed, POST-ONLY (DAY only); no MARKET or PEGGED; price-time priority; no counter-party selection."
    claim_type: venue_mechanics
    load_bearing: false
    affects: [context_only]
    status: UNVERIFIED
    source_class: SEC_FORM_ATS_N
    source_id: boats-atsn-2026-current-view
  - claim_id: C-BOATS-NO-LOCKED-BOOK
    claim_text: "Internal marketable contra orders execute rather than leaving a locked or crossed BOATS book."
    claim_type: venue_mechanics
    load_bearing: true
    affects: [data_quality]
    status: UNVERIFIED
    source_class: SEC_FORM_ATS_N
    source_id: boats-atsn-2026-current-view
  - claim_id: C-BOATS-BAND-20PCT
    claim_text: "BOATS uses a static 20% reference band per session, referenced to the last national-exchange print reported to the SIP as of 7:30pm ET."
    claim_type: venue_mechanics
    load_bearing: true
    affects: [data_quality]
    status: UNVERIFIED
    source_class: SEC_FORM_ATS_N
    source_id: boats-atsn-2026-current-view
  - claim_id: C-BOATS-BAND-15PCT-ERRONEOUS
    claim_text: "The 2023 correcting redline states the 15% band was incorrectly disclosed and the band was 20%; no band-width break exists."
    claim_type: venue_mechanics
    load_bearing: true
    affects: [identification]
    status: UNVERIFIED
    source_class: SEC_FORM_ATS_N
    source_id: boats-atsn-2023-band-redline
  - claim_id: C-BOATS-BROKER-PRIORITY-SUPERSEDED
    claim_text: "Broker Priority (2023 ATS-N) was superseded by the 2024 correcting amendment restoring price-time wording."
    claim_type: venue_mechanics
    load_bearing: true
    affects: [identification]
    status: UNVERIFIED
    source_class: SEC_FORM_ATS_N
    source_id: boats-atsn-2024-correcting-view
    notes: "Effective interval of Broker Priority to be established from the amendment chain (Stage B, W2)."
  - claim_id: C-BOATS-2025-IOC-DISPLAY
    claim_text: "2025 ATS-N amendments introduced IOC and displayed/non-displayed directions; effective dates not yet established."
    claim_type: venue_mechanics
    load_bearing: true
    affects: [identification]
    status: UNVERIFIED
    source_class: SEC_FORM_ATS_N
    source_id: boats-atsn-chain
  - claim_id: C-BOATS-2026-03-01-OOB-REJECT
    claim_text: "From 1 Mar 2026 BOATS rejected passive orders priced outside the 20% band at entry."
    claim_type: venue_mechanics
    load_bearing: true
    affects: [identification, sample]
    status: UNVERIFIED
    source_class: ATS_SERVICE_ALERT
    source_id: blue-ocean-service-status
  - claim_id: C-BOATS-2026-07-20-OOB-NONDISPLAYED
    claim_text: "From 20 Jul 2026 out-of-band passive orders are accepted non-displayed, non-executable and excluded from market data until repriced inside the band."
    claim_type: venue_mechanics
    load_bearing: true
    affects: [identification, metric_semantics]
    status: UNVERIFIED
    source_class: ATS_SERVICE_ALERT
    source_id: blue-ocean-service-status
  - claim_id: C-BOATS-2026-09-10-FAIR-ACCESS
    claim_text: "From 10 Sep 2026 BOATS stopped halting symbols for Rule 301(b)(5) Fair Access reasons."
    claim_type: venue_mechanics
    load_bearing: true
    affects: [identification, data_quality]
    status: UNVERIFIED
    source_class: ATS_SERVICE_ALERT
    source_id: blue-ocean-service-status

  # --- Transition schedule and regulation -----------------------------------------------------
  - claim_id: C-NASDAQ-NIGHT-SESSION
    claim_text: "Nasdaq's 23-hour framework (34-105199) has a 9:00pm-4:00am Night Session targeted for 6 Dec 2026 (ETA 2026-46)."
    claim_type: schedule
    load_bearing: true
    affects: [identification]
    status: UNVERIFIED
    source_class: EXCHANGE_NOTICE
    source_id: nasdaq-eta-2026-46
    notes: "Approval side: nasdaq-34-105199."
  - claim_id: C-ARCA-OVERNIGHT-SESSION
    claim_text: "NYSE Arca's Overnight Session runs 9:00pm-4:00am ET, targeted for 6 Dec 2026."
    claim_type: schedule
    load_bearing: true
    affects: [identification]
    status: UNVERIFIED
    source_class: EXCHANGE_RULE
    source_id: nysearca-sr-2026-53
  - claim_id: C-EDGX-APPROVAL
    claim_text: "Cboe EDGX received accelerated approval for extended overnight trading on 29 May 2026."
    claim_type: regulatory_status
    load_bearing: true
    affects: [identification]
    status: UNVERIFIED
    source_class: SEC_ORDER
    notes: "Locate the SEC approval order; add it to config/monitoring.yaml."
  - claim_id: C-24X-OVERNIGHT
    claim_text: "24X Exchange publishes a 9:00pm-4:00am overnight session targeted for 6 Dec 2026."
    claim_type: schedule
    load_bearing: true
    affects: [identification]
    status: UNVERIFIED
    source_class: EXCHANGE_NOTICE
    notes: "Locate the 24X notice; add it to config/monitoring.yaml."
  - claim_id: C-MEMX-FILING
    claim_text: "MEMX filed for 23-hour trading on 9 Sep 2026 (SR-MEMX-2026-28)."
    claim_type: regulatory_status
    load_bearing: true
    affects: [identification]
    status: UNVERIFIED
    source_class: EXCHANGE_RULE
    notes: "Release number unverified (v2.2 §12)."
  - claim_id: C-SIP-HOURS
    claim_text: "From 6 Dec 2026 the equities SIPs run 9:00pm ET Sunday to 8:00pm ET Friday with an 8-9pm maintenance pause Monday-Thursday."
    claim_type: schedule
    load_bearing: true
    affects: [identification, session_logic]
    status: UNVERIFIED
    source_class: SEC_STAFF
    source_id: sec-staff-memo-24h-2026-09
  - claim_id: C-NSCC-24X5
    claim_text: "NSCC 24x5 clearing went live 29 Jun 2026, running Sunday 8:00pm ET to Friday 8:00pm ET."
    claim_type: schedule
    load_bearing: true
    affects: [date_logic]
    status: UNVERIFIED
    source_class: NSCC_NOTICE
    notes: "Archive the operative NSCC UTC technical notice before Week 2 date logic (v2.2 §12)."
  - claim_id: C-REGNMS-611-610E-PROPOSED
    claim_text: "SEC S7-2026-20 (Release 34-105655, 11 Jun 2026) proposes rescinding Rule 611 and Rule 610(e); status proposed."
    claim_type: regulatory_status
    load_bearing: true
    affects: [data_quality, identification]
    status: UNVERIFIED
    source_class: SEC_RULE
    source_id: sec-s7-2026-20
    recheck_trigger: weekly
  - claim_id: C-LULD-OVERNIGHT-STATIC
    claim_text: "Overnight LULD bands are published once at 9:00pm, stay static, and are cleared at 4:00am; approved 5 Aug 2026."
    claim_type: regulatory_status
    load_bearing: false
    affects: [context_only]
    status: UNVERIFIED
    source_class: SEC_ORDER
  - claim_id: C-FINRA-PUBLICATION-LAG
    claim_text: "FINRA ATS Transparency data is delayed at least two weeks for Tier 1 and at least four weeks for other NMS stocks."
    claim_type: data_semantics
    load_bearing: true
    affects: [sample]
    status: UNVERIFIED
    source_class: FINRA
    notes: "FINRA Rule 6110(c); archive the rule text."

  # --- Research baseline and citations --------------------------------------------------------
  - claim_id: C-LIM-BASELINE
    claim_text: "Lim (SSRN 6610883, rev. 21 Apr 2026): 30 symbols, 24 matched sessions, Sep 2025-Mar 2026; overnight ES about 7c/share and 10s PI about 2.4c/share above Nasdaq RTH."
    claim_type: statistic
    load_bearing: true
    affects: [metric_semantics]
    status: UNVERIFIED
    source_class: PAPER
    source_id: lim-ssrn-6610883-rev-2026-04-21
    recheck_trigger: "Verify every number against its table before D-8 (W4)"
  - claim_id: C-SEC-RELEASE-NUMBERS
    claim_text: "The SEC release numbers cited in project-plan v2.2 §12 are correct."
    claim_type: citation
    load_bearing: false
    affects: [publication]
    status: UNVERIFIED
    notes: "Open each on sec.gov before publication."
```

- [ ] **Step 4: Write `registry/events.yaml`.** `effective_to` is exclusive. Launch targets are `go_live_target` values, not statuses (r2.1 §23.3).

```yaml
# Market-structure event registry (v2.2 §8.3; r2.1 §7, §23.3). One registry for research and tracker.
# Seeded Week 1. Verification status lives on the linked claims (registry/claims.yaml).
events:
  # --- BOATS ----------------------------------------------------------------------------------
  - event_id: E-BOATS-SESSION-HOURS
    entity: BOATS
    field: session_hours
    value: {open: "20:00", close: "04:00", tz: America/New_York, days: [SUN, MON, TUE, WED, THU], test_orders_from: "18:15"}
    status: CURRENT
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-BOATS-SESSION-HOURS, C-BOATS-OPERATING-DAYS]
    load_bearing: true
  - event_id: E-BOATS-TRADE-DATE-RULE
    entity: BOATS
    field: trade_date_rule
    value: "Executions from 20:00 to midnight ET belong to the next trading day"
    status: CURRENT
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-BOATS-TRADE-DATE]
    load_bearing: true
  - event_id: E-BOATS-ORDER-TYPES-2023-BROKER-PRIORITY
    entity: BOATS
    field: order_types
    value: {aspect: broker_priority_election, present: true}
    status: SUPERSEDED
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-BOATS-BROKER-PRIORITY-SUPERSEDED]
    load_bearing: true
    notes: "Historical only; effective interval from the amendment chain (Stage B, W2)."
  - event_id: E-BOATS-ORDER-TYPES-CURRENT
    entity: BOATS
    field: order_types
    value:
      aspect: order_types
      types: [LIMIT]
      time_in_force: [DAY, IOC]
      display: [DISPLAYED, NON_DISPLAYED]
      instructions: [POST_ONLY]
      unsupported: [MARKET, PEGGED]
      priority: price_time
      counterparty_selection: false
    status: CURRENT
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    supersedes: E-BOATS-ORDER-TYPES-2023-BROKER-PRIORITY
    claim_ids: [C-BOATS-ORDER-TYPES, C-BOATS-BROKER-PRIORITY-SUPERSEDED]
    load_bearing: false
  - event_id: E-BOATS-2025-IOC-DISPLAY
    entity: BOATS
    field: order_types
    value: {aspect: ioc_and_display_directions_introduced}
    status: PENDING_VERIFICATION
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-BOATS-2025-IOC-DISPLAY]
    load_bearing: true
    notes: "Stage B (W2). If unresolved by Wed 30 Sep, carry as UNKNOWN_EFFECTIVE into W3 break diagnostics."
  - event_id: E-BOATS-BAND-15PCT-2023
    entity: BOATS
    field: price_band_rule
    value: {aspect: band_width, band_pct: 15}
    status: ERRONEOUS_DISCLOSURE
    effective_granularity: never
    effective_from: null
    effective_to: null
    claim_ids: [C-BOATS-BAND-15PCT-ERRONEOUS]
    load_bearing: true
  - event_id: E-BOATS-BAND-20PCT
    entity: BOATS
    field: price_band_rule
    value: {aspect: band_width, band_pct: 20, reference: "last national-exchange print reported to the SIP as of 19:30 ET", static_for_session: true}
    status: CURRENT
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    correction_of: E-BOATS-BAND-15PCT-2023
    claim_ids: [C-BOATS-BAND-20PCT, C-BOATS-BAND-15PCT-ERRONEOUS]
    load_bearing: true
  - event_id: E-BOATS-OOB-REJECT-2026-03-01
    entity: BOATS
    field: price_band_rule
    value: {aspect: out_of_band_passive_handling, action: REJECT_AT_ENTRY}
    status: SUPERSEDED
    effective_granularity: day
    effective_from: 2026-03-01
    effective_to: 2026-07-20
    claim_ids: [C-BOATS-2026-03-01-OOB-REJECT]
    load_bearing: true
  - event_id: E-BOATS-OOB-NONDISPLAYED-2026-07-20
    entity: BOATS
    field: price_band_rule
    value: {aspect: out_of_band_passive_handling, action: ACCEPT_NON_DISPLAYED_NOT_EXECUTABLE, in_market_data: false}
    status: CURRENT
    effective_granularity: day
    effective_from: 2026-07-20
    effective_to: null
    supersedes: E-BOATS-OOB-REJECT-2026-03-01
    claim_ids: [C-BOATS-2026-07-20-OOB-NONDISPLAYED]
    load_bearing: true
  - event_id: E-BOATS-FAIR-ACCESS-HALTS-END-2026-09-10
    entity: BOATS
    field: halt_rule
    value: {aspect: rule_301b5_fair_access_halts, action: NONE}
    status: CURRENT
    effective_granularity: day
    effective_from: 2026-09-10
    effective_to: null
    claim_ids: [C-BOATS-2026-09-10-FAIR-ACCESS]
    load_bearing: true
  - event_id: E-BOATS-NO-LOCKED-BOOK
    entity: BOATS
    field: market_data_status
    value: {aspect: locked_or_crossed_displayed_bbo, expected: never, on_observation: FEED_ANOMALY}
    status: CURRENT
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-BOATS-NO-LOCKED-BOOK]
    load_bearing: true

  # --- Exchanges ------------------------------------------------------------------------------
  - event_id: E-NASDAQ-NIGHT-SESSION-HOURS
    entity: NASDAQ
    field: session_hours
    value: {session: Night, open: "21:00", close: "04:00", tz: America/New_York}
    status: APPROVED_NOT_EFFECTIVE
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-NASDAQ-NIGHT-SESSION]
    load_bearing: true
  - event_id: E-NASDAQ-GO-LIVE-TARGET
    entity: NASDAQ
    field: go_live_target
    value: 2026-12-06
    status: CURRENT
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-NASDAQ-NIGHT-SESSION]
    load_bearing: true
  - event_id: E-ARCA-OVERNIGHT-SESSION-HOURS
    entity: NYSE_ARCA
    field: session_hours
    value: {session: Overnight, open: "21:00", close: "04:00", tz: America/New_York, opening_auction: false}
    status: APPROVED_NOT_EFFECTIVE
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-ARCA-OVERNIGHT-SESSION]
    load_bearing: true
  - event_id: E-ARCA-GO-LIVE-TARGET
    entity: NYSE_ARCA
    field: go_live_target
    value: 2026-12-06
    status: CURRENT
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-ARCA-OVERNIGHT-SESSION]
    load_bearing: true
  - event_id: E-EDGX-REG-STATUS
    entity: CBOE_EDGX
    field: reg_status
    value: {approval: accelerated, approved_on: 2026-05-29, framework: overnight trading}
    status: APPROVED_NOT_EFFECTIVE
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-EDGX-APPROVAL]
    load_bearing: true
  - event_id: E-24X-OVERNIGHT-SESSION-HOURS
    entity: 24X
    field: session_hours
    value: {open: "21:00", close: "04:00", tz: America/New_York}
    status: PENDING_VERIFICATION
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-24X-OVERNIGHT]
    load_bearing: true
    notes: "Approval status not yet established."
  - event_id: E-24X-GO-LIVE-TARGET
    entity: 24X
    field: go_live_target
    value: 2026-12-06
    status: CURRENT
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-24X-OVERNIGHT]
    load_bearing: true
  - event_id: E-MEMX-REG-STATUS
    entity: MEMX
    field: reg_status
    value: {filing: SR-MEMX-2026-28, filed_on: 2026-09-09, framework: 23-hour trading}
    status: PROPOSED
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-MEMX-FILING]
    load_bearing: true

  # --- Infrastructure and regulation ----------------------------------------------------------
  - event_id: E-SIP-HOURS-23X5
    entity: SIP
    field: session_hours
    value: {open: "SUN 21:00", close: "FRI 20:00", maintenance_pause: "MON-THU 20:00-21:00", tz: America/New_York}
    status: APPROVED_NOT_EFFECTIVE
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-SIP-HOURS]
    load_bearing: true
  - event_id: E-SIP-GO-LIVE-TARGET
    entity: SIP
    field: go_live_target
    value: 2026-12-06
    status: CURRENT
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-SIP-HOURS]
    load_bearing: true
  - event_id: E-NSCC-CLEARING-24X5
    entity: NSCC
    field: clearing_hours
    value: {open: "SUN 20:00", close: "FRI 20:00", tz: America/New_York}
    status: CURRENT
    effective_granularity: day
    effective_from: 2026-06-29
    effective_to: null
    claim_ids: [C-NSCC-24X5]
    load_bearing: true
  - event_id: E-REGNMS-611-610E-PROPOSAL
    entity: REG_NMS
    field: reg_status
    value: {file_number: S7-2026-20, release_number: 34-105655, sec_issue_date: 2026-06-11, comment_due: 2026-08-17, proposal: "rescind Rule 611 and Rule 610(e)"}
    status: PROPOSED
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-REGNMS-611-610E-PROPOSED]
    load_bearing: true
  - event_id: E-LULD-OVERNIGHT-STATIC-BANDS
    entity: LULD
    field: price_band_rule
    value: {aspect: overnight_bands, published_at: "21:00", cleared_at: "04:00", static: true}
    status: APPROVED_NOT_EFFECTIVE
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    claim_ids: [C-LULD-OVERNIGHT-STATIC]
    load_bearing: false

# Provisional BOATS rule versions (r2.1 §7). Stage B (W2) may split them; labels are technical names.
rule_versions:
  - rule_version: BOATS_2025_IOC_DISPLAY_TBD
    venue: BOATS
    effective_granularity: unknown
    effective_from: null
    effective_to: null
    basis_event_ids: [E-BOATS-2025-IOC-DISPLAY]
    provisional: true
    notes: "Placeholder: Stage B sets the interval and may split BOATS_PRE_2026_03_01."
  - rule_version: BOATS_PRE_2026_03_01
    venue: BOATS
    effective_granularity: day
    effective_from: null
    effective_to: 2026-03-01
    basis_event_ids: [E-BOATS-OOB-REJECT-2026-03-01]
    provisional: true
  - rule_version: BOATS_2026_03_01_TO_2026_07_19
    venue: BOATS
    effective_granularity: day
    effective_from: 2026-03-01
    effective_to: 2026-07-20
    basis_event_ids: [E-BOATS-OOB-REJECT-2026-03-01, E-BOATS-OOB-NONDISPLAYED-2026-07-20]
    provisional: true
  - rule_version: BOATS_2026_07_20_TO_2026_09_09
    venue: BOATS
    effective_granularity: day
    effective_from: 2026-07-20
    effective_to: 2026-09-10
    basis_event_ids: [E-BOATS-OOB-NONDISPLAYED-2026-07-20, E-BOATS-FAIR-ACCESS-HALTS-END-2026-09-10]
    provisional: true
  - rule_version: BOATS_POST_2026_09_10
    venue: BOATS
    effective_granularity: day
    effective_from: 2026-09-10
    effective_to: null
    basis_event_ids: [E-BOATS-FAIR-ACCESS-HALTS-END-2026-09-10]
    provisional: true
```

- [ ] **Step 5: Write `config/datasets.yaml`**

```yaml
# Databento spend control. The Week 3 cost guard enforces spend_cap_usd in code, not by memory.
vendor: databento
credit:
  amount_usd: 125
  signup_date: null   # Task 12: record at signup (YYYY-MM-DD)
  expires_on: null    # Task 12: record the expiry the portal shows (claim C-DBN-CREDIT-EXPIRY)
spend_cap_usd: 125    # = the credit until paid spend is approved (weekly §7, Week 4)
datasets:
  OCEA.MEMOIR:
    schemas: [tbbo, mbp-1, bbo-1s, status]
  XNAS.ITCH:
    schemas: [tbbo, mbp-1]
never_request: [mbo]  # L3 exhausts the credit (v2.2 §4)
```

- [ ] **Step 6: Write `config/licensing.yaml`**

```yaml
# Stage C permissions matrix (r2.1 Stage C; v2.2 §12 Contractual).
# Cells: PENDING | ALLOWED | ALLOWED_WITH_ATTRIBUTION | PROHIBITED | NOT_APPLICABLE
# freeze-required may pass with PENDING cells; release-required may not (gate G5).
questions_sent:        # ISO date each written question went out (Task 12)
  databento: null
  blue_ocean: null
  nasdaq: null
  finra: null
permissions:
  - output_type: aggregate_spread_statistics
    ocea: PENDING
    xnas: PENDING
    finra: NOT_APPLICABLE
    attribution: PENDING
    survives_termination: PENDING
    release_status: PENDING
  - output_type: regression_coefficients
    ocea: PENDING
    xnas: PENDING
    finra: NOT_APPLICABLE
    attribution: PENDING
    survives_termination: PENDING
    release_status: PENDING
  - output_type: percentiles
    ocea: PENDING
    xnas: PENDING
    finra: NOT_APPLICABLE
    attribution: PENDING
    survives_termination: PENDING
    release_status: PENDING
  - output_type: figures
    ocea: PENDING
    xnas: PENDING
    finra: NOT_APPLICABLE
    attribution: PENDING
    survives_termination: PENDING
    release_status: PENDING
  - output_type: venue_share_from_finra
    ocea: NOT_APPLICABLE
    xnas: NOT_APPLICABLE
    finra: PENDING
    attribution: PENDING
    survives_termination: PENDING
    release_status: PENDING
  - output_type: preregistration_aggregates
    ocea: PENDING
    xnas: PENDING
    finra: PENDING
    attribution: PENDING
    survives_termination: PENDING
    release_status: PENDING
```

- [ ] **Step 7: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_repo_data.py -v && uv run night-tape registry check`
Expected: 4 passed, then `ok: 38 claims, 24 events, 5 rule versions`.

Run: `make evidence-load-bearing; echo "exit=$?"`
Expected: 35 `status UNVERIFIED` lines, `35 load-bearing claims, 35 block the freeze`, and `exit=2`. That is expected in Week 1 (weekly W1 Build).

- [ ] **Step 8: Full check and commit**

```bash
make test
git add registry config/datasets.yaml config/licensing.yaml tests/unit/test_repo_data.py
git commit -S -m "feat: seed claim register, event registry, spend cap and licensing matrix"
```

---

### Task 10: Databento cost quotes

**Files:**
- Create: `src/night_tape/cost.py`, `tests/unit/test_cost.py`
- Modify: `src/night_tape/cli.py`

**Interfaces:**
- Produces:
  - `cost.quote(metadata: Any, *, dataset: str, schema: str, symbols: list[str], start: str, end: str, sdk_version: str, stype_in: str = "raw_symbol") -> dict[str, Any]`, which returns the keys `request`, `sdk_version`, `quoted_at_utc`, `cost_usd`, `billable_bytes` and `record_count`
  - `cost.save(doc: dict[str, Any], out_dir: Path) -> Path`, which refuses to overwrite
- The W3 cost guard reuses `quote()`.
- CLI: `night-tape cost quote --dataset D --schemas a,b --symbols S --start ISO --end ISO [--out benchmarks/cost]`

- [ ] **Step 1: Write the failing tests** — `tests/unit/test_cost.py`

```python
import json
from pathlib import Path
from typing import Any

import pytest

from night_tape.cost import quote, save


class FakeMetadata:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get_cost(self, **kw: Any) -> float:
        self.calls.append(("cost", kw))
        return 0.42

    def get_billable_size(self, **kw: Any) -> int:
        self.calls.append(("size", kw))
        return 1234

    def get_record_count(self, **kw: Any) -> int:
        self.calls.append(("count", kw))
        return 56


def make_quote(md: FakeMetadata) -> dict[str, Any]:
    return quote(md, dataset="OCEA.MEMOIR", schema="tbbo", symbols=["SPY"],
                 start="2026-09-21T00:00:00Z", end="2026-09-21T08:00:00Z", sdk_version="0.0.test")


def test_one_identical_request_goes_to_all_three_metadata_calls() -> None:
    md = FakeMetadata()
    q = make_quote(md)
    assert [name for name, _ in md.calls] == ["cost", "size", "count"]
    assert all(kw == q["request"] for _, kw in md.calls)
    assert q["request"]["stype_in"] == "raw_symbol"
    assert (q["cost_usd"], q["billable_bytes"], q["record_count"]) == (0.42, 1234, 56)
    assert q["sdk_version"] == "0.0.test" and q["quoted_at_utc"].endswith("Z")


def test_save_writes_json_and_never_overwrites(tmp_path: Path) -> None:
    q = make_quote(FakeMetadata())
    path = save(q, tmp_path)
    assert path.name.endswith("-OCEA.MEMOIR-tbbo.json")
    assert json.loads(path.read_text())["cost_usd"] == 0.42
    with pytest.raises(FileExistsError):
        save(q, tmp_path)
```

- [ ] **Step 2: Run them and watch them fail**

Run: `uv run pytest tests/unit/test_cost.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'night_tape.cost'`

- [ ] **Step 3: Write `src/night_tape/cost.py`**

```python
"""Record Databento cost, billable size and record count for one request. Never downloads data.

Weekly W1 task 9 baseline; the Week 3 cost guard calls quote() before every pull.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def quote(
    metadata: Any,  # databento.Historical().metadata
    *,
    dataset: str,
    schema: str,
    symbols: list[str],
    start: str,
    end: str,
    sdk_version: str,
    stype_in: str = "raw_symbol",
) -> dict[str, Any]:
    request = {"dataset": dataset, "schema": schema, "symbols": symbols,
               "start": start, "end": end, "stype_in": stype_in}
    return {
        "request": request,
        "sdk_version": sdk_version,
        "quoted_at_utc": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "cost_usd": float(metadata.get_cost(**request)),
        "billable_bytes": int(metadata.get_billable_size(**request)),
        "record_count": int(metadata.get_record_count(**request)),
    }


def save(doc: dict[str, Any], out_dir: Path) -> Path:
    r = doc["request"]
    path = out_dir / f"{doc['quoted_at_utc'].replace(':', '')}-{r['dataset']}-{r['schema']}.json"
    if path.exists():
        raise FileExistsError(path)
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
```

- [ ] **Step 4: Add `cost quote` to `src/night_tape/cli.py`**

Add the import `from night_tape import cost`. In `build_parser`, add `_add_cost(sub)`. Then add:

```python
def _add_cost(sub: Subparsers) -> None:
    c = sub.add_parser("cost", help="Databento cost quotes (metadata only; never downloads data)")
    cs = c.add_subparsers(dest="cost_command", required=True, metavar="ACTION")
    p = cs.add_parser("quote", help="save cost/size/count quotes as JSON, one file per schema")
    p.add_argument("--dataset", required=True)
    p.add_argument("--schemas", required=True, help="comma-separated, e.g. tbbo,mbp-1")
    p.add_argument("--symbols", required=True, help="comma-separated raw symbols")
    p.add_argument("--start", required=True, help="UTC ISO-8601, inclusive")
    p.add_argument("--end", required=True, help="UTC ISO-8601, exclusive")
    p.add_argument("--stype-in", default="raw_symbol")
    p.add_argument("--out", type=Path, default=Path("benchmarks/cost"))
    p.set_defaults(handler=_cost_quote)


def _cost_quote(args: argparse.Namespace) -> int:
    import databento as db  # imported here: only this command touches the paid API

    client = db.Historical()  # reads DATABENTO_API_KEY from the environment
    for schema in args.schemas.split(","):
        doc = cost.quote(
            client.metadata, dataset=args.dataset, schema=schema, symbols=args.symbols.split(","),
            start=args.start, end=args.end, stype_in=args.stype_in, sdk_version=db.__version__,
        )
        print(f"{cost.save(doc, args.out)}  ${doc['cost_usd']:.4f}  {doc['billable_bytes']} B")
    return 0
```

If mypy reports missing stubs for `databento`, add to `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = ["databento", "databento.*"]
ignore_missing_imports = true
```

- [ ] **Step 5: Run the tests and confirm they pass**

Run: `uv run pytest tests/unit/test_cost.py -v`
Expected: 2 passed

- [ ] **Step 6: Full check and commit**

```bash
make test
git add src/night_tape/cost.py src/night_tape/cli.py tests/unit/test_cost.py pyproject.toml
git commit -S -m "feat: add Databento cost/size/count quote command"
```

---

### Task 11: Documents: prereg skeleton, r2.2, v2.3 draft

**Files:**
- Create: `preregistration/prereg.md`, `docs/plans/project-plan-v2.3.md`
- Rename + modify: `docs/plans/technical-plan-r2.1.md` → `docs/plans/technical-plan-r2.2.md`
- Modify: `CLAUDE.md`, `docs/superpowers/specs/2026-09-22-claude-md-and-week1-design.md`

**Interfaces:**
- Produces:
  - `preregistration/prereg.md`: every TBD names its decision ID and latest week. Week 6 `prereg-check` fails on any remaining `TBD`.
  - r2.2 keeps r2.1's section numbers, so every `r2.1 §N` reference in the weekly plan still resolves.

- [ ] **Step 1: Write `preregistration/prereg.md`**

```markdown
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
```

- [ ] **Step 2: Produce r2.2, which folds in weekly-build-plan §1**

```bash
mv docs/plans/technical-plan-r2.1.md docs/plans/technical-plan-r2.2.md
```

In `docs/plans/technical-plan-r2.2.md`, make these edits. The line numbers are from the r2.1 file.

1. Frontmatter:
   - `technical_plan_version: "2026-09-22-validated-r2.2"`
   - `pre_event_freeze_target: "2026-10-30"`
   - add `amendment_r2_2: "Folds weekly-build-plan §1: freeze 30 Oct; canonical core before pilot; OCEA.MEMOIR findings (record_idx, trade_id, ordering key); FEED_ANOMALY, PRE_SESSION; calendar facts."`
2. `October 15` → `October 30` on lines 28, 30, 35, 182, 184, 202, 212, 659 and 1571.
3. `Oct 15` → `Oct 30` on lines 429, 1215, 1325 and 1417.
4. Line 1501: `OCTOBER 15 INTERNAL FREEZE` → `OCTOBER 30 INTERNAL FREEZE`.
5. Line 1627: tag message `2026-10-15` → `2026-10-30`.
6. Line 1160: `by Oct 13` → `by Oct 28`. Line 1180: `TBD_BEFORE_2026_10_13` → `TBD_BEFORE_2026_10_28`.
7. Leave the §1.1 decision table (lines 57, 58, 64, 66) unchanged. It is a historical record.
8. Under the §12 heading, add: *"Stage dates below are r2.1's compressed schedule; the operative schedule is weekly-build-plan §2. Stages I–K are first built in Week 2 on synthetic fixtures, before the Stage E pilot; in Week 5 they are scale-up and hardening."*
9. §8.1 field list:
   - add `trade_id` as the first field;
   - add `record_idx` after `sequence`;
   - rename `clearing_business_date` → `nscc_clearing_business_date` (the §7 name).

   §8.2: add `record_idx` after `sequence`.
10. Line 525: `(ts_event, sequence)` → `(ts_event, sequence, record_idx)`. Then add: *"Records normalized from one native MEMOIR message share `sequence`; `record_idx` is the record's position in its source file, assigned at normalization."*
11. §11 reason codes: after `UNKNOWN_SESSION_DATE`, add `FEED_ANOMALY` (locked/crossed displayed BOATS BBO that the ATS-N says should not persist; investigate) and `PRE_SESSION` (records before 8:00pm ET, e.g. test orders).
12. End of §2.4: add *"OCEA.MEMOIR-specific behaviour (`side = N` for non-displayed executions, shared `sequence`, no bust/correct normalization, CMS symbols, session-scoped IDs, single venue timestamp, `status` schema): weekly-build-plan §1.3."*
13. End of §7: add *"Calendar facts (DST 1 Nov 2026, one-UTC-date sessions, session-defined event, holidays): weekly-build-plan §1.5."*

Verify:

Run: `grep -nE 'October 15|Oct 1[35]|10-15|10_13' docs/plans/technical-plan-r2.2.md`
Expected: only the §1.1 decision-table lines (57, 58, 64, 66) and the Stage Q heading (1190). The step-8 note covers stage dates.

- [ ] **Step 3: Start v2.3 of the project plan**

```bash
cp docs/plans/project-plan-v2.2.md docs/plans/project-plan-v2.3.md
```

In `docs/plans/project-plan-v2.3.md`:

1. **Header.** Change it to `Version 2.3 (draft) · <today>`. Replace the "Changes from v2.1" block with a "Changes from v2.2" list:
   1. BOATS mechanics follow the current Form ATS-N and its amendment chain (r2.2 §2.1):
      - one LIMIT order type, DAY or IOC, displayed or non-displayed;
      - POST-ONLY, DAY-only;
      - no MARKET or PEGGED;
      - price-time priority;
      - no counter-party selection.
   2. Broker Priority is historical (2023 ATS-N), superseded by the 2024 correcting amendment.
   3. 6:15pm is for test orders only. The 105-minute accumulation analogy is deleted.
   4. There are three dated BOATS breaks in the pre-period (1 Mar, 20 Jul, 10 Sep 2026), plus the 2025 IOC/display amendments, whose dates are pending Stage B.
   5. `side = None` marks non-displayed executions per Databento's OCEA.MEMOIR page. It is a vendor claim, tested in the Week 3 pilot; D-1 sets the endpoint population.
   6. The freeze moves to 30 Oct 2026.
2. **§2.4 "Order types".** Replace the paragraph with item 1.
3. **§2.4 "Broker Priority".** Replace the paragraph with: *"Historical only. The 2023 ATS-N described a Broker Priority election; a 2024 correcting amendment restored price-time wording, and the current filing has no counter-party selection. Apply it to data only if its effective interval is established from the amendment chain."*
4. **§2.4 "Order entry opens at 6:15pm…".** Replace the paragraph with: *"6:15pm is for test orders only. Bona-fide orders are accepted, and matching starts, at 8:00pm. Records before 8:00pm ET carry reason code `PRE_SESSION`."*
5. **§2.4 break table.** Rename it "Three known structural breaks" and add the row `1 March 2026 | Passive orders outside the 20% band rejected at entry` above 20 July. Update §2.4's closing paragraph, §7 gotcha 11 and the §11 risk row to list all three dates.
6. **§6, "What is actually unknown".** Append: *"Databento's OCEA.MEMOIR page documents one mechanism: trades from the MEMOIR Trade message (non-displayed executions) carry `side = N`. The pilot tests it by checking that the displayed BBO is unchanged across each such trade."*
7. **§6, "A better-grounded explanation exists".** Replace the Broker Priority sentence with: *"Unusual price locations may reflect non-displayed executions (above). Non-displayed out-of-band orders are also excluded from the feed, so location is measured against an incomplete book."*
8. **Footer error history.** Append: *"v2.2 carried Broker Priority, 'limit day orders only' and a 105-minute accumulation from an older ATS-N and an FAQ; the r2.1 amendment-chain review superseded all three."*

Verify:

Run: `grep -nE 'Broker Priority|105|limit day' docs/plans/project-plan-v2.3.md`
Expected: only historical/superseded mentions in the changes list, §2.4 "historical only" and the error history.

- [ ] **Step 4: Point CLAUDE.md at the new versions**

In `CLAUDE.md`:
- replace every `technical-plan-r2.1.md` with `technical-plan-r2.2.md`, and every `r2.1 §` with `r2.2 §`;
- replace `project-plan-v2.2.md` with `project-plan-v2.3.md`;
- in "When docs conflict", delete both stale-text bullets (r2.2 and v2.3 absorb them) and keep the precedence line as: *"weekly §1 beats r2.2, which beats v2.3."*

In the spec's doc-layout table, update the two paths as well.

Run: `wc -l CLAUDE.md && grep -rn 'r2\.1\.md\|v2\.2\.md' CLAUDE.md docs/superpowers`
Expected: under 200 lines, and no stale paths. Historical mentions inside this plan are fine.

- [ ] **Step 5: Commit (signed)**

```bash
git add preregistration/prereg.md docs/plans CLAUDE.md docs/superpowers/specs
git commit -S -m "docs: prereg skeleton, technical plan r2.2, project plan v2.3 draft"
```

---

### Task 12: Operate: archive, verify claims, open the clocks, record the week

Most of this task runs outside the code. Steps marked **(user)** need the user: accounts, emails, decisions. Don't do them on the user's behalf.

**Files:**
- Create: `evidence/**` (via the CLI), `benchmarks/cost/*.json` (via the CLI), `docs/decisions/prereg_venue.md`, `docs/weekly/2026-W39.md`
- Modify: `registry/claims.yaml` (statuses), `config/datasets.yaml`, `config/licensing.yaml`, `config/monitoring.yaml` (URL fixes and newly located sources)

- [ ] **Step 1: Declare the User-Agent.** Ask the user for their contact string; don't guess an email. Put the export in `.envrc`, which is git-ignored:

```bash
echo 'export NIGHT_TAPE_USER_AGENT="night-tape research <contact email>"' >> .envrc
source .envrc
```

- [ ] **Step 2: Archive every configured source**

Run: `uv run night-tape evidence sync`
Expected: `archived …` lines, and `manual: lim-ssrn-6610883-rev-2026-04-21 not archived yet`.

For each `FAILED` line:
- **404 on an unverified URL:** find the real page, fix `config/monitoring.yaml`, re-run.
- **403 from SEC:** check that `NIGHT_TAPE_USER_AGENT` is set.
- **`PaginatedSubmissions`:** stop and extend `edgar.py`. Never hand-pick filings.

Re-run until nothing fails. Unchanged sources print `unchanged`.

- [ ] **Step 3 (user): Archive the pinned Lim PDF**

```bash
uv run night-tape evidence add ~/Downloads/<lim-file>.pdf \
  --url "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6610883" \
  --source-id lim-ssrn-6610883-rev-2026-04-21 --source-class PAPER \
  --notes "revision 21 Apr 2026"
```

- [ ] **Step 4: Gate check: the archive verifies**

Run: `make source-archive-verify`
Expected: `evidence ok`, exit 0.

Also check that the archive contains every ATS-N filing:

Run: `grep -c '"method": "edgar"' evidence/manifest.jsonl`
Then open the archived `CIK0001795131.json` and confirm that every `ATS-N*` accession it lists has files in the manifest.

- [ ] **Step 5: Verify claims against the archive.** For each claim in `registry/claims.yaml`, open its archived snapshot. Then do one of the following:
  - **The snapshot states the claim.** Set `status: VERIFIED` and fill in `retrieved_at`, `sha256` and `source_version_or_accession` from the manifest line (`grep <source_id> evidence/manifest.jsonl`). Correct `claim_text` if the source words it differently.
  - **The snapshot contradicts the claim.** Set `status: REFUTED` with a note, and record the finding in the weekly note.
  - **Same-tier sources disagree.** Set `status: CONFLICTED`. Never pick the newer-looking sentence.
  - **The source hasn't been located** (EDGX, 24X, MEMX, NSCC, FINRA, LULD). Search primary sites only (r2.1 §15). Add each hit to `config/monitoring.yaml`, re-run Steps 2 and 4, then verify.

Run: `uv run night-tape registry check && make evidence-load-bearing`
Expected: `check` is ok. `evidence-load-bearing` still lists gaps; that is expected in Week 1. Record the count in the weekly note.

- [ ] **Step 6 (user): Databento account and cost baseline**
  - Sign up and claim the credit.
  - Record `credit.signup_date` and the actual `credit.expires_on` shown in the portal in `config/datasets.yaml`.
  - Export the key in the shell only (never `.envrc` in the repo, never CI). The session below is Sun 20 Sep 2026, 8pm–4am EDT = 00:00–08:00 UTC, and the RTH day is Mon 21 Sep 2026, 9:30–16:00 EDT.

```bash
export DATABENTO_API_KEY=...   # this shell only
uv run night-tape cost quote --dataset OCEA.MEMOIR --schemas tbbo,mbp-1,bbo-1s,status \
  --symbols SPY --start 2026-09-21T00:00:00Z --end 2026-09-21T08:00:00Z
uv run night-tape cost quote --dataset XNAS.ITCH --schemas tbbo,mbp-1 \
  --symbols SPY --start 2026-09-21T13:30:00Z --end 2026-09-21T20:00:00Z
ls benchmarks/cost/
```

Expected: six JSON files, each with `cost_usd`, `billable_bytes` and `record_count`. If `status` is rejected as a schema name, record the error in the weekly note and quote the other three.

- [ ] **Step 7 (user): Licensing questions.** Send written questions to Databento, Blue Ocean and Nasdaq covering:
  - derived-data publication;
  - attribution;
  - survival after termination.

  Also read FINRA's terms for the ATS Transparency data. Use v2.2 §12 "Contractual" as the question list. Record each send date under `questions_sent` in `config/licensing.yaml`. Every matrix cell stays `PENDING`.

- [ ] **Step 8 (user): Sign D-0.** Create `docs/decisions/prereg_venue.md`:

```markdown
# D-0 — Preregistration venue and embargo

- Decision: <OSF registration | Zenodo DOI>
- Embargo: <yes, until YYYY-MM-DD | no>
- Why: <one paragraph: immutability, timestamp, DOI, embargo support, account ownership>
- Uploaded at freeze (Fri 30 Oct 2026): preregistration/prereg.md, archive SHA256SUMS,
  tag `v1.0-preregistered` and its commit hash. Aggregates only; check config/licensing.yaml first.
- Decided: <date> by <name>. Signed commit required (weekly App. C).
```

Then set `Prereg venue and embargo` in `preregistration/prereg.md` §10 to the decision.

- [ ] **Step 9: Weekly note** — create `docs/weekly/2026-W39.md`:

```markdown
# 2026-W39 (Tue 22 – Sun 27 Sep) — Week 1 foundations

## Gates
- Exit gate: <PASS | FAIL + which bullet>

## Done
- <deliverables checked off from weekly-build-plan §5 Week 1>

## Slipped
- <item — why — new date>

## Decisions signed
- D-0: <venue, embargo>

## Evidence
- Sources archived: <n> (ATS-N filings: <n>); sources added this week: <list>
- Claims: <n> VERIFIED, <n> UNVERIFIED, <n> CONFLICTED, <n> REFUTED; load-bearing gaps: <n>

## Money and clocks
- Databento credit: $<amount>, expires <date>; spend to date: $0
- Licensing questions sent: <dates>

## Open claims needing sources
- <claim_id — what's missing>
```

- [ ] **Step 10: Exit gate** (weekly-build-plan §5 Week 1). All four must hold:
  1. CI is green on the branch, and every commit is signed: `git log --format='%G? %s' main..HEAD` shows `G` on every line.
  2. `make source-archive-verify` passes, and the full BOATS ATS-N chain is in the manifest.
  3. `uv run night-tape registry check` passes.
  4. Cost JSON files exist in `benchmarks/cost/`, and `questions_sent` has dates.

Then run: `make freeze-required; echo "exit=$?"`
Expected: it fails at `evidence-load-bearing` or the first stub. That is the correct Week 1 state (weekly App. A).

- [ ] **Step 11: Commit and open the PR.** Ask the user before pushing.

```bash
git add evidence benchmarks/cost registry config docs/decisions docs/weekly preregistration
git commit -S -m "chore: archive Week 1 sources, verify claims, record cost baseline and D-0"
git push
gh pr create --base main --title "Week 1: foundations" --body "$(cat <<'EOF'
Week 1 of weekly-build-plan: scaffold, loud freeze stubs, contracts, evidence tooling,
seeded registries, archived sources, cost baseline. Exit gate: see docs/weekly/2026-W39.md.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Expected: CI `test` is green on the PR. Merge once the user approves.

---

## Deliverables → task map (weekly-build-plan §5 Week 1)

| Deliverable | Task |
|---|---|
| Repo scaffold, CI, signing, branch protection | 1, 2 |
| Stubbed Makefile (all freeze/release targets present) | 1 |
| Five contracts with tests; `record_idx` and `trade_id` added | 3 |
| Evidence fetch/verify CLI; EDGAR folder capture; Playwright capture | 4, 5, 6, 8 |
| Full BOATS ATS-N chain plus §18 sources archived and hashed | 8, 12 |
| Claim register and event registry seeded | 7, 9 |
| Prereg skeleton with dated TBDs | 11 |
| Databento account; credit expiry recorded; cost JSON saved | 10, 12 |
| Licensing questions sent; matrix at `PENDING` | 9, 12 |
| r2.1 date edits; v2.3 plan draft started; D-0 decided | 11, 12 |
