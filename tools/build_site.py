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
    "azure-web-api.svg",
    "azure-container-apps.svg",
    "azure-functions.svg",
    "azure-aks.svg",
    "azure-ai.svg",
    "azure-data.svg",
    "azure-network.svg",
    "aws-orders.svg",
    "aws-eks.svg",
    "aws-events.svg",
    "azure-decisions.svg",
    "aws-decisions.svg",
    "external-github.svg",
    "external-edge.svg",
)


def aliases() -> dict[tuple[str, str, str], list[str]]:
    sys.path.insert(0, str(ROOT / "src"))
    import infrasketch.aws as aws
    import infrasketch.azure as azure
    import infrasketch.external as external

    found: dict[tuple[str, str, str], list[str]] = {}
    for provider, module in (("azure", azure), ("aws", aws), ("external", external)):
        for public in module.__all__:
            obj = getattr(module, public)
            if not hasattr(obj, "icon"):
                continue
            category = obj.__module__.rsplit(".", 1)[-1]
            found.setdefault((provider, category, obj.__name__), []).append(public)
    for names in found.values():
        names.sort(key=lambda name: (len(name), name))
    return found


def catalog(alias_map: dict[tuple[str, str, str], list[str]]) -> list[dict]:
    from infrasketch.search import catalog as load_catalog

    rows = []
    for item in load_catalog():
        names = alias_map.get((item.provider, item.module, item.name), [])
        imports = [f"from infrasketch.{item.provider} import {name}" for name in names]
        imports.append(item.import_line)
        rows.append(
            {
                "provider": item.provider,
                "module": item.module,
                "name": item.name,
                "service": item.service,
                "icon": f"icons/{item.icon}",
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
