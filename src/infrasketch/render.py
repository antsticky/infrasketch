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
    _assign_node_ids(diagram)
    foldable = _foldable_groups(diagram)
    if foldable:
        return _render_foldable(diagram, foldable)
    diagram.badge_prefix = ""
    layout_diagram(diagram)
    route_diagram(diagram)
    note = footnote(diagram)
    width, height = _canvas_size(diagram, note)
    ids = _Ids()
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg"{_link_ns(diagram)} width="{width:.0f}" height="{height:.0f}" '
            f'viewBox="0 0 {width:.1f} {height:.1f}" role="img" text-rendering="optimizeLegibility">'
        ),
        f"<title>{escape(diagram.title)}</title>",
        f"<desc>{escape(_description(diagram, note))}</desc>",
        f'<rect width="100%" height="100%" fill="{CANVAS}"/>',
        "<defs>",
    ]
    colors = sorted({edge.color or EDGE for edge in diagram.edges})
    for color in colors:
        parts.append(_marker(color))
    parts.append(_interaction_style(diagram))
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


def _link_ns(diagram: Diagram) -> str:
    linked = any(getattr(node, "href", "") for node in _nodes(diagram))
    numbered = any(edge.number for edge in diagram.edges)
    if linked or numbered:
        return ' xmlns:xlink="http://www.w3.org/1999/xlink"'
    return ""


def _assign_node_ids(diagram: Diagram) -> None:
    for index, node in enumerate(_nodes(diagram), start=1):
        node.sketch_id = f"n{index}"


