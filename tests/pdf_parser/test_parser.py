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
    assert parser.document_structure is not None
    assert parser.validation_errors == []


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
    assert text_blocks[0].page == 1
    assert text_blocks[0].text == "Test Bank"
    assert text_blocks[0].bbox == (10, 10, 100, 30)
    
    # Check second text block
    assert text_blocks[1].page == 2
    assert text_blocks[1].text == "Account Number: 1234-5678-9012-3456"
    assert text_blocks[1].bbox == (10, 10, 300, 30)


def test_close():
    """Test closing the PDF document."""
    parser = PDFParser()
    parser.document = MagicMock()
    
    parser.close()
    
    # Verify that the document was closed
    parser.document.close.assert_called_once()
    assert parser.document is None


@patch('fitz.open')
def test_validate_pdf_structure(mock_open, mock_pdf_document, tmp_path):
    """Test validating PDF structure."""
    # Create a temporary PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()
    
    # Configure the mock
    mock_open.return_value = mock_pdf_document
    
    # Mock is_encrypted property
    mock_pdf_document.is_encrypted = False
    
    # Load the PDF and validate structure
    parser = PDFParser()
    parser.load_pdf(str(pdf_path))
    validation_results = parser.validate_pdf_structure()
    
    # Verify the result
    assert validation_results["valid"] is True
    assert len(validation_results["errors"]) == 0
    assert "validation_results" in parser.document_structure.__dict__


@patch('fitz.open')
def test_detect_tables(mock_open, mock_pdf_document, tmp_path):
    """Test detecting tables in a PDF file."""
    # Create a temporary PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()
    
    # Configure the mock
    mock_open.return_value = mock_pdf_document
    
    # Add page dimensions to mock
    page1 = list(mock_pdf_document)[0]
    page1.rect = MagicMock()
    page1.rect.width = 612
    page1.rect.height = 792
    
    page2 = list(mock_pdf_document)[1]
    page2.rect = MagicMock()
    page2.rect.width = 612
    page2.rect.height = 792
    
    # Load the PDF, extract text, and detect tables
    parser = PDFParser()
    parser.load_pdf(str(pdf_path))
    parser.extract_text()
    tables = parser.detect_tables()
    
    # Verify the result
    assert isinstance(tables, list)
    # Note: With our test data, we don't expect to find tables
    # This just verifies the method runs without errors


@patch('fitz.open')
def test_get_document_structure(mock_open, mock_pdf_document, tmp_path):
    """Test getting document structure."""
    # Create a temporary PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()
    
    # Configure the mock
    mock_open.return_value = mock_pdf_document
    
    # Add page dimensions to mock
    for page in mock_pdf_document:
        page.rect = MagicMock()
        page.rect.width = 612
        page.rect.height = 792
    
    # Load the PDF and get document structure
    parser = PDFParser()
    parser.load_pdf(str(pdf_path))
    parser.extract_text()
    doc_structure = parser.get_document_structure()
    
    # Verify the result
    assert doc_structure.metadata == parser.metadata
    assert doc_structure.page_count == parser.page_count
    assert len(doc_structure.text_blocks) == len(parser.text_blocks)
    assert "layout_analysis" in doc_structure.__dict__


@patch('fitz.open')
def test_get_text_for_pii_detection(mock_open, mock_pdf_document, tmp_path):
    """Test getting text formatted for PII detection."""
    # Create a temporary PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()
    
    # Configure the mock
    mock_open.return_value = mock_pdf_document
    
    # Add page dimensions to mock
    for page in mock_pdf_document:
        page.rect = MagicMock()
        page.rect.width = 612
        page.rect.height = 792
    
    # Load the PDF and get text for PII detection
    parser = PDFParser()
    parser.load_pdf(str(pdf_path))
    parser.extract_text()
    document_text = parser.get_text_for_pii_detection()
    
    # Verify the result
    assert "metadata" in document_text
    assert "full_text" in document_text
    assert "text_blocks" in document_text
    assert "layout_map" in document_text
    assert len(document_text["text_blocks"]) == 2


@patch('fitz.open')
def test_chunk_document_for_pii_detection(mock_open, mock_pdf_document, tmp_path):
    """Test chunking document for PII detection."""
    # Create a temporary PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()
    
    # Configure the mock
    mock_open.return_value = mock_pdf_document
    
    # Add page dimensions to mock
    for page in mock_pdf_document:
        page.rect = MagicMock()
        page.rect.width = 612
        page.rect.height = 792
    
    # Load the PDF and chunk document for PII detection
    parser = PDFParser()
    parser.load_pdf(str(pdf_path))
    parser.extract_text()
    chunks = parser.chunk_document_for_pii_detection()
    
    # Verify the result
    assert isinstance(chunks, list)
    # Our test document is small, so it should be a single chunk
    assert len(chunks) > 0