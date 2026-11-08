"""Boundaries used on Azure architecture diagrams."""

from __future__ import annotations

from infrasketch.model import Group


class ResourceGroup(Group):
    """An Azure resource group."""

    kind = "resource_group"


class Subscription(Group):
    """An Azure subscription."""

    kind = "subscription"


class Region(Group):
    """An Azure region."""

    kind = "region"


class VNet(Group):
    """A virtual network. Put subnets inside it."""

    kind = "vnet"


class Subnet(Group):
    """A subnet inside a virtual network."""

    kind = "subnet"


class PrivateNetwork(Group):
    """A private-link or private-endpoint boundary."""

    kind = "private"
