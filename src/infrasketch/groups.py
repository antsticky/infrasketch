"""Boundaries that belong to neither Azure nor AWS."""

from __future__ import annotations

from infrasketch.model import Group


class OnPremises(Group):
    """A datacenter or office outside a public cloud."""

    kind = "on_premises"


class Cluster(Group):
    """A Kubernetes cluster. Put namespaces inside it."""

    kind = "cluster"


class Namespace(Group):
    """A namespace inside a cluster."""

    kind = "namespace"


class Network(Group):
    """A network that is neither a virtual network nor a VPC."""

    kind = "network"


class Zone(Group):
    """An availability zone."""

    kind = "zone"


class DMZ(Group):
    """A public edge in front of a private network."""

    kind = "dmz"
