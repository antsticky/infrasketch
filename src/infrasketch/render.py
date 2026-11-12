"""Render a laid-out diagram to a self-contained SVG document."""

from __future__ import annotations

from xml.sax.saxutils import escape

from infrasketch.icons import embed_icon
from infrasketch.layout import LABEL_LEADING, LABEL_SIZE, layout_diagram, text_width
from infrasketch.model import Connection, Diagram, DiagramError, Group, Node, inside_folded
from infrasketch.route import route_diagram
from infrasketch.theme import BOUNDARIES, CANVAS, EDGE, FONT_ATTR, FOOTER, INK, LINE, MUTED, PAGE_X

def footnote(diagram: Diagram) -> str:
    """Credit the icon sets that actually appear on this diagram."""
    paths: list[str] = []
    for element in diagram.walk():
        icon = getattr(element, "icon", None)
        if isinstance(element, Group):
            icon = BOUNDARIES.get(element.kind, {}).get("icon") or icon
        if icon:
            paths.append(icon)
    notes = []
    if any(path.startswith("azure/") for path in paths):
        notes.append("Azure icons © Microsoft")
    if any(path.startswith("aws/") for path in paths):
        notes.append("AWS icons © Amazon Web Services")
    for spec, credit in (
        ("external/github.svg", "GitHub mark © GitHub"),
        ("external/cloudflare.svg", "Cloudflare mark © Cloudflare"),
        ("external/akamai.svg", "Akamai mark © Akamai"),
    ):
        if spec in paths:
            notes.append(credit)
    if not notes:
        return "Architecture diagram"
    return " · ".join(notes) + " · for architecture diagrams"


def render_svg(diagram: Diagram) -> str:
    foldable = _foldable_groups(diagram)
    if foldable:
        return _render_foldable(diagram, foldable)
    layout_diagram(diagram)
    route_diagram(diagram)
    note = footnote(diagram)
    if diagram.as_of:
        note = f"{note} · as of {diagram.as_of}"
    width, height = _canvas_size(diagram, note)
    ids = _Ids()
    link_ns = ""
    if any(getattr(node, "href", "") for node in _nodes(diagram)):
        link_ns = ' xmlns:xlink="http://www.w3.org/1999/xlink"'
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg"{link_ns} width="{width:.0f}" height="{height:.0f}" '
            f'viewBox="0 0 {width:.1f} {height:.1f}" role="img" text-rendering="optimizeLegibility">'
        ),
        f"<title>{escape(diagram.title)}</title>",
        f"<desc>{escape(diagram.subtitle or diagram.title)}. {escape(note)}</desc>",
        f'<rect width="100%" height="100%" fill="{CANVAS}"/>',
        "<defs>",
    ]
    colors = sorted({edge.color or EDGE for edge in diagram.edges})
    for color in colors:
        parts.append(_marker(color))
    for group in _groups(diagram):
        if inside_folded(group):
            continue
        clip = ids.next("clip")
        group.clip_id = clip
        parts.append(
            f'<clipPath id="{clip}"><rect x="{group.abs_x:.1f}" y="{group.abs_y:.1f}" '
            f'width="{group.w:.1f}" height="{group.h:.1f}" rx="{BOUNDARIES[group.kind]["radius"]}"/></clipPath>'
        )
    parts.append("</defs>")
    for group in _groups(diagram):
        if inside_folded(group):
            continue
        parts.append(_group_body(group))
    for edge in diagram.edges:
        parts.append(_edge_path(edge))
    for group in _groups(diagram):
        if inside_folded(group):
            continue
        parts.append(_group_header(group, ids))
    for node in _nodes(diagram):
        if inside_folded(node):
            continue
        parts.append(_node(node, ids))
    parts.append(_edge_labels(diagram))
    parts.append(_legend(diagram))
    parts.append(_title(diagram))
    parts.append(_footer(diagram, width, height, note))
    parts.append("</svg>")
    return "\n".join(part for part in parts if part)


