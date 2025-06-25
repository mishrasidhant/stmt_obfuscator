#!/usr/bin/env python3
"""
Comprehensive Demonstration of the PDF Bank Statement Obfuscator

This script demonstrates the complete workflow of the PDF Bank Statement Obfuscator:
1. Setting up the environment
2. Generating a synthetic bank statement
3. Detecting PII entities with and without RAG enhancement
4. Obfuscating the detected PII
5. Displaying the results

Usage:
    python demo_bank_statement_obfuscator_fixed.py [--use-existing-sample]

Options:
    --use-existing-sample    Use an existing sample instead of generating a new one
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import project modules
from stmt_obfuscator.pdf_parser.parser import PDFParser
from stmt_obfuscator.pii_detection.detector import PIIDetector
from stmt_obfuscator.rag.context_enhancer import RAGContextEnhancer
from stmt_obfuscator.obfuscation.obfuscator import Obfuscator
from pii_detection_poc.scripts.generate_samples import BankStatementGenerator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def setup_environment() -> bool:
    """
    Set up the necessary environment for the demonstration.
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    print_section_header("ENVIRONMENT SETUP")
    
    # Create necessary directories
    demo_dir = Path("demo_output")
    demo_dir.mkdir(exist_ok=True)
    
    # Check if Ollama is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                logger.info(f"Ollama is available with models: {', '.join([m['name'] for m in models])}")
            else:
                logger.warning("Ollama is available but no models are installed")
                logger.warning("You may need to run: ollama pull mistral:latest")
        else:
            logger.warning("Ollama is not responding correctly")
            logger.warning("Please ensure Ollama is running with: ollama serve")
    except Exception as e:
        logger.warning(f"Could not connect to Ollama: {e}")
        logger.warning("Please ensure Ollama is installed and running")
        logger.warning("Installation instructions: https://ollama.com/download")
        logger.warning("After installation, run: ollama serve")
        logger.warning("Then pull the required model: ollama pull mistral:latest")
        
    logger.info("Environment setup completed")
    return True


def generate_sample_statement() -> Tuple[str, Dict[str, Any], Path]:
    """
    Generate a synthetic bank statement for demonstration.
    
    Returns:
        Tuple containing:
            - The statement text
            - The ground truth annotations
            - The path to the saved statement file
    """
    print_section_header("GENERATING SYNTHETIC BANK STATEMENT")
    
    # Create a generator with a fixed seed for reproducibility
    generator = BankStatementGenerator(seed=42)
    
    # Generate a synthetic bank statement
    logger.info("Generating synthetic bank statement...")
    statement_text, ground_truth = generator.generate_statement()
    
    # Save the statement to a file
    output_path = Path("demo_output/sample_statement.txt")
    with open(output_path, "w") as f:
        f.write(statement_text)
    
    # Save the ground truth to a file
    with open(output_path.with_suffix(".json"), "w") as f:
        json.dump(ground_truth, f, indent=2)
    
    logger.info(f"Sample statement saved to {output_path}")
    logger.info(f"Ground truth saved to {output_path.with_suffix('.json')}")
    
    # Print a preview of the statement
    print("\nPreview of the generated bank statement:")
    print("-" * 80)
    print("\n".join(statement_text.split("\n")[:20]) + "\n...")
    print("-" * 80)
    
    return statement_text, ground_truth, output_path


def detect_pii_without_rag(statement_text: str) -> Dict[str, Any]:
    """
    Detect PII entities in the statement without RAG enhancement.
    
    Args:
        statement_text: The bank statement text
        
    Returns:
        Dictionary containing detected PII entities
    """
    print_section_header("PII DETECTION WITHOUT RAG")
    
    # Initialize the PII detector with mistral:latest model
    detector = PIIDetector(model="mistral:latest")
    
    # Detect PII entities
    logger.info("Detecting PII entities without RAG enhancement...")
    pii_result = detector.detect_pii(statement_text)
    
    # Display detected entities
    logger.info(f"Detected {len(pii_result['entities'])} PII entities:")
    for i, entity in enumerate(pii_result["entities"]):
        confidence = entity.get("confidence", 1.0)
        confidence_indicator = "✓" if confidence >= 0.9 else "?" if confidence >= 0.7 else "✗"
        logger.info(
            f"  {i+1}. [{confidence_indicator}] {entity['type']}: "
            f"{entity['text']} (confidence: {confidence:.2f})"
        )
    
    # Save the results
    output_path = Path("demo_output/pii_detection_without_rag.json")
    with open(output_path, "w") as f:
        json.dump(pii_result, f, indent=2)
    
    logger.info(f"PII detection results saved to {output_path}")
    
    return pii_result


