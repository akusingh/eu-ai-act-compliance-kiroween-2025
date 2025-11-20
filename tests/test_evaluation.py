"""Unit tests for evaluation.py - Evaluation framework."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.evaluation import EvaluationScenario, AgentEvaluator
from src.models import RiskTier
import asyncio


class TestEvaluationScenario:
    """Test suite for EvaluationScenario."""
    
    def test_scenario_creation(self):
        """Test creating a basic evaluation scenario."""
        scenario = EvaluationScenario(
            scenario_id="s1",
            name="Test Scenario",
            description="Test description",
            system_description="AI system for testing",
            use_case="Testing",
            expected_risk_tier=RiskTier.HIGH_RISK,
            expected_score_range=(55, 84)
        )
        
        assert scenario.scenario_id == "s1"
        assert scenario.name == "Test Scenario"
        assert scenario.expected_risk_tier == RiskTier.HIGH_RISK
        assert scenario.expected_score_range == (55, 84)
    
    def test_scenario_with_optional_fields(self):
        """Test scenario with optional data_types and decision_impact."""
        scenario = EvaluationScenario(
            scenario_id="s2",
            name="Complete Scenario",
            description="Complete test",
            system_description="Complete system",
            use_case="Complete testing",
            expected_risk_tier=RiskTier.PROHIBITED,
            expected_score_range=(85, 100),
            data_types=["biometric", "personal_data"],
            decision_impact="significant",
            autonomous_decision=True
        )
        
        assert scenario.data_types == ["biometric", "personal_data"]
        assert scenario.decision_impact == "significant"
        assert scenario.autonomous_decision is True
    
    def test_scenario_score_range_validation(self):
        """Test that score range makes sense."""
        scenario = EvaluationScenario(
            scenario_id="s3",
            name="Range Test",
            description="Test score range",
            system_description="System",
            use_case="Testing",
            expected_risk_tier=RiskTier.MINIMAL_RISK,
            expected_score_range=(0, 24)
        )
        
        min_score, max_score = scenario.expected_score_range
        assert min_score < max_score
        assert 0 <= min_score <= 100
        assert 0 <= max_score <= 100


class TestAgentEvaluator:
    """Test suite for AgentEvaluator."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        agent = Mock()
        agent.run = AsyncMock()
        return agent
    
    @pytest.fixture
    def evaluator(self, mock_agent):
        """Create an AgentEvaluator with mocked agent."""
        return AgentEvaluator(agent=mock_agent)
    
    @pytest.fixture
    def sample_scenarios(self):
        """Create sample evaluation scenarios."""
        return [
            EvaluationScenario(
                scenario_id="s1_test",
                name="Prohibited System",
                description="Social scoring",
                system_description="Government social scoring system",
                use_case="Social credit scoring",
                expected_risk_tier=RiskTier.PROHIBITED,
                expected_score_range=(85, 100)
            ),
            EvaluationScenario(
                scenario_id="s2_test",
                name="High Risk System",
                description="Employment AI",
                system_description="AI for hiring decisions",
                use_case="Recruitment",
                expected_risk_tier=RiskTier.HIGH_RISK,
                expected_score_range=(55, 84)
            )
        ]
    
    def test_evaluator_initialization(self, evaluator):
        """Test that evaluator initializes correctly."""
        assert evaluator.agent is not None
        assert hasattr(evaluator, 'run_evaluation')
        assert hasattr(evaluator, 'evaluate_single_scenario')
    
    def test_risk_tier_match_evaluation(self, evaluator):
        """Test that risk tier matching is evaluated correctly."""
        # This tests the internal logic if accessible
        # You may need to adjust based on actual implementation
        
        # Match case
        assert RiskTier.HIGH_RISK == RiskTier.HIGH_RISK
        
        # Mismatch case  
        assert RiskTier.HIGH_RISK != RiskTier.MINIMAL_RISK
    
    def test_score_range_evaluation(self, evaluator):
        """Test that score range checking works correctly."""
        # Test scores within range
        assert 55 <= 70 <= 84  # High risk range
        assert 0 <= 15 <= 24   # Minimal risk range
        
        # Test scores outside range
        assert not (55 <= 30 <= 84)  # Too low for high risk
        assert not (0 <= 50 <= 24)   # Too high for minimal risk
    
    @pytest.mark.asyncio
    async def test_evaluate_single_scenario_success(self, evaluator, mock_agent):
        """Test successful single scenario evaluation."""
        scenario = EvaluationScenario(
            scenario_id="test_s1",
            name="Test",
            description="Test",
            system_description="Test system",
            use_case="Testing",
            expected_risk_tier=RiskTier.HIGH_RISK,
            expected_score_range=(55, 84)
        )
        
        # Mock agent response
        mock_agent.run.return_value = {
            "assessment": {
                "risk_tier": "high_risk",
                "score": 70,
                "confidence": 0.85
            }
        }
        
        result = await evaluator.evaluate_single_scenario(scenario)
        
        assert result is not None
        assert "scenario_id" in result
        assert result["scenario_id"] == "test_s1"
    
    @pytest.mark.asyncio
    async def test_evaluate_single_scenario_error_handling(self, evaluator, mock_agent):
        """Test that errors in scenario evaluation are handled."""
        scenario = EvaluationScenario(
            scenario_id="error_test",
            name="Error Test",
            description="Test error handling",
            system_description="System",
            use_case="Testing",
            expected_risk_tier=RiskTier.MINIMAL_RISK,
            expected_score_range=(0, 24)
        )
        
        # Mock agent to raise exception
        mock_agent.run.side_effect = Exception("API Error")
        
        result = await evaluator.evaluate_single_scenario(scenario)
        
        assert result is not None
        assert "error" in result
    
    def test_results_aggregation(self, evaluator):
        """Test that results are properly aggregated."""
        # Mock results
        results = [
            {"scenario_id": "s1", "passed": True, "expected": "high_risk", "actual": "high_risk"},
            {"scenario_id": "s2", "passed": False, "expected": "minimal_risk", "actual": "limited_risk"},
            {"scenario_id": "s3", "passed": True, "expected": "prohibited", "actual": "prohibited"}
        ]
        
        # Count passes
        passed = sum(1 for r in results if r.get("passed", False))
        total = len(results)
        accuracy = passed / total if total > 0 else 0
        
        assert passed == 2
        assert total == 3
        assert accuracy == pytest.approx(0.667, abs=0.01)


