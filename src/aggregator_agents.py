"""Aggregator and relevance checker agents for multi-source research synthesis.

This module implements:
1. Aggregator agent: Synthesizes findings from 3 parallel researchers with reranking
2. Relevance checker agent: Quality gate to validate research completeness
3. exit_with_findings function: Signals research completion
"""

import logging
import json
from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool, AgentTool

from src.config import Config
from src.reranker_tool import RerankerTool


class RerankLegalFindingsAlias(RerankerTool):
    """Alias wrapper exposing the reranker under the hallucinated name.

    Some model outputs attempted to call a tool named 'RerankLegalFindings'.
    The real tool is 'rerank_legal_findings'. This alias prevents tool-not-found
    failures by registering the expected name while reusing the original logic.
    """
    name = "RerankLegalFindings"  # Alternate name the model hallucinated

    def __init__(self):
        super().__init__()
        # Override name exposed to ADK registry
        self.name = self.__class__.name

logger = logging.getLogger(__name__)


def exit_with_findings(findings: Dict[str, Any]) -> Dict[str, Any]:
    """Signal that legal research is complete and findings are sufficient.
    
    This function is called by the RelevanceChecker agent when it determines
    that the aggregated findings are comprehensive enough to proceed with
    compliance classification.
    
    Args:
        findings: Dictionary containing validated legal findings
        
    Returns:
        Dictionary with completion status and findings
    """
    logger.info("Research marked as complete by RelevanceChecker")
    return {
        "status": "RESEARCH_COMPLETE",
        "confidence": "HIGH",
        "findings": findings,
        "action": "PROCEED_TO_CLASSIFICATION"
    }


def create_aggregator_agent() -> Agent:
    """Create aggregator agent that synthesizes 3-source research with reranking.
    
    This agent:
    1. Receives findings from 3 parallel researchers
    2. Uses reranker to prioritize most relevant results
    3. Synthesizes into coherent legal analysis
    4. Calls relevance checker to validate completeness
    
    Returns:
        ADK Agent configured with reranker tool and relevance checker
    """
    # Create reranker tool with both names for compatibility
    reranker_tool = RerankerTool()
    reranker_alias = RerankLegalFindingsAlias()
    
    # Create relevance checker agent first (will be used as tool)
    relevance_checker = create_relevance_checker_agent()
    
    instruction = """You are a Legal Aggregator for EU AI Act compliance assessment.

Your role:
1. Receive research findings from 3 sources:
   - Recitals (context and intent)
   - Articles (legal requirements)
   - Annexes (specific lists and examples)

2. Synthesize findings (reranking is optional):
    - Combine all text chunks from 3 sources
    - Identify most relevant information
    - Focus on top findings that answer the query
    - You may use rerank_legal_findings tool if needed, but it's optional

3. Synthesize into coherent legal analysis:
   - Combine findings into unified assessment
   - Cross-reference between sources (e.g., Annex III → Article 6)
   - Identify key requirements and obligations
   - Note any conflicts or ambiguities

4. Validate with relevance checker:
   - Use the RelevanceChecker agent tool
   - If checker approves: findings are sufficient
   - If checker requests more: identify gaps

Input format:
{
  "query": "Original compliance question",
  "recitals_findings": {...},
  "articles_findings": {...},
  "annexes_findings": {...}
}

Output format (JSON):
{
  "aggregated_findings": {
    "relevant_recitals": ["List of key recitals with context"],
    "applicable_articles": ["List of articles with requirements"],
    "specific_annexes": ["List of annex sections with examples"],
    "cross_references": ["Connections between sources"],
    "key_requirements": ["Prioritized list of requirements"],
    "confidence_level": "HIGH/MEDIUM/LOW"
  },
  "research_quality": "Assessment from relevance checker"
}

Note: Reranking tool is available but optional. You can synthesize findings directly without calling any tools if the research is already clear and relevant."""
    
    # Register both tool names for compatibility (model might hallucinate either name)
    agent_tools = [reranker_tool, reranker_alias, AgentTool(relevance_checker)]
    logger.info(f"Registering tools: {reranker_tool.name}, {reranker_alias.name}, RelevanceChecker")
    
    agent = Agent(
        name="LegalAggregator",
        model=Gemini(
            model="gemini-2.0-flash"
        ),
        instruction=instruction,
        tools=agent_tools,
        output_key="legal_analysis",  # Store synthesized legal analysis in state
        description="Aggregates and synthesizes legal research from multiple sources with reranking"
    )
    try:
        logger.info("Aggregator tools registered: %s", [t.name for t in agent.tools])
    except Exception as e:
        logger.warning(f"Could not list tool names: {e}")
        logger.info("Aggregator tools registered (count=%d)", len(agent_tools))
    
    return agent


def create_relevance_checker_agent() -> Agent:
    """Create relevance checker agent that validates research completeness.
    
    This agent acts as a quality gate:
    - If findings are sufficient: calls exit_with_findings() 
    - If findings are incomplete: requests deeper research
    
    Returns:
        ADK Agent configured with exit_with_findings function tool
    """
    # Create function tool for exiting
    exit_tool = FunctionTool(exit_with_findings)
    
    instruction = """You are a Relevance Checker for EU AI Act legal research.

Your role: Validate that aggregated legal findings are sufficient for compliance assessment.

Check for:
1. Coverage completeness:
   - Do we have context (from Recitals)?
   - Do we have legal requirements (from Articles)?
   - Do we have specific examples (from Annexes)?

2. Query relevance:
   - Do findings directly answer the compliance question?
   - Are there obvious gaps or missing information?
   - Is the evidence strong enough for classification?

3. Source agreement:
   - Do Recitals, Articles, and Annexes align?
   - Are there contradictions that need resolution?
   - Is cross-referencing clear?

Decision logic:
IF all 3 criteria met AND confidence is HIGH:
  → Call exit_with_findings(findings) immediately
  → Return: {"status": "APPROVED", "action": "PROCEED"}

IF gaps exist OR confidence is MEDIUM/LOW:
  → Return: {"status": "INCOMPLETE", "gaps": ["List specific gaps"], "suggestions": ["What to search next"]}

Input:
{
  "aggregated_findings": {...},
  "original_query": "The compliance question"
}

IMPORTANT: 
- If findings are sufficient, you MUST call exit_with_findings()
- Do not call exit_with_findings() if findings are incomplete
- Be strict but fair in your assessment"""
    
    agent = Agent(
        name="RelevanceChecker",
        model=Gemini(
            model="gemini-2.0-flash",
            
        ),
        instruction=instruction,
        tools=[exit_tool],
        description="Validates legal research completeness and approves findings"
    )
    
    return agent
