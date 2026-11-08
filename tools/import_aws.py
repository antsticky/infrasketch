"""Copy the official AWS Architecture Icons into the package.

Download Icon-package from https://aws.amazon.com/architecture/icons/
and pass the zip, or leave .aws-icons.zip in the project root:

    python tools/import_aws.py
"""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "infrasketch"
ICONS = PACKAGE / "data" / "icons" / "aws"
ZIP = ROOT / ".aws-icons.zip"

CATEGORIES = {
    "Arch_Analytics": "analytics",
    "Arch_Application-Integration": "integration",
    "Arch_Artificial-Intelligence": "ai",
    "Arch_Blockchain": "blockchain",
    "Arch_Business-Applications": "business",
    "Arch_Cloud-Financial-Management": "cost",
    "Arch_Compute": "compute",
    "Arch_Containers": "containers",
    "Arch_Customer-Enablement": "support",
    "Arch_Databases": "databases",
    "Arch_Developer-Tools": "developer_tools",
    "Arch_End-User-Computing": "end_user",
    "Arch_Front-End-Web-Mobile": "web",
    "Arch_Games": "games",
    "Arch_General-Icons": "general",
    "Arch_Internet-of-Things": "iot",
    "Arch_Management-Tools": "management",
    "Arch_Media-Services": "media",
    "Arch_Migration-Modernization": "migration",
    "Arch_Networking-Content-Delivery": "networking",
    "Arch_Quantum-Technologies": "quantum",
    "Arch_Satellite": "satellite",
    "Arch_Security-Identity": "security",
    "Arch_Storage": "storage",
}

ACRONYMS = {
    "ACM", "AI", "API", "CDN", "CLI", "CPU", "DNS", "EC2", "ECR", "ECS", "EKS",
    "ETL", "GPU", "HSM", "HTTP", "HTTPS", "IAM", "IOT", "JSON", "KMS", "ML",
    "MQ", "MSK", "NAT", "NFS", "QLDB", "RDS", "S3", "SDK", "SMS", "SQL", "SSO",
    "VPC", "VPN", "WAF", "XML", "AWS",
}

ALIASES = {
    "AmazonEC2": "EC2",
    "AWSLambda": "Lambda",
    "AmazonSimpleStorageService": "S3",
    "AmazonSimpleQueueService": "SQS",
    "AmazonSimpleNotificationService": "SNS",
    "AmazonDynamoDB": "DynamoDB",
    "AmazonRDS": "RDS",
    "AmazonAurora": "Aurora",
    "AmazonElastiCache": "ElastiCache",
    "AmazonAPIGateway": "APIGateway",
    "AmazonCloudFront": "CloudFront",
    "AmazonRoute53": "Route53",
    "AmazonElasticKubernetesService": "EKS",
    "AmazonElasticContainerService": "ECS",
    "AmazonElasticContainerRegistry": "ECR",
    "AWSFargate": "Fargate",
    "AWSIdentityAndAccessManagement": "IAM",
    "AmazonCognito": "Cognito",
    "AmazonCloudWatch": "CloudWatch",
    "AWSStepFunctions": "StepFunctions",
    "AmazonEventBridge": "EventBridge",
    "AWSSecretsManager": "SecretsManager",
    "ElasticLoadBalancing": "ELB",
    "AWSWAF": "WAF",
    "AmazonKinesis": "Kinesis",
    "AWSGlue": "Glue",
    "AmazonAthena": "Athena",
    "AmazonRedshift": "Redshift",
    "AmazonOpenSearchService": "OpenSearch",
    "AmazonBedrock": "Bedrock",
    "AmazonSageMaker": "SageMaker",
    "Users": "Users",
    "User": "User",
    "Client": "Client",
    "Internet": "Internet",
    "AmazonVPCInternetGateway": "InternetGateway",
}

EXTRAS = (
    ("Res_General-Icons/Res_48_Light/Res_Users_48_Light.svg", "general"),
    ("Res_General-Icons/Res_48_Light/Res_User_48_Light.svg", "general"),
    ("Res_General-Icons/Res_48_Light/Res_Client_48_Light.svg", "general"),
    ("Res_General-Icons/Res_48_Light/Res_Internet_48_Light.svg", "general"),
    ("Res_General-Icons/Res_48_Light/Res_Mobile-client_48_Light.svg", "general"),
    ("Res_Networking-Content-Delivery/Res_Amazon-VPC_Internet-Gateway_48.svg", "networking"),
)

GROUPS = {
    "Virtual-private-cloud-VPC_32.svg": "VPC.svg",
    "Public-subnet_32.svg": "PublicSubnet.svg",
    "Private-subnet_32.svg": "PrivateSubnet.svg",
    "AWS-Account_32.svg": "Account.svg",
    "Region_32.svg": "Region.svg",
    "Auto-Scaling-group_32.svg": "AutoScaling.svg",
    "AWS-Cloud_32.svg": "AWSCloud.svg",
}


def class_name(stem: str) -> str:
    stem = re.sub(r"^(Arch|Res)_", "", stem)
    stem = re.sub(r"_(64|48)(_Light)?$", "", stem)
    stem = re.sub(r"_Light$", "", stem)
    parts = [part for part in re.split(r"[-_ ]+", stem) if part]
    words = []
    for part in parts:
        if part == "&":
            words.append("And")
            continue
        part = re.sub(r"[^A-Za-z0-9]", "", part)
        if not part:
            continue
        upper = part.upper()
        if upper in ACRONYMS:
            words.append(upper)
        elif part.isdigit():
            words.append(part)
        else:
            words.append(part[:1].upper() + part[1:])
    name = "".join(words)
    if not name or not name[0].isalpha():
        name = "Aws" + name
    return name