def _foldable_groups(diagram: Diagram) -> list[Group]:
    found = []
    for group in _groups(diagram):
        if not getattr(group, "foldable", False):
            continue
        parent = group.parent
        hidden = False
        while isinstance(parent, Group):
            if parent.folded and not parent.foldable:
                hidden = True
                break
            parent = parent.parent
        if not hidden:
            found.append(group)
    if len(found) > 4:
        raise DiagramError("A diagram can have at most 4 foldable groups")
    return found


def _render_foldable(diagram: Diagram, foldable: list[Group]) -> str:
    """One drawing per open/closed combination, switched by a click on the title."""
    note = footnote(diagram)
    if diagram.as_of:
        note = f"{note} · as of {diagram.as_of}"
    saved = [group.folded for group in foldable]
    for index, group in enumerate(foldable):
        group.fold_id = f"f{index}"
    initial = 0
    for index, folded in enumerate(saved):
        if folded:
            initial |= 1 << index
    ids = _Ids()
    scenes: list[tuple[str, str]] = []
    sizes: list[tuple[float, float]] = []
    for mask in range(1 << len(foldable)):
        for index, group in enumerate(foldable):
            group.folded = bool(mask & (1 << index))
        layout_diagram(diagram)
        route_diagram(diagram)
        sizes.append(_canvas_size(diagram, note))
        scenes.append(_scene(diagram, ids))
    for group, folded in zip(foldable, saved):
        group.folded = folded
    width = max(size[0] for size in sizes)
    height = max(size[1] for size in sizes)
    link_ns = ""
    if any(getattr(node, "href", "") for node in _nodes(diagram)):
        link_ns = ' xmlns:xlink="http://www.w3.org/1999/xlink"'
    folds = " ".join(group.fold_id for group in foldable)
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg"{link_ns} width="{width:.0f}" height="{height:.0f}" '
            f'viewBox="0 0 {width:.1f} {height:.1f}" data-folds="{folds}" role="img" '
            f'text-rendering="optimizeLegibility">'
        ),
        f"<title>{escape(diagram.title)}</title>",
        f"<desc>{escape(diagram.subtitle or diagram.title)}. {escape(note)}</desc>",
        f'<rect width="100%" height="100%" fill="{CANVAS}"/>',
        "<defs>",
    ]
    for color in sorted({edge.color or EDGE for edge in diagram.edges}):
        parts.append(_marker(color))
    for clips, _body in scenes:
        parts.append(clips)
    parts.append("</defs>")
    for mask, (_clips, body) in enumerate(scenes):
        hidden = "" if mask == initial else ' style="display:none"'
        parts.append(f'<g data-fold-view="{mask}"{hidden}>{body}</g>')
    parts.append(_title(diagram))
    parts.append(_footer(diagram, width, height, note))
    parts.append(_fold_script())
    parts.append("</svg>")
    layout_diagram(diagram)
    route_diagram(diagram)
    return "\n".join(part for part in parts if part)


def _scene(diagram: Diagram, ids: _Ids) -> tuple[str, str]:
    clips = []
    for group in _groups(diagram):
        if inside_folded(group):
            continue
        clip = ids.next("clip")
        group.clip_id = clip
        clips.append(
            f'<clipPath id="{clip}"><rect x="{group.abs_x:.1f}" y="{group.abs_y:.1f}" '
            f'width="{group.w:.1f}" height="{group.h:.1f}" rx="{BOUNDARIES[group.kind]["radius"]}"/></clipPath>'
        )
    parts = []
    for group in _groups(diagram):
        if inside_folded(group):
            continue
        parts.append(_group_body(group))
    for edge in diagram.edges:
        parts.append(_edge_path(edge))
    for group in _groups(diagram):
        if inside_folded(group):
            continue
        parts.append(_group_header(group, ids))
    for node in _nodes(diagram):
        if inside_folded(node):
            continue
        parts.append(_node(node, ids))
    for group in _groups(diagram):
        if group.foldable and not inside_folded(group):
            parts.append(_fold_toggle(group))
    parts.append(_edge_labels(diagram))
    parts.append(_legend(diagram))
    return "".join(clips), "".join(part for part in parts if part)


