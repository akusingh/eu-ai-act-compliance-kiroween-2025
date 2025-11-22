"""ADK-compatible tools for EU AI Act Compliance Assessment."""

import logging
from typing import Dict, List, Any, Optional
from google.adk.tools import BaseTool

logger = logging.getLogger(__name__)


class EUAIActReferenceTool(BaseTool):
    """Tool for accessing EU AI Act reference materials."""
    
    name = "eu_ai_act_reference"
    description = """Access EU AI Act articles and regulations. 
    Use this tool to look up specific articles, search by keywords, or get compliance information.
    Input should be a JSON string with 'action' (get_article|search_articles) and relevant parameters."""
    
    def __init__(self):
        """Initialize EU AI Act reference tool."""
        super().__init__(
            name=self.name,
            description=self.description
        )
        self.articles = self._load_articles()
        self.source_url = "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
    
    def _load_articles(self) -> Dict[str, Dict[str, str]]:
        """Load key EU AI Act articles."""
        return {
            "Article 1": {
                "title": "Subject matter and scope",
                "summary": "This Regulation lays down harmonised rules on AI systems to ensure proper functioning of the internal market and protect health, safety, and fundamental rights.",
                "requirements": ["General framework establishment", "Scope definition"]
            },
            "Article 5": {
                "title": "Prohibited AI Practices",
                "summary": "AI systems that deploy subliminal techniques, exploit vulnerabilities, enable social credit scoring, or perform real-time biometric identification in public spaces are prohibited.",
                "requirements": ["Cannot be placed on market", "Cannot be put into service", "Cannot be used"]
            },
            "Article 6": {
                "title": "Classification as high-risk AI systems",
                "summary": "AI systems are classified as high-risk if they pose significant risk of harm to health, safety, or fundamental rights.",
                "requirements": ["Risk assessment required", "Conformity assessment", "Registration in EU database"]
            },
            "Article 8": {
                "title": "Compliance with requirements",
                "summary": "High-risk AI systems shall comply with requirements concerning data governance, technical documentation, record-keeping, transparency, human oversight, accuracy, robustness and cybersecurity.",
                "requirements": ["Risk management system", "Data governance", "Technical documentation", "Record-keeping", "Transparency", "Human oversight"]
            },
            "Article 9": {
                "title": "Risk management system",
                "summary": "A risk management system shall be established, implemented, documented and maintained for high-risk AI systems.",
                "requirements": ["Risk identification and analysis", "Risk estimation and evaluation", "Risk mitigation measures", "Continuous monitoring"]
            },
            "Article 52": {
                "title": "Transparency obligations for certain AI systems",
                "summary": "Providers shall ensure that AI systems intended to interact with natural persons are designed to inform those persons that they are interacting with an AI system.",
                "requirements": ["User notification", "Disclosure of AI use", "Transparency about capabilities and limitations"]
            },
            "Article 53": {
                "title": "Transparency obligations for deployers",
                "summary": "Deployers of AI systems that interact with natural persons shall inform them that they are subject to the use of an AI system.",
                "requirements": ["Clear notification", "Information about purpose", "Contact point for queries"]
            }
        }
    
    def execute(self, input_data: str) -> str:
        """Execute the EU AI Act reference tool.
        
        Args:
            input_data: JSON string with action and parameters
            
        Returns:
            Reference information as JSON string
        """
        import json
        
        try:
            params = json.loads(input_data) if isinstance(input_data, str) else input_data
            action = params.get("action", "search_articles")
            
            if action == "get_article":
                article_id = params.get("article_id", "Article 5")
                result = self.get_article(article_id)
                return json.dumps(result, indent=2)
            
            elif action == "search_articles":
                keyword = params.get("keyword", "")
                results = self.search_articles(keyword)
                return json.dumps({"articles": results}, indent=2)
            
            else:
                return json.dumps({"error": f"Unknown action: {action}"})
                
        except Exception as e:
            logger.error(f"EU AI Act Reference tool error: {e}")
            return json.dumps({"error": str(e)})
    
    def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get specific article content."""
        article = self.articles.get(article_id)
        if article:
            return {
                "article_id": article_id,
                "title": article["title"],
                "summary": article["summary"],
                "requirements": article.get("requirements", []),
                "source": self.source_url
            }
        return {"error": f"Article {article_id} not found"}
    
    def search_articles(self, keyword: str) -> List[Dict[str, Any]]:
        """Search articles by keyword."""
        keyword_lower = keyword.lower()
        results = []
        
        for article_id, content in self.articles.items():
            if (keyword_lower in content["title"].lower() or
                keyword_lower in content["summary"].lower()):
                results.append({
                    "article_id": article_id,
                    "title": content["title"],
                    "summary": content["summary"]
                })
        
        return results


class ComplianceScoringTool(BaseTool):
    """Tool for calculating compliance scores."""
    
    name = "compliance_scoring"
    description = """Calculate EU AI Act compliance scores for AI systems.
    Input should be a JSON string with system characteristics including:
    - system_name: Name of the AI system
    - use_case: Description of the use case
    - data_types: List of data types processed
    - decision_impact: Impact level (significant/moderate/minimal)
    - autonomous_decision: Boolean
    - human_oversight: Boolean"""
    
    # Class-level storage for last output (for validation layer)
    _last_output = None
    
    def __init__(self):
        """Initialize compliance scoring tool."""
        super().__init__(
            name=self.name,
            description=self.description
        )
        self.framework = self._load_framework()
    
    def _load_framework(self) -> Dict[str, Any]:
        """Load EU AI Act compliance framework."""
        return {
            "prohibited_patterns": [
                "mass surveillance", "social credit", "subliminal manipulation",
                "exploit vulnerable", "emotion recognition law enforcement"
            ],
            "high_risk_patterns": [
                "creditworthiness", "loan approval", "hiring", "recruitment",
                "employment decision", "law enforcement", "biometric identification",
                "critical infrastructure", "educational admission", "legal decision"
            ],
            "limited_risk_patterns": [
                "chatbot", "synthetic media",
                "conversational ai", "emotion recognition", "content generation"
            ],
            "scoring_weights": {
                "decision_impact": {"significant": 25, "moderate": 12, "minimal": 3},
                "autonomous_decision": 20,
                "human_oversight_penalty": -10,
                "sensitive_data_per_type": 5,
                "severe_consequences": 20,
                "moderate_consequences": 10
            }
        }
    
    def execute(self, input_data: str) -> str:
        """Execute the compliance scoring tool.
        
        Args:
            input_data: JSON string with system characteristics
            
        Returns:
            Compliance score and classification as JSON string
        """
        import json
        
        try:
            system_data = json.loads(input_data) if isinstance(input_data, str) else input_data
            
            # Calculate score
            score = self._calculate_score(system_data)
            
            # Determine classification
            classification = self._determine_classification(score, system_data)
            
            # Get relevant articles
            articles = self._get_relevant_articles(classification)
            
            result = {
                "score": round(score, 1),
                "classification": classification,
                "relevant_articles": articles,
                "requires_assessment": classification in ["prohibited", "high_risk"],
                "transparency_required": classification in ["limited_risk", "high_risk", "prohibited"],
                "origin": "ComplianceScoringTool"
            }
            
            # Store output for potential validation
            ComplianceScoringTool._last_output = result
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Compliance scoring error: {e}")
            return json.dumps({"error": str(e)})
    
    def _calculate_score(self, system_data: Dict[str, Any]) -> float:
        """Calculate risk score 0-100."""
        score = 0.0
        weights = self.framework["scoring_weights"]
        
        # Decision impact
        impact = system_data.get("decision_impact", "minimal")
        score += weights["decision_impact"].get(impact, 3)
        
        # Autonomous decision
        if system_data.get("autonomous_decision", False):
            score += weights["autonomous_decision"]
        
        # Human oversight (reduces score)
        if system_data.get("human_oversight", False):
            score += weights["human_oversight_penalty"]
        
        # Sensitive data
        sensitive_keywords = ["biometric", "health", "financial", "personal_data", "genetic", "criminal"]
        data_types = system_data.get("data_types", [])
        sensitive_count = sum(1 for dt in data_types if any(kw in str(dt).lower() for kw in sensitive_keywords))
        score += min(20, sensitive_count * weights["sensitive_data_per_type"])
        
        # Error consequences
        consequences = system_data.get("error_consequences", "").lower()
        if "severe" in consequences:
            score += weights["severe_consequences"]
        elif "moderate" in consequences:
            score += weights["moderate_consequences"]
        
        # Apply contextual adjustments
        score = self._apply_contextual_adjustments(system_data, score)
        
        return max(0, min(100, score))
    
    def _apply_contextual_adjustments(self, system_data: Dict[str, Any], base_score: float) -> float:
        """Apply context-aware adjustments based on patterns and their context."""
        score = base_score
        use_case = system_data.get("use_case", "").lower()
        system_name = system_data.get("system_name", "").lower()
        purpose = system_data.get("purpose", "").lower()
        combined_text = f"{use_case} {system_name} {purpose}"
        
        # Check for prohibited patterns (highest priority)
        if any(pattern in combined_text for pattern in self.framework["prohibited_patterns"]):
            return max(score, 85)
        
        # Context-aware check for "deepfake" keyword
        if "deepfake" in combined_text:
            # Detection systems are lower risk than generation systems
            if any(word in combined_text for word in ["detection", "detect", "identify", "recognize"]):
                # Deepfake detection is limited-risk (transparency obligation)
                score = max(score, 35)
                if score >= 55:
                    score = 50  # Cap to LIMITED_RISK
            else:
                # Deepfake generation is high-risk
                score = max(score, 60)
                if score >= 85:
                    score = 79
        
        # Context-aware check for "recommendation" keyword  
        elif "recommendation" in combined_text or "recommender" in combined_text:
            # Entertainment/media recommendations are minimal risk
            if any(word in combined_text for word in ["music", "entertainment", "media", "song", "movie", "video", "game"]):
                # Keep natural score, don't force upward
                pass
            # Product/content recommendations may need transparency
            else:
                # Limited-risk for non-entertainment recommendations
                score = max(score, 30)
                if score >= 55:
                    score = 50
        
        # Check for high-risk patterns (after specific context checks)
        elif any(pattern in combined_text for pattern in self.framework["high_risk_patterns"]):
            score = max(score, 60)
            # Enforce maximum to stay in HIGH_RISK tier
            if score >= 85:
                score = 79
        
        # Check for limited-risk patterns (general case)
        elif any(pattern in combined_text for pattern in self.framework["limited_risk_patterns"]):
            # Limited-risk patterns require minimum transparency obligations (Article 52, 53)
            score = max(score, 25)  # Ensure minimum LIMITED_RISK score
            # Cap score to stay in LIMITED_RISK tier if it would exceed
            if score >= 55:
                score = 50  # Cap to stay in LIMITED_RISK tier
        
        return score
    
    def _determine_classification(self, score: float, system_data: Dict[str, Any]) -> str:
        """Determine risk classification."""
        if score >= 85:
            return "prohibited"
        elif score >= 55:
            return "high_risk"
        elif score >= 25:
            return "limited_risk"
        else:
            return "minimal_risk"
    
    def _get_relevant_articles(self, classification: str) -> List[str]:
        """Get relevant EU AI Act articles for classification."""
        article_map = {
            "prohibited": ["Article 5"],
            "high_risk": ["Article 6", "Article 8", "Article 9"],
            "limited_risk": ["Article 52", "Article 53"],
            "minimal_risk": ["Article 1"]
        }
        return article_map.get(classification, [])
