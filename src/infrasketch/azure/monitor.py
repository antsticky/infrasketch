"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class Monitor(Node):
    """Azure Monitor."""

    icon = "azure/monitor/Monitor.svg"
    service = "Azure Monitor"

class ActivityLog(Node):
    """Activity Log."""

    icon = "azure/monitor/ActivityLog.svg"
    service = "Activity Log"

class DiagnosticsSettings(Node):
    """Diagnostics Settings."""

    icon = "azure/monitor/DiagnosticsSettings.svg"
    service = "Diagnostics Settings"

class LogAnalyticsWorkspaces(Node):
    """Log Analytics."""

    icon = "azure/monitor/LogAnalyticsWorkspaces.svg"
    service = "Log Analytics"

class ApplicationInsights(Node):
    """Application Insights."""

    icon = "azure/monitor/ApplicationInsights.svg"
    service = "Application Insights"

class Metrics(Node):
    """Metrics."""

    icon = "azure/monitor/Metrics.svg"
    service = "Metrics"

class AzureMonitorsForSAPSolutions(Node):
    """Azure Monitors for SAP Solutions."""

    icon = "azure/monitor/AzureMonitorsForSAPSolutions.svg"
    service = "Azure Monitors for SAP Solutions"

class ChangeAnalysis(Node):
    """Change Analysis."""

    icon = "azure/monitor/ChangeAnalysis.svg"
    service = "Change Analysis"

class AzureWorkbooks(Node):
    """Azure Workbooks."""

    icon = "azure/monitor/AzureWorkbooks.svg"
    service = "Azure Workbooks"

class NetworkWatcher(Node):
    """Network Watcher."""

    icon = "azure/monitor/NetworkWatcher.svg"
    service = "Network Watcher"

class AutoScale(Node):
    """Auto Scale."""

    icon = "azure/monitor/AutoScale.svg"
    service = "Auto Scale"
