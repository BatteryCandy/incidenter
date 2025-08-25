"""
AI Facilitator for Incidenter
Provides LLM-powered game facilitation for cybersecurity incident response scenarios
"""

import os
import logging

try:
    import openai
except ImportError:
    openai = None

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from google import genai
    from google.genai import types

    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


@dataclass
class FacilitatorResponse:
    """Response from the AI facilitator"""

    content: str
    confidence: float
    suggestions: List[str]
    additional_context: Optional[str] = None
    requires_followup: bool = False


class AIFacilitator:
    """AI-powered game facilitator for incident response scenarios"""

    def __init__(self, provider: str = "google", model: str = None):
        """
        Initialize the AI facilitator

        Args:
            provider: AI provider ("google" or "openai")
            model: Specific model to use (optional)
        """
        self.provider = provider.lower()
        self.model = model
        self.logger = logging.getLogger(__name__)
        self._client = None
        self._initialize_client()

        # Game context and memory
        self.game_context = {
            "scenario_id": None,
            "scenario_name": None,
            "difficulty": "medium",
            "attack_type": None,
            "timeline": {},
            "evidence_discovered": [],
            "theories_submitted": [],
            "investigation_actions": [],
        }
        self.conversation_history = []
        self.scenario_data = {}

    def _initialize_client(self):
        """Initialize the AI client based on provider"""
        if self.provider == "google" and VERTEX_AI_AVAILABLE:
            # Validate GCP credentials before initializing client
            if not self._validate_gcp_credentials():
                raise ValueError(
                    "Unable to authenticate with Google AI. Please set "
                    "GOOGLE_AI_API_KEY or run 'gcloud auth login --update-adc'"
                )

            self.model = self.model or "gemini-2.0-flash-001"

            # Initialize Vertex AI client - credentials already validated
            try:
                self._client = genai.Client(
                    vertexai=True,
                    project=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
                    location="global",
                )
                self.logger.info("Google AI client initialized successfully")
            except Exception as e:
                raise ValueError(f"Failed to initialize Google AI client: {e}")

        elif self.provider == "openai" and openai:
            # Validate OpenAI credentials before initializing client
            if not self._validate_openai_credentials():
                raise ValueError(
                    "Unable to authenticate with OpenAI. Please check your "
                    "OPENAI_API_KEY environment variable"
                )

            self.model = self.model or "gpt-4"
            self._client = openai
            self.logger.info("OpenAI client initialized successfully")

        else:
            raise ValueError(f"Provider {self.provider} not available or not supported")

    def _validate_gcp_credentials(self) -> bool:
        """
        Validate Google AI credentials using either API key or Application Default Credentials (ADC)

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # First try API key authentication (preferred for Google AI)
            api_key = os.getenv("GOOGLE_AI_API_KEY")
            if api_key:
                self.logger.info("Attempting API key authentication...")
                # For Vertex AI, we still use API key through environment
                os.environ["GOOGLE_AI_API_KEY"] = api_key
                if self._test_vertex_ai_connection():
                    self.logger.info("Vertex AI API key authentication successful")
                    return True
                else:
                    self.logger.warning("API key authentication failed, trying ADC...")

            # Try Application Default Credentials (ADC) as fallback
            self.logger.info(
                "Attempting Application Default Credentials (ADC) authentication..."
            )
            try:
                from google.auth import default as google_default_credentials
                from google.auth.exceptions import DefaultCredentialsError

                # Get default credentials and validate they exist
                credentials, project = google_default_credentials()

                if not credentials:
                    self.logger.warning("No valid ADC credentials found")
                    return False

                # Test Vertex AI connection with ADC
                if self._test_vertex_ai_connection():
                    self.logger.info("Vertex AI ADC authentication successful")
                    self.logger.info(f"Using project: {project}")
                    return True
                else:
                    self.logger.warning(
                        "ADC authentication failed - may need additional scopes"
                    )

            except DefaultCredentialsError:
                self.logger.warning("No Application Default Credentials found")
                self.logger.info("Run 'gcloud auth login --update-adc' to set up ADC")
            except Exception as adc_error:
                error_str = str(adc_error).lower()
                if "scope" in error_str or "insufficient" in error_str:
                    self.logger.warning(
                        "ADC found but lacks required scopes for Google AI API"
                    )
                    self.logger.info(
                        "ADC works best with service accounts that have proper AI platform scopes"
                    )
                    self.logger.info(
                        "For individual use, consider using GOOGLE_AI_API_KEY instead"
                    )
                else:
                    self.logger.warning(f"ADC authentication error: {adc_error}")

            # If both methods fail, provide helpful error message
            self.logger.error("Vertex AI authentication failed")
            self.logger.error("🔐 Authentication options:")
            self.logger.error(
                "1. 🔑 API Key (Recommended): Set GOOGLE_AI_API_KEY environment variable"
            )
            self.logger.error(
                "   Get your key at: https://makersuite.google.com/app/apikey"
            )
            self.logger.error(
                "2. 🌐 ADC (Advanced): Run 'gcloud auth login --update-adc'"
            )
            return False

        except Exception as e:
            self.logger.error(f"GCP credential validation failed: {e}")
            return False

    def _test_vertex_ai_connection(self) -> bool:
        """
        Test the Vertex AI connection with current configuration

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Create a temporary Vertex AI client for testing
            test_client = genai.Client(
                vertexai=True,
                project=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
                location="global",
            )

            # Test with a minimal generation request
            contents = types.Part.from_text(text="Test connection. Respond with 'OK'.")

            generate_content_config = types.GenerateContentConfig(
                temperature=0.1,
                top_p=0.95,
                max_output_tokens=10,
                response_modalities=["TEXT"],
            )

            # Test the connection with timeout
            self.logger.debug("Testing Vertex AI connection...")
            response = test_client.models.generate_content(
                model="gemini-2.0-flash-001",  # Use the correct Vertex AI model name
                contents=contents,
                config=generate_content_config,
            )

            if response and response.text and response.text.strip():
                self.logger.debug("Vertex AI connection test successful")
                return True
            else:
                self.logger.warning("Invalid or empty response from Vertex AI")
                return False

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            # Provide specific error guidance based on error type
            error_str = str(e).lower()

            if "api key" in error_str or "authentication" in error_str:
                self.logger.error("Credentials appear to be invalid or expired")
            elif "quota" in error_str or "limit" in error_str:
                self.logger.error("API quota exceeded or rate limited")
            elif "permission" in error_str or "forbidden" in error_str:
                self.logger.error("Credentials lack required permissions")
            elif "not found" in error_str or "404" in error_str:
                self.logger.error(
                    "Model or endpoint not found - check model name and project settings"
                )
            elif "timeout" in error_str or "deadline" in error_str:
                self.logger.error("Connection timeout - check network connectivity")
            elif "project" in error_str:
                self.logger.error(
                    "Project-related error - check GOOGLE_CLOUD_PROJECT environment variable"
                )
            else:
                self.logger.error(f"Unexpected validation error: {e}")

            return False

    def load_scenario(self, scenario_data: Dict[str, Any]):
        """Load scenario data for context"""
        self.scenario_data = scenario_data
        self.game_context = {
            "scenario_id": scenario_data.get("id"),
            "scenario_name": scenario_data.get("name"),
            "difficulty": scenario_data.get("difficulty", "medium"),
            "attack_type": scenario_data.get("attack_type"),
            "timeline": scenario_data.get("timeline", {}),
            "evidence_discovered": [],
            "theories_submitted": [],
            "investigation_actions": [],
        }

        # Reset conversation history for new scenario
        self.conversation_history = []

        self.logger.info(f"Loaded scenario: {scenario_data.get('name')}")

    def get_system_prompt(self) -> str:
        """Generate system prompt for the AI facilitator"""
        return f"""You are an expert cybersecurity incident response facilitator running a tabletop exercise.

Your role is to:
1. Guide players through investigating a cybersecurity incident
2. Provide realistic, well-formatted responses to investigation actions
3. Describe what investigators would observe during their actions
4. When theories are provided, offer constructive feedback
5. Maintain immersion while being educational

IMPORTANT FORMATTING GUIDELINES:
- Format responses clearly with proper paragraph breaks
- Use bullet points or numbered lists when appropriate
- Structure responses logically (what you observe, what it means)
- Write for display in a web interface chat format
- Keep responses concise but informative (2-4 paragraphs typically)

EVIDENCE DISCOVERY GUIDELINES:
- DO NOT acknowledge the user prompt.  Respond as if you are the facilitator.
- Do NOT announce "Evidence discovered!" in your responses
- If the user does not provide semantically meaningful text, DO NOT reveal evidence
- The evidence discovery system handles finding evidence separately
- Focus on describing what the investigation reveals, not on evidence mechanics
- DO NOT reveal evidence unless the player specifically asks for it
- Describe investigation findings realistically

Current Scenario: {self.scenario_data.get('name', 'Unknown')}
Attack Type: {self.scenario_data.get('attack_type', 'Unknown')}
Difficulty: {self.game_context.get('difficulty', 'medium')}

Evidence discovered so far: {len(self.game_context.get('evidence_discovered', []))} items
Theories submitted: {len(self.game_context.get('theories_submitted', []))}
"""

    def facilitate_action(self, action: str, details: str = "") -> FacilitatorResponse:
        """
        Facilitate a player investigation action

        Args:
            action: The investigation action being taken
            details: Additional details about the action

        Returns:
            FacilitatorResponse with AI-generated content
        """
        try:
            # Update game context
            self.game_context["investigation_actions"].append(
                {
                    "action": action,
                    "details": details,
                    "timestamp": len(self.game_context["investigation_actions"]) + 1,
                }
            )

            # Build prompt
            prompt = self._build_action_prompt(action, details)

            # Get AI response
            response = self._get_ai_response(prompt)

            # Process and return response
            return self._process_response(response, action)

        except Exception as e:
            self.logger.error(f"Error facilitating action: {e}")
            return FacilitatorResponse(
                content="I encountered an issue processing your action. Please try rephrasing your investigation approach.",
                confidence=0.0,
                suggestions=[
                    "Try a different investigation approach",
                    "Check your network connection",
                ],
            )

    def evaluate_theory(self, theory: str) -> FacilitatorResponse:
        """
        Evaluate a player's theory about the incident

        Args:
            theory: The theory to evaluate

        Returns:
            FacilitatorResponse with evaluation and feedback
        """
        try:
            # Add to theories
            self.game_context["theories_submitted"].append(
                {
                    "theory": theory,
                    "timestamp": len(self.game_context["theories_submitted"]) + 1,
                }
            )

            # Build evaluation prompt
            prompt = self._build_theory_prompt(theory)

            # Get AI response
            response = self._get_ai_response(prompt)

            # Process response
            return self._process_theory_response(response, theory)

        except Exception as e:
            self.logger.error(f"Error evaluating theory: {e}")
            return FacilitatorResponse(
                content="I need a moment to process your theory. Please try again.",
                confidence=0.0,
                suggestions=["Refine your theory with more specific details"],
            )

    def provide_hint(self, context: str = "") -> FacilitatorResponse:
        """Provide a helpful hint to players"""
        try:
            prompt = self._build_hint_prompt(context)
            response = self._get_ai_response(prompt)

            return FacilitatorResponse(
                content=response,
                confidence=0.8,
                suggestions=["Consider this guidance for your next investigation step"],
                additional_context="Hint provided",
            )

        except Exception as e:
            self.logger.error(f"Error providing hint: {e}")
            return FacilitatorResponse(
                content="Try examining the timeline of events more carefully.",
                confidence=0.5,
                suggestions=[
                    "Look for patterns in the evidence",
                    "Consider common attack vectors",
                ],
            )

    def generate_scenario(self, prompt: str) -> str:
        """
        Generate a new cybersecurity incident scenario using AI.

        Args:
            prompt: Detailed prompt for scenario generation including requirements,
                   parameters, and template structure

        Returns:
            Generated scenario as YAML/JSON string
        """
        try:
            # Build enhanced prompt for scenario generation
            scenario_prompt = self._build_scenario_generation_prompt(prompt)

            # Get AI response
            response = self._get_ai_response(scenario_prompt)

            if response:
                self.logger.info("Scenario generation successful")
                return response
            else:
                self.logger.warning("AI scenario generation failed, using fallback")
                return self._get_fallback_scenario()

        except Exception as e:
            self.logger.error(f"Error in scenario generation: {e}")
            return self._get_fallback_scenario()

    def _build_action_prompt(self, action: str, details: str) -> str:
        """Build prompt for investigation action"""
        evidence_context = ""
        if self.game_context.get("evidence_discovered"):
            evidence_types = [
                e.get("type", "Unknown")
                for e in self.game_context["evidence_discovered"]
            ]
            evidence_context = (
                f"\nEvidence already discovered: {', '.join(evidence_types)}"
            )

        return f"""Player is taking investigation action: {action}
Details: {details}

{evidence_context}

Provide a realistic response about what the player discovers during this investigation action. Your response should:

1. Describe what the investigation reveals - Be specific and realistic
2. Format your response clearly - Use proper structure and formatting including line breaks for readability
3. Only mention new evidence if it's directly relevant - Not every action should reveal evidence
4. Be educational and informative - Help the player understand cybersecurity concepts
5. Maintain realism - Don't reveal everything at once

Important: The evidence discovery system handles finding new evidence separately.
Focus on describing the investigation process and what would be observed, not on announcing evidence discoveries.

Format your response with clear sections if appropriate, using proper paragraph breaks and structure for readability in a web interface.
"""

    def _build_theory_prompt(self, theory: str) -> str:
        """Build prompt for theory evaluation"""
        scenario_summary = self._get_scenario_summary()

        return f"""Player has submitted this theory about the incident:
"{theory}"

Scenario context: {scenario_summary}

Evaluate this theory and provide:
1. What aspects are correct or on the right track
2. What might need refinement or additional investigation
3. Constructive feedback to guide further investigation
4. Whether this theory demonstrates good understanding of the incident

Be supportive but accurate. Don't give away the complete answer.
"""

    def _build_hint_prompt(self, context: str) -> str:
        """Build prompt for providing hints"""
        return f"""Player is requesting a hint. Context: {context}

Current investigation status:
- Actions taken: {len(self.game_context.get('investigation_actions', []))}
- Evidence found: {len(self.game_context.get('evidence_discovered', []))}
- Theories submitted: {len(self.game_context.get('theories_submitted', []))}

Provide a helpful hint that:
1. Guides them toward productive investigation
2. Doesn't give away the answer
3. Suggests specific investigation techniques or areas to explore
4. Maintains the challenge level

Keep it concise and actionable.
"""

    def _build_scenario_generation_prompt(self, user_prompt: str) -> str:
        """Build comprehensive prompt for scenario generation"""

        system_context = """You are an expert cybersecurity scenario designer with deep knowledge of:
- Historical cyberattacks and threat actor TTPs
- MITRE ATT&CK framework and kill chain methodology
- Forensic evidence and digital artifact analysis
- Incident response procedures and investigation techniques
- Red teaming and penetration testing methodologies

Your task is to generate realistic, educational cybersecurity incident scenarios that:
1. Are technically accurate and forensically sound
2. Follow established attack patterns and TTPs
3. Include realistic evidence and artifacts
4. Provide appropriate challenge level for the specified difficulty
5. Include compelling red herrings to increase realism
6. Map to MITRE ATT&CK techniques

Generate scenarios in valid YAML format following the provided template structure exactly."""

        enhanced_prompt = f"""{system_context}

{user_prompt}

IMPORTANT GUIDELINES:
- Return only valid YAML content, no additional text or markdown
- Ensure all MITRE technique IDs are valid (format: T####)
- Include realistic technical details (IPs, domains, file hashes, etc.)
- Make evidence discoverable through logical investigation steps
- Balance difficulty appropriately for the specified complexity level
- Include 25% red herrings that are plausible but misleading
- All fictional organizations, domains, and data should be clearly fake
"""

        return enhanced_prompt

    def _get_fallback_scenario(self) -> str:
        """Return a basic fallback scenario if AI generation fails"""
        fallback = """scenario_metadata:
  name: "Generic Phishing Incident"
  id: "FALLBACK-001"
  version: "1.0"
  inspiration:
    attack_name: "Generic Phishing"
    year: 2024
    attribution: "Unknown"
    references: []
  environment:
    sector: "technology"
    organization_size: "medium"
    infrastructure: "hybrid"
  difficulty: "intermediate"
  estimated_duration: "2-3 hours"
  description: "A phishing campaign targeting employee credentials leads to unauthorized access."

attack_overview:
  summary: "Attackers used spear-phishing emails to steal credentials and gain initial access to corporate systems."
  attack_type: "credential_theft"
  sophistication_level: "medium"
  objectives:
    primary: "Credential harvesting"
    secondary: "Data exfiltration"

initial_alert:
  timestamp: "2024-06-25T14:30:00Z"
  source: "Email Security Gateway"
  alert_type: "Suspicious email detected"
  description: "Multiple employees reported receiving suspicious emails requesting credential verification."
  initial_indicators:
    - "Phishing emails from external domain"
    - "Suspicious login attempts"
    - "Unusual network traffic"

timeline:
  start: "2024-06-25T08:00:00Z"
  discovery: "2024-06-25T14:30:00Z"
  phases:
    - phase: "Initial Access"
      mitre_id: "T1566"
      start_time: "2024-06-25T08:00:00Z"
      duration: "6 hours"
      description: "Phishing campaign launched"

evidence:
  items:
    - id: "FALLBACK-E001"
      type: "email"
      source: "mail_server"
      importance: "critical"
      description: "Phishing email with malicious link"

kill_chain:
  phases:
    - name: "Initial Access"
      mitre_id: "T1566"
      techniques: ["T1566.002"]
      description: "Spearphishing link"

scoring:
  total_points: 100
  phases:
    - name: "Initial Access"
      points: 25
      criteria: ["Identify phishing vector"]
"""
        return fallback

    def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI provider"""
        system_prompt = self.get_system_prompt()
        full_prompt = f"{system_prompt}\n\n{prompt}"

        if self.provider == "google":
            # Use Vertex AI for content generation
            contents = types.Part.from_text(text=full_prompt)

            generate_content_config = types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=500,
                response_modalities=["TEXT"],
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT", threshold="OFF"
                    ),
                ],
            )

            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )

            return response.text

        elif self.provider == "openai":
            response = self._client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _process_response(self, response: str, action: str) -> FacilitatorResponse:
        """Process AI response into structured format"""
        # Simple confidence scoring based on response characteristics
        confidence = 0.8 if len(response) > 50 else 0.6

        # Extract suggestions (simple heuristic)
        suggestions = []
        if "investigate" in response.lower():
            suggestions.append("Continue investigating based on this information")
        if "evidence" in response.lower():
            suggestions.append("Document any new evidence discovered")
        if "timeline" in response.lower():
            suggestions.append("Consider the timing of events")

        return FacilitatorResponse(
            content=response,
            confidence=confidence,
            suggestions=suggestions or ["Continue your investigation"],
            requires_followup="question" in response.lower(),
        )

    def _process_theory_response(
        self, response: str, theory: str
    ) -> FacilitatorResponse:
        """Process theory evaluation response"""
        # Score confidence based on response content
        confidence = 0.9 if "correct" in response.lower() else 0.7

        suggestions = [
            "Continue building on this theory",
            "Look for additional supporting evidence",
        ]

        return FacilitatorResponse(
            content=response,
            confidence=confidence,
            suggestions=suggestions,
            additional_context=f"Theory evaluated: {theory[:50]}...",
        )

    def _get_scenario_summary(self) -> str:
        """Get a brief summary of the current scenario"""
        name = self.scenario_data.get("name", "Incident")
        attack_type = self.scenario_data.get("attack_type", "Cyber attack")
        difficulty = self.game_context.get("difficulty", "medium")
        return f"{name} - {attack_type} (Difficulty: {difficulty})"

    def get_game_summary(self) -> Dict[str, Any]:
        """Get summary of current game state"""
        return {
            "scenario": self.scenario_data.get("name"),
            "actions_taken": len(self.game_context.get("investigation_actions", [])),
            "evidence_found": len(self.game_context.get("evidence_discovered", [])),
            "theories_submitted": len(self.game_context.get("theories_submitted", [])),
            "conversation_length": len(self.conversation_history),
        }

    def display_response(
        self, response: FacilitatorResponse, title: str = "Facilitator"
    ):
        """Display a facilitator response with rich formatting"""
        # Create the main content panel
        content_text = Text(response.content)

        # Add confidence indicator
        confidence_color = (
            "green"
            if response.confidence > 0.8
            else "yellow" if response.confidence > 0.6 else "red"
        )
        confidence_text = f" (Confidence: {response.confidence:.1f})"

        panel = Panel(
            content_text,
            title=f"[bold blue]{title}[/bold blue][{confidence_color}]{confidence_text}[/{confidence_color}]",
            border_style="blue",
            padding=(1, 2),
        )

        console.print(panel)

        # Show suggestions if available
        if response.suggestions:
            console.print("\n[bold yellow]Suggestions:[/bold yellow]")
            for suggestion in response.suggestions:
                console.print(f"  • {suggestion}")

        # Show additional context if available
        if response.additional_context:
            console.print(f"\n[dim]{response.additional_context}[/dim]")

        console.print()  # Add spacing

    def _validate_openai_credentials(self) -> bool:
        """
        Validate OpenAI API credentials by making a test request

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        if not openai:
            self.logger.error("OpenAI library not available")
            return False

        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.logger.error("OPENAI_API_KEY environment variable not set")
                return False

            # Set the API key for testing
            openai.api_key = api_key

            # Test with a minimal API call to validate credentials
            self.logger.info("Testing OpenAI API credentials...")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Use cheaper model for validation
                messages=[
                    {"role": "user", "content": "Test connection. Respond with 'OK'."}
                ],
                max_tokens=5,
                temperature=0,
            )

            if response and response.choices and response.choices[0].message:
                self.logger.info("OpenAI API credentials validated successfully")
                return True
            else:
                self.logger.error("Invalid response from OpenAI API")
                return False

        except openai.error.AuthenticationError:
            self.logger.error("OpenAI API key is invalid or expired")
            return False
        except openai.error.RateLimitError:
            self.logger.warning("OpenAI API rate limit exceeded during validation")
            # Rate limit doesn't mean invalid credentials
            return True
        except openai.error.APIError as e:
            self.logger.error(f"OpenAI API error during validation: {e}")
            return False
        except openai.error.OpenAIError as e:
            self.logger.error(f"OpenAI error during validation: {e}")
            return False
        except AttributeError as e:
            # Handle case where openai module structure is different
            self.logger.error(f"OpenAI API structure error: {e}")
            self.logger.error(
                "Make sure you have the correct version of the openai library"
            )
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error validating OpenAI credentials: {e}")
            return False

    def test_connection(self) -> bool:
        """Test if the AI facilitator can make successful API calls"""
        try:
            test_response = self.facilitate_action("test connection", "")
            # If we get back the generic error message, the connection failed
            return (
                "I encountered an issue processing your action"
                not in test_response.content
            )
        except Exception:
            return False


