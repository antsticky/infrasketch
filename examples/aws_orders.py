import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram
from infrasketch.aws import (
    APIGateway,
    CloudFront,
    DynamoDB,
    Lambda,
    PrivateSubnet,
    PublicSubnet,
    S3,
    Users,
    VPC,
)

OUT = Path(__file__).resolve().parent / "out" / "aws-orders.svg"

def main() -> str:
    with Diagram("Orders", OUT, subtitle="Production · eu-west-1") as diagram:
        customers = Users("Customers")
        edge = CloudFront("Entry")
        with VPC("vpc-orders"):
            with PublicSubnet("public"):
                api = APIGateway("Orders")
            with PrivateSubnet("data"):
                checkout = Lambda("Checkout")
                orders = DynamoDB("Orders")
                images = S3("Images")
        customers >> edge >> api >> checkout
        checkout >> [orders, images]
    return diagram.path

if __name__ == "__main__":
    print(main())
