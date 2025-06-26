#!/usr/bin/env python3
"""
Example script demonstrating the layout preservation functionality.

This script shows how to use the layout preservation feature to maintain
the original document's layout when generating obfuscated PDFs.
"""

import argparse
import logging
import sys
from pathlib import Path

from stmt_obfuscator.pdf_parser.parser import PDFParser
from stmt_obfuscator.pii_detection.detector import PIIDetector
from stmt_obfuscator.obfuscation.obfuscator import Obfuscator
from stmt_obfuscator.output_generator.generator import OutputGenerator


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate layout preservation in PDF obfuscation"
    )
    parser.add_argument(
        "input_pdf", type=str, help="Path to the input PDF file"
    )
    parser.add_argument(
        "output_pdf", type=str, help="Path to save the obfuscated PDF file"
    )
    parser.add_argument(
        "--no-layout-preservation", action="store_true",
        help="Disable layout preservation (for comparison)"
    )
    parser.add_argument(
        "--detail-level", type=str, choices=["low", "medium", "high"],
        default="medium", help="Level of detail for layout analysis"
    )
    return parser.parse_args()


def main():
    """Run the layout preservation example."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse arguments
    args = parse_arguments()
    
    # Validate input file
    input_path = Path(args.input_pdf)
    if not input_path.exists() or input_path.suffix.lower() != ".pdf":
        logger.error(f"Input file does not exist or is not a PDF: {input_path}")
        return 1
    
    # Create output path
    output_path = Path(args.output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Processing PDF: {input_path}")
    logger.info(f"Layout preservation: {'disabled' if args.no_layout_preservation else 'enabled'}")
    
    try:
        # Initialize components
        parser = PDFParser()
        detector = PIIDetector()
        obfuscator = Obfuscator()
        output_generator = OutputGenerator(
            pdf_preserve_layout=not args.no_layout_preservation
        )
        
        # Load and parse the PDF
        logger.info("Loading and parsing PDF...")
        if not parser.load_pdf(str(input_path)):
            logger.error("Failed to load PDF file")
            return 1
        
        parser.extract_text()
        document = parser.get_text_for_pii_detection()
        
        # Add the source file path for layout preservation
        document["source_file"] = str(input_path)
        
        # Detect PII entities
        logger.info("Detecting PII entities...")
        pii_entities = detector.detect_pii(document["full_text"])
        
        # Obfuscate the document
        logger.info("Obfuscating document...")
        obfuscated_document = obfuscator.obfuscate_document(
            document, pii_entities.get("entities", [])
        )
        
        # Generate the obfuscated PDF
        logger.info("Generating obfuscated PDF...")
        success = output_generator.generate_output(
            obfuscated_document, output_path, format="pdf"
        )
        
        if success:
            logger.info(f"Successfully generated obfuscated PDF: {output_path}")
            return 0
        else:
            logger.error("Failed to generate obfuscated PDF")
            return 1
    
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())