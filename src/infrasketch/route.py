"""Orthogonal connectors that stay in the gaps between resources.

A clear run stays straight. A turn is a real step, never a kink of a few pixels.
A connector also stays off every label, caption, and title.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from infrasketch.layout import CAPTION_SIZE, LABEL_SIZE, text_width
from infrasketch.model import Connection, Diagram, Endpoint, Group, Node
from infrasketch.theme import BOUNDARIES, PAGE_X

# Shorter than this, a perpendicular step is a kink and should disappear.
_JOG = 16.0
# When a line must turn more than once, a kept step is at least this tall.
_SQUARE = 28.0


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def top(self) -> float:
        return self.y

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2.0

    @property
    def cy(self) -> float:
        return self.y + self.h / 2.0

    def expanded(self, margin: float) -> Rect:
        return Rect(self.x - margin, self.y - margin, self.w + margin * 2, self.h + margin * 2)


def route_diagram(diagram: Diagram) -> None:
    obstacles: list[tuple[Endpoint | None, Rect]] = []
    for element in _nodes(diagram):
        if _inside_folded(element):
            continue
        obstacles.append((element, _node_obstacle(element)))
    for element in diagram.walk():
        if not isinstance(element, Group) or _inside_folded(element):
            continue
        if element.folded:
            obstacles.append((element, _node_obstacle(element)))
        else:
            # Titles stay clear. The padding under a title is a lane for connectors.
            obstacles.append((None, _header_obstacle(element)))
    for rect in _text_obstacles(diagram):
        obstacles.append((None, rect))
    _assign_lanes(diagram.edges)
    for edge in diagram.edges:
        source, target = _shown(edge.source), _shown(edge.target)
        if source is target:
            edge.points = [] if source is not edge.source else _orthogonal(_loop(source))
            continue
        edge.points = _simplify(
            _orthogonal(_route(edge, obstacles, source, target)),
            _blocked(obstacles, source, target),
            source,
            target,
            edge.lane,
        )


def _shown(element: Endpoint) -> Endpoint:
    """A folded boundary stands in for the resources it hides."""
    shown = element
    parent = element.parent
    while isinstance(parent, Group):
        if parent.folded:
            shown = parent
        parent = parent.parent
    return shown


def _inside_folded(element: Endpoint) -> bool:
    parent = element.parent
    while isinstance(parent, Group):
        if parent.folded:
            return True
        parent = parent.parent
    return False


def _nodes(diagram: Diagram):
    for element in diagram.walk():
        if isinstance(element, Node):
            yield element


def _bounds(element: Endpoint) -> Rect:
    return Rect(element.abs_x, element.abs_y, element.w, element.h)


def _node_obstacle(element: Endpoint) -> Rect:
    """Keep lines off the icon and the label, and leave a lane above the icon."""
    rect = _bounds(element)
    return Rect(rect.x - 8, rect.y - 4, rect.w + 16, rect.h + 12)


def _header_obstacle(element: Group) -> Rect:
    """Cover the title band without consuming the padding underneath it."""
    return Rect(element.abs_x - 2, element.abs_y - 2, element.w + 4, element.header_h + 4)


def _text_obstacles(diagram: Diagram) -> list[Rect]:
    """Glyph boxes. These stay blocked even for the resource a line is leaving."""
    rects: list[Rect] = []
    rects.append(_ink(PAGE_X, 40, text_width(diagram.title, 22), 22))
    if diagram.subtitle:
        rects.append(_ink(PAGE_X, 60, text_width(diagram.subtitle, 13), 13))
    for element in diagram.walk():
        if _inside_folded(element):
            continue
        if isinstance(element, Node):
            rects.extend(_node_text(element))
        elif isinstance(element, Group):
            rects.extend(_group_text(element))
    return rects


def _ink(x: float, baseline: float, width: float, size: float, *, middle: bool = False) -> Rect:
    left = x - width / 2.0 if middle else x
    top = baseline - size * 0.82
    return Rect(left - 2.0, top - 1.0, max(width, 1.0) + 4.0, size + 2.0)


def _node_text(node: Node) -> list[Rect]:
    _ix, iy, _iw, ih = node.icon_box
    center = node.abs_x + node.w / 2.0
    cursor = node.abs_y + iy + ih + 20.0
    rects = []
    batches = (
        (node.label_lines, LABEL_SIZE, 16.0, 0.0),
        (node.caption_lines, CAPTION_SIZE, 14.0, 1.0 if node.caption_lines else 0.0),
        (node.detail_lines, CAPTION_SIZE, 14.0, 0.0),
        (node.note_lines, CAPTION_SIZE, 14.0, 1.0 if node.note_lines else 0.0),
    )
    for batch, size, leading, gap in batches:
        cursor += gap
        for line in batch:
            rects.append(_ink(center, cursor, text_width(line, size), size, middle=True))
            cursor += leading
    floor = node.abs_y + node.h - 1.0
    kept = []
    for rect in rects:
        if rect.bottom > floor:
            rect = Rect(rect.x, rect.y, rect.w, max(4.0, floor - rect.y))
        kept.append(rect)
    return kept


def _group_text(group: Group) -> list[Rect]:
    header = group.header
    style = BOUNDARIES[group.kind]
    text_x = group.abs_x + 14.0 + (28.0 if style["icon"] else 0.0)
    if header.get("detail_lines") or header.get("note_lines"):
        cursor = group.abs_y + (14.0 if header["eyebrow"] else 18.0)
    else:
        cursor = group.abs_y + (
            14.0 if header["eyebrow"] else (group.header_h - len(header["title_lines"]) * 16.0) / 2.0 + 12.0
        )
    rects = []
    if header["eyebrow"]:
        label = header["eyebrow"]
        rects.append(_ink(text_x, cursor, text_width(label, 10.0) * 1.12, 10.0))
        cursor += 16.0
    for line in header["title_lines"]:
        rects.append(_ink(text_x, cursor, text_width(line, 13.5), 13.5))
        cursor += 16.0
    for line in header.get("detail_lines", []):
        rects.append(_ink(text_x, cursor, text_width(line, 11.0), 11.0))
        cursor += 14.0
    for line in header.get("note_lines", []):
        rects.append(_ink(text_x, cursor, text_width(line, 11.0), 11.0))
        cursor += 14.0
    if group.folded and group.fold_caption:
        baseline = group.abs_y + group.header_h + (group.h - group.header_h) / 2.0 + 4.0
        rects.append(
            _ink(group.abs_x + group.w / 2.0, baseline, text_width(group.fold_caption, 11.0), 11.0, middle=True)
        )
    return rects


def _icon_bounds(element: Endpoint) -> Rect:
    if isinstance(element, Node):
        x, y, width, height = element.icon_box
        return Rect(element.abs_x + x, element.abs_y + y, width, height)
    return _bounds(element)


def _ports(source: Endpoint, target: Endpoint) -> tuple[tuple[float, float], tuple[float, float], str]:
    src = _icon_bounds(source)
    dst = _icon_bounds(target)
    src_box = _bounds(source)
    dst_box = _bounds(target)
    dx = dst.cx - src.cx
    dy = dst.cy - src.cy
    if abs(dx) >= abs(dy):
        if dx >= 0:
            return (src.right, src.cy), (dst.x, dst.cy), "h"
        return (src.x, src.cy), (dst.right, dst.cy), "h"
    if dy >= 0:
        return (src.cx, src_box.bottom), (dst.cx, dst.y), "v"
    return (src.cx, src.y), (dst.cx, dst_box.bottom), "v"


def _assign_lanes(edges: list[Connection]) -> None:
    buckets: dict[tuple, list[Connection]] = defaultdict(list)
    for edge in edges:
        source, target = _shown(edge.source), _shown(edge.target)
        if source is target:
            edge.lane = 0.0
            continue
        start, end, orient = _ports(source, target)
        if orient == "h":
            key = ("h", round(start[1] / 34), round(end[1] / 34), int(end[0] >= start[0]))
        else:
            key = ("v", round(start[0] / 34), round(end[0] / 34), int(end[1] >= start[1]))
        buckets[key].append(edge)
    for items in buckets.values():
        count = len(items)
        for index, edge in enumerate(items):
            edge.lane = (index - (count - 1) / 2.0) * 18.0


def _blocked(obstacles: list[tuple[Endpoint | None, Rect]], source: Endpoint, target: Endpoint) -> list[Rect]:
    blocked = [rect for element, rect in obstacles if element is not source and element is not target]
    if isinstance(target, Group) and not target.folded:
        blocked = [rect for element, rect in obstacles if element is not source]
    if isinstance(source, Group) and not source.folded:
        blocked = [rect for element, rect in obstacles if element is not target]
    return blocked


def _kink_cost(delta: float) -> float:
    """A few pixels off the port is a kink. An aligned run, or a full step, costs nothing."""
    gap = abs(delta)
    if gap < 1.0 or gap >= _JOG:
        return 0.0
    return 48.0


def _route(
    edge: Connection,
    obstacles: list[tuple[Endpoint | None, Rect]],
    source: Endpoint | None = None,
    target: Endpoint | None = None,
) -> list[tuple[float, float]]:
    source = source or edge.source
    target = target or edge.target
    if source is target:
        return _loop(source)
    start, end, orient = _ports(source, target)
    blocked = _blocked(obstacles, source, target)
    if orient == "h":
        return _route_horizontal(start, end, edge.lane, blocked)
    return _route_vertical(start, end, edge.lane, blocked)


def _route_horizontal(start, end, lane, obstacles: list[Rect]) -> list[tuple[float, float]]:
    forward = end[0] >= start[0]
    sign = 1.0 if forward else -1.0
    leave = _approach(start, sign, 0.0, obstacles)
    arrive = _approach(end, -sign, 0.0, obstacles)
    if abs(start[1] - end[1]) < 1 and (end[0] - start[0]) * sign > 0 and _clear(start[0], start[1], end[0], end[1], obstacles):
        return [start, end]
    low, high = sorted((leave[0], arrive[0]))
    center = (leave[0] + arrive[0]) / 2.0 + (lane if forward else -lane)
    candidates = [center]
    if high - low > 8:
        cursor = low + 4
        while cursor <= high - 4:
            candidates.append(cursor)
            cursor += 6
    seen: set[float] = set()
    for candidate in candidates:
        key = round(candidate, 1)
        if key in seen:
            continue
        seen.add(key)
        if (
            _clear(leave[0], leave[1], candidate, leave[1], obstacles)
            and _clear(candidate, leave[1], candidate, arrive[1], obstacles)
            and _clear(candidate, arrive[1], arrive[0], arrive[1], obstacles)
        ):
            return _clean([start, leave, (candidate, leave[1]), (candidate, arrive[1]), arrive, end])
    return _detour_horizontal(start, end, leave, arrive, lane, obstacles)


def _route_vertical(start, end, lane, obstacles: list[Rect]) -> list[tuple[float, float]]:
    forward = end[1] >= start[1]
    sign = 1.0 if forward else -1.0
    leave = _approach(start, 0.0, sign, obstacles)
    arrive = _approach(end, 0.0, -sign, obstacles)
    if abs(start[0] - end[0]) < 1 and (end[1] - start[1]) * sign > 0 and _clear(start[0], start[1], end[0], end[1], obstacles):
        return [start, end]
    low, high = sorted((leave[1], arrive[1]))
    center = (leave[1] + arrive[1]) / 2.0 + (lane if forward else -lane)
    candidates = [center]
    if high - low > 8:
        cursor = low + 4
        while cursor <= high - 4:
            candidates.append(cursor)
            cursor += 6
    seen: set[float] = set()
    for candidate in candidates:
        key = round(candidate, 1)
        if key in seen:
            continue
        seen.add(key)
        if (
            _clear(leave[0], leave[1], leave[0], candidate, obstacles)
            and _clear(leave[0], candidate, arrive[0], candidate, obstacles)
            and _clear(arrive[0], candidate, arrive[0], arrive[1], obstacles)
        ):
            return _clean([start, leave, (leave[0], candidate), (arrive[0], candidate), arrive, end])
    return _detour_vertical(start, end, leave, arrive, lane, obstacles)


def _approach(port: tuple[float, float], dx: float, dy: float, obstacles: list[Rect]) -> tuple[float, float]:
    """Step away from a port, stopping before a title band or another resource."""
    length = (dx * dx + dy * dy) ** 0.5
    if length < 1:
        return port
    ux, uy = dx / length, dy / length
    best = port
    dist = 4.0
    while dist <= 16.1:
        point = (port[0] + ux * dist, port[1] + uy * dist)
        if not _clear(port[0], port[1], point[0], point[1], obstacles):
            break
        best = point
        dist += 4.0
    return best


def _detour_horizontal(start, end, leave, arrive, lane, obstacles: list[Rect]):
    routed = _around(leave, arrive, obstacles, horizontal=True, lane=lane)
    if routed is not None:
        return _clean([start, leave, *routed, arrive, end])
    for pad in (36, 72, 120, 180, 260):
        for y in (min(leave[1], arrive[1]) - pad, max(leave[1], arrive[1]) + pad):
            if (
                _clear(leave[0], leave[1], leave[0], y, obstacles)
                and _clear(leave[0], y, arrive[0], y, obstacles)
                and _clear(arrive[0], y, arrive[0], arrive[1], obstacles)
            ):
                return _clean([start, leave, (leave[0], y), (arrive[0], y), arrive, end])
    return _clear_elbow(start, end, obstacles, horizontal=True)


def _detour_vertical(start, end, leave, arrive, lane, obstacles: list[Rect]):
    routed = _around(leave, arrive, obstacles, horizontal=False, lane=lane)
    if routed is not None:
        return _clean([start, leave, *routed, arrive, end])
    for pad in (36, 72, 120, 180, 260):
        for x in (min(leave[0], arrive[0]) - pad, max(leave[0], arrive[0]) + pad):
            if (
                _clear(leave[0], leave[1], x, leave[1], obstacles)
                and _clear(x, leave[1], x, arrive[1], obstacles)
                and _clear(x, arrive[1], arrive[0], arrive[1], obstacles)
            ):
                return _clean([start, leave, (x, leave[1]), (x, arrive[1]), arrive, end])
    return _clear_elbow(start, end, obstacles, horizontal=False)


def _around(leave, arrive, obstacles: list[Rect], *, horizontal: bool, lane: float):
    """Bridge, then step along the port into a gap and bridge from there."""
    bridged = _bridge(leave, arrive, obstacles, horizontal=horizontal, lane=lane)
    if bridged is not None:
        return bridged
    best = None
    best_cost = None
    for post in _axis_posts(leave, arrive, obstacles, horizontal=horizontal):
        bridged = _bridge(post, arrive, obstacles, horizontal=horizontal, lane=lane)
        if bridged is None:
            continue
        path = [post, *bridged]
        cost = _path_cost(leave, path)
        if best is None or cost < best_cost:
            best = path
            best_cost = cost
    if best is not None:
        return best
    for post in _axis_posts(arrive, leave, obstacles, horizontal=horizontal):
        bridged = _bridge(leave, post, obstacles, horizontal=horizontal, lane=lane)
        if bridged is None:
            continue
        path = [*bridged, post]
        cost = _path_cost(leave, path)
        if best is None or cost < best_cost:
            best = path
            best_cost = cost
    return best


def _axis_posts(origin, other, obstacles: list[Rect], *, horizontal: bool) -> list[tuple[float, float]]:
    """Spots on the straight line through a port that can be reached without a turn."""
    if horizontal:
        lo, hi = sorted((origin[0], other[0]))
        lo, hi = lo - 80.0, hi + 80.0
        marks = set()
        for rect in obstacles:
            if rect.bottom < origin[1] - 24 or rect.top > origin[1] + 24:
                continue
            marks.add(round(rect.left - 14))
            marks.add(round(rect.right + 14))
        posts = []
        for mark in sorted(marks):
            if mark < lo or mark > hi or abs(mark - origin[0]) < 8:
                continue
            point = (float(mark), origin[1])
            if _clear(origin[0], origin[1], point[0], point[1], obstacles):
                posts.append(point)
        return posts
    lo, hi = sorted((origin[1], other[1]))
    lo, hi = lo - 80.0, hi + 80.0
    marks = set()
    for rect in obstacles:
        if rect.right < origin[0] - 24 or rect.left > origin[0] + 24:
            continue
        marks.add(round(rect.top - 14))
        marks.add(round(rect.bottom + 14))
    posts = []
    for mark in sorted(marks):
        if mark < lo or mark > hi or abs(mark - origin[1]) < 8:
            continue
        point = (origin[0], float(mark))
        if _clear(origin[0], origin[1], point[0], point[1], obstacles):
            posts.append(point)
    return posts


def _path_cost(origin, path) -> float:
    cost = abs(path[0][0] - origin[0]) + abs(path[0][1] - origin[1])
    previous = path[0]
    for point in path[1:]:
        cost += abs(point[0] - previous[0]) + abs(point[1] - previous[1])
        previous = point
    return cost


def _clear_elbow(start, end, obstacles: list[Rect], *, horizontal: bool):
    """A right-angle bend that stays off labels and icons when one exists."""
    x1, y1 = start
    x2, y2 = end
    bends = []
    if horizontal:
        bends.append((x1 + x2) / 2.0)
        for rect in obstacles:
            bends.extend((rect.left - 14, rect.right + 14))
        for bend in bends:
            if not (min(x1, x2) - 80 <= bend <= max(x1, x2) + 80):
                continue
            points = [start, (bend, y1), (bend, y2), end]
            if _path_clear(points, obstacles):
                return _clean(points)
    else:
        bends.append((y1 + y2) / 2.0)
        for rect in obstacles:
            bends.extend((rect.top - 14, rect.bottom + 14))
        for bend in bends:
            if not (min(y1, y2) - 80 <= bend <= max(y1, y2) + 80):
                continue
            points = [start, (x1, bend), (x2, bend), end]
            if _path_clear(points, obstacles):
                return _clean(points)
    return _elbow(start, end, horizontal=horizontal)


def _path_clear(points, obstacles: list[Rect]) -> bool:
    return all(
        _clear(a[0], a[1], b[0], b[1], obstacles)
        for a, b in zip(points, points[1:])
        if abs(a[0] - b[0]) > 0.6 or abs(a[1] - b[1]) > 0.6
    )


def _bridge(leave, arrive, obstacles: list[Rect], *, horizontal: bool, lane: float = 0.0):
    """One extra bend so a connector can use the gap above a row of resources."""
    x1, y1 = leave
    x2, y2 = arrive
    pad = 48.0
    if horizontal:
        min_x, max_x = min(x1, x2) - pad, max(x1, x2) + pad
        min_y, max_y = min(y1, y2) - 72, max(y1, y2) + 72
    else:
        min_x, max_x = min(x1, x2) - 72, max(x1, x2) + 72
        min_y, max_y = min(y1, y2) - pad, max(y1, y2) + pad
    relevant = [
        rect
        for rect in obstacles
        if rect.right >= min_x and rect.left <= max_x and rect.bottom >= min_y and rect.top <= max_y
    ]
    xs = {round(x1), round(x2), round((x1 + x2) / 2)}
    ys = {round(y1), round(y2), round((y1 + y2) / 2)}
    for rect in relevant:
        xs.update(round(value) for value in (rect.left - 12, rect.left - 6, rect.right + 6, rect.right + 12))
        ys.update(round(value) for value in (rect.top - 12, rect.top - 6, rect.bottom + 6, rect.bottom + 12))
    cursor = min_x
    while cursor <= max_x:
        xs.add(round(cursor))
        cursor += 10
    cursor = min_y
    while cursor <= max_y:
        ys.add(round(cursor))
        cursor += 10

    best = None
    best_cost = None
    for y in ys:
        for x in xs:
            if horizontal:
                segments = ((x1, y1, x1, y), (x1, y, x, y), (x, y, x, y2), (x, y2, x2, y2))
            else:
                segments = ((x1, y1, x, y1), (x, y1, x, y), (x, y, x2, y), (x2, y, x2, y2))
            if not all(_clear(a, b, c, d, obstacles) for a, b, c, d in segments):
                continue
            cost = abs(y - y1) + abs(y - y2) + abs(x - x1) + abs(x - x2)
            # A clear lane above the icons beats a detour underneath the boxes.
            if horizontal and y > max(y1, y2) + 10:
                cost += (y - max(y1, y2)) * 4
            # Parallel connectors take neighbouring gaps when both are clear.
            if horizontal:
                cost += abs(y - (min(y1, y2) + lane)) * 0.35
                cost += _kink_cost(y - y1) + _kink_cost(y - y2)
            else:
                cost += abs(x - (min(x1, x2) + lane)) * 0.35
                cost += _kink_cost(x - x1) + _kink_cost(x - x2)
            if best is None or cost < best_cost:
                best = (x, y)
                best_cost = cost
    if best is None:
        return None
    x, y = best
    if horizontal:
        return [(x1, y), (x, y), (x, y2)]
    return [(x, y1), (x, y), (x2, y)]


def _loop(element: Endpoint) -> list[tuple[float, float]]:
    icon = _icon_bounds(element)
    return [
        (icon.right, icon.cy),
        (icon.right + 18, icon.cy),
        (icon.right + 18, icon.y - 16),
        (icon.cx, icon.y - 16),
        (icon.cx, icon.y),
    ]


def _clear(x1: float, y1: float, x2: float, y2: float, obstacles: list[Rect]) -> bool:
    return not any(_hits(x1, y1, x2, y2, rect) for rect in obstacles)


def _hits(x1: float, y1: float, x2: float, y2: float, rect: Rect) -> bool:
    if abs(y1 - y2) <= 0.8:
        y = y1
        left, right = sorted((x1, x2))
        return rect.top <= y <= rect.bottom and left < rect.right and right > rect.left
    if abs(x1 - x2) <= 0.8:
        x = x1
        top, bottom = sorted((y1, y2))
        return rect.left <= x <= rect.right and top < rect.bottom and bottom > rect.top
    return False


def _elbow(start, end, *, horizontal: bool) -> list[tuple[float, float]]:
    """A right-angle connector. The last segment meets the target port straight on."""
    x1, y1 = start
    x2, y2 = end
    if abs(x1 - x2) <= 0.8 or abs(y1 - y2) <= 0.8:
        return _clean([start, end])
    if horizontal:
        mid = (x1 + x2) / 2.0
        return _clean([start, (mid, y1), (mid, y2), end])
    mid = (y1 + y2) / 2.0
    return _clean([start, (x1, mid), (x2, mid), end])


def _orthogonal(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Replace any slanted segment with a horizontal run and a vertical run."""
    if len(points) < 2:
        return points
    out = [points[0]]
    for nxt in points[1:]:
        x1, y1 = out[-1]
        x2, y2 = nxt
        if abs(x1 - x2) <= 0.8 or abs(y1 - y2) <= 0.8:
            out.append((x2, y2))
            continue
        if len(out) >= 2 and abs(out[-2][1] - y1) <= 0.8:
            out.append((x2, y1))
        else:
            out.append((x1, y2))
        out.append((x2, y2))
    return _clean(out)