def service_name(stem: str) -> str:
    stem = re.sub(r"^(Arch|Res)_", "", stem)
    stem = re.sub(r"_(64|48)(_Light)?$", "", stem)
    stem = re.sub(r"_Light$", "", stem)
    parts = [part for part in re.split(r"[-_ ]+", stem) if part]
    words = []
    for part in parts:
        upper = part.upper()
        words.append(upper if upper in ACRONYMS else part[:1].upper() + part[1:])
    return " ".join(words)


def main() -> None:
    if not ZIP.is_file():
        raise SystemExit(f"Missing {ZIP.name}. Download the AWS icon package first.")
    archive = zipfile.ZipFile(ZIP)
    chosen: list[tuple[str, str, str]] = []
    for name in archive.namelist():
        if (
            "Architecture-Service-Icons_" in name
            and "/64/" in name
            and name.endswith(".svg")
            and "._" not in name
            and "Dark" not in name
        ):
            folder = name.split("/")[1]
            module = CATEGORIES.get(folder)
            if module is None:
                raise SystemExit(f"No category mapping for {folder}")
            chosen.append((name, module, Path(name).stem))
    for relative, module in EXTRAS:
        matches = [name for name in archive.namelist() if name.endswith(relative) and "._" not in name]
        if len(matches) != 1:
            raise SystemExit(f"Expected one match for {relative}, found {matches}")
        chosen.append((matches[0], module, Path(matches[0]).stem))

    items = []
    used: dict[str, str] = {}
    for source, module, stem in chosen:
        klass = class_name(stem)
        if klass in used and used[klass] != module:
            klass = klass + "".join(part[:1].upper() + part[1:] for part in module.split("_"))
        used[klass] = module
        items.append(
            {
                "source": source,
                "module": module,
                "name": klass,
                "service": service_name(stem),
                "icon": f"aws/{module}/{klass}.svg",
                "provider": "aws",
            }
        )

    if ICONS.exists():
        for path in ICONS.rglob("*"):
            if path.is_file() and path.name != "LICENSE.txt":
                path.unlink()
    for item in items:
        target = ICONS / item["module"] / f"{item['name']}.svg"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(item["source"]))

    group_dir = ICONS / "groups"
    group_dir.mkdir(parents=True, exist_ok=True)
    for source_name, target_name in GROUPS.items():
        matches = [
            name
            for name in archive.namelist()
            if name.endswith("Architecture-Group-Icons_07312026/" + source_name) and "._" not in name
        ]
        if len(matches) != 1:
            raise SystemExit(f"Expected one group icon for {source_name}, found {matches}")
        (group_dir / target_name).write_bytes(archive.read(matches[0]))

    by_module: dict[str, list[dict]] = {}
    for item in items:
        by_module.setdefault(item["module"], []).append(item)
    aws_dir = PACKAGE / "aws"
    aws_dir.mkdir(exist_ok=True)
    for module, rows in by_module.items():
        lines = [
            '"""AWS resource nodes.',
            "",
            "Generated from the AWS Architecture Icons.",
            "The icons are Amazon Web Services artwork and are not covered by the MIT license.",
            "See NOTICE and src/infrasketch/data/icons/aws/LICENSE.txt.",
            "Regenerate with tools/import_aws.py rather than editing by hand.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "from infrasketch.model import Node",
            "",
        ]
        for row in sorted(rows, key=lambda row: row["name"]):
            lines.extend(
                [
                    "",
                    f"class {row['name']}(Node):",
                    f'    """{row["service"]}."""',
                    "",
                    f'    icon = "{row["icon"]}"',
                    f'    service = "{row["service"]}"',
                ]
            )
        lines.append("")
        (aws_dir / f"{module}.py").write_text("\n".join(lines))

    exports = []
    for row in items:
        alias = ALIASES.get(row["name"])
        if alias is None:
            continue
        exports.append((alias, row["module"], row["name"]))
    exports.sort()
    init = [
        '"""Common AWS resources and the boundaries around them.',
        "",
        "Every architecture-service icon is available, for example",
        "``from infrasketch.aws.compute import AWSLambda``. Use",
        "``python -m infrasketch search aws lambda`` when you do not know the class.",
        '"""',
        "",
        "from infrasketch.aws.groups import (",
        "    AWSCloud,",
        "    Account,",
        "    AutoScaling,",
        "    PrivateSubnet,",
        "    PublicSubnet,",
        "    Region,",
        "    VPC,",
        ")",
    ]
    for alias, module, klass in exports:
        if alias == klass:
            init.append(f"from infrasketch.aws.{module} import {klass}")
        else:
            init.append(f"from infrasketch.aws.{module} import {klass} as {alias}")
    names = [
        "AWSCloud",
        "Account",
        "AutoScaling",
        "PrivateSubnet",
        "PublicSubnet",
        "Region",
        "VPC",
        *[alias for alias, _, _ in exports],
    ]
    init.extend(["", "__all__ = ["])
    for name in names:
        init.append(f'    "{name}",')
    init.append("]")
    init.append("")
    (aws_dir / "__init__.py").write_text("\n".join(init))

    catalog = [
        {
            "provider": "aws",
            "module": row["module"],
            "name": row["name"],
            "service": row["service"],
            "icon": row["icon"],
        }
        for row in sorted(items, key=lambda row: (row["module"], row["service"], row["name"]))
    ]
    (PACKAGE / "data" / "aws-catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
    print(f"imported {len(items)} AWS icons in {len(by_module)} categories")


if __name__ == "__main__":
    main()