def _fold_toggle(group: Group) -> str:
    height = group.h if group.folded else group.header_h
    action = "Close" if not group.folded else "Open"
    return (
        f'<rect x="{group.abs_x:.1f}" y="{group.abs_y:.1f}" width="{group.w:.1f}" height="{height:.1f}" '
        f'fill="transparent" style="cursor:pointer" '
        f'onclick="infrasketchFold(\'{group.fold_id}\', this.ownerSVGElement)">'
        f"<title>{action}</title></rect>"
    )


def _fold_script() -> str:
    return """<script><![CDATA[
function infrasketchFold(id, svg) {
  var order = svg.getAttribute("data-folds").split(" ");
  var index = order.indexOf(id);
  if (index < 0) return;
  var views = svg.querySelectorAll("[data-fold-view]");
  var current = 0;
  for (var i = 0; i < views.length; i++) {
    if (views[i].style.display !== "none") current = Number(views[i].getAttribute("data-fold-view"));
  }
  var next = current ^ (1 << index);
  for (var j = 0; j < views.length; j++) {
    views[j].style.display = Number(views[j].getAttribute("data-fold-view")) === next ? "" : "none";
  }
}
]]></script>"""


class _Ids:
    def __init__(self) -> None:
        self.number = 0

    def next(self, prefix: str) -> str:
        self.number += 1
        return f"{prefix}{self.number}"


def _canvas_size(diagram: Diagram, note: str) -> tuple[float, float]:
    title_w = text_width(diagram.title, 22) + PAGE_X * 2
    sub_w = text_width(diagram.subtitle, 13) + PAGE_X * 2 if diagram.subtitle else 0
    note_w = text_width(note, 11) + PAGE_X * 2
    content_right = diagram.origin[0] + diagram.content_w
    content_bottom = diagram.origin[1] + diagram.content_h
    legend = _legend_entries(diagram)
    legend_w = 0.0
    legend_h = 0.0
    if legend:
        legend_w = max(text_width(f"{number}   {label}", 12) for number, label in legend) + PAGE_X * 2 + 28
        legend_h = 16.0 + len(legend) * 18.0
    width = max(content_right + PAGE_X, title_w, sub_w, note_w, legend_w, 320)
    height = max(content_bottom + legend_h + FOOTER + 12, 120)
    return width, height


def _groups(diagram: Diagram):
    for element in diagram.walk():
        if isinstance(element, Group):
            yield element


def _nodes(diagram: Diagram):
    for element in diagram.walk():
        if isinstance(element, Node):
            yield element


def _marker(color: str) -> str:
    marker_id = "arrow-" + color.replace("#", "")
    return (
        f'<marker id="{marker_id}" viewBox="0 0 10 10" refX="8.6" refY="5" '
        f'markerWidth="8" markerHeight="8" orient="auto-start-reverse" markerUnits="userSpaceOnUse">'
        f'<path d="M0.8 1.15 L8.6 5 L0.8 8.85 Z" fill="{color}"/></marker>'
    )


def _group_body(group: Group) -> str:
    style = BOUNDARIES[group.kind]
    dash = f' stroke-dasharray="{style["dash"]}"' if style["dash"] else ""
    x, y, w, h = group.abs_x, group.abs_y, group.w, group.h
    radius = style["radius"]
    caption = ""
    if group.folded and group.fold_caption:
        caption = (
            f'<text x="{x + w / 2:.1f}" y="{y + group.header_h + (h - group.header_h) / 2 + 4:.1f}" '
            f'text-anchor="middle" fill="{MUTED}" font-family="{FONT_ATTR}" font-size="11">'
            f"{escape(group.fold_caption)}</text>"
        )
    return (
        f'<g clip-path="url(#{group.clip_id})">'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{style["fill"]}"/>'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{group.header_h:.1f}" fill="{style["header"]}"/>'
        f"</g>"
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}" ry="{radius}" '
        f'fill="none" stroke="{style["stroke"]}" stroke-width="{style["stroke_width"]}"{dash}/>'
        f'<line x1="{x + 1:.1f}" y1="{y + group.header_h:.1f}" x2="{x + w - 1:.1f}" y2="{y + group.header_h:.1f}" '
        f'stroke="{LINE}" stroke-width="1"/>'
        f"{caption}"
    )


