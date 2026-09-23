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
