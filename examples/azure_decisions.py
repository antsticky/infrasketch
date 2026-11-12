"""A reviewed Azure design: SKU, exposure, notes, a date, and a folded group.

    python examples/azure_decisions.py
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram, Https, Private  # noqa: E402
from infrasketch.azure import (  # noqa: E402
    AppService,
    FrontDoor,
    KeyVault,
    LogAnalytics,
    Monitor,
    ResourceGroup,
    Users,
)

OUT = Path(__file__).resolve().parent / "out" / "azure-decisions.svg"

FRONT_DOOR = "https://learn.microsoft.com/azure/frontdoor/front-door-overview"
APP_SERVICE = "https://learn.microsoft.com/azure/app-service/overview"
KEY_VAULT = "https://learn.microsoft.com/azure/key-vault/general/overview"


def main() -> str:
    with Diagram(
        "Orders review",
        OUT,
        subtitle="Decisions for the production design",
        as_of=date(2026, 11, 12),
    ) as diagram:
        customers = Users("Customers", note="Public internet")
        with ResourceGroup("rg-app", region="West Europe", note="Production workload"):
            door = FrontDoor(
                "Entry",
                sku="Premium",
                public=True,
                href=FRONT_DOOR,
            )
            api = AppService(
                "Orders API",
                sku="P1v3",
                region="West Europe",
                public=False,
                note="Private endpoint only",
                href=APP_SERVICE,
            )
            vault = KeyVault(
                "Secrets",
                sku="Standard",
                public=False,
                note="RBAC, no public network",
                href=KEY_VAULT,
            )
        with ResourceGroup("rg-observe", folded=True, note="Shown closed"):
            alerts = Monitor("Alerts")
            LogAnalytics("Workspace")
        customers >> Https("Customers open the storefront", 1) >> door
        door >> Https("Front Door calls the API", 2) >> api
        api >> Private("The API reads secrets", 3) >> vault
        api >> Private("The API reports failures", 4) >> alerts
    return diagram.path


if __name__ == "__main__":
    print(main())
