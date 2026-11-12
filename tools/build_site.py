"""Build the documentation site into ./site for local preview and GitHub Pages.

The icon SVGs stay in the package. This script copies them next to the HTML
so the browser can show each one at its original proportions.
"""

from __future__ import annotations

import json
import shutil
import sys
import time
import urllib.request
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import quote

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
    "azure-grid.svg",
    "custom-icon.svg",
    "azure-network.svg",
    "aws-orders.svg",
    "aws-eks.svg",
    "aws-events.svg",
    "azure-decisions.svg",
    "azure-folded.svg",
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


PYPI = "https://pypi.org/pypi/infrasketch/json"
VERSIONS = '<tbody id="versions"></tbody>'


def project_version() -> str:
    for line in (ROOT / "pyproject.toml").read_text().splitlines():
        if line.startswith("version = "):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("pyproject.toml has no version")


def pypi_releases() -> dict[str, datetime]:
    """Upload time of every version currently listed on PyPI."""
    request = urllib.request.Request(PYPI, headers={"User-Agent": "infrasketch-docs"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    found = {}
    for version, files in payload["releases"].items():
        uploaded = [item["upload_time"] for item in files if item.get("upload_time")]
        if uploaded:
            found[version] = datetime.fromisoformat(min(uploaded))
    return found


def wait_for_release(version: str) -> None:
    """Poll PyPI until the version that was just published is listed."""
    deadline = time.monotonic() + 180
    while True:
        if version in pypi_releases():
            print(f"PyPI lists {version}")
            return
        if time.monotonic() >= deadline:
            raise SystemExit(f"PyPI has not listed {version}")
        time.sleep(5)


def published_versions() -> list[tuple[str, str]]:
    """Every PyPI release, newest first."""
    ordered = sorted(pypi_releases().items(), key=lambda item: item[1], reverse=True)
    return [
        (version, f"{moment.day} {moment.strftime('%b')} {moment.year}")
        for version, moment in ordered
    ]


def fill_versions(html: str) -> str:
    if VERSIONS not in html:
        raise SystemExit("guide.html is missing the versions table")
    rows = []
    for version, published in published_versions():
        href = "https://pypi.org/project/infrasketch/" + quote(version) + "/"
        rows.append(
            f'<tr><td><a href="{href}"><code>{escape(version)}</code></a></td>'
            f"<td>{escape(published)}</td></tr>"
        )
    body = '<tbody id="versions">\n' + "\n".join(rows) + "\n</tbody>"
    return html.replace(VERSIONS, body, 1)


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
    if "--wait-for-release" in sys.argv:
        wait_for_release(project_version())
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(DOCS, OUT)
    guide = OUT / "guide.html"
    guide.write_text(fill_versions(guide.read_text()))
    shutil.copytree(ICONS, OUT / "icons")
    (OUT / "catalog.json").write_text(json.dumps(catalog(aliases()), indent=2) + "\n")
    example_dir = OUT / "examples"
    example_dir.mkdir()
    for name in EXAMPLES:
        shutil.copy(ROOT / "examples" / "out" / name, example_dir / name)
    for path in sorted((ROOT / "examples").glob("*.py")):
        shutil.copy(path, example_dir / path.name)
    (OUT / ".nojekyll").write_text("")
    count = sum(1 for _ in (OUT / "icons").rglob("*.svg"))
    print(f"wrote {OUT} with {count} icons")


if __name__ == "__main__":
    main()
