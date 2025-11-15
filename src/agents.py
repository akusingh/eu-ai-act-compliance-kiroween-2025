"""Agent implementations for EU AI Act Compliance Assessment."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.models import AISystemProfile, ComplianceAssessment, RiskTier
from src.observability import metrics_collector, trace_collector


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, name: str):
        """Initialize agent with name.
        
        Args:
            name: Unique name for the agent
        """
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Execute agent logic.
        
        Args:
            input_data: Input to process
            
        Returns:
            Output from agent execution
        """
        pass

    def _record_trace(
        self,
        action: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error: Optional[str] = None,
    ) -> None:
        """Record execution trace for observability.
        
        Args:
            action: Description of action performed
            input_data: Input data provided to agent
            output_data: Output data produced by agent
            status: Execution status (success/error)
            error: Error message if applicable
        """
        trace_collector.record_trace(
            agent_name=self.name,
            action=action,
            input_data=input_data,
            output_data=output_data,
            status=status,
            error=error,
        )


class InformationGathererAgent(BaseAgent):
    """Gathers and validates AI system information."""

    def __init__(self):
        """Initialize Information Gatherer Agent."""
        super().__init__(name="InformationGatherer")

    def execute(self, system_info: Dict[str, Any]) -> AISystemProfile:
        """Process system information and create profile.
        
        Args:
            system_info: Dictionary with AI system details
            
        Returns:
            AISystemProfile instance
            
        Raises:
            ValueError: If required fields are missing
        """
        try:
            self.logger.info(f"Processing system info for: {system_info.get('system_name', 'Unknown')}")
            
            # Validate and create profile
            profile = AISystemProfile(
                system_name=system_info.get("system_name", ""),
                use_case=system_info.get("use_case", ""),
                data_types=system_info.get("data_types", []),
                decision_impact=system_info.get("decision_impact", "minimal"),
                affected_groups=system_info.get("affected_groups", ""),
                autonomous_decision=system_info.get("autonomous_decision", False),
                human_oversight=system_info.get("human_oversight", False),
                error_consequences=system_info.get("error_consequences", ""),
            )
            
            # Record trace
            self._record_trace(
                action="validate_and_create_profile",
                input_data=system_info,
                output_data=profile.dict(),
                status="success",
            )
            
            self.logger.info(f"Profile created: {profile.system_name}")
            metrics_collector.record_metric(
                "profile_created",
                1,
                tags={"system": profile.system_name},
            )
            
            return profile
            
        except Exception as e:
            error_msg = f"Failed to create profile: {str(e)}"
            self.logger.error(error_msg)
            self._record_trace(
                action="validate_and_create_profile",
                input_data=system_info,
                status="error",
                error=error_msg,
            )
            raise


