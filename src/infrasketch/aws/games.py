"""AWS resource nodes.

Generated from the AWS Architecture Icons.
The icons are Amazon Web Services artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/aws/LICENSE.txt.
Regenerate with tools/import_aws.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class AmazonGameLiftServers(Node):
    """Amazon GameLift Servers."""

    icon = "aws/games/AmazonGameLiftServers.svg"
    service = "Amazon GameLift Servers"

class AmazonGameLiftStreams(Node):
    """Amazon GameLift Streams."""

    icon = "aws/games/AmazonGameLiftStreams.svg"
    service = "Amazon GameLift Streams"

class Open3DEngine(Node):
    """Open 3D Engine."""

    icon = "aws/games/Open3DEngine.svg"
    service = "Open 3D Engine"
