"""Evaluation framework for assessing agent accuracy and performance."""

import json
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path

from src.models import RiskTier
# Using SequentialAgent-based orchestrator for evaluation
from src.sequential_orchestrator import ComplianceOrchestrator
from src.observability import metrics_collector, trace_collector


logger = logging.getLogger(__name__)


class EvaluationScenario:
    """Represents a test scenario for agent evaluation."""

    def __init__(
        self,
        scenario_id: str,
        system_info: Dict[str, Any],
        expected_risk_tier: RiskTier,
        description: str,
    ):
        """Initialize evaluation scenario.
        
        Args:
            scenario_id: Unique identifier for scenario
            system_info: AI system information
            expected_risk_tier: Expected risk classification
            description: Scenario description
        """
        self.scenario_id = scenario_id
        self.system_info = system_info
        self.expected_risk_tier = expected_risk_tier
        self.description = description
        self.actual_risk_tier: RiskTier = None
        self.is_correct = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert scenario to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "scenario_id": self.scenario_id,
            "description": self.description,
            "expected": self.expected_risk_tier.value if self.expected_risk_tier else None,
            "actual": self.actual_risk_tier.value if self.actual_risk_tier else None,
            "correct": self.is_correct,
        }


class AgentEvaluator:
    """Evaluates agent performance against test scenarios."""

    def __init__(self):
        """Initialize agent evaluator."""
        self.orchestrator = ComplianceOrchestrator()
        self.scenarios: List[EvaluationScenario] = []
        self.results: List[Dict[str, Any]] = []
        self._create_default_scenarios()

    def _create_default_scenarios(self) -> None:
        """Create default test scenarios based on EU AI Act."""
        scenarios = [
            EvaluationScenario(
                scenario_id="s1_prohibited",
                system_info={
                    "system_name": "Mass Surveillance Facial Recognition",
                    "use_case": "Mass facial recognition for law enforcement without specific suspicion",
                    "data_types": ["biometric"],
                    "decision_impact": "significant",
                    "affected_groups": "General public",
                    "autonomous_decision": True,
                    "human_oversight": False,
                    "error_consequences": "Severe - fundamental rights violation",
                },
                expected_risk_tier=RiskTier.PROHIBITED,
                description="Facial recognition for mass surveillance (Article 5 violation)",
            ),
            EvaluationScenario(
                scenario_id="s2_high_risk_credit",
                system_info={
                    "system_name": "Loan Approval System",
                    "use_case": "Creditworthiness assessment for loan decisions",
                    "data_types": ["financial", "personal_data"],
                    "decision_impact": "significant",
                    "affected_groups": "Loan applicants",
                    "autonomous_decision": True,
                    "human_oversight": True,
                    "error_consequences": "Severe - affects credit access",
                },
                expected_risk_tier=RiskTier.HIGH_RISK,
                description="High-risk: Creditworthiness assessment (Annex III)",
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
                scenario_id="s5_minimal_risk_recommendations",
                system_info={
                    "system_name": "Music Recommendation Engine",
                    "use_case": "Personalized music recommendations",
                    "data_types": ["user_behavior"],
                    "decision_impact": "minimal",
                    "affected_groups": "Music streaming users",
                    "autonomous_decision": False,
                    "human_oversight": False,
                    "error_consequences": "Minimal - user sees different recommendations",
                },
                expected_risk_tier=RiskTier.MINIMAL_RISK,
                description="Minimal-risk: Personalization system",
            ),
            EvaluationScenario(
                scenario_id="s6_high_risk_law_enforcement",
                system_info={
                    "system_name": "Police Risk Assessment Tool",
                    "use_case": "Risk assessment for law enforcement operations",
                    "data_types": ["personal_data", "criminal"],
                    "decision_impact": "significant",
                    "affected_groups": "Individuals under law enforcement scrutiny",
                    "autonomous_decision": True,
                    "human_oversight": True,
                    "error_consequences": "Severe - affects freedom and security",
                },
                expected_risk_tier=RiskTier.HIGH_RISK,
                description="High-risk: Law enforcement operations (Annex III)",
            ),
            EvaluationScenario(
                scenario_id="s7_minimal_risk_weather",
                system_info={
                    "system_name": "Weather Prediction Model",
                    "use_case": "ML-based weather forecasting",
                    "data_types": ["weather_data"],
                    "decision_impact": "minimal",
                    "affected_groups": "General public",
                    "autonomous_decision": False,
                    "human_oversight": False,
                    "error_consequences": "Minor - inaccurate weather forecast",
                },
                expected_risk_tier=RiskTier.MINIMAL_RISK,
                description="Minimal-risk: General ML application",
            ),
            EvaluationScenario(
                scenario_id="s8_limited_risk_deepfake",
                system_info={
                    "system_name": "Synthetic Media Tool",
                    "use_case": "Generation of synthetic media and deepfakes",
                    "data_types": ["media"],
                    "decision_impact": "moderate",
                    "affected_groups": "Media consumers",
                    "autonomous_decision": False,
                    "human_oversight": True,
                    "error_consequences": "Moderate - misinformation risk",
                },
                expected_risk_tier=RiskTier.LIMITED_RISK,
                description="Limited-risk: Deepfakes and synthetic content",
            ),
        ]
        self.scenarios = scenarios
        logger.info(f"Created {len(scenarios)} evaluation scenarios")

    def run_evaluation(self) -> Dict[str, Any]:
        """Run evaluation against all scenarios.
        
        Returns:
            Dictionary with evaluation results
        """
        import time
        
        logger.info("Starting agent evaluation")
        
        successful = 0
        failed = 0
        
        for idx, scenario in enumerate(self.scenarios):
            try:
                logger.info(f"Running scenario {idx+1}/{len(self.scenarios)}: {scenario.scenario_id}")
                
                trace_collector.record_trace(
                    agent_name="Evaluator",
                    action="scenario_start",
                    input_data={
                        "scenario_id": scenario.scenario_id,
                        "expected_tier": scenario.expected_risk_tier.value
                    },
                    status="success"
                )
                
                # Run assessment
                result = self.orchestrator.assess_system(scenario.system_info)
                
                # Extract risk tier (try both 'tier' and 'risk_tier' for backwards compatibility)
                assessment = result.get("assessment", {})
                actual_tier_str = assessment.get("tier") or assessment.get("risk_tier")
                if not actual_tier_str:
                    raise KeyError(f"No risk tier found in assessment: {assessment.keys()}")
                
                # Convert to lowercase with underscores (e.g., "LIMITED_RISK" -> "limited_risk")
                actual_tier_str = actual_tier_str.lower().replace(" ", "_").replace("-", "_")
                scenario.actual_risk_tier = RiskTier(actual_tier_str)
                
                # Check if correct
                scenario.is_correct = (
                    scenario.actual_risk_tier == scenario.expected_risk_tier
                )
                
                if scenario.is_correct:
                    successful += 1
                    logger.info(f"Scenario {scenario.scenario_id}: PASS")
                else:
                    failed += 1
                    logger.warning(
                        f"Scenario {scenario.scenario_id}: FAIL "
                        f"(expected {scenario.expected_risk_tier}, "
                        f"got {scenario.actual_risk_tier})"
                    )
                
                # Store result
                result_data = scenario.to_dict()
                assessment = result.get("assessment", {})
                result_data["risk_score"] = assessment.get("score", 0)
                result_data["confidence"] = assessment.get("confidence", 0.0)
                
                self.results.append(result_data)
                
                # Record scenario completion
                trace_collector.record_trace(
                    agent_name="Evaluator",
                    action="scenario_complete",
                    output_data={
                        "scenario_id": scenario.scenario_id,
                        "expected": scenario.expected_risk_tier.value,
                        "actual": scenario.actual_risk_tier.value,
                        "correct": scenario.is_correct,
                        "score": result_data["risk_score"]
                    },
                    status="success"
                )
                
                metrics_collector.record_metric(
                    "scenario_result",
                    1 if scenario.is_correct else 0,
                    tags={
                        "scenario_id": scenario.scenario_id,
                        "expected_tier": scenario.expected_risk_tier.value,
                        "actual_tier": scenario.actual_risk_tier.value
                    }
                )
                
                # Add delay between assessments to avoid rate limits
                # Each assessment uses ~13-15 API requests, rate limit is 15/min
                # Need to wait 90 seconds for rate limit window to reset (extra buffer)
                if idx < len(self.scenarios) - 1:  # Don't delay after last scenario
                    logger.info("⏳ Waiting 90 seconds for API rate limit to reset...")
                    time.sleep(90)
                
            except Exception as e:
                failed += 1
                logger.error(f"Scenario {scenario.scenario_id} execution failed: {e}")
                
                trace_collector.record_trace(
                    agent_name="Evaluator",
                    action="scenario_failed",
                    input_data={"scenario_id": scenario.scenario_id},
                    status="error",
                    error=str(e)
                )
                
                self.results.append({
                    "scenario_id": scenario.scenario_id,
                    "error": str(e),
                    "correct": False,
                })
        
        # Calculate metrics
        total = len(self.scenarios)
        accuracy = successful / total if total > 0 else 0
        
        evaluation_summary = {
            "total_scenarios": total,
            "passed": successful,
            "failed": failed,
            "accuracy": accuracy,
            "accuracy_percentage": f"{accuracy * 100:.1f}%",
            "results": self.results,
        }
        
        logger.info(f"Evaluation complete: {successful}/{total} passed")
        metrics_collector.record_metric("evaluation_accuracy", accuracy)
        metrics_collector.record_metric(
            "evaluation_summary",
            successful,
            tags={"total": str(total), "failed": str(failed)}
        )
        
        # Save metrics and traces
        try:
            metrics_collector.save_metrics("outputs/metrics.json")
            trace_collector.save_traces("outputs/traces.json")
            logger.info("Observability data saved to outputs/")
        except Exception as e:
            logger.warning(f"Failed to save observability data: {e}")
        
        return evaluation_summary
    
    def get_evaluation_report(self) -> str:
        """Generate human-readable evaluation report.
        
        Returns:
            Formatted evaluation report
        """
        if not self.results:
            return "No evaluation results available. Run evaluation first."
        
        # Calculate stats
        passed = sum(1 for r in self.results if r.get("correct", False))
        total = len([r for r in self.results if "scenario_id" in r])
        accuracy = passed / total if total > 0 else 0
        
        lines = [
            "="*70,
            "EU AI Act Compliance Agent - Evaluation Report",
            "="*70,
            "",
            f"Total Scenarios: {total}",
            f"Passed: {passed}",
            f"Failed: {total - passed}",
            f"Accuracy: {accuracy * 100:.1f}%",
            "",
            "Detailed Results:",
            "-"*70,
        ]
        
        for result in self.results:
            if "error" in result:
                lines.append(f"  {result['scenario_id']}: ERROR - {result['error']}")
            else:
                status = "PASS" if result["correct"] else "FAIL"
                lines.append(
                    f"  {result['scenario_id']}: {status} "
                    f"(expected {result['expected']}, got {result['actual']})"
                )
        
        lines.append("="*70)
        
        return "\n".join(lines)

    def save_evaluation_results(self, filepath: str) -> None:
        """Save evaluation results to JSON file.
        
        Args:
            filepath: Path to save results
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            "evaluation_summary": {
                "total_scenarios": len(self.scenarios),
                "passed": sum(1 for r in self.results if r.get("correct", False)),
                "failed": sum(1 for r in self.results if not r.get("correct", False)),
            },
            "detailed_results": self.results,
        }
        
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Evaluation results saved to {filepath}")
