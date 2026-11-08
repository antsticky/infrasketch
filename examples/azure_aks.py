"""AKS with a registry, private data, and platform services beside the cluster.

    python examples/azure_aks.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Async, Diagram, Private  # noqa: E402
from infrasketch.azure import (  # noqa: E402
    ACR,
    AKS,
    ApplicationGateway,
    ApplicationInsights,
    FrontDoor,
    KeyVault,
    ManagedRedis,
    PostgreSQL,
    PrivateNetwork,
    ResourceGroup,
    Subnet,
    Users,
    VNet,
)

OUT = Path(__file__).resolve().parent / "out" / "azure-aks.svg"


def main() -> str:
    with Diagram("AKS platform", OUT, subtitle="Cluster, registry, and private data") as diagram:
        users = Users("Customers")

        with ResourceGroup("rg-edge"):
            door = FrontDoor("Global entry")

        with ResourceGroup("rg-runtime"):
            registry = ACR("Platform images")
            with VNet("vnet-aks"):
                with Subnet("snet-ingress"):
                    gateway = ApplicationGateway("Ingress")
                with Subnet("snet-cluster"):
                    cluster = AKS("prod")
                with PrivateNetwork("data"):
                    cache = ManagedRedis("Cache")
                    database = PostgreSQL("App data")
            vault = KeyVault("Cluster secrets")
            insights = ApplicationInsights("Workloads")

        users >> door >> gateway >> cluster
        registry >> Async("pull") >> cluster
        cluster >> cache
        cluster >> Private() >> database
        cluster >> vault
        cluster >> insights
    return diagram.path


if __name__ == "__main__":
    print(main())
