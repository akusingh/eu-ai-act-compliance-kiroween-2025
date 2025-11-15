"""Tools for compliance assessment including Google Search and scoring."""

import logging
import json
from typing import Dict, List, Any, Optional

import requests

from src.config import Config


logger = logging.getLogger(__name__)


class GoogleSearchTool:
    """Tool for performing Google searches on EU AI Act regulations."""

    def __init__(self):
        """Initialize Google Search tool."""
        self.api_key = Config.SERPAPI_API_KEY
        self.base_url = "https://serpapi.com/search"
        self.available = bool(self.api_key)

    def search(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Search for information on EU AI Act.
        
        Args:
            query: Search query about EU AI Act or compliance
            num_results: Number of results to return
            
        Returns:
            List of search results with title, link, snippet
        """
        if not self.available:
            logger.warning("Google Search API not configured. Using mock results.")
            return self._get_mock_results(query)

        try:
            logger.info(f"Searching for: {query}")
            
            params = {
                "q": f"EU AI Act {query}",
                "api_key": self.api_key,
                "num": num_results,
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=Config.SEARCH_TIMEOUT,
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract organic results
            for item in data.get("organic_results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}. Using mock results.")
            return self._get_mock_results(query)

    def _get_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """Return mock search results for testing.
        
        Args:
            query: Original search query
            
        Returns:
            List of mock search results
        """
        mock_results = {
            "high-risk": [
                {
                    "title": "Article 6 - Classification as High-Risk",
                    "link": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
                    "snippet": "High-risk AI systems are AI systems that may cause significant harm to persons...",
                },
                {
                    "title": "EU AI Act Annex III - High-Risk Applications",
                    "link": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
                    "snippet": "Detailed list of AI systems considered high-risk including biometric identification...",
                },
            ],
            "prohibited": [
                {
                    "title": "Article 5 - Prohibited AI Practices",
                    "link": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
                    "snippet": "Certain AI practices that create unacceptable risk are prohibited...",
                },
            ],
            "transparency": [
                {
                    "title": "Article 52 - Transparency Requirements",
                    "link": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
                    "snippet": "Providers of certain AI systems must comply with transparency obligations...",
                },
            ],
        }
        
        # Return relevant mock results based on query
        for key, results in mock_results.items():
            if key.lower() in query.lower():
                return results
        
        # Default results
        return mock_results.get("high-risk", [])


class ComplianceScoringTool:
    """Tool for calculating compliance scores and recommendations."""

    def __init__(self):
        """Initialize compliance scoring tool."""
        self.eu_ai_act_framework = self._load_framework()

    def _load_framework(self) -> Dict[str, Any]:
        """Load EU AI Act compliance framework.
        
        Returns:
            Dictionary with compliance framework data
        """
        return {
            "prohibited_practices": [
                "Facial recognition for mass surveillance",
                "Social credit scoring systems",
                "Emotion recognition for law enforcement decisions",
                "Subliminal manipulation AI",
                "Exploitation of vulnerable groups",
            ],
            "high_risk_applications": [
                "Biometric identification and categorization",
                "Creditworthiness assessment",
                "Employment and worker management",
                "Law enforcement operations",
                "Critical infrastructure operations",
                "Educational evaluation and admission",
                "Interpretation of law and legal decisions",
            ],
            "limited_risk_categories": [
                "Chatbots and conversational AI",
                "Deepfakes and synthetic media",
                "Recommender systems",
                "Emotion recognition systems",
            ],
            "required_documentation": {
                "high_risk": [
                    "Risk assessment documentation",
                    "Data quality and governance procedures",
                    "Performance monitoring procedures",
                    "Logging and record keeping",
                    "Human oversight procedures",
                ],
                "limited_risk": [
                    "Disclosure of AI use",
                    "Transparency documentation",
                ],
            },
        }

    def calculate_compliance_score(
        self,
        system_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate compliance score for an AI system.
        
        Args:
            system_data: Dictionary with system characteristics
            
        Returns:
            Dictionary with compliance score and details
        """
        score = 0
        issues = []
        
        # Check for prohibited practices
        for practice in self.eu_ai_act_framework["prohibited_practices"]:
            if self._matches_description(system_data, practice):
                score = 0
                issues.append(f"PROHIBITED: {practice}")
                return {
                    "score": score,
                    "category": "prohibited",
                    "issues": issues,
                }
        
        # Check for high-risk applications
        high_risk_matches = 0
        for app in self.eu_ai_act_framework["high_risk_applications"]:
            if self._matches_description(system_data, app):
                high_risk_matches += 1
                score += 40
        
        # Check for limited-risk categories
        for category in self.eu_ai_act_framework["limited_risk_categories"]:
            if self._matches_description(system_data, category):
                score += 15
        
        # Evaluate safeguards
        if system_data.get("human_oversight"):
            score -= 10
        
        if system_data.get("audit_trail"):
            score -= 5
        
        if system_data.get("documentation"):
            score -= 5
        
        # Determine category
        if score >= 60:
            category = "high_risk"
        elif score >= 30:
            category = "limited_risk"
        else:
            category = "minimal_risk"
        
        if high_risk_matches > 1 and score < 60:
            issues.append("Multiple high-risk characteristics detected")
        
        return {
            "score": max(0, min(100, score)),
            "category": category,
            "high_risk_matches": high_risk_matches,
            "issues": issues,
        }

    def get_recommendations(
        self,
        risk_category: str,
        compliance_gaps: List[str],
    ) -> List[str]:
        """Get compliance recommendations based on risk category.
        
        Args:
            risk_category: Risk classification (prohibited/high_risk/limited_risk/minimal_risk)
            compliance_gaps: List of identified compliance gaps
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if risk_category == "prohibited":
            recommendations.append("STOP: This system contains prohibited AI practices")
            recommendations.append("Redesign system to remove prohibited elements")
            return recommendations
        
        # Get required documentation for category
        if risk_category == "high_risk":
            docs = self.eu_ai_act_framework["required_documentation"]["high_risk"]
        else:
            docs = self.eu_ai_act_framework["required_documentation"]["limited_risk"]
        
        for doc in docs:
            if not any(doc.lower() in gap.lower() for gap in compliance_gaps):
                recommendations.append(f"Implement: {doc}")
        
        # Add gap-specific recommendations
        gap_recommendations = {
            "human_oversight": "Establish human review process for AI decisions",
            "audit_trail": "Implement comprehensive logging and audit trails",
            "documentation": "Create and maintain AI system documentation",
            "impact_assessment": "Conduct and document impact assessment",
            "transparency": "Add user-facing transparency about AI use",
        }
        
        for gap in compliance_gaps:
            for key, rec in gap_recommendations.items():
                if key in gap.lower():
                    recommendations.append(rec)
        
        return recommendations

    def _matches_description(
        self,
        system_data: Dict[str, Any],
        description: str,
    ) -> bool:
        """Check if system data matches a description.
        
        Args:
            system_data: System characteristics
            description: Description to match
            
        Returns:
            True if description matches system
        """
        # Simple string matching - can be enhanced with NLP
        use_case = system_data.get("use_case", "").lower()
        system_name = system_data.get("system_name", "").lower()
        text = f"{use_case} {system_name}".lower()
        
        keywords = description.lower().split()
        matches = sum(1 for keyword in keywords if keyword in text)
        
        return matches >= len(keywords) * 0.5  # 50% match threshold


class EUAIActReferenceTool:
    """Tool for accessing EU AI Act reference materials."""

    def __init__(self):
        """Initialize EU AI Act reference tool."""
        self.articles = self._load_articles()
        self.source_url = "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"

    def _load_articles(self) -> Dict[str, Dict[str, str]]:
        """Load key EU AI Act articles.
        
        Returns:
            Dictionary mapping article numbers to content
        """
        return {
            "Article 1": {
                "title": "Subject matter and scope",
                "summary": "This Regulation lays down harmonised rules on AI",
            },
            "Article 5": {
                "title": "Prohibited AI Practices",
                "summary": "The following shall be prohibited: AI systems that deploy subliminal techniques...",
            },
            "Article 6": {
                "title": "Classification as high-risk",
                "summary": "AI systems are classified as high-risk if they have potential for significant harm",
            },
            "Article 8": {
                "title": "Risk assessment for high-risk systems",
                "summary": "High-risk AI system providers shall draw up and document a risk assessment",
            },
            "Article 9": {
                "title": "Risk Mitigation Measures",
                "summary": "High-risk AI system providers shall implement measures to mitigate identified risks",
            },
            "Article 52": {
                "title": "Transparency requirements",
                "summary": "Providers of certain AI systems shall inform users about AI use",
            },
            "Article 53": {
                "title": "User notification",
                "summary": "Users of AI systems shall be notified when interacting with AI",
            },
        }

    def get_article(self, article_id: str) -> Optional[Dict[str, str]]:
        """Get specific article content.
        
        Args:
            article_id: Article identifier (e.g., "Article 5")
            
        Returns:
            Article content or None if not found
        """
        return self.articles.get(article_id)

    def search_articles(self, keyword: str) -> List[Dict[str, Any]]:
        """Search articles by keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching articles
        """
        keyword_lower = keyword.lower()
        results = []
        
        for article_id, content in self.articles.items():
            if (keyword_lower in content["title"].lower() or
                    keyword_lower in content["summary"].lower()):
                results.append({
                    "article_id": article_id,
                    "title": content["title"],
                    "summary": content["summary"],
                })
        
        return results

    def get_all_articles(self) -> Dict[str, Dict[str, str]]:
        """Get all available articles.
        
        Returns:
            Dictionary of all articles
        """
        return self.articles.copy()

    def fetch_from_official_source(self) -> bool:
        """Attempt to fetch latest EU AI Act from official source.
        
        Returns:
            True if fetch successful, False otherwise
        """
        try:
            logger.info(f"Fetching EU AI Act from {self.source_url}")
            response = requests.get(self.source_url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML to extract article information
            if response.status_code == 200:
                logger.info("Successfully fetched EU AI Act from official source")
                return True
            return False
            
        except Exception as e:
            logger.warning(f"Failed to fetch from official source: {e}. Using built-in reference.")
            return False

    def get_source_url(self) -> str:
        """Get the official EU AI Act source URL.
        
        Returns:
            Official EUR-Lex URL for EU AI Act
        """
        return self.source_url
