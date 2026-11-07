"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class RemoteRendering(Node):
    """Remote Rendering."""

    icon = "mixed_reality/RemoteRendering.svg"
    service = "Remote Rendering"

class SpatialAnchorAccounts(Node):
    """Spatial Anchor Accounts."""

    icon = "mixed_reality/SpatialAnchorAccounts.svg"
    service = "Spatial Anchor Accounts"
