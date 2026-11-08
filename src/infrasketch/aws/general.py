"""AWS resource nodes.

Generated from the AWS Architecture Icons.
The icons are Amazon Web Services artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/aws/LICENSE.txt.
Regenerate with tools/import_aws.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class AWSMarketplace(Node):
    """AWS Marketplace."""

    icon = "aws/general/AWSMarketplace.svg"
    service = "AWS Marketplace"

class Client(Node):
    """Client."""

    icon = "aws/general/Client.svg"
    service = "Client"

class Internet(Node):
    """Internet."""

    icon = "aws/general/Internet.svg"
    service = "Internet"

class MobileClient(Node):
    """Mobile Client."""

    icon = "aws/general/MobileClient.svg"
    service = "Mobile Client"

class User(Node):
    """User."""

    icon = "aws/general/User.svg"
    service = "User"

class Users(Node):
    """Users."""

    icon = "aws/general/Users.svg"
    service = "Users"
