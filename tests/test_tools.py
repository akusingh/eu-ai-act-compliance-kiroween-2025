"""Unit tests for tools_adk.py - ComplianceScoringTool and EUAIActReferenceTool."""

import pytest
from unittest.mock import Mock, patch
from src.tools_adk import ComplianceScoringTool, EUAIActReferenceTool
from src.models import RiskTier


class TestComplianceScoringTool:
    """Test suite for ComplianceScoringTool."""
    
    @pytest.fixture
    def scoring_tool(self):
        """Create a ComplianceScoringTool instance for testing."""
        return ComplianceScoringTool()
    
    def test_tool_initialization(self, scoring_tool):
        """Test that tool initializes correctly with proper name and description."""
        assert scoring_tool.name == "score_compliance_risk"
        assert "risk score" in scoring_tool.description.lower()
        assert scoring_tool.framework is not None
    
    def test_framework_has_required_patterns(self, scoring_tool):
        """Test that framework contains all required pattern categories."""
        assert "prohibited_patterns" in scoring_tool.framework
        assert "high_risk_patterns" in scoring_tool.framework
        assert "limited_risk_patterns" in scoring_tool.framework
        assert isinstance(scoring_tool.framework["prohibited_patterns"], list)
    
    def test_score_range_bounds(self, scoring_tool):
        """Test that risk scores are within valid range (0-100)."""
        test_input = '{"system_description": "Test system", "use_case": "Testing"}'
        result = scoring_tool._run(test_input)
        
        # Extract score from result string
        import json
        result_dict = json.loads(result)
        score = result_dict.get("risk_score", 0)
        
        assert 0 <= score <= 100, f"Score {score} out of valid range"
    
    def test_prohibited_system_high_score(self, scoring_tool):
        """Test that prohibited systems get very high risk scores (85+)."""
        prohibited_input = '''{
            "system_description": "Real-time biometric facial recognition for mass surveillance",
            "use_case": "social scoring by government",
            "data_types": ["biometric", "personal_data"],
            "autonomous_decision": true
        }'''
        
        result = scoring_tool._run(prohibited_input)
        import json
        result_dict = json.loads(result)
        score = result_dict["risk_score"]
        
        assert score >= 85, f"Prohibited system scored {score}, expected >= 85"
    
    def test_high_risk_system_appropriate_score(self, scoring_tool):
        """Test that high-risk systems get scores in 55-84 range."""
        high_risk_input = '''{
            "system_description": "AI system for employment screening",
            "use_case": "recruitment and hiring decisions",
            "data_types": ["personal_data", "employment_data"],
            "decision_impact": "significant",
            "autonomous_decision": true
        }'''
        
        result = scoring_tool._run(high_risk_input)
        import json
        result_dict = json.loads(result)
        score = result_dict["risk_score"]
        
        assert 55 <= score < 85, f"High-risk system scored {score}, expected 55-84"
    
    def test_limited_risk_system_appropriate_score(self, scoring_tool):
        """Test that limited-risk systems get scores in 25-54 range."""
        limited_risk_input = '''{
            "system_description": "Customer service chatbot",
            "use_case": "automated customer support",
            "data_types": ["conversation_data"],
            "autonomous_decision": false,
            "human_oversight": true
        }'''
        
        result = scoring_tool._run(limited_risk_input)
        import json
        result_dict = json.loads(result)
        score = result_dict["risk_score"]
        
        assert 25 <= score < 55, f"Limited-risk system scored {score}, expected 25-54"
    
    def test_minimal_risk_system_low_score(self, scoring_tool):
        """Test that minimal-risk systems get low scores (< 25)."""
        minimal_risk_input = '''{
            "system_description": "Spam filter",
            "use_case": "email filtering",
            "data_types": ["email_content"],
            "decision_impact": "minimal",
            "autonomous_decision": true
        }'''
        
        result = scoring_tool._run(minimal_risk_input)
        import json
        result_dict = json.loads(result)
        score = result_dict["risk_score"]
        
        assert score < 25, f"Minimal-risk system scored {score}, expected < 25"
    
    def test_confidence_score_in_valid_range(self, scoring_tool):
        """Test that confidence scores are between 0 and 1."""
        test_input = '{"system_description": "Test", "use_case": "Testing"}'
        result = scoring_tool._run(test_input)
        
        import json
        result_dict = json.loads(result)
        confidence = result_dict.get("confidence_score", 0)
        
        assert 0 <= confidence <= 1, f"Confidence {confidence} out of valid range"
    
    def test_result_contains_required_fields(self, scoring_tool):
        """Test that result contains all required fields."""
        test_input = '{"system_description": "Test system", "use_case": "Testing"}'
        result = scoring_tool._run(test_input)
        
        import json
        result_dict = json.loads(result)
        
        assert "risk_score" in result_dict
        assert "risk_tier" in result_dict
        assert "confidence_score" in result_dict
        assert "reasoning" in result_dict
    
    def test_pattern_matching_prohibited(self, scoring_tool):
        """Test that prohibited patterns are correctly identified."""
        patterns = scoring_tool.framework["prohibited_patterns"]
        
        # Check that key prohibited patterns exist
        assert any("social scoring" in p.lower() for p in patterns)
        assert any("biometric" in p.lower() for p in patterns)
        assert any("manipulation" in p.lower() or "subliminal" in p.lower() for p in patterns)
    
    def test_pattern_matching_high_risk(self, scoring_tool):
        """Test that high-risk patterns are correctly identified."""
        patterns = scoring_tool.framework["high_risk_patterns"]
        
        # Check that key high-risk patterns exist
        assert any("employment" in p.lower() or "recruitment" in p.lower() for p in patterns)
        assert any("credit" in p.lower() or "creditworthiness" in p.lower() for p in patterns)
        assert any("law enforcement" in p.lower() for p in patterns)
    
    def test_json_parsing_error_handling(self, scoring_tool):
        """Test that tool handles invalid JSON gracefully."""
        invalid_json = "This is not valid JSON"
        
        # Should not raise exception, should return error in result
        result = scoring_tool._run(invalid_json)
        assert result is not None
        assert "error" in result.lower() or "invalid" in result.lower()


