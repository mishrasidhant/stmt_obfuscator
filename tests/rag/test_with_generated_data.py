"""
Tests for the RAG Context Enhancer using generated test data.

This module demonstrates how to use the test data generator for RAG module tests.
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
from stmt_obfuscator.pii_detection.detector import PIIDetector
from tests.rag.test_data import RAGTestDataGenerator


class TestRAGWithGeneratedData:
    """Test suite for RAG using generated test data."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary directory for the ChromaDB cache."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def test_data_generator(self):
        """Create a test data generator."""
        return RAGTestDataGenerator(seed=42)

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
            yield enhancer

    def test_add_generated_patterns(self, mock_rag_enhancer, test_data_generator):
        """Test adding generated patterns to the RAG knowledge base."""
        # Generate test patterns
        patterns = test_data_generator.generate_patterns(count=5)
        
        # Add patterns to the RAG knowledge base
        for pattern_info in patterns:
            result = mock_rag_enhancer.add_pattern(
                pattern=pattern_info["pattern"],
                pattern_type=pattern_info["type"],
                example=pattern_info["example"]
            )
            assert result is True
        
        # Verify that the patterns were added
        assert mock_rag_enhancer.collection.add.call_count == 5

    def test_get_context_with_generated_data(self, mock_rag_enhancer, test_data_generator):
        """Test getting context with generated data."""
        # Generate test text with PII
        text, ground_truth = test_data_generator.generate_text_with_pii()
        
        # Mock the query results
        mock_results = test_data_generator.generate_query_results(text)
        mock_rag_enhancer.collection.query.return_value = mock_results
        
        # Get context
        context = mock_rag_enhancer.get_context(text)
        
        # Verify context
        assert context is not None
        assert "patterns" in context
        assert "examples" in context
        assert len(context["patterns"]) == len(mock_results["documents"][0])

    def test_pii_detection_with_generated_data(self, mock_rag_enhancer, test_data_generator):
        """Test PII detection with generated RAG context."""
        # Generate test text with PII
        text, ground_truth = test_data_generator.generate_text_with_pii()
        
        # Mock the query results
        mock_results = test_data_generator.generate_query_results(text)
        mock_rag_enhancer.collection.query.return_value = mock_results
        
        # Get context
        context = mock_rag_enhancer.get_context(text)
        
        # Mock the PIIDetector._send_to_ollama method
        with patch('stmt_obfuscator.pii_detection.detector.PIIDetector._send_to_ollama') as mock_send:
            # Create a response that includes the ground truth entities
            response = json.dumps(ground_truth)
            mock_send.return_value = response
            
            # Create a detector and detect PII
            detector = PIIDetector()
            result = detector.detect_pii(text, context)
            
            # Verify that the detector was called with the context
            args, kwargs = mock_send.call_args
            assert "Additional context for detection" in args[0]
            
            # Verify that the result contains the expected entities
            assert result is not None
            assert "entities" in result
            assert len(result["entities"]) == len(ground_truth["entities"])

    def test_real_chromadb_with_generated_data(self, temp_cache_dir, test_data_generator):
        """Test using a real ChromaDB instance with generated data."""
        # Skip if running in CI environment
        if os.environ.get("CI") == "true":
            pytest.skip("Skipping test with real ChromaDB in CI environment")
        
        # Create a real RAGContextEnhancer with a temporary cache directory
        with patch('stmt_obfuscator.config.CACHE_DIR', Path(temp_cache_dir)):
            enhancer = RAGContextEnhancer(collection_name="test_with_generated_data")
            
            # Generate test patterns
            patterns = test_data_generator.generate_patterns(count=10)
            
            # Add patterns to the RAG knowledge base
            for pattern_info in patterns:
                result = enhancer.add_pattern(
                    pattern=pattern_info["pattern"],
                    pattern_type=pattern_info["type"],
                    example=pattern_info["example"]
                )
                assert result is True
            
            # Generate test text with PII
            text, ground_truth = test_data_generator.generate_text_with_pii()
            
            # Get context
            context = enhancer.get_context(text)
            
            # Verify context
            assert context is not None
            assert "patterns" in context
            
            # Cleanup
            enhancer.collection.delete()