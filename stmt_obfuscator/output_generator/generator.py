"""
Output Generator module for the PDF Bank Statement Obfuscator.

This module handles the generation of output files in various formats.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union

import fitz  # PyMuPDF

from stmt_obfuscator.output_generator.pdf_formatter import PDFFormatter
from stmt_obfuscator.config import (
    PDF_EXPORT_ENABLED,
    PDF_DEFAULT_FONT,
    PDF_FONT_SIZE,
    PDF_MARGIN,
    PDF_INCLUDE_TIMESTAMP,
    PDF_INCLUDE_METADATA
)

logger = logging.getLogger(__name__)


class OutputGenerator:
    """
    Generator for output files.
    
    This class handles the generation of output files in various formats,
    including text and PDF.
    """
    
    def __init__(
        self,
        pdf_export_enabled: bool = PDF_EXPORT_ENABLED,
        pdf_font: str = PDF_DEFAULT_FONT,
        pdf_font_size: int = PDF_FONT_SIZE,
        pdf_margin: int = PDF_MARGIN,
        pdf_include_timestamp: bool = PDF_INCLUDE_TIMESTAMP,
        pdf_include_metadata: bool = PDF_INCLUDE_METADATA
    ):
        """
        Initialize the output generator.
        
        Args:
            pdf_export_enabled: Whether PDF export is enabled
            pdf_font: The font to use for PDF output
            pdf_font_size: The font size to use for PDF output
            pdf_margin: The margin to use for PDF output (in points)
            pdf_include_timestamp: Whether to include a timestamp in PDF output
            pdf_include_metadata: Whether to include metadata in PDF output
        """
        self.pdf_export_enabled = pdf_export_enabled
        self.pdf_formatter = PDFFormatter(
            font=pdf_font,
            font_size=pdf_font_size,
            margin=pdf_margin,
            include_timestamp=pdf_include_timestamp,
            include_metadata=pdf_include_metadata
        )
        
        logger.info("Initialized OutputGenerator")
    
    def generate_output(
        self,
        document: Dict[str, Any],
        output_path: Union[str, Path],
        format: str = "text"
    ) -> bool:
        """
        Generate output in the specified format.
        
        Args:
            document: The document to output
            output_path: The path to write the output to
            format: The format to output (text or pdf)
            
        Returns:
            True if the output was generated successfully, False otherwise
        """
        try:
            # Convert output_path to Path object if it's a string
            if isinstance(output_path, str):
                output_path = Path(output_path)
            
            # Create parent directories if they don't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate output based on format
            if format.lower() == "pdf":
                if not self.pdf_export_enabled:
                    logger.warning("PDF export is disabled")
                    return False
                
                return self.generate_pdf(document, output_path)
            else:
                # Default to text format
                return self.generate_text(document, output_path)
        
        except Exception as e:
            logger.error(f"Error generating output: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def generate_text(self, document: Dict[str, Any], output_path: Path) -> bool:
        """
        Generate text output.
        
        Args:
            document: The document to output
            output_path: The path to write the output to
            
        Returns:
            True if the output was generated successfully, False otherwise
        """
        try:
            # Get the document text
            text = document.get("full_text", "")
            
            # Write the text to the output file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            logger.info(f"Generated text output at {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error generating text output: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def generate_pdf(self, document: Dict[str, Any], output_path: Path) -> bool:
        """
        Generate PDF output.
        
        Args:
            document: The document to output
            output_path: The path to write the output to
            
        Returns:
            True if the output was generated successfully, False otherwise
        """
        try:
            # Ensure the output path has a .pdf extension
            if output_path.suffix.lower() != ".pdf":
                output_path = output_path.with_suffix(".pdf")
            
            # Create a new PDF document
            pdf_doc = fitz.open()
            
            # Format the document
            pdf_doc = self.pdf_formatter.format_document(document, pdf_doc)
            
            # Save the PDF
            pdf_doc.save(output_path)
            pdf_doc.close()
            
            logger.info(f"Generated PDF output at {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error generating PDF output: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False