def detect_pii_with_rag(statement_text: str) -> Dict[str, Any]:
    """
    Detect PII entities in the statement with RAG enhancement.
    
    Args:
        statement_text: The bank statement text
        
    Returns:
        Dictionary containing detected PII entities
    """
    print_section_header("PII DETECTION WITH RAG ENHANCEMENT")
    
    # Initialize the PII detector and RAG context enhancer
    detector = PIIDetector(model="mistral:latest")
    rag_enhancer = RAGContextEnhancer()
    
    # Initialize the knowledge base with common PII patterns
    logger.info("Initializing RAG knowledge base...")
    rag_enhancer.initialize_knowledge_base()
    
    # Get RAG context for the statement
    logger.info("Retrieving RAG context for the statement...")
    rag_context = rag_enhancer.get_context(statement_text)
    
    if rag_context:
        logger.info(f"Retrieved {len(rag_context['patterns'])} relevant patterns for context enhancement")
        
        # Display some of the patterns
        print("\nSample of retrieved patterns:")
        for i, pattern in enumerate(rag_context["patterns"][:3]):
            print(f"  Pattern {i+1}: {pattern['type']} - {pattern['pattern']}")
        
        if rag_context["examples"]:
            print("\nSample of retrieved examples:")
            for i, example in enumerate(rag_context["examples"][:3]):
                print(f"  Example {i+1}: {example['type']} - {example['text']}")
    else:
        logger.warning("No RAG context was retrieved")
    
    # Detect PII entities with RAG enhancement
    logger.info("Detecting PII entities with RAG enhancement...")
    pii_result = detector.detect_pii(statement_text, rag_context)
    
    # Display detected entities
    logger.info(f"Detected {len(pii_result['entities'])} PII entities:")
    for i, entity in enumerate(pii_result["entities"]):
        confidence = entity.get("confidence", 1.0)
        confidence_indicator = "✓" if confidence >= 0.9 else "?" if confidence >= 0.7 else "✗"
        logger.info(
            f"  {i+1}. [{confidence_indicator}] {entity['type']}: "
            f"{entity['text']} (confidence: {confidence:.2f})"
        )
    
    # Save the results
    output_path = Path("demo_output/pii_detection_with_rag.json")
    with open(output_path, "w") as f:
        json.dump(pii_result, f, indent=2)
    
    logger.info(f"PII detection results saved to {output_path}")
    
    return pii_result


