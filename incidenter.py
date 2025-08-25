#!/usr/bin/env python3
"""
Incidenter CLI - Tabletop Cybersecurity Incident Response Game

Main entry point for the incidenter game system.
"""

import os
import sys
import click
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from cli.generator import ScenarioGenerator
from cli.game_session import GameSession
from cli.scenario_manager import ScenarioManager

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🚨 Incidenter - CLI Tabletop Cybersecurity Incident Game 🚨

    Practice incident response skills with realistic scenarios based on
    historical cyberattacks. Work as a team to identify attack techniques,
    build timelines, and uncover the full kill chain.
    """
    pass


@cli.command()
@click.option(
    "--sector",
    type=click.Choice(
        [
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
        ]
    ),
    help="Target organization sector",
)
@click.option(
    "--org-size",
    type=click.Choice(["small", "medium", "large", "enterprise"]),
    help="Organization size",
)
@click.option(
    "--infra",
    type=click.Choice(["on-premises", "cloud", "hybrid"]),
    help="Infrastructure type",
)
@click.option(
    "--complexity",
    type=click.Choice(["beginner", "intermediate", "advanced", "expert"]),
    default="intermediate",
    help="Scenario difficulty level",
)
@click.option("--base-attack", help="Base the scenario on a specific historical attack")
@click.option("--output", "-o", help="Output file path for generated scenario")
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive scenario generation with prompts",
)
def generate(sector, org_size, infra, complexity, base_attack, output, interactive):
    """Generate a new incident scenario."""

    console.print("\n🎲 [bold blue]Generating New Incident Scenario[/bold blue]")

    try:
        generator = ScenarioGenerator()

        if interactive:
            scenario = generator.interactive_generation()
        else:
            scenario = generator.generate_scenario(
                sector=sector,
                org_size=org_size,
                infrastructure=infra,
                complexity=complexity,
                base_attack=base_attack,
            )

        if output:
            output_path = Path(output)
        else:
            scenarios_dir = Path("scenarios/generated")
            scenarios_dir.mkdir(parents=True, exist_ok=True)
            output_path = (
                scenarios_dir / f"{scenario['scenario_metadata']['id'].lower()}.yaml"
            )

        # Save generated scenario
        clean_scenario = clean_scenario_for_yaml(scenario)
        with open(output_path, "w") as f:
            yaml.dump(clean_scenario, f, default_flow_style=False, indent=2)

        console.print("\n✅ [green]Scenario generated successfully![/green]")
        console.print(f"📁 Saved to: {output_path}")

        # Display scenario summary
        meta = scenario["scenario_metadata"]
        panel_content = f"""
