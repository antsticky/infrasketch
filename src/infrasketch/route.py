"""Orthogonal connectors that stay in the gaps between resources."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from infrasketch.model import Connection, Diagram, Endpoint, Group, Node


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
    _assign_lanes(diagram.edges)
    for edge in diagram.edges:
        source, target = _shown(edge.source), _shown(edge.target)
        if source is target:
            edge.points = [] if source is not edge.source else _orthogonal(_loop(source))
            continue
        edge.points = _orthogonal(_route(edge, obstacles, source, target))


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


def _route(
    edge: Connection,
    obstacles: list[tuple[Endpoint, Rect]],
    source: Endpoint | None = None,
    target: Endpoint | None = None,
) -> list[tuple[float, float]]:
    source = source or edge.source
    target = target or edge.target
    if source is target:
        return _loop(source)
    start, end, orient = _ports(source, target)
    blocked = [rect for element, rect in obstacles if element is not source and element is not target]
    if isinstance(target, Group) and not target.folded:
        blocked = [rect for element, rect in obstacles if element is not source]
    if isinstance(source, Group) and not source.folded:
        blocked = [rect for element, rect in obstacles if element is not target]
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
    bridged = _bridge(leave, arrive, obstacles, horizontal=True, lane=lane)
    if bridged is not None:
        return _clean([start, leave, *bridged, arrive, end])
    for pad in (36, 72, 120, 180, 260):
        for y in (min(leave[1], arrive[1]) - pad, max(leave[1], arrive[1]) + pad):
            if (
                _clear(leave[0], leave[1], leave[0], y, obstacles)
                and _clear(leave[0], y, arrive[0], y, obstacles)
                and _clear(arrive[0], y, arrive[0], arrive[1], obstacles)
            ):
                return _clean([start, leave, (leave[0], y), (arrive[0], y), arrive, end])
    return _elbow(start, end, horizontal=True)


def _detour_vertical(start, end, leave, arrive, lane, obstacles: list[Rect]):
    bridged = _bridge(leave, arrive, obstacles, horizontal=False, lane=lane)
    if bridged is not None:
        return _clean([start, leave, *bridged, arrive, end])
    for pad in (36, 72, 120, 180, 260):
        for x in (min(leave[0], arrive[0]) - pad, max(leave[0], arrive[0]) + pad):
            if (
                _clear(leave[0], leave[1], x, leave[1], obstacles)
                and _clear(x, leave[1], x, arrive[1], obstacles)
                and _clear(x, arrive[1], arrive[0], arrive[1], obstacles)
            ):
                return _clean([start, leave, (x, leave[1]), (x, arrive[1]), arrive, end])
    return _elbow(start, end, horizontal=False)


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
            else:
                cost += abs(x - (min(x1, x2) + lane)) * 0.35
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
    cleaned = [points[0]]
    for point in points[1:]:
        if abs(point[0] - cleaned[-1][0]) >= 0.6 or abs(point[1] - cleaned[-1][1]) >= 0.6:
            cleaned.append(point)
    return cleaned
