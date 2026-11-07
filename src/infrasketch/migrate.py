"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class CostManagementAndBilling(Node):
    """Cost Management and Billing."""

    icon = "migrate/CostManagementAndBilling.svg"
    service = "Cost Management and Billing"

class RecoveryServicesVaults(Node):
    """Recovery Services Vaults."""

    icon = "migrate/RecoveryServicesVaults.svg"
    service = "Recovery Services Vaults"

class AzureDataboxGateway(Node):
    """Azure Databox Gateway."""

    icon = "migrate/AzureDataboxGateway.svg"
    service = "Azure Databox Gateway"

class DataBox(Node):
    """Data Box."""

    icon = "migrate/DataBox.svg"
    service = "Data Box"

class AzureMigrate(Node):
    """Azure Migrate."""

    icon = "migrate/AzureMigrate.svg"
    service = "Azure Migrate"
