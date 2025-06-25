#!/usr/bin/env python3
"""
PDF Bank Statement Obfuscator - Demo Script.

This script demonstrates the core functionality of the PDF Bank Statement Obfuscator
by processing a sample bank statement and showing the PII detection and obfuscation
capabilities.

Usage:
    python examples/demo_script.py [--sample-path PATH] [--output-path PATH]

Options:
    --sample-path PATH    Path to a sample PDF bank statement
                          (default: uses built-in sample)
    --output-path PATH    Path to save the obfuscated output
                          (default: ./obfuscated_statement.pdf)
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Now import project modules after path is set
from stmt_obfuscator.obfuscation.obfuscator import Obfuscator  # noqa: E402
from stmt_obfuscator.pdf_parser.parser import PDFParser  # noqa: E402
from stmt_obfuscator.pii_detection.detector import PIIDetector  # noqa: E402
from tests.test_utils.data_generator import (  # noqa: E402
    generate_synthetic_bank_statement,
)


def setup_logging():
    """Configure logging for the demo script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


def create_sample_statement(output_path):
    """Create a sample bank statement for demonstration."""
    logger.info("Generating synthetic bank statement...")

    # Generate synthetic data
    statement_text, ground_truth = generate_synthetic_bank_statement(
        num_transactions=20, complexity="medium"
    )

    # Save the text to a file
    with open(output_path, "w") as f:
        f.write(statement_text)

    # Save the ground truth to a JSON file
    with open(output_path.with_suffix(".json"), "w") as f:
        json.dump(ground_truth, f, indent=2)

    logger.info(f"Sample statement saved to {output_path}")
    logger.info(f"Ground truth saved to {output_path.with_suffix('.json')}")

    return output_path, ground_truth


def process_statement(input_path, output_path):
    """Process a bank statement and obfuscate PII."""
    logger.info(f"Processing statement: {input_path}")

    # Initialize components
    parser = PDFParser()
    detector = PIIDetector()
    obfuscator = Obfuscator()

    # Step 1: Parse the document
    logger.info("Step 1: Parsing document...")
    if input_path.suffix.lower() == ".pdf":
        parser.load_pdf(str(input_path))
        parser.extract_text()
        document = parser.get_text_for_pii_detection()
    else:
        # For text files (in demo mode)
        with open(input_path, "r") as f:
            text = f.read()
        document = {"full_text": text}

    logger.info(
        f"Document parsed successfully ({len(document['full_text'])} characters)"
    )

    # Step 2: Detect PII
    logger.info("Step 2: Detecting PII entities...")
    pii_result = detector.detect_pii(document["full_text"])

    # Display detected entities
    logger.info(f"Detected {len(pii_result['entities'])} PII entities:")
    for i, entity in enumerate(pii_result["entities"]):
        confidence = entity.get("confidence", 1.0)
        confidence_indicator = (
            "✓" if confidence >= 0.9 else "?" if confidence >= 0.7 else "✗"
        )
        logger.info(
            f"  {i+1}. [{confidence_indicator}] {entity['type']}: "
            f"{entity['text']} (confidence: {confidence:.2f})"
        )

    # Step 3: Obfuscate document
    logger.info("Step 3: Obfuscating document...")
    obfuscated = obfuscator.obfuscate_document(document, pii_result["entities"])

    # Save output
    with open(output_path, "w") as f:
        f.write(obfuscated.get("full_text", ""))

    logger.info(f"Obfuscated document saved to {output_path}")

    return pii_result, obfuscated


def compare_results(original_text, obfuscated_text, pii_entities):
    """Compare original and obfuscated text to verify PII removal."""
    logger.info("\nVerification Results:")

    # Check if PII entities are still present in obfuscated text
    all_removed = True
    for entity in pii_entities:
        entity_text = entity.get("text", "")
        if entity_text in obfuscated_text:
            logger.warning(
                f"❌ PII entity still present: {entity['type']} - {entity_text}"
            )
            all_removed = False
        else:
            logger.info(
                f"✅ PII entity successfully obfuscated: "
                f"{entity['type']} - {entity_text}"
            )

    if all_removed:
        logger.info("✅ All PII entities successfully obfuscated!")
    else:
        logger.warning(
            "⚠️ Some PII entities may still be present in the obfuscated document."
        )

    # Calculate obfuscation percentage
    original_length = len(original_text)
    obfuscated_length = len(obfuscated_text)

    logger.info(f"\nOriginal document length: {original_length} characters")
    logger.info(f"Obfuscated document length: {obfuscated_length} characters")

    # Print a sample of the obfuscated text
    logger.info("\nSample of obfuscated text:")
    sample_length = min(500, len(obfuscated_text))
    logger.info(f"{obfuscated_text[:sample_length]}...")


def main():
    """Run the demo script."""
    parser = argparse.ArgumentParser(description="PDF Bank Statement Obfuscator Demo")
    parser.add_argument("--sample-path", help="Path to a sample bank statement")
    parser.add_argument(
        "--output-path",
        default="./obfuscated_statement.txt",
        help="Path to save the obfuscated output",
    )

    args = parser.parse_args()

    # Create or use sample statement
    if args.sample_path:
        input_path = Path(args.sample_path)
        if not input_path.exists():
            logger.error(f"Sample file not found: {input_path}")
            return 1
    else:
        # Create a sample statement
        sample_path = Path("./sample_statement.txt")
        input_path, ground_truth = create_sample_statement(sample_path)

    output_path = Path(args.output_path)

    # Process the statement
    pii_result, obfuscated = process_statement(input_path, output_path)

    # Compare results
    with open(input_path, "r") as f:
        original_text = f.read()

    with open(output_path, "r") as f:
        obfuscated_text = f.read()

    compare_results(original_text, obfuscated_text, pii_result["entities"])

    logger.info("\nDemo completed successfully!")
    return 0


if __name__ == "__main__":
    logger = setup_logging()
    logger.info("PDF Bank Statement Obfuscator Demo")
    logger.info("=" * 50)
    sys.exit(main())
