"""
Tests for the PII detection module.
"""

import pytest
from unittest.mock import patch, MagicMock

from stmt_obfuscator.pii_detection.detector import PIIDetector


@pytest.fixture
def mock_ollama_response():
    """Mock response from Ollama API."""
    return """
    {
      "entities": [
        {
          "type": "PERSON_NAME",
          "text": "John Doe",
          "start": 10,
          "end": 18,
          "confidence": 0.95
        },
        {
          "type": "ACCOUNT_NUMBER",
          "text": "1234-5678-9012-3456",
          "start": 42,
          "end": 61,
          "confidence": 0.98
        }
      ]
    }
    """


def test_detector_initialization():
    """Test that the PIIDetector initializes correctly."""
    detector = PIIDetector(model="test-model", host="http://test-host")
    
    assert detector.model == "test-model"
    assert detector.host == "http://test-host"
    assert detector.confidence_threshold == 0.85


@patch('requests.post')
def test_detect_pii(mock_post, mock_ollama_response):
    """Test PII detection with a mock response."""
    # Configure the mock
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": mock_ollama_response}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Create detector and detect PII
    detector = PIIDetector(model="test-model", host="http://test-host")
    result = detector.detect_pii("John Doe has account number 1234-5678-9012-3456")
    
    # Verify the result
    assert "entities" in result
    assert len(result["entities"]) == 2
    
    # Check first entity
    assert result["entities"][0]["type"] == "PERSON_NAME"
    assert result["entities"][0]["text"] == "John Doe"
    
    # Check second entity
    assert result["entities"][1]["type"] == "ACCOUNT_NUMBER"
    assert result["entities"][1]["text"] == "1234-5678-9012-3456"
    
    # Verify that the mock was called correctly
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://test-host/api/generate"
    assert kwargs["json"]["model"] == "test-model"
    assert "Bank statement text:" in kwargs["json"]["prompt"]


@patch('requests.post')
def test_confidence_threshold_filtering(mock_post):
    """Test that entities below the confidence threshold are filtered out."""
    # Configure the mock with a response containing entities with different confidence levels
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": """
    {
      "entities": [
        {
          "type": "PERSON_NAME",
          "text": "John Doe",
          "start": 10,
          "end": 18,
          "confidence": 0.95
        },
        {
          "type": "EMAIL",
          "text": "john.doe@example.com",
          "start": 30,
          "end": 50,
          "confidence": 0.80
        }
      ]
    }
    """}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Create detector with a higher confidence threshold
    detector = PIIDetector(model="test-model", host="http://test-host")
    detector.confidence_threshold = 0.90
    
    # Detect PII
    result = detector.detect_pii("John Doe has email john.doe@example.com")
    
    # Verify that only the high-confidence entity is included
    assert len(result["entities"]) == 1
    assert result["entities"][0]["type"] == "PERSON_NAME"