class TestEUAIActReferenceTool:
    """Test suite for EUAIActReferenceTool."""
    
    @pytest.fixture
    def reference_tool(self):
        """Create an EUAIActReferenceTool instance for testing."""
        return EUAIActReferenceTool()
    
    def test_tool_initialization(self, reference_tool):
        """Test that tool initializes correctly."""
        assert reference_tool.name == "get_euaiact_reference"
        assert "EU AI Act" in reference_tool.description
        assert reference_tool.act_text is not None
    
    def test_article_extraction(self, reference_tool):
        """Test that specific articles can be extracted."""
        # Test for Article 5 (prohibited practices)
        result = reference_tool._run('{"article_number": "5"}')
        
        assert "Article 5" in result
        assert len(result) > 100  # Should contain substantial content
    
    def test_multiple_articles_extraction(self, reference_tool):
        """Test extracting multiple articles at once."""
        result = reference_tool._run('{"article_numbers": ["5", "6", "9"]}')
        
        assert "Article 5" in result
        assert "Article 6" in result  
        assert "Article 9" in result
    
    def test_keyword_search(self, reference_tool):
        """Test keyword-based search functionality."""
        result = reference_tool._run('{"keywords": ["high-risk", "employment"]}')
        
        assert len(result) > 0
        assert "high" in result.lower() or "employment" in result.lower()
    
    def test_invalid_article_number(self, reference_tool):
        """Test handling of invalid article numbers."""
        result = reference_tool._run('{"article_number": "999"}')
        
        # Should handle gracefully, not crash
        assert result is not None
    
    def test_empty_query_handling(self, reference_tool):
        """Test handling of empty queries."""
        result = reference_tool._run('{}')
        
        # Should return something, not crash
        assert result is not None
        assert len(result) > 0


if __name__ == "__main__":
    # Generate test documentation JSON
    from test_utils import generate_test_documentation, save_test_documentation
    
    test_classes = [
        TestComplianceScoringTool,
        TestEUAIActReferenceTool
    ]
    
    docs = generate_test_documentation(__file__, test_classes)
    json_path = save_test_documentation(docs)
    print(f"\n✅ Test documentation generated: {json_path}\n")
    
    # Run tests
    pytest.main([__file__, "-v"])
