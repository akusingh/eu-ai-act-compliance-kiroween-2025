"""SequentialAgent-based orchestrator for EU AI Act compliance assessment.

This replaces the manual orchestrator with ADK's SequentialAgent for cleaner
state management using output_key. The pipeline:

1. InformationGatherer → output_key="profile"
2. ParallelResearchTeam → output_key="research_findings"  
3. LegalAggregator → output_key="legal_analysis"
4. ComplianceClassifier → output_key="assessment"
5. ReportGenerator → output_key="report"
"""

import logging
from typing import Dict, Any

from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
import google.generativeai as genai

from src.config import Config

# Configure Gemini API globally for ADK
if Config.GOOGLE_GENAI_API_KEY:
    genai.configure(api_key=Config.GOOGLE_GENAI_API_KEY)
from src.parallel_research_agents import create_parallel_research_team
from src.aggregator_agents import create_aggregator_agent
from src.tools_adk import ComplianceScoringTool

logger = logging.getLogger(__name__)


def create_information_gatherer() -> Agent:
    """Create Information Gatherer with output_key for state management."""
    
    instruction = """You are an Information Gatherer Agent for EU AI Act compliance assessment.

Your role is to:
1. Validate that all required information about an AI system is provided
2. Structure the information into a standardized format
3. Flag any missing or unclear information

Required fields to validate:
- system_name: Name of the AI system
- use_case: Detailed description of what the system does
- data_types: List of data types the system processes (e.g., personal_data, biometric, financial)
- decision_impact: Level of impact (significant/moderate/minimal)
- affected_groups: Who is affected by the system's decisions
- autonomous_decision: Whether the system makes autonomous decisions (true/false)
- human_oversight: Whether humans can override decisions (true/false)
- error_consequences: What happens if the system makes an error

If any information is missing, ask clarifying questions.
If all information is present, output a JSON object with the validated information.

Format your response as JSON with these exact fields."""

    agent = Agent(
        name="InformationGatherer",
        model=Gemini(
            model="gemini-2.0-flash"
        ),
        instruction=instruction,
        output_key="profile",  # Stored in state for next agents
        description="Validates and structures AI system information for compliance assessment"
    )
    
    return agent


def create_compliance_classifier() -> Agent:
    """Create Compliance Classifier that uses aggregated legal analysis."""
    
    # Create compliance scoring tool
    compliance_tool = ComplianceScoringTool()
    
    instruction = """You are a Compliance Classifier Agent for EU AI Act risk assessment.

WORKFLOW (MUST FOLLOW IN ORDER):
1. Call ComplianceScoringTool with the system information
2. Get the tool's "score" and "classification" output
3. Use those EXACT values - do NOT modify them
4. Reference {legal_analysis} only for article citations and recommendations
5. Reference {profile} only for system description

CRITICAL - SCORING RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE TOOL'S OUTPUT IS FINAL AND CANNOT BE CHANGED:
- Tool returns: {"score": 35, "classification": "limited_risk"}
- You MUST output: {"risk_score": 35, "risk_tier": "limited_risk"}
  
DO NOT:
❌ Override tool classification based on legal analysis keywords
❌ Change score because legal analysis mentions "deepfake" or "biometric"
❌ Recalculate tier from score - use tool's "classification" field directly
❌ Second-guess the tool's context-aware logic

The tool already:
✅ Analyzed EU AI Act requirements
✅ Considered system purpose (detection vs generation)
✅ Evaluated data sensitivity and human oversight
✅ Applied proper risk tier thresholds

Your job: Use tool output + add legal citations + make recommendations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The tool is intelligent and context-aware:
- It knows "deepfake DETECTION" → LIMITED_RISK (transparency obligation)
- It knows "deepfake GENERATION" → HIGH_RISK (manipulative content)  
- It knows "music recommendation" → MINIMAL_RISK (entertainment)
- Trust the tool's judgment!

WORKFLOW EXAMPLE:
1. Call ComplianceScoringTool with system info
2. Tool returns: {"score": 35, "classification": "limited_risk", ...}
3. Your output: {"risk_score": 35, "risk_tier": "limited_risk", ...}
   ↑ Copy these values directly from tool output!

Risk Tiers (ONLY THESE FOUR VALUES ARE VALID):
- "prohibited" (score ≥85): Cannot be deployed (Article 5)
- "high_risk" (score 55-84): Requires strict compliance (Articles 6, 8, 9)
- "limited_risk" (score 25-54): Requires transparency (Articles 52, 53)
- "minimal_risk" (score <25): Standard documentation (Article 1)

IMPORTANT: risk_tier MUST be one of: "prohibited", "high_risk", "limited_risk", "minimal_risk"
Do NOT use: "potentially_high_risk", "moderate_risk", "low_risk" or any other values!

Output Format (JSON):
{
  "risk_score": <copy from tool's "score" field>,
  "risk_tier": <copy from tool's "classification" field - MUST be one of the 4 valid values above>,
  "relevant_articles": [<list from legal_analysis>],
  "compliance_gaps": [<identified gaps>],
  "recommendations": [<actionable recommendations>],
  "confidence": <number 0-1>,
  "reasoning": "<detailed explanation>"
}"""

    agent = Agent(
        name="ComplianceClassifier",
        model=Gemini(
            model="gemini-2.0-flash"
        ),
        instruction=instruction,
        tools=[compliance_tool],
        output_key="assessment",
        description="Classifies AI systems into EU AI Act risk tiers using aggregated legal research"
    )
    
    return agent


