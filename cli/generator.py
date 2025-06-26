"""
Scenario Generator Module

Generates realistic cybersecurity incident scenarios based on historical attacks
and customizable parameters.
"""

import yaml
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from faker import Faker

from facilitator.ai_facilitator import AIFacilitator
from utils.mitre_data import MitreAttackHandler
from utils.evidence_generator import EvidenceGenerator

fake = Faker()


@dataclass
class ScenarioParams:
    """Parameters for scenario generation"""

    sector: str
    org_size: str
    infrastructure: str
    complexity: str
    base_attack: Optional[str] = None
    custom_requirements: Optional[Dict] = None


class ScenarioGenerator:
    """Generates incident scenarios using AI and predefined templates"""

    def __init__(self):
        self.facilitator = AIFacilitator()
        self.mitre = MitreAttackHandler()
        self.evidence_gen = EvidenceGenerator()

        # Load scenario templates and examples
        self.templates_dir = Path("templates")
        self.library_dir = Path("scenarios/library")

    def generate_scenario(
        self,
        sector: str = None,
        org_size: str = None,
        infrastructure: str = None,
        complexity: str = "intermediate",
        base_attack: str = None,
    ) -> Dict[str, Any]:
        """Generate a complete incident scenario"""

        # Create scenario parameters
        params = ScenarioParams(
            sector=sector
            or random.choice(
                ["finance", "healthcare", "government", "technology", "retail"]
            ),
            org_size=org_size
            or random.choice(["small", "medium", "large", "enterprise"]),
            infrastructure=infrastructure
            or random.choice(["on-premises", "cloud", "hybrid"]),
            complexity=complexity,
            base_attack=base_attack,
        )

        # Generate scenario using AI
        scenario = self._generate_with_ai(params)

        # Enhance with technical details
        scenario = self._add_technical_details(scenario, params)

        # Add red herrings
        scenario = self._add_red_herrings(scenario, params)

        # Generate evidence
        scenario = self._generate_evidence(scenario, params)

        # Add scoring rubric
        scenario = self._add_scoring_rubric(scenario, params)

        return scenario

    def interactive_generation(self) -> Dict[str, Any]:
        """Interactive scenario generation with user prompts"""
        from rich.console import Console
        from rich.prompt import Prompt, Confirm

        console = Console()
        console.print("\n🎮 [bold blue]Interactive Scenario Generation[/bold blue]\n")

        # Collect parameters interactively
        sector = Prompt.ask(
            "Select target sector",
            choices=["finance", "healthcare", "government", "technology", "retail"],
            default="technology",
        )

        org_size = Prompt.ask(
            "Select organization size",
            choices=["small", "medium", "large", "enterprise"],
            default="medium",
        )

        infrastructure = Prompt.ask(
            "Select infrastructure type",
            choices=["on-premises", "cloud", "hybrid"],
            default="hybrid",
        )

        complexity = Prompt.ask(
            "Select difficulty level",
            choices=["beginner", "intermediate", "advanced", "expert"],
            default="intermediate",
        )

        # Optional base attack
        use_base_attack = Confirm.ask("Base scenario on a specific historical attack?")
        base_attack = None
        if use_base_attack:
            historical_attacks = [
                "carbanak",
                "notpetya",
                "capital-one",
                "moveit",
                "solarwinds",
                "codecov",
                "kaseya",
                "colonial-pipeline",
                "wannacry",
                "equifax",
            ]
            base_attack = Prompt.ask("Select base attack", choices=historical_attacks)

        console.print("\n🤖 [yellow]Generating scenario with AI...[/yellow]")

        return self.generate_scenario(
            sector=sector,
            org_size=org_size,
            infrastructure=infrastructure,
            complexity=complexity,
            base_attack=base_attack,
        )

    def _generate_with_ai(self, params: ScenarioParams) -> Dict[str, Any]:
        """Use AI to generate the core scenario structure"""

        prompt = self._build_generation_prompt(params)

        # Get AI response
        ai_response = self.facilitator.generate_scenario(prompt)

        try:
            # Parse AI response as YAML/JSON
            if ai_response.strip().startswith("{"):
                scenario = json.loads(ai_response)
            else:
                scenario = yaml.safe_load(ai_response)
        except (json.JSONDecodeError, yaml.YAMLError):
            # Fallback to template-based generation
            scenario = self._generate_from_template(params)

        return scenario

    def _build_generation_prompt(self, params: ScenarioParams) -> str:
        """Build prompt for AI scenario generation"""

        # Load the template structure
        template_path = self.templates_dir / "scenario_template.yaml"
        with open(template_path, "r") as f:
            template_content = f.read()

        base_attack_context = ""
        if params.base_attack:
            base_attack_context = (
                f"\nBase this scenario on the {params.base_attack} attack, "
                f"but make it fictional and adapted to the specified environment."
            )

        prompt = f"""
Generate a realistic cybersecurity incident scenario with the following parameters:

**Requirements:**
- Sector: {params.sector}
- Organization Size: {params.org_size}
- Infrastructure: {params.infrastructure}
- Complexity: {params.complexity}{base_attack_context}

**Instructions:**
1. Create a fictional but realistic cyber incident scenario
2. Follow the YAML structure provided below
3. Include a complete MITRE ATT&CK kill chain
4. Generate realistic technical evidence for each phase
5. Create compelling red herrings (25% of total evidence)
6. Make the scenario appropriate for {params.complexity} level players
7. Ensure all evidence is technically accurate and forensically sound

**Template Structure:**
```yaml
{template_content}
```

Generate a complete scenario following this structure. Make it engaging, educational, and realistic.
"""

        return prompt

    def _generate_from_template(self, params: ScenarioParams) -> Dict[str, Any]:
        """Fallback template-based generation"""

        scenario_id = f"{params.sector.upper()[:2]}{params.complexity.upper()[:1]}-{random.randint(100, 999)}"

        org_names = {
            "finance": ["SecureBank Corp", "TrustFin Holdings", "GlobalCapital Ltd"],
            "healthcare": [
                "MedTech Systems",
                "HealthCare Partners",
                "Regional Medical",
            ],
            "government": [
                "State Agency Services",
                "Municipal Systems",
                "Federal Division",
            ],
            "technology": [
                "InnovateTech Solutions",
                "CloudFirst Systems",
                "DevOps Dynamics",
            ],
            "retail": ["GlobalRetail Chain", "E-Commerce Plus", "Retail Solutions Inc"],
        }

        org_name = random.choice(org_names[params.sector])

        scenario = {
            "scenario_metadata": {
                "name": f"{org_name} Cyber Incident",
                "id": scenario_id,
                "version": "1.0",
                "description": f"Investigate a cybersecurity incident targeting a {params.org_size} {params.sector} organization",
                "difficulty": params.complexity,
                "estimated_duration": self._get_duration(params.complexity),
                "category": "Generated Scenario",
                "scenario_type": "generated",
                "max_players": 6,
                "inspiration": {
                    "attack_name": params.base_attack or "Custom",
                    "year": random.randint(2020, 2024),
                    "attribution": "Unknown",
                    "references": [],
                },
                "environment": {
                    "sector": params.sector,
                    "organization": {
                        "name": org_name,
                        "size": params.org_size,
                        "employee_count": self._get_employee_count(params.org_size),
                        "annual_revenue": self._get_revenue_range(params.org_size),
                    },
                    "infrastructure": {
                        "type": params.infrastructure,
                        "primary_cloud": (
                            random.choice(["AWS", "Azure", "GCP"])
                            if "cloud" in params.infrastructure
                            else None
                        ),
                        "endpoints": self._get_endpoint_count(params.org_size),
                        "servers": self._get_server_count(params.org_size),
                        "critical_systems": self._get_critical_systems(params.sector),
                    },
                },
                "timeline": {
                    "attack_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "detection_time": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": "ongoing",
                },
                "learning_objectives": [
                    f"Understand {params.sector} sector security challenges",
                    f"Practice {params.complexity} level incident response",
                    "Analyze attack patterns and techniques",
                    "Develop threat hunting skills",
                ],
            },
            "attack_overview": {
                "summary": f"A cybersecurity incident targeting {org_name}, involving multiple attack techniques and requiring thorough investigation."
            },
        }

        return scenario

    def _add_technical_details(self, scenario: Dict, params: ScenarioParams) -> Dict:
        """Add realistic technical details to the scenario"""

        # Generate MITRE ATT&CK techniques based on complexity
        techniques = self.mitre.get_techniques_for_scenario(
            sector=params.sector,
            complexity=params.complexity,
            infrastructure=params.infrastructure,
        )

        # Build attack_overview with kill_chain
        if "attack_overview" not in scenario:
            scenario["attack_overview"] = {}

        # Create kill_chain as a list of phases (proper template format)
        kill_chain = []
        for phase, technique in techniques.items():
            kill_chain.append(
                {
                    "phase": phase,
                    "description": technique["description"],
                    "techniques": [technique["id"]],
                }
            )

        scenario["attack_overview"]["kill_chain"] = kill_chain

        # Add initial alert if not present
        if "initial_alert" not in scenario:
            scenario["initial_alert"] = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "Security Operations Center",
                "alert_type": "medium",
                "title": f"Suspicious Activity Detected - {params.sector.title()} Environment",
                "description": f"Anomalous behavior detected in {params.org_size} {params.sector} organization infrastructure",
            }

        # Add timeline if not present
        if "timeline" not in scenario:
            scenario["timeline"] = {
                "day_0": {
                    "09:00": "Initial compromise detected",
                    "10:30": "Investigation initiated",
                    "14:15": "Additional indicators discovered",
                }
            }

        return scenario

    def _add_red_herrings(self, scenario: Dict, params: ScenarioParams) -> Dict:
        """Add realistic red herring clues"""

        red_herrings = []

        # Generate red herrings based on scenario context
        herring_types = [
            "legitimate_admin_activity",
            "unrelated_malware",
            "false_positive_alert",
            "maintenance_activity",
            "user_error_artifact",
        ]

        # Calculate number of red herrings (25% of evidence)
        num_kill_chain_phases = len(
            scenario.get("attack_overview", {}).get("kill_chain", [])
        )
        num_herrings = max(2, num_kill_chain_phases // 3)

        for _ in range(num_herrings):
            herring_type = random.choice(herring_types)
            red_herring = self.evidence_gen.generate_red_herring(
                herring_type, params.sector, params.infrastructure
            )
            # Convert to dictionary and add description
            herring_dict = red_herring.to_dict()
            herring_dict["description"] = (
                f"Red herring: {herring_type.replace('_', ' ').title()}"
            )
            red_herrings.append(herring_dict)

        # Add red herrings to evidence items if evidence section exists
        if "evidence" not in scenario:
            scenario["evidence"] = {"items": []}

        scenario["evidence"]["items"].extend(red_herrings)

        return scenario

    def _generate_evidence(self, scenario: Dict, params: ScenarioParams) -> Dict:
        """Generate realistic evidence for each phase"""

        # Collect all evidence items from all phases
        all_evidence = []

        if (
            "attack_overview" in scenario
            and "kill_chain" in scenario["attack_overview"]
        ):
            for phase_info in scenario["attack_overview"]["kill_chain"]:
                phase_name = phase_info.get("phase", "Unknown")
                techniques = phase_info.get("techniques", [])

                for technique_id in techniques:
                    evidence_list = self.evidence_gen.generate_evidence_for_technique(
                        technique_id=technique_id,
                        phase=phase_name,
                        sector=params.sector,
                        infrastructure=params.infrastructure,
                    )

                    # Convert EvidenceItem objects to dictionaries and add description
                    for evidence_item in evidence_list:
                        evidence_dict = evidence_item.to_dict()
                        # Add description field that's expected in the template
                        evidence_dict["description"] = (
                            f"Evidence related to {phase_name} phase"
                        )
                        all_evidence.append(evidence_dict)

        # Structure evidence according to template format
        scenario["evidence"] = {"items": all_evidence}

        return scenario

    def _add_scoring_rubric(self, scenario: Dict, params: ScenarioParams) -> Dict:
        """Add scoring rubric based on scenario complexity"""

        complexity_multipliers = {
            "beginner": 1.0,
            "intermediate": 1.5,
            "advanced": 2.0,
            "expert": 2.5,
        }

        base_points = 100
        max_points = int(base_points * complexity_multipliers[params.complexity])

        scoring = {
            "max_points": max_points,
            "categories": [
                {
                    "category": "technique_identification",
                    "max_points": max_points // 3,
                    "criteria": [
                        {
                            "description": "Correctly identified initial access method",
                            "points": 10,
                        },
                        {
                            "description": "Identified persistence mechanism",
                            "points": 10,
                        },
                        {
                            "description": "Found lateral movement evidence",
                            "points": 15,
                        },
                        {"description": "Discovered data exfiltration", "points": 15},
                    ],
                },
                {
                    "category": "timeline_reconstruction",
                    "max_points": max_points // 3,
                    "criteria": [
                        {"description": "Accurate attack timeline", "points": 20},
                        {"description": "Correct sequence of events", "points": 15},
                        {"description": "Identified attack duration", "points": 10},
                    ],
                },
                {
                    "category": "attribution_analysis",
                    "max_points": max_points // 3,
                    "criteria": [
                        {"description": "Identified attacker TTPs", "points": 15},
                        {
                            "description": "Assessed threat actor sophistication",
                            "points": 10,
                        },
                        {"description": "Determined likely motivation", "points": 10},
                    ],
                },
            ],
            "bonus_points": [
                {"description": "Avoided all red herrings", "points": 10},
                {"description": "Identified additional IoCs", "points": 15},
                {"description": "Provided actionable remediation", "points": 10},
            ],
            "deductions": [
                {"description": "Fell for red herring", "points": -5},
                {"description": "Incorrect technique attribution", "points": -10},
                {"description": "Major timeline error", "points": -15},
            ],
        }

        scenario["scoring"] = scoring

        return scenario

    def _get_employee_count(self, org_size: str) -> int:
        """Get realistic employee count for organization size"""
        ranges = {
            "small": (50, 500),
            "medium": (500, 5000),
            "large": (5000, 50000),
            "enterprise": (50000, 200000),
        }
        min_count, max_count = ranges[org_size]
        return random.randint(min_count, max_count)

    def _get_revenue_range(self, org_size: str) -> str:
        """Get revenue range for organization size"""
        ranges = {
            "small": "$10M - $100M",
            "medium": "$100M - $1B",
            "large": "$1B - $10B",
            "enterprise": "$10B+",
        }
        return ranges[org_size]

    def _get_endpoint_count(self, org_size: str) -> int:
        """Get endpoint count for organization size"""
        ranges = {
            "small": (100, 1000),
            "medium": (1000, 10000),
            "large": (10000, 100000),
            "enterprise": (100000, 500000),
        }
        min_count, max_count = ranges[org_size]
        return random.randint(min_count, max_count)

    def _get_server_count(self, org_size: str) -> int:
        """Get server count for organization size"""
        ranges = {
            "small": (10, 100),
            "medium": (100, 1000),
            "large": (1000, 10000),
            "enterprise": (10000, 50000),
        }
        min_count, max_count = ranges[org_size]
        return random.randint(min_count, max_count)

    def _get_critical_systems(self, sector: str) -> List[Dict]:
        """Get critical systems for sector"""
        systems = {
            "finance": [
                {
                    "name": "Core Banking System",
                    "description": "Primary transaction processing",
                },
                {
                    "name": "ATM Network",
                    "description": "Automated teller machine infrastructure",
                },
                {
                    "name": "Trading Platform",
                    "description": "Securities trading system",
                },
                {
                    "name": "Risk Management System",
                    "description": "Financial risk assessment",
                },
            ],
            "healthcare": [
                {
                    "name": "Electronic Health Records",
                    "description": "Patient data management",
                },
                {
                    "name": "Medical Imaging System",
                    "description": "DICOM image storage and viewing",
                },
                {
                    "name": "Laboratory Information System",
                    "description": "Lab results and workflows",
                },
                {
                    "name": "Pharmacy Management",
                    "description": "Medication dispensing system",
                },
            ],
            "government": [
                {
                    "name": "Citizen Services Portal",
                    "description": "Public service applications",
                },
                {
                    "name": "Document Management",
                    "description": "Official records and forms",
                },
                {
                    "name": "Emergency Response System",
                    "description": "911 dispatch and coordination",
                },
                {
                    "name": "Tax Processing System",
                    "description": "Revenue collection and processing",
                },
            ],
            "technology": [
                {
                    "name": "Source Code Repository",
                    "description": "Software development assets",
                },
                {
                    "name": "CI/CD Pipeline",
                    "description": "Automated build and deployment",
                },
                {
                    "name": "Customer Data Platform",
                    "description": "User analytics and profiles",
                },
                {
                    "name": "Production Infrastructure",
                    "description": "Live service hosting",
                },
            ],
            "retail": [
                {
                    "name": "Point of Sale System",
                    "description": "Transaction processing",
                },
                {
                    "name": "Inventory Management",
                    "description": "Stock tracking and logistics",
                },
                {
                    "name": "E-commerce Platform",
                    "description": "Online shopping and payments",
                },
                {
                    "name": "Customer Loyalty System",
                    "description": "Rewards and promotions",
                },
            ],
        }

        sector_systems = systems.get(sector, systems["technology"])
        return random.sample(sector_systems, min(3, len(sector_systems)))

    def _get_duration(self, complexity: str) -> str:
        """Get estimated duration for complexity level"""
        durations = {
            "beginner": "30-45 minutes",
            "intermediate": "45-90 minutes",
            "advanced": "90-120 minutes",
            "expert": "2-3 hours",
        }
        return durations[complexity]
