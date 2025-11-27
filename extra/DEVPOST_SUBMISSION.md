# Devpost Submission Template
## EU AI Act Compliance Agent - Kiroween 2024

---

## 📝 PROJECT TITLE
**EU AI Act Compliance Agent - Multi-Agent Risk Assessment System**

---

## 🎯 TAGLINE (50 characters max)
Automate EU AI Act compliance in 30 seconds

---

## 📖 INSPIRATION

The EU AI Act (2024) is the world's first comprehensive AI regulation, affecting thousands of companies. Every AI system must be classified into risk tiers (Prohibited, High-Risk, Limited-Risk, or Minimal-Risk), each with different compliance requirements.

Manual assessment requires:
- Legal expertise in EU regulations
- Days of document review
- Thousands of dollars in consulting fees
- Risk of misclassification

We asked: **What if AI could assess AI compliance?**

---

## 💡 WHAT IT DOES

The EU AI Act Compliance Agent is a multi-agent system that automatically assesses AI systems against EU regulations:

### Core Features:
- **Automated Risk Classification** - Analyzes AI systems and assigns risk tiers
- **Multi-Source Research** - Searches across Recitals, Articles, and Annexes
- **Compliance Gap Analysis** - Identifies specific requirements not met
- **Actionable Recommendations** - Provides step-by-step compliance guidance
- **Citation-Backed Results** - Every finding references specific EU AI Act articles

### Technical Capabilities:
- **8 Specialized Agents** - 5 sequential + 3 parallel researchers
- **1,123 Indexed Chunks** - Complete EU AI Act text
- **Hybrid Search** - Vector embeddings + BM25 + RRF fusion
- **87.5% Accuracy** - 100% on high-stakes (prohibited + high-risk) systems
- **30-40 Second Processing** - Fast enough for production use

### Input:
- AI system description
- Data types processed
- Decision impact level
- Human oversight details
- Error consequences

### Output:
- Risk tier classification
- Risk score (0-100)
- Relevant EU AI Act articles
- Compliance gaps identified
- Prioritized recommendations
- Confidence score

---

## 🛠️ HOW WE BUILT IT

### Architecture:
**5-Agent Sequential Pipeline:**
1. **InformationGatherer** - Validates and structures input
2. **ParallelResearchTeam** - 3 agents search simultaneously:
   - RecitalsResearcher (477 chunks - context & intent)
   - ArticlesResearcher (562 chunks - legal requirements)
   - AnnexesResearcher (84 chunks - specific lists)
3. **LegalAggregator** - Synthesizes findings with cross-source reranking
4. **ComplianceClassifier** - Calculates risk score and assigns tier
5. **ReportGenerator** - Formats structured compliance report

### Technology Stack:
- **Kiro AI IDE** ⭐ - AI-assisted development with:
  - **Steering Rules** - Project context & EU AI Act knowledge
  - **Agent Hooks** - Automated testing & compliance checks
  - **Specs** - Structured feature development
  - **AI Code Generation** - 10,000+ lines generated
- **Google ADK** - Multi-agent orchestration framework
- **Gemini 2.0 Flash** - Powers all 8 agents (fast + cost-effective)
- **FAISS** - Vector similarity search
- **BM25** - Keyword-based retrieval
- **Cohere** - Cross-encoder reranking (optional, +7.5% accuracy)
- **Python** - Core implementation
- **pytest** - 72 unit tests

### Hybrid Search Innovation:
We implemented a 3-stage search pipeline:
1. **Vector Search** - Semantic matching with Gemini embeddings
2. **BM25 Search** - Keyword matching for exact terms
3. **RRF Fusion** - Reciprocal Rank Fusion combines both rankings

This hybrid approach handles both semantic queries ("systems that affect employment") and exact matches ("Article 5").

### Data Processing:
- Downloaded official EU AI Act from EUR-Lex
- Split into 3 sources (Recitals, Articles, Annexes)
- Chunked with 800-character windows and 200-character overlap
- Generated embeddings with Gemini text-embedding-004
- Built FAISS indexes with caching for fast loading

