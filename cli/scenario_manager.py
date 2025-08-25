"""
Scenario Manager Module

Manages scenario files, validation, and metadata operations.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict


class ScenarioManager:
    """Manages scenario files and metadata"""

    def __init__(self):
        self.library_dir = Path("scenarios/library")
        self.generated_dir = Path("scenarios/generated")
        self.templates_dir = Path("templates")

        # Ensure directories exist
        self.library_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)

    def list_scenarios(
        self, library_only: bool = False, generated_only: bool = False
    ) -> List[Dict]:
        """List all available scenarios with metadata"""

        scenarios = []

        if not generated_only:
            # Library scenarios
            for scenario_file in self.library_dir.glob("*.yaml"):
                try:
                    with open(scenario_file, "r") as f:
                        scenario = yaml.safe_load(f)
                    scenarios.append(
                        {
                            "file_path": str(scenario_file),
                            "metadata": scenario["scenario_metadata"],
                            "is_library": True,
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not load {scenario_file}: {e}")

        if not library_only:
            # Generated scenarios
            for scenario_file in self.generated_dir.glob("*.yaml"):
                try:
                    with open(scenario_file, "r") as f:
                        scenario = yaml.safe_load(f)
                    scenarios.append(
                        {
                            "file_path": str(scenario_file),
                            "metadata": scenario["scenario_metadata"],
                            "is_library": False,
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not load {scenario_file}: {e}")

        # Sort by name
        scenarios.sort(key=lambda x: x["metadata"]["name"])

        return scenarios

    def get_scenario(self, scenario_id: str) -> Optional[Dict]:
        """Get a specific scenario by ID"""

        scenarios = self.list_scenarios()

        for scenario_data in scenarios:
            if scenario_data["metadata"]["id"] == scenario_id:
                with open(scenario_data["file_path"], "r") as f:
                    return yaml.safe_load(f)

        return None

    def validate_scenario(self, scenario_file: str) -> Tuple[bool, List[str]]:
        """Validate a scenario file against the template schema"""

        errors = []

        try:
            with open(scenario_file, "r") as f:
                scenario = yaml.safe_load(f)
        except Exception as e:
            return False, [f"Failed to parse YAML: {e}"]

        # Check required top-level sections
        required_sections = [
            "scenario_metadata",
            "attack_overview",
            "initial_alert",
        ]

        for section in required_sections:
            if section not in scenario:
                errors.append(f"Missing required section: {section}")

        # Validate scenario_metadata
        if "scenario_metadata" in scenario:
            metadata = scenario["scenario_metadata"]
            required_metadata_fields = [
                "name",
                "id",
                "version",
                "environment",
                "difficulty",
            ]

            for field in required_metadata_fields:
                if field not in metadata:
                    errors.append(f"Missing required metadata field: {field}")

            # Validate environment section
            if "environment" in metadata:
                env = metadata["environment"]
                if "sector" not in env:
                    errors.append("Missing environment.sector")
                elif env["sector"] not in [
                    "finance",
                    "healthcare",
                    "government",
                    "technology",
                    "retail",
                    "energy",
                    "manufacturing",
                    "education",
                    "transportation",
                    "utilities",
                    "telecommunications",
                    "media",
                    "defense",
                ]:
                    errors.append(f"Invalid sector: {env['sector']}")

                if "organization" not in env:
                    errors.append("Missing environment.organization")
                elif not isinstance(env["organization"], dict):
                    errors.append("environment.organization must be a dictionary")

        # Validate kill_chain under attack_overview
        if (
            "attack_overview" in scenario
            and "kill_chain" in scenario["attack_overview"]
        ):
            kill_chain = scenario["attack_overview"]["kill_chain"]
            if isinstance(kill_chain, list):
                # New format: list of phases with phase, description, techniques
                for phase_item in kill_chain:
                    if not isinstance(phase_item, dict):
                        errors.append(
                            f"Kill chain phase must be a dictionary: {phase_item}"
                        )
                        continue

                    required_fields = ["phase", "description"]
                    for field in required_fields:
                        if field not in phase_item:
                            errors.append(f"Missing {field} in kill_chain phase")
            else:
                errors.append("attack_overview.kill_chain must be a list")

        # Validate initial_alert
        if "initial_alert" in scenario:
            alert = scenario["initial_alert"]
            required_alert_fields = ["alert_type", "timestamp", "description"]

            for field in required_alert_fields:
                if field not in alert:
                    errors.append(f"Missing {field} in initial_alert")

        return len(errors) == 0, errors

    def get_statistics(self, include_generated: bool = True) -> Dict[str, Any]:
        """Get statistics about scenarios"""

        scenarios = self.list_scenarios(
            generated_only=False if include_generated else True
        )

        stats = {
            "total": len(scenarios),
            "library_count": len([s for s in scenarios if s["is_library"]]),
            "generated_count": len([s for s in scenarios if not s["is_library"]]),
            "by_sector": defaultdict(int),
            "by_difficulty": defaultdict(int),
            "by_inspiration": defaultdict(int),
        }

        for scenario in scenarios:
            meta = scenario["metadata"]

            # Count by sector
            stats["by_sector"][meta["environment"]["sector"]] += 1

            # Count by difficulty
            stats["by_difficulty"][meta["difficulty"]] += 1

            # Count by inspiration
            inspiration = meta.get("inspiration", {})
            if inspiration and inspiration.get("attack_name"):
                stats["by_inspiration"][inspiration["attack_name"]] += 1

        # Convert defaultdicts to regular dicts for JSON serialization
        stats["by_sector"] = dict(stats["by_sector"])
        stats["by_difficulty"] = dict(stats["by_difficulty"])
        stats["by_inspiration"] = dict(stats["by_inspiration"])

        return stats

    def export_scenario(self, scenario_id: str, output_format: str = "yaml") -> str:
        """Export a scenario to different formats"""

        scenario = self.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario not found: {scenario_id}")

        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)

        if output_format.lower() == "json":
            output_file = export_dir / f"{scenario_id}.json"
            with open(output_file, "w") as f:
                json.dump(scenario, f, indent=2, default=str)
        elif output_format.lower() == "yaml":
            output_file = export_dir / f"{scenario_id}.yaml"
            with open(output_file, "w") as f:
                yaml.dump(scenario, f, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

        return str(output_file)

    def import_scenario(
        self, scenario_file: str, destination: str = "generated"
    ) -> bool:
        """Import a scenario file to the appropriate directory"""

        source_path = Path(scenario_file)
        if not source_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {scenario_file}")

        # Validate before importing
        is_valid, errors = self.validate_scenario(scenario_file)
        if not is_valid:
            raise ValueError(f"Invalid scenario file: {'; '.join(errors)}")

        # Load to get ID
        with open(scenario_file, "r") as f:
            scenario = yaml.safe_load(f)

        scenario_id = scenario["scenario_metadata"]["id"]

        if destination == "library":
            dest_path = self.library_dir / f"{scenario_id.lower()}.yaml"
        else:
            dest_path = self.generated_dir / f"{scenario_id.lower()}.yaml"

        # Copy file
        import shutil

        shutil.copy2(source_path, dest_path)

        return True

    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario file"""

        scenarios = self.list_scenarios()

        for scenario_data in scenarios:
            if scenario_data["metadata"]["id"] == scenario_id:
                Path(scenario_data["file_path"]).unlink()
                return True

        return False

    def search_scenarios(
        self, query: str, search_fields: List[str] = None
    ) -> List[Dict]:
        """Search scenarios by text query"""

        if search_fields is None:
            search_fields = ["name", "description", "sector", "inspiration.attack_name"]

        scenarios = self.list_scenarios()
        results = []

        query_lower = query.lower()

        for scenario in scenarios:
            meta = scenario["metadata"]
            match_found = False

            # Search in specified fields
            for field in search_fields:
                field_value = self._get_nested_field(meta, field)
                if field_value and query_lower in str(field_value).lower():
                    match_found = True
                    break

            if match_found:
                results.append(scenario)

        return results

    def _get_nested_field(self, data: Dict, field_path: str) -> Any:
        """Get nested field value using dot notation"""

        fields = field_path.split(".")
        value = data

        try:
            for field in fields:
                value = value[field]
            return value
        except (KeyError, TypeError):
            return None

    def create_scenario_index(self) -> Dict[str, Any]:
        """Create a searchable index of all scenarios"""

        scenarios = self.list_scenarios()
        index = {
            "scenarios": [],
            "sectors": set(),
            "difficulties": set(),
            "attack_inspirations": set(),
            "techniques": set(),
        }

        for scenario_data in scenarios:
            meta = scenario_data["metadata"]

            # Load full scenario to get techniques
            with open(scenario_data["file_path"], "r") as f:
                full_scenario = yaml.safe_load(f)

            scenario_index = {
                "id": meta["id"],
                "name": meta["name"],
                "file_path": scenario_data["file_path"],
                "sector": meta["environment"]["sector"],
                "difficulty": meta["difficulty"],
                "is_library": scenario_data["is_library"],
            }

            # Add inspiration if available
            if "inspiration" in meta and meta["inspiration"].get("attack_name"):
                scenario_index["inspiration"] = meta["inspiration"]["attack_name"]
                index["attack_inspirations"].add(meta["inspiration"]["attack_name"])

            # Extract techniques from kill chain
            if "kill_chain" in full_scenario:
                techniques = []
                for phase, phase_data in full_scenario["kill_chain"].items():
                    if "technique_id" in phase_data:
                        techniques.append(phase_data["technique_id"])
                        index["techniques"].add(phase_data["technique_id"])
                scenario_index["techniques"] = techniques

            index["scenarios"].append(scenario_index)
            index["sectors"].add(meta["environment"]["sector"])
            index["difficulties"].add(meta["difficulty"])

        # Convert sets to lists for JSON serialization
        index["sectors"] = list(index["sectors"])
        index["difficulties"] = list(index["difficulties"])
        index["attack_inspirations"] = list(index["attack_inspirations"])
        index["techniques"] = list(index["techniques"])

        # Save index
        index_file = Path("scenarios/index.json")
        with open(index_file, "w") as f:
            json.dump(index, f, indent=2)

        return index
