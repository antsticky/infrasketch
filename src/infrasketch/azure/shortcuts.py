"""Short names for the resources that show up on most architecture diagrams.

Every other icon is still available, for example
``from infrasketch.azure.networking import Bastions``. Use ``python -m infrasketch search``
when you do not know the class name.
"""

from infrasketch.azure.ai import AzureOpenAI
from infrasketch.azure.analytics import EventHubs as EventHub
from infrasketch.azure.compute import AppServices as AppService
from infrasketch.azure.compute import FunctionApps as FunctionApp
from infrasketch.azure.compute import VMScaleSets as VMScaleSet
from infrasketch.azure.compute import VirtualMachine
from infrasketch.azure.containers import ContainerInstances as ContainerInstance
from infrasketch.azure.containers import ContainerRegistries as ContainerRegistry
from infrasketch.azure.containers import KubernetesServices as AKS
from infrasketch.azure.databases import AzureCosmosDB as CosmosDB
from infrasketch.azure.databases import AzureDatabaseMySQLServer as MySQL
from infrasketch.azure.databases import AzureDatabasePostgreSQLServer as PostgreSQL
from infrasketch.azure.databases import AzureManagedRedis as ManagedRedis
from infrasketch.azure.databases import CacheRedis as Redis
from infrasketch.azure.databases import SQLDatabase
from infrasketch.azure.general import BlobBlock as BlobStorage
from infrasketch.azure.general import Browser
from infrasketch.azure.identity import ManagedIdentities as ManagedIdentity
from infrasketch.azure.identity import Users
from infrasketch.azure.integration import APIManagementServices as APIManagement
from infrasketch.azure.integration import AzureServiceBus as ServiceBus
from infrasketch.azure.integration import DataFactories as DataFactory
from infrasketch.azure.integration import EventGridTopics as EventGrid
from infrasketch.azure.integration import LogicApps as LogicApp
from infrasketch.azure.monitor import ApplicationInsights
from infrasketch.azure.monitor import LogAnalyticsWorkspaces as LogAnalytics
from infrasketch.azure.monitor import Monitor
from infrasketch.azure.networking import ApplicationGateways as ApplicationGateway
from infrasketch.azure.networking import Bastions as Bastion
from infrasketch.azure.networking import CDNProfiles as CDN
from infrasketch.azure.networking import DNSZones as DNSZone
from infrasketch.azure.networking import ExpressRouteCircuits as ExpressRoute
from infrasketch.azure.networking import Firewalls as Firewall
from infrasketch.azure.networking import FrontDoorAndCDNProfiles as FrontDoor
from infrasketch.azure.networking import LoadBalancers as LoadBalancer
from infrasketch.azure.networking import NAT as NATGateway
from infrasketch.azure.networking import NetworkSecurityGroups as NSG
from infrasketch.azure.networking import PublicIPAddresses as PublicIP
from infrasketch.azure.networking import TrafficManagerProfiles as TrafficManager
from infrasketch.azure.networking import (
    WebApplicationFirewallPoliciesWAF as WAF,
)
from infrasketch.azure.networking import VirtualNetworkGateways as VPNGateway
from infrasketch.azure.other import ContainerAppsEnvironments as ContainerAppsEnvironment
from infrasketch.azure.other import PrivateEndpoints as PrivateEndpoint
from infrasketch.azure.other import WorkerContainerApp as ContainerApp
from infrasketch.azure.security import KeyVaults as KeyVault
from infrasketch.azure.storage import StorageAccounts as StorageAccount
from infrasketch.azure.web import AppServicePlans as AppServicePlan
from infrasketch.azure.web import CognitiveSearch as AISearch
from infrasketch.azure.web import SignalR
from infrasketch.azure.web import StaticApps as StaticWebApp

ACR = ContainerRegistry
SQL = SQLDatabase

__all__ = [
    "AISearch",
    "AKS",
    "ACR",
    "APIManagement",
    "AppService",
    "AppServicePlan",
    "ApplicationGateway",
    "ApplicationInsights",
    "AzureOpenAI",
    "Bastion",
    "BlobStorage",
    "Browser",
    "CDN",
    "ContainerApp",
    "ContainerAppsEnvironment",
    "ContainerInstance",
    "ContainerRegistry",
    "CosmosDB",
    "DNSZone",
    "DataFactory",
    "EventGrid",
    "EventHub",
    "ExpressRoute",
    "Firewall",
    "FrontDoor",
    "FunctionApp",
    "KeyVault",
    "LoadBalancer",
    "LogAnalytics",
    "LogicApp",
    "ManagedIdentity",
    "ManagedRedis",
    "Monitor",
    "MySQL",
    "NATGateway",
    "NSG",
    "PostgreSQL",
    "PrivateEndpoint",
    "PublicIP",
    "Redis",
    "SQL",
    "SQLDatabase",
    "ServiceBus",
    "SignalR",
    "StaticWebApp",
    "StorageAccount",
    "TrafficManager",
    "Users",
    "VMScaleSet",
    "VPNGateway",
    "VirtualMachine",
    "WAF",
]
