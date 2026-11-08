"""Visual system for architecture diagrams.

The icons themselves are the official Azure artwork and are drawn unchanged.
Everything around them — boundaries, type, and connectors — follows current
architecture-diagram practice: white canvas, quiet type, and orthogonal lines.
"""

from __future__ import annotations

FONT = '"Segoe UI", Inter, "Helvetica Neue", Arial, sans-serif'
FONT_ATTR = FONT.replace('"', "&quot;")

INK = "#0F172A"
MUTED = "#64748B"
EDGE = "#5C6B7C"
LINE = "#D6DEE8"
CANVAS = "#FFFFFF"

SPACING = {
    "compact": {"rank": 44, "item": 14, "pad": 14, "pad_top": 12},
    "regular": {"rank": 64, "item": 22, "pad": 18, "pad_top": 14},
    "relaxed": {"rank": 88, "item": 30, "pad": 24, "pad_top": 18},
}

PAGE_X = 36
PAGE_TOP = 28
FOOTER = 26

# Boundary styles. Icons are referenced after import_icons.py has run.
BOUNDARIES = {
    "group": {
        "fill": "#FFFFFF",
        "stroke": "#E2E8F0",
        "stroke_width": 1.25,
        "dash": None,
        "accent": "#475569",
        "header": "#F8FAFC",
        "eyebrow": None,
        "radius": 14,
        "icon": None,
    },
    "resource_group": {
        "fill": "#FFFFFF",
        "stroke": "#D5DEE8",
        "stroke_width": 1.25,
        "dash": None,
        "accent": "#0078D4",
        "header": "#F3F7FB",
        "eyebrow": "RESOURCE GROUP",
        "radius": 14,
        "icon": "azure/general/ResourceGroups.svg",
    },
    "subscription": {
        "fill": "#F7FBFE",
        "stroke": "#C5D4E8",
        "stroke_width": 1.35,
        "dash": None,
        "accent": "#0078D4",
        "header": "#E7F2FB",
        "eyebrow": "SUBSCRIPTION",
        "radius": 16,
        "icon": "azure/general/Subscriptions.svg",
    },
    "region": {
        "fill": "#FCFCFD",
        "stroke": "#E5E7EB",
        "stroke_width": 1.25,
        "dash": None,
        "accent": "#475569",
        "header": "#F8FAFC",
        "eyebrow": "REGION",
        "radius": 16,
        "icon": "azure/general/RegionManagement.svg",
    },
    "vnet": {
        "fill": "#F4F9FE",
        "stroke": "#4F9AD8",
        "stroke_width": 1.5,
        "dash": "7 5",
        "accent": "#0078D4",
        "header": "#E7F3FC",
        "eyebrow": "VIRTUAL NETWORK",
        "radius": 16,
        "icon": "azure/networking/VirtualNetworks.svg",
    },
    "subnet": {
        "fill": "#FFFFFF",
        "stroke": "#8FB4D4",
        "stroke_width": 1.25,
        "dash": "4 3",
        "accent": "#0F6CBD",
        "header": "#F5FAFD",
        "eyebrow": "SUBNET",
        "radius": 12,
        "icon": "azure/networking/Subnet.svg",
    },
    "private": {
        "fill": "#F4FBF7",
        "stroke": "#3C9D64",
        "stroke_width": 1.4,
        "dash": "5 4",
        "accent": "#107C41",
        "header": "#E7F6EE",
        "eyebrow": "PRIVATE NETWORK",
        "radius": 12,
        "icon": "azure/networking/PrivateLink.svg",
    },
    "aws_cloud": {
        "fill": "#FFFFFF",
        "stroke": "#D6DEE8",
        "stroke_width": 1.35,
        "dash": None,
        "accent": "#232F3E",
        "header": "#F8FAFC",
        "eyebrow": "AWS CLOUD",
        "radius": 16,
        "icon": "aws/groups/AWSCloud.svg",
    },
    "aws_account": {
        "fill": "#FFFFFF",
        "stroke": "#D6DEE8",
        "stroke_width": 1.25,
        "dash": None,
        "accent": "#232F3E",
        "header": "#F8FAFC",
        "eyebrow": "ACCOUNT",
        "radius": 16,
        "icon": "aws/groups/Account.svg",
    },
    "aws_region": {
        "fill": "#FCFCFD",
        "stroke": "#E5E7EB",
        "stroke_width": 1.25,
        "dash": None,
        "accent": "#232F3E",
        "header": "#F8FAFC",
        "eyebrow": "REGION",
        "radius": 16,
        "icon": "aws/groups/Region.svg",
    },
    "aws_vpc": {
        "fill": "#FFF8F3",
        "stroke": "#ED7100",
        "stroke_width": 1.5,
        "dash": "7 5",
        "accent": "#ED7100",
        "header": "#FFF1E6",
        "eyebrow": "VPC",
        "radius": 16,
        "icon": "aws/groups/VPC.svg",
    },
    "aws_public_subnet": {
        "fill": "#F4FBF7",
        "stroke": "#3C9D64",
        "stroke_width": 1.25,
        "dash": "4 3",
        "accent": "#1D8102",
        "header": "#E7F6EE",
        "eyebrow": "PUBLIC SUBNET",
        "radius": 12,
        "icon": "aws/groups/PublicSubnet.svg",
    },
    "aws_private_subnet": {
        "fill": "#F7F8FA",
        "stroke": "#687078",
        "stroke_width": 1.25,
        "dash": "4 3",
        "accent": "#232F3E",
        "header": "#F4F5F7",
        "eyebrow": "PRIVATE SUBNET",
        "radius": 12,
        "icon": "aws/groups/PrivateSubnet.svg",
    },
    "aws_autoscaling": {
        "fill": "#FFFFFF",
        "stroke": "#ED7100",
        "stroke_width": 1.25,
        "dash": "5 4",
        "accent": "#ED7100",
        "header": "#FFF8F3",
        "eyebrow": "AUTO SCALING",
        "radius": 12,
        "icon": "aws/groups/AutoScaling.svg",
    },
}
