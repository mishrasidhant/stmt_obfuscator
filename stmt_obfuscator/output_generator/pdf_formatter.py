"""
PDF Formatter module for the PDF Bank Statement Obfuscator.

This module handles the formatting of PDF output files.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

import fitz  # PyMuPDF

from stmt_obfuscator.config import (
    PDF_DEFAULT_FONT,
    PDF_FONT_SIZE,
    PDF_MARGIN,
    PDF_INCLUDE_TIMESTAMP,
    PDF_INCLUDE_METADATA
)

logger = logging.getLogger(__name__)


class PDFFormatter:
    """
    Formatter for PDF output.
    
    This class handles the formatting of obfuscated bank statements into PDF format.
    """
    
    def __init__(
        self,
        font: str = PDF_DEFAULT_FONT,
        font_size: int = PDF_FONT_SIZE,
        margin: int = PDF_MARGIN,
        include_timestamp: bool = PDF_INCLUDE_TIMESTAMP,
        include_metadata: bool = PDF_INCLUDE_METADATA
    ):
        """
        Initialize the PDF formatter.
        
        Args:
            font: The font to use for the PDF
            font_size: The font size to use for the PDF
            margin: The margin to use for the PDF (in points)
            include_timestamp: Whether to include a timestamp in the PDF
            include_metadata: Whether to include metadata in the PDF
        """
        self.font = font
        self.font_size = font_size
        self.margin = margin
        self.include_timestamp = include_timestamp
        self.include_metadata = include_metadata
        
        logger.info("Initialized PDFFormatter")
    
    def format_document(self, document: Dict[str, Any], pdf_doc: fitz.Document) -> fitz.Document:
        """
        Format a document as a PDF.
        
        Args:
            document: The document to format
            pdf_doc: The PDF document to write to
            
        Returns:
            The formatted PDF document
        """
        try:
            # Add a new page
            page = pdf_doc.new_page()
            
            # Add header
            self.add_header(pdf_doc, document)
            
            # Add content
            self.add_content(pdf_doc, document)
            
            # Add footer
            self.add_footer(pdf_doc, document)
            
            return pdf_doc
        
        except Exception as e:
            logger.error(f"Error formatting PDF document: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return the PDF document even if there was an error
            return pdf_doc
    
    def add_header(self, pdf_doc: fitz.Document, document: Dict[str, Any]) -> None:
        """
        Add a header to the PDF document.
        
        Args:
            pdf_doc: The PDF document to write to
            document: The document containing the data
        """
        try:
            page = pdf_doc[0]  # Get the first page
            
            # Set up the header text
            header_text = "Obfuscated Bank Statement"
            
            # Add timestamp if enabled
            if self.include_timestamp:
                timestamp = document.get("metadata", {}).get(
                    "obfuscation_timestamp",
                    datetime.now().isoformat()
                )
                header_text += f"\nGenerated: {timestamp}"
            
            # Calculate position (centered at top of page)
            text_width = fitz.get_text_length(header_text, fontname=self.font, fontsize=self.font_size + 2)
            x = (page.rect.width - text_width) / 2
            y = self.margin / 2
            
            # Insert the text
            page.insert_text(
                (x, y),
                header_text,
                fontname=self.font,
                fontsize=self.font_size + 2,
                color=(0, 0, 0)
            )
            
            # Add a separator line
            page.draw_line(
                (self.margin, self.margin),
                (page.rect.width - self.margin, self.margin),
                color=(0, 0, 0),
                width=0.5
            )
            
        except Exception as e:
            logger.error(f"Error adding header to PDF: {e}")
    
    def add_content(self, pdf_doc: fitz.Document, document: Dict[str, Any]) -> None:
        """
        Add content to the PDF document.
        
        Args:
            pdf_doc: The PDF document to write to
            document: The document containing the data
        """
        try:
            page = pdf_doc[0]  # Get the first page
            
            # Get the document text
            text = document.get("full_text", "")
            
            # Calculate the starting position
            x = self.margin
            y = self.margin * 1.5  # Start below the header
            
            # Insert the text with proper wrapping
            page.insert_text(
                (x, y),
                text,
                fontname=self.font,
                fontsize=self.font_size,
                color=(0, 0, 0)
            )
            
            # If the text is too long, it will be automatically wrapped to new pages
            
        except Exception as e:
            logger.error(f"Error adding content to PDF: {e}")
    
    def add_footer(self, pdf_doc: fitz.Document, document: Dict[str, Any]) -> None:
        """
        Add a footer to the PDF document.
        
        Args:
            pdf_doc: The PDF document to write to
            document: The document containing the data
        """
        try:
            # Add footer to each page
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                
                # Add a separator line
                page.draw_line(
                    (self.margin, page.rect.height - self.margin * 1.5),
                    (page.rect.width - self.margin, page.rect.height - self.margin * 1.5),
                    color=(0, 0, 0),
                    width=0.5
                )
                
                # Add page number
                footer_text = f"Page {page_num + 1} of {len(pdf_doc)}"
                
                # Add metadata if enabled
                if self.include_metadata and page_num == len(pdf_doc) - 1:  # Only on last page
                    metadata = document.get("metadata", {})
                    if metadata:
                        footer_text += "\n\nMetadata:"
                        for key, value in metadata.items():
                            if key != "obfuscation_timestamp":  # Already shown in header
                                footer_text += f"\n{key}: {value}"
                
                # Calculate position (right-aligned at bottom of page)
                text_width = fitz.get_text_length(footer_text, fontname=self.font, fontsize=self.font_size - 2)
                x = page.rect.width - self.margin - text_width
                y = page.rect.height - self.margin
                
                # Insert the text
                page.insert_text(
                    (x, y),
                    footer_text,
                    fontname=self.font,
                    fontsize=self.font_size - 2,
                    color=(0, 0, 0)
                )
                
        except Exception as e:
            logger.error(f"Error adding footer to PDF: {e}")