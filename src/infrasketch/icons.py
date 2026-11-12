"""Load an icon and make its ids safe to embed many times.

Packaged icons are SVG. A resource can also take a picture file: SVG, PNG,
JPEG, GIF, WebP, BMP, or ICO. The picture is fitted inside the icon square
without cropping or stretching.
"""

from __future__ import annotations

import base64
import re
import struct
import zlib
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

from infrasketch.model import DiagramError

_LIMIT = 4 * 1024 * 1024
_KINDS = "SVG, PNG, JPEG, GIF, WebP, BMP, or ICO"
_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

_SVG = re.compile(r"<svg\b([^>]*)>(.*)</svg>\s*$", re.IGNORECASE | re.DOTALL)
_ID = re.compile(r"""\bid\s*=\s*(['"])([^'"]+)\1""")
_CLASS_ATTR = re.compile(r"""\bclass\s*=\s*(['"])([^'"]+)\1""")
_CLASS_SEL = re.compile(r"\.(-?[_A-Za-z][\w-]*)")


@lru_cache(maxsize=1024)
def read_icon(spec: str) -> str:
    _suffix, raw = _load(spec)
    return raw.decode("utf-8")


def embed_icon(spec: str, prefix: str, x: float, y: float, size: float) -> str:
    """Return a nested <svg> for one icon, scaled uniformly into a square."""
    suffix, raw = _load(spec)
    if _looks_svg(suffix, raw):
        viewbox, inner, namespaces = _prepare(raw.decode("utf-8"), prefix)
        ns = " ".join(namespaces) if namespaces else 'xmlns="http://www.w3.org/2000/svg"'
        if "xmlns=" not in ns:
            ns = 'xmlns="http://www.w3.org/2000/svg" ' + ns
        return (
            f'<svg x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" '
            f'viewBox="{viewbox}" preserveAspectRatio="xMidYMid meet" overflow="visible" {ns}>'
            f"{inner}</svg>"
        )
    payload, mime = _picture(spec, suffix, raw)
    encoded = base64.b64encode(payload).decode("ascii")
    href = f"data:{mime};base64,{encoded}"
    return (
        f'<svg x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" '
        f'viewBox="0 0 {size:.0f} {size:.0f}" preserveAspectRatio="xMidYMid meet" overflow="visible" '
        f'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
        f'<image href="{href}" xlink:href="{href}" x="0" y="0" width="{size:.0f}" height="{size:.0f}" '
        f'preserveAspectRatio="xMidYMid meet"/></svg>'
    )


@lru_cache(maxsize=1024)
def _load(spec: str) -> tuple[str, bytes]:
    path = Path(spec)
    if path.is_file():
        raw = path.read_bytes()
    else:
        resource = files("infrasketch").joinpath("data", "icons", spec)
        try:
            raw = resource.read_bytes()
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"No icon at {spec}. Find one with: python -m infrasketch search <name>"
            ) from exc
    if len(raw) > _LIMIT:
        raise DiagramError(f"{spec} is too large to use as an icon")
    return path.suffix.lower(), raw


def _looks_svg(suffix: str, raw: bytes) -> bool:
    if suffix == ".svg":
        return True
    if suffix in _MIME or suffix in {".bmp", ".ico", ".cur"}:
        return False
    head = raw.lstrip()[:300].lower()
    return head.startswith((b"<svg", b"<?xml")) or b"<svg" in head


def _picture(spec: str, suffix: str, raw: bytes) -> tuple[bytes, str]:
    """Return bytes a browser can draw, and their media type."""
    mime = _MIME.get(suffix)
    if mime is not None:
        if not _magic(mime, raw):
            raise DiagramError(f"{spec} is not a {suffix[1:].upper()} picture")
        return raw, mime
    if suffix == ".bmp" or (suffix not in {".ico", ".cur"} and raw.startswith(b"BM")):
        return _bmp_to_png(raw), "image/png"
    if suffix in {".ico", ".cur"} or _looks_ico(raw):
        return _ico_to_png(raw), "image/png"
    raise DiagramError(f"{spec} is not a supported icon. Use {_KINDS}.")


def _magic(mime: str, raw: bytes) -> bool:
    if mime == "image/png":
        return raw.startswith(b"\x89PNG\r\n\x1a\n")
    if mime == "image/jpeg":
        return raw.startswith(b"\xff\xd8\xff")
    if mime == "image/gif":
        return raw.startswith((b"GIF87a", b"GIF89a"))
    if mime == "image/webp":
        return len(raw) >= 12 and raw.startswith(b"RIFF") and raw[8:12] == b"WEBP"
    return False


def _looks_ico(raw: bytes) -> bool:
    if len(raw) < 6:
        return False
    reserved, kind, count = struct.unpack_from("<HHH", raw, 0)
    return reserved == 0 and kind in (1, 2) and 0 < count < 256


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


