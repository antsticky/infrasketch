"""Common AWS resources and the boundaries around them.

Every architecture-service icon is available, for example
``from infrasketch.aws.compute import AWSLambda``. Use
``python -m infrasketch search aws lambda`` when you do not know the class.
"""

from infrasketch.aws.groups import (
    AWSCloud,
    Account,
    AutoScaling,
    PrivateSubnet,
    PublicSubnet,
    Region,
    VPC,
)
from infrasketch.aws.networking import AmazonAPIGateway as APIGateway
from infrasketch.aws.analytics import AmazonAthena as Athena
from infrasketch.aws.databases import AmazonAurora as Aurora
from infrasketch.aws.ai import AmazonBedrock as Bedrock
from infrasketch.aws.general import Client
from infrasketch.aws.networking import AmazonCloudFront as CloudFront
from infrasketch.aws.management import AmazonCloudWatch as CloudWatch
from infrasketch.aws.security import AmazonCognito as Cognito
from infrasketch.aws.databases import AmazonDynamoDB as DynamoDB
from infrasketch.aws.compute import AmazonEC2 as EC2
from infrasketch.aws.containers import AmazonElasticContainerRegistry as ECR
from infrasketch.aws.containers import AmazonElasticContainerService as ECS
from infrasketch.aws.containers import AmazonElasticKubernetesService as EKS
from infrasketch.aws.networking import ElasticLoadBalancing as ELB
from infrasketch.aws.databases import AmazonElastiCache as ElastiCache
from infrasketch.aws.integration import AmazonEventBridge as EventBridge
from infrasketch.aws.containers import AWSFargate as Fargate
from infrasketch.aws.analytics import AWSGlue as Glue
from infrasketch.aws.security import AWSIdentityAndAccessManagement as IAM
from infrasketch.aws.general import Internet
from infrasketch.aws.networking import AmazonVPCInternetGateway as InternetGateway
from infrasketch.aws.analytics import AmazonKinesis as Kinesis
from infrasketch.aws.compute import AWSLambda as Lambda
from infrasketch.aws.analytics import AmazonOpenSearchService as OpenSearch
from infrasketch.aws.databases import AmazonRDS as RDS
from infrasketch.aws.analytics import AmazonRedshift as Redshift
from infrasketch.aws.networking import AmazonRoute53 as Route53
from infrasketch.aws.storage import AmazonSimpleStorageService as S3
from infrasketch.aws.integration import AmazonSimpleNotificationService as SNS
from infrasketch.aws.integration import AmazonSimpleQueueService as SQS
from infrasketch.aws.analytics import AmazonSageMaker as SageMaker
from infrasketch.aws.security import AWSSecretsManager as SecretsManager
from infrasketch.aws.integration import AWSStepFunctions as StepFunctions
from infrasketch.aws.general import User
from infrasketch.aws.general import Users
from infrasketch.aws.security import AWSWAF as WAF

__all__ = [
    "AWSCloud",
    "Account",
    "AutoScaling",
    "PrivateSubnet",
    "PublicSubnet",
    "Region",
    "VPC",
    "APIGateway",
    "Athena",
    "Aurora",
    "Bedrock",
    "Client",
    "CloudFront",
    "CloudWatch",
    "Cognito",
    "DynamoDB",
    "EC2",
    "ECR",
    "ECS",
    "EKS",
    "ELB",
    "ElastiCache",
    "EventBridge",
    "Fargate",
    "Glue",
    "IAM",
    "Internet",
    "InternetGateway",
    "Kinesis",
    "Lambda",
    "OpenSearch",
    "RDS",
    "Redshift",
    "Route53",
    "S3",
    "SNS",
    "SQS",
    "SageMaker",
    "SecretsManager",
    "StepFunctions",
    "User",
    "Users",
    "WAF",
]
