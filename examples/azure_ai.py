"""An assistant app in front of Azure OpenAI and AI Search.

    python examples/azure_ai.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram, Https, Private  # noqa: E402
from infrasketch.azure import (  # noqa: E402
    AISearch,
    AppService,
    AzureOpenAI,
    BlobStorage,
    KeyVault,
    PrivateNetwork,
    ResourceGroup,
    StaticWebApp,
    Subnet,
    Users,
    VNet,
)

OUT = Path(__file__).resolve().parent / "out" / "azure-ai.svg"


def main() -> str:
    with Diagram("AI assistant", OUT, subtitle="Search, a model, and the source documents") as diagram:
        people = Users("Analysts")

        with ResourceGroup("rg-ai"):
            site = StaticWebApp("Assistant")
            with VNet("vnet-ai"):
                with Subnet("snet-api"):
                    api = AppService("Chat API")
                with PrivateNetwork("private"):
                    search = AISearch("Documents")
                    model = AzureOpenAI("gpt")
                    corpus = BlobStorage("Corpus")
                    vault = KeyVault("Keys")

        people >> Https() >> site >> api
        api >> search
        api >> model
        api >> corpus
        api >> Private("secrets") >> vault
    return diagram.path


if __name__ == "__main__":
    print(main())
