"""Short names for the resources that show up on most architecture diagrams.

Every other icon is still available, for example
``from infrasketch.networking import Bastions``. Use ``python -m infrasketch search``
when you do not know the class name.
"""

from infrasketch.ai import AzureOpenAI
from infrasketch.analytics import EventHubs as EventHub
from infrasketch.compute import AppServices as AppService
from infrasketch.compute import FunctionApps as FunctionApp
from infrasketch.compute import VMScaleSets as VMScaleSet
from infrasketch.compute import VirtualMachine
from infrasketch.containers import ContainerInstances as ContainerInstance
from infrasketch.containers import ContainerRegistries as ContainerRegistry
from infrasketch.containers import KubernetesServices as AKS
from infrasketch.databases import AzureCosmosDB as CosmosDB
from infrasketch.databases import AzureDatabaseMySQLServer as MySQL
from infrasketch.databases import AzureDatabasePostgreSQLServer as PostgreSQL
from infrasketch.databases import AzureManagedRedis as ManagedRedis
from infrasketch.databases import CacheRedis as Redis
from infrasketch.databases import SQLDatabase
from infrasketch.general import BlobBlock as BlobStorage
from infrasketch.general import Browser
from infrasketch.identity import ManagedIdentities as ManagedIdentity
from infrasketch.identity import Users
from infrasketch.integration import APIManagementServices as APIManagement
from infrasketch.integration import AzureServiceBus as ServiceBus
from infrasketch.integration import DataFactories as DataFactory
from infrasketch.integration import EventGridTopics as EventGrid
from infrasketch.integration import LogicApps as LogicApp
from infrasketch.monitor import ApplicationInsights
from infrasketch.monitor import LogAnalyticsWorkspaces as LogAnalytics
from infrasketch.monitor import Monitor
from infrasketch.networking import ApplicationGateways as ApplicationGateway
from infrasketch.networking import Bastions as Bastion
from infrasketch.networking import CDNProfiles as CDN
from infrasketch.networking import DNSZones as DNSZone
from infrasketch.networking import ExpressRouteCircuits as ExpressRoute
from infrasketch.networking import Firewalls as Firewall
from infrasketch.networking import FrontDoorAndCDNProfiles as FrontDoor
from infrasketch.networking import LoadBalancers as LoadBalancer
from infrasketch.networking import NAT as NATGateway
from infrasketch.networking import NetworkSecurityGroups as NSG
from infrasketch.networking import PublicIPAddresses as PublicIP
from infrasketch.networking import TrafficManagerProfiles as TrafficManager
from infrasketch.networking import (
    WebApplicationFirewallPoliciesWAF as WAF,
)
from infrasketch.networking import VirtualNetworkGateways as VPNGateway
from infrasketch.other import ContainerAppsEnvironments as ContainerAppsEnvironment
from infrasketch.other import PrivateEndpoints as PrivateEndpoint
from infrasketch.other import WorkerContainerApp as ContainerApp
from infrasketch.security import KeyVaults as KeyVault
from infrasketch.storage import StorageAccounts as StorageAccount
from infrasketch.web import AppServicePlans as AppServicePlan
from infrasketch.web import CognitiveSearch as AISearch
from infrasketch.web import SignalR
from infrasketch.web import StaticApps as StaticWebApp

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
