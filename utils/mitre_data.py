"""
MITRE ATT&CK Data Handler
Provides utilities for working with MITRE ATT&CK framework data
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AttackTechnique:
    """Represents a MITRE ATT&CK technique"""

    id: str
    name: str
    description: str
    tactics: List[str]
    platforms: List[str]
    data_sources: List[str] = None
    mitigations: List[str] = None
    detection: str = ""


@dataclass
class AttackTactic:
    """Represents a MITRE ATT&CK tactic"""

    id: str
    name: str
    description: str
    techniques: List[str] = None


class MitreAttackHandler:
    """Handler for MITRE ATT&CK framework data"""

    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize MITRE ATT&CK handler

        Args:
            data_file: Path to MITRE ATT&CK data file (JSON format)
        """
        self.logger = logging.getLogger(__name__)
        self.techniques: Dict[str, AttackTechnique] = {}
        self.tactics: Dict[str, AttackTactic] = {}

        # Load built-in minimal dataset if no file provided
        if data_file and Path(data_file).exists():
            self._load_from_file(data_file)
        else:
            self._load_minimal_dataset()

    def _load_from_file(self, data_file: str):
        """Load MITRE ATT&CK data from JSON file"""
        try:
            with open(data_file, "r") as f:
                data = json.load(f)

            # Parse techniques
            for tech_data in data.get("techniques", []):
                technique = AttackTechnique(
                    id=tech_data["id"],
                    name=tech_data["name"],
                    description=tech_data.get("description", ""),
                    tactics=tech_data.get("tactics", []),
                    platforms=tech_data.get("platforms", []),
                    data_sources=tech_data.get("data_sources", []),
                    mitigations=tech_data.get("mitigations", []),
                    detection=tech_data.get("detection", ""),
                )
                self.techniques[technique.id] = technique

            # Parse tactics
            for tactic_data in data.get("tactics", []):
                tactic = AttackTactic(
                    id=tactic_data["id"],
                    name=tactic_data["name"],
                    description=tactic_data.get("description", ""),
                    techniques=tactic_data.get("techniques", []),
                )
                self.tactics[tactic.id] = tactic

            self.logger.info(
                f"Loaded {len(self.techniques)} techniques and {len(self.tactics)} tactics"
            )

        except Exception as e:
            self.logger.error(f"Error loading MITRE data: {e}")
            self._load_minimal_dataset()

    def _load_minimal_dataset(self):
        """Load minimal built-in MITRE ATT&CK dataset"""
        # Common tactics
        tactics_data = [
            {
                "id": "TA0001",
                "name": "Initial Access",
                "description": "The adversary is trying to get into your network",
            },
            {
                "id": "TA0002",
                "name": "Execution",
                "description": "The adversary is trying to run malicious code",
            },
            {
                "id": "TA0003",
                "name": "Persistence",
                "description": "The adversary is trying to maintain their foothold",
            },
            {
                "id": "TA0004",
                "name": "Privilege Escalation",
                "description": "The adversary is trying to gain higher-level permissions",
            },
            {
                "id": "TA0005",
                "name": "Defense Evasion",
                "description": "The adversary is trying to avoid being detected",
            },
            {
                "id": "TA0006",
                "name": "Credential Access",
                "description": "The adversary is trying to steal account names and passwords",
            },
            {
                "id": "TA0007",
                "name": "Discovery",
                "description": "The adversary is trying to figure out your environment",
            },
            {
                "id": "TA0008",
                "name": "Lateral Movement",
                "description": "The adversary is trying to move through your environment",
            },
            {
                "id": "TA0009",
                "name": "Collection",
                "description": "The adversary is trying to gather data of interest",
            },
            {
                "id": "TA0010",
                "name": "Exfiltration",
                "description": "The adversary is trying to steal data",
            },
            {
                "id": "TA0011",
                "name": "Command and Control",
                "description": "The adversary is trying to communicate with compromised systems",
            },
            {
                "id": "TA0040",
                "name": "Impact",
                "description": "The adversary is trying to manipulate, interrupt, or destroy your systems and data",
            },
        ]

        # Common techniques
        techniques_data = [
            {
                "id": "T1566.001",
                "name": "Spearphishing Attachment",
                "description": "Adversaries may send spearphishing emails with a malicious attachment",
                "tactics": ["Initial Access"],
                "platforms": ["Windows", "macOS", "Linux"],
                "data_sources": [
                    "Email Gateway",
                    "File Monitoring",
                    "Process Monitoring",
                ],
            },
            {
                "id": "T1059.001",
                "name": "PowerShell",
                "description": "Adversaries may abuse PowerShell commands and scripts for execution",
                "tactics": ["Execution"],
                "platforms": ["Windows"],
                "data_sources": [
                    "PowerShell Logs",
                    "Process Monitoring",
                    "Command History",
                ],
            },
            {
                "id": "T1055",
                "name": "Process Injection",
                "description": "Adversaries may inject code into processes to evade process-based defenses",
                "tactics": ["Defense Evasion", "Privilege Escalation"],
                "platforms": ["Windows", "Linux", "macOS"],
                "data_sources": [
                    "Process Monitoring",
                    "API Monitoring",
                    "DLL Monitoring",
                ],
            },
            {
                "id": "T1003.001",
                "name": "LSASS Memory",
                "description": "Adversaries may attempt to access credential material stored in LSASS memory",
                "tactics": ["Credential Access"],
                "platforms": ["Windows"],
                "data_sources": [
                    "Process Monitoring",
                    "Process Access",
                    "Security Logs",
                ],
            },
            {
                "id": "T1083",
                "name": "File and Directory Discovery",
                "description": "Adversaries may enumerate files and directories or search in specific locations",
                "tactics": ["Discovery"],
                "platforms": ["Windows", "Linux", "macOS"],
                "data_sources": [
                    "File Monitoring",
                    "Process Monitoring",
                    "Command History",
                ],
            },
            {
                "id": "T1021.001",
                "name": "Remote Desktop Protocol",
                "description": "Adversaries may use Valid Accounts to log into a computer using RDP",
                "tactics": ["Lateral Movement"],
                "platforms": ["Windows"],
                "data_sources": [
                    "Authentication Logs",
                    "Network Traffic",
                    "Process Monitoring",
                ],
            },
            {
                "id": "T1071.001",
                "name": "Web Protocols",
                "description": "Adversaries may communicate using application layer protocols associated with web traffic",
                "tactics": ["Command and Control"],
                "platforms": ["Windows", "Linux", "macOS"],
                "data_sources": ["Network Traffic", "Packet Capture", "Netflow"],
            },
            {
                "id": "T1486",
                "name": "Data Encrypted for Impact",
                "description": "Adversaries may encrypt data on target systems or on large numbers of systems",
                "tactics": ["Impact"],
                "platforms": ["Windows", "Linux", "macOS"],
                "data_sources": [
                    "File Monitoring",
                    "Process Monitoring",
                    "Binary File Metadata",
                ],
            },
        ]

        # Load tactics
        for tactic_data in tactics_data:
            tactic = AttackTactic(**tactic_data)
            self.tactics[tactic.id] = tactic

        # Load techniques
        for tech_data in techniques_data:
            technique = AttackTechnique(**tech_data)
            self.techniques[technique.id] = technique

        self.logger.info("Loaded minimal MITRE ATT&CK dataset")

    def get_technique(self, technique_id: str) -> Optional[AttackTechnique]:
        """Get technique by ID"""
        return self.techniques.get(technique_id)

    def get_tactic(self, tactic_id: str) -> Optional[AttackTactic]:
        """Get tactic by ID"""
        return self.tactics.get(tactic_id)

    def get_techniques_by_tactic(self, tactic_name: str) -> List[AttackTechnique]:
        """Get all techniques for a given tactic"""
        return [
            tech for tech in self.techniques.values() if tactic_name in tech.tactics
        ]

    def search_techniques(self, query: str) -> List[AttackTechnique]:
        """Search techniques by name or description"""
        query = query.lower()
        results = []

        for technique in self.techniques.values():
            if (
                query in technique.name.lower()
                or query in technique.description.lower()
                or query in technique.id.lower()
            ):
                results.append(technique)

        return results

    def get_kill_chain_for_scenario(self, scenario_type: str) -> List[str]:
        """Get typical kill chain tactics for a scenario type"""
        kill_chains = {
            "phishing": [
                "Initial Access",
                "Execution",
                "Persistence",
                "Credential Access",
                "Discovery",
                "Lateral Movement",
                "Collection",
                "Exfiltration",
            ],
            "ransomware": [
                "Initial Access",
                "Execution",
                "Persistence",
                "Defense Evasion",
                "Discovery",
                "Lateral Movement",
                "Impact",
            ],
            "apt": [
                "Initial Access",
                "Execution",
                "Persistence",
                "Defense Evasion",
                "Credential Access",
                "Discovery",
                "Lateral Movement",
                "Collection",
                "Command and Control",
                "Exfiltration",
            ],
            "insider_threat": [
                "Privilege Escalation",
                "Credential Access",
                "Discovery",
                "Collection",
                "Exfiltration",
            ],
            "supply_chain": [
                "Initial Access",
                "Execution",
                "Persistence",
                "Defense Evasion",
                "Discovery",
                "Command and Control",
            ],
            "default": [
                "Initial Access",
                "Execution",
                "Persistence",
                "Discovery",
                "Lateral Movement",
                "Impact",
            ],
        }

        return kill_chains.get(scenario_type.lower(), kill_chains["default"])

    def generate_technique_evidence(self, technique_id: str) -> Dict[str, Any]:
        """Generate evidence items for a given technique"""
        technique = self.get_technique(technique_id)
        if not technique:
            return {}

        evidence = {
            "technique_id": technique_id,
            "technique_name": technique.name,
            "evidence_items": [],
        }

        # Generate evidence based on data sources
        if technique.data_sources:
            for data_source in technique.data_sources:
                evidence_item = self._generate_evidence_for_data_source(
                    data_source, technique
                )
                if evidence_item:
                    evidence["evidence_items"].append(evidence_item)

        return evidence

    def _generate_evidence_for_data_source(
        self, data_source: str, technique: AttackTechnique
    ) -> Dict[str, Any]:
        """Generate specific evidence for a data source"""
        evidence_templates = {
            "Process Monitoring": {
                "type": "process_log",
                "description": f"Process execution related to {technique.name}",
                "indicators": [
                    "unusual process names",
                    "command line arguments",
                    "parent-child process relationships",
                ],
            },
            "Network Traffic": {
                "type": "network_log",
                "description": f"Network activity associated with {technique.name}",
                "indicators": [
                    "unusual connections",
                    "data transfer patterns",
                    "protocol anomalies",
                ],
            },
            "File Monitoring": {
                "type": "file_system_log",
                "description": f"File system changes related to {technique.name}",
                "indicators": [
                    "file creation/modification",
                    "directory changes",
                    "permission modifications",
                ],
            },
            "Authentication Logs": {
                "type": "authentication_log",
                "description": f"Authentication events related to {technique.name}",
                "indicators": [
                    "login attempts",
                    "account usage patterns",
                    "privilege changes",
                ],
            },
            "PowerShell Logs": {
                "type": "powershell_log",
                "description": f"PowerShell activity related to {technique.name}",
                "indicators": ["script execution", "command history", "module usage"],
            },
        }

        template = evidence_templates.get(data_source)
        if template:
            return {
                "data_source": data_source,
                "type": template["type"],
                "description": template["description"],
                "potential_indicators": template["indicators"],
            }

        return {
            "data_source": data_source,
            "type": "generic_log",
            "description": f"Log data from {data_source} related to {technique.name}",
            "potential_indicators": ["anomalous activity", "unusual patterns"],
        }

    def get_detection_recommendations(self, technique_id: str) -> List[str]:
        """Get detection recommendations for a technique"""
        technique = self.get_technique(technique_id)
        if not technique:
            return []

        recommendations = []

        # Generic recommendations based on data sources
        if technique.data_sources:
            for data_source in technique.data_sources:
                if data_source == "Process Monitoring":
                    recommendations.append(
                        "Monitor for unusual process creation and execution patterns"
                    )
                elif data_source == "Network Traffic":
                    recommendations.append(
                        "Analyze network connections for suspicious communication patterns"
                    )
                elif data_source == "File Monitoring":
                    recommendations.append(
                        "Track file system changes and access patterns"
                    )
                elif data_source == "Authentication Logs":
                    recommendations.append(
                        "Monitor authentication events for anomalous login behavior"
                    )

        # Add technique-specific detection if available
        if technique.detection:
            recommendations.append(technique.detection)

        return recommendations[:5]  # Limit to top 5 recommendations

    def get_techniques_for_scenario(
        self, sector: str, complexity: str, infrastructure: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get appropriate MITRE ATT&CK techniques for a scenario based on parameters.

        Args:
            sector: Target sector (finance, healthcare, government, technology, retail)
            complexity: Difficulty level (beginner, intermediate, advanced, expert)
            infrastructure: Infrastructure type (on-premises, cloud, hybrid)

        Returns:
            Dictionary mapping kill chain phases to technique details
        """

        # Define technique sets based on complexity
        technique_sets = {
            "beginner": {
                "Initial Access": [
                    "T1566.002",
                    "T1078",
                    "T1190",
                ],  # Spearphishing, Valid Accounts, Exploit Public-Facing App
                "Execution": [
                    "T1059.001",
                    "T1059.003",
                    "T1204",
                ],  # PowerShell, cmd, User Execution
                "Persistence": [
                    "T1547.001",
                    "T1053",
                    "T1136",
                ],  # Registry Run Keys, Scheduled Task, Create Account
                "Discovery": [
                    "T1083",
                    "T1057",
                    "T1082",
                ],  # File and Directory Discovery, Process Discovery, System Information
                "Impact": [
                    "T1486",
                    "T1489",
                    "T1490",
                ],  # Data Encrypted for Impact, Service Stop, Inhibit System Recovery
            },
            "intermediate": {
                "Initial Access": [
                    "T1566.001",
                    "T1078.004",
                    "T1133",
                ],  # Spearphishing Attachment, Cloud Accounts, External Remote Services
                "Execution": [
                    "T1059.001",
                    "T1086",
                    "T1053.005",
                ],  # PowerShell, PowerShell, Scheduled Task
                "Persistence": [
                    "T1098",
                    "T1136.003",
                    "T1547.009",
                ],  # Account Manipulation, Cloud Account, Shortcut Modification
                "Defense Evasion": [
                    "T1027",
                    "T1070.004",
                    "T1218",
                ],  # Obfuscated Files, File Deletion, Signed Binary Proxy
                "Credential Access": [
                    "T1003.001",
                    "T1110",
                    "T1555",
                ],  # LSASS Memory, Brute Force, Credentials from Password Stores
                "Discovery": [
                    "T1018",
                    "T1033",
                    "T1069",
                ],  # Remote System Discovery, System Owner/User Discovery, Permission Groups Discovery
                "Lateral Movement": [
                    "T1021.001",
                    "T1076",
                    "T1550",
                ],  # Remote Desktop Protocol, Remote Desktop Services, Use Alternate Authentication Material
                "Collection": [
                    "T1005",
                    "T1039",
                    "T1113",
                ],  # Data from Local System, Data from Network Drive, Screen Capture
                "Exfiltration": [
                    "T1041",
                    "T1567",
                    "T1020",
                ],  # Exfiltration Over C2 Channel, Exfiltration Over Web Service, Automated Exfiltration
            },
            "advanced": {
                "Initial Access": [
                    "T1566.003",
                    "T1195.002",
                    "T1199",
                ],  # Spearphishing via Service, Compromise Software Supply Chain, Trusted Relationship
                "Execution": [
                    "T1059.007",
                    "T1569.002",
                    "T1047",
                ],  # JavaScript, Service Execution, Windows Management Instrumentation
                "Persistence": [
                    "T1546.003",
                    "T1574.002",
                    "T1053.005",
                ],  # Windows Management Instrumentation Event Subscription, DLL Side-Loading, Scheduled Task
                "Defense Evasion": [
                    "T1055",
                    "T1134",
                    "T1620",
                ],  # Process Injection, Access Token Manipulation, Reflective Code Loading
                "Privilege Escalation": [
                    "T1068",
                    "T1134.001",
                    "T1484",
                ],  # Exploitation for Privilege Escalation, Token Impersonation/Theft, Domain Policy Modification
                "Credential Access": [
                    "T1003.003",
                    "T1558.003",
                    "T1212",
                ],  # NTDS, Kerberoasting, Exploitation for Credential Access
                "Discovery": [
                    "T1482",
                    "T1087.002",
                    "T1120",
                ],  # Domain Trust Discovery, Domain Account, Peripheral Device Discovery
                "Lateral Movement": [
                    "T1550.003",
                    "T1021.002",
                    "T1080",
                ],  # Pass the Ticket, SMB/Windows Admin Shares, Taint Shared Content
                "Command and Control": [
                    "T1071.001",
                    "T1573.002",
                    "T1090",
                ],  # Web Protocols, Asymmetric Cryptography, Proxy
                "Collection": [
                    "T1560",
                    "T1114.002",
                    "T1056",
                ],  # Archive Collected Data, Remote Email Collection, Input Capture
                "Exfiltration": [
                    "T1048",
                    "T1537",
                    "T1029",
                ],  # Exfiltration Over Alternative Protocol, Transfer Data to Cloud Account, Scheduled Transfer
            },
            "expert": {
                "Initial Access": [
                    "T1195.003",
                    "T1566.004",
                    "T1189",
                ],  # Compromise Hardware Supply Chain, Spearphishing Voice, Drive-by Compromise
                "Execution": [
                    "T1559.001",
                    "T1648",
                    "T1106",
                ],  # Component Object Model, Serverless Execution, Native API
                "Persistence": [
                    "T1546.015",
                    "T1053.003",
                    "T1137",
                ],  # Component Object Model Hijacking, Cron, Office Application Startup
                "Defense Evasion": [
                    "T1550.001",
                    "T1036.005",
                    "T1564.001",
                ],  # Use Alternate Authentication Material, Match Legitimate Name or Location, Hidden Files and Directories
                "Privilege Escalation": [
                    "T1543.003",
                    "T1546.008",
                    "T1484.001",
                ],  # Windows Service, Accessibility Features, Group Policy Modification
                "Credential Access": [
                    "T1187",
                    "T1552.004",
                    "T1606",
                ],  # Forced Authentication, Private Keys, Forge Web Credentials
                "Discovery": [
                    "T1614",
                    "T1518.001",
                    "T1124",
                ],  # System Location Discovery, Security Software Discovery, System Time Discovery
                "Lateral Movement": [
                    "T1021.007",
                    "T1534",
                    "T1563",
                ],  # SSH, Internal Spearphishing, Remote Service Session Hijacking
                "Command and Control": [
                    "T1102",
                    "T1132.001",
                    "T1568",
                ],  # Web Service, Standard Encoding, Dynamic Resolution
                "Collection": [
                    "T1123",
                    "T1115",
                    "T1125",
                ],  # Audio Capture, Clipboard Data, Video Capture
                "Exfiltration": [
                    "T1052",
                    "T1011",
                    "T1030",
                ],  # Exfiltration Over Physical Medium, Exfiltration Over Other Network Medium, Data Transfer Size Limits
                "Impact": [
                    "T1499",
                    "T1561",
                    "T1485",
                ],  # Endpoint Denial of Service, Disk Wipe, Data Destruction
            },
        }

        # Get base technique set for complexity level
        base_techniques = technique_sets.get(complexity, technique_sets["intermediate"])

        # Adjust techniques based on infrastructure
        if infrastructure == "cloud":
            # Add cloud-specific techniques
            cloud_additions = {
                "Initial Access": "T1078.004",  # Cloud Accounts
                "Persistence": "T1098.001",  # Additional Cloud Credentials
                "Defense Evasion": "T1578",  # Modify Cloud Compute Infrastructure
                "Discovery": "T1580",  # Cloud Infrastructure Discovery
            }
            for phase, tech_id in cloud_additions.items():
                if phase in base_techniques:
                    if tech_id not in base_techniques[phase]:
                        base_techniques[phase].append(tech_id)

        elif infrastructure == "on-premises":
            # Add on-premises specific techniques
            onprem_additions = {
                "Lateral Movement": "T1021.002",  # SMB/Windows Admin Shares
                "Persistence": "T1547.001",  # Registry Run Keys
                "Discovery": "T1016",  # System Network Configuration Discovery
            }
            for phase, tech_id in onprem_additions.items():
                if phase in base_techniques:
                    if tech_id not in base_techniques[phase]:
                        base_techniques[phase].append(tech_id)

        # Select one technique per phase and build response
        result = {}
        for phase, technique_ids in base_techniques.items():
            import random

            selected_id = random.choice(technique_ids)
            technique = self.get_technique(selected_id)

            if technique:
                result[phase] = {
                    "id": technique.id,
                    "name": technique.name,
                    "description": technique.description,
                    "tactics": technique.tactics,
                    "platforms": technique.platforms,
                }
            else:
                # Fallback with basic technique info
                result[phase] = {
                    "id": selected_id,
                    "name": f"Technique {selected_id}",
                    "description": f"MITRE ATT&CK technique {selected_id}",
                    "tactics": [phase],
                    "platforms": ["Windows", "Linux", "macOS"],
                }

        return result


# Global instance for easy access
mitre_handler = MitreAttackHandler()
