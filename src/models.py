"""Data models for EU AI Act Compliance Agent."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    """EU AI Act risk classifications."""

    PROHIBITED = "prohibited"
    HIGH_RISK = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"


class AISystemProfile(BaseModel):
    """Profile of an AI system to assess."""

    system_name: str = Field(..., description="Name of the AI system")
    use_case: str = Field(..., description="Description of the use case")
    data_types: List[str] = Field(..., description="Types of data processed")
    decision_impact: str = Field(
        ..., description="Impact level: significant/moderate/minimal"
    )
    affected_groups: str = Field(
        ..., description="Groups affected by the AI system"
    )
    autonomous_decision: bool = Field(
        ..., description="Whether system makes autonomous decisions"
    )
    human_oversight: bool = Field(
        ..., description="Whether human can override decisions"
    )
    error_consequences: str = Field(
        ..., description="Consequences of errors"
    )


class ComplianceAssessment(BaseModel):
    """Compliance assessment result."""

    system_name: str
    risk_tier: RiskTier
    risk_score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    relevant_articles: List[str] = Field(
        default_factory=list, description="Relevant EU AI Act articles"
    )
    compliance_gaps: List[str] = Field(
        default_factory=list, description="Identified compliance gaps"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for compliance"
    )
    confidence_score: float = Field(
        default=0.5, ge=0, le=1.0, description="Confidence in assessment 0-1"
    )
    supporting_evidence: str = Field(
        default="", description="Evidence and reasoning"
    )


class SessionState(BaseModel):
    """State of a user session."""

    session_id: str
    user_input: str
    conversation_history: List[dict] = Field(default_factory=list)
    current_profile: Optional[AISystemProfile] = None
    assessment_results: List[ComplianceAssessment] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
