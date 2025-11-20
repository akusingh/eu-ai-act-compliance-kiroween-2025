#!/usr/bin/env python3
"""Evaluation runner for EU AI Act Compliance Agent."""

import logging
from pathlib import Path

from src.config import Config
from src.observability import setup_logging, trace_collector, metrics_collector
from src.evaluation import AgentEvaluator


# Setup logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


def main():
    """Run agent evaluation against test scenarios using ADK."""
    print("\n" + "="*70)
    print("EU AI Act Compliance Agent - Evaluation Suite (ADK)")
    print("Framework: Google ADK + Gemini 2.0 Flash")
    print("="*70 + "\n")
    
    logger.info("Starting ADK agent evaluation")
    
    # Validate Gemini API key (required for ADK)
    if not Config.GOOGLE_GENAI_API_KEY:
        logger.error("GOOGLE_GENAI_API_KEY not set!")
        print("\n⚠️  ERROR: GOOGLE_GENAI_API_KEY not configured in .env")
        print("ADK evaluation requires Gemini API key.")
        print("Get one at: https://aistudio.google.com/\n")
        return False
    
    # Initialize evaluator
    evaluator = AgentEvaluator()
    
    print(f"Running {len(evaluator.scenarios)} test scenarios...\n")
    
    # Run evaluation
    evaluation_results = evaluator.run_evaluation()
    
    # Print report
    print(evaluator.get_evaluation_report())
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Total Scenarios: {evaluation_results['total_scenarios']}")
    print(f"  Passed: {evaluation_results['passed']}")
    print(f"  Failed: {evaluation_results['failed']}")
    print(f"  Accuracy: {evaluation_results['accuracy_percentage']}")
    
    # Save results
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Save evaluation results
    eval_file = output_dir / "evaluation.json"
    evaluator.save_evaluation_results(str(eval_file))
    print(f"\nEvaluation results saved to {eval_file}")
    
    # Save traces
    trace_file = output_dir / "traces.json"
    trace_collector.save_traces(str(trace_file))
    print(f"Execution traces saved to {trace_file}")
    
    # Save metrics
    metrics_file = output_dir / "metrics.json"
    metrics_collector.save_metrics(str(metrics_file))
    print(f"Performance metrics saved to {metrics_file}")
    
    print("\n" + "="*70)
    print("ADK Evaluation complete!")
    print("Framework: Google ADK with Gemini 2.0 Flash")
    print("="*70 + "\n")
    
    return evaluation_results["passed"] == evaluation_results["total_scenarios"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
