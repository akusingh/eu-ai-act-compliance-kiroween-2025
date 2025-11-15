# EU AI Act Compliance Agent

## Overview

An intelligent multi-agent system that profiles AI solutions against the EU AI Act using sequential agents, built-in tools (Google Search), memory management, comprehensive observability, and agent evaluation capabilities.

This project demonstrates advanced AI agent concepts from the Google Agents Intensive Course including:
- **Multi-agent Systems**: Sequential agents workflow (Information Gatherer → Classifier → Reporter)
- **Built-in Tools**: Google Search integration for regulatory lookup
- **Sessions & Memory**: InMemorySessionService for multi-turn conversations
- **Observability**: Structured logging, execution tracing, and metrics collection
- **Agent Evaluation**: Test framework validating classification accuracy

## Problem Statement

Organizations struggle to understand if their AI systems comply with the EU AI Act's risk-based framework. Manual compliance assessment is time-consuming, requires domain expertise, and is prone to errors. The EU AI Act defines a complex categorization system (Prohibited, High-Risk, Limited-Risk, Minimal-Risk) with specific requirements for each category.

## Solution

A conversational AI agent that:
1. Gathers information about an AI system through structured input
2. Analyzes the system against EU AI Act requirements
3. Classifies the system into risk categories
4. Identifies compliance gaps
5. Generates actionable recommendations
6. Maintains conversation history for multi-turn interactions
7. Provides full observability into decision-making process
8. Evaluates its own accuracy against known compliance cases

## Architecture

```
User Input
    |
    v
Session Manager (maintains conversation history)
    |
    v
Compliance Orchestrator (coordinates workflow)
    |
    +---> Information Gatherer Agent (validates input)
    |         |
    |         v
    +---> Compliance Classifier Agent (risk assessment)
    |         |
    |         v (uses tools: ComplianceScoringTool, GoogleSearchTool, EUAIActReferenceTool)
    |         |
    +---> Report Generator Agent (formats output)
    |
    v
Observability Layer (logging, tracing, metrics)
    |
    +---> Trace Collector (execution traces)
    +---> Metrics Collector (performance metrics)
    +---> Structured Logging (decision context)
```

## Key Features

### 1. Sequential Multi-Agent System

Three specialized agents working in sequence:

- **InformationGathererAgent**: Validates and structures AI system information
- **ComplianceClassifierAgent**: Classifies risk tier, identifies gaps, generates recommendations
- **ReportGeneratorAgent**: Formats assessment into compliance report

### 2. Built-in Tools Integration

