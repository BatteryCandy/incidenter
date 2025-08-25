<img src="image.png" alt="Incidenter" width="250">  

# Incidenter - Tabletop Cybersecurity Incident Simulator

Incidenter is a CLI and web-based tabletop cybersecurity incident response game that uses real-world historical attacks as inspiration to build fictional but realistic incident scenarios. Players act as an incident response team attempting to identify the attacker's full kill chain based on investigative actions and clues returned by an AI facilitator.

## Features

- **Realistic Scenarios**: Based on historical attacks (Carbanak, NotPetya, MOVEit, etc.)
- **Dual Interface**: CLI and web-based gameplay options
- **Interactive Investigation**: Realistic forensic clues and evidence gathering
- **AI Facilitator**: Vertex AI-powered facilitator with enterprise-grade capabilities and intelligent fallback responses
- **Scoring System**: Evaluates player responses against actual attack methodology
- **Red Herrings**: 25% of clues are intentional misdirections
- **Session Management**: Save and resume investigation sessions
- **Customizable**: Generate scenarios based on sector, organization size, and infrastructure

## Quick Start

### CLI Interface
```bash
# Install dependencies
pip install -r requirements.txt

# Ensure everything is ready to pla 
python incidenter.py setup

# List available scenarios
python incidenter.py list-scenarios

# Validate all scenarios
python incidenter.py validate

# Validate only library scenarios  
python incidenter.py validate --library-only

# Validate only generated scenarios
python incidenter.py validate --generated-only

# Validate a specific scenario
python incidenter.py validate scenarios/library/carbanak_inspired.yaml

# Generate a new scenario
python incidenter.py generate --sector finance --org-size large --infra hybrid

# Start a CLI game session
python incidenter.py play scenarios/library/carbanak_inspired.yaml
```

## AI Facilitator Requirements

Incidenter uses AI to provide intelligent, context-aware facilitation during incident response scenarios. The system supports multiple AI providers with automatic fallback to mock responses if no AI is configured.

### Supported AI Providers

#### Google AI (Recommended)
- **Gemini API**: Easiest setup, best for individual use
- **Vertex AI**: Enterprise-grade, best for production deployments

#### OpenAI
- **GPT Models**: Alternative AI provider support

### Authentication Setup

#### Option 1: Google AI API Key (Recommended)
```bash
# Get your API key from https://makersuite.google.com/app/apikey
export GOOGLE_AI_API_KEY="your_api_key_here"

# Test the connection
python incidenter.py setup
```

#### Option 2: Google Cloud Application Default Credentials (ADC)
```bash
# Install Google Cloud CLI
# macOS: brew install google-cloud-sdk
# Windows/Linux: https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth login --update-adc

# Set your project (optional, but recommended)
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Test the connection
python incidenter.py setup
```

#### Option 3: OpenAI API Key - technically havent tested openAI. Maybe ill get a key, maybe i wont.
```bash
# Get your API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="your_openai_api_key_here"

# Test the connection
python incidenter.py setup
```

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `GOOGLE_AI_API_KEY` | Gemini API authentication | For Google AI |
| `GOOGLE_CLOUD_PROJECT` | GCP project for Vertex AI | For ADC setup |
| `OPENAI_API_KEY` | OpenAI API authentication | For OpenAI |

### Fallback Behavior

If no AI provider is configured, Incidenter automatically falls back to:
- **Mock Facilitator**: Pre-scripted responses based on scenario structure
- **Static Evidence**: Deterministic clue delivery without AI enhancement
- **Basic Scoring**: Rule-based evaluation without AI insights

This ensures the game remains fully functional even without AI credentials.

## CLI Game Structure

### Scenario Components
- **Initial Alert**: Starting point that players receive
- **Kill Chain Phases**: MITRE ATT&CK mapped progression
- **Evidence Pool**: Technical artifacts, logs, and forensic data
- **Red Herrings**: Misleading but realistic evidence
- **Scoring Rubric**: Points awarded for correct deductions

### Investigation Flow
1. Players receive initial alert/indicator
2. Request specific investigation steps ("Check firewall logs", "Examine IAM roles")
3. AI facilitator provides one clue per request
4. Players build timeline and identify attack methodology
5. Submit kill chain theory for scoring

## Directory Structure

```
incidenter/
├── scenarios/           # Pre-built and generated scenarios
│   └── library/        # 8 validated historical scenarios
├── server/             # Flask web interface
│   ├── app.py         # Main web server
│   └── templates/     # HTML templates
├── cli/               # Command-line interface components
├── facilitator/       # AI facilitator logic with fallbacks
├── utils/             # Session management and shared utilities
├── scoring/           # Scoring and evaluation system
└── templates/         # Scenario generation templates
```

## Scenario Categories

### Pre-built Historical Scenarios
- **WannaCry**: Ransomware worm targeting SMB vulnerabilities
- **Target**: Retail POS system credit card breach
- **Equifax**: SQL injection leading to massive data exposure
- **Carbanak**: Financial sector APT with ATM manipulation
- **Colonial Pipeline**: Ransomware attack on critical infrastructure
- **MOVEit**: Supply chain file transfer compromise
- **SolarWinds**: Software supply chain attack
- **NotPetya**: State-sponsored destructive malware

