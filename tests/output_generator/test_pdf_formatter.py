"""Tests for the PDFFormatter module."""

import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest

from stmt_obfuscator.output_generator.pdf_formatter import PDFFormatter


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


def test_format_document(sample_document):
    """Test formatting a document as a PDF."""
    formatter = PDFFormatter()

    # Create a new PDF document
    pdf_doc = fitz.open()

    # Format the document
    result = formatter.format_document(sample_document, pdf_doc)

    # Check that the document was formatted successfully
    assert result is not None
    assert len(result) > 0  # At least one page

    # Save the PDF to a temporary file for inspection
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_format.pdf"
        result.save(output_path)

        # Check that the file exists and is a valid PDF
        assert output_path.exists()

        # Check that the file is a valid PDF (starts with %PDF)
        with open(output_path, "rb") as f:
            content = f.read(4)

        assert content == b"%PDF"


def test_add_header(sample_document):
    """Test adding a header to a PDF document."""
    formatter = PDFFormatter()

    # Create a new PDF document
    pdf_doc = fitz.open()
    pdf_doc.new_page()

    # Add header
    formatter.add_header(pdf_doc, sample_document)

    # Check that the document still has one page
    assert len(pdf_doc) == 1

    # Save the PDF to a temporary file for inspection
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_header.pdf"
        pdf_doc.save(output_path)

        # Check that the file exists
        assert output_path.exists()


def test_add_content(sample_document):
    """Test adding content to a PDF document."""
    formatter = PDFFormatter()

    # Create a new PDF document
    pdf_doc = fitz.open()
    pdf_doc.new_page()

    # Add content
    formatter.add_content(pdf_doc, sample_document)

    # Check that the document still has one page
    assert len(pdf_doc) == 1

    # Save the PDF to a temporary file for inspection
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_content.pdf"
        pdf_doc.save(output_path)

        # Check that the file exists
        assert output_path.exists()


def test_add_footer(sample_document):
    """Test adding a footer to a PDF document."""
    formatter = PDFFormatter()

    # Create a new PDF document
    pdf_doc = fitz.open()
    pdf_doc.new_page()

    # Add footer
    formatter.add_footer(pdf_doc, sample_document)

    # Check that the document still has one page
    assert len(pdf_doc) == 1

    # Save the PDF to a temporary file for inspection
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_footer.pdf"
        pdf_doc.save(output_path)

        # Check that the file exists
        assert output_path.exists()


def test_custom_formatting_options():
    """Test custom formatting options."""
    # Create a formatter with custom options
    formatter = PDFFormatter(
        font="Times-Roman",
        font_size=14,
        margin=36,
        include_timestamp=False,
        include_metadata=False,
    )

    # Check that the options were set correctly
    assert formatter.font == "Times-Roman"
    assert formatter.font_size == 14
    assert formatter.margin == 36
    assert formatter.include_timestamp is False
    assert formatter.include_metadata is False


def test_wrap_text():
    """Test text wrapping functionality."""
    formatter = PDFFormatter(margin=72)  # 1 inch margin

    # Create a sample text with long lines
    sample_line = (
        "This is a very long line that should be wrapped to fit within margins. "
    )
    text = sample_line * 5

    text += "\nThis is a paragraph with some very long words like "
    text += "supercalifragilisticexpialidocious"
    text += " and pneumonoultramicroscopicsilicovolcanoconiosis."
    text += "\n\nThis is a paragraph after an empty line."

    # Calculate available width (assuming a standard letter page width of 612 points)
    page_width = 612
    start_x = formatter.margin

    # Wrap the text
    wrapped_lines = formatter.wrap_text(text, page_width, start_x)

    # Verify that the text was wrapped
    assert len(wrapped_lines) > 5  # Should be more than 5 lines after wrapping

    # Verify that each line fits within the margins
    available_width = page_width - start_x - formatter.margin
    for line in wrapped_lines:
        if line:  # Skip empty lines
            line_width = fitz.get_text_length(
                line, fontname=formatter.font, fontsize=formatter.font_size
            )
            assert line_width <= available_width, f"Line too long: {line}"

    # Verify that paragraphs are preserved
    assert "" in wrapped_lines  # Empty line should be preserved

    # Verify that long words are properly handled
    long_words = [
        "supercalifragilisticexpialidocious",
        "pneumonoultramicroscopicsilicovolcanoconiosis",
    ]
    for word in long_words:
        # Check that the long word was split across lines
        found = False
        for line in wrapped_lines:
            if word[:10] in line:  # Check for the beginning of the word
                found = True
                break
        assert found, f"Long word not properly handled: {word}"
