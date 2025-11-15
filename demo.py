#!/usr/bin/env python3
"""Demo script showing the EU AI Act Compliance Agent in action."""

import json
import logging
from pathlib import Path

from src.config import Config
from src.observability import setup_logging, metrics_collector, trace_collector
from src.orchestrator import ComplianceOrchestrator
from src.sessions import SessionManager, ConversationMemory
from src.tools import GoogleSearchTool, ComplianceScoringTool, EUAIActReferenceTool


# Setup logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


def demo_basic_assessment():
    """Demo basic compliance assessment workflow."""
    print("\n" + "="*70)
    print("EU AI Act Compliance Agent - Demo")
    print("="*70)
    
    # Initialize orchestrator
    orchestrator = ComplianceOrchestrator()
    
    # Test case 1: High-risk system
    print("\n--- Test Case 1: Loan Approval System ---")
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
        print(f"Risk Classification: {result_1['assessment']['risk_tier']}")
        print(f"Risk Score: {result_1['assessment']['risk_score']}/100")
        print(f"Confidence: {result_1['assessment']['confidence_score']:.2f}")
        print("Relevant Articles:")
        for article in result_1['assessment']['relevant_articles']:
            print(f"  - {article}")
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
    
    # Test case 2: Minimal risk system
    print("\n--- Test Case 2: Music Recommendation System ---")
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
        result_2 = orchestrator.assess_system(system_info_2)
        print(f"Risk Classification: {result_2['assessment']['risk_tier']}")
        print(f"Risk Score: {result_2['assessment']['risk_score']}/100")
        print(f"Confidence: {result_2['assessment']['confidence_score']:.2f}")
    except Exception as e:
        logger.error(f"Assessment failed: {e}")


def demo_sessions_and_memory():
    """Demo session management and multi-turn conversation."""
    print("\n" + "="*70)
    print("Session Management & Memory Demo")
    print("="*70)
    
    session_manager = SessionManager(timeout_seconds=3600)
    
    # Create session
    session = session_manager.create_session()
    print(f"\nSession created: {session.session_id}")
    
    # Add messages to conversation
    memory = ConversationMemory(session)
    memory.add_exchange(
        "I'm building a facial recognition system for access control",
        "That's a high-risk system. Let me assess it against EU AI Act requirements."
    )
    
    # Show context
    print("\nConversation Context:")
    print(memory.get_context_for_agent())
    
    # Show memory summary
    print("\nMemory Summary:")
    print(json.dumps(memory.get_memory_summary(), indent=2))


def demo_tools():
    """Demo available tools."""
    print("\n" + "="*70)
    print("Tools Demo")
    print("="*70)
    
    # Google Search Tool
    print("\n--- Google Search Tool ---")
    search_tool = GoogleSearchTool()
    results = search_tool.search("high-risk AI applications", num_results=2)
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['snippet'][:80]}...")
    
    # EU AI Act Reference Tool
    print("\n--- EU AI Act Reference Tool ---")
    ref_tool = EUAIActReferenceTool()
    articles = ref_tool.search_articles("high-risk")
    print(f"Found {len(articles)} articles mentioning 'high-risk':")
    for article in articles:
        print(f"  {article['article_id']}: {article['title']}")
    
    # Compliance Scoring Tool
    print("\n--- Compliance Scoring Tool ---")
    scoring_tool = ComplianceScoringTool()
    system_data = {
        "system_name": "Employment Screening AI",
        "use_case": "Automated hiring decisions",
    }
    score_result = scoring_tool.calculate_compliance_score(system_data)
    print(f"Score: {score_result['score']}/100")
    print(f"Category: {score_result['category']}")


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
    logger.info("Starting EU AI Act Compliance Agent Demo")
    
    # Validate configuration
    if not Config.validate():
        logger.warning("Some APIs not configured - using mock implementations")
    
    # Run demos
    demo_basic_assessment()
    demo_sessions_and_memory()
    demo_tools()
    demo_observability()
    save_outputs()
    
    print("\n" + "="*70)
    print("Demo completed successfully!")
    print("Check 'outputs/' directory for generated traces and metrics")
    print("="*70 + "\n")
