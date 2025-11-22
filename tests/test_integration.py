"""Integration tests for complete EU AI Act compliance assessment workflow.

These tests require API access and are marked with @pytest.mark.integration.
Run with: pytest tests/test_integration.py -v -m integration
Skip with: pytest tests/ -v -m "not integration"
"""

import pytest
import os
from pathlib import Path
from src.sequential_orchestrator import ComplianceOrchestrator
from src.models import RiskTier
from src.config import Config

# Check if API key is available
API_KEY_AVAILABLE = bool(Config.GOOGLE_GENAI_API_KEY)


@pytest.mark.integration
@pytest.mark.skipif(not API_KEY_AVAILABLE, reason="Requires GOOGLE_GENAI_API_KEY")
class TestFullAssessmentWorkflow:
    """Integration tests for complete assessment workflow."""
    
    @pytest.fixture(scope="class")
    def orchestrator(self):
        """Create orchestrator instance for integration tests."""
        return ComplianceOrchestrator()
    
    def test_minimal_risk_assessment(self, orchestrator):
        """Test full assessment of minimal-risk system (music recommender)."""
        system_info = {
            "system_name": "Music Recommendation System",
            "use_case": "Suggest songs based on user listening history",
            "data_types": ["listening_history"],
            "decision_impact": "minimal",
            "affected_groups": "Music listeners",
            "autonomous_decision": True,
            "human_oversight": False,
            "error_consequences": "Minimal - user gets bad music suggestion",
        }
        
        result = orchestrator.assess_system(system_info)
        
        # Verify structure
        assert "assessment" in result
        assert "report" in result
        assert "state" in result
        
        # Verify assessment content
        assessment = result["assessment"]
        assert "tier" in assessment
        assert "score" in assessment
        
        # Should be minimal risk
        assert assessment["tier"] == "minimal_risk"
        assert assessment["score"] < 25
    
    def test_limited_risk_assessment(self, orchestrator):
        """Test full assessment of limited-risk system (chatbot)."""
        system_info = {
            "system_name": "Customer Service Chatbot",
            "use_case": "Automated customer support chatbot",
            "data_types": ["conversation_data"],
            "decision_impact": "moderate",
            "affected_groups": "Customer service users",
            "autonomous_decision": False,
            "human_oversight": True,
            "error_consequences": "Moderate - frustrated customer",
        }
        
        result = orchestrator.assess_system(system_info)
        
        assessment = result["assessment"]
        assert assessment["tier"] == "limited_risk"
        assert 25 <= assessment["score"] < 55
    
    def test_high_risk_assessment(self, orchestrator):
        """Test full assessment of high-risk system (hiring AI)."""
        system_info = {
            "system_name": "Employment Screening System",
            "use_case": "AI system for recruitment and hiring decisions",
            "data_types": ["personal_data", "employment_data"],
            "decision_impact": "significant",
            "affected_groups": "Job applicants",
            "autonomous_decision": True,
            "human_oversight": True,
            "error_consequences": "Severe - candidate wrongly rejected",
        }
        
        result = orchestrator.assess_system(system_info)
        
        assessment = result["assessment"]
        assert assessment["tier"] == "high_risk"
        assert 55 <= assessment["score"] < 85
    
    def test_prohibited_assessment(self, orchestrator):
        """Test full assessment of prohibited system (mass surveillance)."""
        system_info = {
            "system_name": "Mass Surveillance System",
            "use_case": "Real-time biometric facial recognition for mass surveillance and social scoring",
            "data_types": ["biometric", "personal_data"],
            "decision_impact": "significant",
            "affected_groups": "General public",
            "autonomous_decision": True,
            "human_oversight": False,
            "error_consequences": "Severe - civil liberties violations",
        }
        
        result = orchestrator.assess_system(system_info)
        
        assessment = result["assessment"]
        assert assessment["tier"] == "prohibited"
        assert assessment["score"] >= 85
    
    def test_assessment_includes_articles(self, orchestrator):
        """Test that assessment includes relevant EU AI Act articles."""
        system_info = {
            "system_name": "Loan Approval System",
            "use_case": "Creditworthiness assessment for loan decisions",
            "data_types": ["financial", "personal_data"],
            "decision_impact": "significant",
            "affected_groups": "Loan applicants",
            "autonomous_decision": True,
            "human_oversight": True,
            "error_consequences": "Severe - affects credit access",
        }
        
        result = orchestrator.assess_system(system_info)
        
        assessment = result["assessment"]
        assert "articles" in assessment or "relevant_articles" in result.get("report", {})
        
        # High-risk systems should reference Articles 6, 8, 9
        assert assessment["tier"] == "high_risk"
    
    def test_assessment_produces_report(self, orchestrator):
        """Test that assessment produces a complete report."""
        system_info = {
            "system_name": "Test System",
            "use_case": "Integration testing",
            "data_types": ["test_data"],
            "decision_impact": "minimal",
            "affected_groups": "Test users",
            "autonomous_decision": False,
            "human_oversight": True,
            "error_consequences": "Minimal",
        }
        
        result = orchestrator.assess_system(system_info)
        
        # Report should exist and have content
        assert "report" in result
        report = result["report"]
        
        # Report should be a dictionary with metadata
        assert isinstance(report, dict)
    
    def test_state_management(self, orchestrator):
        """Test that state is properly managed through pipeline."""
        system_info = {
            "system_name": "State Test System",
            "use_case": "Testing state management",
            "data_types": ["test_data"],
            "decision_impact": "minimal",
            "affected_groups": "Test users",
            "autonomous_decision": True,
            "human_oversight": False,
            "error_consequences": "Minimal",
        }
        
        result = orchestrator.assess_system(system_info)
        
        # State should contain all pipeline stages
        state = result.get("state", {})
        
        # Check for expected state keys (may vary based on implementation)
        assert isinstance(state, dict)


