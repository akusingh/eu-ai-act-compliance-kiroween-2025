"""Reranker tool for cross-source result ranking using Cohere API.

This tool reranks search results from multiple sources (Recitals, Articles, Annexes)
based on query relevance. Falls back to passthrough mode if Cohere API key is not available.
"""

import logging
import json
from typing import List, Dict, Any

from google.adk.tools import BaseTool

from src.config import Config

logger = logging.getLogger(__name__)


class RerankerTool(BaseTool):
    """Rerank search results from multiple sources using Cohere or passthrough.
    
    This tool handles reranking of search results from 3 EU AI Act sources:
    - Recitals (context and intent)
    - Articles (legal requirements)
    - Annexes (specific lists)
    
    With API key: Uses Cohere rerank-english-v3.0 (best quality)
    Without API key: Falls back to passthrough mode (preserves original order)
    """
    
    name = "rerank_legal_findings"
    description = """Rerank search results from multiple EU AI Act sources by query relevance.
    
    Input should be a JSON string with:
    - query: The search query
    - documents: List of text chunks from different sources
    - top_n: Number of results to return (default: 10)
    
    Returns reranked results with relevance scores."""
    
    def __init__(self):
        """Initialize reranker with Cohere or fallback mode."""
        super().__init__(
            name=self.name,
            description=self.description
        )
        self.cohere_available = False
        self.co = None
        
        if Config.COHERE_API_KEY:
            try:
                import cohere
                self.co = cohere.Client(Config.COHERE_API_KEY)
                self.cohere_available = True
                logger.info("Cohere reranker enabled (rerank-english-v3.0)")
            except ImportError:
                logger.warning("Cohere package not installed. Install with: pip install cohere")
                logger.info("Reranker: using passthrough mode")
            except Exception as e:
                logger.warning(f"Cohere initialization failed: {e}")
                logger.info("Reranker: using passthrough mode")
        else:
            logger.info("No COHERE_API_KEY configured - reranker using passthrough mode")
            logger.info("To enable reranking: get free key at https://dashboard.cohere.com/api-keys")
    
    def execute(self, input_data: str) -> str:
        """Execute reranking on search results.
        
        Args:
            input_data: JSON string with query, documents, and optional top_n
            
        Returns:
            JSON string with reranked results and scores
        """
        try:
            # Parse input
            data = json.loads(input_data) if isinstance(input_data, str) else input_data
            query = data.get("query", "")
            documents = data.get("documents", [])
            top_n = min(data.get("top_n", 10), 20)  # Max 20 results
            
            if not query:
                return json.dumps({"error": "Query is required"})
            
            if not documents:
                return json.dumps({"error": "No documents provided"})
            
            logger.info(f"Reranking {len(documents)} documents for query: {query[:50]}...")
            
            # Execute reranking
            if self.cohere_available:
                return self._rerank_with_cohere(query, documents, top_n)
            else:
                return self._rerank_passthrough(query, documents, top_n)
        
        except Exception as e:
            logger.error(f"Reranker error: {e}")
            return json.dumps({"error": str(e)})
    
    def _rerank_with_cohere(self, query: str, documents: List[str], top_n: int) -> str:
        """Rerank using Cohere API.
        
        Args:
            query: Search query
            documents: List of document texts
            top_n: Number of results to return
            
        Returns:
            JSON string with reranked results
        """
        try:
            # Call Cohere rerank API
            results = self.co.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=documents,
                top_n=top_n,
                return_documents=False  # We already have the docs
            )
            
            # Format results
            reranked = []
            for result in results.results:
                reranked.append({
                    "index": result.index,
                    "text": documents[result.index],
                    "relevance_score": result.relevance_score
                })
            
            logger.info(f"🔄 RERANKING: {len(reranked)} results | Scores: {reranked[0]['relevance_score']:.4f}→{reranked[-1]['relevance_score']:.4f} | Cohere rerank-v3")
            
            return json.dumps({
                "query": query,
                "reranked_results": reranked,
                "total_results": len(reranked),
                "method": "cohere_rerank_v3"
            }, indent=2)
        
        except Exception as e:
            logger.error(f"Cohere reranking failed: {e}")
            logger.info("Falling back to passthrough mode")
            return self._rerank_passthrough(query, documents, top_n)
    
    def _rerank_passthrough(self, query: str, documents: List[str], top_n: int) -> str:
        """Passthrough mode - preserve original order with synthetic scores.
        
        Args:
            query: Search query
            documents: List of document texts
            top_n: Number of results to return
            
        Returns:
            JSON string with passthrough results
        """
        # Return documents in original order with decreasing scores
        results = []
        for i, doc in enumerate(documents[:top_n]):
            results.append({
                "index": i,
                "text": doc,
                "relevance_score": 1.0 - (i * 0.05)  # Synthetic score
            })
        
        logger.info(f"🔄 RERANKING (Passthrough): {len(results)} results | No API key")
        
        return json.dumps({
            "query": query,
            "reranked_results": results,
            "total_results": len(results),
            "method": "passthrough_no_api_key"
        }, indent=2)
    
    def get_status(self) -> Dict[str, Any]:
        """Get reranker status information.
        
        Returns:
            Dictionary with reranker configuration and status
        """
        return {
            "cohere_available": self.cohere_available,
            "mode": "cohere_rerank_v3" if self.cohere_available else "passthrough",
            "api_key_configured": bool(Config.COHERE_API_KEY)
        }
