"""An HTTP API that hands work to functions through Service Bus.

    python examples/functions_events.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import (  # noqa: E402
    APIManagement,
    ApplicationInsights,
    Async,
    BlobStorage,
    CosmosDB,
    Diagram,
    EventHub,
    FunctionApp,
    Https,
    KeyVault,
    LogAnalytics,
    ManagedIdentity,
    Monitor,
    ResourceGroup,
    ServiceBus,
    Users,
)

OUT = Path(__file__).resolve().parent / "out" / "functions-events.svg"


def main() -> str:
    with Diagram("Event-driven functions", OUT, subtitle="API, queue, and data") as diagram:
        callers = Users("Partners")

        with ResourceGroup("rg-integration"):
            gateway = APIManagement("Public API")
            orders = FunctionApp("Orders")
            worker = FunctionApp("Fulfillment")
            bus = ServiceBus("orders")
            events = EventHub("Telemetry")

        with ResourceGroup("rg-data", arrange="row"):
            catalog = CosmosDB("Catalog")
            documents = BlobStorage("Invoices")
            identity = ManagedIdentity("Workload")
            vault = KeyVault("Keys")

        with ResourceGroup("rg-observe"):
            insights = ApplicationInsights("API")
            logs = LogAnalytics("Workspace")
            monitor = Monitor("Alerts")

        callers >> Https() >> gateway >> orders
        orders >> Async("enqueue") >> bus >> worker
        orders >> catalog
        worker >> documents
        worker >> events
        orders >> identity
        worker >> identity
        identity >> vault
        orders >> insights
        worker >> insights
        insights >> logs >> monitor
    return diagram.path


if __name__ == "__main__":
    print(main())
