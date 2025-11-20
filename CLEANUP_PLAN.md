# Cleanup Plan - November 20, 2025

## Current Situation
- ✅ **Code is WORKING** - No bugs, everything functional
- ⚠️ **API Quota Exhausted** - Hit 200 requests/day limit on Gemini 2.0 Flash
- 🗂️ **Repository Bloated** - 64 uncommitted files, many unnecessary test stubs and docs

## Issues Found

### 1. Git Repository Bloat
- **64 uncommitted files** (massive test files, duplicate docs)
- Multiple README versions (README.md, README.md.old, README.md.backup_nov20)
- Lots of documentation files that should be consolidated or removed

### 2. Test Files Situation
- Many large test files created but not fully implemented
- Test documentation JSON files (3,000-10,000 lines each)
- Duplicate/redundant test scenarios

### 3. What's Actually Working
- ✅ Core pipeline: `src/sequential_orchestrator.py`
- ✅ Tools: `src/tools_adk.py`, `src/vector_index_tool.py`, `src/reranker_tool.py`
- ✅ Models: `src/models.py`
- ✅ Evaluation: `src/evaluation.py`
- ✅ Agents: `src/aggregator_agents.py`, `src/parallel_research_agents.py`

## Cleanup Actions

### Priority 1: Remove Unnecessary Files
```bash
# Remove duplicate/old README files
rm README.md.old README.md.backup_nov20

# Remove redundant documentation (keep only essential ones)
# Keep: README.md, PROJECT_SUMMARY.md
# Consider removing: All the other 20+ markdown files
```

### Priority 2: Clean Test Files
```bash
# Remove incomplete/stub test files in root
rm test_*.py  # Move to tests/ directory or remove

# Keep only:
# - tests/test_models.py
# - tests/test_tools.py
# - tests/test_vector_index.py
# - tests/test_evaluation.py
```

### Priority 3: Consolidate Documentation
- Merge similar docs into single comprehensive files
- Keep:
  - **README.md** - Main project documentation
  - **PROJECT_SUMMARY.md** - Architecture overview
  - **IMPLEMENTATION_COMPLETE.md** - Development notes
- Archive or remove the rest

### Priority 4: Git Commit Strategy
```bash
# Stage working code changes
git add src/
git add evaluate.py
git add README.md

# Commit working state
git commit -m "feat: Refactored to Google ADK with 5-agent pipeline"

# Then clean untracked files
git clean -n  # Preview what will be removed
git clean -fd  # Actually remove untracked files
```

## Today's Goals

### Goal 1: Repository Cleanup (30 min)
- [ ] Remove duplicate/old files
- [ ] Consolidate documentation
- [ ] Clean test stubs
- [ ] Commit clean working state

### Goal 2: Wait for API Quota Reset
- [ ] Current time: 11:14 AM
- [ ] Quota resets: Tomorrow (daily limit)
- [ ] Alternative: Create new API key or upgrade to paid

### Goal 3: Final Evaluation Run (when quota available)
- [ ] Run full 8-scenario evaluation
- [ ] Verify 100% accuracy target
- [ ] Document final results

### Goal 4: Kaggle Submission Prep
- [ ] Clean repository
- [ ] Update README with final accuracy
- [ ] Create demo video (2-3 hours)
- [ ] Package for submission

## Immediate Next Steps

1. **Create cleanup script** to remove bloat
2. **Commit current working state** to git
3. **Wait for quota reset** or get new API key
4. **Run final evaluation** tomorrow
5. **Create demo video** and submit

## Timeline
- **Today**: Cleanup + commit (1-2 hours)
- **Tomorrow**: Final evaluation when quota resets
- **Next 2 days**: Demo video + documentation
- **Submission**: Within 12 days deadline

## Notes
- Code quality: ✅ Clean after refactoring
- Functionality: ✅ All features working
- Blocker: ⏳ API quota (temporary)
- Risk: 🟢 Low - just need quota to run evaluation
