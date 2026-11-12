import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram
from infrasketch.azure import (
    AppService,
    ApplicationInsights,
    KeyVault,
    LogAnalytics,
    Monitor,
    ResourceGroup,
    StorageAccount,
)

OUT = Path(__file__).resolve().parent / "out" / "azure-grid.svg"

def main() -> str:
    with Diagram("Shared services", OUT, subtitle="A grid of three columns") as diagram:
        api = AppService("Orders API")
        with ResourceGroup("rg-shared", arrange="grid", columns=3):
            vault = KeyVault("Keys")
            StorageAccount("Files")
            Monitor("Health")
            LogAnalytics("Logs")
            ApplicationInsights("Traces")
        api >> vault
    return diagram.path

if __name__ == "__main__":
    print(main())
