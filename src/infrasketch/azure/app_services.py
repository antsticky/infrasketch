"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class AppServicePlans(Node):
    """App Service Plan."""

    icon = "azure/app_services/AppServicePlans.svg"
    service = "App Service Plan"

class AppServiceCertificates(Node):
    """App Service Certificates."""

    icon = "azure/app_services/AppServiceCertificates.svg"
    service = "App Service Certificates"

class AppServiceDomains(Node):
    """App Service Domains."""

    icon = "azure/app_services/AppServiceDomains.svg"
    service = "App Service Domains"

class CDNProfiles(Node):
    """CDN."""

    icon = "azure/app_services/CDNProfiles.svg"
    service = "CDN"

class AppServices(Node):
    """App Service."""

    icon = "azure/app_services/AppServices.svg"
    service = "App Service"

class CognitiveSearch(Node):
    """AI Search."""

    icon = "azure/app_services/CognitiveSearch.svg"
    service = "AI Search"

class NotificationHubs(Node):
    """Notification Hubs."""

    icon = "azure/app_services/NotificationHubs.svg"
    service = "Notification Hubs"

class AppServiceEnvironments(Node):
    """App Service Environments."""

    icon = "azure/app_services/AppServiceEnvironments.svg"
    service = "App Service Environments"
