"""Render every example into examples/out."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aks_platform import main as aks  # noqa: E402
from container_apps import main as containers  # noqa: E402
from functions_events import main as functions  # noqa: E402
from web_api_redis import main as web  # noqa: E402


def main() -> None:
    for render in (web, containers, functions, aks):
        print(render())


if __name__ == "__main__":
    main()
