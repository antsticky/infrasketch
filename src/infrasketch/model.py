"""Diagram model and the connection operators.

Create resources inside a ``Diagram``. ``>>`` draws a forward arrow,
``<<`` draws one pointing back at the left side, and ``-`` draws a plain line.
Lists work on either side because the right-hand object handles the operator.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Iterator

_stack: list[Scope] = []


class DiagramError(RuntimeError):
    """Raised when a diagram is built outside a valid context."""


class Scope:
    """A diagram or a boundary that can contain nodes and other boundaries."""

    def __init__(self) -> None:
        self.children: list[Endpoint] = []
        self.parent: Scope | None = None
        self.diagram: Diagram | None = None
        self.x = 0.0
        self.y = 0.0
        self.w = 0.0
        self.h = 0.0
        self.abs_x = 0.0
        self.abs_y = 0.0
        self.content_w = 0.0
        self.content_h = 0.0
        self.content_x = 0.0
        self.content_y = 0.0

    def walk(self) -> Iterator[Endpoint]:
        for child in self.children:
            yield child
            if isinstance(child, Scope):
                yield from child.walk()


class Endpoint(Scope):
    """Something an arrow can connect to: a resource or a boundary."""

    label = ""
    sku = ""
    region = ""
    public: bool | None = None
    note = ""

    def facts(self) -> str:
        """SKU, region, and exposure, joined for the second caption."""
        parts = []
        if self.sku:
            parts.append(self.sku)
        if self.region:
            parts.append(self.region)
        if self.public is True:
            parts.append("Public")
        elif self.public is False:
            parts.append("Private")
        return " · ".join(parts)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.label!r})"

    def connect(self, other: Endpoint, edge: Edge) -> Endpoint:
        if not isinstance(other, Endpoint):
            raise DiagramError(f"{other!r} is not a resource or group")
        diagram = self.diagram
        if diagram is None or other.diagram is None:
            raise DiagramError("Connect resources that belong to a diagram")
        if diagram is not other.diagram:
            raise DiagramError("Cannot connect resources from different diagrams")
        if edge.forward and edge.reverse:
            direction = "both"
        elif edge.forward:
            direction = "forward"
        elif edge.reverse:
            direction = "back"
        else:
            direction = "none"
        diagram.edges.append(
            Connection(
                source=self,
                target=other,
                label=edge.label,
                color=edge.color,
                style=edge.style or "solid",
                direction=direction,
                number=edge.number,
            )
        )
        return other

    def __rshift__(self, other):
        if isinstance(other, list):
            for item in other:
                self >> item
            return other
        if isinstance(other, Endpoint):
            return self.connect(other, Edge(forward=True))
        other.forward = True
        other.node = self
        return other

    def __lshift__(self, other):
        if isinstance(other, list):
            for item in other:
                self << item
            return other
        if isinstance(other, Endpoint):
            return self.connect(other, Edge(reverse=True))
        other.reverse = True
        return other.connect(self)

    def __sub__(self, other):
        if isinstance(other, list):
            for item in other:
                self - item
            return other
        if isinstance(other, Endpoint):
            return self.connect(other, Edge())
        other.node = self
        return other

    def __rrshift__(self, other):
        for item in other:
            if isinstance(item, Edge):
                item.forward = True
                item.connect(self)
            else:
                item.connect(self, Edge(forward=True))
        return self

    def __rlshift__(self, other):
        for item in other:
            if isinstance(item, Edge):
                item.reverse = True
                item.connect(self)
            else:
                item.connect(self, Edge(reverse=True))
        return self

    def __rsub__(self, other):
        for item in other:
            if isinstance(item, Edge):
                item.connect(self)
            else:
                item.connect(self, Edge())
        return self


@dataclass
class Connection:
    source: Endpoint
    target: Endpoint
    label: str = ""
    color: str = ""
    style: str = "solid"
    direction: str = "forward"
    number: int | None = None
    points: list[tuple[float, float]] = field(default_factory=list)
    lane: float = 0.0


class Edge:
    """A connector. Put it between resources: ``api >> Edge("SQL") >> db``."""

    def __init__(
        self,
        label: str = "",
        number: int | None = None,
        *,
        color: str = "",
        style: str = "solid",
        forward: bool = False,
        reverse: bool = False,
        node: Endpoint | None = None,
    ) -> None:
        self.label = label or ""
        self.number = _check_number(number)
        self.color = color or ""
        self.style = style or "solid"
        self.forward = forward
        self.reverse = reverse
        self.node = node
        _check_color(self.color)
        if self.style not in {"solid", "dashed", "dotted"}:
            raise DiagramError("Edge style must be solid, dashed, or dotted")

    def __rshift__(self, other):
        self.forward = True
        return self.connect(other)

    def __lshift__(self, other):
        self.reverse = True
        return self.connect(other)

    def __sub__(self, other):
        return self.connect(other)

    def __rrshift__(self, other):
        return self._from_list(other, forward=True)

    def __rlshift__(self, other):
        return self._from_list(other, reverse=True)

    def __rsub__(self, other):
        return self._from_list(other)

    def _from_list(self, other, forward: bool = False, reverse: bool = False):
        result = []
        for item in other:
            edge = Edge(
                self.label,
                self.number,
                color=self.color,
                style=self.style,
                forward=forward or self.forward,
                reverse=reverse or self.reverse,
                node=item if isinstance(item, Endpoint) else None,
            )
            if isinstance(item, Edge):
                edge.label = item.label or edge.label
                edge.color = item.color or edge.color
                edge.style = item.style or edge.style
                if item.number is not None:
                    edge.number = item.number
            result.append(edge)
        return result

    def connect(self, other):
        if isinstance(other, list):
            for item in other:
                self.connect(item)
            return other
        if isinstance(other, Edge):
            if other.label:
                self.label = other.label
            if other.color:
                self.color = other.color
            if other.style:
                self.style = other.style
            if other.number is not None:
                self.number = other.number
            return self
        if self.node is not None:
            return self.node.connect(other, self)
        self.node = other
        return self


class Https(Edge):
    """HTTPS connector in Azure blue."""

    def __init__(self, label: str = "HTTPS", number: int | None = None, **kwargs) -> None:
        kwargs.setdefault("color", "#0078D4")
        super().__init__(label, number, **kwargs)


class Async(Edge):
    """Dashed connector for queues, events, and other asynchronous calls."""

    def __init__(self, label: str = "", number: int | None = None, **kwargs) -> None:
        kwargs.setdefault("color", "#7C3AED")
        kwargs.setdefault("style", "dashed")
        super().__init__(label, number, **kwargs)


class Private(Edge):
    """Dashed green connector for Private Link and private endpoints."""

    def __init__(self, label: str = "", number: int | None = None, **kwargs) -> None:
        kwargs.setdefault("color", "#107C41")
        kwargs.setdefault("style", "dashed")
        super().__init__(label, number, **kwargs)


class Node(Endpoint):
    """A single cloud resource. Subclasses set ``icon`` and ``service``."""

    icon: str | None = None
    service: str = "Resource"

    def __init__(
        self,
        label: str | None = None,
        *,
        caption: str | bool | None = None,
        icon: str | None = None,
        sku: str | None = None,
        region: str | None = None,
        public: bool | None = None,
        note: str | None = None,
        href: str | None = None,
    ) -> None:
        super().__init__()
        parent = _current_parent()
        service = self.service or type(self).__name__
        if label:
            self.label = label
            if caption is False:
                self.caption = ""
            elif isinstance(caption, str):
                self.caption = caption
            else:
                self.caption = "" if label == service else service
        else:
            self.label = service
            self.caption = ""
        self.icon = icon if icon is not None else self.__class__.icon
        self.sku = _text(sku, "sku")
        self.region = _text(region, "region")
        self.public = _check_public(public)
        self.note = _text(note, "note")
        self.href = _check_href(href)
        self.diagram = parent.diagram if not isinstance(parent, Diagram) else parent
        self.parent = parent
        parent.children.append(self)
        self.label_lines: list[str] = []
        self.caption_lines: list[str] = []
        self.detail_lines: list[str] = []
        self.note_lines: list[str] = []
        self.icon_box = (0.0, 0.0, 0.0, 0.0)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        doc = getattr(cls, "__doc__", None)
        if doc and cls.service == "Resource":
            cls.service = doc.strip().splitlines()[0].strip(". ")


class Group(Endpoint):
    """A rounded boundary. Prefer ``ResourceGroup``, ``VNet``, or ``Subnet``.

    The title opens and closes the box. ``folded=True`` starts it closed.
    ``foldable=False`` leaves the box fixed.
    """

    kind = "group"

    def __init__(
        self,
        label: str,
        *,
        kind: str | None = None,
        direction: str | None = None,
        arrange: str | None = None,
        columns: int | None = None,
        align: str | None = None,
        sku: str | None = None,
        region: str | None = None,
        public: bool | None = None,
        note: str | None = None,
        folded: bool = False,
        foldable: bool = True,
    ) -> None:
        super().__init__()
        self.label = label
        self.sku = _text(sku, "sku")
        self.region = _text(region, "region")
        self.public = _check_public(public)
        self.note = _text(note, "note")
        if not isinstance(folded, bool):
            raise DiagramError("folded must be true or false")
        if not isinstance(foldable, bool):
            raise DiagramError("foldable must be true or false")
        self.folded = folded
        self.foldable = foldable
        self.fold_id = ""
        self.fold_caption = ""
        self.kind = kind or self.__class__.kind
        self.direction = _check_direction(direction) if direction else None
        self.arrange = arrange
        self.columns = columns
        self.align = align
        self.header_h = 0.0
        if self.arrange not in {None, "flow", "row", "column", "grid"}:
            raise DiagramError("arrange must be flow, row, column, or grid")
        if self.align not in {None, "top", "center"}:
            raise DiagramError("align must be top or center")

    def __enter__(self) -> Group:
        parent = _current_parent()
        self.parent = parent
        self.diagram = parent if isinstance(parent, Diagram) else parent.diagram
        parent.children.append(self)
        _stack.append(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not _stack or _stack[-1] is not self:
            raise DiagramError("Group context closed out of order")
        _stack.pop()


def inside_folded(element: Endpoint) -> bool:
    """True when a folded boundary hides this resource."""
    parent = element.parent
    while isinstance(parent, Group):
        if parent.folded:
            return True
        parent = parent.parent
    return False


class Diagram(Scope):
    """An architecture diagram. Use it as a context manager.

    Resources created inside the ``with`` block are added to the diagram and,
    unless ``autosave`` is false, the SVG is written when the block ends.
    """

    def __init__(
        self,
        title: str,
        path: str | None = None,
        *,
        direction: str = "LR",
        subtitle: str | None = None,
        spacing: str = "regular",
        align: str = "top",
        autosave: bool = True,
        as_of: str | date | None = None,
    ) -> None:
        super().__init__()
        self.title = title
        self.subtitle = subtitle or ""
        self.as_of = _as_of(as_of)
        self.path = path or _slug(title) + ".svg"
        self.direction = _check_direction(direction)
        if spacing not in {"compact", "regular", "relaxed"}:
            raise DiagramError("spacing must be compact, regular, or relaxed")
        if align not in {"top", "center"}:
            raise DiagramError("align must be top or center")
        self.spacing = spacing
        self.align = align
        self.arrange = "flow"
        self.columns = None
        self.autosave = autosave
        self.edges: list[Connection] = []
        self.diagram = self
        self.label = title

    def __enter__(self) -> Diagram:
        if _stack:
            raise DiagramError("Start a diagram on its own, not inside another diagram or group")
        _stack.append(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not _stack or _stack[-1] is not self:
            raise DiagramError("Diagram context closed out of order")
        _stack.pop()
        if exc_type is None and self.autosave:
            self.save()

    def svg(self) -> str:
        from infrasketch.render import render_svg

        return render_svg(self)

    def save(self, path: str | None = None) -> str:
        from pathlib import Path

        destination = Path(path or self.path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.svg(), encoding="utf-8")
        self.path = str(destination)
        return self.path


def _current_parent() -> Scope:
    if not _stack:
        raise DiagramError(
            "Create resources inside a diagram:\n\n"
            "    with Diagram('Orders') as diagram:\n"
            "        api = FunctionApp('API')\n"
        )
    return _stack[-1]


def _check_direction(direction: str) -> str:
    value = direction.upper()
    if value not in {"LR", "TB"}:
        raise DiagramError("direction must be LR (left to right) or TB (top to bottom)")
    return value


def _as_of(value: str | date | None) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, date):
        return f"{value.day} {value.strftime('%b %Y')}"
    if not isinstance(value, str):
        raise DiagramError("as_of must be text or a date")
    return value.strip()


def _text(value: str | None, name: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise DiagramError(f"{name} must be text")
    return value.strip()


def _check_public(value: bool | None) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise DiagramError("public must be true or false")
    return value


def _check_href(value: str | None) -> str:
    if value is None or value == "":
        return ""
    if not isinstance(value, str) or not re.match(r"https?://\S+$", value.strip(), re.IGNORECASE):
        raise DiagramError("href must be an http or https URL")
    return value.strip()


def _check_number(value: int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise DiagramError("Edge number must be a positive integer")
    return value


def _check_color(color: str) -> None:
    if not color:
        return
    if re.fullmatch(r"#[0-9A-Fa-f]{3,8}", color) or re.fullmatch(r"[A-Za-z]{1,32}", color):
        return
    raise DiagramError(f"Unsupported edge color {color!r}. Use a hex color such as #0078D4.")


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")
    return slug or "diagram"