- **GoogleSearchTool**: Searches for EU AI Act regulations and compliance information (with mock fallback)
- **ComplianceScoringTool**: Calculates compliance scores using EU AI Act framework
- **EUAIActReferenceTool**: Accesses EU AI Act articles and fetches from official source (https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

### 3. Sessions & Memory Management

- **SessionManager**: In-memory session service with automatic timeout handling
- **ConversationMemory**: Maintains conversation history and context for multi-turn interactions
- **Context Window**: Keeps last 10 messages in context for agent reference

### 4. Comprehensive Observability

- **Structured Logging**: All agent actions logged with context and reasoning
- **Execution Tracing**: Full trace of agent decisions (what → why → result)
- **Metrics Collection**: 
  - Profile creation metrics
  - Classification accuracy
  - Report generation metrics
  - Evaluation metrics
  - Processing latency

### 5. Agent Evaluation Framework

- **8 Test Scenarios**: Covering all risk categories (Prohibited, High-Risk, Limited-Risk, Minimal-Risk)
- **Accuracy Metrics**: Validates classification correctness
- **Detailed Reports**: Scenario-by-scenario results and analysis

## Risk Classification

The agent classifies AI systems into four categories defined by EU AI Act:

1. **Prohibited (Risk Score ≥ 80)**
   - Examples: Mass surveillance facial recognition, social credit scoring
   - Articles: Article 5
   - Requirement: Cannot be deployed

2. **High-Risk (Risk Score 60-79)**
   - Examples: Loan approval, hiring decisions, law enforcement
   - Articles: Articles 6, 8, 9
   - Requirements: Risk assessment, human oversight, monitoring

3. **Limited-Risk (Risk Score 30-59)**
   - Examples: Chatbots, deepfakes, recommendation systems
   - Articles: Articles 52, 53
   - Requirements: Transparency, user disclosure

4. **Minimal-Risk (Risk Score < 30)**
   - Examples: General ML, weather prediction, music recommendations
   - Requirements: Standard documentation

## Setup

### Prerequisites

- Python 3.9+
- pip package manager

### Installation

1. Clone repository and navigate to directory:
```bash
cd kaggle-capstone
```

2. Run setup script:
```bash
bash setup.sh
```

This will:
- Create virtual environment (if not exists)
- Install dependencies
- Create .env file from template

### Configuration

1. Copy environment template:
```bash
cp .env.example .env
```

2. Add API keys to `.env`:
```
GOOGLE_GENAI_API_KEY=your_gemini_api_key
SERPAPI_API_KEY=your_serpapi_key
LOG_LEVEL=INFO
ENVIRONMENT=development
```

Note: If API keys are not provided, the system uses mock implementations for demo purposes.

### Activate Virtual Environment

```bash
source venv/bin/activate
```

## Usage

### Run Demo

```bash
python3 demo.py
```

Shows:
- Basic compliance assessments
- Session management and memory
- Tool integration
- Observability features

Output files created in `outputs/`:
- `traces.json`: Execution traces
- `metrics.json`: Performance metrics

### Run Evaluation

```bash
python3 evaluate.py
```

Runs 8 test scenarios and generates accuracy report.

### Use as Library

```python
from src.orchestrator import ComplianceOrchestrator
from src.sessions import SessionManager, ConversationMemory

# Create orchestrator
orchestrator = ComplianceOrchestrator()

# Assess AI system
system_info = {
    "system_name": "Loan Approval System",
    "use_case": "Creditworthiness assessment",
    "data_types": ["financial", "personal_data"],
    "decision_impact": "significant",
    "affected_groups": "Loan applicants",
    "autonomous_decision": True,
    "human_oversight": True,
    "error_consequences": "Severe - affects credit decisions",
}

result = orchestrator.assess_system(system_info)

print(f"Risk Tier: {result['assessment']['risk_tier']}")
print(f"Risk Score: {result['assessment']['risk_score']}/100")
print(f"Confidence: {result['assessment']['confidence_score']}")
```

### Session Management

```python
from src.sessions import SessionManager, ConversationMemory

# Create session manager
session_manager = SessionManager(timeout_seconds=3600)

# Create session
session = session_manager.create_session()

# Use memory for multi-turn conversation
memory = ConversationMemory(session)

memory.add_exchange(
    user_message="I'm building a facial recognition system",
    assistant_response="That's a high-risk system. Let me assess it."
)

# Get context for agent
context = memory.get_context_for_agent()
```

## Project Structure

```
kaggle-capstone/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── setup.sh                 # Setup script
├── demo.py                  # Demo script
├── evaluate.py              # Evaluation runner
├── SPRINT_TRACKER.md        # Development progress
│
├── src/                     # Source code
│   ├── __init__.py          # Package init
│   ├── config.py            # Configuration management
│   ├── models.py            # Data models (Pydantic)
│   ├── agents.py            # Agent implementations
│   ├── orchestrator.py      # Agent orchestrator
│   ├── tools.py             # Tools (Google Search, scoring, reference)
│   ├── sessions.py          # Session and memory management
│   ├── observability.py     # Logging, tracing, metrics
│   └── evaluation.py        # Evaluation framework
│
├── tests/                   # Unit tests
│   └── test_*.py           # Test files
│
├── outputs/                 # Generated outputs
│   ├── traces.json         # Execution traces
│   ├── metrics.json        # Performance metrics
│   └── evaluation.json     # Evaluation results
│
└── logs/                    # Log files
    └── *.log               # Application logs
```

## Features Demonstrated

This submission demonstrates 5 core concepts from the Agents Intensive Course:

1. **Multi-agent System** (Sequential Agents)
   - Three specialized agents working in sequence
   - Clean separation of concerns
   - State passing between agents

2. **Built-in Tools** (Google Search)
   - Integration with external tools (Google Search API)
   - Mock fallback for testing
   - EU AI Act reference tool

3. **Sessions & Memory** (InMemorySessionService)
   - Session management with timeout
   - Conversation history tracking
   - Context window management
   - Multi-turn interaction support

4. **Observability** (Logging, Tracing, Metrics)
   - Structured logging throughout
   - Complete execution tracing
   - Metrics collection
   - Performance monitoring

5. **Agent Evaluation** (Accuracy Testing)
   - 8 test scenarios covering all risk categories
   - Accuracy metrics
   - Detailed evaluation reports

## Observability Outputs

### Traces (traces.json)

```json
{
  "timestamp": "2025-11-15T14:30:00.000Z",
  "agent": "Orchestrator",
  "action": "start_assessment",
  "status": "started",
  "input": {...},
  "output": {...}
}
```

### Metrics (metrics.json)

```json
{
  "metric_name": "classification_completed",
  "value": 1,
  "elapsed_seconds": 0.25,
  "tags": {"risk_tier": "high_risk"}
}
```

## Evaluation Results

The agent achieves high accuracy across test scenarios:

- **Prohibited Systems**: Correctly identifies prohibited practices
- **High-Risk Systems**: Accurately classifies high-risk applications
- **Limited-Risk Systems**: Properly categorizes limited-risk systems
- **Minimal-Risk Systems**: Correctly identifies minimal-risk applications

## Dependencies

- `google-genai`: Google Generative AI API
- `google-search-results`: SerpAPI for search
- `requests`: HTTP library
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation
- `structlog`: Structured logging
- `pytest`: Testing framework

## Compliance & Security

- No API keys stored in code (uses environment variables via .env)
- All sensitive data handled securely
- Comprehensive error handling
- Input validation on all system profiles

## EU AI Act Reference

Key Articles Referenced:
- **Article 5**: Prohibited AI Practices
- **Article 6**: Classification as High-Risk
- **Article 8**: Risk Assessment for High-Risk Systems
- **Article 9**: Risk Mitigation Measures
- **Article 52**: Transparency Requirements
- **Article 53**: User Notification

Official Source: https://eur-lex.europa.eu/eli/reg/2024/1689/oj

## Future Enhancements

1. Integration with real LLMs (Gemini, GPT) for reasoning
2. NLP-based use case analysis
3. Risk assessment refinement with ML models
4. Persistent storage for sessions
5. Web API endpoint deployment
6. Dashboard for compliance reports
7. Audit trail and compliance documentation generation

## Author

Arun Kumar Singh

## License

MIT License
