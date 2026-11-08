"""Boundaries used on AWS architecture diagrams."""

from __future__ import annotations

from infrasketch.model import Group


class AWSCloud(Group):
    """An AWS Cloud boundary."""

    kind = "aws_cloud"


class Account(Group):
    """An AWS account."""

    kind = "aws_account"


class Region(Group):
    """An AWS region."""

    kind = "aws_region"


class VPC(Group):
    """A virtual private cloud. Put subnets inside it."""

    kind = "aws_vpc"


class PublicSubnet(Group):
    """A public subnet inside a VPC."""

    kind = "aws_public_subnet"


class PrivateSubnet(Group):
    """A private subnet inside a VPC."""

    kind = "aws_private_subnet"


class AutoScaling(Group):
    """An Auto Scaling group."""

    kind = "aws_autoscaling"
