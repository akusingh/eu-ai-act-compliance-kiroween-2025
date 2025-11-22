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
import time

from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
import google.generativeai as genai

from src.config import Config
from src.observability import metrics_collector, trace_collector

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

⚠️  MANDATORY FIRST STEP - YOU MUST CALL THE TOOL BEFORE ANYTHING ELSE ⚠️
Before you can output ANYTHING, you MUST:
1. Call the compliance_scoring tool with the system profile from {profile}
2. Wait for the tool's response
3. Extract "score" and "classification" from tool output
4. ONLY THEN can you proceed to write your assessment

IF YOU DO NOT CALL THE TOOL FIRST, YOUR RESPONSE IS INVALID.

WORKFLOW (MUST FOLLOW IN ORDER):
1. ✅ CALL compliance_scoring tool with {profile} data (MANDATORY FIRST STEP)
2. ✅ Get the tool's "score" and "classification" output  
3. ✅ Use those EXACT values - do NOT modify them
4. Reference {legal_analysis} only for article citations and recommendations

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

FUNCTION CALL FORMAT (MANDATORY):
You MUST invoke the tool with a single function call named: compliance_scoring
Arguments must be a JSON string of the system profile. Example:
CALL compliance_scoring WITH INPUT:
{"system_name":"Loan Approval System","use_case":"Creditworthiness assessment for loan decisions","data_types":["financial","personal_data"],"decision_impact":"significant","autonomous_decision":true,"human_oversight":true,"error_consequences":"Severe - affects credit access"}

If you cannot find required fields, ask for them BEFORE calling the tool.
DO NOT fabricate a score. If the tool does not return a score, call it again.

MANDATORY OUTPUT JSON (after tool call):
{
    "risk_score": <number from tool score>,
    "risk_tier": <string from tool classification>,
    "relevant_articles": [<citations from legal_analysis>],
    "compliance_gaps": ["..."],
    "recommendations": ["..."],
    "confidence": <0-1>,
    "reasoning": "Step-by-step justification using tool output + articles"
}

