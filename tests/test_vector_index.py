"""Unit tests for vector_index_tool.py - VectorIndexTool."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.vector_index_tool import VectorIndexTool
import os


class TestVectorIndexTool:
    """Test suite for VectorIndexTool."""
    
    @pytest.fixture
    def vector_tool(self):
        """Create a VectorIndexTool instance with mocked genai.embed_content."""
        # Mock genai.configure to avoid API key requirement
        with patch('google.generativeai.configure'):
            # Create tool instance - will load from cache or use empty index
            tool = VectorIndexTool()
            return tool
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        with patch('google.generativeai.configure'):
            tool = VectorIndexTool()
            assert tool.name == "vector_search_eu_ai_act"
            assert "hybrid" in tool.description.lower() or "search" in tool.description.lower()
            assert tool.chunks is not None
    
    def test_tool_has_required_attributes(self):
        """Test that tool has all required attributes."""
        with patch('google.generativeai.configure'):
            tool = VectorIndexTool()
            assert hasattr(tool, 'chunks')
            assert hasattr(tool, 'embeddings')
            assert hasattr(tool, 'bm25')
            assert hasattr(tool, 'text_path')
            assert hasattr(tool, 'cache_dir')
    
    def test_search_query_structure(self, vector_tool):
        """Test that search accepts properly formatted queries."""
        query = '{"query": "high-risk AI systems", "top_k": 5}'
        
        # Mock genai.embed_content and hybrid_search
        with patch('google.generativeai.embed_content', return_value={'embedding': [0.1] * 768}):
            with patch.object(vector_tool, '_hybrid_search') as mock_hybrid:
                # Add dummy chunks and embeddings
                vector_tool.chunks = [
                    {"text": "Article 6: High-risk AI systems", "article": "Article 6"},
                    {"text": "Article 9: Risk management", "article": "Article 9"}
                ]
                vector_tool.embeddings = [[0.1] * 768, [0.2] * 768]
                
                mock_hybrid.return_value = [
                    {"article": "Article 6", "text": "Article 6: High-risk AI systems", "score": 0.9}
                ]
                
                result = vector_tool.execute(query)
                
                assert result is not None
                assert isinstance(result, str)
                assert len(result) > 0
    
    def test_top_k_parameter_respected(self, vector_tool):
        """Test that top_k parameter limits results."""
        query = '{"query": "test query", "top_k": 3}'
        
        # Add multiple dummy chunks and embeddings
        vector_tool.chunks = [
            {"text": f"Result {i}", "article": f"Article {i}"} 
            for i in range(5)
        ]
        vector_tool.embeddings = [[0.1 * i] * 768 for i in range(5)]
        
        with patch('google.generativeai.embed_content', return_value={'embedding': [0.1] * 768}):
            with patch.object(vector_tool, '_hybrid_search') as mock_hybrid:
                mock_hybrid.return_value = [
                    {"article": f"Article {i}", "text": f"Result {i}", "score": 1.0 - i*0.1}
                    for i in range(3)
                ]
                result = vector_tool.execute(query)
                
                # Result should be limited by top_k
                assert result is not None
                assert isinstance(result, str)
                # Verify top_k was passed correctly
                mock_hybrid.assert_called_once()
                assert mock_hybrid.call_args[0][2] == 3  # top_k argument
    
    def test_default_top_k_value(self, vector_tool):
        """Test that default top_k is used when not specified."""
        query = '{"query": "test query"}'
        
        vector_tool.chunks = [{"text": "Result", "article": "Article 1"}]
        vector_tool.embeddings = [[0.1] * 768]
        
        with patch('google.generativeai.embed_content', return_value={'embedding': [0.1] * 768}):
            with patch.object(vector_tool, '_hybrid_search') as mock_hybrid:
                mock_hybrid.return_value = [{"article": "Article 1", "text": "Result", "score": 0.9}]
                result = vector_tool.execute(query)
                
                # Should return valid result with default top_k (3)
                assert result is not None
                assert isinstance(result, str)
                # Verify default top_k=3 was used
                mock_hybrid.assert_called_once()
                assert mock_hybrid.call_args[0][2] == 3  # default top_k
    
    def test_empty_query_handling(self, vector_tool):
        """Test handling of empty query string."""
        query = '{"query": ""}'
        
        vector_tool.chunks = [{"text": "Test content", "article": "Article 1"}]
        vector_tool.embeddings = [[0.1] * 768]
        
        with patch('google.generativeai.configure'):
            result = vector_tool.execute(query)
            # Should return error JSON for empty query
            assert result is not None
            assert isinstance(result, str)
            assert "error" in result.lower()
    
    def test_result_formatting(self, vector_tool):
        """Test that results are properly formatted."""
        query = '{"query": "test", "top_k": 2}'
        
        vector_tool.chunks = [
            {"text": "Content 1", "article": "Article 1"},
            {"text": "Content 2", "article": "Article 2"}
        ]
        vector_tool.embeddings = [[0.1] * 768, [0.2] * 768]
        
        with patch('google.generativeai.embed_content', return_value={'embedding': [0.1] * 768}):
            with patch.object(vector_tool, '_hybrid_search') as mock_hybrid:
                mock_hybrid.return_value = [
                    {"article": "Article 1", "text": "Content 1", "score": 0.9},
                    {"article": "Article 2", "text": "Content 2", "score": 0.8}
                ]
                result = vector_tool.execute(query)
                
                # Result should be a formatted JSON string
                assert result is not None
                assert isinstance(result, str)
                assert len(result) > 0
                assert "results" in result
    
    def test_metadata_inclusion(self, vector_tool):
        """Test that results include article references."""
        query = '{"query": "test", "top_k": 1}'
        
        vector_tool.chunks = [
            {"text": "Test content about prohibited practices", "article": "Article 5"}
        ]
        vector_tool.embeddings = [[0.1] * 768]
        
        with patch('google.generativeai.embed_content', return_value={'embedding': [0.1] * 768}):
            with patch.object(vector_tool, '_hybrid_search') as mock_hybrid:
                mock_hybrid.return_value = [
                    {"article": "Article 5", "text": "Test content about prohibited practices", "score": 0.95}
                ]
                result = vector_tool.execute(query)
                
                # Result should be a JSON string with article reference
                assert result is not None
                assert isinstance(result, str)
                assert "Article 5" in result


class TestVectorIndexCaching:
    """Test suite for vector index caching functionality."""
    
    def test_cache_directory_structure(self):
        """Test that cache directory has expected structure."""
        cache_base = "data/embeddings_cache"
        
        # Check that cache directories exist for each section
        sections = ["articles", "recitals", "annexes"]
        for section in sections:
            cache_path = os.path.join(cache_base, section)
            if os.path.exists(cache_base):
                # If cache exists, check structure
                assert os.path.exists(cache_path) or not os.path.exists(cache_base)
    
    def test_index_file_naming(self):
        """Test that index files follow expected naming convention."""
        cache_base = "data/embeddings_cache"
        sections = ["articles", "recitals", "annexes"]
        
        for section in sections:
            index_path = os.path.join(cache_base, section, "eu_ai_act_index.pkl")
            # If cache exists, index should exist
            if os.path.exists(os.path.join(cache_base, section)):
                assert os.path.exists(index_path), f"Index file missing for {section}"


class TestVectorSearchIntegration:
    """Integration tests for vector search functionality."""
    
    @pytest.mark.skipif(
        not os.path.exists("data/embeddings_cache/eu_ai_act_index.pkl"),
        reason="Vector index cache not available"
    )
    def test_real_search_articles(self):
        """Test real search on articles if cache is available."""
        tool = VectorIndexTool()
        query = '{"query": "high-risk AI systems", "top_k": 3}'
        
        result = tool.execute(query)
        
        assert result is not None
        assert len(result) > 0
        assert "Article" in result or "high" in result.lower()
    
    @pytest.mark.skipif(
        not os.path.exists("data/embeddings_cache/eu_ai_act_index.pkl"),
        reason="Vector index cache not available"
    )
    def test_real_search_recitals(self):
        """Test real search on recitals if cache is available."""
        tool = VectorIndexTool()
        query = '{"query": "fundamental rights", "top_k": 3}'
        
        result = tool.execute(query)
        
        assert result is not None
        assert len(result) > 0
    
    @pytest.mark.skipif(
        not os.path.exists("data/embeddings_cache/eu_ai_act_index.pkl"),
        reason="Vector index cache not available"
    )
    def test_real_search_annexes(self):
        """Test real search on annexes if cache is available."""
        tool = VectorIndexTool()
        query = '{"query": "technical documentation", "top_k": 3}'
        
        result = tool.execute(query)
        
        assert result is not None
        assert len(result) > 0


if __name__ == "__main__":
    # Generate test documentation JSON
    from test_utils import generate_test_documentation, save_test_documentation
    
    test_classes = [
        TestVectorIndexTool,
        TestVectorIndexCaching,
        TestVectorSearchIntegration
    ]
    
    docs = generate_test_documentation(__file__, test_classes)
    json_path = save_test_documentation(docs)
    print(f"\n✅ Test documentation generated: {json_path}\n")
    
    # Run tests
    pytest.main([__file__, "-v"])
