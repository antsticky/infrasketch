"""Look up resource classes without memorising the catalog."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files


@dataclass(frozen=True)
class IconInfo:
    """One cloud resource you can place on a diagram."""

    module: str
    name: str
    service: str
    icon: str
    provider: str = "azure"

    @property
    def import_line(self) -> str:
        if self.provider == "external":
            return f"from infrasketch.external import {self.name}"
        return f"from infrasketch.{self.provider}.{self.module} import {self.name}"

    def __str__(self) -> str:
        return f"{self.module}.{self.name}  —  {self.service}\n    {self.import_line}"


@lru_cache(maxsize=1)
def catalog() -> tuple[IconInfo, ...]:
    root = files("infrasketch").joinpath("data")
    rows = []
    for name in ("catalog.json", "aws-catalog.json", "external-catalog.json"):
        path = root.joinpath(name)
        if not path.is_file():
            continue
        for item in json.loads(path.read_text(encoding="utf-8")):
            item.setdefault("provider", "aws" if name.startswith("aws") else "azure")
            rows.append(IconInfo(**item))
    return tuple(rows)


def categories() -> list[str]:
    """Category names, such as ``azure/compute`` and ``aws/networking``."""
    return sorted({f"{item.provider}/{item.module}" for item in catalog()})


def search(query: str) -> list[IconInfo]:
    """Find resources by service name, class name, or category.

    Every word in ``query`` has to match. ``search("managed redis")`` finds
    Azure Managed Redis, and ``search("aws lambda")`` finds AWS Lambda.
    """
    words = query.lower().split()
    if not words:
        return []
    hits = []
    for item in catalog():
        haystack = f"{item.provider} {item.module} {item.name} {item.service}".lower()
        if all(word in haystack for word in words):
            hits.append(item)
    return hits
