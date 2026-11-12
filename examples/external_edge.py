"""Cloudflare and Akamai both reach the same API.

    python examples/external_edge.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram, Https  # noqa: E402
from infrasketch.azure import AppService, ResourceGroup  # noqa: E402
from infrasketch.external import Akamai, Cloudflare  # noqa: E402

OUT = Path(__file__).resolve().parent / "out" / "external-edge.svg"


def main() -> str:
    with Diagram("Edge providers", OUT, subtitle="Two networks in front of the API") as diagram:
        primary = Cloudflare("Primary")
        failover = Akamai("Failover")
        with ResourceGroup("rg-app"):
            api = AppService("Orders API")
        primary >> Https("Primary path", 1) >> api
        failover >> Https("Failover path", 2) >> api
    return diagram.path


if __name__ == "__main__":
    print(main())
