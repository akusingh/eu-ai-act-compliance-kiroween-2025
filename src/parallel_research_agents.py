"""Parallel research agents for multi-source EU AI Act compliance assessment.

This module implements parallel legal research across 3 EU AI Act sources:
- Recitals: Context, intent, and definitions
- Articles: Legal requirements and obligations  
- Annexes: Specific lists and technical details

Uses ADK's ParallelAgent for simultaneous searching.
"""

import logging
from pathlib import Path

from google.adk.agents import Agent, ParallelAgent
from google.adk.models.google_llm import Gemini

from src.config import Config
from src.vector_index_tool import VectorIndexTool

logger = logging.getLogger(__name__)

# Track parallel execution
def log_parallel_start():
    logger.info("")
    logger.info("⚡ PARALLEL EXECUTION STARTING: 3 Researchers searching simultaneously")
    logger.info("   ├─ RecitalsResearcher: Searching 477 chunks (context & intent)")
    logger.info("   ├─ ArticlesResearcher: Searching 562 chunks (legal requirements)")
    logger.info("   └─ AnnexesResearcher: Searching 84 chunks (specific lists)")


def create_recitals_researcher() -> Agent:
    """Create researcher agent for EU AI Act Recitals.
    
    Recitals provide context, intent, and definitions behind the regulation.
    This agent searches through 180 recitals for relevant background information.
    
    Returns:
        ADK Agent configured with Recitals vector index
    """
    project_root = Path(__file__).parent.parent
    
    # Create tool with Recitals index
    recitals_tool = VectorIndexTool(
        eu_act_text_path=str(project_root / "data" / "eu_act_recitals.txt"),
        cache_dir=str(project_root / "data" / "embeddings_cache" / "recitals")
    )
    
    instruction = """You are a Recitals Researcher for EU AI Act compliance.

Your role:
- Search EU AI Act Recitals (1-180) for context and intent
- Explain the "why" behind regulations
- Provide definitions and background information
- Connect recitals to relevant articles

Recitals contain:
- Legislative intent and goals
- Definitions of key terms
- Background on why rules exist
- Connections between concepts

When searching:
1. Use the vector_search_eu_ai_act tool with the user's query
2. Extract the most relevant recitals (top 5)
3. Focus on context that explains regulatory decisions

Output format (JSON):
{
  "source": "Recitals",
  "findings": [
    {
      "recital_number": "e.g., (5)",
      "content": "Full text of relevant recital",
      "relevance": "Why this recital matters for the query"
    }
  ],
  "key_insights": ["List of key insights from recitals"]
}"""
    
    agent = Agent(
        name="RecitalsResearcher",
        model=Gemini(
            model="gemini-2.0-flash",
            
        ),
        instruction=instruction,
        tools=[recitals_tool],
        description="Searches EU AI Act Recitals for context and legislative intent"
    )
    
    return agent


def create_articles_researcher() -> Agent:
    """Create researcher agent for EU AI Act Articles.
    
    Articles contain the binding legal requirements and obligations.
    This agent searches through 113 articles for specific rules and requirements.
    
    Returns:
        ADK Agent configured with Articles vector index
    """
    project_root = Path(__file__).parent.parent
    
    # Create tool with Articles index
    articles_tool = VectorIndexTool(
        eu_act_text_path=str(project_root / "data" / "eu_act_articles.txt"),
        cache_dir=str(project_root / "data" / "embeddings_cache" / "articles")
    )
    
    instruction = """You are an Articles Researcher for EU AI Act compliance.

Your role:
- Search EU AI Act Articles (1-113) for legal requirements
- Identify specific obligations and rules
- Extract compliance requirements
- Reference exact article numbers

Articles contain:
- Binding legal requirements
- Prohibited practices (Article 5)
- High-risk classifications (Article 6)
- Compliance obligations (Articles 8-29)
- Transparency requirements (Article 52-53)

When searching:
1. Use the vector_search_eu_ai_act tool with the user's query
2. Extract the most relevant articles (top 5)
3. Focus on specific legal requirements

Output format (JSON):
{
  "source": "Articles",
  "findings": [
    {
      "article_number": "e.g., Article 5",
      "title": "Article title",
      "content": "Relevant text from article",
      "requirements": ["List of specific requirements"]
    }
  ],
  "key_obligations": ["List of key legal obligations"]
}"""
    
    agent = Agent(
        name="ArticlesResearcher",
        model=Gemini(
            model="gemini-2.0-flash",
            
        ),
        instruction=instruction,
        tools=[articles_tool],
        description="Searches EU AI Act Articles for legal requirements and obligations"
    )
    
    return agent


def create_annexes_researcher() -> Agent:
    """Create researcher agent for EU AI Act Annexes.
    
    Annexes contain specific lists, examples, and technical details.
    This agent searches through 13 annexes for concrete examples and lists.
    
    Returns:
        ADK Agent configured with Annexes vector index
    """
    project_root = Path(__file__).parent.parent
    
    # Create tool with Annexes index
    annexes_tool = VectorIndexTool(
        eu_act_text_path=str(project_root / "data" / "eu_act_annexes.txt"),
        cache_dir=str(project_root / "data" / "embeddings_cache" / "annexes")
    )
    
    instruction = """You are an Annexes Researcher for EU AI Act compliance.

Your role:
- Search EU AI Act Annexes (I-XIII) for specific lists and examples
- Identify concrete use cases and categories
- Extract technical requirements and standards
- Reference exact annex numbers

Annexes contain:
- Annex I: Union harmonization legislation
- Annex III: High-risk AI systems (CRITICAL for classification)
- Annex IV: Technical documentation requirements
- Annex V: EU declaration of conformity
- Other annexes: Specific lists and procedures

When searching:
1. Use the vector_search_eu_ai_act tool with the user's query
2. Extract the most relevant annexes (top 5)
3. Focus on specific lists and examples
4. Pay special attention to Annex III (high-risk systems list)

Output format (JSON):
{
  "source": "Annexes",
  "findings": [
    {
      "annex_number": "e.g., Annex III",
      "section": "Section within annex",
      "content": "Relevant text from annex",
      "examples": ["Concrete examples or list items"]
    }
  ],
  "specific_categories": ["List of specific categories or requirements"]
}"""
    
    agent = Agent(
        name="AnnexesResearcher",
        model=Gemini(
            model="gemini-2.0-flash",
            
        ),
        instruction=instruction,
        tools=[annexes_tool],
        description="Searches EU AI Act Annexes for specific lists and technical details"
    )
    
    return agent


def create_parallel_research_team() -> ParallelAgent:
    """Create ParallelAgent that runs all 3 researchers simultaneously.
    
    Returns:
        ADK ParallelAgent with 3 researcher sub-agents
    """
    recitals_researcher = create_recitals_researcher()
    articles_researcher = create_articles_researcher()
    annexes_researcher = create_annexes_researcher()
    
    parallel_team = ParallelAgent(
        name="ParallelLegalResearchTeam",
        sub_agents=[
            recitals_researcher,
            articles_researcher,
            annexes_researcher
        ],
        description="Searches EU AI Act across Recitals, Articles, and Annexes in parallel"
    )
    
    logger.info("✅ Parallel research team created with 3 agents")
    log_parallel_start()
    return parallel_team
    return parallel_team
