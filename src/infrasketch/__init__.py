"""Draw Azure and AWS architecture diagrams as SVG, with the official resource icons.

Graphviz is not required. A diagram is a ``with`` block, resources are
constructed inside it, and ``>>`` draws the arrow::

    from infrasketch import Diagram
    from infrasketch.azure import FrontDoor, FunctionApp, Redis, ResourceGroup

    with Diagram("Orders", "orders.svg"):
        with ResourceGroup("rg-app"):
            web = FrontDoor("Frontend")
            api = FunctionApp("API")
            cache = Redis("Sessions")
        web >> api >> cache

The file is written when the block ends. ``python -m infrasketch search redis``
finds the class for any other resource. AWS resources are in ``infrasketch.aws``.

The source code is MIT. The Azure icons are Microsoft artwork and the AWS
icons are Amazon Web Services artwork. Neither set is covered by that license.
See ``NOTICE``.
"""

from infrasketch.groups import Cluster, DMZ, Namespace, Network, OnPremises, Zone
from infrasketch.model import Async, Diagram, Edge, Group, Https, Node, Private
from infrasketch.search import categories, search

__all__ = [
    "Async",
    "Cluster",
    "DMZ",
    "Diagram",
    "Edge",
    "Group",
    "Https",
    "Namespace",
    "Network",
    "Node",
    "OnPremises",
    "Private",
    "Zone",
    "categories",
    "search",
]