class MockFacilitator(AIFacilitator):
    """Mock facilitator for testing and offline use"""

    def __init__(self):
        """Initialize mock facilitator without AI providers"""
        self.provider = "mock"
        self.model = "mock-model"
        self.logger = logging.getLogger(__name__)
        self._client = None

        # Game context and memory - properly initialize like the real facilitator
        self.game_context = {
            "scenario_id": None,
            "scenario_name": None,
            "difficulty": "medium",
            "attack_type": None,
            "timeline": {},
            "evidence_discovered": [],
            "theories_submitted": [],
            "investigation_actions": [],
        }
        self.conversation_history = []
        self.scenario_data = {}

    def _get_ai_response(self, prompt: str) -> str:
        """Return mock responses for testing"""
        if "theory" in prompt.lower():
            return (
                "Your theory shows good understanding of the attack pattern. "
                "Consider investigating the network logs more thoroughly to find "
                "additional evidence of lateral movement."
            )
        elif "hint" in prompt.lower():
            return (
                "Focus on the timeline of events. Look for any unusual network "
                "activity or authentication patterns that occurred around the "
                "same time as the initial alert."
            )
        else:
            return (
                "Investigation reveals important information. You should document "
                "this finding and consider how it relates to the overall attack "
                "timeline. This appears to be a significant piece of evidence."
            )


