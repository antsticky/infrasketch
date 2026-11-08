"""AWS resource nodes.

Generated from the AWS Architecture Icons.
The icons are Amazon Web Services artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/aws/LICENSE.txt.
Regenerate with tools/import_aws.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class AWSGroundStation(Node):
    """AWS Ground Station."""

    icon = "aws/satellite/AWSGroundStation.svg"
    service = "AWS Ground Station"