def _bmp_to_png(raw: bytes) -> bytes:
    if len(raw) < 54 or raw[:2] != b"BM":
        raise DiagramError("Icon file is not a BMP")
    pixel_at = struct.unpack_from("<I", raw, 10)[0]
    return _dib_to_png(raw[14:], pixel_at - 14, ico=False)


def _ico_to_png(raw: bytes) -> bytes:
    if not _looks_ico(raw):
        raise DiagramError("Icon file is not an ICO")
    _reserved, _kind, count = struct.unpack_from("<HHH", raw, 0)
    best: bytes | None = None
    best_area = -1
    for index in range(count):
        entry = 6 + index * 16
        if entry + 16 > len(raw):
            break
        width, height, _colors, _res, _planes, _bits, size, offset = struct.unpack_from("<BBBBHHII", raw, entry)
        area = (width or 256) * (height or 256)
        chunk = raw[offset : offset + size]
        if area > best_area and chunk:
            best = chunk
            best_area = area
    if not best:
        raise DiagramError("Icon file has no picture")
    if best.startswith(b"\x89PNG\r\n\x1a\n"):
        return best
    return _dib_to_png(best, None, ico=True)


def _dib_to_png(dib: bytes, pixel_at: int | None, *, ico: bool) -> bytes:
    if len(dib) < 40:
        raise DiagramError("This bitmap is too small to use as an icon")
    header = struct.unpack_from("<I", dib, 0)[0]
    if header < 40 or header > len(dib):
        raise DiagramError("This bitmap header is not supported")
    width, height = struct.unpack_from("<ii", dib, 4)
    _planes, bits = struct.unpack_from("<HH", dib, 12)
    compression = struct.unpack_from("<I", dib, 16)[0]
    colors = struct.unpack_from("<I", dib, 32)[0]
    if width <= 0 or width > 4096 or bits not in (1, 4, 8, 24, 32):
        raise DiagramError("This bitmap is not supported as an icon")
    if compression not in (0, 3):
        raise DiagramError("This bitmap compression is not supported")
    top_down = height < 0
    height = abs(height)
    if ico and not top_down:
        height //= 2
    if height <= 0 or height > 4096:
        raise DiagramError("This bitmap is not supported as an icon")
    if bits <= 8 and colors == 0:
        colors = 1 << bits
    if bits > 8:
        colors = 0
    palette_at = header
    if compression == 3 and header == 40:
        palette_at = 40 + 12
    palette = []
    for index in range(colors):
        start = palette_at + index * 4
        blue, green, red = dib[start], dib[start + 1], dib[start + 2]
        palette.append((red, green, blue, 255))
    if pixel_at is None:
        pixel_at = palette_at + colors * 4
    stride = ((width * bits + 31) // 32) * 4
    rows: list[bytearray] = []
    for row in range(height):
        source = row if top_down else height - 1 - row
        start = pixel_at + source * stride
        rows.append(_pixels(dib[start : start + stride], width, bits, palette))
    if ico and bits < 32:
        mask_stride = ((width + 31) // 32) * 4
        mask_at = pixel_at + height * stride
        for row, pixels in enumerate(rows):
            source = row if top_down else height - 1 - row
            mask = dib[mask_at + source * mask_stride :]
            for column in range(width):
                if column // 8 >= len(mask):
                    break
                if (mask[column // 8] >> (7 - (column % 8))) & 1:
                    pixels[column * 4 + 3] = 0
    if bits == 32 and all(pixel[3] == 0 for row in rows for pixel in _groups(row)):
        for row in rows:
            for column in range(width):
                row[column * 4 + 3] = 255
    raw = b"".join(rows)
    return _png(width, height, raw)


def _groups(row: bytearray):
    for index in range(0, len(row), 4):
        yield row[index : index + 4]


def _pixels(row: bytes, width: int, bits: int, palette: list[tuple[int, int, int, int]]) -> bytearray:
    out = bytearray()
    for column in range(width):
        if bits == 32:
            start = column * 4
            blue, green, red, alpha = row[start : start + 4]
            out += bytes((red, green, blue, alpha))
        elif bits == 24:
            start = column * 3
            blue, green, red = row[start : start + 3]
            out += bytes((red, green, blue, 255))
        elif bits == 8:
            out += bytes(palette[row[column]])
        elif bits == 4:
            packed = row[column // 2]
            index = packed >> 4 if column % 2 == 0 else packed & 0x0F
            out += bytes(palette[index])
        else:
            index = (row[column // 8] >> (7 - (column % 8))) & 1
            out += bytes(palette[index])
    return out


def _png(width: int, height: int, rgba: bytes) -> bytes:
    raw = bytearray()
    stride = width * 4
    for row in range(height):
        raw.append(0)
        raw += rgba[row * stride : (row + 1) * stride]

    def chunk(tag: bytes, payload: bytes) -> bytes:
        body = tag + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
