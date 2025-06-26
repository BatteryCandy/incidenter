"""
Mock AI Facilitator for Incidenter
Provides simple mock responses for testing purposes
"""

import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class FacilitatorResponse:
    """Response from the AI facilitator"""

    content: str
    confidence: float
    suggestions: List[str]
    additional_context: Optional[str] = None
    requires_followup: bool = False


class MockAIFacilitator:
    """Mock AI facilitator for testing"""

    def __init__(self):
        self.scenario_data = {}
        self.game_context = {}
        self.conversation_history = []

    def load_scenario(self, scenario_data: Dict[str, Any]):
        """Load scenario data for context"""
        self.scenario_data = scenario_data

    def provide_hint(self, scenario: Dict[str, Any], game_session) -> Dict[str, Any]:
        """Provide a helpful hint"""
        hints = [
            "Look for unusual network traffic patterns in the logs.",
            "Check for any recent software updates or patches that may have failed.",
            "Examine user authentication logs for suspicious activity.",
            "Review system event logs around the time of the incident.",
            "Consider checking for any new processes or services running.",
            "Look for file system changes or modifications to critical files.",
            "Check if any security tools detected threats before the incident.",
            "Review backup logs to see if data integrity was compromised.",
        ]

        return {
            "success": True,
            "message": random.choice(hints),
            "confidence": random.uniform(0.7, 0.9),
        }

    def provide_feedback(
        self, theory: str, scenario: Dict[str, Any], evidence: List[Dict]
    ) -> Dict[str, Any]:
        """Provide feedback on a theory"""
        feedback_options = [
            "Your theory shows good understanding of the attack vector. Consider the timeline of events.",
            "You're on the right track. Think about what the attacker's ultimate goal might be.",
            "That's an interesting perspective. What evidence supports this theory?",
            "Good analysis. Consider how this relates to the broader attack chain.",
            "Your theory addresses part of the incident. What other factors might be involved?",
        ]

        accuracy_score = random.uniform(0.6, 0.95)

        return {
            "success": True,
            "feedback": random.choice(feedback_options),
            "accuracy_score": accuracy_score,
            "suggestions": [
                "Review the evidence timeline more carefully",
                "Consider the attacker's motivations",
                "Look for additional indicators of compromise",
            ],
        }

    def evaluate_investigation_action(
        self, action: str, context: Dict[str, Any]
    ) -> FacilitatorResponse:
        """Evaluate an investigation action"""
        responses = [
            "That's a good investigative step. This should provide valuable information.",
            "Excellent choice. This action will help clarify the situation.",
            "This investigation approach makes sense given the current evidence.",
            "Good thinking. This should reveal important details about the incident.",
        ]

        return FacilitatorResponse(
            content=random.choice(responses),
            confidence=random.uniform(0.7, 0.9),
            suggestions=[
                "Continue investigating related systems",
                "Document your findings",
            ],
            requires_followup=False,
        )

    def generate_evidence_discovery(
        self, action: str, scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate evidence based on investigation action"""
        evidence_templates = [
            {
                "type": "log_entry",
                "description": f"Found relevant log entries related to {action}",
                "details": "Multiple authentication failures detected",
                "timestamp": "2024-01-15 14:23:17",
                "source": "Security logs",
            },
            {
                "type": "network_traffic",
                "description": f"Network traffic analysis from {action}",
                "details": "Unusual outbound connections to external IPs",
                "timestamp": "2024-01-15 14:25:33",
                "source": "Network monitoring",
            },
            {
                "type": "file_analysis",
                "description": f"File system changes discovered during {action}",
                "details": "Suspicious executables found in temp directory",
                "timestamp": "2024-01-15 14:18:42",
                "source": "File system audit",
            },
        ]

        return random.choice(evidence_templates)

    def facilitate_action(self, action: str, details: str = "") -> FacilitatorResponse:
        """Facilitate an investigation action (compatible with AIFacilitator interface)"""

        # Generate realistic investigation responses based on the action
        investigation_responses = {
            "email": [
                "Found suspicious phishing email from external sender with malicious attachment.",
                "Discovered spear-phishing campaign targeting IT administrators with credential harvesting links.",
                "Located ransomware delivery email with ZIP attachment containing malicious payload.",
            ],
            "log": [
                "Network logs show unusual outbound connections to suspicious IP addresses.",
                "Security logs reveal multiple failed authentication attempts followed by successful login.",
                "System logs indicate process execution anomalies and suspicious file creation.",
            ],
            "process": [
                "Identified suspicious process 'svchost.exe' running from unusual location.",
                "Found evidence of lateral movement through remote process execution.",
                "Discovered cryptocurrency mining process consuming excessive system resources.",
            ],
            "network": [
                "Network traffic analysis reveals data exfiltration to command and control servers.",
                "Firewall logs show blocked connections to known malicious domains.",
                "DNS queries indicate communication with suspicious domains associated with ransomware.",
            ],
            "file": [
                "File system analysis reveals encrypted files with ransom note extensions.",
                "Found suspicious executable files dropped in temporary directories.",
                "Discovered shadow copy deletion indicating ransomware preparation activities.",
            ],
            "ransom": [
                "Located ransom note file 'HOW_TO_RECOVER_FILES.txt' in multiple directories.",
                "Found ransom payment instructions demanding cryptocurrency payment.",
                "Discovered ransom note indicating DarkSide ransomware group involvement.",
            ],
        }

        # Determine response category based on action keywords
        action_lower = action.lower()
        response_category = "log"  # default

        for category in investigation_responses.keys():
            if category in action_lower:
                response_category = category
                break

        # Select appropriate response
        responses = investigation_responses.get(
            response_category, investigation_responses["log"]
        )
        content = random.choice(responses)

        # Generate relevant suggestions
        suggestions = [
            "Investigate related system components",
            "Check for additional indicators of compromise",
            "Document findings for timeline reconstruction",
            "Look for evidence of persistence mechanisms",
        ]

        return FacilitatorResponse(
            content=content,
            confidence=random.uniform(0.75, 0.95),
            suggestions=random.sample(suggestions, 2),
            additional_context=f"Investigation: {action[:50]}{'...' if len(action) > 50 else ''}",
            requires_followup=random.choice([True, False]),
        )

    def get_hint(self, **kwargs) -> str:
        """Provide a hint (compatible with AIFacilitator interface)"""
        hints = [
            "Focus on the initial access vector - how did the attackers first get in?",
            "Look for signs of reconnaissance and lateral movement through the network.",
            "Check for evidence of data collection before the ransomware deployment.",
            "Consider the timeline - what happened between initial access and encryption?",
            "Examine network traffic for command and control communication patterns.",
        ]
        return random.choice(hints)
