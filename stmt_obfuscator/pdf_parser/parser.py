"""
PDF Parser module for the PDF Bank Statement Obfuscator.

This module handles PDF parsing and text extraction with positional metadata.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import fitz  # PyMuPDF

from stmt_obfuscator.config import MAX_PAGE_SIZE, MAX_DOCUMENT_SIZE


logger = logging.getLogger(__name__)


class PDFParser:
    """PDF Parser for extracting text and structure from bank statements."""

    def __init__(self):
        """Initialize the PDF parser."""
        self.document = None
        self.page_count = 0
        self.text_blocks = []
        self.tables = []
        self.metadata = {}

    def load_pdf(self, pdf_path: str) -> bool:
        """
        Load a PDF file for processing.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            True if the PDF was loaded successfully, False otherwise
        """
        path = Path(pdf_path)
        
        if not path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        
        if path.stat().st_size > MAX_DOCUMENT_SIZE:
            logger.error(f"PDF file too large: {path.stat().st_size} bytes")
            return False
        
        try:
            self.document = fitz.open(pdf_path)
            self.page_count = len(self.document)
            self.metadata = self._extract_metadata()
            logger.info(f"Loaded PDF with {self.page_count} pages: {pdf_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load PDF: {e}")
            return False

    def extract_text(self) -> List[Dict[str, Any]]:
        """
        Extract text blocks with positional metadata from the PDF.

        Returns:
            A list of text blocks with positional metadata
        """
        if not self.document:
            logger.error("No PDF document loaded")
            return []
        
        self.text_blocks = []
        
        for page_num, page in enumerate(self.document):
            # Extract text blocks
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            self.text_blocks.append({
                                "page": page_num + 1,
                                "text": span["text"],
                                "bbox": span["bbox"],  # (x0, y0, x1, y1)
                                "font": span["font"],
                                "size": span["size"],
                                "color": span["color"],
                            })
        
        logger.info(f"Extracted {len(self.text_blocks)} text blocks")
        return self.text_blocks

    def detect_tables(self) -> List[Dict[str, Any]]:
        """
        Detect tables in the PDF document.

        Returns:
            A list of detected tables with positional metadata
        """
        if not self.document:
            logger.error("No PDF document loaded")
            return []
        
        self.tables = []
        
        # Simple table detection based on text alignment
        # This is a placeholder for more sophisticated table detection
        
        logger.info(f"Detected {len(self.tables)} tables")
        return self.tables

    def get_document_structure(self) -> Dict[str, Any]:
        """
        Get the document structure with text blocks and tables.

        Returns:
            A dictionary containing the document structure
        """
        return {
            "metadata": self.metadata,
            "page_count": self.page_count,
            "text_blocks": self.text_blocks,
            "tables": self.tables,
        }

    def _extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the PDF document.

        Returns:
            A dictionary containing the PDF metadata
        """
        if not self.document:
            return {}
        
        metadata = self.document.metadata
        
        # Clean up metadata
        cleaned_metadata = {}
        for key, value in metadata.items():
            if value and isinstance(value, str):
                cleaned_metadata[key] = value
        
        return cleaned_metadata

    def close(self):
        """Close the PDF document and release resources."""
        if self.document:
            self.document.close()
            self.document = None
            logger.info("Closed PDF document")