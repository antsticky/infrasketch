"""Azure resource nodes.

Generated from the Microsoft Azure Architecture Icons.
The icons are Microsoft artwork and are not covered by the MIT license.
See NOTICE and src/infrasketch/data/icons/LICENSE.txt.
Regenerate with tools/import_icons.py rather than editing by hand.
"""

from __future__ import annotations

from infrasketch.model import Node


class Detonation(Node):
    """Detonation."""

    icon = "azure/security/Detonation.svg"
    service = "Detonation"

class MicrosoftDefenderForIoT(Node):
    """Microsoft Defender for IoT."""

    icon = "azure/security/MicrosoftDefenderForIoT.svg"
    service = "Microsoft Defender for IoT"

class MicrosoftDefenderEASM(Node):
    """Microsoft Defender EASM."""

    icon = "azure/security/MicrosoftDefenderEASM.svg"
    service = "Microsoft Defender EASM"

class IdentitySecureScore(Node):
    """Identity Secure Score."""

    icon = "azure/security/IdentitySecureScore.svg"
    service = "Identity Secure Score"

class EntraIdentityRiskySignins(Node):
    """Entra Identity Risky Signins."""

    icon = "azure/security/EntraIdentityRiskySignins.svg"
    service = "Entra Identity Risky Signins"

class EntraIdentityRiskyUsers(Node):
    """Entra Identity Risky Users."""

    icon = "azure/security/EntraIdentityRiskyUsers.svg"
    service = "Entra Identity Risky Users"

class MultifactorAuthentication(Node):
    """Multifactor Authentication."""

    icon = "azure/security/MultifactorAuthentication.svg"
    service = "Multifactor Authentication"

class AzureInformationProtection(Node):
    """Azure Information Protection."""

    icon = "azure/security/AzureInformationProtection.svg"
    service = "Azure Information Protection"

class ConditionalAccess(Node):
    """Conditional Access."""

    icon = "azure/security/ConditionalAccess.svg"
    service = "Conditional Access"

class MicrosoftDefenderForCloud(Node):
    """Microsoft Defender for Cloud."""

    icon = "azure/security/MicrosoftDefenderForCloud.svg"
    service = "Microsoft Defender for Cloud"

class ApplicationSecurityGroups(Node):
    """Application Security Groups."""

    icon = "azure/security/ApplicationSecurityGroups.svg"
    service = "Application Security Groups"

class KeyVaults(Node):
    """Key Vault."""

    icon = "azure/security/KeyVaults.svg"
    service = "Key Vault"

class AzureSentinel(Node):
    """Azure Sentinel."""

    icon = "azure/security/AzureSentinel.svg"
    service = "Azure Sentinel"

class UserSettings(Node):
    """User Settings."""

    icon = "azure/security/UserSettings.svg"
    service = "User Settings"

class ExtendedSecurityUpdates(Node):
    """ExtendedSecurityUpdates."""

    icon = "azure/security/ExtendedSecurityUpdates.svg"
    service = "ExtendedSecurityUpdates"
