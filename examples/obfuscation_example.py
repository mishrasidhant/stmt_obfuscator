"""
Example script demonstrating how to use the obfuscation module.

This script shows how to:
1. Load a document
2. Detect PII entities
3. Obfuscate the document
4. Save the obfuscated document
"""

import json
import logging
from pathlib import Path

from stmt_obfuscator.pdf_parser import PDFParser
from stmt_obfuscator.pii_detection import PIIDetector
from stmt_obfuscator.obfuscation import Obfuscator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run the obfuscation example."""
    # Get the input PDF path
    input_pdf = input("Enter the path to the PDF file: ")
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize components
    parser = PDFParser()
    detector = PIIDetector()
    obfuscator = Obfuscator()
    
    try:
        # Step 1: Parse the PDF
        logger.info(f"Parsing PDF: {input_pdf}")
        parser.load_pdf(input_pdf)
        parser.extract_text()
        document = parser.get_text_for_pii_detection()
        
        # Step 2: Detect PII entities
        logger.info("Detecting PII entities")
        pii_result = detector.detect_pii(document["full_text"])
        pii_entities = pii_result["entities"]
        logger.info(f"Detected {len(pii_entities)} PII entities")
        
        # Step 3: Obfuscate the document
        logger.info("Obfuscating document")
        obfuscated_document = obfuscator.obfuscate_document(document, pii_entities)
        
        # Step 4: Save the results
        output_path = output_dir / f"{Path(input_pdf).stem}_obfuscated.json"
        with open(output_path, "w") as f:
            json.dump(obfuscated_document, f, indent=2)
        
        logger.info(f"Obfuscated document saved to: {output_path}")
        
        # Display summary
        print("\nObfuscation Summary:")
        print(f"  - Input PDF: {input_pdf}")
        print(f"  - PII Entities Detected: {len(pii_entities)}")
        print(f"  - PII Entities Obfuscated: {obfuscated_document['metadata']['entities_obfuscated']}")
        print(f"  - Output File: {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())