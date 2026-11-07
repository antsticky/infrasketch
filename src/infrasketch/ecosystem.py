"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class CollaborativeService(Node):
    """Collaborative Service."""

    icon = "ecosystem/CollaborativeService.svg"
    service = "Collaborative Service"

class Applens(Node):
    """Applens."""

    icon = "ecosystem/Applens.svg"
    service = "Applens"

class AzureHybridCenter(Node):
    """Azure Hybrid Center."""

    icon = "ecosystem/AzureHybridCenter.svg"
    service = "Azure Hybrid Center"
