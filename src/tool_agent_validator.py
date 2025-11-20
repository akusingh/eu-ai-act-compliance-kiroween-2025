"""Tool-Agent Validation Layer for Observability and Transparency.

This module tracks when agents override tool outputs and provides reasoning transparency.
It demonstrates sophisticated agent behavior - not blindly following tools, but applying
contextual legal reasoning while maintaining full observability.
"""

import logging
from typing import Dict, Any, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class ToolAgentValidator:
    """Validates and tracks discrepancies between tool outputs and agent decisions.
    
    This enables:
    1. Full observability of agent decision-making
    2. Transparency when agents apply higher-order reasoning
    3. Metrics for both tool accuracy and agent reasoning quality
    """
    
    def __init__(self):
        self.validations = []
        self.tool_agent_discrepancies = []
    
    def validate_classification(
        self,
        tool_output: Dict[str, Any],
        agent_output: Dict[str, Any],
        system_name: str,
        legal_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compare tool and agent outputs, flag significant discrepancies.
        
        Args:
            tool_output: Raw output from ComplianceScoringTool
            agent_output: Final classification from ComplianceClassifier agent
            system_name: Name of AI system being assessed
            legal_context: Optional legal analysis that informed agent decision
            
        Returns:
            Validation result with transparency metrics
        """
        # Extract values
        tool_score = tool_output.get('score', 0)
        tool_tier = tool_output.get('classification', 'unknown')
        
        agent_score = agent_output.get('score', 0)
        agent_tier = agent_output.get('tier', 'unknown')
        
        # Calculate discrepancy
        score_diff = abs(agent_score - tool_score)
        tier_match = tool_tier.lower() == agent_tier.lower()
        
        # Determine if this is a significant discrepancy (>15 points)
        is_significant = score_diff > 15
        
        # Categorize agent behavior
        if score_diff == 0 and tier_match:
            behavior = "EXACT_MATCH"
            reasoning = "Agent agreed with tool assessment"
        elif score_diff <= 15 and tier_match:
            behavior = "MINOR_ADJUSTMENT"
            reasoning = "Agent made minor score adjustment within same risk tier"
        elif tier_match:
            behavior = "INTRA_TIER_ADJUSTMENT"
            reasoning = f"Agent adjusted score by {score_diff} points but maintained {tool_tier} classification"
        else:
            behavior = "TIER_OVERRIDE"
            reasoning = f"Agent applied contextual reasoning to reclassify from {tool_tier} to {agent_tier}"
        
        validation_result = {
            "system_name": system_name,
            "tool_output": {
                "score": tool_score,
                "tier": tool_tier
            },
            "agent_output": {
                "score": agent_score,
                "tier": agent_tier
            },
            "discrepancy": {
                "score_difference": score_diff,
                "tier_match": tier_match,
                "is_significant": is_significant,
                "behavior_type": behavior
            },
            "transparency": {
                "reasoning": reasoning,
                "legal_context_considered": legal_context is not None
            }
        }
        
        # Log significant discrepancies
        if is_significant:
            logger.warning("="*80)
            logger.warning("⚠️  TOOL-AGENT DISCREPANCY DETECTED")
            logger.warning("="*80)
            logger.warning(f"System: {system_name}")
            logger.warning(f"Tool Assessment: {tool_tier} (score: {tool_score})")
            logger.warning(f"Agent Decision: {agent_tier} (score: {agent_score})")
            logger.warning(f"Difference: {score_diff} points")
            logger.warning(f"Behavior: {behavior}")
            logger.warning(f"Reasoning: {reasoning}")
            logger.warning("="*80)
            
            self.tool_agent_discrepancies.append(validation_result)
        else:
            logger.info(f"✅ Tool-Agent Alignment: {system_name} - {behavior}")
        
        # Store validation
        self.validations.append(validation_result)
        
        return validation_result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Calculate metrics for tool accuracy and agent reasoning quality.
        
        Returns:
            Dictionary with accuracy metrics and reasoning quality scores
        """
        if not self.validations:
            return {
                "total_assessments": 0,
                "tool_accuracy": 0.0,
                "agent_reasoning_quality": 0.0,
                "combined_score": 0.0
            }
        
        total = len(self.validations)
        
        # Tool accuracy: % where tool tier was correct (based on final expected)
        # Agent reasoning quality: weighted score based on behavior type
        exact_matches = sum(1 for v in self.validations if v['discrepancy']['behavior_type'] == 'EXACT_MATCH')
        minor_adjustments = sum(1 for v in self.validations if v['discrepancy']['behavior_type'] == 'MINOR_ADJUSTMENT')
        intra_tier = sum(1 for v in self.validations if v['discrepancy']['behavior_type'] == 'INTRA_TIER_ADJUSTMENT')
        tier_overrides = sum(1 for v in self.validations if v['discrepancy']['behavior_type'] == 'TIER_OVERRIDE')
        
        # Agent reasoning quality (weighted)
        # EXACT_MATCH: 1.0 (perfect agreement)
        # MINOR_ADJUSTMENT: 0.9 (thoughtful refinement)
        # INTRA_TIER_ADJUSTMENT: 0.7 (kept tier, adjusted score)
        # TIER_OVERRIDE: 0.5 (could be good or bad, depends on context)
        reasoning_quality = (
            (exact_matches * 1.0) +
            (minor_adjustments * 0.9) +
            (intra_tier * 0.7) +
            (tier_overrides * 0.5)
        ) / total
        
        # Tier match rate (tool was in right tier)
        tier_matches = sum(1 for v in self.validations if v['discrepancy']['tier_match'])
        tool_accuracy = tier_matches / total
        
        # Combined score: 70% tool correctness + 30% agent reasoning
        combined_score = (tool_accuracy * 0.7) + (reasoning_quality * 0.3)
        
        return {
            "total_assessments": total,
            "tool_accuracy": tool_accuracy,
            "agent_reasoning_quality": reasoning_quality,
            "combined_score": combined_score,
            "behavior_distribution": {
                "exact_match": exact_matches,
                "minor_adjustment": minor_adjustments,
                "intra_tier_adjustment": intra_tier,
                "tier_override": tier_overrides
            },
            "significant_discrepancies": len(self.tool_agent_discrepancies)
        }
    
    def get_discrepancy_report(self) -> str:
        """Generate human-readable report of tool-agent discrepancies.
        
        Returns:
            Formatted report string
        """
        if not self.tool_agent_discrepancies:
            return "✅ No significant tool-agent discrepancies detected."
        
        report = []
        report.append("\n" + "="*80)
        report.append("🔍 TOOL-AGENT DISCREPANCY ANALYSIS")
        report.append("="*80)
        report.append(f"\nTotal Significant Discrepancies: {len(self.tool_agent_discrepancies)}\n")
        
        for i, disc in enumerate(self.tool_agent_discrepancies, 1):
            report.append(f"\n{i}. {disc['system_name']}")
            report.append(f"   Tool: {disc['tool_output']['tier']} (score: {disc['tool_output']['score']})")
            report.append(f"   Agent: {disc['agent_output']['tier']} (score: {disc['agent_output']['score']})")
            report.append(f"   Difference: {disc['discrepancy']['score_difference']} points")
            report.append(f"   Reasoning: {disc['transparency']['reasoning']}")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)
    
    def export_validations(self, filepath: str):
        """Export all validations to JSON file for analysis.
        
        Args:
            filepath: Path to output JSON file
        """
        with open(filepath, 'w') as f:
            json.dump({
                "validations": self.validations,
                "metrics": self.get_metrics(),
                "discrepancy_count": len(self.tool_agent_discrepancies)
            }, f, indent=2)
        
        logger.info(f"Validation results exported to: {filepath}")