### Development Process:
Built entirely with **Kiro AI IDE** - showcasing all major features:

**Steering Rules** (`.kiro/steering/`):
- Provided EU AI Act context to AI
- Defined architecture patterns and code standards
- Enabled consistent code generation across 10,000+ lines

**Agent Hooks** (`.kiro/hooks/`):
- Automated compliance checks on file save
- Continuous testing during development
- Auto-updated documentation on structure changes

**Specs** (`.kiro/specs/`):
- Structured feature development (e.g., multi-regulation support)
- Design-first approach with phased implementation
- Progress tracking with checkboxes

**AI-Assisted Development**:
- Generated 10,000+ lines of Python code
- Created 72 unit tests automatically
- Refactored for maintainability
- Documented complex logic
- **Time saved: 78%** (6 days → 13 hours)

---

## 🚧 CHALLENGES WE RAN INTO

### 1. Context-Aware Risk Scoring
**Problem**: Simple keyword matching failed. "Deepfake" could mean detection (limited-risk) or generation (high-risk).

**Solution**: Implemented context-aware pattern matching that analyzes surrounding text to understand intent.

### 2. Balancing Search Methods
**Problem**: Vector search missed exact article references. BM25 missed semantic queries.

**Solution**: Hybrid search with RRF fusion. Best of both worlds without manual score normalization.

### 3. Parallel Agent State Management
**Problem**: ADK's ParallelAgent needed careful state passing between sequential stages.

**Solution**: Used `output_key` for clean state management. Each agent writes to a specific key that next agents read from.

### 4. Performance Optimization
**Problem**: Initial implementation took 60+ seconds per assessment.

**Solution**: 
- Parallel research (3 agents simultaneously)
- Vector index caching (9.2 MB cache, instant loading)
- Optimized chunk sizes (800 chars with 200 overlap)
- Result: 30-40 seconds per assessment

### 5. Test Scenario Edge Cases
**Problem**: Some scenarios failed due to overly broad pattern matching.

**Solution**: Refined scoring logic with contextual adjustments. Achieved 87.5% accuracy (100% on high-stakes systems).

---

## 🏆 ACCOMPLISHMENTS THAT WE'RE PROUD OF

### Technical Achievements:
- ✅ **Multi-Agent Architecture** - Successfully orchestrated 8 agents with complex state management
- ✅ **Hybrid Search** - Novel combination of vector + BM25 + RRF for legal text
- ✅ **Production Quality** - 72 unit tests, comprehensive documentation, error handling
- ✅ **High Accuracy** - 87.5% overall, 100% on critical systems
- ✅ **Fast Processing** - 30-40 seconds despite searching 1,123 chunks

### Real-World Impact:
- ✅ **Solves Actual Problem** - EU AI Act affects thousands of companies
- ✅ **Saves Time** - Days of legal review → 30 seconds
- ✅ **Saves Money** - Thousands in consulting fees → Free
- ✅ **Accessible** - Open source, well-documented, easy to use

### Development Process:
- ✅ **Built with Kiro** - Showcases AI-assisted development
- ✅ **Clean Architecture** - Modular, testable, maintainable
- ✅ **Comprehensive Docs** - README, architecture diagrams, test docs
- ✅ **Reproducible** - One-command setup, cached indexes

---

## 📚 WHAT WE LEARNED

### Technical Learnings:
1. **Multi-agent systems need careful orchestration** - State management is critical
2. **Hybrid search outperforms single methods** - Especially for legal/regulatory text
3. **Context matters in AI** - Simple pattern matching isn't enough
4. **Caching is essential** - Vector indexes must be cached for production use
5. **Testing is crucial** - Edge cases reveal scoring logic flaws