def _group_header(group: Group, ids: _Ids) -> str:
    style = BOUNDARIES[group.kind]
    header = group.header
    x = group.abs_x + 14
    y = group.abs_y
    text_x = x
    chunks = [
        (
            f'<g clip-path="url(#{group.clip_id})"><rect x="{group.abs_x + 1:.1f}" '
            f'y="{group.abs_y + 1:.1f}" width="{group.w - 2:.1f}" height="{group.header_h - 1:.1f}" '
            f'fill="{style["header"]}"/></g>'
        )
    ]
    if style["icon"]:
        icon_y = y + (group.header_h - 20) / 2
        chunks.append(embed_icon(style["icon"], ids.next("g"), x, icon_y, 20))
        text_x = x + 28
    if header.get("detail_lines") or header.get("note_lines"):
        cursor = y + (14 if header["eyebrow"] else 18)
    else:
        cursor = y + (14 if header["eyebrow"] else (group.header_h - len(header["title_lines"]) * 16) / 2 + 12)
    if header["eyebrow"]:
        chunks.append(
            f'<text x="{text_x:.1f}" y="{cursor:.1f}" fill="{style["accent"]}" '
            f'font-family="{FONT_ATTR}" font-size="10" font-weight="600" letter-spacing="0.08em">'
            f"{escape(header['eyebrow'])}</text>"
        )
        cursor += 16
    for line in header["title_lines"]:
        chunks.append(
            f'<text x="{text_x:.1f}" y="{cursor:.1f}" fill="{INK}" font-family="{FONT_ATTR}" '
            f'font-size="13.5" font-weight="600">{escape(line)}</text>'
        )
        cursor += 16
    for line in header.get("detail_lines", []):
        chunks.append(
            f'<text x="{text_x:.1f}" y="{cursor:.1f}" fill="{MUTED}" font-family="{FONT_ATTR}" '
            f'font-size="11">{escape(line)}</text>'
        )
        cursor += 14
    for line in header.get("note_lines", []):
        chunks.append(
            f'<text x="{text_x:.1f}" y="{cursor:.1f}" fill="#475569" font-family="{FONT_ATTR}" '
            f'font-size="11">{escape(line)}</text>'
        )
        cursor += 14
    return "".join(chunks)