def create_report_generator() -> Agent:
    """Create Report Generator that formats final output."""
    
    instruction = """You are a Report Generator Agent for EU AI Act compliance assessments.

Your role:
1. Take the compliance assessment: {assessment}
2. Take the legal analysis: {legal_analysis}
3. Generate a clear, structured compliance report

Report Structure:
1. Executive Summary (2-3 sentences)
   - Overall risk classification
   - Key findings
   - Immediate actions required

2. Risk Classification Details
   - Risk tier and score (MUST use EXACT values from {assessment})
   - Relevant EU AI Act articles
   - Confidence level in assessment

IMPORTANT: When copying risk_classification from {assessment}:
- The "tier" field MUST be exactly: "prohibited", "high_risk", "limited_risk", or "minimal_risk"
- Do NOT create new tier names like "potentially_high_risk" or "moderate_risk"
- Copy the tier value EXACTLY as provided in {assessment}

3. Compliance Gaps Identified
   - List of specific gaps found
   - Severity of each gap
   - Regulatory implications

4. Recommendations
   - Prioritized action items
   - Specific steps to achieve compliance
   - Timeline considerations

5. Supporting Evidence
   - Reasoning behind classification
   - References to EU AI Act (from legal_analysis)
   - Analysis methodology

Output Format (JSON):
{
  "title": "EU AI Act Compliance Assessment: [System Name]",
  "executive_summary": "<2-3 sentence summary>",
  "risk_classification": {
    "tier": "<risk tier>",
    "score": <number>,
    "confidence": <number>,
    "articles": [<list>]
  },
  "compliance_gaps": [<detailed list>],
  "recommendations": [<prioritized list>],
  "supporting_evidence": "<detailed reasoning>",
  "next_steps": [<immediate actions>]
}"""

    agent = Agent(
        name="ReportGenerator",
        model=Gemini(
            model="gemini-2.0-flash"
        ),
        instruction=instruction,
        output_key="report",
        description="Generates structured compliance reports from assessment results"
    )
    
    return agent


def create_compliance_pipeline() -> SequentialAgent:
    """Create full SequentialAgent pipeline for compliance assessment.
    
    Returns:
        SequentialAgent with 5-step workflow
    """
    # Create all agents
    information_gatherer = create_information_gatherer()
    parallel_research = create_parallel_research_team()
    aggregator = create_aggregator_agent()
    classifier = create_compliance_classifier()
    reporter = create_report_generator()
    
    # Wire up sequential pipeline
    pipeline = SequentialAgent(
        name="EUAIActCompliancePipeline",
        sub_agents=[
            information_gatherer,    # → profile
            parallel_research,       # → research_findings (3 sources in parallel)
            aggregator,              # → legal_analysis (reranked + synthesized)
            classifier,              # → assessment (risk classification)
            reporter                 # → report (final output)
        ],
        description="Complete EU AI Act compliance assessment pipeline with parallel multi-source research"
    )
    
    logger.info("Sequential compliance pipeline created with 5 agents")
    return pipeline