### Customizable Parameters
- **Sector**: Finance, Healthcare, Government, Technology
- **Organization Size**: Small (<500), Medium (500-5000), Large (5000+)
- **Infrastructure**: On-premises, Cloud, Hybrid
- **Complexity**: Beginner, Intermediate, Advanced

## Usage Examples

### Generate Custom Scenario. 
Scenario generation is iffy at the moment.  Needs refined into multi step prompts.   
```bash
python incidenter.py generate \
  --sector healthcare \
  --org-size medium \
  --infra cloud \
  --complexity intermediate \
  --base-attack ransomware \
  --output scenarios/custom_healthcare.yaml
```

### Interactive Gameplay

#### CLI Interface
```bash
$ python incidenter.py play scenarios/library/carbanak_inspired.yaml

🚨 INCIDENT RESPONSE EXERCISE
Loading scenario and initializing AI facilitator...

✅ Google AI facilitator initialized successfully
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🚨 INCIDENT RESPONSE EXERCISE 🚨                                                                                                                                       │
│                                                                                                                                                                        │
│ Scenario: Operation Digital Heist                                                                                                                                      │
│ Organization: Regional Trust Bank                                                                                                                                      │
│ Sector: Finance                                                                                                                                                        │
│ Difficulty: Hard                                                                                                                                                       │
│ Team Size: 1                                                                                                                                                           │
│ Estimated Duration: 90 minutes                                                                                                                                         │
│                                                                                                                                                                        │
│                                                                                                                                                                        │
│ You are the incident response team for this organization.                                                                                                              │
│ Your goal is to investigate the incident, identify the attack methodology,                                                                                             │
│ and reconstruct the complete attack timeline.                                                                                                                          │
│                                                                                                                                                                        │
│ ⚠️  Remember: Not all evidence is reliable. Stay vigilant for red herrings! ⚠️                                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────────────────────── Instructions ─────────────────────────────────────────────────────────────────────────────╮
│ How to Play:                                                                                                                                                           │
│ • Ask specific investigative questions (e.g., "Check firewall logs", "Examine running processes")                                                                      │
│ • You can request up to 20 investigation questions                                                                                                                     │
│ • The AI facilitator will provide one clue per investigation                                                                                                           │
│ • Build your theory of the attack as you gather evidence                                                                                                               │
│ • Submit your final assessment when ready                                                                                                                              │
│                                                                                                                                                                        │
│ Commands:                                                                                                                                                              │
│ • Type your investigation request naturally                                                                                                                            │
│ • Type 'theory' to submit your current attack theory                                                                                                                   │
│ • Type 'status' to see your progress                                                                                                                                   │
│ • Type 'evidence' to view discovered clues                                                                                                                             │
│ • Type 'help' for more options                                                                                                                                         │
│ • Type 'quit' to exit (you can resume later)                                                                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Press Enter to begin the incident response...

╭──────────────────────────────────────────────────────────────────────────── Initial Alert ─────────────────────────────────────────────────────────────────────────────╮
│ 🚨 SECURITY ALERT 🚨                                                                                                                                                   │
│                                                                                                                                                                        │
│ Alert Type: High                                                                                                                                                       │
│ Severity: UNKNOWN                                                                                                                                                      │
│ Source: Unknown                                                                                                                                                        │
│ Time: 2024-05-20 09:30:00                                                                                                                                              │
│                                                                                                                                                                        │
│ Description:                                                                                                                                                           │
│ Unusual encrypted traffic patterns detected to external IP addresses. Multiple endpoints showing signs of compromise.                                                  │
│                                                                                                                                                                        │
│ Raw Alert Data:                                                                                                                                                        │
│ No additional raw data available.                                                                                                                                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────────────────────────────────────────────── Status ────────────────────────────────────────────────────────────────────────────────╮
│ Investigation Questions Remaining: 20                                                                                                                                  │
│ Clues Discovered: 0                                                                                                                                                    │
│ Current Score: 0                                                                                                                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

What would you like to investigate?: investigate the reputation of the external ip addresses

╭──────────────────────────────────────────────────────────────────────── Investigation Results ─────────────────────────────────────────────────────────────────────────╮
│ Investigation Request: investigate the reputation of the external ip addresses                                                                                         │
│                                                                                                                                                                        │
│ Findings:                                                                                                                                                              │
│ Okay, let's investigate the reputation of those external IP addresses. This is a crucial step in understanding the source and potential severity of the incident.      │
│ Here's what you find:                                                                                                                                                  │
│                                                                                                                                                                        │
│ **Reputation Analysis Results:**                                                                                                                                       │
│                                                                                                                                                                        │
│ *   **IP Address 1 (Let's call it 203.0.113.1):** This IP address is listed on several public blocklists (Spamhaus, AbuseIPDB) with a moderate to high confidence      │
│ score for sending spam and being involved in brute-force attacks. There are also reports indicating it has recently hosted phishing sites.                             │
│                                                                                                                                                                        │
│ *   **IP Address 2 (Let's call it 198.51.100.2):** This IP has a relatively clean reputation. Some historical data shows it was associated with a Tor exit node a few  │
│ months ago, but no recent malicious activity is attributed to it. It's possible this IP is being used legitimately or has been compromised recently.                   │
│                                                                                                                                                                        │
│ *   **IP Address 3 (Let's call it 192.0.2.3):** This IP address is associated with a known cloud hosting provider (e.g., AWS, Azure, GCP). This doesn't automatically  │
│ mean it's malicious, but it warrants closer scrutiny, as attackers frequently use cloud infrastructure to mask their activities. You'll need to investigate further to │
│ determine its role in the incident.                                                                                                                                    │
│                                                                                                                                                                        │
│ **Interpretation:**                                                                                                                                                    │
│                                                                                                                                                                        │
│ The presence of one IP address (203.0.113.1) on multiple blocklists strongly suggests malicious activity originating from that source. The second IP (198.51.100.2)    │
│ being a former Tor exit node is not necessarily malicious in and of itself, but warrants keeping an eye on. The third IP (192.0.2.3) requires more investigation since │
│ it is from a cloud provider. This could be legitimate traffic, or an attacker using cloud resources.                                                                   │
│                                                                                                                                                                        │
│ This information can help you prioritize your investigation efforts and potentially block or rate-limit traffic from the identified malicious IP address (203.0.113.1) │
│ to contain the incident. Remember to consider the possibility of false positives and investigate further before taking drastic actions that could disrupt legitimate   │
│ business operations.                                                                                                                                                   │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

💡 Suggested follow-up investigations:
  1. Continue investigating based on this information

Would you like to submit your theory now? [y/n] (n): n
╭──────────────────────────────────────────────────────────────────────────────── Status ────────────────────────────────────────────────────────────────────────────────╮
│ Investigation Questions Remaining: 19                                                                                                                                  │
│ Clues Discovered: 1                                                                                                                                                    │
│ Current Score: 0                                                                                                                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

What would you like to investigate?: evidence
                                                                 Discovered Evidence                                                                 
┏━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID       ┃ Time     ┃ Investigation                            ┃ Key Findings                                                                     ┃
┡━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ E001     │ 3.183    │ investigate the reputation of the e...   │ This is a crucial step in understanding the source and potential severity o...   │
└──────────┴──────────┴──────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────┘

Total Evidence Items: 1
Unique Clues Discovered: 1

💡 Tip: Use 'evidence detail E001' to see full details for a specific evidence item
```