def _node(node: Node, ids: _Ids) -> str:
    ix, iy, iw, ih = node.icon_box
    x = node.abs_x + ix
    y = node.abs_y + iy
    chunks = []
    if node.icon:
        chunks.append(embed_icon(node.icon, ids.next("n"), x, y, iw))
    else:
        chunks.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{iw:.1f}" height="{ih:.1f}" rx="12" '
            f'fill="#F1F5F9" stroke="#CBD5E1"/>'
            f'<text x="{x + iw / 2:.1f}" y="{y + ih / 2 + 5:.1f}" text-anchor="middle" '
            f'font-family="{FONT_ATTR}" font-size="16" font-weight="600" fill="#475569">'
            f"{escape(_initials(node.label))}</text>"
        )
    center = node.abs_x + node.w / 2
    cursor = y + ih + 8 + 12
    for line in node.label_lines:
        chunks.append(
            f'<text x="{center:.1f}" y="{cursor:.1f}" text-anchor="middle" fill="{INK}" '
            f'font-family="{FONT_ATTR}" font-size="{LABEL_SIZE:.0f}" font-weight="600">{escape(line)}</text>'
        )
        cursor += LABEL_LEADING
    if node.caption_lines:
        cursor += 1
        for line in node.caption_lines:
            chunks.append(
                f'<text x="{center:.1f}" y="{cursor:.1f}" text-anchor="middle" fill="{MUTED}" '
                f'font-family="{FONT_ATTR}" font-size="11">{escape(line)}</text>'
            )
            cursor += 14
    for line in node.detail_lines:
        chunks.append(
            f'<text x="{center:.1f}" y="{cursor:.1f}" text-anchor="middle" fill="{MUTED}" '
            f'font-family="{FONT_ATTR}" font-size="11">{escape(line)}</text>'
        )
        cursor += 14
    if node.note_lines:
        cursor += 1
    for line in node.note_lines:
        chunks.append(
            f'<text x="{center:.1f}" y="{cursor:.1f}" text-anchor="middle" fill="#475569" '
            f'font-family="{FONT_ATTR}" font-size="11">{escape(line)}</text>'
        )
        cursor += 14
    body = "".join(chunks)
    if not node.href:
        return body
    href = escape(node.href, {'"': "&quot;"})
    tip = escape(node.note or node.label)
    return f'<a href="{href}" xlink:href="{href}" target="_blank"><title>{tip}</title>{body}</a>'


def _edge_path(edge: Connection) -> str:
    if len(edge.points) < 2:
        return ""
    color = edge.color or EDGE
    marker = "arrow-" + color.replace("#", "")
    start = ' marker-start="url(#{0})"'.format(marker) if edge.direction in {"back", "both"} else ""
    end = ' marker-end="url(#{0})"'.format(marker) if edge.direction in {"forward", "both"} else ""
    dash = {"dashed": ' stroke-dasharray="6 4"', "dotted": ' stroke-dasharray="1.4 4"'}.get(edge.style, "")
    return (
        f'<path d="{_polyline(edge.points)}" fill="none" stroke="{color}" stroke-width="1.6" '
        f'stroke-linecap="butt" stroke-linejoin="miter"{dash}{start}{end}/>'
    )


def _edge_labels(diagram: Diagram) -> str:
    labels = []
    occupied = [(node.abs_x, node.abs_y, node.w, node.h) for node in _nodes(diagram)]
    for edge in diagram.edges:
        if len(edge.points) < 2 or not (edge.label or edge.number):
            continue
        start, end = _longest(edge.points)
        if edge.number:
            labels.append(_number_badge(edge, start, end, occupied))
            continue
        if not edge.label:
            continue
        width = text_width(edge.label, 11) + 14
        height = 18
        box = _on_line(start, end, width, height, occupied)
        occupied.append(box)
        labels.append(
            f'<rect x="{box[0]:.1f}" y="{box[1]:.1f}" width="{box[2]:.1f}" height="{box[3]:.1f}" rx="9" '
            f'fill="#FFFFFF" stroke="{LINE}"/>'
            f'<text x="{box[0] + box[2] / 2:.1f}" y="{box[1] + 12.5:.1f}" text-anchor="middle" '
            f'fill="{INK}" font-family="{FONT_ATTR}" font-size="11">{escape(edge.label)}</text>'
        )
    return "".join(labels)


def _on_line(start, end, width: float, height: float, occupied: list) -> tuple[float, float, float, float]:
    """Keep the chip centered on the stroke. Slide along the segment to clear a resource."""
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    midpoint = _chip(x1 + dx * 0.5, y1 + dy * 0.5, width, height)
    if not any(_overlaps(midpoint, other) for other in occupied):
        return midpoint
    for step in range(1, 8):
        for sign in (1, -1):
            t = 0.5 + sign * step * 0.06
            if not 0.18 <= t <= 0.82:
                continue
            box = _chip(x1 + dx * t, y1 + dy * t, width, height)
            if not any(_overlaps(box, other) for other in occupied):
                return box
    return midpoint