class ComplianceClassifierAgent(BaseAgent):
    """Classifies AI systems against EU AI Act risk tiers."""

    def __init__(self):
        """Initialize Compliance Classifier Agent."""
        super().__init__(name="ComplianceClassifier")
        self.risk_factors = self._load_risk_factors()

    def _load_risk_factors(self) -> Dict[str, Dict[str, Any]]:
        """Load EU AI Act risk classification factors.
        
        Returns:
            Dictionary mapping risk tiers to criteria
        """
        return {
            "prohibited": {
                "criteria": [
                    "Facial recognition for mass surveillance",
                    "Social credit scoring",
                    "Emotion recognition for law enforcement",
                    "Manipulative AI for vulnerable groups",
                ],
                "articles": ["Article 5"],
            },
            "high_risk": {
                "criteria": [
                    "Creditworthiness assessment",
                    "Employment decisions",
                    "Law enforcement operations",
                    "Critical infrastructure",
                    "Educational access",
                    "Healthcare decisions",
                ],
                "articles": ["Article 6"],
            },
            "limited_risk": {
                "criteria": [
                    "Chatbots and conversational AI",
                    "Deep fakes and synthetic content",
                    "Recommender systems",
                ],
                "articles": ["Article 52"],
            },
            "minimal_risk": {
                "criteria": [
                    "General machine learning models",
                    "Data analytics",
                    "Personalized recommendations (low impact)",
                ],
                "articles": ["Article 1"],
            },
        }

    def execute(self, profile: AISystemProfile) -> ComplianceAssessment:
        """Classify AI system risk tier and generate assessment.
        
        Args:
            profile: AISystemProfile to classify
            
        Returns:
            ComplianceAssessment with risk classification
        """
        try:
            self.logger.info(f"Classifying system: {profile.system_name}")
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(profile)
            risk_tier = self._determine_risk_tier(risk_score)
            
            # Identify relevant articles and gaps
            relevant_articles = self._get_relevant_articles(risk_tier)
            compliance_gaps = self._identify_gaps(profile, risk_tier)
            recommendations = self._generate_recommendations(profile, risk_tier)
            
            # Create assessment
            assessment = ComplianceAssessment(
                system_name=profile.system_name,
                risk_tier=risk_tier,
                risk_score=risk_score,
                relevant_articles=relevant_articles,
                compliance_gaps=compliance_gaps,
                recommendations=recommendations,
                confidence_score=self._calculate_confidence(profile),
                supporting_evidence=self._generate_evidence(profile, risk_tier),
            )
            
            # Record trace
            self._record_trace(
                action="classify_system",
                input_data=profile.dict(),
                output_data={
                    "risk_tier": risk_tier,
                    "risk_score": risk_score,
                },
                status="success",
            )
            
            metrics_collector.record_metric(
                "classification_completed",
                1,
                tags={"risk_tier": risk_tier, "system": profile.system_name},
            )
            
            return assessment
            
        except Exception as e:
            error_msg = f"Classification failed: {str(e)}"
            self.logger.error(error_msg)
            self._record_trace(
                action="classify_system",
                input_data=profile.dict(),
                status="error",
                error=error_msg,
            )
            raise

    def _calculate_risk_score(self, profile: AISystemProfile) -> float:
        """Calculate risk score 0-100 based on profile factors.
        
        Args:
            profile: System profile to score
            
        Returns:
            Risk score between 0 and 100
        """
        score = 0.0
        
        # Decision impact (0-30 points)
        impact_scores = {
            "significant": 30,
            "moderate": 15,
            "minimal": 5,
        }
        score += impact_scores.get(profile.decision_impact, 5)
        
        # Autonomous decision (0-25 points)
        if profile.autonomous_decision:
            score += 25
        
        # Human oversight (reduces score -15 points)
        if profile.human_oversight:
            score -= 15
        
        # Personal/sensitive data (0-20 points)
        sensitive_data = [
            "biometric", "health", "financial", "personal_data",
            "genetic", "criminal", "location"
        ]
        sensitive_count = sum(1 for dt in profile.data_types if any(s in dt.lower() for s in sensitive_data))
        score += min(20, sensitive_count * 5)
        
        # Error consequences (0-20 points)
        if "severe" in profile.error_consequences.lower():
            score += 20
        elif "moderate" in profile.error_consequences.lower():
            score += 10
        
        # Clamp score between 0-100
        return max(0, min(100, score))

    def _determine_risk_tier(self, score: float) -> RiskTier:
        """Determine risk tier from score.
        
        Args:
            score: Risk score 0-100
            
        Returns:
            RiskTier classification
        """
        if score >= 80:
            return RiskTier.PROHIBITED
        elif score >= 60:
            return RiskTier.HIGH_RISK
        elif score >= 30:
            return RiskTier.LIMITED_RISK
        else:
            return RiskTier.MINIMAL_RISK

    def _get_relevant_articles(self, tier: RiskTier) -> list:
        """Get relevant EU AI Act articles for risk tier.
        
        Args:
            tier: Risk tier classification
            
        Returns:
            List of relevant article references
        """
        articles_map = {
            RiskTier.PROHIBITED: ["Article 5 - Prohibited AI Practices"],
            RiskTier.HIGH_RISK: [
                "Article 6 - Classification as High-Risk",
                "Article 8 - Risk Assessment",
                "Article 9 - Risk Mitigation Measures",
            ],
            RiskTier.LIMITED_RISK: [
                "Article 52 - Transparency Requirements",
                "Article 53 - Disclosure to Users",
            ],
            RiskTier.MINIMAL_RISK: [
                "Article 1 - General Provisions",
            ],
        }
        return articles_map.get(tier, [])

    def _identify_gaps(self, profile: AISystemProfile, tier: RiskTier) -> list:
        """Identify compliance gaps for the system.
        
        Args:
            profile: System profile
            tier: Risk classification
            
        Returns:
            List of identified compliance gaps
        """
        gaps = []
        
        if tier in [RiskTier.HIGH_RISK, RiskTier.PROHIBITED]:
            if not profile.human_oversight:
                gaps.append("No human oversight mechanism identified")
            
            if not profile.affected_groups:
                gaps.append("Affected groups not clearly defined")
        
        if profile.autonomous_decision and not profile.human_oversight:
            gaps.append("Autonomous decisions require human review mechanism")
        
        if profile.decision_impact == "significant" and len(profile.data_types) == 0:
            gaps.append("Significant impact system with undefined data types")
        
        return gaps

    def _generate_recommendations(self, profile: AISystemProfile, tier: RiskTier) -> list:
        """Generate compliance recommendations.
        
        Args:
            profile: System profile
            tier: Risk classification
            
        Returns:
            List of compliance recommendations
        """
        recommendations = []
        
        if tier == RiskTier.PROHIBITED:
            recommendations.append("This system contains prohibited practices and cannot be deployed under EU AI Act")
            recommendations.append("Consider redesigning the system to remove prohibited elements")
        
        elif tier == RiskTier.HIGH_RISK:
            recommendations.append("Implement comprehensive risk assessment (Article 8)")
            recommendations.append("Establish human oversight and decision review process")
            recommendations.append("Create impact assessment documentation")
            recommendations.append("Implement continuous monitoring and logging")
            recommendations.append("Maintain audit trails for all decisions")
        
        elif tier == RiskTier.LIMITED_RISK:
            recommendations.append("Implement transparency measures (Article 52)")
            recommendations.append("Disclose to users that they interact with AI")
            recommendations.append("Document AI decision logic")
        
        else:  # MINIMAL_RISK
            recommendations.append("Standard compliance documentation recommended")
            recommendations.append("Consider transparency best practices")
        
        # General recommendations
        if profile.autonomous_decision:
            recommendations.append("Establish clear appeal/redress mechanism for users")
        
        return recommendations

    def _calculate_confidence(self, profile: AISystemProfile) -> float:
        """Calculate confidence in classification.
        
        Args:
            profile: System profile
            
        Returns:
            Confidence score 0-1
        """
        confidence = 0.8
        
        # Reduce confidence if key fields are empty
        if not profile.affected_groups:
            confidence -= 0.1
        
        if not profile.data_types:
            confidence -= 0.1
        
        if not profile.use_case:
            confidence -= 0.1
        
        return max(0.3, min(1.0, confidence))

    def _generate_evidence(self, profile: AISystemProfile, tier: RiskTier) -> str:
        """Generate evidence string explaining classification.
        
        Args:
            profile: System profile
            tier: Risk classification
            
        Returns:
            Evidence explanation
        """
        evidence = f"Classified as {tier.value.replace('_', ' ').title()}\n"
        evidence += f"Decision Impact: {profile.decision_impact}\n"
        evidence += f"Autonomous Decision: {'Yes' if profile.autonomous_decision else 'No'}\n"
        evidence += f"Human Oversight: {'Yes' if profile.human_oversight else 'No'}\n"
        evidence += f"Data Types Processed: {', '.join(profile.data_types) if profile.data_types else 'Unspecified'}\n"
        return evidence


