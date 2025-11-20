"""Unit tests for models.py - Pydantic models and enums."""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydantic import ValidationError
from src.models import RiskTier, AISystemProfile, ComplianceAssessment


class TestRiskTierEnum:
    """Test suite for RiskTier enum."""
    
    def test_all_risk_tiers_defined(self):
        """Test that all four risk tiers are defined."""
        assert RiskTier.PROHIBITED
        assert RiskTier.HIGH_RISK
        assert RiskTier.LIMITED_RISK
        assert RiskTier.MINIMAL_RISK
    
    def test_risk_tier_values_lowercase(self):
        """Test that risk tier values are lowercase with underscores."""
        assert RiskTier.PROHIBITED.value == "prohibited"
        assert RiskTier.HIGH_RISK.value == "high_risk"
        assert RiskTier.LIMITED_RISK.value == "limited_risk"
        assert RiskTier.MINIMAL_RISK.value == "minimal_risk"
    
    def test_risk_tier_from_string(self):
        """Test creating RiskTier from string values."""
        assert RiskTier("prohibited") == RiskTier.PROHIBITED
        assert RiskTier("high_risk") == RiskTier.HIGH_RISK
        assert RiskTier("limited_risk") == RiskTier.LIMITED_RISK
        assert RiskTier("minimal_risk") == RiskTier.MINIMAL_RISK
    
    def test_invalid_risk_tier_raises_error(self):
        """Test that invalid risk tier string raises ValueError."""
        with pytest.raises(ValueError):
            RiskTier("invalid_tier")
    
    def test_risk_tier_comparison(self):
        """Test that risk tiers can be compared."""
        prohibited = RiskTier.PROHIBITED
        high = RiskTier.HIGH_RISK
        
        assert prohibited == RiskTier.PROHIBITED
        assert prohibited != high


class TestAISystemProfile:
    """Test suite for AISystemProfile model."""
    
    def test_valid_profile_creation(self):
        """Test creating a valid AISystemProfile."""
        profile = AISystemProfile(
            system_name="Test AI System",
            use_case="Employment screening",
            data_types=["personal_data", "employment_data"],
            decision_impact="significant",
            affected_groups="Job applicants",
            autonomous_decision=True,
            human_oversight=True,
            error_consequences="Candidate might be wrongly rejected"
        )
        
        assert profile.system_name == "Test AI System"
        assert profile.use_case == "Employment screening"
        assert len(profile.data_types) == 2
        assert profile.autonomous_decision is True
        assert profile.human_oversight is True
    
    def test_profile_with_minimal_data_types(self):
        """Test profile with single data type."""
        profile = AISystemProfile(
            system_name="Simple System",
            use_case="Email filtering",
            data_types=["email_content"],
            decision_impact="minimal",
            affected_groups="Email users",
            autonomous_decision=True,
            human_oversight=False,
            error_consequences="Spam might reach inbox"
        )
        
        assert len(profile.data_types) == 1
        assert profile.data_types[0] == "email_content"
    
    def test_profile_requires_all_fields(self):
        """Test that all required fields must be provided."""
        with pytest.raises(ValidationError):
            AISystemProfile(
                system_name="Incomplete System"
                # Missing required fields
            )
    
    def test_profile_boolean_fields(self):
        """Test boolean field validation."""
        profile = AISystemProfile(
            system_name="Test",
            use_case="Testing",
            data_types=["test_data"],
            decision_impact="moderate",
            affected_groups="Test users",
            autonomous_decision=False,
            human_oversight=True,
            error_consequences="Test error"
        )
        
        assert isinstance(profile.autonomous_decision, bool)
        assert isinstance(profile.human_oversight, bool)