ABSOLUTE RULES:
1. Never output a score > 100 or < 0.
2. Never change classification tier wording.
3. If tool classification conflicts with legal_analysis text, KEEP the tool classification.
4. If you accidentally produce a different tier, immediately correct it to the tool's classification.
5. Only one JSON object as final output - no surrounding commentary.

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
            # Start observability tracking
            start_time = time.time()
            metrics_collector.start_timer()
            
            trace_collector.record_trace(
                agent_name="ComplianceOrchestrator",
                action="assessment_start",
                input_data={"system_name": system_info.get('system_name', 'Unknown')},
                status="success"
            )
            
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
            
            # Track pipeline execution
            pipeline_start = time.time()
            trace_collector.record_trace(
                agent_name="SequentialPipeline",
                action="pipeline_execution_start",
                input_data={"stages": 5},
                status="success"
            )
            
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
            
            # Define async function to get session state
            async def run_and_get_state():
                events = await self.runner.run_debug(
                    user_messages=f"Assess this AI system for EU AI Act compliance: {json.dumps(system_info)}",
                    quiet=True  # Suppress ADK debug output
                )
                
                # Get session state using async method
                debug_user_id = 'debug_user_id'
                debug_session_id = 'debug_session_id'
                try:
                    session = await self.runner.session_service.get_session(
                        app_name="agents",
                        user_id=debug_user_id,
                        session_id=debug_session_id
                    )
                    return events, session
                except Exception as e:
                    logger.warning(f"Could not retrieve session: {e}")
                    return events, None
            
            # Run async operations
            events, session = loop.run_until_complete(run_and_get_state())
            
            pipeline_duration = time.time() - pipeline_start
            metrics_collector.record_metric(
                "pipeline_execution_time",
                pipeline_duration,
                tags={"system": system_info.get('system_name', 'Unknown')}
            )
            
            trace_collector.record_trace(
                agent_name="SequentialPipeline",
                action="pipeline_execution_complete",
                output_data={"duration_seconds": pipeline_duration},
                status="success"
            )
            
            logger.info("Compliance assessment completed successfully")
            
            # Extract state and content
            final_content = None
            final_state = {}
            
            # Get final content from last event
            for event in events:
                if hasattr(event, 'content') and event.content:
                    final_content = event.content
            
            # Extract state from session
            if session and hasattr(session, 'state'):
                final_state = dict(session.state)
                logger.info(f"✅ Retrieved session state with keys: {list(final_state.keys())}")
                
                trace_collector.record_trace(
                    agent_name="SessionService",
                    action="state_retrieval",
                    output_data={"state_keys": list(final_state.keys())},
                    status="success"
                )
            else:
                logger.warning("Session not available or has no state")
                trace_collector.record_trace(
                    agent_name="SessionService",
                    action="state_retrieval",
                    status="warning",
                    error="Session not available or has no state attribute"
                )
            
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
                            report_data = json.loads(text)
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
            
            # Get authoritative assessment from state (ComplianceClassifier output)
            state_assessment = {}
            if "assessment" in final_state:
                assessment_value = final_state.get("assessment")
                
                # Parse assessment - may be dict or JSON string
                if isinstance(assessment_value, dict):
                    state_assessment = assessment_value
                elif isinstance(assessment_value, str):
                    # Check if this is a tool call (ADK stores function calls in output_key)
                    if '```tool_code' in assessment_value or 'CALL compliance_scoring' in assessment_value:
                        logger.info("Assessment contains tool call, not result - will use tool validation")
                        # This is the function call, not the result
                        # The actual assessment should be extracted from the report or we rely on tool validation
                    else:
                        # Try to parse JSON from string (may be wrapped in markdown)
                        try:
                            text = assessment_value.strip()
                            logger.debug(f"Raw assessment string (first 500 chars): {text[:500]}")
                            
                            # Handle various markdown code block formats:
                            # ```json, ```tool_code, `````, etc.
                            if '```' in text:
                                # Find first code block regardless of language tag
                                parts = text.split('```')
                                if len(parts) >= 3:
                                    # Get content between first ``` and second ```
                                    code_block = parts[1]
                                    # Remove language identifier if present (e.g. "json", "tool_code")
                                    # Language identifiers are on the first line
                                    lines = code_block.split('\n', 1)
                                    if len(lines) > 1:
                                        # If first line looks like language tag, skip it
                                        first_line = lines[0].strip()
                                        if first_line and not first_line.startswith('{'):
                                            text = lines[1].strip()
                                        else:
                                            text = code_block.strip()
                                    else:
                                        text = code_block.strip()
                            
                            state_assessment = json.loads(text)
                            logger.info(f"✅ Parsed assessment from state string")
                        except Exception as e:
                            logger.debug(f"Could not parse assessment string: {e}")
                
                if state_assessment:
                    logger.info(f"✅ Assessment in state: tier={state_assessment.get('risk_tier')}, score={state_assessment.get('risk_score')}")
            else:
                logger.warning("No 'assessment' key found in final_state. Keys present: %s", list(final_state.keys()))

            # Invoke scoring tool for ground truth validation
            # This serves as both fallback (if agent didn't run tool) and validation (to check agent accuracy)
            tool_output = None
            try:
                from src.tools_adk import ComplianceScoringTool as _CST
                _tool = _CST()
                import json as _json
                logger.info(f"⚙️  Running tool for validation: {system_info.get('system_name')}")
                
                tool_start = time.time()
                tool_raw = _tool.execute(_json.dumps(system_info))
                tool_duration = time.time() - tool_start
                
                tool_output = _json.loads(tool_raw)
                logger.info(f"✅ Tool result: score={tool_output.get('score')}, tier={tool_output.get('classification')}")
                
                metrics_collector.record_metric(
                    "tool_execution_time",
                    tool_duration,
                    tags={"tool": "ComplianceScoringTool"}
                )
                
                trace_collector.record_trace(
                    agent_name="ComplianceScoringTool",
                    action="score_validation",
                    input_data={"system": system_info.get('system_name')},
                    output_data={
                        "score": tool_output.get('score'),
                        "tier": tool_output.get('classification'),
                        "duration": tool_duration
                    },
                    status="success"
                )
            except Exception as e:
                logger.error(f"❌ Tool execution failed: {e}")
                trace_collector.record_trace(
                    agent_name="ComplianceScoringTool",
                    action="score_validation",
                    status="error",
                    error=str(e)
                )

            # Extract report classification
            report_classification = report_data.get("risk_classification", {}) if isinstance(report_data, dict) else {}

            def _normalize_tier(val: Any) -> str:
                if not isinstance(val, str):
                    return ""
                return val.lower().replace(" ", "_").replace("-", "_")

            # Build validated assessment starting from tool output → state → report
            validated = {}
            if tool_output and isinstance(tool_output, dict):
                validated = {
                    "tier": _normalize_tier(tool_output.get("classification", "")),
                    "score": tool_output.get("score", 0),
                    "confidence": report_classification.get("confidence") or state_assessment.get("confidence") or 0.8,
                    "articles": tool_output.get("relevant_articles", [])
                }
            elif state_assessment:
                # Fallback to classifier state if tool output missing
                validated = {
                    "tier": _normalize_tier(state_assessment.get("risk_tier") or state_assessment.get("tier") or ""),
                    "score": state_assessment.get("risk_score") or state_assessment.get("score") or 0,
                    "confidence": state_assessment.get("confidence", 0.7),
                    "articles": state_assessment.get("relevant_articles", [])
                }
            else:
                validated = {
                    "tier": _normalize_tier(report_classification.get("tier", "")),
                    "score": report_classification.get("score", 0),
                    "confidence": report_classification.get("confidence", 0.5),
                    "articles": report_classification.get("articles", [])
                }

            # Compare report classification against validated assessment; override mismatch
            mismatch = False
            if report_classification:
                rep_tier = _normalize_tier(report_classification.get("tier", ""))
                rep_score = report_classification.get("score")
                if rep_tier and rep_tier != validated.get("tier"):
                    mismatch = True
                if rep_score is not None and isinstance(rep_score, (int, float)) and abs(rep_score - validated.get("score", 0)) > 1e-6:
                    mismatch = True
            
            # REMOVED: Pattern-based correction that was overriding tool output
            # The tool is context-aware and already handles deepfake detection vs generation
            # Trust the tool's judgment - it knows the difference between detection and generation

            if mismatch:
                logger.warning("Risk classification in final report differed from tool/state. Overriding with validated assessment.")
                # Inject corrected classification into report
                if isinstance(report_data, dict):
                    report_data.setdefault("risk_classification", {})
                    report_data["risk_classification"].update(validated)
                    
                trace_collector.record_trace(
                    agent_name="ComplianceOrchestrator",
                    action="classification_mismatch_correction",
                    input_data={"report_tier": rep_tier, "validated_tier": validated.get("tier")},
                    output_data={"corrected": True},
                    status="success"
                )
            else:
                logger.info("Risk classification validated against tool/state.")
            
            # Record final assessment metrics
            total_duration = time.time() - start_time
            metrics_collector.record_metric(
                "total_assessment_time",
                total_duration,
                tags={
                    "system": system_info.get('system_name', 'Unknown'),
                    "risk_tier": validated.get("tier", "unknown")
                }
            )
            metrics_collector.record_metric(
                "risk_score",
                validated.get("score", 0),
                tags={"system": system_info.get('system_name', 'Unknown')}
            )
            
            trace_collector.record_trace(
                agent_name="ComplianceOrchestrator",
                action="assessment_complete",
                output_data={
                    "tier": validated.get("tier"),
                    "score": validated.get("score"),
                    "total_duration": total_duration
                },
                status="success"
            )

            return {
                "assessment": validated,
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
                    ],
                    "validation": {
                        "source": "tool_output" if tool_output else ("state_assessment" if state_assessment else "report_only"),
                        "mismatch_corrected": mismatch
                    }
                }
            }
            
        except Exception as e:
            error_msg = f"SequentialAgent assessment workflow failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            trace_collector.record_trace(
                agent_name="ComplianceOrchestrator",
                action="assessment_failed",
                input_data={"system": system_info.get('system_name', 'Unknown')},
                status="error",
                error=error_msg
            )
            
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
