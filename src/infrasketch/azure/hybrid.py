"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class ArcKubernetes(Node):
    """Arc Kubernetes."""

    icon = "azure/hybrid/ArcKubernetes.svg"
    service = "Arc Kubernetes"

class WorkloadOrchestration(Node):
    """Workload Orchestration."""

    icon = "azure/hybrid/WorkloadOrchestration.svg"
    service = "Workload Orchestration"

class AzureOperator5GCore(Node):
    """Azure Operator 5G Core."""

    icon = "azure/hybrid/AzureOperator5GCore.svg"
    service = "Azure Operator 5G Core"

class AzureOperatorNexus(Node):
    """Azure Operator Nexus."""

    icon = "azure/hybrid/AzureOperatorNexus.svg"
    service = "Azure Operator Nexus"

class AzureOperatorInsights(Node):
    """Azure Operator Insights."""

    icon = "azure/hybrid/AzureOperatorInsights.svg"
    service = "Azure Operator Insights"

class AzureOperatorServiceManager(Node):
    """Azure Operator Service Manager."""

    icon = "azure/hybrid/AzureOperatorServiceManager.svg"
    service = "Azure Operator Service Manager"

class AzureProgrammableConnectivity(Node):
    """Azure Programmable Connectivity."""

    icon = "azure/hybrid/AzureProgrammableConnectivity.svg"
    service = "Azure Programmable Connectivity"

class AzureLocal(Node):
    """Azure Local."""

    icon = "azure/hybrid/AzureLocal.svg"
    service = "Azure Local"

class EdgeStorageAccelerator(Node):
    """Edge Storage Accelerator."""

    icon = "azure/hybrid/EdgeStorageAccelerator.svg"
    service = "Edge Storage Accelerator"

class AzureMonitorPipeline(Node):
    """Azure Monitor Pipeline."""

    icon = "azure/hybrid/AzureMonitorPipeline.svg"
    service = "Azure Monitor Pipeline"

class AIAtEdge(Node):
    """AI at Edge."""

    icon = "azure/hybrid/AIAtEdge.svg"
    service = "AI at Edge"
