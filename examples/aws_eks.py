import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Diagram
from infrasketch.aws import (
    ECR,
    EKS,
    ELB,
    ElastiCache,
    PrivateSubnet,
    PublicSubnet,
    RDS,
    Users,
    VPC,
)

OUT = Path(__file__).resolve().parent / "out" / "aws-eks.svg"

def main() -> str:
    with Diagram("EKS platform", OUT, subtitle="Cluster, registry, and private data") as diagram:
        users = Users("Customers")
        registry = ECR("Images")
        with VPC("vpc-prod"):
            with PublicSubnet("public"):
                balancer = ELB("Ingress")
            with PrivateSubnet("cluster"):
                cluster = EKS("prod")
            with PrivateSubnet("data"):
                cache = ElastiCache("Cache")
                database = RDS("App data")
        users >> balancer >> cluster
        registry >> cluster
        cluster >> cache
        cluster >> database
    return diagram.path

if __name__ == "__main__":
    print(main())
