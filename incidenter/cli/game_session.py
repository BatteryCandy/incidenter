"""
Game Session Module

Manages interactive incident response game sessions with AI facilitation.
"""

import time
import logging

# import random
from datetime import datetime
from typing import Dict
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from facilitator.ai_facilitator import get_facilitator
from facilitator.mock_facilitator import MockAIFacilitator
from scoring.scorer import IncidenterScorer
from utils.session_manager import SessionManager


class GameSession:
    """Interactive incident response game session"""

    def __init__(
        self,
        scenario: Dict,
        facilitator_model: str = "gemini-2.0-flash-001",
        team_size: int = 1,
        difficulty_adjustment: str = "normal",
    ):
        self.scenario = scenario
        self.console = Console()

        # Initialize AI facilitator with ADC support
        try:
            # If user passed just 'google', use the default Google model
            if facilitator_model == "google":
                facilitator_model = "gemini-2.0-flash-001"
                self.console.print(
                    "[yellow]💡 Using default Google model: gemini-2.0-flash-001[/yellow]"
                )

            self.facilitator = get_facilitator(model=facilitator_model)

            # Check if we got the mock facilitator from get_facilitator
            if (
                hasattr(self.facilitator, "__class__")
                and "Mock" in self.facilitator.__class__.__name__
            ):
                self.using_mock_facilitator = True
            else:
                self.facilitator.load_scenario(scenario)
                self.using_mock_facilitator = False

        except Exception as e:
            self.console.print(
                f"[yellow]⚠️  Fallback to mock facilitator ({str(e)[:50]}...)[/yellow]"
            )
            self.facilitator = MockAIFacilitator()
            self.facilitator.load_scenario(scenario)
            self.using_mock_facilitator = True

        self.scorer = IncidenterScorer()
        self.session_manager = SessionManager()

        # Session state
        self.team_size = team_size
        self.difficulty_adjustment = difficulty_adjustment
        self.session_id = self._generate_session_id()
        self.start_time = datetime.now()
        self.revealed_clues = set()
        self.investigation_history = []
        self.player_theories = []
        self.current_score = 0
        self.red_herrings_encountered = []

        # Game configuration
        self.max_investigations = self._get_max_investigations()
        self.red_herring_probability = 0.25

        # Setup logging
        self._setup_logging()

    def start_session(self):
        """Start the interactive game session"""

        try:
            self._display_welcome()
            self._display_initial_alert()
            self._main_game_loop()
            self._conclude_session()

        except KeyboardInterrupt:
            self._handle_early_exit()
        except Exception as e:
            self.console.print(f"\n❌ [red]Session error: {e}[/red]")
            logging.error(f"Session error: {e}", exc_info=True)

    def _display_welcome(self):
        """Display welcome message and scenario overview"""

        meta = self.scenario["scenario_metadata"]

        welcome_content = f"""
[bold blue]🚨 INCIDENT RESPONSE EXERCISE 🚨[/bold blue]

[bold]Scenario:[/bold] {meta['name']}
[bold]Organization:[/bold] {meta['environment']['organization']['name']}
[bold]Sector:[/bold] {meta['environment']['sector'].title()}
[bold]Difficulty:[/bold] {meta['difficulty'].title()}
[bold]Team Size:[/bold] {self.team_size}
[bold]Estimated Duration:[/bold] {meta['estimated_duration']}
{"[dim yellow]🤖 Using mock AI facilitator (demo mode)[/dim yellow]" if self.using_mock_facilitator else ""}

[yellow]You are the incident response team for this organization.
Your goal is to investigate the incident, identify the attack methodology,
and reconstruct the complete attack timeline.[/yellow]

[bold red]⚠️  Remember: Not all evidence is reliable. Stay vigilant for red herrings! ⚠️[/bold red]
        """

        self.console.print(Panel(welcome_content.strip(), border_style="blue"))

        # Brief pause for dramatic effect
        time.sleep(2)

        # Game instructions
        instructions = """
[bold]How to Play:[/bold]
• Ask specific investigative questions (e.g., "Check firewall logs", "Examine running processes")
• You can request up to {max_investigations} investigation questions
• The AI facilitator will provide one clue per investigation
• Build your theory of the attack as you gather evidence
• Submit your final assessment when ready

[bold]Commands:[/bold]
• Type your investigation request naturally
• Type 'theory' to submit your current attack theory
• Type 'status' to see your progress
• Type 'evidence' to view discovered clues
• Type 'help' for more options
• Type 'quit' to exit (you can resume later)
        """.format(
            max_investigations=self.max_investigations
        )

        self.console.print(
            Panel(instructions.strip(), title="Instructions", border_style="green")
        )

        input("\nPress Enter to begin the incident response...")

    def _display_initial_alert(self):
        """Display the initial incident alert"""

        alert = self.scenario.get("initial_alert", {})

        alert_content = f"""
[bold red]🚨 SECURITY ALERT 🚨[/bold red]

[bold]Alert Type:[/bold] {alert.get('alert_type', 'Unknown').title()}
[bold]Severity:[/bold] {alert.get('severity', 'Unknown').upper()}
[bold]Source:[/bold] {alert.get('source_system', 'Unknown')}
[bold]Time:[/bold] {alert.get('timestamp', 'Unknown')}

[bold]Description:[/bold]
{alert.get('description', 'A security incident has been detected and requires immediate investigation.')}

[bold]Raw Alert Data:[/bold]
[dim]{alert.get('raw_data', 'No additional raw data available.')}[/dim]
        """

        self.console.print(
            Panel(alert_content.strip(), title="Initial Alert", border_style="red")
        )

        # Log the initial alert
        self.investigation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "initial_alert",
                "content": alert,
                "investigator": "system",
            }
        )

    def _main_game_loop(self):
        """Main interactive game loop"""

        investigations_remaining = self.max_investigations

        while investigations_remaining > 0:
            # Display status
            self._display_status(investigations_remaining)

            # Get player input
            user_input = Prompt.ask(
                "\n[bold cyan]What would you like to investigate?[/bold cyan]"
            ).strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ["quit", "exit"]:
                if Confirm.ask("Are you sure you want to quit? You can resume later."):
                    self._save_session()
                    return
                else:
                    continue
            elif user_input.lower() == "theory":
                self._handle_theory_submission()
                continue
            elif user_input.lower() == "status":
                self._display_detailed_status()
                continue
            elif user_input.lower() == "evidence":
                self._display_evidence()
                continue
            elif user_input.lower().startswith("evidence detail "):
                evidence_id = user_input.lower().replace("evidence detail ", "").strip()
                self._display_detailed_evidence(evidence_id)
                continue
            elif user_input.lower() == "help":
                self._display_help()
                continue
            elif user_input.lower() == "hint":
                self._provide_hint()
                continue

            # Process investigation request
            self._process_investigation(user_input)
            investigations_remaining -= 1

            # Check if player wants to submit theory
            if investigations_remaining > 0:
                if Confirm.ask(
                    "\nWould you like to submit your theory now?", default=False
                ):
                    self._handle_theory_submission()
                    break

        if investigations_remaining == 0:
            self.console.print(
                "\n[yellow]⚠️  You've used all your investigation questions![/yellow]"
            )
            self.console.print("[yellow]Time to submit your final theory.[/yellow]")
            self._handle_theory_submission()

    def _process_investigation(self, investigation_request: str):
        """Process a player's investigation request"""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("🔍 Investigating...", total=None)

            # Determine if this investigation reveals a clue or red herring
            # reveal_red_herring = random.random() < self.red_herring_probability and len(
            #    self.red_herrings_encountered
            # ) < len(self.scenario.get("red_herrings", []))

            # Get response from AI facilitator
            response = self.facilitator.facilitate_action(
                action=investigation_request, details=""
            )

            progress.remove_task(task)

        # Record investigation
        investigation_record = {
            "timestamp": datetime.now().isoformat(),
            "type": "investigation",
            "request": investigation_request,
            "response": response,
            "investigator": "team",
        }
        self.investigation_history.append(investigation_record)

        # Display response
        self._display_investigation_result(investigation_request, response)

        # Update revealed clues - For now, we'll generate a clue_id based on the investigation
        # In a full implementation, this would be handled by the facilitator response
        if response.content:
            clue_id = f"clue_{len(self.revealed_clues) + 1}"
            self.revealed_clues.add(clue_id)

        # For now, we don't track red herrings from the basic response
        # This would need to be enhanced based on the facilitator's response structure

    def _display_investigation_result(self, request: str, response):
        """Display the results of an investigation"""

        result_content = f"""
[bold]Investigation Request:[/bold] {request}

[bold]Findings:[/bold]
{response.content if hasattr(response, 'content') else 'No specific findings available.'}
        """

        # For now, we'll work with the basic FacilitatorResponse structure
        # Additional details would need to be parsed from the content or
        # the FacilitatorResponse structure would need to be enhanced

        if hasattr(response, "additional_context") and response.additional_context:
            result_content += f"\n\n[bold]Additional Context:[/bold]\n[dim]{response.additional_context}[/dim]"

        # Use green border for now, red herring detection would need enhancement
        border_style = "green"

        self.console.print(
            Panel(
                result_content.strip(),
                title="Investigation Results",
                border_style=border_style,
            )
        )

        # Provide suggestions if available
        if hasattr(response, "suggestions") and response.suggestions:
            self.console.print("\n[dim]💡 Suggested follow-up investigations:[/dim]")
            for i, suggestion in enumerate(response.suggestions, 1):
                self.console.print(f"[dim]  {i}. {suggestion}[/dim]")

    def _handle_theory_submission(self):
        """Handle player's theory submission"""

        self.console.print("\n[bold blue]📝 Theory Submission[/bold blue]")
        self.console.print("Please provide your analysis of the attack:")

        # Collect theory components
        theory = {}

        theory["initial_access"] = Prompt.ask(
            "\n[bold]How did the attacker initially gain access?[/bold]"
        )
        theory["techniques_used"] = Prompt.ask(
            "[bold]What techniques/tools did the attacker use?[/bold]"
        )
        theory["timeline"] = Prompt.ask(
            "[bold]Describe the attack timeline (key events and order):[/bold]"
        )
        theory["objective"] = Prompt.ask(
            "[bold]What was the attacker's likely objective?[/bold]"
        )
        theory["attribution"] = Prompt.ask(
            "[bold]Any insights on the threat actor (sophistication, motivation)?[/bold]"
        )
        theory["impact"] = Prompt.ask(
            "[bold]What was the impact or potential impact?[/bold]"
        )

        # Optional: Additional evidence
        if Confirm.ask("\nDid you identify any additional indicators of compromise?"):
            theory["additional_iocs"] = Prompt.ask("Describe any additional IoCs:")

        # Record theory
        theory_record = {
            "timestamp": datetime.now().isoformat(),
            "theory": theory,
            "revealed_clues": list(self.revealed_clues),
            "red_herrings_encountered": self.red_herrings_encountered,
        }
        self.player_theories.append(theory_record)

        # Score the theory
        score_result = self.scorer.score_theory(theory_record)
        self.current_score = score_result["total_score"]

        # Display scoring results
        self._display_scoring_results(score_result)

    def _display_scoring_results(self, score_result: Dict):
        """Display scoring results and feedback"""

        self.console.print("\n[bold blue]📊 Scoring Results[/bold blue]")

        # Overall score
        max_score = score_result["max_possible_score"]
        percentage = (score_result["total_score"] / max_score) * 100

        score_panel = f"""
[bold]Total Score:[/bold] {score_result['total_score']} / {max_score} ({percentage:.1f}%)

[bold]Performance Level:[/bold] {score_result['performance_level']}
        """

        self.console.print(Panel(score_panel.strip(), border_style="blue"))

        # Category breakdown
        scoring_table = Table(title="Detailed Scoring")
        scoring_table.add_column("Category", style="cyan")
        scoring_table.add_column("Score", style="green")
        scoring_table.add_column("Max", style="blue")
        scoring_table.add_column("Feedback", style="yellow")

        for category in score_result["category_scores"]:
            scoring_table.add_row(
                category["category"],
                str(category["earned_points"]),
                str(category["max_points"]),
                category["feedback"],
            )

        self.console.print(scoring_table)

        # Bonus points and deductions
        if score_result.get("bonus_points", 0) > 0:
            self.console.print(
                f"\n[green]✅ Bonus Points: +{score_result['bonus_points']}[/green]"
            )

        if score_result.get("deductions", 0) > 0:
            self.console.print(
                f"[red]❌ Deductions: -{score_result['deductions']}[/red]"
            )

        # Red herring analysis
        if self.red_herrings_encountered:
            self.console.print(
                f"\n[yellow]⚠️  Red herrings encountered: {len(self.red_herrings_encountered)}[/yellow]"
            )
        else:
            self.console.print(
                "\n[green]✅ Successfully avoided all red herrings![/green]"
            )

        # Learning feedback
        if score_result.get("learning_feedback"):
            feedback_content = "\n".join(score_result["learning_feedback"])
            self.console.print(
                Panel(
                    feedback_content, title="💡 Learning Points", border_style="yellow"
                )
            )

    def _conclude_session(self):
        """Conclude the game session"""

        end_time = datetime.now()
        duration = end_time - self.start_time

        session_summary = f"""
[bold green]🎯 Session Complete![/bold green]

[bold]Final Score:[/bold] {self.current_score}
[bold]Duration:[/bold] {duration}
[bold]Investigation Questions Used:[/bold] {len([h for h in self.investigation_history if h['type'] == 'investigation'])} / {self.max_investigations}
[bold]Theories Submitted:[/bold] {len(self.player_theories)}

[bold]Session ID:[/bold] {self.session_id}
        """

        self.console.print(Panel(session_summary.strip(), border_style="green"))

        # Offer to save session
        if Confirm.ask("Would you like to save this session for review?"):
            self._save_session()
            self.console.print("[green]✅ Session saved successfully![/green]")

        # Offer to play again
        if Confirm.ask("Would you like to try another scenario?"):
            self.console.print(
                "\nUse '[cyan]python incidenter.py list-scenarios[/cyan]' to see available scenarios"
            )
            self.console.print(
                "Use '[cyan]python incidenter.py play <scenario_file>[/cyan]' to start a new session"
            )

    def _display_status(self, investigations_remaining: int):
        """Display current session status"""

        status_content = f"""
[bold]Investigation Questions Remaining:[/bold] {investigations_remaining}
[bold]Clues Discovered:[/bold] {len(self.revealed_clues)}
[bold]Current Score:[/bold] {self.current_score}
        """

        self.console.print(
            Panel(status_content.strip(), title="Status", border_style="blue")
        )

    def _display_detailed_status(self):
        """Display detailed session status"""

        # Investigation history table
        history_table = Table(title="Investigation History")
        history_table.add_column("Time", style="cyan")
        history_table.add_column("Type", style="green")
        history_table.add_column("Summary", style="white")

        for record in self.investigation_history[-10:]:  # Last 10 entries
            time_str = record["timestamp"][-8:-3]  # HH:MM format
            type_str = record["type"].replace("_", " ").title()

            if record["type"] == "investigation":
                summary = (
                    record["request"][:50] + "..."
                    if len(record["request"]) > 50
                    else record["request"]
                )
            else:
                summary = "Initial incident alert"

            history_table.add_row(time_str, type_str, summary)

        self.console.print(history_table)

        # Additional stats
        self.console.print(
            f"\n[bold]Session Duration:[/bold] {datetime.now() - self.start_time}"
        )
        if self.red_herrings_encountered:
            self.console.print(
                f"[yellow]Red Herrings Encountered:[/yellow] {len(self.red_herrings_encountered)}"
            )

    def _provide_hint(self):
        """Provide a hint to the player"""

        hint = self.facilitator.get_hint(
            scenario_context=self.scenario,
            revealed_clues=list(self.revealed_clues),
            investigation_history=self.investigation_history,
            difficulty_adjustment=self.difficulty_adjustment,
        )

        hint_content = f"""
[bold]💡 Hint:[/bold]
{hint}

[dim]Note: Hints don't count against your investigation limit.[/dim]
        """

        self.console.print(
            Panel(hint_content.strip(), title="Hint", border_style="yellow")
        )

    def _display_evidence(self):
        """Display all discovered evidence/clues"""

        # Count actual investigation records
        investigation_records = [
            r for r in self.investigation_history if r["type"] == "investigation"
        ]

        if not investigation_records and not self.revealed_clues:
            self.console.print(
                Panel(
                    "[yellow]No evidence discovered yet.[/yellow]\n\n"
                    "Continue investigating to uncover clues and build your case.",
                    title="📋 Evidence Log",
                    border_style="blue",
                )
            )
            return

        # Create evidence table
        evidence_table = Table(title="Discovered Evidence")
        evidence_table.add_column("ID", style="cyan", width=8)
        evidence_table.add_column("Time", style="green", width=8)
        evidence_table.add_column("Investigation", style="yellow", width=40)
        evidence_table.add_column("Key Findings", style="white", width=80)

        # Add investigation results as evidence entries
        evidence_count = 0
        for i, record in enumerate(self.investigation_history, 1):
            if record["type"] == "investigation":
                evidence_count += 1
                time_str = record["timestamp"][-8:-3]  # HH:MM format
                investigation = self._truncate_text(record["request"], 38)

                # Extract key findings from response content
                response = record.get("response", {})
                if hasattr(response, "content"):
                    findings = self._extract_key_findings(
                        response.content, max_length=78
                    )
                else:
                    findings = "Investigation completed"

                evidence_table.add_row(
                    f"E{evidence_count:03d}", time_str, investigation, findings
                )

        self.console.print(evidence_table)

        # Show summary stats
        self.console.print(f"\n[bold]Total Evidence Items:[/bold] {evidence_count}")
        self.console.print(
            f"[bold]Unique Clues Discovered:[/bold] {len(self.revealed_clues)}"
        )

        if self.red_herrings_encountered:
            self.console.print(
                f"[yellow]⚠️  Red Herrings Identified:[/yellow] {len(self.red_herrings_encountered)}"
            )

        # Show help for detailed evidence viewing
        self.console.print(
            "\n[dim]💡 Tip: Use 'evidence detail E001' to see full details for a specific evidence item[/dim]"
        )

    def _display_detailed_evidence(self, evidence_id: str):
        """
        Display detailed view of a specific evidence item.

        Args:
            evidence_id: Evidence ID (e.g., "E001", "e001", "001")
        """
        # Normalize evidence ID
        if evidence_id.upper().startswith("E"):
            evidence_num = evidence_id[1:]
        else:
            evidence_num = evidence_id

        try:
            evidence_index = int(evidence_num) - 1
        except ValueError:
            self.console.print(f"[red]❌ Invalid evidence ID: {evidence_id}[/red]")
            self.console.print(
                "[yellow]Use format like 'evidence detail E001' or 'evidence detail 1'[/yellow]"
            )
            return

        # Get investigation records
        investigation_records = [
            r for r in self.investigation_history if r["type"] == "investigation"
        ]

        if evidence_index < 0 or evidence_index >= len(investigation_records):
            self.console.print(
                f"[red]❌ Evidence {evidence_id.upper()} not found[/red]"
            )
            self.console.print(
                f"[yellow]Available evidence: E001 to E{len(investigation_records):03d}[/yellow]"
            )
            return

        record = investigation_records[evidence_index]

        # Format detailed display
        timestamp = record["timestamp"]
        request = record["request"]
        response = record.get("response", {})

        content = f"""
[bold]Evidence ID:[/bold] E{evidence_index + 1:03d}
[bold]Timestamp:[/bold] {timestamp}
[bold]Investigation Request:[/bold]
{request}

[bold]Full Response:[/bold]
"""

        if hasattr(response, "content") and response.content:
            content += response.content
        else:
            content += "No response content available"

        self.console.print(
            Panel(
                content.strip(),
                title=f"📋 Evidence E{evidence_index + 1:03d} - Detailed View",
                border_style="blue",
            )
        )

    def _display_help(self):
        """Display help information"""

        help_content = """
[bold]Available Commands:[/bold]
• [cyan]<investigation request>[/cyan] - Ask to investigate something specific
• [cyan]theory[/cyan] - Submit your attack theory for scoring
• [cyan]status[/cyan] - Show detailed session status
• [cyan]evidence[/cyan] - View all discovered evidence and clues
• [cyan]evidence detail E001[/cyan] - View full details for specific evidence
• [cyan]hint[/cyan] - Get a hint (doesn't count as investigation)
• [cyan]help[/cyan] - Show this help message
• [cyan]quit[/cyan] - Exit the session (can resume later)

[bold]Investigation Examples:[/bold]
• "Check firewall logs for suspicious connections"
• "Examine running processes on the affected server"
• "Review authentication logs for unusual activity"
• "Analyze network traffic for data exfiltration"
• "Look for persistence mechanisms in the registry"

[bold]Tips:[/bold]
• Be specific in your investigation requests
• Follow up on interesting findings
• Consider the attack timeline
• Watch out for red herrings!
        """

        self.console.print(
            Panel(help_content.strip(), title="Help", border_style="cyan")
        )

    def _save_session(self):
        """Save current session state"""
        from utils.session_manager import SessionState
        from datetime import datetime

        session_data = SessionState(
            session_id=self.session_id,
            scenario_id=self.scenario.get("scenario_metadata", {}).get("id", "unknown"),
            scenario_name=self.scenario.get("scenario_metadata", {}).get(
                "name", "Unknown Scenario"
            ),
            player_name=getattr(self, "player_name", "Anonymous"),
            start_time=self.start_time,
            current_phase=getattr(self, "current_phase", "investigation"),
            investigation_actions=self.investigation_history,
            evidence_discovered=list(self.revealed_clues),
            theories_submitted=self.player_theories,
            hints_used=getattr(self, "hints_used", 0),
            score_checkpoints=[],
            is_completed=False,
            completion_time=None,
            final_score=self.current_score,
            session_notes="",
            metadata={
                "scenario": self.scenario,
                "team_size": self.team_size,
                "difficulty_adjustment": self.difficulty_adjustment,
                "red_herrings_encountered": self.red_herrings_encountered,
                "end_time": datetime.now().isoformat(),
            },
        )

        self.session_manager.save_session(session_data)

    def _handle_early_exit(self):
        """Handle early exit from session"""

        self.console.print("\n[yellow]Session interrupted![/yellow]")

        if Confirm.ask("Would you like to save your progress?"):
            self._save_session()
            self.console.print("[green]✅ Progress saved![/green]")
            self.console.print(f"[blue]Session ID: {self.session_id}[/blue]")

        self.console.print("Thank you for playing Incidenter!")

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid

        return f"INC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"

    def _get_max_investigations(self) -> int:
        """Get maximum investigations based on scenario complexity"""

        complexity = self.scenario["scenario_metadata"]["difficulty"].lower()

        # Map scenario difficulty values to internal complexity levels
        difficulty_mapping = {
            "easy": "beginner",
            "medium": "intermediate",
            "hard": "advanced",
            "expert": "expert",
            "beginner": "beginner",
            "intermediate": "intermediate",
            "advanced": "advanced",
        }

        # Get mapped complexity or default to intermediate
        mapped_complexity = difficulty_mapping.get(complexity, "intermediate")

        base_investigations = {
            "beginner": 30,
            "intermediate": 25,
            "advanced": 20,
            "expert": 10,
        }

        # Adjust for team size
        team_multiplier = min(1.5, 1 + (self.team_size - 1) * 0.1)

        return int(base_investigations[mapped_complexity] * team_multiplier)

    def _setup_logging(self):
        """Setup session logging"""

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"{self.session_id}.log"

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        logging.info(f"Session started: {self.session_id}")
        logging.info(f"Scenario: {self.scenario['scenario_metadata']['name']}")
        logging.info(f"Team size: {self.team_size}")

    def _extract_key_findings(self, content: str, max_length: int = 80) -> str:
        """
        Extract key findings from AI response content for evidence table display.

        This method:
        1. Removes markdown formatting and code blocks
        2. Extracts the most important sentences
        3. Truncates to fit table width

        Args:
            content: The full AI response content
            max_length: Maximum length for the findings summary

        Returns:
            Cleaned and truncated key findings
        """
        import re

        if not content or not content.strip():
            return "No findings available"

        # Remove markdown code blocks (```...```)
        content = re.sub(r"```[\s\S]*?```", "[Code Block]", content)

        # Remove markdown formatting (* ** _ __ ~ ~~)
        content = re.sub(r"[*_~`]+([^*_~`]+)[*_~`]+", r"\1", content)

        # Remove markdown headers (# ## ###)
        content = re.sub(r"^#{1,6}\s+", "", content, flags=re.MULTILINE)

        # Remove markdown links [text](url)
        content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", content)

        # Clean up extra whitespace and newlines
        content = re.sub(r"\s+", " ", content).strip()

        # Split into sentences and extract the most meaningful ones
        sentences = [s.strip() for s in content.split(".") if s.strip()]

        if not sentences:
            return "Investigation completed"

        # Build summary from first few sentences
        summary = ""
        for sentence in sentences:
            # Skip very short or generic sentences
            if len(sentence) < 10 or sentence.lower().startswith(
                ("okay", "let me", "i will", "here is")
            ):
                continue

            # Add sentence if it fits
            test_summary = summary + sentence + ". "
            if len(test_summary) <= max_length:
                summary = test_summary
            else:
                # If adding this sentence would exceed limit, try to fit part of it
                remaining_space = max_length - len(summary) - 3  # -3 for "..."
                if remaining_space > 20:  # Only add if meaningful space left
                    summary += sentence[:remaining_space] + "..."
                break

        # If we couldn't build a summary, take the beginning of the content
        if not summary.strip():
            if len(content) <= max_length:
                return content
            else:
                return content[: max_length - 3] + "..."

        return summary.strip()

    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to fit within specified length, adding ellipsis if needed.

        Args:
            text: Text to truncate
            max_length: Maximum length (ellipsis counted in this limit)

        Returns:
            Truncated text with ellipsis if needed
        """
        if not text:
            return ""

        text = text.strip()
        if len(text) <= max_length:
            return text

        return text[: max_length - 3] + "..."
