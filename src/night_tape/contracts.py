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
