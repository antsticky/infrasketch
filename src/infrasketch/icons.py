"""Load official Azure SVG icons and make their ids safe to embed many times."""

from __future__ import annotations

import re
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

_SVG = re.compile(r"<svg\b([^>]*)>(.*)</svg>\s*$", re.IGNORECASE | re.DOTALL)
_ID = re.compile(r"""\bid\s*=\s*(['"])([^'"]+)\1""")
_CLASS_ATTR = re.compile(r"""\bclass\s*=\s*(['"])([^'"]+)\1""")
_CLASS_SEL = re.compile(r"\.(-?[_A-Za-z][\w-]*)")


@lru_cache(maxsize=1024)
def read_icon(spec: str) -> str:
    path = Path(spec)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    resource = files("infrasketch").joinpath("data", "icons", spec)
    try:
        return resource.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"No icon at {spec}. Find one with: python -m infrasketch search <name>"
        ) from exc


def embed_icon(spec: str, prefix: str, x: float, y: float, size: float) -> str:
    """Return a nested <svg> for one icon, scaled uniformly into a square."""
    viewbox, inner, namespaces = _prepare(read_icon(spec), prefix)
    ns = " ".join(namespaces) if namespaces else 'xmlns="http://www.w3.org/2000/svg"'
    if "xmlns=" not in ns:
        ns = 'xmlns="http://www.w3.org/2000/svg" ' + ns
    return (
        f'<svg x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" '
        f'viewBox="{viewbox}" preserveAspectRatio="xMidYMid meet" overflow="visible" {ns}>'
        f"{inner}</svg>"
    )


def _prepare(raw: str, prefix: str) -> tuple[str, str, list[str]]:
    text = raw.strip().lstrip("\ufeff")
    text = re.sub(r"<\?xml[^?]*\?>", "", text).strip()
    text = re.sub(r"<!DOCTYPE[^>]*>", "", text).strip()
    match = _SVG.search(text)
    if match is None:
        raise ValueError("Icon is not an SVG document")
    attrs, inner = match.group(1), match.group(2)
    viewbox_match = re.search(r'viewBox\s*=\s*"([^"]+)"', attrs) or re.search(
        r"viewBox\s*=\s*'([^']+)'", attrs
    )
    viewbox = viewbox_match.group(1) if viewbox_match else "0 0 18 18"
    namespaces = re.findall(r'\bxmlns(?::[\w]+)?\s*=\s*["\'][^"\']+["\']', attrs)

    ids = [item[1] for item in _ID.findall(inner)]
    mapping = {old: prefix + _safe(old) for old in ids}
    for old, new in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        inner = re.sub(
            rf"""\bid\s*=\s*(['"]){re.escape(old)}\1""",
            f'id="{new}"',
            inner,
        )
        inner = re.sub(
            rf"""url\(\s*(['"]?)#{re.escape(old)}\1\s*\)""",
            f"url(#{new})",
            inner,
        )
        inner = re.sub(
            rf"""(\b(?:href|xlink:href)\s*=\s*['"])#{re.escape(old)}(['"])""",
            rf"\1#{new}\2",
            inner,
        )

    class_names = set(_CLASS_SEL.findall(inner))
    for value in _CLASS_ATTR.findall(inner):
        class_names.update(value[1].split())
    for old in sorted(class_names, key=len, reverse=True):
        new = prefix + old
        inner = re.sub(rf"\.{re.escape(old)}\b", f".{new}", inner)

        def replace_class(match: re.Match[str], old: str = old, new: str = new) -> str:
            parts = [new if part == old else part for part in match.group(2).split()]
            return f"class={match.group(1)}{' '.join(parts)}{match.group(1)}"

        inner = _CLASS_ATTR.sub(replace_class, inner)
    return viewbox, inner, namespaces


def _safe(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", value)
    if cleaned and cleaned[0].isdigit():
        cleaned = "n" + cleaned
    return cleaned or "id"
