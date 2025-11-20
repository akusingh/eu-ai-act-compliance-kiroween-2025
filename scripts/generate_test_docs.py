#!/usr/bin/env python3
"""Generate JSON documentation for all test modules."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tests"))

from test_utils import generate_test_documentation, save_test_documentation


def main():
    """Generate documentation for all test modules."""
    
    print("\n" + "="*60)
    print("GENERATING TEST DOCUMENTATION")
    print("="*60 + "\n")
    
    # Test Models
    print("📄 Generating test_models documentation...")
    from test_models import (
        TestRiskTierEnum,
        TestAISystemProfile,
        TestComplianceAssessment,
        TestModelSerialization
    )
    
    docs_models = generate_test_documentation(
        "tests/test_models.py",
        [TestRiskTierEnum, TestAISystemProfile, TestComplianceAssessment, TestModelSerialization]
    )
    json_path_models = save_test_documentation(docs_models)
    print(f"   ✅ {json_path_models}")
    print(f"   📊 {docs_models['total_test_cases']} test cases in {docs_models['total_test_classes']} classes\n")
    
    # Test Tools
    print("📄 Generating test_tools documentation...")
    try:
        from test_tools import (
            TestComplianceScoringTool,
            TestEUAIActReferenceTool
        )
        
        docs_tools = generate_test_documentation(
            "tests/test_tools.py",
            [TestComplianceScoringTool, TestEUAIActReferenceTool]
        )
        json_path_tools = save_test_documentation(docs_tools)
        print(f"   ✅ {json_path_tools}")
        print(f"   📊 {docs_tools['total_test_cases']} test cases in {docs_tools['total_test_classes']} classes\n")
    except ImportError as e:
        print(f"   ⚠️  Skipped (import error): {e}\n")
    
    # Test Vector Index
    print("📄 Generating test_vector_index documentation...")
    try:
        from test_vector_index import (
            TestVectorIndexTool,
            TestVectorIndexCaching,
            TestVectorSearchIntegration
        )
        
        docs_vector = generate_test_documentation(
            "tests/test_vector_index.py",
            [TestVectorIndexTool, TestVectorIndexCaching, TestVectorSearchIntegration]
        )
        json_path_vector = save_test_documentation(docs_vector)
        print(f"   ✅ {json_path_vector}")
        print(f"   📊 {docs_vector['total_test_cases']} test cases in {docs_vector['total_test_classes']} classes\n")
    except ImportError as e:
        print(f"   ⚠️  Skipped (import error): {e}\n")
    
    # Test Evaluation
    print("📄 Generating test_evaluation documentation...")
    try:
        from test_evaluation import (
            TestEvaluationScenario,
            TestAgentEvaluator,
            TestEvaluationMetrics,
            TestScenarioExecution
        )
        
        docs_eval = generate_test_documentation(
            "tests/test_evaluation.py",
            [TestEvaluationScenario, TestAgentEvaluator, TestEvaluationMetrics, TestScenarioExecution]
        )
        json_path_eval = save_test_documentation(docs_eval)
        print(f"   ✅ {json_path_eval}")
        print(f"   📊 {docs_eval['total_test_cases']} test cases in {docs_eval['total_test_classes']} classes\n")
    except ImportError as e:
        print(f"   ⚠️  Skipped (import error): {e}\n")
    
    # Summary
    print("="*60)
    print("✅ TEST DOCUMENTATION GENERATION COMPLETE")
    print("="*60)
    print(f"\nDocumentation files saved in: tests/docs/")
    print("\nTo view:")
    print("  cat tests/docs/test_models_documentation.json | python -m json.tool")
    print("\n")


if __name__ == "__main__":
    main()