#### Web Interface
1. Navigate to `http://localhost:5003`
2. Browse available scenarios with detailed metadata
3. Start an interactive game session
4. Use the hint system for investigation guidance
5. Submit theories and receive intelligent feedback
6. Track progress and manage multiple sessions

## Web Interface Features

- **Scenario Browser**: Visual catalog of all available scenarios
- **Interactive Sessions**: Point-and-click investigation interface
- **Evidence Tracking**: Automatically tracks discovered clues
- **Hint System**: Contextual guidance during investigations
- **Theory Submission**: Submit and evaluate kill chain theories
- **Session Management**: Save, resume, and manage multiple games
- **Responsive Design**: Works on desktop, tablet, and mobile
- **AI Fallbacks**: Intelligent responses even without AI API keys


## Contributing

### Adding New Scenarios
1. Add new historical attack scenarios in `scenarios/library/`
2. Follow the established YAML structure with `scenario_metadata` wrapper
3. Include all required sections: `attack_overview`, `initial_alert`, `inspiration`, `environment`
4. Validate with: `python -m incidenter.py validate`

### Development
1. **CLI Improvements**: Add OpenAI support. Enhance command-line interface in `cli/`
2. **Web Interface**: Improve templates and functionality in `server/`: vibe code - probably lots of happy accidents lingering
3. **AI Facilitator**: Test Support for OpenAI. Enhance prompts and responses in `facilitator/` 
4. **Scoring**: Improve evaluation algorithms in `scoring/`
5. **Infra**: Make simple Terraform template for GCP/AWS
6. **Testing**: Feels like an AI job now
7. **MITRE ATT&CK**: This is just a small sample of tactics and techniques. Need to add full support. 

### Testing

- Run all tests: `python tests/run_all_tests.py`
- Run web interface tests: `python tests/test_web_interface.py`
- Run GCP authentication + AI facilitator tests: `python tests/test_gcp_credentials.py`
- Validate all scenarios: `python incidenter.py validate`
- Validate only library scenarios: `python incidenter.py validate --library-only`
- Validate specific scenario: `python incidenter.py validate scenarios/library/scenario.yaml`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

- Based on real-world cybersecurity incidents for educational purposes
- Inspired by MITRE ATT&CK framework for kill chain methodology
- Built with AI-powered facilitation for enhanced learning experiences