### Domain Learnings:
1. **EU AI Act is complex** - 180 recitals, 113 articles, 13 annexes
2. **Risk classification is nuanced** - Same technology, different use cases = different risks
3. **Legal AI needs explainability** - Citations and reasoning are mandatory
4. **Compliance is ongoing** - Not one-time assessment, needs monitoring

### Development Learnings:
1. **Kiro accelerates development** - AI assistance for code, tests, docs
2. **Start with architecture** - Good design prevents refactoring pain
3. **Test early and often** - Caught scoring bugs before they became problems
4. **Documentation matters** - Clear docs make projects accessible

---

## 🚀 WHAT'S NEXT FOR EU AI ACT COMPLIANCE AGENT

### Short-Term (Next Month):
- [ ] **Web UI** - User-friendly interface for non-technical users
- [ ] **PDF Export** - Generate shareable compliance reports
- [ ] **Batch Processing** - Assess multiple systems at once
- [ ] **API Deployment** - REST API for integration

### Medium-Term (3-6 Months):
- [ ] **Multi-Regulation Support** - GDPR, CCPA, other frameworks
- [ ] **Compliance Monitoring** - Continuous assessment as systems change
- [ ] **Remediation Guidance** - Step-by-step fixes for gaps
- [ ] **Fine-Tuned Embeddings** - Train on legal text for better accuracy

### Long-Term (6-12 Months):
- [ ] **Enterprise Features** - Multi-tenant, audit logs, RBAC
- [ ] **Compliance Copilot** - Chat interface for EU AI Act questions
- [ ] **Regulatory Change Tracking** - Alert when regulations update
- [ ] **Industry Benchmarking** - Compare against similar systems

### Vision:
Make EU AI Act compliance accessible to every company, regardless of size or legal budget. Democratize regulatory compliance through AI.

---

## 🔗 LINKS

- **GitHub Repository**: [your-github-url]
- **Live Demo**: [demo-url if deployed]
- **Video Demo**: [youtube/vimeo-url]
- **Documentation**: [docs-url]

---

## 🏷️ BUILT WITH

- kiro-ai
- google-adk
- gemini
- python
- faiss
- cohere
- flask
- pytest
- ai-agents
- multi-agent-systems
- eu-ai-act
- compliance
- regulatory-tech
- legal-tech

---

## 📸 SCREENSHOTS

1. **Terminal Demo** - Colored output showing agent pipeline
2. **Web UI** - Interactive assessment form and results
3. **Architecture Diagram** - Visual system overview
4. **Test Results** - 87.5% accuracy metrics
5. **Sample Report** - Compliance assessment output

---

## 🎬 VIDEO DEMO SCRIPT

See VIDEO_SCRIPT.md for detailed 2-minute demo script.

**Key Points to Cover:**
1. Problem: EU AI Act compliance is complex and expensive
2. Solution: Multi-agent system automates assessment
3. Demo: Show 3 systems (prohibited, high-risk, minimal)
4. Technical: 8 agents, hybrid search, 87.5% accuracy
5. Impact: Save time, money, make compliance accessible

---

## 💬 ELEVATOR PITCH

"The EU AI Act requires every AI system to be risk-classified. Manual assessment takes days and costs thousands. We built a multi-agent system that does it in 30 seconds with 87.5% accuracy. 8 specialized agents search 1,123 indexed chunks from the official EU AI Act using hybrid vector + keyword search. Built with Kiro AI IDE and Google ADK. Open source, production-ready, and ready to save companies weeks of legal review."

---

## 🏆 WHY WE SHOULD WIN

1. **Real-World Impact** - Solves actual problem affecting thousands of companies
2. **Technical Innovation** - Novel multi-agent architecture with hybrid search
3. **Production Quality** - 72 tests, comprehensive docs, 87.5% accuracy
4. **Kiro Showcase** - Perfect example of AI-assisted development
5. **Open Source** - Accessible to everyone, well-documented
6. **Scalable** - Can extend to other regulations and use cases

---

**Built with ❤️ and Kiro AI IDE for Kiroween 2024 🏆**
