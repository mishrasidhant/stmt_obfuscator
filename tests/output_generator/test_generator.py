"""
Tests for the OutputGenerator module.
"""

import os
import tempfile
from pathlib import Path
import pytest

from stmt_obfuscator.output_generator.generator import OutputGenerator


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
            "entities_obfuscated": 3
        },
        "text_blocks": [
            {
                "text": "This is a sample obfuscated bank statement."
            },
            {
                "text": "Account: XXXX-XXXX-XXXX-1234"
            },
            {
                "text": "Name: XXXX XXXXX"
            },
            {
                "text": "Balance: $1,234.56"
            }
        ]
    }


def test_generate_text_output(sample_document):
    """Test generating text output."""
    generator = OutputGenerator()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.txt"
        
        # Generate text output
        result = generator.generate_text(sample_document, output_path)
        
        # Check that the output was generated successfully
        assert result is True
        assert output_path.exists()
        
        # Check the content of the output file
        with open(output_path, "r") as f:
            content = f.read()
        
        assert content == sample_document["full_text"]


def test_generate_pdf_output(sample_document):
    """Test generating PDF output."""
    generator = OutputGenerator()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.pdf"
        
        # Generate PDF output
        result = generator.generate_pdf(sample_document, output_path)
        
        # Check that the output was generated successfully
        assert result is True
        assert output_path.exists()
        
        # Check that the file is a valid PDF (starts with %PDF)
        with open(output_path, "rb") as f:
            content = f.read(4)
        
        assert content == b"%PDF"


def test_generate_output_with_format(sample_document):
    """Test generating output with different formats."""
    generator = OutputGenerator()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test text format
        text_path = Path(temp_dir) / "test_output.txt"
        text_result = generator.generate_output(sample_document, text_path, format="text")
        
        assert text_result is True
        assert text_path.exists()
        
        # Test PDF format
        pdf_path = Path(temp_dir) / "test_output.pdf"
        pdf_result = generator.generate_output(sample_document, pdf_path, format="pdf")
        
        assert pdf_result is True
        assert pdf_path.exists()


def test_generate_output_with_invalid_format(sample_document):
    """Test generating output with an invalid format."""
    generator = OutputGenerator()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Invalid format should default to text
        output_path = Path(temp_dir) / "test_output.txt"
        result = generator.generate_output(sample_document, output_path, format="invalid")
        
        assert result is True
        assert output_path.exists()
        
        # Check the content of the output file
        with open(output_path, "r") as f:
            content = f.read()
        
        assert content == sample_document["full_text"]


def test_generate_output_with_disabled_pdf(sample_document):
    """Test generating PDF output when PDF export is disabled."""
    generator = OutputGenerator(pdf_export_enabled=False)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.pdf"
        
        # Generate PDF output
        result = generator.generate_output(sample_document, output_path, format="pdf")
        
        # Check that the output was not generated
        assert result is False
        assert not output_path.exists()