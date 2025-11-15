"""Agent orchestrator for managing sequential workflow execution."""

import logging
from typing import Any, Dict, Optional

from src.agents import (
    InformationGathererAgent,
    ComplianceClassifierAgent,
    ReportGeneratorAgent,
)
from src.models import AISystemProfile, ComplianceAssessment
from src.observability import metrics_collector, trace_collector


logger = logging.getLogger(__name__)


class ComplianceOrchestrator:
    """Orchestrates sequential execution of compliance assessment agents."""

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.information_gatherer = InformationGathererAgent()
        self.classifier = ComplianceClassifierAgent()
        self.report_generator = ReportGeneratorAgent()
        
        self.last_profile: Optional[AISystemProfile] = None
        self.last_assessment: Optional[ComplianceAssessment] = None
        self.last_report: Optional[Dict[str, Any]] = None

    def assess_system(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full compliance assessment workflow.
        
        This method orchestrates the sequential execution of:
        1. Information Gatherer: Validates and creates system profile
        2. Compliance Classifier: Classifies risk tier and identifies gaps
        3. Report Generator: Creates formatted compliance report
        
        Args:
            system_info: Dictionary containing AI system details
            
        Returns:
            Dictionary with complete compliance assessment and report
            
        Raises:
            ValueError: If assessment workflow fails
        """
        metrics_collector.start_timer()
        
        try:
            logger.info("Starting compliance assessment workflow")
            trace_collector.record_trace(
                agent_name="Orchestrator",
                action="start_assessment",
                input_data=system_info,
                status="started",
            )
            
            # Step 1: Gather and validate system information
            logger.info("Step 1: Gathering system information")
            self.last_profile = self.information_gatherer.execute(system_info)
            
            # Step 2: Classify compliance risk
            logger.info("Step 2: Classifying compliance risk")
            self.last_assessment = self.classifier.execute(self.last_profile)
            
            # Step 3: Generate report
            logger.info("Step 3: Generating compliance report")
            self.last_report = self.report_generator.execute(self.last_assessment)
            
            # Compile complete result
            result = {
                "profile": self.last_profile.dict(),
                "assessment": self.last_assessment.dict(),
                "report": self.last_report,
            }
            
            trace_collector.record_trace(
                agent_name="Orchestrator",
                action="complete_assessment",
                output_data=result,
                status="success",
            )
            
            metrics_collector.record_metric(
                "assessment_completed",
                1,
                tags={"system": self.last_profile.system_name},
            )
            
            logger.info(f"Assessment completed for: {self.last_profile.system_name}")
            
            return result
            
        except Exception as e:
            error_msg = f"Assessment workflow failed: {str(e)}"
            logger.error(error_msg)
            trace_collector.record_trace(
                agent_name="Orchestrator",
                action="assessment_failed",
                input_data=system_info,
                status="error",
                error=error_msg,
            )
            raise ValueError(error_msg) from e

    def get_last_report(self) -> Optional[Dict[str, Any]]:
        """Get the last generated report.
        
        Returns:
            Last report dictionary or None if no assessment completed
        """
        return self.last_report

    def get_last_assessment(self) -> Optional[ComplianceAssessment]:
        """Get the last compliance assessment.
        
        Returns:
            Last ComplianceAssessment or None if no assessment completed
        """
        return self.last_assessment

    def get_last_profile(self) -> Optional[AISystemProfile]:
        """Get the last system profile.
        
        Returns:
            Last AISystemProfile or None if no assessment completed
        """
        return self.last_profile