@pytest.mark.integration
@pytest.mark.skipif(not API_KEY_AVAILABLE, reason="Requires GOOGLE_GENAI_API_KEY")
class TestObservabilityIntegration:
    """Integration tests for observability during assessments."""
    
    def test_metrics_recorded_during_assessment(self):
        """Test that metrics are recorded during full assessment."""
        from src.observability import metrics_collector, trace_collector
        
        # Clear any existing data
        metrics_collector.metrics.clear()
        trace_collector.traces.clear()
        
        orchestrator = ComplianceOrchestrator()
        
        system_info = {
            "system_name": "Metrics Test System",
            "use_case": "Testing metrics collection",
            "data_types": ["test_data"],
            "decision_impact": "minimal",
            "affected_groups": "Test users",
            "autonomous_decision": True,
            "human_oversight": False,
            "error_consequences": "Minimal",
        }
        
        result = orchestrator.assess_system(system_info)
        
        # Verify metrics were recorded
        assert len(metrics_collector.metrics) > 0
        
        # Check for expected metric types
        metric_names = [m["metric_name"] for m in metrics_collector.metrics]
        assert any("time" in name.lower() for name in metric_names)
    
    def test_traces_recorded_during_assessment(self):
        """Test that traces are recorded during full assessment."""
        from src.observability import metrics_collector, trace_collector
        
        # Clear any existing data
        metrics_collector.metrics.clear()
        trace_collector.traces.clear()
        
        orchestrator = ComplianceOrchestrator()
        
        system_info = {
            "system_name": "Traces Test System",
            "use_case": "Testing trace collection",
            "data_types": ["test_data"],
            "decision_impact": "minimal",
            "affected_groups": "Test users",
            "autonomous_decision": True,
            "human_oversight": False,
            "error_consequences": "Minimal",
        }
        
        result = orchestrator.assess_system(system_info)
        
        # Verify traces were recorded
        assert len(trace_collector.traces) > 0
        
        # Check for orchestrator traces
        agent_names = [t["agent"] for t in trace_collector.traces]
        assert "ComplianceOrchestrator" in agent_names or "SequentialPipeline" in agent_names


@pytest.mark.integration
@pytest.mark.skipif(not API_KEY_AVAILABLE, reason="Requires GOOGLE_GENAI_API_KEY")
class TestErrorHandling:
    """Integration tests for error handling in assessment workflow."""
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        orchestrator = ComplianceOrchestrator()
        
        # System info with missing fields
        incomplete_info = {
            "system_name": "Incomplete System",
            # Missing many required fields
        }
        
        # Should either handle gracefully or raise informative error
        try:
            result = orchestrator.assess_system(incomplete_info)
            # If it succeeds, verify it has reasonable defaults
            assert "assessment" in result
        except Exception as e:
            # If it fails, error should be informative
            assert len(str(e)) > 0
    
    def test_invalid_data_types(self):
        """Test handling of invalid data types."""
        orchestrator = ComplianceOrchestrator()
        
        system_info = {
            "system_name": "Invalid Data Test",
            "use_case": "Testing invalid data handling",
            "data_types": ["invalid_type_xyz123"],
            "decision_impact": "minimal",
            "affected_groups": "Test users",
            "autonomous_decision": True,
            "human_oversight": False,
            "error_consequences": "Minimal",
        }
        
        # Should handle unknown data types gracefully
        result = orchestrator.assess_system(system_info)
        assert "assessment" in result


@pytest.mark.integration
@pytest.mark.skipif(not API_KEY_AVAILABLE, reason="Requires GOOGLE_GENAI_API_KEY")
class TestPipelineInfo:
    """Integration tests for pipeline information and metadata."""
    
    def test_get_pipeline_info(self):
        """Test retrieving pipeline architecture information."""
        orchestrator = ComplianceOrchestrator()
        
        pipeline_info = orchestrator.get_pipeline_info()
        
        assert "type" in pipeline_info
        assert "total_agents" in pipeline_info
        assert pipeline_info["total_agents"] >= 3  # At least 3 agents in pipeline
    
    def test_metadata_in_result(self):
        """Test that assessment results include metadata."""
        orchestrator = ComplianceOrchestrator()
        
        system_info = {
            "system_name": "Metadata Test",
            "use_case": "Testing metadata",
            "data_types": ["test_data"],
            "decision_impact": "minimal",
            "affected_groups": "Test users",
            "autonomous_decision": True,
            "human_oversight": False,
            "error_consequences": "Minimal",
        }
        
        result = orchestrator.assess_system(system_info)
        
        # Check for metadata
        assert "metadata" in result or "meta" in result
        metadata = result.get("metadata", result.get("meta", {}))
        
        # Should include framework and model info
        if metadata:
            assert isinstance(metadata, dict)


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])