class TestComplianceAssessment:
    """Test suite for ComplianceAssessment model."""
    
    def test_valid_assessment_creation(self):
        """Test creating a valid ComplianceAssessment."""
        assessment = ComplianceAssessment(
            system_name="Test System",
            risk_tier=RiskTier.HIGH_RISK,
            risk_score=75.5,
            relevant_articles=["Article 5", "Article 6"],
            compliance_gaps=["Missing human oversight documentation"]
        )
        
        assert assessment.system_name == "Test System"
        assert assessment.risk_tier == RiskTier.HIGH_RISK
        assert assessment.risk_score == 75.5
        assert len(assessment.relevant_articles) == 2
        assert len(assessment.compliance_gaps) == 1
    
    def test_risk_score_validation_bounds(self):
        """Test that risk score must be between 0 and 100."""
        # Valid score
        assessment = ComplianceAssessment(
            system_name="Test",
            risk_tier=RiskTier.MINIMAL_RISK,
            risk_score=50.0
        )
        assert assessment.risk_score == 50.0
        
        # Invalid score - too low
        with pytest.raises(ValidationError):
            ComplianceAssessment(
                system_name="Test",
                risk_tier=RiskTier.MINIMAL_RISK,
                risk_score=-10.0
            )
        
        # Invalid score - too high
        with pytest.raises(ValidationError):
            ComplianceAssessment(
                system_name="Test",
                risk_tier=RiskTier.MINIMAL_RISK,
                risk_score=150.0
            )
    
    def test_risk_score_at_boundaries(self):
        """Test risk scores at exact boundary values."""
        # Score 0
        assessment_zero = ComplianceAssessment(
            system_name="Zero Risk",
            risk_tier=RiskTier.MINIMAL_RISK,
            risk_score=0.0
        )
        assert assessment_zero.risk_score == 0.0
        
        # Score 100
        assessment_max = ComplianceAssessment(
            system_name="Max Risk",
            risk_tier=RiskTier.PROHIBITED,
            risk_score=100.0
        )
        assert assessment_max.risk_score == 100.0
    
    def test_optional_fields_defaults(self):
        """Test that optional fields have proper defaults."""
        assessment = ComplianceAssessment(
            system_name="Minimal Assessment",
            risk_tier=RiskTier.MINIMAL_RISK,
            risk_score=15.0
        )
        
        assert assessment.relevant_articles == []
        assert assessment.compliance_gaps == []
    
    def test_risk_tier_score_consistency_prohibited(self):
        """Test prohibited risk tier with appropriate score."""
        assessment = ComplianceAssessment(
            system_name="Prohibited System",
            risk_tier=RiskTier.PROHIBITED,
            risk_score=95.0
        )
        
        assert assessment.risk_tier == RiskTier.PROHIBITED
        assert assessment.risk_score >= 85
    
    def test_risk_tier_score_consistency_high_risk(self):
        """Test high risk tier with appropriate score."""
        assessment = ComplianceAssessment(
            system_name="High Risk System",
            risk_tier=RiskTier.HIGH_RISK,
            risk_score=70.0
        )
        
        assert assessment.risk_tier == RiskTier.HIGH_RISK
        assert 55 <= assessment.risk_score < 85
    
    def test_risk_tier_score_consistency_limited_risk(self):
        """Test limited risk tier with appropriate score."""
        assessment = ComplianceAssessment(
            system_name="Limited Risk System",
            risk_tier=RiskTier.LIMITED_RISK,
            risk_score=40.0
        )
        
        assert assessment.risk_tier == RiskTier.LIMITED_RISK
        assert 25 <= assessment.risk_score < 55
    
    def test_risk_tier_score_consistency_minimal_risk(self):
        """Test minimal risk tier with appropriate score."""
        assessment = ComplianceAssessment(
            system_name="Minimal Risk System",
            risk_tier=RiskTier.MINIMAL_RISK,
            risk_score=15.0
        )
        
        assert assessment.risk_tier == RiskTier.MINIMAL_RISK
        assert assessment.risk_score < 25


class TestModelSerialization:
    """Test suite for model serialization and deserialization."""
    
    def test_profile_to_dict(self):
        """Test converting AISystemProfile to dictionary."""
        profile = AISystemProfile(
            system_name="Test",
            use_case="Testing",
            data_types=["test_data"],
            decision_impact="moderate",
            affected_groups="Users",
            autonomous_decision=True,
            human_oversight=False,
            error_consequences="Error"
        )
        
        profile_dict = profile.model_dump()
        
        assert profile_dict["system_name"] == "Test"
        assert profile_dict["autonomous_decision"] is True
        assert isinstance(profile_dict["data_types"], list)
    
    def test_assessment_to_dict(self):
        """Test converting ComplianceAssessment to dictionary."""
        assessment = ComplianceAssessment(
            system_name="Test System",
            risk_tier=RiskTier.HIGH_RISK,
            risk_score=75.0,
            relevant_articles=["Article 5"]
        )
        
        assessment_dict = assessment.model_dump()
        
        assert assessment_dict["risk_tier"] == "high_risk"
        assert assessment_dict["risk_score"] == 75.0
        assert isinstance(assessment_dict["relevant_articles"], list)
    
    def test_assessment_from_dict(self):
        """Test creating ComplianceAssessment from dictionary."""
        data = {
            "system_name": "Test",
            "risk_tier": "limited_risk",
            "risk_score": 40.0,
            "relevant_articles": ["Article 52"],
            "compliance_gaps": ["Gap 1"]
        }
        
        assessment = ComplianceAssessment(**data)
        
        assert assessment.risk_tier == RiskTier.LIMITED_RISK
        assert assessment.risk_score == 40.0
    
    def test_risk_tier_json_serialization(self):
        """Test that RiskTier serializes to string in JSON."""
        assessment = ComplianceAssessment(
            system_name="Test",
            risk_tier=RiskTier.PROHIBITED,
            risk_score=95.0
        )
        
        json_data = assessment.model_dump_json()
        
        assert '"risk_tier":"prohibited"' in json_data or '"risk_tier": "prohibited"' in json_data


if __name__ == "__main__":
    # Generate test documentation JSON
    from test_utils import generate_test_documentation, save_test_documentation
    
    test_classes = [
        TestRiskTierEnum,
        TestAISystemProfile,
        TestComplianceAssessment,
        TestModelSerialization
    ]
    
    docs = generate_test_documentation(__file__, test_classes)
    json_path = save_test_documentation(docs)
    print(f"\n✅ Test documentation generated: {json_path}\n")
    
    # Run tests
    pytest.main([__file__, "-v"])
