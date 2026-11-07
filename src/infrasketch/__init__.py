"""Draw Azure architecture diagrams as SVG, with the official resource icons.

Graphviz is not required. A diagram is a ``with`` block, resources are
constructed inside it, and ``>>`` draws the arrow::

    from infrasketch import Diagram, FrontDoor, FunctionApp, Redis, ResourceGroup

    with Diagram("Orders", "orders.svg"):
        with ResourceGroup("rg-app"):
            web = FrontDoor("Frontend")
            api = FunctionApp("API")
            cache = Redis("Sessions")
        web >> api >> cache

The file is written when the block ends. ``python -m infrasketch search redis``
finds the class for any other resource.

The source code is MIT. The Azure icons are Microsoft artwork and are not
covered by that license. See ``NOTICE``.
"""

from infrasketch.groups import (
    Cluster,
    Group,
    PrivateNetwork,
    Region,
    ResourceGroup,
    Subnet,
    Subscription,
    VNet,
)
from infrasketch.model import Async, Diagram, Edge, Https, Node, Private
from infrasketch.search import categories, search
from infrasketch.shortcuts import *  # noqa: F403
from infrasketch.shortcuts import __all__ as _resources

__all__ = [
    "Async",
    "Cluster",
    "Diagram",
    "Edge",
    "Group",
    "Https",
    "Node",
    "Private",
    "PrivateNetwork",
    "Region",
    "ResourceGroup",
    "Subnet",
    "Subscription",
    "VNet",
    "categories",
    "search",
    *_resources,
]
