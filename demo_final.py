#!/usr/bin/env python3
"""Final demo showcasing the complete ADK-based EU AI Act Compliance Agent."""

import logging
from src.config import Config
from src.observability import setup_logging
from src.evaluation import AgentEvaluator, EvaluationScenario
from src.models import RiskTier

# Setup logging to show architecture
setup_logging("INFO")
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("EU AI ACT COMPLIANCE AGENT - GOOGLE ADK IMPLEMENTATION")
print("="*80)
print("Framework: Google Agent Development Kit (ADK)")
print("Model: Gemini 2.0 Flash")
print("Features: Multi-agent pipeline, Parallel research, Hybrid search")
print("="*80 + "\n")

# Validate API key
if not Config.GOOGLE_GENAI_API_KEY:
    print("⚠️  ERROR: GOOGLE_GENAI_API_KEY not configured in .env")
    print("Get one at: https://aistudio.google.com/\n")
    exit(1)

# Create evaluator (which creates the orchestrator)
evaluator = AgentEvaluator()

# Test case: High-risk loan approval system
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

print("\nINPUT: Assessing loan approval system...")
print("-" * 80)
print(f"System: {system_info['system_name']}")
print(f"Use Case: {system_info['use_case']}")
print(f"Data Types: {', '.join(system_info['data_types'])}")
print(f"Decision Impact: {system_info['decision_impact']}")
print(f"Human Oversight: {system_info['human_oversight']}")
print("-" * 80)

try:
    # Run assessment using the same method as evaluate.py
    result = evaluator.orchestrator.assess_system(system_info)
    
    # Extract results (handle both 'tier' and 'risk_tier' keys)
    assessment = result.get('assessment', {})
    report = result.get('report', {})
    
    # Get tier (try both keys for compatibility)
    tier = assessment.get('tier') or assessment.get('risk_tier', 'N/A')
    score = assessment.get('score', 0)
    confidence = assessment.get('confidence', 0)
    articles = assessment.get('articles', [])
    
    # Display results
    print("\n" + "="*80)
    print("ASSESSMENT RESULTS")
    print("="*80)
    
    print(f"\nRisk Classification: {tier.upper()}")
    print(f"Risk Score: {score}/100")
    print(f"Confidence: {confidence:.2%}")
    
    print(f"\nRelevant EU AI Act Articles:")
    for i, article in enumerate(articles[:5], 1):
        print(f"   {i}. {article}")
    
    # Extract compliance gaps and recommendations from report
    if isinstance(report, dict):
        gaps = report.get('compliance_gaps', [])
        if gaps:
            print(f"\nCompliance Gaps Identified ({len(gaps)}):")
            for i, gap in enumerate(gaps[:3], 1):
                print(f"   {i}. {gap}")
        
        recs = report.get('recommendations', [])
        if recs:
            print(f"\nKey Recommendations:")
            for i, rec in enumerate(recs[:3], 1):
                print(f"   {i}. {rec}")
    
    print("\n" + "="*80)
    print("ASSESSMENT COMPLETE - Full report generated")
    print("="*80 + "\n")
    
    print("Architecture Metrics:")
    print(f"   * Total Agents: 5 (sequential + parallel sub-team)")
    print(f"   * Vector Indexes: 3 sources (1,123 total chunks)")
    print(f"   * Search Method: Hybrid (Vector + BM25 + RRF)")
    print(f"   * Processing Time: ~30-40 seconds")
    
    # Verify expected result
    print("\n" + "="*80)
    print("VALIDATION")
    print("="*80)
    expected_tier = "high_risk"
    actual_tier = tier.lower().replace(" ", "_").replace("-", "_")
    
    if actual_tier == expected_tier:
        print(f"✅ PASS: Correctly classified as {expected_tier.upper()}")
        print("   (Loan approval systems are in Annex III high-risk list)")
    else:
        print(f"⚠️  UNEXPECTED: Got {actual_tier}, expected {expected_tier}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*80)
print("Demo Complete!")
print("="*80 + "\n")
