"""Build the documentation site into ./site for local preview and GitHub Pages.

The icon SVGs stay in the package. This script copies them next to the HTML
so the browser can show each one at its original proportions.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "site"
ICONS = ROOT / "src" / "infrasketch" / "data" / "icons"
EXAMPLES = (
    "web-api-redis.svg",
    "container-apps.svg",
    "aks-platform.svg",
    "functions-events.svg",
)


def aliases() -> dict[tuple[str, str], list[str]]:
    sys.path.insert(0, str(ROOT / "src"))
    import infrasketch.shortcuts as shortcuts

    found: dict[tuple[str, str], list[str]] = {}
    for public in shortcuts.__all__:
        obj = getattr(shortcuts, public)
        module = obj.__module__.rsplit(".", 1)[-1]
        found.setdefault((module, obj.__name__), []).append(public)
    for names in found.values():
        names.sort(key=lambda name: (len(name), name))
    return found


def catalog(alias_map: dict[tuple[str, str], list[str]]) -> list[dict]:
    raw = json.loads((ROOT / "src" / "infrasketch" / "data" / "catalog.json").read_text())
    rows = []
    for item in raw:
        names = alias_map.get((item["module"], item["name"]), [])
        imports = [f"from infrasketch import {name}" for name in names]
        imports.append(f"from infrasketch.{item['module']} import {item['name']}")
        rows.append(
            {
                "module": item["module"],
                "name": item["name"],
                "service": item["service"],
                "icon": f"icons/{item['icon']}",
                "aliases": names,
                "imports": list(dict.fromkeys(imports)),
            }
        )
    return rows


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(DOCS, OUT)
    shutil.copytree(ICONS, OUT / "icons")
    (OUT / "catalog.json").write_text(json.dumps(catalog(aliases()), indent=2) + "\n")
    example_dir = OUT / "examples"
    example_dir.mkdir()
    for name in EXAMPLES:
        shutil.copy(ROOT / "examples" / "out" / name, example_dir / name)
    (OUT / ".nojekyll").write_text("")
    count = sum(1 for _ in (OUT / "icons").rglob("*.svg"))
    print(f"wrote {OUT} with {count} icons")


if __name__ == "__main__":
    main()
