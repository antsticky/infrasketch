import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrasketch import Async, Diagram
from infrasketch.aws import (
    APIGateway,
    CloudWatch,
    DynamoDB,
    Lambda,
    S3,
    SQS,
    Users,
)

OUT = Path(__file__).resolve().parent / "out" / "aws-events.svg"

def main() -> str:
    with Diagram("Event-driven functions", OUT, subtitle="API, queue, and data") as diagram:
        callers = Users("Partners")
        gateway = APIGateway("Public API")
        orders = Lambda("Orders")
        queue = SQS("orders")
        worker = Lambda("Fulfillment")
        catalog = DynamoDB("Catalog")
        documents = S3("Invoices")
        logs = CloudWatch("Logs")

        callers >> gateway >> orders
        orders >> Async("enqueue") >> queue >> worker >> documents
        orders >> catalog
        worker >> logs
    return diagram.path

if __name__ == "__main__":
    print(main())
