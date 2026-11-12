import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram, Https, Private
from infrasketch.azure import (
    AppService,
    FrontDoor,
    KeyVault,
    PrivateNetwork,
    Redis,
    ResourceGroup,
    SQLDatabase,
    StaticWebApp,
    Subnet,
    Users,
    VNet,
)

OUT = Path(__file__).resolve().parent / "out" / "azure-web-api.svg"

def main() -> str:
    with Diagram("Web, API, and Redis", OUT, subtitle="Production · West Europe") as diagram:
        customers = Users("Customers")

        with ResourceGroup("rg-edge"):
            door = FrontDoor("Storefront entry")

        with ResourceGroup("rg-app"):
            with VNet("vnet-app"):
                with Subnet("snet-web"):
                    web = StaticWebApp("Storefront")
                with Subnet("snet-api"):
                    api = AppService("Orders API")
                with PrivateNetwork("data"):
                    cache = Redis("Sessions")
                    database = SQLDatabase("Orders")
                    vault = KeyVault("Secrets")

        customers >> Https() >> door >> Https() >> web >> api
        api >> cache
        api >> database
        api >> Private("secrets") >> vault
    return diagram.path

if __name__ == "__main__":
    print(main())
