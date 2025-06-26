import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
"""
Flask Web Server for Incidenter
Provides web-based interface for playing cybersecurity incident scenarios
"""

import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
from datetime import datetime
from cli.scenario_manager import ScenarioManager
from facilitator.ai_facilitator import get_facilitator
from scoring.scorer import IncidenterScorer
from utils.session_manager import SessionManager

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "dev-secret-key-change-in-production"
)

# Initialize managers
scenario_manager = ScenarioManager()
session_manager = SessionManager()

# Perform initial cleanup of old sessions on startup
session_manager.cleanup_sessions()

# Initialize AI facilitator with improved credential validation
try:
    facilitator = get_facilitator()
    print(f"✅ AI Facilitator initialized: {type(facilitator).__name__}")
except Exception as e:
    print(f"Warning: AI Facilitator initialization failed: {e}")
    from facilitator.ai_facilitator import MockFacilitator

    facilitator = MockFacilitator()
    print("🔄 Using MockFacilitator as fallback")

try:
    scorer = IncidenterScorer()
except Exception as e:
    print(f"Warning: Scorer initialization failed: {e}")
    scorer = None


def check_for_evidence_discovery(action, details, scenario, game_session):
    """
    Check if an investigation action should trigger evidence discovery

    Args:
        action: The investigation action type
        details: Action details/description
        scenario: The scenario data
        game_session: Current game session

    Returns:
        Evidence dict if found, None otherwise
    """
    if not scenario.get("evidence", {}).get("items"):
        return None

    # Get already discovered evidence IDs to avoid duplicates
    discovered_ids = {
        ev.get("id") for ev in game_session.evidence_discovered if ev.get("id")
    }

    # Define action to evidence type mapping
    action_mappings = {
        "examine_logs": [
            "web_log",
            "file_system_log",
            "database_log",
            "security_alert",
            "security_log",
            "log",  # Added generic log type
            "process",
            "registry",
            "memory",
            "email",  # Phishing emails often found in logs
        ],
        "analyze_network": [
            "network_log",
            "network",
            "forensic",  # Network forensics
        ],
        "check_system": [
            "file_system_log",
            "security_alert",
            "process",
            "registry",
            "malware",  # System checks can find malware
            "forensic",  # System forensics
        ],
        "analyze_file": [
            "file_system_log",
            "process",
            "malware",  # File analysis finds malware
            "forensic",  # File forensics
        ],
        "search_database": [
            "database_log",
            "log",  # Database logs
            "report",  # Database reports
        ],
        "contact_vendor": [
            "vendor_advisory",
            "report",  # Vendor reports
            "intelligence",  # Vendor intelligence
        ],
        "interview_user": [
            "email",
            "witness",
            "report",  # User reports
        ],
        "run_command": [
            "file_system_log",
            "security_alert",
            "process",
            "registry",
            "forensic",  # Command line forensics
        ],
        "other": [
            "web_log",
            "network_log",
            "security_alert",
            "email",
            "process",
            "registry",
            "memory",
            "network",
            "lateral_movement",
            "log",  # Generic logs
            "report",  # Generic reports
            "malware",  # Malware analysis
            "intelligence",  # Threat intelligence
            "forensic",  # Digital forensics
        ],  # Fallback for other actions
    }

    # Get potential evidence types for this action
    evidence_types = action_mappings.get(action, ["security_alert"])

    # Check each evidence item in the scenario
    for evidence_item in scenario["evidence"]["items"]:
        evidence_id = evidence_item.get("id")
        evidence_type = evidence_item.get("type")

        # Skip if already discovered
        if evidence_id in discovered_ids:
            continue

        # Check if evidence type matches action
        if evidence_type in evidence_types:
            # Additional keyword matching for more realistic discovery
            keywords_match = check_evidence_keywords(details, evidence_item)

            # Discovery probability based on evidence importance and keyword matching
            discovery_chance = calculate_discovery_chance(evidence_item, keywords_match)

            # For demo purposes, we'll use a simple probability
            # In a real implementation, you might want more sophisticated logic
            if random.random() < discovery_chance:
                # Ensure the evidence has all required fields for UI display
                formatted_evidence = {
                    "id": evidence_item.get(
                        "id", f"ev_{len(game_session.evidence_discovered) + 1}"
                    ),
                    "type": evidence_item.get("type", "unknown"),
                    "source": evidence_item.get("source", "unknown"),
                    "importance": evidence_item.get("importance", "medium"),
                    "description": evidence_item.get(
                        "description", "No description available"
                    ),
                    "content": evidence_item.get("content", "No content available"),
                    "discovered_at": datetime.now().isoformat(),
                }
                return formatted_evidence

    return None


