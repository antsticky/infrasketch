"""Services that belong to neither Azure nor AWS.

Each class is a node. More external icons can be added the same way:
a class here, an SVG under ``data/icons/external/``, and a row in
``data/external-catalog.json``.
"""

from infrasketch.model import Node

__all__ = ["Akamai", "Cloudflare", "GitHub"]


class Akamai(Node):
    """Akamai."""

    icon = "external/akamai.svg"
    service = "Akamai"


class Cloudflare(Node):
    """Cloudflare."""

    icon = "external/cloudflare.svg"
    service = "Cloudflare"


class GitHub(Node):
    """GitHub."""

    icon = "external/github.svg"
    service = "GitHub"
