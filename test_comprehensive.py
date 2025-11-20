#!/usr/bin/env python3
"""
Comprehensive Test Suite - Consolidated from all test files
Combines unique testing scenarios into one organized file
"""

import json
import logging
import time
from typing import Dict, Any

from src.config import Config
from src.observability import setup_logging
from src.sequential_orchestrator import ComplianceOrchestrator
from src.evaluation import AgentEvaluator, EvaluationScenario
from src.models import RiskTier
from src.tools_adk import ComplianceScoringTool


# =============================================================================
# Test 1: Direct Tool Testing
# =============================================================================

def test_tool_directly():
    """Test ComplianceScoringTool directly without the full pipeline."""
    print("\n" + "="*80)
    print("TEST 1: Direct Tool Testing")
    print("="*80)
    
    tool = ComplianceScoringTool()
    
    # Test deepfake detection system
    system_data = {
        'system_name': 'Deepfake Detection System',
        'use_case': 'Detects manipulated media and deepfakes',
        'data_types': ['media_files', 'digital_content'],
        'decision_impact': 'moderate',
        'autonomous_decision': True,
        'human_oversight': True,
        'error_consequences': 'Moderate - affects content moderation'
    }
    
    print(f"\nInput system data:")
    print(json.dumps(system_data, indent=2))
    
    result = tool.execute(json.dumps(system_data))
    result_dict = json.loads(result)
    
    print(f"\nTool Output:")
    print(f"  Score: {result_dict['score']}")
    print(f"  Classification: {result_dict['classification']}")
    
    print(f"\nExpected: LIMITED_RISK (score 35-50)")
    print(f"Actual: {result_dict['classification']} (score {result_dict['score']})")
    
    passed = 35 <= result_dict['score'] <= 50 and result_dict['classification'] == 'limited_risk'
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")
    
    return passed


# =============================================================================
# Test 2: Single Assessment (Full Pipeline)
# =============================================================================

def test_single_assessment():
    """Test single assessment through full orchestrator pipeline."""
    print("\n" + "="*80)
    print("TEST 2: Single Assessment (Full Pipeline)")
    print("="*80)
    
    orchestrator = ComplianceOrchestrator()
    
    system_info = {
        "system_name": "AutoLoan Approval System",
        "use_case": "Automated creditworthiness assessment for loan applications",
        "data_types": ["financial", "personal_data", "employment"],
        "decision_impact": "significant",
        "affected_groups": "Loan applicants",
        "autonomous_decision": True,
        "human_oversight": True,
        "error_consequences": "Severe - affects credit decisions",
    }
    
    print(f"\nTesting system: {system_info['system_name']}")
    
    try:
        result = orchestrator.assess_system(system_info)
        
        print(f"\n✅ Assessment completed successfully")
        print(f"Risk Tier: {result.get('risk_tier', 'N/A')}")
        print(f"Risk Score: {result.get('risk_score', 'N/A')}")
        
        # Expected: HIGH_RISK (credit scoring is in Annex III)
        passed = result.get('risk_tier') == 'high_risk'
        print(f"\nExpected: HIGH_RISK")
        print(f"{'✅ PASS' if passed else '❌ FAIL'}")
        
        return passed
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Test 3: Template Variables
# =============================================================================

def test_template_variables():
    """Test that template variables work correctly in the pipeline."""
    print("\n" + "="*80)
    print("TEST 3: Template Variables")
    print("="*80)
    
    orchestrator = ComplianceOrchestrator()
    
    system_info = {
        "system_name": "Test System",
        "use_case": "Testing template variables",
        "data_types": ["test_data"],
        "decision_impact": "minimal",
        "autonomous_decision": False,
        "human_oversight": True,
        "error_consequences": "Minimal",
    }
    
    print("\nTesting full pipeline with template variables...")
    
    try:
        result = orchestrator.assess_system(system_info)
        print("✅ Success! Template variables work correctly")
        return True
        
    except KeyError as e:
        print(f"❌ KeyError: {e}")
        print("Template variable not found in context")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# =============================================================================
# Test 4: Single Evaluation Scenario
# =============================================================================

def test_single_scenario():
    """Test single evaluation scenario (deepfake detection)."""
    print("\n" + "="*80)
    print("TEST 4: Single Evaluation Scenario")
    print("="*80)
    
    scenario = EvaluationScenario(
        scenario_id="s6_deepfake_detection",
        system_info={
            "system_name": "Deepfake Detection System",
            "use_case": "Detects manipulated media and deepfakes",
            "data_types": ["media_files", "digital_content"],
            "decision_impact": "moderate",
            "autonomous_decision": True,
            "human_oversight": True,
            "error_consequences": "Moderate - affects content moderation",
        },
        expected_risk_tier=RiskTier.LIMITED_RISK,
        description="Deepfake Detection"
    )
    
    print(f"\nScenario: {scenario.scenario_id}")
    print(f"Expected: {scenario.expected_risk_tier.value}")
    
    evaluator = AgentEvaluator()
    evaluator.scenarios = [scenario]
    evaluator.results = []
    
    try:
        result = evaluator.run_evaluation()
        
        print(f"\n✅ Evaluation completed")
        print(f"Passed: {result.get('passed', 0)}/1")
        print(f"Accuracy: {result.get('accuracy', 0)*100:.1f}%")
        
        return result.get('passed', 0) == 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


# =============================================================================
# Test 5: Quick Multi-Scenario Evaluation
# =============================================================================