def check_evidence_keywords(details, evidence_item):
    """Check if investigation details contain relevant keywords for evidence discovery"""
    details_lower = details.lower()
    evidence_content = evidence_item.get("content", "").lower()
    evidence_description = evidence_item.get("description", "").lower()
    evidence_type = evidence_item.get("type", "").lower()

    # Extract keywords from evidence based on type and content
    keywords = []

    # Email evidence keywords
    if "email" in evidence_type:
        keywords.extend(
            ["email", "phishing", "attachment", "mail", "message", "sender"]
        )

    # Process/execution evidence keywords
    if "process" in evidence_type:
        keywords.extend(
            ["powershell", "cmd", "process", "execution", "command", "script"]
        )

    # Network evidence keywords
    if "network" in evidence_type:
        keywords.extend(["network", "traffic", "connection", "ip", "domain", "dns"])

    # Registry evidence keywords
    if "registry" in evidence_type:
        keywords.extend(["registry", "hklm", "hkcu", "run", "startup", "persistence"])

    # Memory evidence keywords
    if "memory" in evidence_type:
        keywords.extend(["memory", "lsass", "dump", "credential", "hash"])

    # Lateral movement evidence keywords
    if "lateral_movement" in evidence_type:
        keywords.extend(["smb", "admin$", "c$", "wmi", "lateral", "movement"])

    # Log evidence keywords
    if "log" in evidence_type:
        keywords.extend(["log", "event", "audit", "system", "security", "application"])

    # Report evidence keywords
    if "report" in evidence_type:
        keywords.extend(["report", "analysis", "summary", "findings", "investigation"])

    # Malware evidence keywords
    if "malware" in evidence_type:
        keywords.extend(["malware", "virus", "trojan", "backdoor", "payload", "sample"])

    # Intelligence evidence keywords
    if "intelligence" in evidence_type:
        keywords.extend(
            ["intelligence", "ioc", "indicator", "threat", "attribution", "campaign"]
        )

    # Forensic evidence keywords
    if "forensic" in evidence_type:
        keywords.extend(
            [
                "forensic",
                "analysis",
                "artifact",
                "evidence",
                "timeline",
                "investigation",
            ]
        )

    # Generic keywords from content analysis
    if "sql" in evidence_description or "sql" in evidence_content:
        keywords.extend(["sql", "injection", "database"])
    if "web shell" in evidence_description or "aspx" in evidence_content:
        keywords.extend(["web shell", "file", "aspx", "php"])
    if "vendor" in evidence_item.get("source", "").lower():
        keywords.extend(["vendor", "advisory", "bulletin", "patch"])
    if "hvac" in evidence_description.lower() or "hvac" in evidence_content:
        keywords.extend(["hvac", "cooling", "heating", "vendor", "third-party"])

    # Check if any keywords match
    return any(keyword in details_lower for keyword in keywords)


def calculate_discovery_chance(evidence_item, keywords_match):
    """Calculate probability of discovering evidence based on importance and keyword matching"""
    base_chance = {
        "critical": 0.8,
        "high": 0.6,
        "medium": 0.4,
        "low": 0.2,
    }

    importance = evidence_item.get("importance", "medium")
    chance = base_chance.get(importance, 0.4)

    # Boost chance if keywords match
    if keywords_match:
        chance = min(0.95, chance + 0.3)

    return chance


@app.route("/")
def index():
    """Home page showing available scenarios"""
    scenarios = scenario_manager.list_scenarios()
    return render_template("index.html", scenarios=scenarios)


@app.route("/scenario/<scenario_id>")
def scenario_detail(scenario_id):
    """Show scenario details and start game option"""
    scenario = scenario_manager.get_scenario(scenario_id)
    if not scenario:
        return "Scenario not found", 404

    return render_template("scenario_detail.html", scenario=scenario)


