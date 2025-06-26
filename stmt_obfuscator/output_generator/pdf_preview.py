"""
PDF Preview module for the PDF Bank Statement Obfuscator.

This module handles the generation of PDF previews for the UI.
"""

import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import fitz  # PyMuPDF
from PyQt6.QtGui import QImage, QPixmap

from stmt_obfuscator.output_generator.pdf_formatter import PDFFormatter

logger = logging.getLogger(__name__)


class PDFPreviewGenerator:
    """
    Generator for PDF previews.
    
    This class handles the generation of PDF previews for display in the UI,
    ensuring that what users see in the preview matches the final PDF output.
    """
    
    def __init__(self, pdf_formatter: Optional[PDFFormatter] = None):
        """
        Initialize the PDF preview generator.
        
        Args:
            pdf_formatter: The PDF formatter to use for generating PDFs.
                If None, a new formatter will be created with default settings.
        """
        self.pdf_formatter = pdf_formatter or PDFFormatter()
        logger.info("Initialized PDFPreviewGenerator")
    
    def generate_preview(self, document: Dict[str, Any], dpi: int = 150) -> List[QPixmap]:
        """
        Generate preview images of PDF pages.
        
        Args:
            document: The document to generate a preview for
            dpi: The resolution of the preview images in dots per inch
            
        Returns:
            A list of QPixmap objects, one for each page of the PDF
        """
        try:
            # Create a temporary PDF document
            pdf_doc = fitz.open()
            
            # Format the document using the same formatter that would be used for export
            pdf_doc = self.pdf_formatter.format_document(document, pdf_doc)
            
            # Convert each page to an image
            pixmaps = []
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                
                # Render the page to a pixmap
                # Use a higher zoom factor for better quality
                zoom_factor = dpi / 72  # 72 DPI is the default PDF resolution
                matrix = fitz.Matrix(zoom_factor, zoom_factor)
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                
                # Convert the pixmap to a QPixmap
                img = QImage(
                    pixmap.samples,
                    pixmap.width,
                    pixmap.height,
                    pixmap.stride,
                    QImage.Format.Format_RGB888
                )
                qpixmap = QPixmap.fromImage(img)
                pixmaps.append(qpixmap)
            
            # Close the PDF document
            pdf_doc.close()
            
            return pixmaps
        
        except Exception as e:
            logger.error(f"Error generating PDF preview: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def generate_preview_file(self, document: Dict[str, Any]) -> Optional[Path]:
        """
        Generate a temporary PDF file for preview purposes.
        
        Args:
            document: The document to generate a preview for
            
        Returns:
            The path to the temporary PDF file, or None if generation failed
        """
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            # Create a new PDF document
            pdf_doc = fitz.open()
            
            # Format the document
            pdf_doc = self.pdf_formatter.format_document(document, pdf_doc)
            
            # Save the PDF to the temporary file
            pdf_doc.save(temp_path)
            pdf_doc.close()
            
            return temp_path
        
        except Exception as e:
            logger.error(f"Error generating PDF preview file: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None