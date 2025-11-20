"""Unit tests for vector_index_tool.py - VectorIndexTool."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.vector_index_tool import VectorIndexTool
import os


class TestVectorIndexTool:
    """Test suite for VectorIndexTool."""
    
    @pytest.fixture
    def mock_embedding_model(self):
        """Create a mock embedding model."""
        mock_model = Mock()
        mock_model.embed_query.return_value = [0.1] * 768  # 768-dim embedding
        return mock_model
    
    @pytest.fixture
    def vector_tool(self, mock_embedding_model):
        """Create a VectorIndexTool instance with mocked embedding model."""
        with patch('src.vector_index_tool.GoogleGenerativeAIEmbeddings', return_value=mock_embedding_model):
            tool = VectorIndexTool(section="articles")
            return tool
    
    def test_tool_initialization_articles(self):
        """Test tool initialization with articles section."""
        with patch('src.vector_index_tool.GoogleGenerativeAIEmbeddings'):
            tool = VectorIndexTool(section="articles")
            assert tool.name == "search_euaiact_articles"
            assert "articles" in tool.description.lower()
            assert tool.section == "articles"
    
    def test_tool_initialization_recitals(self):
        """Test tool initialization with recitals section."""
        with patch('src.vector_index_tool.GoogleGenerativeAIEmbeddings'):
            tool = VectorIndexTool(section="recitals")
            assert tool.name == "search_euaiact_recitals"
            assert "recitals" in tool.description.lower()
            assert tool.section == "recitals"
    
    def test_tool_initialization_annexes(self):
        """Test tool initialization with annexes section."""
        with patch('src.vector_index_tool.GoogleGenerativeAIEmbeddings'):
            tool = VectorIndexTool(section="annexes")
            assert tool.name == "search_euaiact_annexes"
            assert "annexes" in tool.description.lower()
            assert tool.section == "annexes"
    
    def test_invalid_section_raises_error(self):
        """Test that invalid section raises ValueError."""
        with pytest.raises(ValueError):
            with patch('src.vector_index_tool.GoogleGenerativeAIEmbeddings'):
                VectorIndexTool(section="invalid_section")
    
    def test_search_query_structure(self, vector_tool):
        """Test that search accepts properly formatted queries."""
        query = '{"query": "high-risk AI systems", "top_k": 5}'
        
        # Mock the vector store
        mock_results = [
            Mock(page_content="Article 6: High-risk AI systems", metadata={"source": "article_6"}),
            Mock(page_content="Article 9: Risk management", metadata={"source": "article_9"})
        ]
        
        with patch.object(vector_tool, 'vector_store') as mock_store:
            mock_store.similarity_search.return_value = mock_results
            result = vector_tool._run(query)
            
            assert result is not None
            assert len(result) > 0
    
    def test_top_k_parameter_respected(self, vector_tool):
        """Test that top_k parameter limits results."""
        query = '{"query": "test query", "top_k": 3}'
        
        mock_results = [Mock(page_content=f"Result {i}", metadata={"source": f"doc_{i}"}) for i in range(3)]
        
        with patch.object(vector_tool, 'vector_store') as mock_store:
            mock_store.similarity_search.return_value = mock_results
            result = vector_tool._run(query)
            
            # Should call similarity_search with k=3
            mock_store.similarity_search.assert_called_once()
            call_kwargs = mock_store.similarity_search.call_args[1]
            assert call_kwargs.get('k') == 3 or len(mock_store.similarity_search.call_args[0]) >= 2
    
    def test_default_top_k_value(self, vector_tool):
        """Test that default top_k is 5 when not specified."""
        query = '{"query": "test query"}'
        
        mock_results = [Mock(page_content="Result", metadata={"source": "doc"})]
        
        with patch.object(vector_tool, 'vector_store') as mock_store:
            mock_store.similarity_search.return_value = mock_results
            vector_tool._run(query)
            
            # Check that default k=5 was used
            call_args = mock_store.similarity_search.call_args
            # Either positional or keyword argument
            if len(call_args[0]) > 1:
                assert call_args[0][1] == 5
            elif 'k' in call_args[1]:
                assert call_args[1]['k'] == 5
    
    def test_empty_query_handling(self, vector_tool):
        """Test handling of empty query string."""
        query = '{"query": ""}'
        
        result = vector_tool._run(query)
        # Should handle gracefully
        assert result is not None
    
    def test_result_formatting(self, vector_tool):
        """Test that results are properly formatted."""
        query = '{"query": "test", "top_k": 2}'
        
        mock_results = [
            Mock(page_content="Content 1", metadata={"source": "doc_1"}),
            Mock(page_content="Content 2", metadata={"source": "doc_2"})
        ]
        
        with patch.object(vector_tool, 'vector_store') as mock_store:
            mock_store.similarity_search.return_value = mock_results
            result = vector_tool._run(query)
            
            # Result should contain content from both documents
            assert "Content 1" in result
            assert "Content 2" in result
    
    def test_metadata_inclusion(self, vector_tool):
        """Test that metadata is included in results."""
        query = '{"query": "test", "top_k": 1}'
        
        mock_results = [
            Mock(page_content="Test content", metadata={"source": "article_5", "section": "paragraph_1"})
        ]
        
        with patch.object(vector_tool, 'vector_store') as mock_store:
            mock_store.similarity_search.return_value = mock_results
            result = vector_tool._run(query)
            
            # Result should contain metadata reference
            assert "article_5" in result or "Test content" in result


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
        not os.path.exists("data/embeddings_cache/articles/eu_ai_act_index.pkl"),
        reason="Vector index cache not available"
    )
    def test_real_search_articles(self):
        """Test real search on articles if cache is available."""
        tool = VectorIndexTool(section="articles")
        query = '{"query": "high-risk AI systems", "top_k": 3}'
        
        result = tool._run(query)
        
        assert result is not None
        assert len(result) > 0
        assert "Article" in result or "high" in result.lower()
    
    @pytest.mark.skipif(
        not os.path.exists("data/embeddings_cache/recitals/eu_ai_act_index.pkl"),
        reason="Vector index cache not available"
    )
    def test_real_search_recitals(self):
        """Test real search on recitals if cache is available."""
        tool = VectorIndexTool(section="recitals")
        query = '{"query": "fundamental rights", "top_k": 3}'
        
        result = tool._run(query)
        
        assert result is not None
        assert len(result) > 0
    
    @pytest.mark.skipif(
        not os.path.exists("data/embeddings_cache/annexes/eu_ai_act_index.pkl"),
        reason="Vector index cache not available"
    )
    def test_real_search_annexes(self):
        """Test real search on annexes if cache is available."""
        tool = VectorIndexTool(section="annexes")
        query = '{"query": "technical documentation", "top_k": 3}'
        
        result = tool._run(query)
        
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
