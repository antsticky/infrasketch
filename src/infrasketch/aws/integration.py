"""AWS resource nodes.

Generated from the AWS Architecture Icons.
The icons are Amazon Web Services artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/aws/LICENSE.txt.
Regenerate with tools/import_aws.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class AWSAppSync(Node):
    """AWS AppSync."""

    icon = "aws/integration/AWSAppSync.svg"
    service = "AWS AppSync"

class AWSB2BDataInterchange(Node):
    """AWS B2B Data Interchange."""

    icon = "aws/integration/AWSB2BDataInterchange.svg"
    service = "AWS B2B Data Interchange"

class AWSExpressWorkflows(Node):
    """AWS Express Workflows."""

    icon = "aws/integration/AWSExpressWorkflows.svg"
    service = "AWS Express Workflows"

class AWSStepFunctions(Node):
    """AWS Step Functions."""

    icon = "aws/integration/AWSStepFunctions.svg"
    service = "AWS Step Functions"

class AmazonAppFlow(Node):
    """Amazon AppFlow."""

    icon = "aws/integration/AmazonAppFlow.svg"
    service = "Amazon AppFlow"

class AmazonEventBridge(Node):
    """Amazon EventBridge."""

    icon = "aws/integration/AmazonEventBridge.svg"
    service = "Amazon EventBridge"

class AmazonMQ(Node):
    """Amazon MQ."""

    icon = "aws/integration/AmazonMQ.svg"
    service = "Amazon MQ"

class AmazonManagedWorkflowsForApacheAirflow(Node):
    """Amazon Managed Workflows For Apache Airflow."""

    icon = "aws/integration/AmazonManagedWorkflowsForApacheAirflow.svg"
    service = "Amazon Managed Workflows For Apache Airflow"

class AmazonSimpleNotificationService(Node):
    """Amazon Simple Notification Service."""

    icon = "aws/integration/AmazonSimpleNotificationService.svg"
    service = "Amazon Simple Notification Service"

class AmazonSimpleQueueService(Node):
    """Amazon Simple Queue Service."""

    icon = "aws/integration/AmazonSimpleQueueService.svg"
    service = "Amazon Simple Queue Service"
