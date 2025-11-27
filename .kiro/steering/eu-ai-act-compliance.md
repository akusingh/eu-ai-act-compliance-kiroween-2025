---
inclusion: always
---

# EU AI Act Compliance Agent - Kiro Steering Rules

## Project Overview

This is an EU AI Act compliance assessment system built with:
- **Kiro AI IDE** for AI-assisted development
- **Google ADK** for multi-agent orchestration
- **Gemini 2.0 Flash** for all agents
- **Hybrid Search** (Vector + BM25 + RRF)

## Architecture Principles

### Multi-Agent System
- 5 sequential agents: InformationGatherer → ParallelResearchTeam → LegalAggregator → ComplianceClassifier → ReportGenerator
- 3 parallel sub-agents: RecitalsResearcher, ArticlesResearcher, AnnexesResearcher
- State management via ADK's `output_key` pattern

### Code Standards
- **Python 3.13+** required
- **Type hints** for all function signatures
- **Docstrings** for all public functions and classes
- **Pydantic models** for data validation
- **pytest** for all tests (target 90%+ coverage)

### Testing Requirements
- Unit tests for all tools and models
- Integration tests for agent pipeline
- Evaluation scenarios for accuracy measurement
- All tests must pass before commit

### Documentation Standards
- Clear README with quick start
- Architecture diagrams in diagrams/
- Inline comments for complex logic
- API documentation for all tools

## EU AI Act Knowledge

### Risk Tiers (Official Classification)
1. **PROHIBITED** (Unacceptable Risk) - Score ≥85
   - Social credit scoring
   - Subliminal manipulation
   - Real-time biometric identification in public spaces
   - Exploitation of vulnerabilities

2. **HIGH_RISK** - Score 55-84
   - Critical infrastructure
   - Education/employment decisions
   - Law enforcement
   - Credit scoring
   - Biometric identification

3. **LIMITED_RISK** - Score 25-54
   - Chatbots (transparency required)
   - Emotion recognition
   - Deepfake detection
   - Content generation with disclosure

4. **MINIMAL_RISK** - Score 0-24
   - Spam filters
   - Game AI
   - Music recommendations
   - Entertainment systems

### Key Articles to Reference
- **Article 5**: Prohibited AI practices
- **Article 6**: High-risk AI system classification
- **Article 8**: Compliance requirements for high-risk systems
- **Article 9**: Risk management system
- **Article 52**: Transparency obligations
- **Article 53**: Deployer transparency
- **Annex III**: List of high-risk AI systems

## Scoring Logic

### Base Score Calculation (0-100)
```python
score = (
    decision_impact_weight * 0.30 +  # 30%
    data_sensitivity * 0.25 +         # 25%
    autonomous_decision * 0.25 +      # 25%
    human_oversight_penalty * 0.20    # 20%
)
```

### Context-Aware Adjustments
- **Deepfake detection** (not generation) → LIMITED_RISK (35-50)
- **Entertainment recommendations** → MINIMAL_RISK (10-20)
- **Financial decisions** → HIGH_RISK (60-79)
- **Social scoring** → PROHIBITED (85-100)

### Pattern Matching Rules
- Check PURPOSE and USE_CASE for context
- "Detection" vs "Generation" matters
- "Entertainment" vs "Critical" matters
- Human oversight reduces risk by 10-15 points

## Development Workflow

### When Adding New Features
1. Write tests first (TDD)
2. Implement feature
3. Update documentation
4. Run full test suite
5. Update evaluation scenarios if needed

### When Fixing Bugs
1. Add failing test that reproduces bug
2. Fix the bug
3. Verify test passes
4. Check for similar issues elsewhere
5. Update documentation if behavior changed

### When Refactoring
1. Ensure all tests pass before starting
2. Refactor incrementally
3. Run tests after each change
4. Update documentation
5. Verify evaluation accuracy unchanged

## Common Patterns

### Creating New Agents
```python
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

agent = Agent(
    name="AgentName",
    model=Gemini(model="gemini-2.0-flash"),
    instruction="Clear, specific instructions...",
    tools=[tool1, tool2],
    output_key="state_key",  # For sequential pipelines
    description="Brief description"
)
```

### Creating New Tools
```python
from google.adk.tools import BaseTool

class MyTool(BaseTool):
    name = "tool_name"
    description = "What this tool does..."
    
    def __init__(self):
        super().__init__(name=self.name, description=self.description)
    
    def execute(self, input_data: str) -> str:
        # Tool logic here
        return json.dumps(result)
```

### Adding Test Scenarios
```python
from src.evaluation import EvaluationScenario
from src.models import RiskTier

scenario = EvaluationScenario(
    scenario_id="s_unique_id",
    system_info={
        "system_name": "...",
        "use_case": "...",
        # ... other fields
    },
    expected_risk_tier=RiskTier.HIGH_RISK,
    description="Brief description"
)
```

## Performance Targets

- **Accuracy**: ≥85% overall, 100% on high-stakes (prohibited + high-risk)
- **Processing Time**: 30-40 seconds per assessment
- **Test Coverage**: ≥90%
- **Cache Hit Rate**: ≥90% for repeated queries

## File Organization

```
src/
├── config.py              # Configuration management
├── models.py              # Pydantic data models
├── sequential_orchestrator.py  # Main pipeline
├── parallel_research_agents.py # Parallel researchers
├── aggregator_agents.py   # Aggregation & reporting
├── tools_adk.py           # Scoring & reference tools
├── vector_index_tool.py   # Hybrid search
├── reranker_tool.py       # Cohere reranking
├── evaluation.py          # Test scenarios
└── observability.py       # Logging & metrics
```

## Kiro-Specific Features

### Agent Hooks
- Auto-run compliance check on file save
- Update tests when code changes
- Regenerate docs on structure change

### Steering Rules
- This file provides context to Kiro
- Helps with code generation
- Ensures consistency

### MCP Integration
- Connect to legal databases
- Access EU AI Act updates
- Query regulatory changes

## Common Issues & Solutions

### Issue: Agent not calling tool
**Solution**: Make instruction more explicit about WHEN to call tool

### Issue: State not passing between agents
**Solution**: Verify `output_key` is set and next agent references it

### Issue: Scoring inconsistent
**Solution**: Check context-aware adjustments in `_apply_contextual_adjustments`

### Issue: Tests failing intermittently
**Solution**: Check for API rate limits, add retries

### Issue: Vector search slow
**Solution**: Verify embeddings are cached, check FAISS index size

## Best Practices

1. **Always use type hints** - Helps Kiro understand code
2. **Write descriptive docstrings** - Kiro uses these for context
3. **Keep functions small** - Easier for AI to understand and modify
4. **Test edge cases** - Don't just test happy path
5. **Document assumptions** - Make implicit knowledge explicit
6. **Use meaningful names** - `calculate_risk_score` not `calc_rs`
7. **Avoid magic numbers** - Use named constants
8. **Handle errors gracefully** - Don't let exceptions crash pipeline

## Resources

- EU AI Act Official Text: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- Google ADK Docs: https://github.com/google/adk
- Gemini API: https://ai.google.dev/
- FAISS: https://github.com/facebookresearch/faiss

## Questions to Ask Kiro

- "How can I improve the accuracy of risk classification?"
- "What's the best way to add a new evaluation scenario?"
- "How do I optimize the hybrid search performance?"
- "Can you help me refactor this agent's instruction?"
- "What tests should I add for this new feature?"

---

**This steering file helps Kiro understand the project context and maintain consistency across development.**
