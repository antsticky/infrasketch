"""Measure resources and pack them into columns or rows.

Connected resources flow along the diagram direction. Resources that share a
rank — a frontend beside its cache, for example — stack on the cross axis.
Ranks are top-aligned so titles line up the way architecture diagrams expect.
"""

from __future__ import annotations

from infrasketch.model import Diagram, Endpoint, Group, Node
from infrasketch.theme import BOUNDARIES, SPACING

ICON = 48.0
ICON_TEXT_GAP = 8.0
LABEL_SIZE = 13.0
LABEL_LEADING = 16.0
CAPTION_SIZE = 11.0
CAPTION_LEADING = 14.0
TEXT_MAX = 138.0


def layout_diagram(diagram: Diagram) -> None:
    layout_scope(diagram)
    title_h = 42.0 + (20.0 if diagram.subtitle else 0.0)
    diagram.title_block = title_h
    origin_y = 28.0 + title_h
    origin_x = 36.0

    def place(element: Endpoint, ox: float, oy: float) -> None:
        element.abs_x = ox + element.x
        element.abs_y = oy + element.y
        if isinstance(element, Group):
            for child in element.children:
                place(child, element.abs_x + element.content_x, element.abs_y + element.content_y)

    for child in diagram.children:
        place(child, origin_x, origin_y)
    diagram.origin = (origin_x, origin_y)


def layout_scope(scope: Diagram | Group) -> None:
    for child in scope.children:
        if isinstance(child, Group):
            layout_scope(child)
        else:
            measure_node(child)
    arrange = "flow"
    if isinstance(scope, Group) and scope.arrange:
        arrange = scope.arrange
    if arrange == "row":
        place_line(scope, horizontal=True)
    elif arrange == "column":
        place_line(scope, horizontal=False)
    elif arrange == "grid":
        place_grid(scope)
    else:
        place_flow(scope)
    if isinstance(scope, Group):
        apply_chrome(scope)
    else:
        scope.w = scope.content_w
        scope.h = scope.content_h
        scope.content_x = 0.0
        scope.content_y = 0.0


def measure_node(node: Node) -> None:
    node.label_lines = wrap(node.label, LABEL_SIZE, TEXT_MAX)[:3]
    node.caption_lines = wrap(node.caption, CAPTION_SIZE, TEXT_MAX)[:2] if node.caption else []
    node.detail_lines = wrap(node.facts(), CAPTION_SIZE, TEXT_MAX)[:2]
    node.note_lines = wrap(node.note, CAPTION_SIZE, TEXT_MAX)[:2]
    widths = [text_width(line, LABEL_SIZE) for line in node.label_lines]
    widths += [text_width(line, CAPTION_SIZE) for line in node.caption_lines]
    widths += [text_width(line, CAPTION_SIZE) for line in node.detail_lines]
    widths += [text_width(line, CAPTION_SIZE) for line in node.note_lines]
    text_w = max(widths) if widths else 0.0
    node.w = max(ICON + 20.0, text_w + 12.0)
    text_h = len(node.label_lines) * LABEL_LEADING
    if node.caption_lines:
        text_h += 3.0 + len(node.caption_lines) * CAPTION_LEADING
    if node.detail_lines:
        text_h += len(node.detail_lines) * CAPTION_LEADING
    if node.note_lines:
        text_h += 2.0 + len(node.note_lines) * CAPTION_LEADING
    node.h = ICON + ICON_TEXT_GAP + text_h
    node.icon_box = ((node.w - ICON) / 2.0, 0.0, ICON, ICON)


def apply_chrome(group: Group) -> None:
    style = BOUNDARIES[group.kind]
    spacing = SPACING[group.diagram.spacing]
    header = measure_header(group.label, style, detail=group.facts(), note=group.note)
    group.header = header
    group.header_h = header["height"]
    pad = spacing["pad"]
    pad_top = spacing["pad_top"]
    natural = group.content_w + pad * 2.0
    group.w = max(natural, header["width"])
    group.content_x = pad + max(0.0, (group.w - natural) / 2.0)
    group.content_y = group.header_h + pad_top
    group.h = group.content_y + group.content_h + pad


