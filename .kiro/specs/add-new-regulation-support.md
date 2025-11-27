# Spec: Add Support for Additional Regulations

## Overview
Extend the compliance agent to support multiple regulatory frameworks beyond EU AI Act (e.g., GDPR, CCPA, UK AI Regulation).

## Requirements

### Functional Requirements
1. Support multiple regulation frameworks simultaneously
2. Allow users to select which regulations to check against
3. Provide cross-regulation compliance analysis
4. Generate unified compliance reports

### Technical Requirements
1. Modular regulation loader system
2. Separate vector indexes per regulation
3. Regulation-specific scoring logic
4. Unified agent interface

## Design

### Data Model Changes

```python
class RegulationFramework(str, Enum):
    EU_AI_ACT = "eu_ai_act"
    GDPR = "gdpr"
    CCPA = "ccpa"
    UK_AI_REGULATION = "uk_ai_regulation"

class MultiRegulationAssessment(BaseModel):
    system_name: str
    regulations_checked: List[RegulationFramework]
    assessments: Dict[RegulationFramework, ComplianceAssessment]
    cross_regulation_conflicts: List[str]
    unified_recommendations: List[str]
```

### Architecture Changes

1. **RegulationLoader** - Abstract base class for loading regulation text
2. **MultiRegulationOrchestrator** - Coordinates assessments across regulations
3. **ConflictAnalyzer** - Identifies conflicting requirements
4. **UnifiedReportGenerator** - Combines results

### File Structure

```
src/
├── regulations/
│   ├── base.py              # Abstract regulation loader
│   ├── eu_ai_act.py         # EU AI Act implementation
│   ├── gdpr.py              # GDPR implementation
│   └── ccpa.py              # CCPA implementation
├── multi_regulation_orchestrator.py
└── conflict_analyzer.py

data/
├── eu_ai_act/               # Existing
├── gdpr/                    # New
│   ├── gdpr_articles.txt
│   └── embeddings_cache/
└── ccpa/                    # New
    ├── ccpa_text.txt
    └── embeddings_cache/
```

## Implementation Tasks

### Phase 1: Foundation
- [ ] Create `RegulationLoader` abstract base class
- [ ] Refactor existing EU AI Act code to use new structure
- [ ] Add `RegulationFramework` enum to models
- [ ] Update tests for new structure

### Phase 2: GDPR Support
- [ ] Download GDPR official text
- [ ] Create GDPR-specific scoring logic
- [ ] Build GDPR vector indexes
- [ ] Add GDPR evaluation scenarios
- [ ] Test GDPR assessments

### Phase 3: Multi-Regulation
- [ ] Create `MultiRegulationOrchestrator`
- [ ] Implement parallel regulation checking
- [ ] Build conflict analyzer
- [ ] Create unified report generator
- [ ] Add cross-regulation tests

### Phase 4: UI Updates
- [ ] Update web UI to support regulation selection
- [ ] Add multi-regulation comparison view
- [ ] Show cross-regulation conflicts
- [ ] Export multi-regulation reports

## Testing Strategy

### Unit Tests
- Test each regulation loader independently
- Test conflict detection logic
- Test unified report generation

### Integration Tests
- Test multi-regulation orchestration
- Test with all regulation combinations
- Test conflict resolution

### Evaluation Scenarios
- Systems that comply with one but not another
- Systems with conflicting requirements
- Systems that comply with all

## Success Criteria

1. Support at least 3 regulations (EU AI Act, GDPR, CCPA)
2. Maintain ≥85% accuracy per regulation
3. Correctly identify cross-regulation conflicts
4. Processing time <60 seconds for 3 regulations
5. Comprehensive test coverage (≥90%)

## Future Enhancements

- Add more regulations (UK, Canada, Australia)
- Implement regulation change tracking
- Add compliance timeline planning
- Support custom/internal regulations

## References

- #[[file:src/models.py]] - Current data models
- #[[file:src/sequential_orchestrator.py]] - Current orchestrator
- #[[file:src/vector_index_tool.py]] - Vector search implementation

---

**This spec can be used with Kiro's spec feature to guide implementation of multi-regulation support.**
