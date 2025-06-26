"""
Evidence Generator for Incidenter
Generates realistic evidence items for cybersecurity scenarios
"""

import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid


@dataclass
class EvidenceItem:
    """Represents a piece of evidence in an incident"""

    id: str
    type: str
    source: str
    timestamp: datetime
    content: str
    importance: str  # critical, high, medium, low
    reliability: str  # high, medium, low
    tags: List[str]
    related_techniques: List[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert EvidenceItem to dictionary for YAML serialization"""
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else self.timestamp
            ),
            "content": self.content,
            "importance": self.importance,
            "reliability": self.reliability,
            "tags": self.tags or [],
            "related_techniques": self.related_techniques or [],
            "metadata": self.metadata or {},
        }


class EvidenceGenerator:
    """Generates realistic evidence for cybersecurity scenarios"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_evidence_templates()

    def _load_evidence_templates(self):
        """Load evidence generation templates"""
        self.log_templates = {
            "process_log": [
                "Process created: {process_name} (PID: {pid}) with command line: {command_line}",
                "Process {process_name} (PID: {pid}) accessed file: {file_path}",
                "Process {process_name} terminated with exit code: {exit_code}",
                "Process {process_name} created child process: {child_process} (PID: {child_pid})",
            ],
            "network_log": [
                "Connection established from {src_ip}:{src_port} to {dst_ip}:{dst_port} using {protocol}",
                "DNS query for {domain} from {src_ip} returned {resolved_ip}",
                "HTTP request to {url} from {src_ip} - Response: {status_code}",
                "Network connection blocked: {src_ip} -> {dst_ip}:{dst_port} (Rule: {rule_name})",
            ],
            "authentication_log": [
                "User {username} logged in from {src_ip} at {timestamp}",
                "Failed login attempt for user {username} from {src_ip}",
                "User {username} elevated privileges to {privilege_level}",
                "Account {username} locked after {failed_attempts} failed attempts",
            ],
            "file_system_log": [
                "File created: {file_path} by process {process_name} (PID: {pid})",
                "File {file_path} was modified by user {username}",
                "Directory {directory_path} was accessed by {process_name}",
                "File {file_path} was deleted by user {username}",
            ],
            "security_alert": [
                "Malware detected: {malware_name} in file {file_path}",
                "Suspicious behavior detected: {behavior_description}",
                "Security rule triggered: {rule_name} - {rule_description}",
                "Anomaly detected: {anomaly_type} from source {source}",
            ],
        }

        # Sample data for evidence generation
        self.sample_data = {
            "process_names": [
                "powershell.exe",
                "cmd.exe",
                "rundll32.exe",
                "regsvr32.exe",
                "wscript.exe",
                "cscript.exe",
                "mshta.exe",
                "certutil.exe",
                "svchost.exe",
                "winlogon.exe",
                "explorer.exe",
                "chrome.exe",
            ],
            "malicious_processes": [
                "evil.exe",
                "payload.exe",
                "backdoor.exe",
                "keylogger.exe",
                "trojan.exe",
                "ransomware.exe",
                "miner.exe",
                "stealer.exe",
            ],
            "file_paths": [
                "C:\\Windows\\Temp\\file.exe",
                "C:\\Users\\Public\\document.doc",
                "C:\\ProgramData\\update.exe",
                "C:\\Windows\\System32\\malware.dll",
                "/tmp/evil_script.sh",
                "/var/tmp/payload",
                "/home/user/suspicious.bin",
            ],
            "domains": [
                "malicious-domain.com",
                "evil-c2.net",
                "bad-actor.org",
                "suspicious-site.info",
                "phishing-site.com",
                "malware-host.biz",
            ],
            "ip_addresses": [
                "192.168.1.100",
                "10.0.0.50",
                "172.16.1.200",
                "203.0.113.45",
                "198.51.100.23",
                "192.0.2.150",
            ],
            "malicious_ips": [
                "185.220.101.42",
                "45.142.214.123",
                "94.102.61.44",
                "138.197.148.152",
                "159.203.176.62",
                "104.248.144.120",
            ],
            "usernames": [
                "admin",
                "administrator",
                "user",
                "service_account",
                "backup_user",
                "temp_user",
                "guest",
                "operator",
            ],
        }

    def generate_evidence_for_scenario(
        self, scenario_data: Dict[str, Any], num_items: int = 10
    ) -> List[EvidenceItem]:
        """Generate evidence items for a complete scenario"""
        evidence_items = []

        # Get scenario timeline and attack chain
        timeline = scenario_data.get("timeline", {})
        attack_chain = scenario_data.get("attack_chain", [])

        # Generate evidence for each phase of the attack
        for phase in attack_chain:
            phase_evidence = self._generate_phase_evidence(phase, timeline)
            evidence_items.extend(phase_evidence)

        # Add some red herrings and contextual evidence
        red_herrings = self._generate_red_herrings(scenario_data, max_items=3)
        evidence_items.extend(red_herrings)

        # Limit to requested number of items
        if len(evidence_items) > num_items:
            # Keep most important evidence
            evidence_items.sort(
                key=lambda x: self._get_importance_weight(x.importance), reverse=True
            )
            evidence_items = evidence_items[:num_items]

        return evidence_items

    def _generate_phase_evidence(
        self, phase: Dict[str, Any], timeline: Dict[str, Any]
    ) -> List[EvidenceItem]:
        """Generate evidence for a specific attack phase"""
        evidence_items = []

        phase_name = phase.get("name", "Unknown Phase")
        techniques = phase.get("techniques", [])
        phase_time = self._get_phase_timestamp(phase_name, timeline)

        for technique in techniques:
            # Generate 1-3 evidence items per technique
            num_items = random.randint(1, 3)
            for _ in range(num_items):
                evidence = self._generate_technique_evidence(technique, phase_time)
                if evidence:
                    evidence_items.append(evidence)

        return evidence_items

    def _generate_technique_evidence(
        self, technique: Dict[str, Any], base_time: datetime
    ) -> Optional[EvidenceItem]:
        """Generate evidence for a specific MITRE technique"""
        technique_id = technique.get("id", "")
        technique_name = technique.get("name", "Unknown Technique")

        # Determine evidence type based on technique
        evidence_type = self._get_evidence_type_for_technique(technique_id)

        # Generate timestamp (within +/- 30 minutes of base time)
        timestamp = base_time + timedelta(minutes=random.randint(-30, 30))

        # Generate content based on evidence type
        content = self._generate_evidence_content(evidence_type, technique)

        # Determine importance and reliability
        importance = self._determine_evidence_importance(technique_id)
        reliability = random.choice(
            ["high", "medium", "high"]
        )  # Bias toward reliable evidence

        # Generate tags
        tags = self._generate_evidence_tags(technique, evidence_type)

        return EvidenceItem(
            id=str(uuid.uuid4())[:8],
            type=evidence_type,
            source=self._get_evidence_source(evidence_type),
            timestamp=timestamp,
            content=content,
            importance=importance,
            reliability=reliability,
            tags=tags,
            related_techniques=[technique_id],
            metadata={"technique_name": technique_name, "generated": True},
        )

    def _get_evidence_type_for_technique(self, technique_id: str) -> str:
        """Determine appropriate evidence type for a MITRE technique"""
        technique_mappings = {
            "T1566": "security_alert",  # Phishing
            "T1059": "process_log",  # Command and Scripting Interpreter
            "T1055": "process_log",  # Process Injection
            "T1003": "authentication_log",  # OS Credential Dumping
            "T1083": "file_system_log",  # File and Directory Discovery
            "T1021": "network_log",  # Remote Services
            "T1071": "network_log",  # Application Layer Protocol
            "T1486": "file_system_log",  # Data Encrypted for Impact
        }

        # Check for technique family match
        for tech_prefix, evidence_type in technique_mappings.items():
            if technique_id.startswith(tech_prefix):
                return evidence_type

        # Default to process log
        return "process_log"

    def _generate_evidence_content(
        self, evidence_type: str, technique: Dict[str, Any]
    ) -> str:
        """Generate realistic content for evidence"""
        templates = self.log_templates.get(
            evidence_type, self.log_templates["process_log"]
        )
        template = random.choice(templates)

        # Generate appropriate data for template
        data = self._generate_template_data(evidence_type, technique)

        try:
            return template.format(**data)
        except KeyError:
            # Fallback if template formatting fails
            return f"Evidence related to {technique.get('name', 'security incident')}"

    def _generate_template_data(
        self, evidence_type: str, technique: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate data to fill evidence templates"""
        base_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pid": random.randint(1000, 9999),
            "child_pid": random.randint(1000, 9999),
            "exit_code": random.choice([0, 1, -1, 127]),
            "src_port": random.randint(1024, 65535),
            "dst_port": random.choice([80, 443, 8080, 3389, 22, 53]),
            "protocol": random.choice(["TCP", "UDP", "HTTP", "HTTPS"]),
            "status_code": random.choice([200, 404, 403, 500]),
            "failed_attempts": random.randint(3, 10),
            "privilege_level": random.choice(["Administrator", "SYSTEM", "root"]),
            "rule_name": f"RULE_{random.randint(1000, 9999)}",
            "behavior_description": "Unusual network activity pattern detected",
            "anomaly_type": "Statistical anomaly in process behavior",
            "source": "Security monitoring system",
        }

        # Add type-specific data
        if evidence_type == "process_log":
            technique_id = technique.get("id", "")
            if "T1059" in technique_id:  # Command line execution
                base_data.update(
                    {
                        "process_name": random.choice(
                            ["powershell.exe", "cmd.exe", "wscript.exe"]
                        ),
                        "command_line": "powershell.exe -ExecutionPolicy Bypass -File malicious.ps1",
                        "child_process": random.choice(
                            self.sample_data["malicious_processes"]
                        ),
                    }
                )
            else:
                base_data.update(
                    {
                        "process_name": random.choice(
                            self.sample_data["process_names"]
                        ),
                        "command_line": f"{random.choice(self.sample_data['process_names'])} -arg1 -arg2",
                        "child_process": random.choice(
                            self.sample_data["process_names"]
                        ),
                    }
                )

        elif evidence_type == "network_log":
            base_data.update(
                {
                    "src_ip": random.choice(self.sample_data["ip_addresses"]),
                    "dst_ip": random.choice(self.sample_data["malicious_ips"]),
                    "domain": random.choice(self.sample_data["domains"]),
                    "resolved_ip": random.choice(self.sample_data["malicious_ips"]),
                    "url": f"http://{random.choice(self.sample_data['domains'])}/malicious_path",
                }
            )

        elif evidence_type == "authentication_log":
            base_data.update(
                {
                    "username": random.choice(self.sample_data["usernames"]),
                    "src_ip": random.choice(self.sample_data["ip_addresses"]),
                }
            )

        elif evidence_type == "file_system_log":
            base_data.update(
                {
                    "file_path": random.choice(self.sample_data["file_paths"]),
                    "directory_path": "C:\\Windows\\Temp\\",
                    "process_name": random.choice(self.sample_data["process_names"]),
                    "username": random.choice(self.sample_data["usernames"]),
                }
            )

        elif evidence_type == "security_alert":
            base_data.update(
                {
                    "malware_name": f"Trojan.Win32.{random.choice(['Emotet', 'Trickbot', 'Cobalt', 'Beacon'])}",
                    "file_path": random.choice(self.sample_data["file_paths"]),
                    "rule_description": "Suspicious process execution pattern detected",
                }
            )

        return base_data

    def _get_phase_timestamp(
        self, phase_name: str, timeline: Dict[str, Any]
    ) -> datetime:
        """Get timestamp for a specific attack phase"""
        # Default timeline if none provided
        base_time = datetime.now() - timedelta(hours=24)

        phase_offsets = {
            "Initial Access": timedelta(hours=0),
            "Execution": timedelta(minutes=30),
            "Persistence": timedelta(hours=1),
            "Privilege Escalation": timedelta(hours=2),
            "Defense Evasion": timedelta(hours=3),
            "Credential Access": timedelta(hours=4),
            "Discovery": timedelta(hours=5),
            "Lateral Movement": timedelta(hours=6),
            "Collection": timedelta(hours=8),
            "Command and Control": timedelta(hours=1),  # Often throughout
            "Exfiltration": timedelta(hours=10),
            "Impact": timedelta(hours=12),
        }

        offset = phase_offsets.get(phase_name, timedelta(hours=random.randint(1, 12)))
        return base_time + offset

    def _determine_evidence_importance(self, technique_id: str) -> str:
        """Determine importance level for evidence based on technique"""
        critical_techniques = [
            "T1486",
            "T1003",
            "T1055",
        ]  # Ransomware, credential dumping, injection
        high_techniques = ["T1566", "T1059", "T1071"]  # Phishing, execution, C2

        if any(tech in technique_id for tech in critical_techniques):
            return "critical"
        elif any(tech in technique_id for tech in high_techniques):
            return "high"
        else:
            return random.choice(
                ["medium", "medium", "high"]
            )  # Bias toward medium/high

    def _generate_evidence_tags(
        self, technique: Dict[str, Any], evidence_type: str
    ) -> List[str]:
        """Generate relevant tags for evidence"""
        tags = [evidence_type.replace("_", "-")]

        # Add technique-based tags
        technique_name = technique.get("name", "").lower()
        if "powershell" in technique_name:
            tags.append("powershell")
        if "network" in technique_name or "remote" in technique_name:
            tags.append("network")
        if "file" in technique_name:
            tags.append("file-system")
        if "credential" in technique_name or "password" in technique_name:
            tags.append("credentials")

        # Add evidence type specific tags
        if evidence_type == "security_alert":
            tags.extend(["alert", "detection"])
        elif evidence_type == "network_log":
            tags.extend(["network", "connection"])
        elif evidence_type == "process_log":
            tags.extend(["process", "execution"])

        return tags

    def _get_evidence_source(self, evidence_type: str) -> str:
        """Get appropriate source for evidence type"""
        sources = {
            "process_log": "Windows Event Log (Process Creation)",
            "network_log": "Firewall Logs",
            "authentication_log": "Domain Controller Logs",
            "file_system_log": "File Integrity Monitoring",
            "security_alert": "Endpoint Detection and Response",
        }
        return sources.get(evidence_type, "Security Monitoring System")

    def _generate_red_herrings(
        self, scenario_data: Dict[str, Any], max_items: int = 3
    ) -> List[EvidenceItem]:
        """Generate red herring evidence to add complexity"""
        red_herrings = []

        # Generate benign but suspicious-looking evidence
        for i in range(random.randint(1, max_items)):
            evidence_type = random.choice(list(self.log_templates.keys()))

            red_herring = EvidenceItem(
                id=f"rh_{i:03d}",
                type=evidence_type,
                source=self._get_evidence_source(evidence_type),
                timestamp=datetime.now() - timedelta(hours=random.randint(1, 48)),
                content=self._generate_red_herring_content(evidence_type),
                importance="low",
                reliability=random.choice(["medium", "low"]),
                tags=["red-herring", evidence_type.replace("_", "-")],
                metadata={"is_red_herring": True, "generated": True},
            )
            red_herrings.append(red_herring)

        return red_herrings

    def _generate_red_herring_content(self, evidence_type: str) -> str:
        """Generate content for red herring evidence"""
        red_herring_templates = {
            "process_log": [
                "Process created: update_checker.exe (PID: 1234) - Normal system update",
                "Process svchost.exe performed routine maintenance task",
                "Scheduled task executed: SystemBackup - completed successfully",
            ],
            "network_log": [
                "Connection to update.microsoft.com - Windows Update service",
                "DNS query for time.nist.gov - NTP synchronization",
                "HTTPS connection to corporate.sharepoint.com - Normal user activity",
            ],
            "authentication_log": [
                "User service_account scheduled login - automated process",
                "User admin performed routine administrative task",
                "Scheduled service authentication - backup service",
            ],
            "file_system_log": [
                "File created: C:\\Windows\\Temp\\update_log.txt - System update",
                "Directory accessed: C:\\Program Files\\Common Files - Normal operation",
                "File modified: user_preferences.ini - User settings update",
            ],
            "security_alert": [
                "Information: Scheduled scan completed - No threats found",
                "Warning: System resource usage high - Non-critical",
                "Notice: Certificate renewal reminder - Routine maintenance",
            ],
        }

        templates = red_herring_templates.get(
            evidence_type, ["Normal system activity detected"]
        )
        return random.choice(templates)

    def _get_importance_weight(self, importance: str) -> int:
        """Get numeric weight for importance level"""
        weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return weights.get(importance, 1)

    def generate_evidence_for_technique(
        self,
        technique_id: str,
        phase: str = None,
        sector: str = None,
        infrastructure: str = None,
        num_items: int = 3,
    ) -> List[EvidenceItem]:
        """Generate evidence items for a specific MITRE technique"""
        evidence_items = []

        # Create a mock technique object for internal methods
        technique = {
            "id": technique_id,
            "name": self._get_technique_name(technique_id),
            "phase": phase,
        }

        # Generate base timestamp for the phase
        base_time = self._get_phase_timestamp(phase or "Unknown", {})

        # Generate the requested number of evidence items
        for i in range(num_items):
            evidence = self._generate_technique_evidence(technique, base_time)
            if evidence:
                # Customize based on sector and infrastructure if provided
                if sector or infrastructure:
                    evidence = self._customize_evidence_for_context(
                        evidence, sector, infrastructure
                    )
                evidence_items.append(evidence)

        return evidence_items

    def generate_red_herring(
        self, herring_type: str, sector: str = None, infrastructure: str = None
    ) -> EvidenceItem:
        """Generate a single red herring evidence item"""

        # Map herring types to evidence types
        type_mapping = {
            "benign_process": "process_log",
            "legitimate_network": "network_log",
            "system_auth": "authentication_log",
            "maintenance_file": "file_system_log",
            "info_alert": "security_alert",
        }

        evidence_type = type_mapping.get(herring_type, "process_log")

        # Generate timestamp (recent but not too recent)
        timestamp = datetime.now() - timedelta(hours=random.randint(2, 48))

        # Generate content
        content = self._generate_red_herring_content(evidence_type)

        # Customize for sector/infrastructure if provided
        if sector or infrastructure:
            content = self._customize_red_herring_for_context(
                content, sector, infrastructure
            )

        return EvidenceItem(
            id=f"rh_{str(uuid.uuid4())[:8]}",
            type=evidence_type,
            source=self._get_evidence_source(evidence_type),
            timestamp=timestamp,
            content=content,
            importance="low",
            reliability=random.choice(
                ["medium", "low", "medium"]
            ),  # Bias toward medium
            tags=["red-herring", evidence_type.replace("_", "-")],
            metadata={
                "is_red_herring": True,
                "generated": True,
                "herring_type": herring_type,
            },
        )

    def _get_technique_name(self, technique_id: str) -> str:
        """Get a human-readable name for a MITRE technique ID"""
        technique_names = {
            "T1566": "Phishing",
            "T1059": "Command and Scripting Interpreter",
            "T1055": "Process Injection",
            "T1003": "OS Credential Dumping",
            "T1083": "File and Directory Discovery",
            "T1021": "Remote Services",
            "T1071": "Application Layer Protocol",
            "T1486": "Data Encrypted for Impact",
            "T1027": "Obfuscated Files or Information",
            "T1078": "Valid Accounts",
            "T1082": "System Information Discovery",
            "T1049": "System Network Connections Discovery",
        }

        # Check for exact match first
        if technique_id in technique_names:
            return technique_names[technique_id]

        # Check for technique family match (e.g., T1059.001 -> T1059)
        base_technique = technique_id.split(".")[0]
        if base_technique in technique_names:
            return technique_names[base_technique]

        return f"Technique {technique_id}"

    def _customize_evidence_for_context(
        self, evidence: EvidenceItem, sector: str = None, infrastructure: str = None
    ) -> EvidenceItem:
        """Customize evidence content based on sector and infrastructure"""

        # Sector-specific customizations
        if sector:
            if sector.lower() in ["healthcare", "medical"]:
                evidence.content = evidence.content.replace(
                    "document.doc", "patient_records.xlsx"
                )
                evidence.content = evidence.content.replace(
                    "file.exe", "medical_software.exe"
                )
            elif sector.lower() in ["finance", "financial", "banking"]:
                evidence.content = evidence.content.replace(
                    "document.doc", "transaction_data.csv"
                )
                evidence.content = evidence.content.replace("user", "account_mgr")
            elif sector.lower() in ["energy", "utility", "power"]:
                evidence.content = evidence.content.replace(
                    "document.doc", "scada_config.cfg"
                )
                evidence.content = evidence.content.replace("user", "operator")

        # Infrastructure-specific customizations
        if infrastructure:
            if infrastructure.lower() in ["cloud", "aws", "azure", "gcp"]:
                evidence.content = evidence.content.replace("C:\\Windows", "/var/log")
                evidence.content = evidence.content.replace("192.168.", "10.0.")
            elif infrastructure.lower() in ["hybrid"]:
                # Mix of on-prem and cloud indicators
                if random.choice([True, False]):
                    evidence.content = evidence.content.replace(
                        "C:\\Windows", "/opt/app"
                    )

        return evidence

    def _customize_red_herring_for_context(
        self, content: str, sector: str = None, infrastructure: str = None
    ) -> str:
        """Customize red herring content for sector and infrastructure"""

        if sector:
            if sector.lower() in ["healthcare", "medical"]:
                content = content.replace("corporate", "hospital")
                content = content.replace("update", "medical_system_update")
            elif sector.lower() in ["finance", "financial"]:
                content = content.replace("corporate", "trading_platform")
                content = content.replace("backup", "transaction_backup")
            elif sector.lower() in ["energy", "utility"]:
                content = content.replace("corporate", "control_system")
                content = content.replace("maintenance", "grid_maintenance")

        if infrastructure and infrastructure.lower() in ["cloud"]:
            content = content.replace("C:\\Windows", "/var/lib")
            content = content.replace("svchost.exe", "systemd")

        return content
