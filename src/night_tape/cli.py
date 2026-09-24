"""night-tape command line. Each command group is registered by one _add_* function."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Iterable, Sequence
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

from night_tape import contracts
from night_tape.evidence import fetch, verify
from night_tape.evidence.manifest import Entry

if TYPE_CHECKING:
    Subparsers = argparse._SubParsersAction[argparse.ArgumentParser]

Handler = Callable[[argparse.Namespace], int]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="night-tape", description="night-tape research pipeline")
    parser.add_argument("--version", action="version", version=version("night-tape"))
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    _add_evidence(sub)
    return parser


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
        _print_stored(
            [
                fetch.fetch(
                    args.evidence_dir,
                    client,
                    args.url,
                    source_id=args.source_id,
                    source_class=args.source_class,
                    supersedes=args.supersedes,
                    notes=args.notes,
                )
            ]
        )
    return 0


def _evidence_add(args: argparse.Namespace) -> int:
    _print_stored(
        [
            fetch.add_file(
                args.evidence_dir,
                args.path,
                url=args.url,
                source_id=args.source_id,
                source_class=args.source_class,
                content_type=args.content_type,
                notes=args.notes,
            )
        ]
    )
    return 0


def _report_verify(report: verify.Report) -> int:
    for label, items in (
        ("missing", report.missing),
        ("hash mismatch", report.mismatched),
        ("orphan", report.orphans),
        ("never archived", report.unarchived_sources),
    ):
        for item in items:
            print(f"{label}: {item}")
    print("evidence ok" if report.ok else "evidence FAILED", file=sys.stderr)
    return 0 if report.ok else 1


def _evidence_verify(args: argparse.Namespace) -> int:
    return _report_verify(verify.verify(args.evidence_dir))


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler: Handler = args.handler
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
