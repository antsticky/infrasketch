import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram, Https, Node
from infrasketch.azure import AppService, ResourceGroup

OUT = Path(__file__).resolve().parent / "out" / "custom-icon.svg"
MARK = Path(__file__).resolve().parent / "assets" / "mark.png"

def main() -> str:
    with Diagram("Custom icon", OUT, subtitle="A PNG used as the resource icon") as diagram:
        billing = Node("Billing", icon=str(MARK), caption="Own service")
        with ResourceGroup("rg-app"):
            api = AppService("Orders API")
        billing >> Https() >> api
    return diagram.path

if __name__ == "__main__":
    print(main())
