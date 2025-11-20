"""Vector Index Tool for EU AI Act semantic search using Gemini embeddings."""

import logging
import json
import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from google.adk.tools import BaseTool
import google.generativeai as genai
from rank_bm25 import BM25Okapi

from src.config import Config

logger = logging.getLogger(__name__)


class VectorIndexTool(BaseTool):
    """Tool for hybrid search over EU AI Act using vector embeddings + BM25.
    
    This tool chunks the full EU AI Act text and implements hybrid search:
    1. Vector search: Gemini embeddings + cosine similarity (semantic matching)
    2. BM25 search: Keyword-based retrieval (lexical matching)
    3. RRF fusion: Combines both rankings using Reciprocal Rank Fusion
    
    This hybrid approach handles both semantic queries and exact keyword matches.
    """
    
    name = "vector_search_eu_ai_act"
    description = """Perform hybrid semantic + keyword search over the complete EU AI Act regulation text.
    Uses both vector embeddings (semantic) and BM25 (keyword) with RRF fusion for optimal results.
    
    Input should be a JSON string with:
    - query: Natural language search query (e.g., "high-risk AI systems requirements" or "Article 5")
    - top_k: Number of results to return (default: 3, max: 10)
    
    Returns the most relevant text chunks with article references and hybrid scores."""
    
    def __init__(self, eu_act_text_path: Optional[str] = None, cache_dir: Optional[str] = None):
        """Initialize vector index tool.
        
        Args:
            eu_act_text_path: Path to cleaned EU AI Act text file
            cache_dir: Directory to cache embeddings
        """
        super().__init__(
            name=self.name,
            description=self.description
        )
        
        # Configure paths
        project_root = Path(__file__).parent.parent
        self.text_path = Path(eu_act_text_path) if eu_act_text_path else project_root / "data" / "eu_ai_act_clean.txt"
        self.cache_dir = Path(cache_dir) if cache_dir else project_root / "data" / "embeddings_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Gemini embeddings
        if Config.GOOGLE_GENAI_API_KEY:
            genai.configure(api_key=Config.GOOGLE_GENAI_API_KEY)
        else:
            logger.warning("GOOGLE_GENAI_API_KEY not set. Vector search will not work.")
        
        # Load or build index
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []
        self.bm25: Optional[BM25Okapi] = None
        self._load_or_build_index()
    
    def _load_or_build_index(self):
        """Load cached index or build new one."""
        cache_file = self.cache_dir / "eu_ai_act_index.pkl"
        
        # Check if cache exists and is newer than source text
        if cache_file.exists() and self.text_path.exists():
            cache_mtime = cache_file.stat().st_mtime
            text_mtime = self.text_path.stat().st_mtime
            
            if cache_mtime > text_mtime:
                logger.info("Loading cached vector index...")
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                        self.chunks = data['chunks']
                        self.embeddings = data['embeddings']
                        self.bm25 = data.get('bm25')  # May not exist in old caches
                    logger.info(f"Loaded {len(self.chunks)} chunks from cache")
                    
                    # Build BM25 if not in cache
                    if self.bm25 is None:
                        logger.info("Building BM25 index (not in cache)...")
                        self._build_bm25()
                    return
                except Exception as e:
                    logger.warning(f"Failed to load cache: {e}. Rebuilding index...")
        
        # Build new index
        logger.info("Building vector index from EU AI Act text...")
        self._build_index()
        
        # Build BM25 index
        self._build_bm25()
        
        # Save to cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'chunks': self.chunks,
                    'embeddings': self.embeddings,
                    'bm25': self.bm25
                }, f)
            logger.info(f"Cached hybrid index to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache index: {e}")
    
    def _build_index(self):
        """Build vector index by chunking text and generating embeddings."""
        if not self.text_path.exists():
            logger.error(f"EU AI Act text not found at {self.text_path}")
            logger.info("Run: bash scripts/download_eu_ai_act.sh")
            return
        
        # Read and chunk text
        with open(self.text_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
        
        self.chunks = self._chunk_text(full_text)
        logger.info(f"Created {len(self.chunks)} text chunks")
        
        # Generate embeddings
        if not Config.GOOGLE_GENAI_API_KEY:
            logger.warning("No API key - skipping embeddings generation")
            return
        
        logger.info("Generating embeddings with Gemini...")
        for i, chunk in enumerate(self.chunks):
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=chunk['text'],
                    task_type="retrieval_document"
                )
                self.embeddings.append(result['embedding'])
                
                if (i + 1) % 50 == 0:
                    logger.info(f"  Generated embeddings for {i + 1}/{len(self.chunks)} chunks")
            except Exception as e:
                logger.error(f"Failed to generate embedding for chunk {i}: {e}")
                # Use zero vector as fallback
                self.embeddings.append([0.0] * 768)
        
        logger.info(f"Generated {len(self.embeddings)} embeddings")
    
    def _build_bm25(self):
        """Build BM25 index from text chunks."""
        if not self.chunks:
            logger.warning("No chunks available for BM25 indexing")
            return
        
        # Tokenize chunks for BM25
        tokenized_corpus = [chunk['text'].lower().split() for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"Built BM25 index with {len(tokenized_corpus)} documents")
    
    def _chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 200) -> List[Dict[str, Any]]:
        """Chunk text into overlapping segments with metadata.
        
        Args:
            text: Full EU AI Act text
            chunk_size: Target characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        
        # Split by article markers for better chunking
        article_pattern = r'(Article \d+)'
        import re
        
        # Split into sections
        sections = re.split(article_pattern, text)
        
        current_article = "Preamble"
        current_text = ""
        
        for i, section in enumerate(sections):
            # Check if this is an article marker
            if re.match(article_pattern, section):
                # Save previous chunk if it exists
                if current_text.strip():
                    chunks.extend(self._split_into_chunks(current_text, current_article, chunk_size, overlap))
                
                current_article = section.strip()
                current_text = ""
            else:
                current_text += section
        
        # Add last chunk
        if current_text.strip():
            chunks.extend(self._split_into_chunks(current_text, current_article, chunk_size, overlap))
        
        return chunks
    
    def _split_into_chunks(self, text: str, article: str, chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata."""
        chunks = []
        text = text.strip()
        
        if len(text) <= chunk_size:
            chunks.append({
                'text': text,
                'article': article,
                'char_start': 0,
                'char_end': len(text)
            })
        else:
            # Split into overlapping chunks
            start = 0
            chunk_id = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                
                # Try to break at sentence boundary
                if end < len(text):
                    last_period = text[start:end].rfind('. ')
                    if last_period > chunk_size // 2:  # Only if found in latter half
                        end = start + last_period + 1
                
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        'text': chunk_text,
                        'article': article,
                        'char_start': start,
                        'char_end': end,
                        'chunk_id': chunk_id
                    })
                    chunk_id += 1
                
                # Move start forward with overlap
                start = end - overlap if end < len(text) else len(text)
        
        return chunks
    
    def execute(self, input_data: str) -> str:
        """Execute semantic search over EU AI Act.
        
        Args:
            input_data: JSON string with query and optional top_k
            
        Returns:
            JSON string with search results
        """
        try:
            params = json.loads(input_data) if isinstance(input_data, str) else input_data
            query = params.get("query", "")
            top_k = min(params.get("top_k", 3), 10)
            
            if not query:
                return json.dumps({"error": "Query is required"})
            
            if not self.embeddings:
                return json.dumps({
                    "error": "Vector index not available",
                    "message": "Run: bash scripts/download_eu_ai_act.sh to download EU AI Act text"
                })
            
            # Generate query embedding for vector search
            logger.info(f"Hybrid search query: {query}")
            query_result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            query_embedding = query_result['embedding']
            
            # Perform hybrid search (vector + BM25 + RRF)
            results = self._hybrid_search(query, query_embedding, top_k)
            
            return json.dumps({
                "query": query,
                "results": results,
                "total_results": len(results)
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return json.dumps({"error": str(e)})
    
    def _hybrid_search(self, query: str, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Perform hybrid search using vector + BM25 with RRF fusion.
        
        Args:
            query: Original text query
            query_embedding: Query vector for semantic search
            top_k: Number of results to return
            
        Returns:
            List of result dictionaries with text, article, and fused score
        """
        # 1. Vector search
        vector_results = self._vector_search(query_embedding, top_k * 3)  # Get more candidates
        
        # 2. BM25 search
        bm25_results = self._bm25_search(query, top_k * 3)
        
        # 3. Reciprocal Rank Fusion
        fused_results = self._reciprocal_rank_fusion(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=top_k
        )
        
        return fused_results
    
    def _vector_search(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search for most similar chunks using cosine similarity.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            
        Returns:
            List of result dictionaries with text, article, and score
        """
        # Calculate cosine similarity for all chunks
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top-k results
        results = []
        for idx, score in similarities[:top_k]:
            chunk = self.chunks[idx]
            results.append({
                "chunk_idx": idx,
                "article": chunk['article'],
                "text": chunk['text'][:500] + "..." if len(chunk['text']) > 500 else chunk['text'],
                "full_text": chunk['text'],
                "score": round(score, 4),
                "metadata": {
                    "char_start": chunk.get('char_start', 0),
                    "char_end": chunk.get('char_end', 0),
                    "chunk_id": chunk.get('chunk_id', 0)
                }
            })
        
        return results
    
    def _bm25_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search.
        
        Args:
            query: Text query
            top_k: Number of results to return
            
        Returns:
            List of result dictionaries with chunk index and BM25 score
        """
        if self.bm25 is None:
            logger.warning("BM25 index not available")
            return []
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            results.append({
                "chunk_idx": idx,
                "article": chunk['article'],
                "text": chunk['text'][:500] + "..." if len(chunk['text']) > 500 else chunk['text'],
                "full_text": chunk['text'],
                "score": float(bm25_scores[idx]),
                "metadata": {
                    "char_start": chunk.get('char_start', 0),
                    "char_end": chunk.get('char_end', 0),
                    "chunk_id": chunk.get('chunk_id', 0)
                }
            })
        
        return results
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        top_k: int,
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """Combine vector and BM25 results using Reciprocal Rank Fusion.
        
        RRF formula: score(d) = sum(1 / (k + rank(d))) for each ranking
        where k=60 is a constant to reduce impact of high ranks.
        
        Args:
            vector_results: Results from vector search
            bm25_results: Results from BM25 search
            top_k: Number of final results to return
            k: RRF constant (default 60)
            
        Returns:
            Fused and ranked results
        """
        # Build RRF scores
        rrf_scores: Dict[int, float] = {}
        
        # Add vector search rankings
        for rank, result in enumerate(vector_results, start=1):
            chunk_idx = result['chunk_idx']
            rrf_scores[chunk_idx] = rrf_scores.get(chunk_idx, 0) + 1 / (k + rank)
        
        # Add BM25 rankings
        for rank, result in enumerate(bm25_results, start=1):
            chunk_idx = result['chunk_idx']
            rrf_scores[chunk_idx] = rrf_scores.get(chunk_idx, 0) + 1 / (k + rank)
        
        # Sort by fused score
        sorted_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)
        
        # Build final results
        final_results = []
        for idx in sorted_indices[:top_k]:
            chunk = self.chunks[idx]
            final_results.append({
                "article": chunk['article'],
                "text": chunk['text'][:500] + "..." if len(chunk['text']) > 500 else chunk['text'],
                "full_text": chunk['text'],
                "rrf_score": round(rrf_scores[idx], 6),
                "search_method": "hybrid_rrf",
                "metadata": {
                    "char_start": chunk.get('char_start', 0),
                    "char_end": chunk.get('char_end', 0),
                    "chunk_id": chunk.get('chunk_id', 0)
                }
            })
        
        return final_results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_article(self, article_name: str) -> Optional[str]:
        """Get full text of a specific article.
        
        Args:
            article_name: Article identifier (e.g., "Article 5", "Article 6")
            
        Returns:
            Combined text of all chunks belonging to that article
        """
        article_chunks = [c for c in self.chunks if c['article'] == article_name]
        if not article_chunks:
            return None
        
        # Sort by position and combine
        article_chunks.sort(key=lambda x: x.get('char_start', 0))
        return "\n".join(c['text'] for c in article_chunks)
