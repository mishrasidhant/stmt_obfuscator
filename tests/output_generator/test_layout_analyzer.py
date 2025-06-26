"""Tests for the LayoutAnalyzer module."""

import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest

from stmt_obfuscator.output_generator.layout_analyzer import (
    LayoutAnalyzer,
    LayoutElement,
    create_layout_mapping,
)


@pytest.fixture
def sample_pdf():
    """Create a sample PDF for testing."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
    
    # Create a new PDF document
    pdf_doc = fitz.open()
    
    # Add a page
    page = pdf_doc.new_page()
    
    # Add some text elements with different alignments
    # Left-aligned text
    page.insert_text((72, 72), "Left-aligned text", fontname="Helvetica", fontsize=12)
    
    # Center-aligned text
    center_text = "Center-aligned text"
    text_width = fitz.get_text_length(center_text, fontname="Helvetica", fontsize=12)
    x = (page.rect.width - text_width) / 2
    page.insert_text((x, 100), center_text, fontname="Helvetica", fontsize=12)
    
    # Right-aligned text
    right_text = "Right-aligned text"
    text_width = fitz.get_text_length(right_text, fontname="Helvetica", fontsize=12)
    x = page.rect.width - 72 - text_width
    page.insert_text((x, 128), right_text, fontname="Helvetica", fontsize=12)
    
    # Add a header
    header_text = "Document Header"
    text_width = fitz.get_text_length(header_text, fontname="Helvetica", fontsize=14)
    x = (page.rect.width - text_width) / 2
    page.insert_text((x, 36), header_text, fontname="Helvetica", fontsize=14)
    
    # Add a footer
    footer_text = "Page 1"
    text_width = fitz.get_text_length(footer_text, fontname="Helvetica", fontsize=10)
    x = (page.rect.width - text_width) / 2
    page.insert_text((x, page.rect.height - 36), footer_text, fontname="Helvetica", fontsize=10)
    
    # Save the PDF
    pdf_doc.save(temp_path)
    pdf_doc.close()
    
    yield temp_path
    
    # Clean up
    temp_path.unlink()


def test_layout_element_initialization():
    """Test initializing a LayoutElement."""
    element = LayoutElement(
        element_type="text",
        bbox=(10, 20, 100, 30),
        content="Sample text",
        attributes={"font": "Helvetica", "font_size": 12}
    )
    
    assert element.element_type == "text"
    assert element.bbox == (10, 20, 100, 30)
    assert element.content == "Sample text"
    assert element.attributes == {"font": "Helvetica", "font_size": 12}
    
    # Test with default attributes
    element = LayoutElement(
        element_type="image",
        bbox=(10, 20, 100, 30),
        content=None
    )
    
    assert element.element_type == "image"
    assert element.attributes == {}


def test_layout_analyzer_initialization():
    """Test initializing a LayoutAnalyzer."""
    analyzer = LayoutAnalyzer()
    assert analyzer.detail_level == "medium"
    
    analyzer = LayoutAnalyzer(detail_level="high")
    assert analyzer.detail_level == "high"


def test_analyze_document(sample_pdf):
    """Test analyzing a document's layout."""
    analyzer = LayoutAnalyzer()
    
    with fitz.open(sample_pdf) as pdf_doc:
        layout_map = analyzer.analyze_document(pdf_doc)
        
        # Check that we have layout information for the page
        assert 0 in layout_map
        
        # Check that we have elements on the page
        elements = layout_map[0]
        assert len(elements) > 0
        
        # Check that elements are LayoutElement instances
        for element in elements:
            assert isinstance(element, LayoutElement)
            
        # Check that we have text elements
        text_elements = [e for e in elements if e.element_type == "text"]
        assert len(text_elements) > 0
        
        # Check that elements have appropriate attributes
        for element in text_elements:
            assert "alignment" in element.attributes
            assert element.attributes["alignment"] in ["left", "center", "right"]


def test_determine_alignment():
    """Test determining text alignment."""
    analyzer = LayoutAnalyzer()
    
    # Test left alignment
    assert analyzer._determine_alignment((10, 20, 100, 30), 612) == "left"
    
    # Test center alignment
    assert analyzer._determine_alignment((256, 20, 356, 30), 612) == "center"
    
    # Test right alignment
    assert analyzer._determine_alignment((512, 20, 602, 30), 612) == "right"


def test_enhance_layout_detection():
    """Test enhancing layout detection."""
    analyzer = LayoutAnalyzer(detail_level="high")
    
    with fitz.open() as pdf_doc:
        page = pdf_doc.new_page()
        
        # Create some basic elements
        elements = [
            LayoutElement("text", (10, 10, 100, 20), "Header text"),
            LayoutElement("text", (10, 100, 100, 110), "Body text"),
            LayoutElement("text", (10, 700, 100, 710), "Footer text")
        ]
        
        # Enhance the layout detection
        enhanced_elements = analyzer._enhance_layout_detection(page, elements)
        
        # Check that elements have been enhanced
        assert len(enhanced_elements) == 3
        
        # Check that header and footer have been identified
        assert enhanced_elements[0].attributes.get("potential_role") == "header"
        assert enhanced_elements[2].attributes.get("potential_role") == "footer"


def test_create_layout_mapping():
    """Test creating a mapping between layout elements and obfuscated content."""
    # Create a simple layout map
    layout_map = {
        0: [
            LayoutElement("text", (10, 10, 100, 20), "Original header"),
            LayoutElement("text", (10, 30, 100, 40), "Original line 1"),
            LayoutElement("text", (10, 50, 100, 60), "Original line 2"),
            LayoutElement("image", (10, 70, 100, 170), None)
        ]
    }
    
    # Create obfuscated text
    obfuscated_text = "Obfuscated header\nObfuscated line 1\nObfuscated line 2"
    
    # Create the mapping
    mapping = create_layout_mapping(layout_map, obfuscated_text)
    
    # Check that we have a mapping for page 0
    assert 0 in mapping
    
    # Check that we have mappings for all elements
    assert len(mapping[0]) == 4
    
    # Check that text elements are mapped to obfuscated content
    assert mapping[0][0][1] == "Obfuscated header"
    assert mapping[0][1][1] == "Obfuscated line 1"
    assert mapping[0][2][1] == "Obfuscated line 2"
    
    # Check that non-text elements are mapped to empty strings
    assert mapping[0][3][1] == ""