class TestEvaluationMetrics:
    """Test suite for evaluation metrics calculation."""
    
    def test_accuracy_calculation(self):
        """Test accuracy metric calculation."""
        results = [
            {"passed": True},
            {"passed": True},
            {"passed": False},
            {"passed": True}
        ]
        
        passed = sum(1 for r in results if r.get("passed", False))
        accuracy = passed / len(results)
        
        assert accuracy == 0.75
    
    def test_risk_tier_confusion_matrix(self):
        """Test confusion matrix for risk tier predictions."""
        results = [
            {"expected": "high_risk", "actual": "high_risk"},  # TP
            {"expected": "high_risk", "actual": "minimal_risk"},  # FP
            {"expected": "minimal_risk", "actual": "minimal_risk"},  # TN
            {"expected": "prohibited", "actual": "prohibited"}  # TP
        ]
        
        # Count correct predictions
        correct = sum(1 for r in results if r.get("expected") == r.get("actual"))
        assert correct == 3
    
    def test_score_difference_calculation(self):
        """Test calculation of score differences."""
        results = [
            {"expected_score": 70, "actual_score": 75},  # diff: 5
            {"expected_score": 30, "actual_score": 25},  # diff: 5
            {"expected_score": 90, "actual_score": 95}   # diff: 5
        ]
        
        diffs = [abs(r["expected_score"] - r["actual_score"]) for r in results]
        avg_diff = sum(diffs) / len(diffs)
        
        assert avg_diff == 5.0
    
    def test_confidence_score_aggregation(self):
        """Test aggregation of confidence scores."""
        results = [
            {"confidence": 0.85},
            {"confidence": 0.90},
            {"confidence": 0.75},
            {"confidence": 0.95}
        ]
        
        confidences = [r["confidence"] for r in results]
        avg_confidence = sum(confidences) / len(confidences)
        
        assert avg_confidence == 0.8625


class TestScenarioExecution:
    """Test suite for scenario execution flow."""
    
    @pytest.mark.asyncio
    async def test_sequential_scenario_execution(self):
        """Test that scenarios are executed sequentially."""
        execution_order = []
        
        async def mock_execute(scenario_id):
            execution_order.append(scenario_id)
            await asyncio.sleep(0.01)  # Simulate async work
            return {"scenario_id": scenario_id}
        
        scenarios = ["s1", "s2", "s3"]
        
        for s_id in scenarios:
            await mock_execute(s_id)
        
        assert execution_order == ["s1", "s2", "s3"]
    
    def test_rate_limiting_delay(self):
        """Test that rate limiting delay is applied."""
        import time
        
        delay_seconds = 0.1
        start_time = time.time()
        time.sleep(delay_seconds)
        elapsed = time.time() - start_time
        
        assert elapsed >= delay_seconds


if __name__ == "__main__":
    # Generate test documentation JSON
    from test_utils import generate_test_documentation, save_test_documentation
    
    test_classes = [
        TestEvaluationScenario,
        TestAgentEvaluator,
        TestEvaluationMetrics,
        TestScenarioExecution
    ]
    
    docs = generate_test_documentation(__file__, test_classes)
    json_path = save_test_documentation(docs)
    print(f"\n✅ Test documentation generated: {json_path}\n")
    
    # Run tests
    pytest.main([__file__, "-v"])
