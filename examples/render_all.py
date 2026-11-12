"""Render every example into examples/out."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aws_decisions import main as aws_decisions  # noqa: E402
from aws_eks import main as aws_eks  # noqa: E402
from aws_events import main as aws_events  # noqa: E402
from aws_orders import main as aws_orders  # noqa: E402
from azure_ai import main as azure_ai  # noqa: E402
from azure_aks import main as azure_aks  # noqa: E402
from azure_container_apps import main as azure_container_apps  # noqa: E402
from azure_data import main as azure_data  # noqa: E402
from azure_decisions import main as azure_decisions  # noqa: E402
from azure_functions import main as azure_functions  # noqa: E402
from azure_network import main as azure_network  # noqa: E402
from azure_web_api import main as azure_web_api  # noqa: E402


def main() -> None:
    for render in (
        azure_web_api,
        azure_container_apps,
        azure_functions,
        azure_aks,
        azure_ai,
        azure_data,
        azure_network,
        azure_decisions,
        aws_orders,
        aws_eks,
        aws_events,
        aws_decisions,
    ):
        print(render())


if __name__ == "__main__":
    main()
