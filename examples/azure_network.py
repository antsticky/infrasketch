"""A hub virtual network with a firewall, a private app, and a jump host.

    python examples/azure_network.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram, Https  # noqa: E402
from infrasketch.azure import (  # noqa: E402
    AppService,
    ApplicationGateway,
    Bastion,
    Firewall,
    ResourceGroup,
    Subnet,
    Users,
    VNet,
    VirtualMachine,
)

OUT = Path(__file__).resolve().parent / "out" / "azure-network.svg"


def main() -> str:
    with Diagram("Hub network", OUT, subtitle="Firewall, ingress, and administration") as diagram:
        people = Users("Operators")

        with ResourceGroup("rg-hub"):
            with VNet("vnet-hub"):
                with Subnet("AzureFirewallSubnet"):
                    firewall = Firewall("Hub")
                with Subnet("snet-app"):
                    gateway = ApplicationGateway("Ingress")
                    app = AppService("Internal app")
                with Subnet("AzureBastionSubnet"):
                    bastion = Bastion("Admin")
                with Subnet("snet-mgmt"):
                    jump = VirtualMachine("Jump host")

        people >> Https() >> firewall >> gateway >> app
        firewall >> bastion >> jump
    return diagram.path


if __name__ == "__main__":
    print(main())