class ComplianceOrchestrator:
    """Orchestrator using SequentialAgent for EU AI Act compliance assessment."""
    
    def __init__(self):
        """Initialize orchestrator with SequentialAgent pipeline."""
        logger.info("Initializing SequentialAgent-based Compliance Orchestrator")
        
        self.pipeline = create_compliance_pipeline()
        # Use 'agents' as app_name to match the agent's module path
        self.runner = InMemoryRunner(agent=self.pipeline, app_name="agents")
        
        logger.info("SequentialAgent Compliance Orchestrator initialized successfully")
    
    def assess_system(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full compliance assessment workflow using SequentialAgent.
        
        Args:
            system_info: Dictionary containing AI system details
            
        Returns:
            Dictionary with complete compliance assessment and report
            
        Raises:
            Exception: If assessment workflow fails
        """
        try:
            logger.info("="*80)
            logger.info(f"🚀 STARTING COMPLIANCE ASSESSMENT: {system_info.get('system_name', 'Unknown')}")
            logger.info("="*80)
            logger.info("📋 Architecture: 5-Agent Sequential Pipeline with Parallel Multi-Source Research")
            logger.info("   └─ Agent 1: InformationGatherer")
            logger.info("   └─ Agent 2: ParallelLegalResearchTeam (3 parallel sub-agents)")
            logger.info("        ├─ RecitalsResearcher (Vector + BM25 + RRF)")
            logger.info("        ├─ ArticlesResearcher (Vector + BM25 + RRF)")
            logger.info("        └─ AnnexesResearcher (Vector + BM25 + RRF)")
            logger.info("   └─ Agent 3: LegalAggregator (Cross-source reranking + synthesis)")
            logger.info("   └─ Agent 4: ComplianceClassifier (Risk scoring + classification)")
            logger.info("   └─ Agent 5: ReportGenerator (Final compliance report)")
            logger.info("="*80)
            
            # Run sequential pipeline
            # The pipeline will automatically:
            # 1. Gather info → state["profile"]
            # 2. Parallel research → state["research_findings"]
            # 3. Aggregate → state["legal_analysis"]
            # 4. Classify → state["assessment"]
            # 5. Report → state["report"]
            
            import json
            import asyncio
            
            # Use run_debug for simpler execution (auto-creates sessions)
            # run_debug is async, so we need to run it with asyncio.run()
            # Get or create event loop to avoid "Event loop is closed" error
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            events = loop.run_until_complete(self.runner.run_debug(
                user_messages=f"Assess this AI system for EU AI Act compliance: {json.dumps(system_info)}",
                quiet=True  # Suppress ADK debug output
            ))
            
            logger.info("Compliance assessment completed successfully")
            
            # Extract final content from last event
            final_content = None
            final_state = {}
            
            # Parse events for final content and state
            for event in events:
                # Get the text content from the event
                if hasattr(event, 'content') and event.content:
                    final_content = event.content
                
                # Also try to get state if available
                if hasattr(event, 'state') and event.state:
                    final_state = dict(event.state)
            
            # Final results logging
            logger.info("="*80)
            logger.info("ASSESSMENT COMPLETE")
            logger.info("="*80)
            
            # Extract text from Content object and parse JSON
            report_data = {}
            
            # Parse final report from content (text parts only, not function responses)
            if final_content and hasattr(final_content, 'parts'):
                for part in final_content.parts:
                    if hasattr(part, 'text') and part.text:
                        text = part.text.strip()
                        # Try to extract JSON from markdown code block
                        if '```json' in text:
                            text = text.split('```json')[1].split('```')[0].strip()
                        elif '```' in text:
                            text = text.split('```')[1].split('```')[0].strip()
                        try:
                            # Clean up JSON: remove trailing commas before closing braces/brackets
                            cleaned_text = text
                            import re
                            # Remove trailing commas before closing brackets/braces
                            cleaned_text = re.sub(r',(\s*[}\]])', r'\1', cleaned_text)
                            
                            report_data = json.loads(cleaned_text)
                            # Extract key results for logging
                            risk_class = report_data.get('risk_classification', {})
                            agent_score = risk_class.get('score', 0)
                            agent_tier = risk_class.get('tier', 'N/A')
                            
                            logger.info(f"Classification: {agent_tier} | Score: {agent_score}/100 | Confidence: {risk_class.get('confidence', 'N/A')}")
                            logger.info(f"Report generated: {report_data.get('title', 'N/A')}")
                            break
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse JSON: {e}")
                            logger.warning(f"Text preview: {text[:200]}")
            
            # Return assessment from parsed report
            return {
                "assessment": report_data.get("risk_classification", {}),
                "report": report_data,
                "state": final_state,
                "metadata": {
                    "framework": "Google ADK with SequentialAgent",
                    "model": "gemini-2.0-flash",
                    "architecture": "5-agent sequential pipeline with parallel research",
                    "agents_used": [
                        "InformationGatherer",
                        "ParallelLegalResearchTeam (3 sub-agents)",
                        "LegalAggregator (with RelevanceChecker)",
                        "ComplianceClassifier",
                        "ReportGenerator"
                    ]
                }
            }
            
        except Exception as e:
            error_msg = f"SequentialAgent assessment workflow failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline structure.
        
        Returns:
            Dictionary with pipeline details
        """
        return {
            "type": "SequentialAgent",
            "total_agents": 5,
            "parallel_agents": 3,  # Within ParallelResearchTeam
            "state_keys": ["profile", "research_findings", "legal_analysis", "assessment", "report"],
            "features": [
                "Parallel multi-source research",
                "Cross-source reranking",
                "Agent-to-agent communication (AgentTool)",
                "Function tools (exit_with_findings)",
                "Automatic state management (output_key)"
            ]
        }