@app.route("/start/<scenario_id>", methods=["POST"])
def start_game(scenario_id):
    """Start a new game session"""
    player_name = request.form.get("player_name", "Player")

    # Load scenario
    scenario = scenario_manager.get_scenario(scenario_id)
    if not scenario:
        return "Scenario not found", 404

    # Create game session
    game_session = session_manager.create_session(
        scenario_id=scenario_id,
        scenario_name=scenario["scenario_metadata"]["name"],
        player_name=player_name,
    )

    # Store session ID in Flask session
    session["game_session_id"] = game_session.session_id

    return redirect(url_for("play_game"))


@app.route("/play")
def play_game():
    """Main game interface"""
    if "game_session_id" not in session:
        return redirect(url_for("index"))

    game_session = session_manager.load_session(session["game_session_id"])
    if not game_session:
        return redirect(url_for("index"))

    scenario = scenario_manager.get_scenario(game_session.scenario_id)

    return render_template("game.html", session=game_session, scenario=scenario)


@app.route("/api/investigate", methods=["POST"])
def investigate():
    """Handle investigation actions via API"""
    if "game_session_id" not in session:
        return jsonify({"error": "No active session"}), 401

    data = request.json
    action = data.get("action", "")
    details = data.get("details", "")

    if not action:
        return jsonify({"error": "Action required"}), 400

    # Load session and scenario
    game_session = session_manager.load_session(session["game_session_id"])
    scenario = scenario_manager.get_scenario(game_session.scenario_id)

    # Record the action
    session_manager.current_session = game_session
    session_manager.add_investigation_action(action, details)

    # Get AI facilitator response
    try:
        if not facilitator:
            return jsonify(
                {
                    "success": True,
                    "response": "AI Facilitator not available. Action recorded successfully.",
                    "evidence_found": None,
                    "hints": [],
                }
            )

        # Load scenario data for facilitator
        facilitator.load_scenario(scenario)

        # Get facilitator response
        facilitator_response = facilitator.facilitate_action(action, details)

        # Extract response content
        response_content = facilitator_response.content
        hints = facilitator_response.suggestions or []

        # Check for evidence discovery based on action type and details
        evidence_found = check_for_evidence_discovery(
            action, details, scenario, game_session
        )

        # Add any discovered evidence to the session
        if evidence_found:
            session_manager.add_evidence_discovered(evidence_found)

        return jsonify(
            {
                "success": True,
                "response": response_content,
                "evidence_found": evidence_found,
                "hints": hints,
            }
        )

    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": f"Error processing investigation: {str(e)}"}
            ),
            500,
        )


@app.route("/api/submit_theory", methods=["POST"])
def submit_theory():
    """Handle theory submission"""
    if "game_session_id" not in session:
        return jsonify({"error": "No active session"}), 401

    data = request.json
    theory = data.get("theory", "")

    if not theory:
        return jsonify({"error": "Theory required"}), 400

    # Load session and scenario
    game_session = session_manager.load_session(session["game_session_id"])
    scenario = scenario_manager.get_scenario(game_session.scenario_id)

    # Record the theory
    session_manager.current_session = game_session
    session_manager.add_theory_submitted(theory)

    # Get AI facilitator feedback
    try:
        if not facilitator:
            fallback_feedback = [
                "Your theory shows good understanding of the attack vector. Consider the timeline of events.",
                "You're on the right track. Think about what the attacker's ultimate goal might be.",
                "That's an interesting perspective. What evidence supports this theory?",
                "Good analysis. Consider how this relates to the broader attack chain.",
                "Your theory addresses part of the incident. What other factors might be involved?",
            ]
            return jsonify(
                {
                    "success": True,
                    "feedback": random.choice(fallback_feedback),
                    "accuracy_score": random.uniform(0.6, 0.9),
                }
            )

        # Load scenario data for facilitator
        facilitator.load_scenario(scenario)

        # Get facilitator evaluation
        facilitator_response = facilitator.evaluate_theory(theory)

        return jsonify(
            {
                "success": True,
                "feedback": facilitator_response.content,
                "accuracy_score": facilitator_response.confidence,
            }
        )

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Error evaluating theory: {str(e)}"}),
            500,
        )