def obfuscate_document(statement_text: str, pii_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Obfuscate the detected PII entities in the document.
    
    Args:
        statement_text: The bank statement text
        pii_entities: List of detected PII entities
        
    Returns:
        Dictionary containing the obfuscated document
    """
    print_section_header("PII OBFUSCATION")
    
    # Initialize the obfuscator
    obfuscator = Obfuscator()
    
    # Create a document structure for obfuscation
    document = {
        "full_text": statement_text,
        "metadata": {"source": "demo"},
        "text_blocks": [{"text": statement_text}]
    }
    
    # Obfuscate the document
    logger.info("Obfuscating document...")
    obfuscated_document = obfuscator.obfuscate_document(document, pii_entities)
    
    # Save the obfuscated document
    output_path = Path("demo_output/obfuscated_statement.txt")
    with open(output_path, "w") as f:
        f.write(obfuscated_document["full_text"])
    
    # Save the full obfuscated document structure
    with open(output_path.with_suffix(".json"), "w") as f:
        json.dump(obfuscated_document, f, indent=2)
    
    logger.info(f"Obfuscated statement saved to {output_path}")
    logger.info(f"Obfuscated document structure saved to {output_path.with_suffix('.json')}")
    
    return obfuscated_document


def compare_results(original_text: str, obfuscated_text: str, pii_entities: List[Dict[str, Any]]):
    """
    Compare the original and obfuscated text to verify PII removal.
    
    Args:
        original_text: The original bank statement text
        obfuscated_text: The obfuscated bank statement text
        pii_entities: List of detected PII entities
    """
    print_section_header("VERIFICATION OF PII REMOVAL")
    
    # Check if PII entities are still present in obfuscated text
    all_removed = True
    for entity in pii_entities:
        entity_text = entity.get("text", "")
        if entity_text in obfuscated_text:
            logger.warning(f"❌ PII entity still present: {entity['type']} - {entity_text}")
            all_removed = False
        else:
            logger.info(f"✅ PII entity successfully obfuscated: {entity['type']} - {entity_text}")
    
    if all_removed:
        logger.info("✅ All PII entities successfully obfuscated!")
    else:
        logger.warning("⚠️ Some PII entities may still be present in the obfuscated document.")
    
    # Display a side-by-side comparison of a section
    print("\nSide-by-side comparison (CUSTOMER INFORMATION section):")
    print("-" * 80)
    
    # Extract the customer information section
    original_lines = original_text.split("\n")
    obfuscated_lines = obfuscated_text.split("\n")
    
    customer_info_start = None
    customer_info_end = None
    
    for i, line in enumerate(original_lines):
        if "CUSTOMER INFORMATION:" in line:
            customer_info_start = i
        elif customer_info_start and line.strip() == "" and i > customer_info_start + 1:
            customer_info_end = i
            break
    
    if customer_info_start and customer_info_end:
        print("Original                          | Obfuscated")
        print("-" * 30 + "+" + "-" * 49)
        
        for i in range(customer_info_start, customer_info_end):
            if i < len(original_lines) and i < len(obfuscated_lines):
                print(f"{original_lines[i]:<30} | {obfuscated_lines[i]}")
    
    print("-" * 80)


def main():
    """Run the comprehensive demonstration."""
    parser = argparse.ArgumentParser(description="Demonstrate the PDF Bank Statement Obfuscator")
    parser.add_argument("--use-existing-sample", action="store_true", 
                        help="Use an existing sample instead of generating a new one")
    
    args = parser.parse_args()
    
    print_section_header("PDF BANK STATEMENT OBFUSCATOR DEMONSTRATION")
    logger.info("Starting comprehensive demonstration of the PDF Bank Statement Obfuscator")
    
    # Step 1: Set up the environment
    setup_environment()
    
    # Step 2: Generate or use a sample bank statement
    if args.use_existing_sample:
        logger.info("Using existing sample statement")
        sample_path = Path("tests/data/samples/sample_statement.txt")
        
        if not sample_path.exists():
            logger.error(f"Sample file not found: {sample_path}")
            return 1
        
        with open(sample_path, "r") as f:
            statement_text = f.read()
        
        ground_truth_path = sample_path.with_suffix(".json")
        if ground_truth_path.exists():
            with open(ground_truth_path, "r") as f:
                ground_truth = json.load(f)
        else:
            ground_truth = {"entities": []}
    else:
        statement_text, ground_truth, _ = generate_sample_statement()
    
    # Step 3: Detect PII without RAG
    pii_result_without_rag = detect_pii_without_rag(statement_text)
    
    # Step 4: Detect PII with RAG enhancement
    pii_result_with_rag = detect_pii_with_rag(statement_text)
    
    # Step 5: Compare PII detection results
    print_section_header("COMPARISON OF PII DETECTION METHODS")
    
    entities_without_rag = len(pii_result_without_rag["entities"])
    entities_with_rag = len(pii_result_with_rag["entities"])
    
    print(f"PII entities detected without RAG: {entities_without_rag}")
    print(f"PII entities detected with RAG:    {entities_with_rag}")
    
    # Find entities that were only detected with RAG
    entities_only_with_rag = []
    for entity_with_rag in pii_result_with_rag["entities"]:
        found = False
        for entity_without_rag in pii_result_without_rag["entities"]:
            if (entity_with_rag["text"] == entity_without_rag["text"] and 
                entity_with_rag["type"] == entity_without_rag["type"]):
                found = True
                break
        
        if not found:
            entities_only_with_rag.append(entity_with_rag)
    
    if entities_only_with_rag:
        print(f"\nEntities detected only with RAG enhancement ({len(entities_only_with_rag)}):")
        for entity in entities_only_with_rag:
            print(f"  - {entity['type']}: {entity['text']} (confidence: {entity.get('confidence', 1.0):.2f})")
    else:
        print("\nNo additional entities were detected with RAG enhancement in this sample.")
    
    # Step 6: Obfuscate the document using the RAG-enhanced detection
    obfuscated_document = obfuscate_document(statement_text, pii_result_with_rag["entities"])
    
    # Step 7: Compare original and obfuscated text
    compare_results(statement_text, obfuscated_document["full_text"], pii_result_with_rag["entities"])
    
    # Step 8: Display summary
    print_section_header("DEMONSTRATION SUMMARY")
    
    print("The PDF Bank Statement Obfuscator demonstration has completed successfully!")
    print("\nKey results:")
    print(f"  - PII entities detected without RAG: {entities_without_rag}")
    print(f"  - PII entities detected with RAG:    {entities_with_rag}")
    print(f"  - PII entities obfuscated:           {obfuscated_document['metadata']['entities_obfuscated']}")
    
    print("\nOutput files:")
    for file in Path("demo_output").glob("*"):
        print(f"  - {file}")
    
    print("\nThank you for using the PDF Bank Statement Obfuscator!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())