def _chip(cx: float, cy: float, width: float, height: float) -> tuple[float, float, float, float]:
    return (cx - width / 2, cy - height / 2, width, height)


def _number_badge(edge: Connection, start, end, occupied: list) -> str:
    text = str(edge.number)
    size = max(16.0, text_width(text, 11) + 8)
    box = _on_line(start, end, size, size, occupied)
    occupied.append(box)
    color = edge.color or EDGE
    cx = box[0] + box[2] / 2
    cy = box[1] + box[3] / 2
    return (
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{box[2] / 2:.1f}" fill="#FFFFFF" stroke="{color}" stroke-width="1.4"/>'
        f'<text x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle" fill="{INK}" '
        f'font-family="{FONT_ATTR}" font-size="11" font-weight="600">{escape(text)}</text>'
    )


def _legend_entries(diagram: Diagram) -> list[tuple[int, str]]:
    seen: set[tuple[int, str]] = set()
    entries = []
    for edge in diagram.edges:
        if edge.number is None or len(edge.points) < 2:
            continue
        item = (edge.number, edge.label)
        if item in seen:
            continue
        seen.add(item)
        entries.append(item)
    entries.sort(key=lambda item: (item[0], item[1]))
    return entries


def _legend(diagram: Diagram) -> str:
    entries = _legend_entries(diagram)
    if not entries:
        return ""
    top = diagram.origin[1] + diagram.content_h + 22
    lines = []
    for index, (number, label) in enumerate(entries):
        y = top + index * 18
        lines.append(
            f'<circle cx="{PAGE_X + 8:.1f}" cy="{y - 3:.1f}" r="8" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.2"/>'
            f'<text x="{PAGE_X + 8:.1f}" y="{y:.1f}" text-anchor="middle" fill="{INK}" '
            f'font-family="{FONT_ATTR}" font-size="11" font-weight="600">{number}</text>'
            f'<text x="{PAGE_X + 24:.1f}" y="{y:.1f}" fill="{INK}" font-family="{FONT_ATTR}" font-size="12">'
            f"{escape(label)}</text>"
        )
    return "".join(lines)


def _title(diagram: Diagram) -> str:
    title = (
        f'<text x="{PAGE_X}" y="40" fill="{INK}" font-family="{FONT_ATTR}" font-size="22" font-weight="600">'
        f"{escape(diagram.title)}</text>"
    )
    if not diagram.subtitle:
        return title
    return title + (
        f'<text x="{PAGE_X}" y="60" fill="{MUTED}" font-family="{FONT_ATTR}" font-size="13">'
        f"{escape(diagram.subtitle)}</text>"
    )


def _footer(diagram: Diagram, width: float, height: float, note: str) -> str:
    return (
        f'<text x="{PAGE_X}" y="{height - 12:.1f}" fill="#94A3B8" font-family="{FONT_ATTR}" font-size="11">'
        f"{escape(note)}</text>"
    )


def _polyline(points: list[tuple[float, float]]) -> str:
    """Straight horizontal and vertical runs. Corners stay at 90 degrees."""
    pts = [points[0]]
    for point in points[1:]:
        if abs(point[0] - pts[-1][0]) >= 0.6 or abs(point[1] - pts[-1][1]) >= 0.6:
            pts.append(point)
    commands = [f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for x, y in pts[1:]:
        commands.append(f"L {x:.1f} {y:.1f}")
    return " ".join(commands)


def _longest(points: list[tuple[float, float]]) -> tuple[tuple[float, float], tuple[float, float]]:
    best = (points[0], points[1])
    best_len = -1.0
    for start, end in zip(points, points[1:]):
        length = abs(end[0] - start[0]) + abs(end[1] - start[1])
        if length > best_len:
            best = (start, end)
            best_len = length
    return best


def _overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]


def _initials(label: str) -> str:
    parts = [part for part in label.replace("-", " ").split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()
