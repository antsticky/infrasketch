"""A repository on GitHub deploys the API.

    python examples/external_github.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram, Https  # noqa: E402
from infrasketch.azure import AppService, ResourceGroup  # noqa: E402
from infrasketch.external import GitHub  # noqa: E402

OUT = Path(__file__).resolve().parent / "out" / "external-github.svg"


def main() -> str:
    with Diagram("Deploy from GitHub", OUT, subtitle="Source and the running API") as diagram:
        repo = GitHub("Orders", href="https://github.com")
        with ResourceGroup("rg-app"):
            api = AppService("Orders API")
        repo >> Https("GitHub Actions deploys the API", 1) >> api
    return diagram.path


if __name__ == "__main__":
    print(main())
