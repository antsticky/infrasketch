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

    icon = "azure/web/AppServicePlans.svg"
    service = "App Service Plan"

class AppServiceCertificates(Node):
    """App Service Certificates."""

    icon = "azure/web/AppServiceCertificates.svg"
    service = "App Service Certificates"

class AppServiceDomains(Node):
    """App Service Domains."""

    icon = "azure/web/AppServiceDomains.svg"
    service = "App Service Domains"

class StaticApps(Node):
    """Static Web App."""

    icon = "azure/web/StaticApps.svg"
    service = "Static Web App"

class APICenter(Node):
    """API Center."""

    icon = "azure/web/APICenter.svg"
    service = "API Center"

class PowerPlatform(Node):
    """Power Platform."""

    icon = "azure/web/PowerPlatform.svg"
    service = "Power Platform"

class AppSpace(Node):
    """App Space."""

    icon = "azure/web/AppSpace.svg"
    service = "App Space"

class AppSpaceComponent(Node):
    """App Space Component."""

    icon = "azure/web/AppSpaceComponent.svg"
    service = "App Space Component"

class AppServices(Node):
    """App Service."""

    icon = "azure/web/AppServices.svg"
    service = "App Service"

class APIManagementServices(Node):
    """API Management."""

    icon = "azure/web/APIManagementServices.svg"
    service = "API Management"

class CognitiveSearch(Node):
    """AI Search."""

    icon = "azure/web/CognitiveSearch.svg"
    service = "AI Search"

class AppServiceEnvironments(Node):
    """App Service Environments."""

    icon = "azure/web/AppServiceEnvironments.svg"
    service = "App Service Environments"

class APIConnections(Node):
    """API Connections."""

    icon = "azure/web/APIConnections.svg"
    service = "API Connections"

class SignalR(Node):
    """SignalR."""

    icon = "azure/web/SignalR.svg"
    service = "SignalR"

class NotificationHubNamespaces(Node):
    """Notification Hub Namespaces."""

    icon = "azure/web/NotificationHubNamespaces.svg"
    service = "Notification Hub Namespaces"

class FrontDoorAndCDNProfiles(Node):
    """Front Door."""

    icon = "azure/web/FrontDoorAndCDNProfiles.svg"
    service = "Front Door"

class CognitiveServices(Node):
    """Cognitive Services."""

    icon = "azure/web/CognitiveServices.svg"
    service = "Cognitive Services"

class AzureMediaService(Node):
    """Azure Media Service."""

    icon = "azure/web/AzureMediaService.svg"
    service = "Azure Media Service"

class AzureSpringApps(Node):
    """Azure Spring Apps."""

    icon = "azure/web/AzureSpringApps.svg"
    service = "Azure Spring Apps"
