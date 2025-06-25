"""
Tests for the PDF parser module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from stmt_obfuscator.pdf_parser.parser import PDFParser


@pytest.fixture
def mock_pdf_document():
    """Create a mock PDF document for testing."""
    mock_doc = MagicMock()
    
    # Mock metadata
    mock_doc.metadata = {
        "title": "Test Bank Statement",
        "author": "Test Bank",
        "subject": "Monthly Statement",
        "keywords": "bank,statement,test",
        "creator": "PDF Generator",
    }
    
    # Mock page count
    mock_doc.__len__ = lambda self: 2
    
    # Mock pages with text blocks
    page1 = MagicMock()
    page1.get_text.return_value = {
        "blocks": [
            {
                "type": 0,  # Text block
                "lines": [
                    {
                        "spans": [
                            {
                                "text": "Test Bank",
                                "bbox": (10, 10, 100, 30),
                                "font": "Helvetica",
                                "size": 12,
                                "color": 0,
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    page2 = MagicMock()
    page2.get_text.return_value = {
        "blocks": [
            {
                "type": 0,  # Text block
                "lines": [
                    {
                        "spans": [
                            {
                                "text": "Account Number: 1234-5678-9012-3456",
                                "bbox": (10, 10, 300, 30),
                                "font": "Helvetica",
                                "size": 10,
                                "color": 0,
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    mock_doc.__iter__ = lambda self: iter([page1, page2])
    
    return mock_doc


def test_parser_initialization():
    """Test that the PDFParser initializes correctly."""
    parser = PDFParser()
    
    assert parser.document is None
    assert parser.page_count == 0
    assert parser.text_blocks == []
    assert parser.tables == []
    assert parser.metadata == {}


@patch('fitz.open')
def test_load_pdf_success(mock_open, mock_pdf_document, tmp_path):
    """Test loading a PDF file successfully."""
    # Create a temporary PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()
    
    # Configure the mock
    mock_open.return_value = mock_pdf_document
    
    # Load the PDF
    parser = PDFParser()
    result = parser.load_pdf(str(pdf_path))
    
    # Verify the result
    assert result is True
    assert parser.document is not None
    assert parser.page_count == 2
    assert parser.metadata == {
        "title": "Test Bank Statement",
        "author": "Test Bank",
        "subject": "Monthly Statement",
        "keywords": "bank,statement,test",
        "creator": "PDF Generator",
    }
    
    # Verify that the mock was called correctly
    mock_open.assert_called_once_with(str(pdf_path))


@patch('fitz.open')
def test_extract_text(mock_open, mock_pdf_document, tmp_path):
    """Test extracting text from a PDF file."""
    # Create a temporary PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()
    
    # Configure the mock
    mock_open.return_value = mock_pdf_document
    
    # Load the PDF and extract text
    parser = PDFParser()
    parser.load_pdf(str(pdf_path))
    text_blocks = parser.extract_text()
    
    # Verify the result
    assert len(text_blocks) == 2
    
    # Check first text block
    assert text_blocks[0]["page"] == 1
    assert text_blocks[0]["text"] == "Test Bank"
    assert text_blocks[0]["bbox"] == (10, 10, 100, 30)
    
    # Check second text block
    assert text_blocks[1]["page"] == 2
    assert text_blocks[1]["text"] == "Account Number: 1234-5678-9012-3456"
    assert text_blocks[1]["bbox"] == (10, 10, 300, 30)


def test_close():
    """Test closing the PDF document."""
    parser = PDFParser()
    parser.document = MagicMock()
    
    parser.close()
    
    # Verify that the document was closed
    parser.document.close.assert_called_once()
    assert parser.document is None