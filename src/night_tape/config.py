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
