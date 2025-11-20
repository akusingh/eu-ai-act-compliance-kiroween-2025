#!/usr/bin/env python3
"""Final demo showcasing the complete ADK-based EU AI Act Compliance Agent."""

import logging
from src.config import Config
from src.observability import setup_logging
from src.sequential_orchestrator import ComplianceOrchestrator

# Setup logging to show architecture
setup_logging("INFO")
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("EU AI ACT COMPLIANCE AGENT - GOOGLE ADK IMPLEMENTATION")
print("="*80)
print("Framework: Google Agent Development Kit (ADK)")
print("Model: Gemini 2.0 Flash")
print("Features: Multi-agent pipeline, Parallel research, Hybrid search, Reranking")
print("="*80 + "\n")

# Create orchestrator (logs architecture automatically)
orchestrator = ComplianceOrchestrator()

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

try:
    # Run assessment (logs full pipeline execution)
    result = orchestrator.assess_system(system_info)
    
    # Extract results
    assessment = result['assessment']
    report = result['report']
    
    # Display results
    print("\n" + "="*80)
    print("ASSESSMENT RESULTS")
    print("="*80)
    
    print(f"\nRisk Classification: {assessment.get('tier', 'N/A')}")
    print(f"Risk Score: {assessment.get('score', 'N/A')}/100")
    print(f"Confidence: {assessment.get('confidence', 0):.2%}")
    
    print(f"\nRelevant EU AI Act Articles:")
    for i, article in enumerate(assessment.get('articles', [])[:5], 1):
        print(f"   {i}. {article}")
    
    if 'compliance_gaps' in report:
        print(f"\nCompliance Gaps Identified ({len(report['compliance_gaps'])}):")
        for i, gap in enumerate(report['compliance_gaps'][:3], 1):
            print(f"   {i}. {gap}")
    
    if 'recommendations' in report:
        print(f"\nKey Recommendations:")
        for i, rec in enumerate(report['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
    
    print("\n" + "="*80)
    print("ASSESSMENT COMPLETE - Full report generated")
    print("="*80 + "\n")
    
    print("Architecture Metrics:")
    print(f"   * Total Agents: 5 (sequential + parallel sub-team)")
    print(f"   * Vector Indexes: 3 sources (1,123 total chunks)")
    print(f"   * Search Method: Hybrid (Vector + BM25 + RRF)")
    print(f"   * Reranking: Cross-source synthesis")
    print(f"   * Processing Time: ~30-40 seconds")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("Demo Complete!")
print("="*80 + "\n")
