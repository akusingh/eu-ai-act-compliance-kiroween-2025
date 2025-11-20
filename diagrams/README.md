# EU AI Act Compliance Agent - Architecture Diagrams

This directory contains 8 comprehensive Graphviz (`.dot`) diagrams visualizing different aspects of the system architecture.

## 📊 Diagram Overview

### 1. System Architecture (`01_system_architecture.dot`)
**High-level system overview**
- Shows 5-agent sequential pipeline
- Vector indexes and knowledge base
- Hybrid search architecture
- Data flow from input to output

**Use in demo:** Introduction and system overview segment

---

### 2. Agent Flow (`02_agent_flow.dot`)
**Detailed agent pipeline**
- 5 sequential agents with sub-agents
- State transitions between agents
- Data transformations
- Processing time estimates

**Use in demo:** Code walkthrough - agent orchestration

---

### 3. Hybrid Search (`03_hybrid_search.dot`)
**Search architecture deep dive**
- Vector search (Gemini embeddings + FAISS)
- BM25 keyword search
- RRF fusion algorithm
- Optional Cohere reranking

**Use in demo:** Technical explanation of search capabilities

---

### 4. Risk Classification (`04_risk_classification.dot`)
**Scoring and classification logic**
- Base score calculation (weighted factors)
- Contextual adjustments
- Risk tier assignment rules
- Confidence calculation

**Use in demo:** How the system determines risk levels

---

### 5. Testing Framework (`05_testing_framework.dot`)
**Test suite structure**
- 72 unit tests across 4 modules
- 8 evaluation scenarios
- Test results (5/8 passing)
- JSON artifact generation

**Use in demo:** Quality assurance and validation segment

---

### 6. Data Flow (`06_data_flow.dot`)
**End-to-end data journey**
- Input validation
- Parallel research phase
- Legal processing
- Classification and analysis
- Report generation

**Use in demo:** Technical deep dive showing data transformations

---

### 7. Project Structure (`07_project_structure.dot`)
**File organization**
- Directory structure
- Key files in each module
- Documentation hierarchy
- Build artifacts

**Use in demo:** Code walkthrough - project organization

---

### 8. Cohere Reranking (`08_cohere_reranking.dot`)
**Optional performance enhancement**
- With vs without reranking comparison
- Performance metrics (+7.5% accuracy)
- Cost-benefit analysis
- Implementation details

**Use in demo:** Advanced features and optimizations

---

## 🎨 Rendering Diagrams

### Install Graphviz (macOS)
```bash
brew install graphviz
```

### Render Single Diagram
```bash
dot -Tpng 01_system_architecture.dot -o 01_system_architecture.png
```

### Render All Diagrams (Batch)
```bash
for file in *.dot; do
    dot -Tpng "$file" -o "${file%.dot}.png"
done
```

### Render to Different Formats
```bash
# SVG (scalable, best for web)
dot -Tsvg 01_system_architecture.dot -o 01_system_architecture.svg

# PDF (best for documents)
dot -Tpdf 01_system_architecture.dot -o 01_system_architecture.pdf

# High-res PNG (for presentations)
dot -Tpng -Gdpi=300 01_system_architecture.dot -o 01_system_architecture_hires.png
```

---

## 📹 Using in Demo Video

### Recommended Workflow

1. **Render all diagrams first**
   ```bash
   cd diagrams
   ./render_all.sh  # or use batch command above
   ```

2. **Open in image viewer for recording**
   ```bash
   open *.png
   ```

3. **Screen record while explaining**
   - Use QuickTime Player → File → New Screen Recording
   - Zoom into relevant sections
   - Annotate with cursor or markup tools

### Suggested Video Segments

**Segment 1: Introduction (30s)**
- Show `01_system_architecture.png`
- Explain overall approach

**Segment 2: Architecture Overview (60s)**
- Show `01_system_architecture.png` (detailed)
- Show `02_agent_flow.png` (agent pipeline)
- Show `03_hybrid_search.png` (search capabilities)

**Segment 3: Code Walkthrough (60s)**
- Show `07_project_structure.png`
- Show `06_data_flow.png`
- Reference actual code files

**Segment 4: Classification Logic (30s)**
- Show `04_risk_classification.png`
- Explain scoring methodology

**Segment 5: Testing & Results (30s)**
- Show `05_testing_framework.png`
- Reference test results

**Segment 6: Advanced Features (optional, 20s)**
- Show `08_cohere_reranking.png`
- Explain performance gains

---

## 🎯 Diagram Statistics

| Diagram | Nodes | Edges | Complexity | Render Time |
|---------|-------|-------|------------|-------------|
| 01_system_architecture | 22 | 18 | Medium | ~1s |
| 02_agent_flow | 18 | 15 | Medium | ~1s |
| 03_hybrid_search | 20 | 16 | High | ~1s |
| 04_risk_classification | 24 | 20 | High | ~1s |
| 05_testing_framework | 26 | 22 | High | ~1s |
| 06_data_flow | 28 | 24 | High | ~2s |
| 07_project_structure | 15 | 12 | Medium | ~1s |
| 08_cohere_reranking | 20 | 16 | Medium | ~1s |

**Total render time:** ~10 seconds for all diagrams

---

## 🔧 Customization

### Color Schemes
Diagrams use consistent color coding:
- **Lightblue**: Core components
- **Lightgreen**: Success/output
- **Orange**: Decisions/scoring
- **Lavender**: Optional/enhanced features
- **Wheat**: Data/state
- **Pink/Red**: High-risk/prohibited
- **Yellow**: Medium-risk/warnings

### Editing Diagrams
1. Open `.dot` file in text editor
2. Modify node labels, colors, or structure
3. Re-render to see changes
4. Graphviz syntax: https://graphviz.org/doc/info/lang.html

### Common Modifications
```dot
// Change node color
node [fillcolor=lightblue];

// Change arrow style
edge [style=dashed, color=red];

// Add annotation
note [label="Important note", shape=note, fillcolor=yellow];

// Change layout direction
rankdir=LR;  // Left-to-right (default is TB = top-to-bottom)
```

---

## 📚 Resources

- **Graphviz Documentation:** https://graphviz.org/documentation/
- **DOT Language Guide:** https://graphviz.org/doc/info/lang.html
- **Node Shapes:** https://graphviz.org/doc/info/shapes.html
- **Color Names:** https://graphviz.org/doc/info/colors.html
- **Online Editor:** https://dreampuf.github.io/GraphvizOnline/

---

## ✅ Checklist for Demo Video

- [ ] Install Graphviz (`brew install graphviz`)
- [ ] Render all 8 diagrams to PNG
- [ ] Review each diagram for accuracy
- [ ] Prepare talking points for each diagram
- [ ] Practice screen recording workflow
- [ ] Set up image viewer for easy navigation
- [ ] Test zoom and annotation tools
- [ ] Record practice segment
- [ ] Review and refine

---

## 🎬 Final Notes

These diagrams provide professional, comprehensive visualizations that will significantly enhance your demo video. They show:

✅ **Technical depth** - Multi-agent architecture, hybrid search, risk scoring  
✅ **Systematic approach** - Clear data flow, well-tested, documented  
✅ **Production quality** - Professional diagrams, not just code  
✅ **Completeness** - All aspects covered (arch, code, tests, results)

Judges will appreciate the visual clarity and thorough documentation!
