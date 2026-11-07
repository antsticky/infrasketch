"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class BlockchainApplications(Node):
    """Blockchain Applications."""

    icon = "blockchain/BlockchainApplications.svg"
    service = "Blockchain Applications"

class OutboundConnection(Node):
    """Outbound Connection."""

    icon = "blockchain/OutboundConnection.svg"
    service = "Outbound Connection"

class AzureBlockchainService(Node):
    """Azure Blockchain Service."""

    icon = "blockchain/AzureBlockchainService.svg"
    service = "Azure Blockchain Service"

class AzureTokenService(Node):
    """Azure Token Service."""

    icon = "blockchain/AzureTokenService.svg"
    service = "Azure Token Service"

class ABSMember(Node):
    """ABS Member."""

    icon = "blockchain/ABSMember.svg"
    service = "ABS Member"

class Consortium(Node):
    """Consortium."""

    icon = "blockchain/Consortium.svg"
    service = "Consortium"
