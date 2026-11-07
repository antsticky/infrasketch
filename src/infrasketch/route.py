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
        obstacles.append((element, _bounds(element).expanded(8)))
    for element in diagram.walk():
        if isinstance(element, Group):
            # Titles stay clear. The rest of a boundary can be crossed.
            obstacles.append((None, Rect(element.abs_x - 3, element.abs_y - 3, element.w + 6, element.header_h + 8)))
    _assign_lanes(diagram.edges)
    for edge in diagram.edges:
        edge.points = _route(edge, obstacles)


def _nodes(diagram: Diagram):
    for element in diagram.walk():
        if isinstance(element, Node):
            yield element


def _bounds(element: Endpoint) -> Rect:
    return Rect(element.abs_x, element.abs_y, element.w, element.h)


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
        if edge.source is edge.target:
            edge.lane = 0.0
            continue
        start, end, orient = _ports(edge.source, edge.target)
        if orient == "h":
            key = ("h", round(start[1] / 34), round(end[1] / 34), int(end[0] >= start[0]))
        else:
            key = ("v", round(start[0] / 34), round(end[0] / 34), int(end[1] >= start[1]))
        buckets[key].append(edge)
    for items in buckets.values():
        count = len(items)
        for index, edge in enumerate(items):
            edge.lane = (index - (count - 1) / 2.0) * 18.0


def _route(edge: Connection, obstacles: list[tuple[Endpoint, Rect]]) -> list[tuple[float, float]]:
    source, target = edge.source, edge.target
    if source is target:
        return _loop(source)
    start, end, orient = _ports(source, target)
    blocked = [rect for element, rect in obstacles if element is not source and element is not target]
    if isinstance(target, Group):
        blocked = [rect for element, rect in obstacles if element is not source]
    if isinstance(source, Group):
        blocked = [rect for element, rect in obstacles if element is not target]
    if orient == "h":
        return _route_horizontal(start, end, edge.lane, blocked)
    return _route_vertical(start, end, edge.lane, blocked)


def _route_horizontal(start, end, lane, obstacles: list[Rect]) -> list[tuple[float, float]]:
    forward = end[0] >= start[0]
    distance = abs(end[0] - start[0])
    stub = min(16.0, max(8.0, distance * 0.22))
    sign = 1.0 if forward else -1.0
    leave = (start[0] + sign * stub, start[1])
    arrive = (end[0] - sign * stub, end[1])
    if abs(leave[1] - arrive[1]) < 1 and (arrive[0] - leave[0]) * sign > 0:
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
    return _detour_horizontal(start, end, leave, arrive, obstacles)


def _route_vertical(start, end, lane, obstacles: list[Rect]) -> list[tuple[float, float]]:
    forward = end[1] >= start[1]
    distance = abs(end[1] - start[1])
    stub = min(16.0, max(8.0, distance * 0.22))
    sign = 1.0 if forward else -1.0
    leave = (start[0], start[1] + sign * stub)
    arrive = (end[0], end[1] - sign * stub)
    if abs(leave[0] - arrive[0]) < 1 and (arrive[1] - leave[1]) * sign > 0:
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
    return _detour_vertical(start, end, leave, arrive, obstacles)


def _detour_horizontal(start, end, leave, arrive, obstacles: list[Rect]):
    bridged = _bridge(leave, arrive, obstacles, horizontal=True)
    if bridged is not None:
        return _clean([start, leave, *bridged, arrive, end])
    channel = (leave[1] + arrive[1]) / 2.0
    return _clean([start, leave, (leave[0], channel), (arrive[0], channel), arrive, end])


def _detour_vertical(start, end, leave, arrive, obstacles: list[Rect]):
    bridged = _bridge(leave, arrive, obstacles, horizontal=False)
    if bridged is not None:
        return _clean([start, leave, *bridged, arrive, end])
    channel = (leave[0] + arrive[0]) / 2.0
    return _clean([start, leave, (channel, leave[1]), (channel, arrive[1]), arrive, end])


def _bridge(leave, arrive, obstacles: list[Rect], *, horizontal: bool):
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
        xs.update((round(rect.left - 14), round(rect.right + 14)))
        ys.update((round(rect.top - 14), round(rect.bottom + 14)))
    cursor = min_x
    while cursor <= max_x:
        xs.add(round(cursor))
        cursor += 14
    cursor = min_y
    while cursor <= max_y:
        ys.add(round(cursor))
        cursor += 14

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


def _clean(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    cleaned = [points[0]]
    for point in points[1:]:
        if abs(point[0] - cleaned[-1][0]) >= 0.6 or abs(point[1] - cleaned[-1][1]) >= 0.6:
            cleaned.append(point)
    return cleaned
