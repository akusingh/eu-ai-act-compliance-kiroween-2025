#!/usr/bin/env python3
"""Demo script showing the EU AI Act Compliance Agent in action."""

import json
import logging
from pathlib import Path

from src.config import Config
from src.observability import setup_logging, metrics_collector, trace_collector

# ADK-based orchestrator with SequentialAgent
from src.sequential_orchestrator import ComplianceOrchestrator


# Setup logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


def demo_basic_assessment():
    """Demo basic compliance assessment workflow using ADK agents."""
    print("\n" + "="*70)
    print("EU AI Act Compliance Agent - ADK Demo")
    print("Framework: Google ADK SequentialAgent + Parallel Research")
    print("Model: Gemini 2.0 Flash")
    print("Features: 3-source parallel search, reranking, agent-to-agent")
    print("="*70)
    
    # Test case 1: High-risk system
    print("\n--- Test Case 1: Loan Approval System ---")
    orchestrator = ComplianceOrchestrator()  # Create new orchestrator for each test
    system_info_1 = {
        "system_name": "AutoLoan Approval System",
        "use_case": "Automated creditworthiness assessment for loan applications",
        "data_types": ["financial", "personal_data", "employment"],
        "decision_impact": "significant",
        "affected_groups": "Loan applicants",
        "autonomous_decision": True,
        "human_oversight": True,
        "error_consequences": "Severe - affects credit decisions",
    }
    
    try:
        result_1 = orchestrator.assess_system(system_info_1)
        assessment = result_1['assessment']
        report = result_1['report']
        
        # Extract risk classification
        tier = assessment.get('tier', 'unknown')
        score = assessment.get('score', 'N/A')
        confidence = assessment.get('confidence', 0)
        articles = assessment.get('articles', [])
        
        print(f"\n✅ Risk Classification: {tier}")
        print(f"📊 Risk Score: {score}/100")
        print(f"🎯 Confidence: {confidence:.2f}")
        print(f"\n📜 Relevant Articles:")
        for article in articles[:5]:  # Show top 5
            print(f"  - {article}")
        
        # Show compliance gaps
        if 'compliance_gaps' in report:
            print(f"\n⚠️  Compliance Gaps ({len(report['compliance_gaps'])})'):")
            for gap in report['compliance_gaps'][:3]:  # Show top 3
                print(f"  - {gap}")
        
        # Show top recommendations
        if 'recommendations' in report:
            print(f"\n💡 Key Recommendations:")
            for rec in report['recommendations'][:2]:  # Show top 2
                print(f"  - {rec}")
    except Exception as e:
        logger.error(f"Assessment failed: {e}", exc_info=True)
        print(f"Error: {e}")
    
    # Test case 2: Minimal risk system
    print("\n--- Test Case 2: Music Recommendation System ---")
    orchestrator2 = ComplianceOrchestrator()  # Create new orchestrator to avoid event loop issues
    system_info_2 = {
        "system_name": "Spotify Recommendation Engine",
        "use_case": "Personalized music recommendations based on listening history",
        "data_types": ["user_behavior"],
        "decision_impact": "minimal",
        "affected_groups": "Music listeners",
        "autonomous_decision": False,
        "human_oversight": False,
        "error_consequences": "Minor - user sees different recommendations",
    }
    
    try:
        result_2 = orchestrator2.assess_system(system_info_2)
        assessment = result_2['assessment']
        
        risk_tier = assessment.get('risk_tier', 'unknown')
        if hasattr(risk_tier, 'value'):
            risk_tier = risk_tier.value
            
        print(f"Risk Classification: {risk_tier}")
        print(f"Risk Score: {assessment.get('risk_score', 'N/A')}/100")
        print(f"Confidence: {assessment.get('confidence', assessment.get('confidence_score', 0)):.2f}")
    except Exception as e:
        logger.error(f"Assessment failed: {e}", exc_info=True)
        print(f"Error: {e}")




def demo_observability():
    """Demo observability features."""
    print("\n" + "="*70)
    print("Observability Demo")
    print("="*70)
    
    # Run a quick assessment to generate traces and metrics
    orchestrator = ComplianceOrchestrator()
    system_info = {
        "system_name": "ChatBot Support System",
        "use_case": "Customer support chatbot",
        "data_types": ["conversation_data"],
        "decision_impact": "minimal",
        "affected_groups": "Customers",
        "autonomous_decision": False,
        "human_oversight": False,
        "error_consequences": "Minimal - users can escalate to human agent",
    }
    
    try:
        result = orchestrator.assess_system(system_info)
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
    
    # Show traces
    print("\nExecution Traces:")
    traces = trace_collector.get_traces()
    for trace in traces[-3:]:  # Last 3 traces
        print(f"  {trace['agent']} - {trace['action']}: {trace['status']}")
    
    # Show metrics
    print("\nMetrics Collected:")
    metrics = metrics_collector.get_summary()
    print(f"  Total Metrics: {metrics['total_metrics']}")
    for metric in metrics['metrics'][-3:]:
        print(f"  {metric['metric_name']}: {metric['value']}")


def save_outputs():
    """Save observability data to files."""
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Save traces
    trace_file = output_dir / "traces.json"
    trace_collector.save_traces(str(trace_file))
    print(f"\nTraces saved to {trace_file}")
    
    # Save metrics
    metrics_file = output_dir / "metrics.json"
    metrics_collector.save_metrics(str(metrics_file))
    print(f"Metrics saved to {metrics_file}")


if __name__ == "__main__":
    logger.info("Starting EU AI Act Compliance Agent Demo (ADK version)")
    
    # Validate Gemini API key (required for ADK)
    if not Config.GOOGLE_GENAI_API_KEY:
        logger.error("GOOGLE_GENAI_API_KEY not set!")
        print("\n⚠️  ERROR: GOOGLE_GENAI_API_KEY not configured in .env")
        print("ADK requires Gemini API key to function.")
        print("Get one at: https://aistudio.google.com/\n")
        exit(1)
    
    logger.info(f"Using ADK framework with Gemini 2.0 Flash")
    
    # Run demos
    demo_basic_assessment()
    # demo_observability()  # Optional: enable after basic test works
    # save_outputs()        # Optional: enable after basic test works
    
    print("\n" + "="*70)
    print("ADK Demo completed successfully!")
    print("Framework: Google ADK with Gemini 2.0 Flash")
    print("Check 'outputs/' directory for generated traces and metrics")
    print("="*70 + "\n")
