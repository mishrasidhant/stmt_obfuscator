"""Tests for the PDFPreviewGenerator module."""

import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from PyQt6.QtGui import QPixmap, QImage

from stmt_obfuscator.output_generator.pdf_formatter import PDFFormatter
from stmt_obfuscator.output_generator.pdf_preview import PDFPreviewGenerator


@pytest.fixture
def sample_document():
    """Return a sample document for testing."""
    return {
        "full_text": "This is a sample obfuscated bank statement.\n"
        "Account: XXXX-XXXX-XXXX-1234\n"
        "Name: XXXX XXXXX\n"
        "Balance: $1,234.56",
        "metadata": {
            "obfuscated": True,
            "obfuscation_timestamp": "2025-06-25T13:00:00",
            "entities_obfuscated": 3,
        },
        "text_blocks": [
            {"text": "This is a sample obfuscated bank statement."},
            {"text": "Account: XXXX-XXXX-XXXX-1234"},
            {"text": "Name: XXXX XXXXX"},
            {"text": "Balance: $1,234.56"},
        ],
    }


def test_init_pdf_preview_generator():
    """Test initializing the PDF preview generator."""
    # Test with default formatter
    preview_generator = PDFPreviewGenerator()
    assert preview_generator.pdf_formatter is not None
    assert isinstance(preview_generator.pdf_formatter, PDFFormatter)

    # Test with custom formatter
    custom_formatter = PDFFormatter(
        font="Times-Roman",
        font_size=14,
        margin=36,
    )
    preview_generator = PDFPreviewGenerator(pdf_formatter=custom_formatter)
    assert preview_generator.pdf_formatter is custom_formatter


def test_generate_preview(sample_document):
    """Test generating preview images."""
    # Create mock objects for QImage and QPixmap
    mock_qimage = MagicMock(spec=QImage)
    mock_qpixmap = MagicMock(spec=QPixmap)
    mock_qpixmap.width.return_value = 800
    mock_qpixmap.height.return_value = 600
    mock_qpixmap.isNull.return_value = False
    
    # Patch QImage and QPixmap.fromImage to avoid GUI operations
    with patch('stmt_obfuscator.output_generator.pdf_preview.QImage', return_value=mock_qimage), \
         patch('stmt_obfuscator.output_generator.pdf_preview.QPixmap.fromImage', return_value=mock_qpixmap):
        
        preview_generator = PDFPreviewGenerator()
        
        # Generate previews with default DPI
        pixmaps = preview_generator.generate_preview(sample_document)
        
        # Check that at least one preview was generated
        assert pixmaps
        assert len(pixmaps) > 0
        
        # Check that the pixmaps are our mocked objects
        for pixmap in pixmaps:
            assert pixmap is mock_qpixmap
        
        # Test with different DPI values
        for dpi in [72, 150, 300]:
            pixmaps = preview_generator.generate_preview(sample_document, dpi=dpi)
            assert len(pixmaps) > 0


def test_generate_preview_file(sample_document):
    """Test generating a temporary PDF file for preview."""
    preview_generator = PDFPreviewGenerator()
    
    # Generate a preview file
    temp_path = preview_generator.generate_preview_file(sample_document)
    
    # Check that the file exists and is a valid PDF
    assert temp_path is not None
    assert temp_path.exists()
    
    # Check that the file is a valid PDF
    with open(temp_path, "rb") as f:
        content = f.read(4)
    assert content == b"%PDF"
    
    # Check that the PDF has at least one page
    pdf_doc = fitz.open(temp_path)
    assert len(pdf_doc) > 0
    pdf_doc.close()
    
    # Clean up the temporary file
    temp_path.unlink()


def test_preview_matches_export(sample_document):
    """Test that the preview matches the exported PDF."""
    try:
        preview_generator = PDFPreviewGenerator()
        formatter = preview_generator.pdf_formatter
        
        # Generate a preview file
        preview_path = preview_generator.generate_preview_file(sample_document)
        
        # Generate an export file using the same formatter
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "export.pdf"
            
            # Create a new PDF document
            pdf_doc = fitz.open()
            
            # Format the document
            pdf_doc = formatter.format_document(sample_document, pdf_doc)
            
            # Save the PDF
            pdf_doc.save(export_path)
            pdf_doc.close()
            
            # Compare the two PDFs
            preview_doc = fitz.open(preview_path)
            export_doc = fitz.open(export_path)
            
            # Check that they have the same number of pages
            assert len(preview_doc) == len(export_doc)
            
            # Check that the page sizes match
            for i in range(len(preview_doc)):
                preview_page = preview_doc[i]
                export_page = export_doc[i]
                assert preview_page.rect.width == export_page.rect.width
                assert preview_page.rect.height == export_page.rect.height
            
            preview_doc.close()
            export_doc.close()
        
        # Clean up the temporary file
        if preview_path and preview_path.exists():
            preview_path.unlink()
    except Exception as e:
        # Clean up in case of exception
        if 'preview_path' in locals() and preview_path and preview_path.exists():
            try:
                preview_path.unlink()
            except:
                pass
        raise e