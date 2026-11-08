"""Azure resources and the boundaries around them.

Every Azure icon is available, for example
``from infrasketch.azure.networking import Bastions``. Use
``python -m infrasketch search redis`` when you do not know the class.
"""

from infrasketch.azure.groups import (
    PrivateNetwork,
    Region,
    ResourceGroup,
    Subnet,
    Subscription,
    VNet,
)
from infrasketch.azure.shortcuts import *  # noqa: F403
from infrasketch.azure.shortcuts import __all__ as _resources

__all__ = [
    "PrivateNetwork",
    "Region",
    "ResourceGroup",
    "Subnet",
    "Subscription",
    "VNet",
    *_resources,
]
