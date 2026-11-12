import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Async, Diagram, Private
from infrasketch.azure import (
    ACR,
    ApplicationGateway,
    ContainerApp,
    ContainerAppsEnvironment,
    ManagedRedis,
    PrivateEndpoint,
    PrivateNetwork,
    ResourceGroup,
    SQLDatabase,
    Subnet,
    Users,
    VNet,
)

OUT = Path(__file__).resolve().parent / "out" / "azure-container-apps.svg"

def main() -> str:
    with Diagram(
        "Container Apps platform",
        OUT,
        subtitle="Images, private endpoints, and a shared environment",
    ) as diagram:
        clients = Users("Clients")

        with ResourceGroup("rg-platform"):
            registry = ACR("Images")

            with VNet("vnet-prod"):
                with Subnet("snet-ingress"):
                    gateway = ApplicationGateway("Ingress")
                with Subnet("snet-apps", arrange="column"):
                    environment = ContainerAppsEnvironment("cae-prod")
                    frontend = ContainerApp("Frontend")
                    backend = ContainerApp("Backend")
                with PrivateNetwork("private endpoints"):
                    redis_pe = PrivateEndpoint("Redis")
                    sql_pe = PrivateEndpoint("SQL")

            cache = ManagedRedis("Cart")
            database = SQLDatabase("Catalog")

        clients >> gateway >> frontend
        frontend >> backend
        registry >> Async("pull") >> environment
        backend >> Private() >> redis_pe >> cache
        backend >> Private() >> sql_pe >> database
    return diagram.path

if __name__ == "__main__":
    print(main())
