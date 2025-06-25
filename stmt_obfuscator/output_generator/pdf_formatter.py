"""
PDF Formatter module for the PDF Bank Statement Obfuscator.

This module handles the formatting of PDF output files.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF

from stmt_obfuscator.config import (
    PDF_DEFAULT_FONT,
    PDF_FONT_FALLBACKS,
    PDF_FONT_SIZE,
    PDF_INCLUDE_METADATA,
    PDF_INCLUDE_TIMESTAMP,
    PDF_MARGIN,
)

logger = logging.getLogger(__name__)

# Default font fallback chain - use configuration if available
DEFAULT_FONT_FALLBACKS = PDF_FONT_FALLBACKS + [
    "Helvetica",  # Latin characters
    "Times-Roman",  # Alternative for Latin
    "Courier",  # Monospaced
    "Symbol",  # Symbol characters
    "ZapfDingbats",  # Dingbats
]
# Remove duplicates while preserving order
DEFAULT_FONT_FALLBACKS = list(dict.fromkeys(DEFAULT_FONT_FALLBACKS))

# Unicode block ranges for different scripts
UNICODE_BLOCKS = {
    "Basic Latin": (0x0000, 0x007F),
    "Latin-1 Supplement": (0x0080, 0x00FF),
    "Latin Extended-A": (0x0100, 0x017F),
    "Latin Extended-B": (0x0180, 0x024F),
    "Greek and Coptic": (0x0370, 0x03FF),
    "Cyrillic": (0x0400, 0x04FF),
    "Cyrillic Supplement": (0x0500, 0x052F),
    "General Punctuation": (0x2000, 0x206F),
    "Currency Symbols": (0x20A0, 0x20CF),
    "Letterlike Symbols": (0x2100, 0x214F),
    "Mathematical Operators": (0x2200, 0x22FF),
    "Mathematical Symbols": (0x27C0, 0x27EF),
    "Supplemental Mathematical Operators": (0x2A00, 0x2AFF),
}

# Map of Unicode blocks to appropriate fonts
BLOCK_TO_FONT_MAP = {
    "Greek and Coptic": "Symbol",
    "Mathematical Operators": "Symbol",
    "Mathematical Symbols": "Symbol",
    "Supplemental Mathematical Operators": "Symbol",
    "Currency Symbols": "Symbol",
    "Letterlike Symbols": "Symbol",
    "General Punctuation": "Symbol",
}


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
        font_fallbacks: Optional[List[str]] = None,
    ):
        """
        Initialize the PDF formatter.

        Args:
            font: The font to use for the PDF
            font_size: The font size to use for the PDF
            margin: The margin to use for the PDF (in points)
            include_timestamp: Whether to include a timestamp in the PDF
            include_metadata: Whether to include metadata in the PDF
            font_fallbacks: List of fallback fonts to use for characters not supported
                by the primary font
        """
        self.font = font
        self.font_size = font_size
        self.margin = margin
        self.include_timestamp = include_timestamp
        self.include_metadata = include_metadata
        self.font_fallbacks = font_fallbacks or DEFAULT_FONT_FALLBACKS

        # Ensure the primary font is not duplicated in fallbacks
        if self.font in self.font_fallbacks:
            self.font_fallbacks.remove(self.font)

        # Create a font cache to avoid repeated lookups
        self.font_cache = {}

        logger.info(
            f"Initialized PDFFormatter with font fallbacks: {self.font_fallbacks}"
        )

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

            # Insert the text with font fallback support
            self.insert_text_with_fallback(
                page,
                (x, y),
                header_text,
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
                # Calculate word width with font fallback consideration
                word_width, _ = self.get_text_width_with_fallback(word, self.font_size)

                # Handle special case: very long words (longer than available width)
                if word_width > available_width:
                    # If we have content in the current line, add it first
                    if current_line:
                        lines.append(" ".join(current_line))
                        current_line = []
                        current_width = 0

                    # Split the long word
                    remaining_word = word
                    while remaining_word:
                        word_width, _ = self.get_text_width_with_fallback(
                            remaining_word, self.font_size
                        )
                        if word_width <= available_width:
                            break
                        # Find the maximum characters that can fit
                        for i in range(len(remaining_word), 0, -1):
                            segment = remaining_word[:i]
                            segment_width, _ = self.get_text_width_with_fallback(
                                segment, self.font_size
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
                        current_width, _ = self.get_text_width_with_fallback(
                            remaining_word, self.font_size
                        )
                else:
                    # Check if adding this word would exceed the available width
                    space_width, _ = self.get_text_width_with_fallback(
                        " ", self.font_size
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

                # Insert the line with font fallback support
                self.insert_text_with_fallback(
                    page,
                    (start_x, y),
                    line,
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
                text_width, _ = self.get_text_width_with_fallback(
                    footer_text, self.font_size - 2
                )
                x = page.rect.width - self.margin - text_width
                y = page.rect.height - self.margin

                # Insert the text with font fallback support
                self.insert_text_with_fallback(
                    page,
                    (x, y),
                    footer_text,
                    fontsize=self.font_size - 2,
                    color=(0, 0, 0),
                )

        except Exception as e:
            logger.error(f"Error adding footer to PDF: {e}")

    def get_text_width_with_fallback(
        self, text: str, fontsize: int
    ) -> Tuple[float, str]:
        """
        Calculate the width of text considering font fallbacks.

        Args:
            text: The text to measure
            fontsize: The font size to use

        Returns:
            Tuple of (text_width, font_used)
        """
        if not text:
            return 0.0, self.font

        # Try to get from cache first
        cache_key = f"{text}:{fontsize}"
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # First try with the primary font
        try:
            width = fitz.get_text_length(text, fontname=self.font, fontsize=fontsize)
            self.font_cache[cache_key] = (width, self.font)
            return width, self.font
        except Exception as e:
            logger.debug(f"Primary font failed for text '{text}': {e}")

        # If that fails, try to determine which characters need fallbacks
        best_font = self.font
        best_width = 0.0

        # Try each fallback font
        for fallback_font in self.font_fallbacks:
            try:
                width = fitz.get_text_length(
                    text, fontname=fallback_font, fontsize=fontsize
                )
                # If we got a valid width, use this font
                if width > 0:
                    best_font = fallback_font
                    best_width = width
                    break
            except Exception as e:
                logger.debug(
                    f"Fallback font {fallback_font} failed for text '{text}': {e}"
                )
                continue

        # Cache the result
        self.font_cache[cache_key] = (best_width, best_font)
        return best_width, best_font

    def get_font_for_character(self, char: str) -> str:
        """
        Determine the appropriate font for a character.

        Args:
            char: The character to check

        Returns:
            The font name to use for this character
        """
        if not char:
            return self.font

        # Get the Unicode code point
        code_point = ord(char[0])

        # Check which Unicode block this character belongs to
        for block_name, (start, end) in UNICODE_BLOCKS.items():
            if start <= code_point <= end:
                # Use the block-to-font mapping if available
                if block_name in BLOCK_TO_FONT_MAP:
                    return BLOCK_TO_FONT_MAP[block_name]

                # Special case for mathematical symbols not in our mapping
                if (
                    0x2100 <= code_point <= 0x2BFF
                ):  # Range covering most mathematical symbols
                    return "Symbol"

                # Special case for Greek letters
                if 0x0370 <= code_point <= 0x03FF:  # Greek and Coptic
                    return "Symbol"

                # Special case for Cyrillic
                if block_name.startswith("Cyrillic"):
                    # Try to find a font that supports Cyrillic
                    for font in self.font_fallbacks:
                        if font in [
                            "Times-Roman",
                            "Helvetica",
                        ]:  # These might support some Cyrillic
                            return font
                    return self.font

        # Default to the primary font
        return self.font

    def insert_text_with_fallback(
        self,
        page: fitz.Page,
        pos: Tuple[float, float],
        text: str,
        fontsize: int,
        color: Tuple[float, float, float] = (0, 0, 0),
    ) -> None:
        """
        Insert text with font fallback support.

        This method breaks down the text and uses appropriate fonts for different
        character ranges to ensure all characters are displayed correctly.

        Args:
            page: The PDF page to write to
            pos: The (x, y) position to insert the text
            text: The text to insert
            fontsize: The font size to use
            color: The RGB color tuple to use
        """
        if not text:
            return

        # For simple cases, try using the primary font first
        try:
            page.insert_text(
                pos,
                text,
                fontname=self.font,
                fontsize=fontsize,
                color=color,
            )
            return
        except Exception as e:
            # If there's an error, we'll need to use the fallback approach
            logger.debug(f"Primary font insertion failed, using fallbacks: {e}")

        # Split text into lines
        lines = text.split("\n")
        x, y = pos
        line_height = fontsize * 1.2

        for line_idx, line in enumerate(lines):
            if not line:
                y += line_height
                continue

            # Process the line character by character
            current_font = self.font
            current_text = ""
            current_x = x

            for char in line:
                # Check if we need to switch fonts
                char_font = self.get_font_for_character(char)

                # If the font changes, output the accumulated text and reset
                if char_font != current_font and current_text:
                    try:
                        page.insert_text(
                            (current_x, y),
                            current_text,
                            fontname=current_font,
                            fontsize=fontsize,
                            color=color,
                        )
                        # Update x position
                        current_x += fitz.get_text_length(
                            current_text, fontname=current_font, fontsize=fontsize
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to insert text with font {current_font}: {e}"
                        )

                    # Reset for the new font
                    current_text = ""
                    current_font = char_font

                # Add the character to the current text segment
                current_text += char

            # Output any remaining text
            if current_text:
                try:
                    page.insert_text(
                        (current_x, y),
                        current_text,
                        fontname=current_font,
                        fontsize=fontsize,
                        color=color,
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to insert text with font {current_font}: {e}"
                    )

                    # Last resort: try each fallback font
                    for fallback in self.font_fallbacks:
                        try:
                            page.insert_text(
                                (current_x, y),
                                current_text,
                                fontname=fallback,
                                fontsize=fontsize,
                                color=color,
                            )
                            break
                        except Exception:
                            continue

            # Move to the next line
            y += line_height
