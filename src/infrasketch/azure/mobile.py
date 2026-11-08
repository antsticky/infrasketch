"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class PowerPlatform(Node):
    """Power Platform."""

    icon = "azure/mobile/PowerPlatform.svg"
    service = "Power Platform"

class AppServices(Node):
    """App Service."""

    icon = "azure/mobile/AppServices.svg"
    service = "App Service"

class NotificationHubs(Node):
    """Notification Hubs."""

    icon = "azure/mobile/NotificationHubs.svg"
    service = "Notification Hubs"
