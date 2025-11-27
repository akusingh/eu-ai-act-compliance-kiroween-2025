# Kiro Integration for EU AI Act Compliance Agent

> **🏆 Kiroween Hackathon 2025 - Showcasing Kiro AI IDE Features**

This directory contains Kiro-specific configuration that powered the development of this multi-agent compliance system.

## 📁 Directory Structure

```
.kiro/
├── steering/                              # AI context and coding guidelines
│   └── eu-ai-act-compliance.md               # EU AI Act knowledge, patterns, standards
├── hooks/                                 # Automated workflows
│   ├── validate-models-on-save.json          # Auto-test on model changes
│   ├── test-on-agent-changes.json            # Integration tests on agent updates
│   └── update-docs-on-structure-change.json  # Auto-update documentation
├── specs/                                 # Feature development templates
│   ├── eu-ai-act-compliance-implementation.md  # Current solution (COMPLETE)
│   └── add-new-regulation-support.md           # Future feature (PLANNED)
├── settings/                              # Kiro configuration
│   └── mcp.json (optional)
└── README.md                              # This file
```

## 🎯 Kiro Features Used

### 1. Steering Rules (`steering/`)
Provides AI context about the project to help Kiro understand:
- Architecture patterns (multi-agent system)
- Code standards (Python 3.13+, type hints, docstrings)
- EU AI Act knowledge (risk tiers, articles, scoring logic)
- Development workflow (TDD, testing, documentation)
- Common patterns and best practices

**How it helps:**
- Kiro generates code that follows project conventions
- Suggestions are contextually aware of EU AI Act requirements
- Maintains consistency across the codebase

### 2. Agent Hooks (`hooks/`)
Automated workflows triggered by file events:

#### `validate-models-on-save.json` ✅ ENABLED
- **Trigger**: Save `src/models.py`, `src/tools_adk.py`, or `src/evaluation.py`
- **Actions**: 
  - Run model and tool tests automatically
  - AI reviews changes for compliance pattern issues
- **Use case**: Catch scoring logic errors immediately when modifying data models or tools

#### `test-on-agent-changes.json` ❌ DISABLED
- **Trigger**: Save agent files (`sequential_orchestrator.py`, `parallel_research_agents.py`, `aggregator_agents.py`)
- **Actions**: 
  - Run integration tests for agent pipeline
  - AI analyzes failures and suggests fixes
- **Use case**: Validate agent pipeline when modifying agents
- **Note**: Disabled by default since agents are stable (enable when actively developing agents)

#### `update-docs-on-structure-change.json` ✅ ENABLED
- **Trigger**: Create new file in `src/`
- **Actions**: 
  - AI reviews if README needs updates
  - Suggests documentation changes
- **Use case**: Keep docs in sync with code structure automatically

**How to use hooks:**
1. Hooks run automatically based on triggers
2. View hook execution in Kiro's Agent Hooks panel
3. Enable/disable hooks as needed
4. Customize triggers and actions in JSON files

### 3. Specs (`specs/`)
Structured feature development templates:

#### `eu-ai-act-compliance-implementation.md` ✅ COMPLETE
Documents the **current solution**:
- Complete architecture overview (8 agents, hybrid search)
- Implementation details (all source files)
- Performance metrics (100% accuracy achieved!)
- Kiro integration showcase
- Lessons learned and challenges overcome
- Status: Production-ready

#### `add-new-regulation-support.md` 🔮 PLANNED
Plans **future feature** for multi-regulation support:
- Requirements (GDPR, CCPA, UK AI Regulation)
- Design (multi-regulation orchestrator, conflict detection)
- Implementation tasks (phased approach)
- Testing strategy
- Success criteria

**How to use specs:**
1. **Retrospective specs** - Document completed work (like implementation.md)
2. **Planning specs** - Design future features (like add-new-regulation.md)
3. Reference files with `#[[file:path/to/file.py]]`
4. Kiro uses specs for context in development
5. Track progress with checkboxes

### 4. MCP Integration (Optional)
Model Context Protocol for external data sources:

**Potential integrations:**
- Legal database APIs (EUR-Lex, LexisNexis)
- Regulatory change feeds
- Compliance knowledge bases
- Document management systems

**Setup:**
Create `.kiro/settings/mcp.json` to configure MCP servers.

## 🚀 Getting Started with Kiro

### First Time Setup

1. **Open project in Kiro IDE**
   ```bash
   # Kiro will automatically detect .kiro/ directory
   ```

2. **Review steering rules**
   - Open `.kiro/steering/eu-ai-act-compliance.md`
   - Kiro uses this for context in all interactions

3. **Enable useful hooks**
   - Open Kiro's Agent Hooks panel
   - Enable `compliance-check-on-save`
   - Enable `update-docs-on-structure-change`
   - Keep `test-on-code-change` disabled initially

4. **Try a spec**
   - Open `.kiro/specs/add-new-regulation-support.md`
   - Use Kiro's spec feature to explore implementation

### Daily Development Workflow

1. **Ask Kiro for help**
   - "How can I improve risk classification accuracy?"
   - "Add a new evaluation scenario for chatbots"
   - "Refactor the scoring logic for better maintainability"

2. **Let hooks automate**
   - Save files → tests run automatically
   - Create new files → docs update suggestions
   - Modify profiles → compliance checks run

3. **Use specs for features**
   - Create spec for new feature
   - Let Kiro guide implementation
   - Track progress with checkboxes

## 💡 Kiro Tips for This Project

### Code Generation
Ask Kiro to:
- "Create a new agent for analyzing Article 52 compliance"
- "Add a tool for querying Annex III high-risk categories"
- "Generate test scenarios for prohibited AI systems"

### Refactoring
Ask Kiro to:
- "Refactor the scoring logic to be more modular"
- "Extract common patterns from agent instructions"
- "Improve error handling in the orchestrator"

### Testing
Ask Kiro to:
- "Generate unit tests for the new tool"
- "Add edge case tests for deepfake detection"
- "Create integration tests for the full pipeline"

### Documentation
Ask Kiro to:
- "Update README with new feature documentation"
- "Generate API docs for the tools module"
- "Create a troubleshooting guide"

## 🎓 Learning Resources

### Kiro Features
- **Steering**: Provides project context to AI
- **Hooks**: Automates repetitive tasks
- **Specs**: Guides feature development
- **MCP**: Connects to external data sources

### Project-Specific
- See `steering/eu-ai-act-compliance.md` for:
  - Architecture patterns
  - Code standards
  - EU AI Act knowledge
  - Common issues & solutions

## 🤝 Contributing

When contributing to this project:

1. **Read steering rules** - Understand project conventions
2. **Use Kiro for consistency** - Let AI help maintain standards
3. **Update steering if needed** - Add new patterns/knowledge
4. **Create specs for big features** - Document design decisions
5. **Test with hooks** - Ensure quality before committing

## 📞 Questions?

Ask Kiro:
- "Explain the Kiro integration in this project"
- "How do I create a new agent hook?"
- "What steering rules apply to this code?"
- "Show me how to use specs for feature development"

---

**Built with Kiro AI IDE for Kiroween Hackathon 2025 🏆**
