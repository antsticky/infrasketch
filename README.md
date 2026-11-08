# infrasketch

Draw Azure and AWS architecture diagrams as SVG. The package uses the official
resource icons and lays the diagram out itself, so Graphviz is not required.

```python
from infrasketch import Diagram
from infrasketch.azure import FrontDoor, FunctionApp, Redis, ResourceGroup

with Diagram("Orders", "orders.svg"):
    with ResourceGroup("rg-app"):
        web = FrontDoor("Frontend")
        api = FunctionApp("API")
        cache = Redis("Sessions")
    web >> api >> cache
```

That writes `orders.svg` when the block ends. The icon says which service it
is. The label is your name for that piece of the system, and the caption under
it is the service name.

Azure resources come from `infrasketch.azure`. AWS resources come from `infrasketch.aws`:

```python
from infrasketch import Diagram
from infrasketch.aws import APIGateway, CloudFront, DynamoDB, Lambda, S3, Users, VPC

with Diagram("Orders", "orders.svg"):
    with VPC("vpc-orders"):
        api = APIGateway("Orders")
        checkout = Lambda("Checkout")
        orders = DynamoDB("Orders")
        images = S3("Images")
    Users("Customers") >> CloudFront("Entry") >> api >> checkout
    checkout >> [orders, images]
```

## Install

```bash
pip install infrasketch
```

## Documentation

The guide and the searchable icon browser are published at
[antsticky.github.io/infrasketch](https://antsticky.github.io/infrasketch/).

## Draw a diagram

Resources only exist inside a diagram. Groups are context managers too, so the
indentation is the architecture:

```python
from infrasketch import Diagram, Https, Private
from infrasketch.azure import (
    ResourceGroup, VNet, Subnet, PrivateNetwork,
    Users, FrontDoor, StaticWebApp, AppService, Redis, SQLDatabase, KeyVault,
)

with Diagram("Web, API, and Redis", "platform.svg", subtitle="Production · West Europe"):
    customers = Users("Customers")
    with ResourceGroup("rg-edge"):
        door = FrontDoor("Entry")
    with ResourceGroup("rg-app"):
        with VNet("vnet-app"):
            with Subnet("snet-web"):
                web = StaticWebApp("Storefront")
            with Subnet("snet-api"):
                api = AppService("Orders API")
            with PrivateNetwork("data"):
                cache = Redis("Sessions")
                database = SQLDatabase("Orders")
                vault = KeyVault("Secrets")

    customers >> Https() >> door >> web >> api
    api >> [cache, database]
    api >> Private("secrets") >> vault
```

`direction="TB"` flows top to bottom. `spacing` is `"compact"`, `"regular"`,
or `"relaxed"`. Pass `autosave=False` when you want the SVG string yourself:

```python
with Diagram("Orders", autosave=False) as diagram:
    ...
svg = diagram.svg()
diagram.save("orders.svg")
```

## Connectors

| Code | Result |
| --- | --- |
| `a >> b` | Arrow from a to b |
| `a >> [b, c]` | Arrow from a to each target |
| `[a, b] >> c` | Arrow from each source to c |
| `a << b` | Arrow pointing back at a |
| `a - b` | Line with no arrowhead |
| `a >> Edge("SQL", style="dashed") >> b` | Labelled connector |
| `a >> Https() >> b` | Azure-blue HTTPS |
| `a >> Async("enqueue") >> b` | Dashed queue or event |
| `a >> Private() >> b` | Dashed Private Link |

`style` is `"solid"`, `"dashed"`, or `"dotted"`. `color` is a hex color such
as `"#0078D4"`.

## Boundaries

| Group | Use it for |
| --- | --- |
| `Subscription("sub")` | A subscription |
| `ResourceGroup("rg-app")` | A resource group |
| `Region("West Europe")` | A region |
| `VNet("vnet-app")` | A virtual network |
| `Subnet("snet-api")` | A subnet |
| `PrivateNetwork("data")` | Private endpoints or Private Link |
| `Group("Workers")` | Anything else |

Inside a boundary, connected resources flow in the diagram direction.
Resources at the same step stack, which is what you want for a cache beside
its database. `arrange="row"` forces a single row, `arrange="column"` a
single column, and `arrange="grid"` with `columns=3` a grid.

## Finding an icon

Common Azure names, imported from `infrasketch.azure`: `FunctionApp`,
`ContainerApp`, `ACR`, `AKS`, `Redis`, `ManagedRedis`, `SQLDatabase`,
`CosmosDB`, `PostgreSQL`, `StorageAccount`, `KeyVault`, `FrontDoor`,
`ApplicationGateway`, `ServiceBus`, `StaticWebApp`.

Common AWS names, imported from `infrasketch.aws`: `Lambda`, `EC2`, `S3`,
`DynamoDB`, `APIGateway`, `CloudFront`, `SQS`, `EKS`.

Search when you need the rest:

```bash
python -m infrasketch search private endpoint
python -m infrasketch search container registry
python -m infrasketch categories
```

```python
from infrasketch import search

for hit in search("cosmos"):
    print(hit.import_line)
```

```python
from infrasketch.azure.networking import Bastions
from infrasketch.aws.compute import AWSLambda
```

`FunctionApp("Orders")` labels the box "Orders" and captions it "Function App".
`FunctionApp()` uses the service name as the only label. `caption=False` hides
the caption.

A resource with no icon draws a neutral placeholder. Pass `icon="path/to.svg"`
to use your own artwork. Azure icons are never recoloured or stretched.

## Examples

| Script | What it shows |
| --- | --- |
| `examples/azure_web_api.py` | Front Door, static web app, API, Redis, SQL, Key Vault |
| `examples/azure_container_apps.py` | ACR, Container Apps, private endpoints |
| `examples/azure_functions.py` | API Management, functions, Service Bus, Cosmos DB, storage |
| `examples/azure_aks.py` | AKS, ACR, PostgreSQL, managed Redis |
| `examples/azure_ai.py` | Static web app, Azure OpenAI, AI Search, storage |
| `examples/azure_data.py` | Event Hubs, Logic Apps, Data Factory, SQL |
| `examples/azure_network.py` | Firewall, Application Gateway, Bastion, a jump host |
| `examples/aws_orders.py` | CloudFront, API Gateway, Lambda, DynamoDB, and S3 in a VPC |
| `examples/aws_eks.py` | EKS, a registry, ElastiCache, and RDS |
| `examples/aws_events.py` | API Gateway, Lambda, SQS, DynamoDB, and S3 |

![Web, API, and Redis](examples/out/azure-web-api.svg)

![Orders on AWS](examples/out/aws-orders.svg)

## License

The package license expression is
`MIT AND LicenseRef-Microsoft-Azure-Architecture-Icons AND LicenseRef-AWS-Architecture-Icons`.

The Python code is MIT. See `LICENSE`.

The SVG files in `src/infrasketch/data/icons` are official cloud artwork. They
are not MIT. Azure icons are `LicenseRef-Microsoft-Azure-Architecture-Icons`.
AWS icons, under `src/infrasketch/data/icons/aws`, are
`LicenseRef-AWS-Architecture-Icons`. Microsoft allows the Azure icons in
architecture diagrams, training materials, and documentation. AWS allows
customers and partners to use the AWS icons in architecture diagrams, and in
whitepapers, presentations, datasheets, and posters. Do not use either set as
a logo or to represent your own product. The terms travel with the files in
`NOTICE`, `src/infrasketch/data/icons/LICENSE.txt`, and
`src/infrasketch/data/icons/aws/LICENSE.txt`.