def measure_header(label: str, style: dict, detail: str = "", note: str = "") -> dict:
    title_lines = wrap(label, 13.5, 240.0)[:2] or [label]
    detail_lines = wrap(detail, 11.0, 240.0)[:2] if detail else []
    note_lines = wrap(note, 11.0, 240.0)[:2] if note else []
    title_w = max(text_width(line, 13.5) for line in title_lines)
    detail_w = max((text_width(line, 11.0) for line in detail_lines), default=0.0)
    note_w = max((text_width(line, 11.0) for line in note_lines), default=0.0)
    eyebrow = style["eyebrow"]
    eye_w = text_width(eyebrow, 10.0) * 1.18 if eyebrow else 0.0
    icon_slot = 28.0 if style["icon"] else 0.0
    width = 16.0 + icon_slot + max(title_w, eye_w, detail_w, note_w) + 18.0
    if eyebrow:
        height = 14.0 + 13.0 + len(title_lines) * 16.0 + 8.0
    else:
        height = 10.0 + len(title_lines) * 18.0 + 10.0
    extra = (len(detail_lines) + len(note_lines)) * 14.0
    if extra:
        height += extra + 2.0
    return {
        "height": height,
        "width": width,
        "title_lines": title_lines,
        "eyebrow": eyebrow,
        "detail_lines": detail_lines,
        "note_lines": note_lines,
    }


def place_flow(scope: Diagram | Group) -> None:
    children = list(scope.children)
    if not children:
        scope.content_w = 0.0
        scope.content_h = 0.0
        return
    direction = _direction(scope)
    align = _align(scope)
    spacing = SPACING[scope.diagram.spacing]
    ranks = _order_ranks(scope, children)
    rank_gap = spacing["rank"]
    item_gap = spacing["item"]

    def main_of(child: Endpoint) -> float:
        return child.w if direction == "LR" else child.h

    def cross_of(child: Endpoint) -> float:
        return child.h if direction == "LR" else child.w

    rank_main = [max(main_of(child) for child in rank) for rank in ranks]
    rank_cross = []
    for rank in ranks:
        gaps = item_gap * (len(rank) - 1)
        rank_cross.append(sum(cross_of(child) for child in rank) + gaps)
    content_main = sum(rank_main) + rank_gap * (len(ranks) - 1)
    content_cross = max(rank_cross)
    cursor = 0.0
    for rank, span, cross in zip(ranks, rank_main, rank_cross):
        cross_cursor = 0.0 if align == "top" else (content_cross - cross) / 2.0
        for child in rank:
            main_pos = cursor + (span - main_of(child)) / 2.0
            if direction == "LR":
                child.x = main_pos
                child.y = cross_cursor
            else:
                child.x = cross_cursor
                child.y = main_pos
            cross_cursor += cross_of(child) + item_gap
        cursor += span + rank_gap
    if direction == "LR":
        scope.content_w = content_main
        scope.content_h = content_cross
    else:
        scope.content_w = content_cross
        scope.content_h = content_main


def place_line(scope: Diagram | Group, *, horizontal: bool) -> None:
    children = list(scope.children)
    spacing = SPACING[scope.diagram.spacing]
    gap = spacing["rank"] if horizontal else spacing["item"]
    align = _align(scope)
    if not children:
        scope.content_w = 0.0
        scope.content_h = 0.0
        return
    if horizontal:
        height = max(child.h for child in children)
        x = 0.0
        for child in children:
            child.x = x
            child.y = 0.0 if align == "top" else (height - child.h) / 2.0
            x += child.w + gap
        scope.content_w = x - gap
        scope.content_h = height
        return
    width = max(child.w for child in children)
    y = 0.0
    for child in children:
        child.y = y
        child.x = 0.0 if align == "top" else (width - child.w) / 2.0
        y += child.h + gap
    scope.content_w = width
    scope.content_h = y - gap


def place_grid(scope: Diagram | Group) -> None:
    children = list(scope.children)
    if not children:
        scope.content_w = 0.0
        scope.content_h = 0.0
        return
    columns = scope.columns or 3
    columns = max(1, columns)
    gap = SPACING[scope.diagram.spacing]["item"]
    rows = [children[index : index + columns] for index in range(0, len(children), columns)]
    col_w = []
    for column in range(columns):
        widths = [row[column].w for row in rows if column < len(row)]
        col_w.append(max(widths) if widths else 0.0)
    row_h = [max(child.h for child in row) for row in rows]
    for row_index, row in enumerate(rows):
        for column, child in enumerate(row):
            child.x = sum(col_w[:column]) + gap * column + (col_w[column] - child.w) / 2.0
            child.y = sum(row_h[:row_index]) + gap * row_index
    scope.content_w = sum(col_w) + gap * (len(col_w) - 1)
    scope.content_h = sum(row_h) + gap * (len(row_h) - 1)