def _clean(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Drop duplicates, and pull a colinear run onto one horizontal or vertical line."""
    if not points:
        return points
    cleaned = [points[0]]
    for point in points[1:]:
        last = cleaned[-1]
        if abs(point[0] - last[0]) < 0.6 and abs(point[1] - last[1]) < 0.6:
            continue
        if len(cleaned) >= 2 and _colinear(cleaned[-2], last, point):
            cleaned[-1] = _snap(cleaned[-2], point)
            continue
        cleaned.append(point)
    return cleaned


def _colinear(a, b, c) -> bool:
    horizontal = abs(a[1] - b[1]) <= 0.8 and abs(b[1] - c[1]) <= 0.8
    vertical = abs(a[0] - b[0]) <= 0.8 and abs(b[0] - c[0]) <= 0.8
    return horizontal or vertical


def _snap(origin, point) -> tuple[float, float]:
    if abs(origin[1] - point[1]) <= 0.8:
        return (point[0], origin[1])
    return (origin[0], point[1])


def _simplify(points, obstacles, source, target, lane: float = 0.0):
    """Straight when the gap is clear. Otherwise drop a kink, or make the step square."""
    pts = _clean(points)
    if len(pts) < 2:
        return pts
    start, end = pts[0], pts[-1]
    if abs(lane) < 1:
        straight = _try_straight(pts, obstacles, source, target)
        if straight is not None:
            return straight
    for _ in range(8):
        nxt = _absorb_once(pts, obstacles, source, target, start, end)
        if nxt is None:
            break
        pts = _clean(nxt)
    pts = _square_steps(pts, obstacles, source, target, start, end)
    pts = _square_arrival(pts, obstacles, source, target, start, end)
    return _clean(pts)


def _try_straight(points, obstacles, source, target):
    start, end = points[0], points[-1]
    dx, dy = abs(end[0] - start[0]), abs(end[1] - start[1])
    if dx >= dy and dy < _JOG and dx > 0.8:
        for y in (end[1], start[1]):
            trial = [(start[0], y), (end[0], y)]
            if _acceptable(trial, obstacles, source, target, start, end):
                return trial
    if dy > dx and dx < _JOG and dy > 0.8:
        for x in (end[0], start[0]):
            trial = [(x, start[1]), (x, end[1])]
            if _acceptable(trial, obstacles, source, target, start, end):
                return trial
    return None


def _absorb_once(pts, obstacles, source, target, start, end):
    for index in range(len(pts) - 3):
        trial = _flatten_jog(pts, index, obstacles, source, target, start, end)
        if trial is not None:
            return trial
    return _flatten_stub(pts, obstacles, source, target, start, end)


def _flatten_jog(pts, index, obstacles, source, target, start, end):
    a, b, c, d = pts[index : index + 4]
    incoming, middle, outgoing = _dir(a, b), _dir(b, c), _dir(c, d)
    if incoming == 0 or incoming != outgoing or incoming == middle:
        return None
    if abs(c[0] - b[0]) + abs(c[1] - b[1]) >= _JOG:
        return None
    travel = 0 if incoming == 1 else 1
    if (b[travel] - a[travel]) * (d[travel] - c[travel]) <= 0:
        return None
    keep_incoming = _run(pts, index + 1, -1)
    keep_outgoing = _run(pts, index + 2, 1)
    cross = 1 - travel
    first, second = (keep_incoming, b), (keep_outgoing, c)
    if _span(pts, keep_outgoing) > _span(pts, keep_incoming):
        first, second = (keep_outgoing, c), (keep_incoming, b)
    for run, anchor in (first, second):
        other = keep_outgoing if run is keep_incoming else keep_incoming
        trial = _shift(pts, other, cross, anchor[cross])
        if _acceptable(_clean(trial), obstacles, source, target, start, end):
            return trial
    return None


def _flatten_stub(pts, obstacles, source, target, start, end):
    """A short last or first leg disappears when the run beside it can meet the icon."""
    if len(pts) < 3:
        return None
    for end_side in (True, False):
        if end_side:
            a, b, c = pts[-3], pts[-2], pts[-1]
        else:
            a, b, c = pts[2], pts[1], pts[0]
        left, right = _dir(a, b), _dir(b, c)
        if left == 0 or right == 0 or left == right:
            continue
        if abs(c[0] - b[0]) + abs(c[1] - b[1]) >= _JOG:
            continue
        coord = 0 if right == 2 else 1
        moved = list(c)
        moved[1 - coord] = b[1 - coord]
        trial = list(pts)
        trial[-1 if end_side else 0] = tuple(moved)
        if _acceptable(_clean(trial), obstacles, source, target, start, end):
            return trial
    return None


def _square_steps(pts, obstacles, source, target, start, end):
    """A detour that already turns keeps a short interior step only if it can grow to a square."""
    if _bends(pts) < 2:
        return pts
    for index in range(1, len(pts) - 2):
        b, c = pts[index], pts[index + 1]
        if _dir(b, c) == 0 or _dir(pts[index - 1], b) == _dir(b, c):
            continue
        length = abs(c[0] - b[0]) + abs(c[1] - b[1])
        if length >= _JOG or length < 0.8:
            continue
        coord = 1 if abs(b[0] - c[0]) <= 0.8 else 0
        sign = 1.0 if c[coord] >= b[coord] else -1.0
        run = _run(pts, index + 1, 1)
        if 0 in run or len(pts) - 1 in run:
            continue
        shifted = _shift(pts, run, coord, b[coord] + sign * _SQUARE)
        cleaned = _clean(shifted)
        if _acceptable(cleaned, obstacles, source, target, start, end):
            return _square_steps(cleaned, obstacles, source, target, start, end)
    return pts


def _square_arrival(pts, obstacles, source, target, start, end):
    """Keep the arrow on the icon, but don't finish with a kink of a few pixels."""
    if len(pts) < 3:
        return pts
    b, c = pts[-2], pts[-1]
    length = abs(c[0] - b[0]) + abs(c[1] - b[1])
    if length >= _JOG or length < 0.8 or _dir(pts[-3], b) == _dir(b, c):
        return pts
    axis = 1 if abs(b[0] - c[0]) <= 0.8 else 0
    sign = 1.0 if c[axis] >= b[axis] else -1.0
    run = _run(pts, len(pts) - 2, -1)
    if 0 in run or (len(pts) - 1) in run:
        return pts
    shifted = _shift(pts, run, axis, c[axis] - sign * _SQUARE)
    cleaned = _clean(shifted)
    if _acceptable(cleaned, obstacles, source, target, start, end):
        return cleaned
    return pts


def _bends(pts) -> int:
    count = 0
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        if _dir(a, b) and _dir(b, c) and _dir(a, b) != _dir(b, c):
            count += 1
    return count


def _dir(a, b) -> int:
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    if dx <= 0.8 and dy <= 0.8:
        return 0
    if dy <= 0.8:
        return 1
    if dx <= 0.8:
        return 2
    return 0


def _run(pts, index, step) -> list[int]:
    run = [index]
    j = index + step
    if j < 0 or j >= len(pts):
        return run
    horizontal = abs(pts[index][1] - pts[j][1]) <= 0.8
    while 0 <= j < len(pts):
        prev, cur = pts[j - step], pts[j]
        if horizontal and abs(prev[1] - cur[1]) > 0.8:
            break
        if not horizontal and abs(prev[0] - cur[0]) > 0.8:
            break
        run.append(j)
        j += step
    return run


def _span(pts, indices) -> float:
    ordered = sorted(indices)
    return sum(abs(pts[a][0] - pts[b][0]) + abs(pts[a][1] - pts[b][1]) for a, b in zip(ordered, ordered[1:]))


def _shift(pts, indices, coord, value):
    moved = [list(point) for point in pts]
    for index in indices:
        moved[index][coord] = value
    return [tuple(point) for point in moved]


def _acceptable(pts, obstacles, source, target, start, end) -> bool:
    if len(pts) < 2:
        return False
    if not _on_side(source, start, pts[0]) or not _on_side(target, end, pts[-1]):
        return False
    for a, b in zip(pts, pts[1:]):
        if abs(a[0] - b[0]) < 0.6 and abs(a[1] - b[1]) < 0.6:
            continue
        if abs(a[0] - b[0]) > 0.8 and abs(a[1] - b[1]) > 0.8:
            return False
        if not _clear(a[0], a[1], b[0], b[1], obstacles):
            return False
    return True


def _on_side(element: Endpoint, original, moved) -> bool:
    rect = _icon_bounds(element)
    ox, oy = original
    x, y = moved
    if abs(ox - rect.left) <= 1.5 or abs(ox - rect.right) <= 1.5:
        side = rect.left if abs(ox - rect.left) <= abs(ox - rect.right) else rect.right
        return abs(x - side) <= 1.5 and rect.top - 0.5 <= y <= rect.bottom + 0.5
    if abs(oy - rect.top) <= 1.5 or abs(oy - rect.bottom) <= 1.5:
        side = rect.top if abs(oy - rect.top) <= abs(oy - rect.bottom) else rect.bottom
        return abs(y - side) <= 1.5 and rect.left - 0.5 <= x <= rect.right + 0.5
    return abs(x - ox) <= 0.8 and abs(y - oy) <= 0.8
