"""
PDF Formatter module for the PDF Bank Statement Obfuscator.

This module handles the formatting of PDF output files.
"""

import logging
from datetime import datetime
from typing import Any, Dict

import fitz  # PyMuPDF

from stmt_obfuscator.config import (
    PDF_DEFAULT_FONT,
    PDF_FONT_SIZE,
    PDF_INCLUDE_METADATA,
    PDF_INCLUDE_TIMESTAMP,
    PDF_MARGIN,
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
        include_metadata: bool = PDF_INCLUDE_METADATA,
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

    def format_document(
        self, document: Dict[str, Any], pdf_doc: fitz.Document
    ) -> fitz.Document:
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
            pdf_doc.new_page()

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
                    "obfuscation_timestamp", datetime.now().isoformat()
                )
                header_text += f"\nGenerated: {timestamp}"

            # Calculate position (centered at top of page)
            text_width = fitz.get_text_length(
                header_text, fontname=self.font, fontsize=self.font_size + 2
            )
            x = (page.rect.width - text_width) / 2
            y = self.margin / 2

            # Insert the text
            page.insert_text(
                (x, y),
                header_text,
                fontname=self.font,
                fontsize=self.font_size + 2,
                color=(0, 0, 0),
            )

            # Add a separator line
            page.draw_line(
                (self.margin, self.margin),
                (page.rect.width - self.margin, self.margin),
                color=(0, 0, 0),
                width=0.5,
            )

        except Exception as e:
            logger.error(f"Error adding header to PDF: {e}")

    def wrap_text(self, text: str, page_width: float, start_x: float) -> list:
        """
        Wrap text to fit within page margins.

        Args:
            text: The text to wrap
            page_width: The width of the page
            start_x: The starting x position (left margin)

        Returns:
            A list of wrapped lines
        """
        available_width = page_width - start_x - self.margin
        lines = []

        # Split text into paragraphs
        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            if not paragraph:  # Handle empty lines
                lines.append("")
                continue

            # Initialize variables for line building
            current_line = []
            current_width = 0

            # Split paragraph into words
            words = paragraph.split()

            for word in words:
                # Calculate word width
                word_width = fitz.get_text_length(
                    word, fontname=self.font, fontsize=self.font_size
                )

                # Handle special case: very long words (longer than available width)
                if word_width > available_width:
                    # If we have content in the current line, add it first
                    if current_line:
                        lines.append(" ".join(current_line))
                        current_line = []
                        current_width = 0

                    # Split the long word
                    remaining_word = word
                    while (
                        remaining_word
                        and fitz.get_text_length(
                            remaining_word, fontname=self.font, fontsize=self.font_size
                        )
                        > available_width
                    ):
                        # Find the maximum characters that can fit
                        for i in range(len(remaining_word), 0, -1):
                            segment = remaining_word[:i]
                            segment_width = fitz.get_text_length(
                                segment, fontname=self.font, fontsize=self.font_size
                            )
                            if segment_width <= available_width:
                                lines.append(segment)
                                remaining_word = remaining_word[i:]
                                break
                        # Safeguard against infinite loops
                        if i == 1:
                            lines.append(remaining_word[0])
                            remaining_word = remaining_word[1:]

                    # Add any remaining part of the word
                    if remaining_word:
                        current_line = [remaining_word]
                        current_width = fitz.get_text_length(
                            remaining_word, fontname=self.font, fontsize=self.font_size
                        )
                else:
                    # Check if adding this word would exceed the available width
                    space_width = fitz.get_text_length(
                        " ", fontname=self.font, fontsize=self.font_size
                    )
                    if (
                        current_line
                        and current_width + space_width + word_width > available_width
                    ):
                        # Line would be too long, start a new line
                        lines.append(" ".join(current_line))
                        current_line = [word]
                        current_width = word_width
                    else:
                        # Add word to current line
                        current_line.append(word)
                        # Add space width if not the first word
                        if len(current_line) > 1:
                            current_width += space_width
                        current_width += word_width

            # Add the last line of the paragraph
            if current_line:
                lines.append(" ".join(current_line))

        return lines

    def add_content(self, pdf_doc: fitz.Document, document: Dict[str, Any]) -> None:
        """
        Add content to the PDF document.

        Args:
            pdf_doc: The PDF document to write to
            document: The document containing the data
        """
        try:
            # Get the document text
            text = document.get("full_text", "")

            # Start with the first page
            page_num = 0
            page = pdf_doc[page_num]

            # Calculate the starting position
            start_x = self.margin
            y = self.margin * 1.5  # Start below the header
            line_height = self.font_size * 1.2  # Add some spacing between lines

            # Wrap text to fit within margins
            wrapped_lines = self.wrap_text(text, page.rect.width, start_x)

            # Insert the wrapped text
            for line in wrapped_lines:
                # Check if we need to add a new page
                if y + line_height > page.rect.height - self.margin * 2:
                    # Create a new page
                    page = pdf_doc.new_page()
                    page_num += 1
                    y = self.margin * 1.5  # Reset y position

                # Skip empty lines (just advance y position)
                if not line:
                    y += line_height
                    continue

                # Insert the line
                page.insert_text(
                    (start_x, y),
                    line,
                    fontname=self.font,
                    fontsize=self.font_size,
                    color=(0, 0, 0),
                )

                # Move to the next line
                y += line_height

        except Exception as e:
            logger.error(f"Error adding content to PDF: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")

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
                    (
                        page.rect.width - self.margin,
                        page.rect.height - self.margin * 1.5,
                    ),
                    color=(0, 0, 0),
                    width=0.5,
                )

                # Add page number
                footer_text = f"Page {page_num + 1} of {len(pdf_doc)}"

                # Add metadata if enabled
                if (
                    self.include_metadata and page_num == len(pdf_doc) - 1
                ):  # Only on last page
                    metadata = document.get("metadata", {})
                    if metadata:
                        footer_text += "\n\nMetadata:"
                        for key, value in metadata.items():
                            if (
                                key != "obfuscation_timestamp"
                            ):  # Already shown in header
                                footer_text += f"\n{key}: {value}"

                # Calculate position (right-aligned at bottom of page)
                text_width = fitz.get_text_length(
                    footer_text, fontname=self.font, fontsize=self.font_size - 2
                )
                x = page.rect.width - self.margin - text_width
                y = page.rect.height - self.margin

                # Insert the text
                page.insert_text(
                    (x, y),
                    footer_text,
                    fontname=self.font,
                    fontsize=self.font_size - 2,
                    color=(0, 0, 0),
                )

        except Exception as e:
            logger.error(f"Error adding footer to PDF: {e}")