@app.route("/api/get_hint")
def get_hint():
    """Get a hint for the current scenario"""
    if "game_session_id" not in session:
        return jsonify({"error": "No active session"}), 401

    game_session = session_manager.load_session(session["game_session_id"])
    scenario = scenario_manager.get_scenario(game_session.scenario_id)

    try:
        if not facilitator:
            fallback_hints = [
                "Look for unusual network traffic patterns in the logs.",
                "Check for any recent software updates or patches that may have failed.",
                "Examine user authentication logs for suspicious activity.",
                "Review system event logs around the time of the incident.",
                "Consider checking for any new processes or services running.",
                "Look for file system changes or modifications to critical files.",
                "Check if any security tools detected threats before the incident.",
                "Review backup logs to see if data integrity was compromised.",
            ]
            # Increment hint counter even for fallback
            session_manager.current_session = game_session
            session_manager.increment_hints_used()

            # Reload session to get updated hints count
            updated_session = session_manager.load_session(session["game_session_id"])

            # Log for debugging
            print(
                f"DEBUG: Fallback hints used after increment: {updated_session.hints_used}"
            )

            return jsonify(
                {
                    "success": True,
                    "hint": random.choice(fallback_hints),
                    "hints_used": updated_session.hints_used,
                }
            )

        # Load scenario data for facilitator
        facilitator.load_scenario(scenario)

        # Get facilitator hint
        facilitator_response = facilitator.provide_hint()

        # Increment hint counter
        session_manager.current_session = game_session
        session_manager.increment_hints_used()

        # Reload session to get updated hints count
        updated_session = session_manager.load_session(session["game_session_id"])

        # Log for debugging
        print(f"DEBUG: Hints used after increment: {updated_session.hints_used}")

        return jsonify(
            {
                "success": True,
                "hint": facilitator_response.content,
                "hints_used": updated_session.hints_used,
            }
        )

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Error getting hint: {str(e)}"}),
            500,
        )


@app.route("/api/complete_scenario", methods=["POST"])
def complete_scenario():
    """Complete the current scenario and get final score"""
    if "game_session_id" not in session:
        return jsonify({"error": "No active session"}), 401

    game_session = session_manager.load_session(session["game_session_id"])
    scenario = scenario_manager.get_scenario(game_session.scenario_id)

    try:
        # Calculate final score
        if not scorer:
            final_score = 85  # Default score when scorer not available
        else:
            # Convert game_session to dict format expected by scorer
            session_data = {
                "investigation_actions": game_session.investigation_actions,
                "evidence_discovered": game_session.evidence_discovered,
                "theories_submitted": game_session.theories_submitted,
                "hints_used": game_session.hints_used,
                "start_time": (
                    game_session.start_time.isoformat()
                    if game_session.start_time
                    else None
                ),
                "end_time": datetime.now().isoformat(),
            }

            game_score = scorer.score_game_session(scenario, session_data)
            final_score = game_score.percentage

        # Complete the session
        session_manager.current_session = game_session
        session_manager.complete_session(final_score)

        return jsonify(
            {
                "success": True,
                "final_score": final_score,
                "summary": session_manager.get_session_summary(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": f"Error completing scenario: {str(e)}"}
            ),
            500,
        )


@app.route("/sessions")
def view_sessions():
    """View previous game sessions"""
    sessions = session_manager.list_sessions()
    return render_template("sessions.html", sessions=sessions)


@app.route("/session/<session_id>")
def view_session_detail(session_id):
    """View details of a specific session"""
    game_session = session_manager.load_session(session_id)
    if not game_session:
        return "Session not found", 404

    scenario = scenario_manager.get_scenario(game_session.scenario_id)
    summary = session_manager.get_session_summary(session_id)

    return render_template(
        "session_detail.html", session=game_session, scenario=scenario, summary=summary
    )


@app.route("/api/session_status")
def session_status():
    """Get current session status"""
    if "game_session_id" not in session:
        return jsonify({"active": False})

    game_session = session_manager.load_session(session["game_session_id"])
    if not game_session:
        return jsonify({"active": False})

    return jsonify(
        {
            "active": True,
            "session_id": game_session.session_id,
            "scenario_name": game_session.scenario_name,
            "player_name": game_session.player_name,
            "phase": game_session.current_phase,
            "actions_count": len(game_session.investigation_actions),
            "evidence_count": len(game_session.evidence_discovered),
            "theories_count": len(game_session.theories_submitted),
            "hints_used": game_session.hints_used,
            "start_time": (
                game_session.start_time.isoformat() if game_session.start_time else None
            ),
        }
    )


@app.route("/logout")
def logout():
    """End current session"""
    session.pop("game_session_id", None)
    return redirect(url_for("index"))


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="Page not found"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error="Internal server error"), 500


if __name__ == "__main__":
    # Development server
    app.run(debug=True, host="0.0.0.0", port=5003)