class ReportGeneratorAgent(BaseAgent):
    """Generates compliance reports from assessments."""

    def __init__(self):
        """Initialize Report Generator Agent."""
        super().__init__(name="ReportGenerator")

    def execute(self, assessment: ComplianceAssessment) -> Dict[str, Any]:
        """Generate compliance report from assessment.
        
        Args:
            assessment: ComplianceAssessment to report on
            
        Returns:
            Dictionary with formatted report data
        """
        try:
            self.logger.info(f"Generating report for: {assessment.system_name}")
            
            report = {
                "title": f"EU AI Act Compliance Assessment: {assessment.system_name}",
                "risk_classification": assessment.risk_tier.value,
                "risk_score": assessment.risk_score,
                "confidence": assessment.confidence_score,
                "relevant_articles": assessment.relevant_articles,
                "compliance_gaps": assessment.compliance_gaps,
                "recommendations": assessment.recommendations,
                "supporting_evidence": assessment.supporting_evidence,
            }
            
            # Record trace
            self._record_trace(
                action="generate_report",
                input_data=assessment.dict(),
                output_data=report,
                status="success",
            )
            
            metrics_collector.record_metric(
                "report_generated",
                1,
                tags={"system": assessment.system_name},
            )
            
            return report
            
        except Exception as e:
            error_msg = f"Report generation failed: {str(e)}"
            self.logger.error(error_msg)
            self._record_trace(
                action="generate_report",
                input_data=assessment.dict(),
                status="error",
                error=error_msg,
            )
            raise
