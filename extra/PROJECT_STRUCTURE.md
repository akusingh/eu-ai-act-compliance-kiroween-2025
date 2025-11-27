# 🏗️ Project Structure

## EU AI Act Compliance Agent - Kiroween 2024

Built with **Kiro AI IDE** + Google ADK

---

## 📁 Root Directory

```
eu-ai-act-compliance/
├── .kiro/                      # Kiro AI IDE integration ⭐
├── src/                        # Core application code
├── tests/                      # Test suite (72 tests, 100% accuracy)
├── data/                       # EU AI Act knowledge base
├── diagrams/                   # Architecture diagrams
├── scripts/                    # Setup and utility scripts
├── logs/                       # Web UI logs
├── outputs/                    # Evaluation results
├── demo_hackathon.py          # Simulated demo (for video)
├── demo_final.py              # Real single assessment
├── evaluate.py                # Evaluation suite (8 scenarios)
├── web_demo.py                # Web UI (http://localhost:8080)
├── test_hackathon_ready.py    # Readiness checker
├── test_comprehensive.py      # Comprehensive test suite
├── quickstart.sh              # One-command setup
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
└── README.md                  # Main documentation
```

---

## 🤖 Kiro Integration (`.kiro/`)

**Purpose:** Showcases Kiro AI IDE features

```
.kiro/
├── steering/                   # AI context & project knowledge
│   └── eu-ai-act-compliance.md    # EU AI Act knowledge, patterns, standards
├── hooks/                      # Automated workflows
│   ├── compliance-check-on-save.json
│   ├── test-on-code-change.json
│   └── update-docs-on-structure-change.json
├── specs/                      # Feature development templates
│   └── add-new-regulation-support.md
└── README.md                   # Kiro integration docs
```

**Key Features:**
- **Steering Rules**: Provides EU AI Act context to AI
- **Agent Hooks**: Automates testing and compliance checks
- **Specs**: Guides structured feature development

---

## 💻 Source Code (`src/`)

**Purpose:** Core multi-agent system implementation

```
src/
├── sequential_orchestrator.py  # Main 5-agent pipeline
├── parallel_research_agents.py # 3 parallel researchers
├── aggregator_agents.py        # Legal aggregation & synthesis
├── tools_adk.py                # Compliance scoring tools
├── vector_index_tool.py        # Hybrid search (Vector + BM25 + RRF)
├── reranker_tool.py            # Cohere reranking (optional)
├── models.py                   # Pydantic data models
├── evaluation.py               # Test scenarios & evaluator
├── config.py                   # Configuration management
└── observability.py            # Logging & metrics
```

**Architecture:**
- 5 sequential agents + 3 parallel sub-agents = 8 total
- Hybrid search across 1,123 indexed chunks
- 100% accuracy on test scenarios

---

## 🧪 Tests (`tests/`)

**Purpose:** Comprehensive test coverage

```
tests/
├── test_models.py              # Data model tests (21 tests)
├── test_tools.py               # Tool validation tests (18 tests)
├── test_vector_index.py        # Search tests (20 tests)
├── test_evaluation.py          # Evaluation tests (13 tests)
├── test_integration.py         # Integration tests
├── test_observability.py       # Logging tests
├── test_utils.py               # Utility tests
└── docs/                       # Test documentation
```

**Coverage:** 72 unit tests, 90%+ code coverage

---

## 📚 Data (`data/`)

**Purpose:** EU AI Act knowledge base

```
data/
├── eu_act_recitals.txt         # 477 chunks (context & intent)
├── eu_act_articles.txt         # 562 chunks (legal requirements)
├── eu_act_annexes.txt          # 84 chunks (specific lists)
└── embeddings_cache/           # FAISS indexes (9.2 MB)
    ├── recitals/
    ├── articles/
    └── annexes/
```

**Total:** 1,123 indexed chunks from official EU AI Act

---

## 🎨 Diagrams (`diagrams/`)

**Purpose:** Visual architecture documentation

```
diagrams/
├── 01_system_architecture.png  # High-level overview
├── 02_agent_flow.png           # 5-agent pipeline
├── 03_hybrid_search.png        # Search architecture
├── 04_risk_classification.png  # Scoring logic
├── 05_testing_framework.png    # Test coverage
├── 06_data_flow.png            # Data transformations
├── 07_project_structure.png    # File organization
├── 08_cohere_reranking.png     # Reranking feature
└── *.dot                       # Graphviz source files
```

**Format:** PNG images + Graphviz .dot sources

---

## 🚀 Demo Scripts

### `demo_hackathon.py` ⭐
**Purpose:** Simulated demo for video recording
- No API key required
- Fast (~10 seconds)
- Colored terminal output
- Perfect for competition video

### `demo_final.py`
**Purpose:** Real single assessment
- Requires API key
- Tests loan approval system
- Shows full pipeline execution
- ~30-40 seconds

### `evaluate.py`
**Purpose:** Full evaluation suite
- 8 test scenarios
- 100% accuracy achieved
- Saves results to `outputs/`
- ~6-8 minutes (with rate limits)

### `web_demo.py`
**Purpose:** Web UI demo
- Beautiful interface at http://localhost:8080
- Real-time assessments
- Expandable recommendations
- Logs to `logs/` directory

---

## 📝 Documentation Files

### Competition Materials
- **COMPETITION_READY.md** - Final readiness checklist
- **DEVPOST_SUBMISSION.md** - Submission template (copy-paste ready)
- **VIDEO_SCRIPT.md** - 2-minute video script
- **SUBMISSION_CHECKLIST.md** - Step-by-step tasks
- **QUICK_REFERENCE.md** - One-page cheat sheet

### Kiro Showcase
- **KIRO_SHOWCASE.md** - Detailed Kiro features showcase
- **.kiro/README.md** - Kiro integration documentation

### Main Documentation
- **README.md** - Comprehensive project documentation
- **LICENSE** - MIT License (open source requirement)

---

## 🔧 Utility Scripts (`scripts/`)

```
scripts/
├── download_eu_ai_act.sh       # Download official EU AI Act text
├── split_eu_ai_act.py          # Split into sections
├── build_vector_indexes.py     # Build FAISS indexes
└── generate_test_docs.py       # Generate test documentation
```

---

## 📊 Output Directories

### `logs/`
- Web UI logs (timestamped)
- Request/response data
- Error tracebacks

### `outputs/`
- `evaluation.json` - Test results
- `metrics.json` - Performance metrics
- `traces.json` - Agent execution traces

---

## 🎯 Quick Commands

```bash
# Setup
./quickstart.sh

# Test readiness
python3 test_hackathon_ready.py

# Run demos
python3 demo_hackathon.py      # Simulated (no API)
python3 demo_final.py          # Real single assessment
python3 evaluate.py            # Full evaluation (100% accuracy)
python3 web_demo.py            # Web UI

# Run tests
pytest tests/ -v
python3 test_comprehensive.py
```

---

## 🏆 Competition Highlights

### Kiro Integration ⭐
- Steering rules with EU AI Act knowledge
- Agent hooks for automation
- Specs for structured development
- Built entirely with Kiro AI IDE

### Technical Innovation
- 8-agent multi-agent architecture
- Hybrid search (Vector + BM25 + RRF)
- 100% accuracy on test scenarios
- Production-ready quality

### Real-World Impact
- Solves actual EU compliance problem
- Saves days of work and thousands in costs
- Open source and accessible

---

**Built with ❤️ and Kiro AI IDE for Kiroween 2024 🏆**
