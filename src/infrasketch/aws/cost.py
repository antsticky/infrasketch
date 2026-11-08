"""AWS resource nodes.

Generated from the AWS Architecture Icons.
The icons are Amazon Web Services artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/aws/LICENSE.txt.
Regenerate with tools/import_aws.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class AWSBillingConductor(Node):
    """AWS Billing Conductor."""

    icon = "aws/cost/AWSBillingConductor.svg"
    service = "AWS Billing Conductor"

class AWSBudgets(Node):
    """AWS Budgets."""

    icon = "aws/cost/AWSBudgets.svg"
    service = "AWS Budgets"

class AWSCostAndUsageReport(Node):
    """AWS Cost And Usage Report."""

    icon = "aws/cost/AWSCostAndUsageReport.svg"
    service = "AWS Cost And Usage Report"

class AWSCostExplorer(Node):
    """AWS Cost Explorer."""

    icon = "aws/cost/AWSCostExplorer.svg"
    service = "AWS Cost Explorer"

class AWSFinOpsAgent(Node):
    """AWS FinOps Agent."""

    icon = "aws/cost/AWSFinOpsAgent.svg"
    service = "AWS FinOps Agent"

class ReservedInstanceReporting(Node):
    """Reserved Instance Reporting."""

    icon = "aws/cost/ReservedInstanceReporting.svg"
    service = "Reserved Instance Reporting"

class SavingsPlans(Node):
    """Savings Plans."""

    icon = "aws/cost/SavingsPlans.svg"
    service = "Savings Plans"
