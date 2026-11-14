import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aws_decisions import main as aws_decisions
from aws_eks import main as aws_eks
from aws_events import main as aws_events
from aws_orders import main as aws_orders
from azure_ai import main as azure_ai
from azure_aks import main as azure_aks
from azure_container_apps import main as azure_container_apps
from azure_data import main as azure_data
from azure_decisions import main as azure_decisions
from azure_folded import main as azure_folded
from azure_functions import main as azure_functions
from azure_grid import main as azure_grid
from custom_icon import main as custom_icon
from azure_network import main as azure_network
from azure_web_api import main as azure_web_api
from external_boundaries import main as external_boundaries
from external_edge import main as external_edge
from external_github import main as external_github

def main() -> None:
    for render in (
        azure_web_api,
        azure_container_apps,
        azure_functions,
        azure_aks,
        azure_ai,
        azure_data,
        azure_grid,
        custom_icon,
        azure_network,
        azure_decisions,
        azure_folded,
        aws_orders,
        aws_eks,
        aws_events,
        aws_decisions,
        external_github,
        external_edge,
        external_boundaries,
    ):
        print(render())

if __name__ == "__main__":
    main()
