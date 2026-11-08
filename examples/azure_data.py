"""A nightly pipeline from events into a lake and a database.

    python examples/azure_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Async, Diagram  # noqa: E402
from infrasketch.azure import (  # noqa: E402
    BlobStorage,
    DataFactory,
    EventHub,
    KeyVault,
    LogicApp,
    ResourceGroup,
    SQLDatabase,
)

OUT = Path(__file__).resolve().parent / "out" / "azure-data.svg"


def main() -> str:
    with Diagram("Data pipeline", OUT, subtitle="Ingest, transform, and store") as diagram:
        events = EventHub("Telemetry")

        with ResourceGroup("rg-data", arrange="row"):
            trigger = LogicApp("Schedule")
            factory = DataFactory("Nightly")
            lake = BlobStorage("Raw")
            warehouse = SQLDatabase("Curated")
            vault = KeyVault("Connections")

        events >> Async("ingest") >> factory
        trigger >> factory
        factory >> lake
        factory >> warehouse
        factory >> vault
    return diagram.path


if __name__ == "__main__":
    print(main())
