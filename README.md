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

# Generate a new scenario
python incidenter.py generate --sector finance --org-size large --infra hybrid

# Start a CLI game session
python incidenter.py play --scenario scenarios/carbanak_inspired.yaml
```

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

### Generate Custom Scenario
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
$ python incidenter.py play --scenario scenarios/carbanak_inspired.yaml

🚨 INCIDENT ALERT 🚨
A suspicious PowerShell process has been detected on a domain controller.
Time: 2024-03-15 14:23:17 UTC
Host: DC01.contoso.local
Process: powershell.exe -enc <base64_blob>

What would you like to investigate first?
> Check process details
> Examine network connections
> Review authentication logs
> Analyze PowerShell command

Enter your choice: Check process details
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
- Validate all scenarios: `python -m incidenter.py validate`

## License