[bold]Name:[/bold] {meta['name']}
[bold]ID:[/bold] {meta['id']}
[bold]Sector:[/bold] {meta['environment']['sector']}
[bold]Difficulty:[/bold] {meta['difficulty']}
[bold]Duration:[/bold] {meta['estimated_duration']}
[bold]Inspiration:[/bold] {meta.get('inspiration', {}).get('attack_name', 'Custom')}
        """

        console.print(
            Panel(
                panel_content.strip(), title="📋 Scenario Summary", border_style="green"
            )
        )

    except Exception as e:
        console.print(f"\n❌ [red]Error generating scenario: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("scenario_file")
@click.option(
    "--facilitator-model",
    default="gemini-2.0-flash-001",
    help="AI model to use for facilitation (e.g., gemini-2.0-flash-001, gemini-1.5-flash-001)",
)
@click.option(
    "--team-size",
    type=int,
    default=1,
    help="Number of players on the incident response team",
)
@click.option(
    "--difficulty-adjustment",
    type=click.Choice(["easier", "normal", "harder"]),
    default="normal",
    help="Adjust scenario difficulty on the fly",
)
def play(scenario_file, facilitator_model, team_size, difficulty_adjustment):
    """Start an interactive incident response game session."""

    if not Path(scenario_file).exists():
        console.print(f"❌ [red]Scenario file not found: {scenario_file}[/red]")
        sys.exit(1)

    console.print("\n🚨 [bold red]INCIDENT RESPONSE EXERCISE[/bold red]")
    console.print(
        "[yellow]Loading scenario and initializing AI facilitator...[/yellow]\n"
    )

    try:
        # Load scenario
        with open(scenario_file, "r") as f:
            scenario = yaml.safe_load(f)

        # Initialize game session
        game = GameSession(
            scenario=scenario,
            facilitator_model=facilitator_model,
            team_size=team_size,
            difficulty_adjustment=difficulty_adjustment,
        )

        # Start the game
        game.start_session()

    except Exception as e:
        console.print(f"❌ [red]Error starting game session: {e}[/red]")
        sys.exit(1)


@cli.command("list-scenarios")
@click.option(
    "--library", "-l", is_flag=True, help="Show only pre-built library scenarios"
)
@click.option("--generated", "-g", is_flag=True, help="Show only generated scenarios")
def list_scenarios(library, generated):
    """List available scenarios."""

    console.print("\n📚 [bold blue]Available Scenarios[/bold blue]\n")

    manager = ScenarioManager()
    scenarios = manager.list_scenarios(library_only=library, generated_only=generated)

    if not scenarios:
        console.print("[yellow]No scenarios found.[/yellow]")
        return

    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Sector", style="green")
    table.add_column("Difficulty", style="yellow")
    table.add_column("Inspiration", style="blue")
    table.add_column("Type", style="red")

    for scenario in scenarios:
        meta = scenario["metadata"]
        scenario_type = "Library" if scenario["is_library"] else "Generated"

        table.add_row(
            meta["id"],
            meta["name"],
            meta["environment"]["sector"],
            meta["difficulty"],
            meta.get("inspiration", {}).get("attack_name", "Custom"),
            scenario_type,
        )

    console.print(table)


@cli.command()
@click.argument("scenario_file", required=False)
@click.option(
    "--all",
    is_flag=True,
    help="Validate all scenario files in the scenarios folder",
)
@click.option(
    "--library-only",
    is_flag=True,
    help="Only validate library scenarios (excludes generated)",
)
@click.option(
    "--generated-only",
    is_flag=True,
    help="Only validate generated scenarios (excludes library)",
)
def validate(scenario_file, all, library_only, generated_only):
    """Validate scenario file(s) against the template schema.

    If no scenario_file is provided and --all is not specified,
    validates all scenarios by default.
    """

    if library_only and generated_only:
        console.print(
            "❌ [red]Cannot specify both --library-only and --generated-only[/red]"
        )
        sys.exit(1)

    # If no file specified and no --all flag, default to validating all
    if not scenario_file and not all:
        all = True

    if all or not scenario_file:
        # Validate all scenarios
        console.print("\n🔍 [bold blue]Validating All Scenarios[/bold blue]\n")

        manager = ScenarioManager()

        # Get list of scenarios to validate
        if library_only:
            scenarios = manager.list_scenarios(library_only=True)
        elif generated_only:
            scenarios = manager.list_scenarios(generated_only=True)
        else:
            scenarios = manager.list_scenarios()

        if not scenarios:
            console.print("📁 [yellow]No scenario files found to validate[/yellow]")
            return

        # Validate each scenario
        total_scenarios = len(scenarios)
        valid_scenarios = 0
        invalid_scenarios = 0
        validation_results = []

        for scenario_info in scenarios:
            scenario_path = scenario_info["file_path"]
            scenario_name = scenario_info["metadata"].get(
                "name", Path(scenario_path).stem
            )

            try:
                is_valid, errors = manager.validate_scenario(scenario_path)

                if is_valid:
                    valid_scenarios += 1
                    validation_results.append(
                        {
                            "file": scenario_path,
                            "name": scenario_name,
                            "valid": True,
                            "errors": [],
                        }
                    )
                    console.print(
                        f"✅ [green]{scenario_name}[/green] ({Path(scenario_path).name})"
                    )
                else:
                    invalid_scenarios += 1
                    validation_results.append(
                        {
                            "file": scenario_path,
                            "name": scenario_name,
                            "valid": False,
                            "errors": errors,
                        }
                    )
                    console.print(
                        f"❌ [red]{scenario_name}[/red] ({Path(scenario_path).name})"
                    )
                    for error in errors:
                        console.print(f"   • {error}")

            except Exception as e:
                invalid_scenarios += 1
                validation_results.append(
                    {
                        "file": scenario_path,
                        "name": scenario_name,
                        "valid": False,
                        "errors": [f"Exception during validation: {e}"],
                    }
                )
                console.print(
                    f"❌ [red]{scenario_name}[/red] ({Path(scenario_path).name}) - Error: {e}"
                )

        # Print summary
        console.print(f"\n📊 [bold blue]Validation Summary[/bold blue]")
        console.print(f"[green]✅ Valid scenarios: {valid_scenarios}[/green]")
        console.print(f"[red]❌ Invalid scenarios: {invalid_scenarios}[/red]")
        console.print(f"[blue]📁 Total scenarios: {total_scenarios}[/blue]")

        if invalid_scenarios > 0:
            console.print(
                f"\n[yellow]⚠️  {invalid_scenarios} scenario(s) failed validation[/yellow]"
            )
            sys.exit(1)
        else:
            console.print(f"\n[green]🎉 All scenarios are valid![/green]")

    else:
        # Validate single scenario file
        if not Path(scenario_file).exists():
            console.print(f"❌ [red]Scenario file not found: {scenario_file}[/red]")
            sys.exit(1)

        console.print(
            f"\n🔍 [bold blue]Validating Scenario[/bold blue]: {scenario_file}"
        )

        try:
            manager = ScenarioManager()
            is_valid, errors = manager.validate_scenario(scenario_file)

            if is_valid:
                console.print("✅ [green]Scenario is valid![/green]")
            else:
                console.print("❌ [red]Scenario validation failed:[/red]")
                for error in errors:
                    console.print(f"  • {error}")
                sys.exit(1)

        except Exception as e:
            console.print(f"❌ [red]Error validating scenario: {e}[/red]")
            sys.exit(1)


@cli.command()
@click.option(
    "--include-generated",
    is_flag=True,
    help="Include generated scenarios in statistics",
)
def stats(include_generated):
    """Show statistics about available scenarios."""

    console.print("\n📊 [bold blue]Scenario Statistics[/bold blue]\n")

    manager = ScenarioManager()
    stats_data = manager.get_statistics(include_generated=include_generated)

    # Total scenarios
    console.print(f"[bold]Total Scenarios:[/bold] {stats_data['total']}")
    console.print(f"[bold]Library Scenarios:[/bold] {stats_data['library_count']}")
    if include_generated:
        console.print(
            f"[bold]Generated Scenarios:[/bold] {stats_data['generated_count']}"
        )

    # By sector
    console.print("\n[bold]By Sector:[/bold]")
    for sector, count in stats_data["by_sector"].items():
        console.print(f"  • {sector.title()}: {count}")

    # By difficulty
    console.print("\n[bold]By Difficulty:[/bold]")
    for difficulty, count in stats_data["by_difficulty"].items():
        console.print(f"  • {difficulty.title()}: {count}")

    # By inspiration
    if stats_data["by_inspiration"]:
        console.print("\n[bold]By Historical Attack:[/bold]")
        for attack, count in stats_data["by_inspiration"].items():
            console.print(f"  • {attack}: {count}")


@cli.command()
def setup():
    """Initialize the incidenter environment and check dependencies."""

    console.print("\n🔧 [bold blue]Setting Up Incidenter[/bold blue]\n")

    # Create directory structure
    dirs_to_create = ["scenarios/library", "scenarios/generated", "logs", "exports"]

    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        console.print(f"✅ Created directory: {dir_path}")

    # Check Google Cloud authentication
    console.print("\n🔍 [bold]Checking Google Cloud Authentication[/bold]")

    auth_status = _check_gcp_authentication()

    if auth_status["has_credentials"]:
        console.print("✅ Google Cloud authentication: Available")
        if auth_status["method"] == "api_key":
            console.print("   📝 Using GOOGLE_AI_API_KEY")
        elif auth_status["method"] == "adc":
            console.print("   � Using Application Default Credentials (ADC)")
        elif auth_status["method"] == "service_account":
            console.print("   🔑 Using Service Account credentials")

        if auth_status["project"]:
            console.print(f"   🏗️  Project: {auth_status['project']}")
    else:
        console.print("❌ Google Cloud authentication: Not available")
        console.print(
            "\n[yellow]⚠️  AI facilitator will not work without proper authentication.[/yellow]"
        )
        console.print("\n[bold]Authentication Setup Options:[/bold]")
        console.print(
            "1. 🔑 [bold green]API Key (Recommended for personal use):[/bold green]"
        )
        console.print("   • Get your API key: https://makersuite.google.com/app/apikey")
        console.print(
            "   • Set environment variable: export GOOGLE_AI_API_KEY='your-api-key'"
        )
        console.print(
            "\n2. 🌐 [bold blue]Application Default Credentials (ADC):[/bold blue]"
        )
        console.print("   • For local development: gcloud auth login --update-adc")
        console.print("   • For production: Use service account with proper IAM roles")
        console.print("\n3. 🔑 [bold yellow]Service Account (Advanced):[/bold yellow]")
        console.print("   • Download service account key JSON")
        console.print(
            "   • Set: export GOOGLE_APPLICATION_CREDENTIALS='path/to/key.json'"
        )

    # Check project configuration
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id:
        console.print(f"✅ GOOGLE_CLOUD_PROJECT: {project_id}")
    else:
        console.print("❌ GOOGLE_CLOUD_PROJECT: Not set")
        console.print(
            "   💡 Set your project: export GOOGLE_CLOUD_PROJECT='your-project-id'"
        )

    # Test AI connection
    console.print("\n🤖 [bold]Testing AI Facilitator Connection[/bold]")

    if not auth_status["has_credentials"]:
        console.print("⏭️  Skipping AI connection test - no authentication available")
    else:
        try:
            from facilitator.ai_facilitator import AIFacilitator

            facilitator = AIFacilitator()
            test_result = facilitator.test_connection()
            if test_result:
                console.print("✅ AI facilitator connection successful")
                console.print(f"   🎯 Provider: Google AI ({facilitator.model})")
                console.print(f"   🔐 Authentication: {auth_status['method'].upper()}")
            else:
                console.print("❌ AI facilitator connection failed")
                console.print("   💡 Check your credentials and try again")
        except ImportError as e:
            console.print(f"❌ Missing AI dependencies: {e}")
            console.print("   💡 Run: pip install -r requirements.txt")
        except Exception as e:
            console.print(f"❌ Error testing AI facilitator: {e}")
            console.print("   💡 Check your authentication setup above")

    console.print("\n🎉 [bold green]Setup complete![/bold green]")

    if auth_status["has_credentials"]:
        console.print(
            "\n[bold green]✅ You're ready to use Incidenter with AI facilitation![/bold green]"
        )
        console.print("\nNext steps:")
        console.print(
            "1. Run '[cyan]python incidenter.py list-scenarios[/cyan]' to see available scenarios"
        )
        console.print(
            "2. Run '[cyan]python incidenter.py generate --interactive[/cyan]' to create a new scenario"
        )
        console.print(
            "3. Run '[cyan]python incidenter.py play <scenario_file>[/cyan]' to start a game session"
        )
    else:
        console.print(
            "\n[bold yellow]⚠️  Setup complete, but AI features require authentication[/bold yellow]"
        )
        console.print("\nNext steps:")
        console.print("1. Set up Google Cloud authentication (see options above)")
        console.print(
            "2. Run '[cyan]python incidenter.py setup[/cyan]' again to verify authentication"
        )
        console.print(
            "3. Run '[cyan]python incidenter.py list-scenarios[/cyan]' to see available scenarios"
        )
        console.print(
            "\n[dim]💡 You can still use basic scenario management without AI features[/dim]"
        )


def _check_gcp_authentication():
    """
    Check for available Google Cloud authentication methods.

    Returns:
        dict: Authentication status with method, project, and availability
    """
    auth_info = {
        "has_credentials": False,
        "method": None,
        "project": None,
        "details": [],
    }

    # Method 1: Check for GOOGLE_AI_API_KEY (preferred for Google AI)
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if api_key and api_key.strip():
        auth_info["has_credentials"] = True
        auth_info["method"] = "api_key"
        auth_info["project"] = os.getenv("GOOGLE_CLOUD_PROJECT", "default")
        return auth_info

    # Method 2: Check for Service Account credentials file
    service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if service_account_path and os.path.isfile(service_account_path):
        try:
            import json

            with open(service_account_path, "r") as f:
                sa_data = json.load(f)
                if "project_id" in sa_data:
                    auth_info["has_credentials"] = True
                    auth_info["method"] = "service_account"
                    auth_info["project"] = sa_data["project_id"]
                    return auth_info
        except (json.JSONDecodeError, IOError):
            pass

    # Method 3: Check for Application Default Credentials (ADC)
    try:
        from google.auth import default as google_default_credentials
        from google.auth.exceptions import DefaultCredentialsError

        credentials, project = google_default_credentials()
        if credentials:
            auth_info["has_credentials"] = True
            auth_info["method"] = "adc"
            auth_info["project"] = project or os.getenv("GOOGLE_CLOUD_PROJECT")
            return auth_info

    except ImportError:
        # google-auth not available
        pass
    except DefaultCredentialsError:
        # No ADC found
        pass
    except Exception:
        # Other ADC-related errors
        pass

    return auth_info


def clean_scenario_for_yaml(scenario):
    """Clean scenario data to ensure proper YAML serialization without Python objects"""
    import copy
    from datetime import datetime

    # Deep copy to avoid modifying original
    clean_scenario = copy.deepcopy(scenario)

    # Function to recursively clean any remaining objects
    def clean_value(value):
        if isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [clean_value(item) for item in value]
        elif isinstance(value, datetime):
            return value.isoformat()
        elif hasattr(value, "to_dict"):  # Handle any remaining dataclass objects
            return clean_value(value.to_dict())
        elif hasattr(value, "__dict__"):  # Handle any other objects
            return clean_value(value.__dict__)
        else:
            return value

    return clean_value(clean_scenario)


@cli.command()
@click.argument("scenario_file")
@click.option(
    "--output",
    "-o",
    help="Output file path for cleaned scenario YAML",
)
def clean(scenario_file, output):
    """Clean a scenario file for YAML serialization."""

    if not Path(scenario_file).exists():
        console.print(f"❌ [red]Scenario file not found: {scenario_file}[/red]")
        sys.exit(1)

    console.print(
        f"\n🧹 [bold blue]Cleaning Scenario for YAML[/bold blue]: {scenario_file}"
    )

    try:
        # Load scenario
        with open(scenario_file, "r") as f:
            scenario = yaml.safe_load(f)

        # Clean scenario data
        cleaned_scenario = clean_scenario_for_yaml(scenario)

        # Determine output path
        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"{scenario_file}.clean.yaml")

        # Save cleaned scenario
        with open(output_path, "w") as f:
            yaml.dump(cleaned_scenario, f, default_flow_style=False, indent=2)

        console.print("\n✅ [green]Scenario cleaned and saved successfully![/green]")
        console.print(f"📁 Saved to: {output_path}")

    except Exception as e:
        console.print(f"❌ [red]Error cleaning scenario: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
