"""
Integration tests for the RAG Context Enhancer module.

This module contains tests for the integration between the RAG module and other components.
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


class TestRAGIntegration:
    """Test suite for RAG integration with other components."""

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
            yield enhancer

    @pytest.fixture
    def mock_pii_detector(self):
        """Create a mock PIIDetector."""
        with patch('stmt_obfuscator.pii_detection.detector.PIIDetector._send_to_ollama') as mock_send:
            mock_send.return_value = json.dumps({
                "entities": [
                    {
                        "type": "PERSON_NAME",
                        "text": "John Doe",
                        "start": 10,
                        "end": 18,
                        "confidence": 0.95
                    }
                ]
            })
            detector = PIIDetector()
            yield detector

    def test_rag_enhances_pii_detection(self, mock_rag_enhancer, mock_pii_detector):
        """Test that RAG context enhances PII detection."""
        # Setup RAG context
        mock_rag_enhancer.collection.query.return_value = {
            "documents": [["\\b[A-Z][a-z]+ [A-Z][a-z]+\\b"]],
            "metadatas": [[{"type": "PERSON_NAME", "example": "John Doe"}]],
            "distances": [[0.1]]
        }
        
        # Mock the PIIDetector._send_to_ollama method to return different responses based on input
        def mock_send_to_ollama(prompt):
            if "Additional context for detection" in prompt:
                # With RAG context, return more entities
                return json.dumps({
                    "entities": [
                        {
                            "type": "PERSON_NAME",
                            "text": "John Doe",
                            "start": 10,
                            "end": 18,
                            "confidence": 0.95
                        },
                        {
                            "type": "PERSON_NAME",
                            "text": "Jane Smith",
                            "start": 30,
                            "end": 40,
                            "confidence": 0.92
                        }
                    ]
                })
            else:
                # Without RAG context, return fewer entities
                return json.dumps({
                    "entities": [
                        {
                            "type": "PERSON_NAME",
                            "text": "John Doe",
                            "start": 10,
                            "end": 18,
                            "confidence": 0.90
                        }
                    ]
                })
        
        with patch('stmt_obfuscator.pii_detection.detector.PIIDetector._send_to_ollama', side_effect=mock_send_to_ollama):
            # Test text with names
            test_text = "Hello, John Doe and Jane Smith. How are you today?"
            
            # Detect PII without RAG context
            result_without_rag = mock_pii_detector.detect_pii(test_text)
            
            # Detect PII with RAG context
            rag_context = mock_rag_enhancer.get_context(test_text)
            result_with_rag = mock_pii_detector.detect_pii(test_text, rag_context)
            
            # Verify that RAG context improved detection
            assert len(result_without_rag["entities"]) < len(result_with_rag["entities"])
            assert any(entity["text"] == "Jane Smith" for entity in result_with_rag["entities"])

    def test_rag_improves_confidence_scores(self, mock_rag_enhancer, mock_pii_detector):
        """Test that RAG context improves confidence scores in PII detection."""
        # Setup RAG context
        mock_rag_enhancer.collection.query.return_value = {
            "documents": [["\\b[A-Z][a-z]+ [A-Z][a-z]+\\b"]],
            "metadatas": [[{"type": "PERSON_NAME", "example": "John Doe"}]],
            "distances": [[0.1]]
        }
        
        # Mock the PIIDetector._send_to_ollama method to return different confidence scores
        def mock_send_to_ollama(prompt):
            if "Additional context for detection" in prompt:
                # With RAG context, return higher confidence
                return json.dumps({
                    "entities": [
                        {
                            "type": "PERSON_NAME",
                            "text": "John Doe",
                            "start": 10,
                            "end": 18,
                            "confidence": 0.98  # Higher confidence with RAG
                        }
                    ]
                })
            else:
                # Without RAG context, return lower confidence
                return json.dumps({
                    "entities": [
                        {
                            "type": "PERSON_NAME",
                            "text": "John Doe",
                            "start": 10,
                            "end": 18,
                            "confidence": 0.85  # Lower confidence without RAG
                        }
                    ]
                })
        
        with patch('stmt_obfuscator.pii_detection.detector.PIIDetector._send_to_ollama', side_effect=mock_send_to_ollama):
            # Test text with names
            test_text = "Hello, John Doe. How are you today?"
            
            # Detect PII without RAG context
            result_without_rag = mock_pii_detector.detect_pii(test_text)
            
            # Detect PII with RAG context
            rag_context = mock_rag_enhancer.get_context(test_text)
            result_with_rag = mock_pii_detector.detect_pii(test_text, rag_context)
            
            # Verify that RAG context improved confidence
            assert result_without_rag["entities"][0]["confidence"] < result_with_rag["entities"][0]["confidence"]

    def test_rag_helps_detect_edge_cases(self, mock_rag_enhancer, mock_pii_detector):
        """Test that RAG context helps detect edge cases."""
        # Setup RAG context with a specific pattern for partially masked account numbers
        mock_rag_enhancer.collection.query.return_value = {
            "documents": [["\\bXXXX[-\\s]?XXXX[-\\s]?XXXX[-\\s]?\\d{4}\\b"]],
            "metadatas": [[{"type": "ACCOUNT_NUMBER", "example": "XXXX-XXXX-XXXX-1234"}]],
            "distances": [[0.1]]
        }
        
        # Mock the PIIDetector._send_to_ollama method to handle edge cases
        def mock_send_to_ollama(prompt):
            if "Additional context for detection" in prompt:
                # With RAG context, detect the masked account number
                return json.dumps({
                    "entities": [
                        {
                            "type": "ACCOUNT_NUMBER",
                            "text": "XXXX-XXXX-XXXX-5678",
                            "start": 20,
                            "end": 39,
                            "confidence": 0.95
                        }
                    ]
                })
            else:
                # Without RAG context, miss the masked account number
                return json.dumps({
                    "entities": []
                })
        
        with patch('stmt_obfuscator.pii_detection.detector.PIIDetector._send_to_ollama', side_effect=mock_send_to_ollama):
            # Test text with masked account number
            test_text = "Your account number XXXX-XXXX-XXXX-5678 is confidential."
            
            # Detect PII without RAG context
            result_without_rag = mock_pii_detector.detect_pii(test_text)
            
            # Detect PII with RAG context
            rag_context = mock_rag_enhancer.get_context(test_text)
            result_with_rag = mock_pii_detector.detect_pii(test_text, rag_context)
            
            # Verify that RAG context helped detect the edge case
            assert len(result_without_rag["entities"]) == 0
            assert len(result_with_rag["entities"]) == 1
            assert result_with_rag["entities"][0]["type"] == "ACCOUNT_NUMBER"

    def test_rag_with_chromadb_integration(self, temp_cache_dir):
        """Test integration with actual ChromaDB (not mocked)."""
        # Use a temporary directory for ChromaDB
        with patch('stmt_obfuscator.config.CACHE_DIR', Path(temp_cache_dir)):
            # Create a real RAGContextEnhancer
            enhancer = RAGContextEnhancer(collection_name="test_integration")
            
            # Add some test patterns
            enhancer.add_pattern(
                pattern=r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                pattern_type="ACCOUNT_NUMBER",
                example="1234-5678-9012-3456"
            )
            
            enhancer.add_pattern(
                pattern=r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
                pattern_type="PERSON_NAME",
                example="John Doe"
            )
            
            # Test getting context
            test_text = "Hello, John Smith. Your account number is 1111-2222-3333-4444."
            context = enhancer.get_context(test_text)
            
            # Verify context contains relevant patterns
            assert context is not None
            assert "patterns" in context
            assert len(context["patterns"]) > 0
            
            # Verify at least one pattern is for PERSON_NAME or ACCOUNT_NUMBER
            pattern_types = [p["type"] for p in context["patterns"]]
            assert "PERSON_NAME" in pattern_types or "ACCOUNT_NUMBER" in pattern_types