import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram, Group, Https, Private
from infrasketch.aws import APIGateway, CloudWatch, Lambda, SecretsManager, Users, VPC

OUT = Path(__file__).resolve().parent / "out" / "aws-decisions.svg"

API = "https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html"
LAMBDA = "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html"
SECRETS = "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html"

def main() -> str:
    with Diagram(
        "Orders review",
        OUT,
        subtitle="Decisions for the production design",
        as_of=date(2026, 11, 12),
    ) as diagram:
        customers = Users("Customers", note="Public internet")
        with VPC("vpc-orders", region="eu-west-1", note="Production account"):
            api = APIGateway(
                "Orders",
                sku="HTTP API",
                public=True,
                href=API,
            )
            checkout = Lambda(
                "Checkout",
                sku="512 MB",
                region="eu-west-1",
                public=False,
                note="VPC only, no function URL",
                href=LAMBDA,
            )
            secrets = SecretsManager(
                "Keys",
                public=False,
                note="Rotation every 30 days",
                href=SECRETS,
            )
        with Group("Observability", folded=True, foldable=True, note="Shown closed"):
            metrics = CloudWatch("Metrics")
            CloudWatch("Alarms")
        customers >> Https("Customers call the API", 1) >> api
        api >> Https("API Gateway invokes checkout", 2) >> checkout
        checkout >> Private("Checkout reads the keys", 3) >> secrets
        checkout >> Private("Checkout emits metrics", 4) >> metrics
    return diagram.path

if __name__ == "__main__":
    print(main())