def _render_foldable(diagram: Diagram, foldable: list[Group]) -> str:
    """One drawing per open/closed combination, switched by a click on the title."""
    note = footnote(diagram)
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
        diagram.badge_prefix = f"v{mask}-"
        layout_diagram(diagram)
        route_diagram(diagram)
        sizes.append(_canvas_size(diagram, note))
        scenes.append(_scene(diagram, ids))
    for group, folded in zip(foldable, saved):
        group.folded = folded
    width = max(size[0] for size in sizes)
    height = max(size[1] for size in sizes)
    folds = " ".join(group.fold_id for group in foldable)
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg"{_link_ns(diagram)} width="{width:.0f}" height="{height:.0f}" '
            f'viewBox="0 0 {width:.1f} {height:.1f}" data-folds="{folds}" role="img" '
            f'text-rendering="optimizeLegibility">'
        ),
        f"<title>{escape(diagram.title)}</title>",
        f"<desc>{escape(_description(diagram, note))}</desc>",
        f'<rect width="100%" height="100%" fill="{CANVAS}"/>',
        "<defs>",
    ]
    for color in sorted({edge.color or EDGE for edge in diagram.edges}):
        parts.append(_marker(color))
    parts.append(_interaction_style(diagram))
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
    hit = group.h if group.folded else group.header_h
    action = "Close" if not group.folded else "Open"
    label = escape(group.label, {'"': "&quot;"})
    radius = BOUNDARIES[group.kind]["radius"]
    x, y, w = group.abs_x, group.abs_y, group.w
    return (
        f'<g class="isk-fold" tabindex="0" role="button" data-fold="{group.fold_id}" '
        f'aria-label="{action} {label}" '
        f'onfocus="this.classList.add(\'isk-focused\')" onblur="this.classList.remove(\'isk-focused\')" '
        f'onclick="infrasketchFold(\'{group.fold_id}\', this.ownerSVGElement)" '
        f'onkeydown="infrasketchFoldKey(event, \'{group.fold_id}\', this.ownerSVGElement)">'
        f'<rect class="isk-fold-hit" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{hit:.1f}" '
        f'fill="transparent"><title>{action}</title></rect>'
        f'<rect class="isk-fold-ring" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{group.h:.1f}" '
        f'rx="{radius}" ry="{radius}" fill="none" stroke="transparent" pointer-events="none"/>'
        f"</g>"
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
  var shown = null;
  for (var j = 0; j < views.length; j++) {
    var on = Number(views[j].getAttribute("data-fold-view")) === next;
    views[j].style.display = on ? "" : "none";
    if (on) shown = views[j];
  }
  if (!shown) return;
  var focused = svg.querySelectorAll(".isk-focused");
  for (var p = 0; p < focused.length; p++) focused[p].classList.remove("isk-focused");
  var controls = shown.querySelectorAll("[data-fold]");
  for (var k = 0; k < controls.length; k++) {
    if (controls[k].getAttribute("data-fold") === id) {
      controls[k].classList.add("isk-focused");
      controls[k].focus();
      return;
    }
  }
}
function infrasketchFoldKey(event, id, svg) {
  if (event.key !== "Enter" && event.key !== " ") return;
  event.preventDefault();
  infrasketchFold(id, svg);
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
    date_w = text_width(f"as of {diagram.as_of}", 11) + PAGE_X * 2 if diagram.as_of else 0.0
    content_right = diagram.origin[0] + diagram.content_w
    content_bottom = diagram.origin[1] + diagram.content_h
    legend = _legend_entries(diagram)
    legend_w = 0.0
    legend_h = 0.0
    if legend:
        legend_w = max(text_width(f"{number}   {label}", 12) for number, label in legend) + PAGE_X * 2 + 28
        legend_h = 16.0 + len(legend) * 18.0
    width = max(content_right + PAGE_X, title_w, sub_w, note_w, date_w, legend_w, 320)
    extra = 16.0 if diagram.as_of else 0.0
    height = max(content_bottom + legend_h + FOOTER + 12 + extra, 120)
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
            f'<text x="{x + w / 2:.1f}" y="{y + h - 12:.1f}" '
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
    wrapped = body
    if node.href:
        href = escape(node.href, {'"': "&quot;"})
        tip = escape(node.note or node.label)
        wrapped = f'<a href="{href}" xlink:href="{href}" target="_blank"><title>{tip}</title>{body}</a>'
    return f'<g class="isk-item" data-node="{node.sketch_id}">{wrapped}</g>'


def _edge_path(edge: Connection) -> str:
    if len(edge.points) < 2:
        return ""
    color = edge.color or EDGE
    marker = "arrow-" + color.replace("#", "")
    start = ' marker-start="url(#{0})"'.format(marker) if edge.direction in {"back", "both"} else ""
    end = ' marker-end="url(#{0})"'.format(marker) if edge.direction in {"forward", "both"} else ""
    dash = {"dashed": ' stroke-dasharray="6 4"', "dotted": ' stroke-dasharray="1.4 4"'}.get(edge.style, "")
    touch = _touch(edge)
    linked = f' data-touch="{touch}"' if touch else ""
    return (
        f'<path class="isk-item"{linked} d="{_polyline(edge.points)}" fill="none" stroke="{color}" stroke-width="1.6" '
        f'stroke-linecap="butt" stroke-linejoin="miter"{dash}{start}{end}/>'
    )


def _edge_labels(diagram: Diagram) -> str:
    _mark_badges(diagram)
    labels = []
    occupied = [(node.abs_x, node.abs_y, node.w, node.h) for node in _nodes(diagram)]
    for edge in diagram.edges:
        if len(edge.points) < 2 or not (edge.label or edge.number):
            continue
        start, end = _own_line(edge, diagram.edges)
        if edge.number:
            labels.append(_item(edge, _number_badge(edge, start, end, occupied)))
            continue
        if not edge.label:
            continue
        width = text_width(edge.label, 11) + 14
        height = 18
        box = _on_line(start, end, width, height, occupied)
        occupied.append(box)
        labels.append(
            _item(
                edge,
                f'<rect x="{box[0]:.1f}" y="{box[1]:.1f}" width="{box[2]:.1f}" height="{box[3]:.1f}" rx="9" '
                f'fill="#FFFFFF" stroke="{LINE}"/>'
                f'<text x="{box[0] + box[2] / 2:.1f}" y="{box[1] + 12.5:.1f}" text-anchor="middle" '
                f'fill="{INK}" font-family="{FONT_ATTR}" font-size="11">{escape(edge.label)}</text>',
            )
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
        target = _badge_target(diagram, number, label)
        row = (
            f'<circle cx="{PAGE_X + 8:.1f}" cy="{y - 3:.1f}" r="8" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.2"/>'
            f'<text x="{PAGE_X + 8:.1f}" y="{y:.1f}" text-anchor="middle" fill="{INK}" '
            f'font-family="{FONT_ATTR}" font-size="11" font-weight="600">{number}</text>'
            f'<text x="{PAGE_X + 24:.1f}" y="{y:.1f}" fill="{INK}" font-family="{FONT_ATTR}" font-size="12">'
            f"{escape(label)}</text>"
        )
        if not target:
            lines.append(row)
            continue
        width = 28 + text_width(label, 12)
        lines.append(
            f'<a class="isk-legend" href="#{target}" xlink:href="#{target}" '
            f'onfocus="this.classList.add(\'isk-focused\')" onblur="this.classList.remove(\'isk-focused\')">'
            f'<rect class="isk-legend-ring" x="{PAGE_X - 6:.1f}" y="{y - 15:.1f}" width="{width:.1f}" height="20" '
            f'rx="10" fill="none" stroke="transparent"/>'
            f"{row}</a>"
        )
    return "".join(lines)


def _interaction_style(diagram: Diagram) -> str:
    rules = [
        ".isk-item{transition:opacity 140ms ease}",
        "svg:has([data-node]:hover) .isk-item{opacity:.22}",
    ]
    for node in _nodes(diagram):
        ident = node.sketch_id
        rules.append(
            f'svg:has([data-node="{ident}"]:hover) .isk-item[data-node="{ident}"]'
            f',svg:has([data-node="{ident}"]:hover) .isk-item[data-touch~="{ident}"]{{opacity:1}}'
        )
    rules.extend(
        [
            ".isk-fold{outline:none;cursor:pointer}",
            ".isk-fold.isk-focused .isk-fold-ring,.isk-fold:focus .isk-fold-ring,.isk-fold:focus-visible .isk-fold-ring{stroke:#0078D4;stroke-width:2}",
            ".isk-legend{cursor:pointer}",
            ".isk-legend.isk-focused .isk-legend-ring,.isk-legend:focus .isk-legend-ring,.isk-legend:focus-visible .isk-legend-ring{stroke:#0078D4;stroke-width:1.6}",
            ".isk-badge:target{filter:drop-shadow(0 0 2.5px #0078D4)}",
        ]
    )
    return "<style>" + "".join(rules) + "</style>"


def _touch(edge: Connection) -> str:
    found = []
    for end in (edge.source, edge.target):
        ident = getattr(end, "sketch_id", "")
        if ident and ident not in found:
            found.append(ident)
    return " ".join(found)


def _mark_badges(diagram: Diagram) -> None:
    prefix = getattr(diagram, "badge_prefix", "") or ""
    seen: dict[tuple[int, str], str] = {}
    for edge in diagram.edges:
        edge.badge_id = ""
        if edge.number is None or len(edge.points) < 2:
            continue
        key = (edge.number, edge.label)
        if key in seen:
            continue
        seen[key] = f"{prefix}step-{edge.number}-{len(seen) + 1}"
        edge.badge_id = seen[key]


def _badge_target(diagram: Diagram, number: int, label: str) -> str:
    for edge in diagram.edges:
        if edge.number == number and edge.label == label and getattr(edge, "badge_id", ""):
            return edge.badge_id
    return ""


def _item(edge: Connection, inner: str) -> str:
    touch = _touch(edge)
    linked = f' data-touch="{touch}"' if touch else ""
    if edge.badge_id:
        return f'<g class="isk-item isk-badge" id="{edge.badge_id}"{linked}>{inner}</g>'
    return f'<g class="isk-item"{linked}>{inner}</g>'


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


def _description(diagram: Diagram, note: str) -> str:
    text = f"{diagram.subtitle or diagram.title}. {note}"
    if diagram.as_of:
        text = f"{text}. As of {diagram.as_of}"
    return text


def _footer(diagram: Diagram, width: float, height: float, note: str) -> str:
    def line(y: float, text: str) -> str:
        return (
            f'<text x="{PAGE_X}" y="{y:.1f}" fill="#94A3B8" font-family="{FONT_ATTR}" font-size="11">'
            f"{escape(text)}</text>"
        )

    if not diagram.as_of:
        return line(height - 12, note)
    return line(height - 28, note) + line(height - 12, f"as of {diagram.as_of}")


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


def _own_line(edge: Connection, edges: list[Connection]) -> tuple[tuple[float, float], tuple[float, float]]:
    """Middle of the run that belongs to this arrow, once a shared stretch is removed."""
    best = None
    best_len = 0.0
    for start, end in _runs(edge.points):
        for left, right in _without_meet(start, end, edge, edges):
            length = abs(right[0] - left[0]) + abs(right[1] - left[1])
            if length > best_len:
                best = (left, right)
                best_len = length
    if best is not None and best_len >= 12.0:
        return best
    return _longest(edge.points)


def _without_meet(start, end, edge: Connection, edges: list[Connection]):
    """Pieces of one run that no other arrow travels along."""
    x1, y1 = start
    x2, y2 = end
    horizontal = abs(y1 - y2) <= 1.0
    vertical = abs(x1 - x2) <= 1.0
    if horizontal == vertical:
        return [(start, end)]
    if horizontal:
        origin, a, b = y1, x1, x2
    else:
        origin, a, b = x1, y1, y2
    lo, hi = (a, b) if a <= b else (b, a)
    blocked: list[tuple[float, float]] = []
    for other in edges:
        if other is edge:
            continue
        for left, right in _runs(other.points):
            if horizontal:
                if abs(left[1] - right[1]) > 1.0 or abs(left[1] - origin) > 1.0 or abs(right[1] - origin) > 1.0:
                    continue
                span = sorted((left[0], right[0]))
            else:
                if abs(left[0] - right[0]) > 1.0 or abs(left[0] - origin) > 1.0 or abs(right[0] - origin) > 1.0:
                    continue
                span = sorted((left[1], right[1]))
            cover_lo = max(lo, span[0])
            cover_hi = min(hi, span[1])
            if cover_hi - cover_lo > 2.0:
                blocked.append((cover_lo, cover_hi))
    if not blocked:
        return [(start, end)]
    blocked.sort()
    merged = [blocked[0]]
    for cover_lo, cover_hi in blocked[1:]:
        if cover_lo <= merged[-1][1] + 0.5:
            merged[-1] = (merged[-1][0], max(merged[-1][1], cover_hi))
        else:
            merged.append((cover_lo, cover_hi))
    free: list[tuple[float, float]] = []
    cursor = lo
    for cover_lo, cover_hi in merged:
        if cover_lo - cursor > 0.6:
            free.append((cursor, cover_lo))
        cursor = max(cursor, cover_hi)
    if hi - cursor > 0.6:
        free.append((cursor, hi))
    pieces = []
    for left, right in free:
        if horizontal:
            pieces.append(((left, origin), (right, origin)))
        else:
            pieces.append(((origin, left), (origin, right)))
    return pieces


def _runs(points: list[tuple[float, float]]):
    return [
        (start, end)
        for start, end in zip(points, points[1:])
        if abs(end[0] - start[0]) >= 0.6 or abs(end[1] - start[1]) >= 0.6
    ]


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
