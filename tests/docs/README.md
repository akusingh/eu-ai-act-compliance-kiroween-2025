# Test Documentation

This directory contains automatically generated JSON documentation for all test modules in the test suite.

## Generated Documentation Files

### 📋 Master Index
- **`test_suite_index.json`** - Complete overview of all 72 test cases across 4 modules

### 📄 Individual Test Module Documentation

1. **`test_models_documentation.json`** (21 tests)
   - Tests for Pydantic models: RiskTier enum, AISystemProfile, ComplianceAssessment
   - Status: ✅ 21/21 PASSING
   - Coverage: Model validation, serialization, enum handling

2. **`test_tools_documentation.json`** (18 tests)
   - Tests for ComplianceScoringTool and EUAIActReferenceTool
   - Status: ⏳ Pending verification
   - Coverage: Risk scoring, pattern matching, article extraction

3. **`test_vector_index_documentation.json`** (20 tests)
   - Tests for VectorIndexTool and search functionality
   - Status: ⏳ Pending verification  
   - Coverage: Vector search, caching, integration tests

4. **`test_evaluation_documentation.json`** (13 tests)
   - Tests for evaluation framework and metrics
   - Status: ⏳ Pending verification
   - Coverage: Scenarios, evaluator, metrics, async execution

## JSON Structure

Each test module documentation file contains:

```json
{
  "test_module": "module_name",
  "file_path": "path/to/test_file.py",
  "generated_at": "ISO timestamp",
  "total_test_classes": N,
  "total_test_cases": M,
  "test_classes": [
    {
      "class_name": "TestClassName",
      "description": "Test suite description",
      "test_case_count": X,
      "test_cases": [
        {
          "test_name": "test_function_name",
          "description": "What this test validates",
          "test_type": "unit|integration",
          "markers": ["asyncio", "integration", "slow"]
        }
      ]
    }
  ]
}
```

## Viewing Documentation

### View formatted JSON:
```bash
# View specific module documentation
cat tests/docs/test_models_documentation.json | python -m json.tool

# View master index
cat tests/docs/test_suite_index.json | python -m json.tool | less
```

### Extract specific information:
```bash
# Count total tests per module
jq '.total_test_cases' tests/docs/*.json

# List all test class names
jq '.test_classes[].class_name' tests/docs/test_models_documentation.json

# Get test descriptions
jq '.test_classes[].test_cases[] | {name: .test_name, desc: .description}' \
  tests/docs/test_models_documentation.json
```

## Regenerating Documentation

Documentation is automatically generated when running test modules directly:

```bash
# Generate all documentation at once
python scripts/generate_test_docs.py

# Or run individual test files (also generates docs)
python tests/test_models.py
python tests/test_tools.py
python tests/test_vector_index.py
python tests/test_evaluation.py
```

## Test Statistics

- **Total Test Modules**: 4
- **Total Test Classes**: 13
- **Total Test Cases**: 72
  - Unit tests: 66
  - Integration tests: 6
  - Async tests: 3

## Key Test Coverage

### Risk Score Validation
- Prohibited: 85-100
- High Risk: 55-84
- Limited Risk: 25-54
- Minimal Risk: 0-24

### Components Tested
- ✅ Pydantic models and enums
- ⏳ Compliance scoring tool
- ⏳ EU AI Act reference tool
- ⏳ Vector index search
- ⏳ Evaluation framework
- ⏳ Metrics calculation

## Notes

- Documentation is generated from test docstrings
- Test markers are automatically detected (@pytest.mark.integration, etc.)
- Timestamps show when documentation was last generated
- Status indicators: ✅ (passing), ⏳ (pending), ❌ (failing)
