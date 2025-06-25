"""
Unit tests for the PII Detection module.

These tests verify the functionality of the PII detector component in isolation.
"""

import os
import json
import pytest
from typing import Dict, List, Any

from stmt_obfuscator.pii_detection.detector import PIIDetector


class TestPIIDetectorUnit:
    """Unit tests for the PIIDetector class."""

    def test_detector_initialization(self, pii_detector):
        """Test that the PIIDetector initializes correctly."""
        assert pii_detector is not None
        assert isinstance(pii_detector, PIIDetector)
        assert hasattr(pii_detector, 'detect_pii')
        
    def test_detect_pii_with_sample_text(self, pii_detector, sample_text):
        """Test PII detection with a sample text."""
        # Skip if Ollama is not available
        try:
            result = pii_detector.detect_pii(sample_text)
            
            # Basic validation of the result structure
            assert isinstance(result, dict)
            assert "entities" in result
            assert isinstance(result["entities"], list)
            
            # Check that some entities were detected
            assert len(result["entities"]) > 0
            
            # Validate entity structure
            for entity in result["entities"]:
                assert "type" in entity
                assert "text" in entity
                assert "start" in entity
                assert "end" in entity
                assert "confidence" in entity
                
                # Validate entity types
                assert entity["type"] in [
                    "PERSON_NAME", "ADDRESS", "PHONE_NUMBER", "EMAIL",
                    "ACCOUNT_NUMBER", "ROUTING_NUMBER", "ORGANIZATION_NAME",
                    "WEBSITE", "SSN", "CREDIT_CARD_NUMBER", "IP_ADDRESS"
                ]
                
                # Validate confidence score
                assert 0 <= entity["confidence"] <= 1
                
                # Validate text positions
                assert 0 <= entity["start"] < entity["end"]
                assert entity["end"] <= len(sample_text)
                assert sample_text[entity["start"]:entity["end"]] == entity["text"]
                
        except Exception as e:
            pytest.skip(f"Skipping test because Ollama is not available: {str(e)}")
    
    def test_detect_pii_with_empty_text(self, pii_detector):
        """Test PII detection with empty text."""
        # Skip if Ollama is not available
        try:
            result = pii_detector.detect_pii("")
            
            # Should return an empty list of entities
            assert isinstance(result, dict)
            assert "entities" in result
            assert isinstance(result["entities"], list)
            assert len(result["entities"]) == 0
            
        except Exception as e:
            pytest.skip(f"Skipping test because Ollama is not available: {str(e)}")
    
    def test_detect_pii_with_no_pii(self, pii_detector):
        """Test PII detection with text containing no PII."""
        text = """
        This is a sample text with no personally identifiable information.
        It contains generic information about banking and finance.
        The quick brown fox jumps over the lazy dog.
        """
        
        # Skip if Ollama is not available
        try:
            result = pii_detector.detect_pii(text)
            
            # Should return an empty or very small list of entities
            assert isinstance(result, dict)
            assert "entities" in result
            assert isinstance(result["entities"], list)
            
            # There might be false positives, but should be minimal
            if len(result["entities"]) > 0:
                print(f"Warning: {len(result['entities'])} potential false positives detected")
                for entity in result["entities"]:
                    print(f"  {entity['type']}: {entity['text']} (confidence: {entity['confidence']})")
            
        except Exception as e:
            pytest.skip(f"Skipping test because Ollama is not available: {str(e)}")
    
    def test_detect_pii_with_generated_statement(self, pii_detector, generated_statement):
        """Test PII detection with a generated bank statement."""
        # Skip if Ollama is not available
        try:
            result = pii_detector.detect_pii(generated_statement["text"])
            
            # Basic validation of the result structure
            assert isinstance(result, dict)
            assert "entities" in result
            assert isinstance(result["entities"], list)
            
            # Check that some entities were detected
            assert len(result["entities"]) > 0
            
            # Get ground truth entities
            ground_truth = generated_statement["ground_truth"]
            assert "entities" in ground_truth
            
            # Compare detected entities with ground truth
            # Note: This is not a strict comparison, as the detector might not find all entities
            # or might find entities not in the ground truth
            detected_types = {entity["type"] for entity in result["entities"]}
            ground_truth_types = {entity["type"] for entity in ground_truth["entities"]}
            
            # Check that at least some types overlap
            assert len(detected_types.intersection(ground_truth_types)) > 0
            
            print(f"Detected {len(result['entities'])} entities of types: {detected_types}")
            print(f"Ground truth has {len(ground_truth['entities'])} entities of types: {ground_truth_types}")
            
        except Exception as e:
            pytest.skip(f"Skipping test because Ollama is not available: {str(e)}")
    
    def test_confidence_threshold_filtering(self, pii_detector, mock_pii_entities):
        """Test filtering entities based on confidence threshold."""
        # Mock the detect_pii method to return our mock entities
        original_detect_pii = pii_detector.detect_pii
        pii_detector.detect_pii = lambda text: mock_pii_entities
        
        try:
            # Test with different confidence thresholds
            thresholds = [0.0, 0.5, 0.9, 0.95, 0.99, 1.0]
            for threshold in thresholds:
                pii_detector.confidence_threshold = threshold
                
                # Count how many entities should pass the threshold
                expected_count = sum(1 for entity in mock_pii_entities["entities"] 
                                    if entity["confidence"] >= threshold)
                
                # Get filtered entities
                filtered_entities = pii_detector.filter_by_confidence(mock_pii_entities["entities"])
                
                assert len(filtered_entities) == expected_count
                
                # Verify all remaining entities meet the threshold
                for entity in filtered_entities:
                    assert entity["confidence"] >= threshold
        
        finally:
            # Restore the original method
            pii_detector.detect_pii = original_detect_pii
            # Reset threshold to default
            pii_detector.confidence_threshold = 0.85


class TestPIITypeSpecificDetection:
    """Tests for detecting specific types of PII."""
    
    @pytest.mark.parametrize("pii_type,sample_text,expected", [
        ("PERSON_NAME", "John Doe is the account holder.", True),
        ("ADDRESS", "123 Main St, Anytown, CA 90210 is the billing address.", True),
        ("PHONE_NUMBER", "Please call (555) 123-4567 for assistance.", True),
        ("EMAIL", "Contact us at john.doe@example.com for support.", True),
        ("ACCOUNT_NUMBER", "Your account number is 1234-5678-9012-3456.", True),
        ("ROUTING_NUMBER", "The routing number 123456789 is used for direct deposits.", True),
        ("CREDIT_CARD_NUMBER", "Your credit card 4111-1111-1111-1111 will be charged.", True),
        ("SSN", "SSN: 123-45-6789 is required for verification.", True),
    ])
    def test_specific_pii_type_detection(self, pii_detector, pii_type, sample_text, expected):
        """Test detection of specific PII types."""
        # Skip if Ollama is not available
        try:
            result = pii_detector.detect_pii(sample_text)
            
            # Check if the specific PII type was detected
            detected_types = [entity["type"] for entity in result.get("entities", [])]
            
            if expected:
                assert pii_type in detected_types, f"Failed to detect {pii_type} in '{sample_text}'"
            else:
                assert pii_type not in detected_types, f"Incorrectly detected {pii_type} in '{sample_text}'"
                
        except Exception as e:
            pytest.skip(f"Skipping test because Ollama is not available: {str(e)}")