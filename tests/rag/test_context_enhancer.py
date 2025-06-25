"""
Unit tests for the RAG Context Enhancer module.

This module contains tests for the RAGContextEnhancer class.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import chromadb
from chromadb.config import Settings

from stmt_obfuscator.rag.context_enhancer import RAGContextEnhancer


class TestRAGContextEnhancer:
    """Test suite for the RAGContextEnhancer class."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary directory for the ChromaDB cache."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_chromadb_client(self):
        """Create a mock ChromaDB client."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        return mock_client, mock_collection

    @pytest.fixture
    def mock_rag_enhancer(self, mock_chromadb_client):
        """Create a mock RAGContextEnhancer with a mocked ChromaDB client."""
        mock_client, mock_collection = mock_chromadb_client
        
        with patch('chromadb.PersistentClient', return_value=mock_client):
            enhancer = RAGContextEnhancer(collection_name="test_collection")
            enhancer.collection = mock_collection
            # We don't want to mock add_pattern completely as it would break the tests
            # that check its behavior
            yield enhancer

    def test_init(self):
        """Test initialization of RAGContextEnhancer."""
        with patch('chromadb.PersistentClient') as mock_client_class:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_client_class.return_value = mock_client
            
            enhancer = RAGContextEnhancer(collection_name="test_collection")
            
            assert enhancer.collection_name == "test_collection"
            assert enhancer.enabled is True
            mock_client.get_or_create_collection.assert_called_once_with(
                name="test_collection",
                metadata={"description": "PII patterns for bank statements"}
            )

    def test_init_exception(self):
        """Test initialization with exception."""
        with patch('chromadb.PersistentClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.get_or_create_collection.side_effect = Exception("Test exception")
            mock_client_class.return_value = mock_client
            
            enhancer = RAGContextEnhancer(collection_name="test_collection")
            
            assert enhancer.enabled is False

    def test_get_context_disabled(self, mock_rag_enhancer):
        """Test get_context when RAG is disabled."""
        mock_rag_enhancer.enabled = False
        
        result = mock_rag_enhancer.get_context("Test text")
        
        assert result is None

    def test_get_context_no_results(self, mock_rag_enhancer):
        """Test get_context when no results are found."""
        mock_rag_enhancer.collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        
        result = mock_rag_enhancer.get_context("Test text")
        
        assert result is None
        mock_rag_enhancer.collection.query.assert_called_once_with(
            query_texts=["Test text"],
            n_results=5
        )

    def test_get_context_with_results(self, mock_rag_enhancer):
        """Test get_context with results."""
        mock_rag_enhancer.collection.query.return_value = {
            "documents": [["pattern1", "pattern2"]],
            "metadatas": [[
                {"type": "ACCOUNT_NUMBER", "example": "1234-5678-9012-3456"},
                {"type": "PERSON_NAME"}
            ]],
            "distances": [[0.1, 0.2]]
        }
        
        result = mock_rag_enhancer.get_context("Test text")
        
        assert result is not None
        assert "patterns" in result
        assert "examples" in result
        assert len(result["patterns"]) == 2
        assert len(result["examples"]) == 1
        
        assert result["patterns"][0]["type"] == "ACCOUNT_NUMBER"
        assert result["patterns"][0]["pattern"] == "pattern1"
        assert result["patterns"][0]["score"] == 0.1
        
        assert result["patterns"][1]["type"] == "PERSON_NAME"
        assert result["patterns"][1]["pattern"] == "pattern2"
        assert result["patterns"][1]["score"] == 0.2
        
        assert result["examples"][0]["type"] == "ACCOUNT_NUMBER"
        assert result["examples"][0]["text"] == "1234-5678-9012-3456"

    def test_get_context_exception(self, mock_rag_enhancer):
        """Test get_context with exception."""
        mock_rag_enhancer.collection.query.side_effect = Exception("Test exception")
        
        result = mock_rag_enhancer.get_context("Test text")
        
        assert result is None

    def test_add_pattern_disabled(self, mock_rag_enhancer):
        """Test add_pattern when RAG is disabled."""
        mock_rag_enhancer.enabled = False
        
        result = mock_rag_enhancer.add_pattern("pattern", "ACCOUNT_NUMBER")
        
        assert result is False
        mock_rag_enhancer.collection.add.assert_not_called()

    def test_add_pattern_success(self, mock_rag_enhancer):
        """Test add_pattern success."""
        result = mock_rag_enhancer.add_pattern("pattern", "ACCOUNT_NUMBER", "example")
        
        assert result is True
        mock_rag_enhancer.collection.add.assert_called_once()
        args, kwargs = mock_rag_enhancer.collection.add.call_args
        
        assert kwargs["documents"] == ["pattern"]
        assert kwargs["metadatas"] == [{"type": "ACCOUNT_NUMBER", "example": "example"}]
        assert "ids" in kwargs

    def test_add_pattern_without_example(self, mock_rag_enhancer):
        """Test add_pattern without example."""
        result = mock_rag_enhancer.add_pattern("pattern", "ACCOUNT_NUMBER")
        
        assert result is True
        mock_rag_enhancer.collection.add.assert_called_once()
        args, kwargs = mock_rag_enhancer.collection.add.call_args
        
        assert kwargs["documents"] == ["pattern"]
        assert kwargs["metadatas"] == [{"type": "ACCOUNT_NUMBER"}]
        assert "ids" in kwargs

    def test_add_pattern_exception(self, mock_rag_enhancer):
        """Test add_pattern with exception."""
        mock_rag_enhancer.collection.add.side_effect = Exception("Test exception")
        
        result = mock_rag_enhancer.add_pattern("pattern", "ACCOUNT_NUMBER")
        
        assert result is False

    def test_initialize_knowledge_base_disabled(self, mock_rag_enhancer):
        """Test initialize_knowledge_base when RAG is disabled."""
        mock_rag_enhancer.enabled = False
        
        result = mock_rag_enhancer.initialize_knowledge_base()
        
        assert result is False

    def test_initialize_knowledge_base_already_initialized(self, mock_rag_enhancer):
        """Test initialize_knowledge_base when already initialized."""
        mock_rag_enhancer.collection.count.return_value = 10
        
        # Spy on the add_pattern method to check if it's called
        with patch.object(mock_rag_enhancer, 'add_pattern', wraps=mock_rag_enhancer.add_pattern) as spy:
            result = mock_rag_enhancer.initialize_knowledge_base()
            
            assert result is True
            # Verify add_pattern was not called
            assert spy.call_count == 0

    def test_initialize_knowledge_base_success(self, mock_rag_enhancer):
        """Test initialize_knowledge_base success."""
        mock_rag_enhancer.collection.count.return_value = 0
        
        # Spy on the add_pattern method to check if it's called
        with patch.object(mock_rag_enhancer, 'add_pattern', wraps=mock_rag_enhancer.add_pattern) as spy:
            # Make the spy return True
            spy.return_value = True
            
            result = mock_rag_enhancer.initialize_knowledge_base()
            
            assert result is True
            # There are 9 patterns in the default initialization
            assert spy.call_count == 9

    def test_initialize_knowledge_base_exception(self, mock_rag_enhancer):
        """Test initialize_knowledge_base with exception."""
        mock_rag_enhancer.collection.count.side_effect = Exception("Test exception")
        
        result = mock_rag_enhancer.initialize_knowledge_base()
        
        assert result is False