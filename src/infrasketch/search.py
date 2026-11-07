"""Look up resource classes without memorising the catalog."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files


@dataclass(frozen=True)
class IconInfo:
    """One Azure resource you can place on a diagram."""

    module: str
    name: str
    service: str
    icon: str

    @property
    def import_line(self) -> str:
        return f"from infrasketch.{self.module} import {self.name}"

    def __str__(self) -> str:
        return f"{self.module}.{self.name}  —  {self.service}\n    {self.import_line}"


@lru_cache(maxsize=1)
def catalog() -> tuple[IconInfo, ...]:
    raw = files("infrasketch").joinpath("data", "catalog.json").read_text(encoding="utf-8")
    return tuple(IconInfo(**item) for item in json.loads(raw))


def categories() -> list[str]:
    """Category module names, such as ``compute`` and ``networking``."""
    return sorted({item.module for item in catalog()})


def search(query: str) -> list[IconInfo]:
    """Find resources by service name, class name, or category.

    Every word in ``query`` has to match. ``search("managed redis")`` finds
    Azure Managed Redis, and the result tells you exactly what to import.
    """
    words = query.lower().split()
    if not words:
        return []
    hits = []
    for item in catalog():
        haystack = f"{item.module} {item.name} {item.service}".lower()
        if all(word in haystack for word in words):
            hits.append(item)
    return hits
