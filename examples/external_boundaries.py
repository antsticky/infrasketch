import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Cluster, DMZ, Diagram, Https, Namespace, Network, OnPremises, Private, Zone
from infrasketch.external import Cloudflare, Kubernetes, PostgreSQL, Prometheus

OUT = Path(__file__).resolve().parent / "out" / "external-boundaries.svg"


def main() -> str:
    with Diagram("Shop platform", OUT, subtitle="A public edge, a cluster, and the office") as diagram:
        with DMZ("Public edge"):
            edge = Cloudflare("Storefront")
        with OnPremises("Prague office"):
            with Zone("dc1"):
                with Network("lan", direction="TB"):
                    with Cluster("shop", direction="LR"):
                        with Namespace("orders"):
                            api = Kubernetes("API")
                        with Namespace("data"):
                            database = PostgreSQL("Orders")
                    metrics = Prometheus("Metrics")
        edge >> Https("Customers reach the API", 1) >> api
        api >> Private("The API reads orders", 2) >> database
        api >> Private() >> metrics
    return diagram.path


if __name__ == "__main__":
    print(main())