def test_quick_evaluation(num_scenarios=2):
    """Test multiple scenarios quickly (for smoke testing)."""
    print("\n" + "="*80)
    print(f"TEST 5: Quick Evaluation ({num_scenarios} scenarios)")
    print("="*80)
    
    evaluator = AgentEvaluator()
    
    # Use just 2 diverse scenarios for quick testing
    evaluator.scenarios = [
        EvaluationScenario(
            scenario_id="s4_limited_risk_chatbot",
            system_info={
                "system_name": "Customer Support Chatbot",
                "use_case": "Automated customer service chatbot",
                "data_types": ["conversation_data"],
                "decision_impact": "minimal",
                "affected_groups": "Customer service users",
                "autonomous_decision": False,
                "human_oversight": True,
                "error_consequences": "Minor - can be escalated to human",
            },
            expected_risk_tier=RiskTier.LIMITED_RISK,
            description="Limited-risk: Chatbot transparency requirements",
        ),
        EvaluationScenario(
            scenario_id="s3_high_risk_hiring",
            system_info={
                "system_name": "Automated Recruitment System",
                "use_case": "Employment decisions through automated screening",
                "data_types": ["personal_data", "employment"],
                "decision_impact": "significant",
                "affected_groups": "Job applicants",
                "autonomous_decision": True,
                "human_oversight": False,
                "error_consequences": "Severe - affects employment opportunities",
            },
            expected_risk_tier=RiskTier.HIGH_RISK,
            description="High-risk: Employment decisions (Annex III)",
        ),
    ]
    
    print(f"\nRunning {len(evaluator.scenarios)} scenarios...")
    
    try:
        result = evaluator.run_evaluation()
        
        print(f"\n✅ Evaluation completed")
        print(f"Passed: {result['passed']}/{len(evaluator.scenarios)}")
        print(f"Accuracy: {result['accuracy']*100:.1f}%")
        
        # Show individual results
        for r in result['results']:
            if 'error' in r:
                print(f"  ❌ {r['scenario_id']}: ERROR")
            else:
                status = "✅" if r.get('correct') else "❌"
                print(f"  {status} {r['scenario_id']}: {r.get('actual', 'N/A')}")
        
        return result['passed'] == len(evaluator.scenarios)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


# =============================================================================
# Test 6: API Quota Check
# =============================================================================

def test_quota_check():
    """Quick test to verify API quota is available."""
    print("\n" + "="*80)
    print("TEST 6: API Quota Check")
    print("="*80)
    
    if not Config.GOOGLE_GENAI_API_KEY:
        print("❌ ERROR: GOOGLE_GENAI_API_KEY not set!")
        return False
    
    print(f"✅ API Key configured (ends with: ...{Config.GOOGLE_GENAI_API_KEY[-8:]})")
    
    # Test with simplest scenario
    scenario = EvaluationScenario(
        scenario_id="quota_test",
        system_info={
            "system_name": "Simple Test System",
            "use_case": "Testing API quota availability",
            "data_types": ["test_data"],
            "decision_impact": "minimal",
            "autonomous_decision": False,
            "human_oversight": True,
            "error_consequences": "Minimal",
        },
        expected_risk_tier=RiskTier.MINIMAL_RISK,
        description="Quota check test"
    )
    
    evaluator = AgentEvaluator()
    evaluator.scenarios = [scenario]
    evaluator.results = []
    
    try:
        print("\n🚀 Testing API call...")
        result = evaluator.run_evaluation()
        
        print("✅ API quota available! Test passed.")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print("⚠️  API QUOTA EXHAUSTED")
            print("   Wait until quota resets (usually next day)")
            print(f"   Error: {error_msg[:200]}...")
        else:
            print(f"❌ Unexpected error: {error_msg[:200]}...")
        
        return False


# =============================================================================
# Main Test Runner
# =============================================================================

def run_all_tests(skip_api_tests=False):
    """Run all tests and report results."""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUITE")
    print("Consolidated from all test files")
    print("="*80)
    
    results = {}
    
    # Test 1: Direct tool testing (no API calls)
    print("\n[1/6] Running tool test...")
    results['tool'] = test_tool_directly()
    
    if skip_api_tests:
        print("\n⏭️  Skipping API-dependent tests (--skip-api flag)")
        print("\n" + "="*80)
        print("TEST SUMMARY (Non-API tests only)")
        print("="*80)
        print(f"✅ Tool Test: {'PASS' if results['tool'] else 'FAIL'}")
        return results
    
    # Check API quota first
    print("\n[2/6] Checking API quota...")
    quota_ok = test_quota_check()
    results['quota'] = quota_ok
    
    if not quota_ok:
        print("\n⚠️  API quota exhausted. Skipping remaining tests.")
        print("   Run with --skip-api to test only non-API functionality")
        return results
    
    # Test 3: Template variables
    print("\n[3/6] Testing template variables...")
    results['template'] = test_template_variables()
    
    # Test 4: Single assessment
    print("\n[4/6] Testing single assessment...")
    results['single'] = test_single_assessment()
    
    # Test 5: Single scenario evaluation
    print("\n[5/6] Testing single scenario...")
    results['scenario'] = test_single_scenario()
    
    # Test 6: Quick multi-scenario
    print("\n[6/6] Testing quick evaluation...")
    results['quick_eval'] = test_quick_evaluation()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Setup logging
    setup_logging("INFO")
    
    # Check for flags
    skip_api = "--skip-api" in sys.argv or "-s" in sys.argv
    
    # Run tests
    results = run_all_tests(skip_api_tests=skip_api)
    
    # Exit with appropriate code
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)
