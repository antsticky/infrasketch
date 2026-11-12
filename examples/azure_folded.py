import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram, Https, Private
from infrasketch.azure import (
    AppService,
    ApplicationInsights,
    LogAnalytics,
    Monitor,
    Redis,
    ResourceGroup,
    Users,
)

OUT = Path(__file__).resolve().parent / "out" / "azure-folded.svg"

def main() -> str:
    with Diagram("Orders, with observability closed", OUT, subtitle="The API is open. Monitoring stays folded.") as diagram:
        customers = Users("Customers")
        with ResourceGroup("rg-app"):
            api = AppService("Orders API")
            cache = Redis("Sessions")
        with ResourceGroup("rg-observe", folded=True, foldable=True, note="Click to open"):
            alerts = Monitor("Alerts")
            LogAnalytics("Workspace")
            ApplicationInsights("Workloads")
        customers >> Https() >> api
        api >> cache
        api >> Private("The API reports failures") >> alerts
    return diagram.path

if __name__ == "__main__":
    print(main())
