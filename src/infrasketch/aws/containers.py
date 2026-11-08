"""AWS resource nodes.

Generated from the AWS Architecture Icons.
The icons are Amazon Web Services artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/aws/LICENSE.txt.
Regenerate with tools/import_aws.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class AWSFargate(Node):
    """AWS Fargate."""

    icon = "aws/containers/AWSFargate.svg"
    service = "AWS Fargate"

class AmazonECSAnywhere(Node):
    """Amazon ECS Anywhere."""

    icon = "aws/containers/AmazonECSAnywhere.svg"
    service = "Amazon ECS Anywhere"

class AmazonEKSAnywhere(Node):
    """Amazon EKS Anywhere."""

    icon = "aws/containers/AmazonEKSAnywhere.svg"
    service = "Amazon EKS Anywhere"

class AmazonEKSDistro(Node):
    """Amazon EKS Distro."""

    icon = "aws/containers/AmazonEKSDistro.svg"
    service = "Amazon EKS Distro"

class AmazonElasticContainerRegistry(Node):
    """Amazon Elastic Container Registry."""

    icon = "aws/containers/AmazonElasticContainerRegistry.svg"
    service = "Amazon Elastic Container Registry"

class AmazonElasticContainerService(Node):
    """Amazon Elastic Container Service."""

    icon = "aws/containers/AmazonElasticContainerService.svg"
    service = "Amazon Elastic Container Service"

class AmazonElasticKubernetesService(Node):
    """Amazon Elastic Kubernetes Service."""

    icon = "aws/containers/AmazonElasticKubernetesService.svg"
    service = "Amazon Elastic Kubernetes Service"

class RedHatOpenShiftServiceOnAWS(Node):
    """Red Hat OpenShift Service On AWS."""

    icon = "aws/containers/RedHatOpenShiftServiceOnAWS.svg"
    service = "Red Hat OpenShift Service On AWS"