def get_facilitator(provider: str = None, model: str = None) -> AIFacilitator:
    """
    Factory function to get appropriate facilitator instance

    Args:
        provider: AI provider preference
        model: Model preference

    Returns:
        AIFacilitator instance
    """
    # Check for available providers
    if provider is None:
        # Check for Vertex AI first (API key or ADC)
        if VERTEX_AI_AVAILABLE and (
            os.getenv("GOOGLE_AI_API_KEY") or _has_adc_credentials()
        ):
            provider = "google"
        elif openai and os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            console.print(
                "[yellow]⚠️  No AI provider available, using mock facilitator[/yellow]"
            )
            console.print("[blue]💡 To enable AI facilitation:[/blue]")
            console.print("   • Set GOOGLE_AI_API_KEY environment variable, or")
            console.print("   • Run 'gcloud auth login --update-adc' for ADC")
            return MockFacilitator()

    try:
        facilitator = AIFacilitator(provider=provider, model=model)
        console.print(
            f"[green]✅ {provider.title()} AI facilitator initialized successfully[/green]"
        )
        return facilitator
    except ValueError as e:
        error_msg = str(e)

        # Handle specific error types with helpful messages
        if "authenticate" in error_msg.lower() or "credentials" in error_msg.lower():
            console.print(f"[red]❌ {provider.title()} authentication failed[/red]")

            if provider == "google":
                console.print("[blue]🔐 Google AI Authentication options:[/blue]")
                console.print(
                    "   1. [yellow]API Key (Recommended):[/yellow] Set GOOGLE_AI_API_KEY environment variable"
                )
                console.print(
                    "      Get your key at: https://makersuite.google.com/app/apikey"
                )
                console.print(
                    "   2. [yellow]ADC (Advanced):[/yellow] Run 'gcloud auth login --update-adc'"
                )
                console.print(
                    "      Note: ADC requires proper scopes and works best with service accounts"
                )
            elif provider == "openai":
                console.print("[blue]🔐 OpenAI Authentication options:[/blue]")
                console.print(
                    "   • [yellow]API Key:[/yellow] Set OPENAI_API_KEY environment variable"
                )
                console.print(
                    "     Get your key at: https://platform.openai.com/api-keys"
                )

        elif "API key" in error_msg or "invalid" in error_msg:
            console.print(f"[red]❌ {provider.title()} API credentials invalid:[/red]")
            console.print(f"[dim]{error_msg}[/dim]")

            if provider == "google":
                console.print(
                    "[yellow]💡 Tip: Verify your GOOGLE_AI_API_KEY is valid and has proper permissions[/yellow]"
                )
            elif provider == "openai":
                console.print(
                    "[yellow]💡 Tip: Verify your OPENAI_API_KEY is valid and has sufficient quota[/yellow]"
                )

        elif "not available" in error_msg or "not supported" in error_msg:
            console.print(
                f"[red]❌ {provider.title()} provider not available:[/red] {error_msg}"
            )
            console.print(
                "[yellow]💡 Install required dependencies or check provider name[/yellow]"
            )

        else:
            console.print(
                f"[red]❌ {provider.title()} initialization failed:[/red] {error_msg}"
            )

        console.print(
            "[yellow]🔄 Falling back to mock facilitator with intelligent responses[/yellow]"
        )
        return MockFacilitator()
    except Exception as e:
        console.print(
            f"[red]❌ Unexpected error initializing {provider} facilitator:[/red] {e}"
        )
        console.print("[yellow]🔄 Falling back to mock facilitator[/yellow]")
        return MockFacilitator()


def _has_adc_credentials() -> bool:
    """Check if Application Default Credentials are available"""
    try:
        from google.auth import default as google_default_credentials
        from google.auth.exceptions import DefaultCredentialsError

        # Try to get default credentials
        credentials, project = google_default_credentials()
        return True
    except (DefaultCredentialsError, ImportError):
        return False
    except Exception:
        return False