def _order_ranks(scope: Diagram | Group, children: list[Endpoint]) -> list[list[Endpoint]]:
    index = {id(child): position for position, child in enumerate(children)}
    indegree = {id(child): 0 for child in children}
    successors: dict[int, list[int]] = {id(child): [] for child in children}
    predecessors: dict[int, list[int]] = {id(child): [] for child in children}
    for edge in scope.diagram.edges:
        if edge.direction == "none":
            continue
        left = _direct_child(edge.source, scope)
        right = _direct_child(edge.target, scope)
        if left is None or right is None or left is right:
            continue
        successors[id(left)].append(id(right))
        predecessors[id(right)].append(id(left))
        indegree[id(right)] += 1

    remaining = [id(child) for child in children]
    ordered_ids: list[list[int]] = []
    while remaining:
        ready = [item for item in remaining if indegree[item] == 0]
        if not ready:
            ordered_ids.append(remaining)
            break
        ordered_ids.append(ready)
        for item in ready:
            remaining.remove(item)
            for successor in successors[item]:
                indegree[successor] -= 1

    by_id = {id(child): child for child in children}
    ranks = [[by_id[item] for item in rank] for rank in ordered_ids]
    _barycenter(ranks, predecessors, successors, index)
    return ranks


def _barycenter(
    ranks: list[list[Endpoint]],
    predecessors: dict[int, list[int]],
    successors: dict[int, list[int]],
    declaration: dict[int, int],
) -> None:
    def sort_rank(rank: list[Endpoint], neighbor_index: dict[int, int], neighbors) -> list[Endpoint]:
        def key(child: Endpoint) -> tuple[float, int]:
            refs = [neighbor_index[item] for item in neighbors(id(child)) if item in neighbor_index]
            if not refs:
                return (float(declaration[id(child)]), declaration[id(child)])
            return (sum(refs) / len(refs), declaration[id(child)])

        return sorted(rank, key=key)

    for index in range(1, len(ranks)):
        previous = {id(child): position for position, child in enumerate(ranks[index - 1])}
        ranks[index] = sort_rank(ranks[index], previous, lambda item: predecessors[item])
    for index in range(len(ranks) - 2, -1, -1):
        nxt = {id(child): position for position, child in enumerate(ranks[index + 1])}
        ranks[index] = sort_rank(ranks[index], nxt, lambda item: successors[item])


def _direct_child(element: Endpoint, scope: Diagram | Group) -> Endpoint | None:
    """Return the direct child of scope that contains element."""
    current: Endpoint | None = element
    while current is not None and current.parent is not scope:
        parent = current.parent
        if not isinstance(parent, Endpoint):
            return None
        current = parent
    if current is not None and current.parent is scope:
        return current
    return None


def _direction(scope: Diagram | Group) -> str:
    if isinstance(scope, Diagram):
        return scope.direction
    if scope.direction:
        return scope.direction
    return _direction(scope.parent)  # type: ignore[arg-type]


def _align(scope: Diagram | Group) -> str:
    if isinstance(scope, Group) and scope.align:
        return scope.align
    # Sibling boundaries of different heights sit on a shared centerline,
    # so a short subnet lines up with the middle of a taller one.
    if isinstance(scope, Group) and scope.children and all(isinstance(child, Group) for child in scope.children):
        return "center"
    if isinstance(scope, Diagram):
        return scope.align
    parent = scope.parent
    if isinstance(parent, (Diagram, Group)):
        return _align(parent)
    return "top"


def wrap(text: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if text_width(trial, size) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def text_width(text: str, size: float) -> float:
    width = 0.0
    for char in text:
        if char == " ":
            width += 0.33
        elif char in "iljI.,'`|!:;":
            width += 0.30
        elif char in "mwMW@%&":
            width += 0.96
        elif char.isupper() or char.isdigit():
            width += 0.68
        else:
            width += 0.56
    return width * size
