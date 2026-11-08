"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class ServiceGroups(Node):
    """Service Groups."""

    icon = "azure/containers/ServiceGroups.svg"
    service = "Service Groups"

class AKSNetworkPolicy(Node):
    """AKS Network Policy."""

    icon = "azure/containers/AKSNetworkPolicy.svg"
    service = "AKS Network Policy"

class AzureRedHatOpenShift(Node):
    """Azure Red Hat OpenShift."""

    icon = "azure/containers/AzureRedHatOpenShift.svg"
    service = "Azure Red Hat OpenShift"

class KubernetesHub(Node):
    """Kubernetes Hub."""

    icon = "azure/containers/KubernetesHub.svg"
    service = "Kubernetes Hub"

class AzureContainerStorage(Node):
    """Azure Container Storage."""

    icon = "azure/containers/AzureContainerStorage.svg"
    service = "Azure Container Storage"

class KubernetesServices(Node):
    """Azure Kubernetes Service."""

    icon = "azure/containers/KubernetesServices.svg"
    service = "Azure Kubernetes Service"

class BatchAccounts(Node):
    """Batch Accounts."""

    icon = "azure/containers/BatchAccounts.svg"
    service = "Batch Accounts"

class AppServices(Node):
    """App Service."""

    icon = "azure/containers/AppServices.svg"
    service = "App Service"

class ServiceFabricClusters(Node):
    """Service Fabric Clusters."""

    icon = "azure/containers/ServiceFabricClusters.svg"
    service = "Service Fabric Clusters"

class ContainerInstances(Node):
    """Container Instance."""

    icon = "azure/containers/ContainerInstances.svg"
    service = "Container Instance"

class ContainerRegistries(Node):
    """Container Registry."""

    icon = "azure/containers/ContainerRegistries.svg"
    service = "Container Registry"
