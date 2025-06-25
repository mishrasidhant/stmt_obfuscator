#!/usr/bin/env python3
"""
Quick test script for PII detection using Ollama.

This script demonstrates how to use the PII detector with a sample bank statement.
It generates a sample, runs detection, and shows the results.
"""

import json
import os
import sys

# Add the scripts directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pii_detector import OllamaPIIDetector
from generate_samples import BankStatementGenerator


def main():
    """
    Run a quick test of the PII detector.
    """
    print("PII Detection Quick Test")
    print("=======================\n")
    
    # Check if Ollama is running
    print("Checking Ollama connection...")
    try:
        detector = OllamaPIIDetector()
        print("✅ Connected to Ollama\n")
    except ConnectionError as e:
        print(f"❌ Error connecting to Ollama: {e}")
        print("\nMake sure Ollama is running. You can start it with:")
        print("  ollama serve")
        return
    
    # Generate a sample bank statement
    print("Generating a sample bank statement...")
    generator = BankStatementGenerator(seed=42)  # Use a fixed seed for reproducibility
    statement_text, ground_truth = generator.generate_statement()
    
    # Save the sample
    os.makedirs("../data", exist_ok=True)
    sample_path = "../data/quick_test_sample.txt"
    with open(sample_path, "w") as f:
        f.write(statement_text)
    
    ground_truth_path = "../data/quick_test_sample_ground_truth.json"
    with open(ground_truth_path, "w") as f:
        json.dump(ground_truth, f, indent=2)
    
    print(f"✅ Sample saved to {sample_path}\n")
    
    # Display some of the statement
    print("Sample bank statement (excerpt):")
    print("--------------------------------")
    lines = statement_text.split("\n")
    for i, line in enumerate(lines):
        if i > 5 and i < 15:  # Show a small excerpt
            print(line)
    print("...\n")
    
    # Detect PII
    print("Detecting PII (this may take a moment)...")
    detected = detector.detect_pii(statement_text)
    
    # Save the results
    results_path = "../data/quick_test_results.json"
    with open(results_path, "w") as f:
        json.dump(detected, f, indent=2)
    
    print(f"✅ Detection results saved to {results_path}\n")
    
    # Display the results
    print("Detection Results:")
    print("-----------------")
    if not detected["entities"]:
        print("No PII entities detected.")
    else:
        for entity in detected["entities"]:
            entity_text = entity.get("text", "")
            entity_type = entity.get("type", "UNKNOWN")
            print(f"- {entity_type}: {entity_text}")
    
    print("\nGround Truth:")
    print("-------------")
    for entity in ground_truth["entities"][:10]:  # Show first 10 for brevity
        entity_text = entity.get("text", "")
        entity_type = entity.get("type", "UNKNOWN")
        print(f"- {entity_type}: {entity_text}")
    
    if len(ground_truth["entities"]) > 10:
        print(f"... and {len(ground_truth['entities']) - 10} more entities")
    
    print("\nNext Steps:")
    print("-----------")
    print("1. Run the full evaluation:")
    print("   python evaluate.py")
    print("2. Generate more samples:")
    print("   python generate_samples.py --num-samples 10")
    print("3. Try a different model:")
    print("   python pii_detector.py --model llama3:8b --input ../data/quick_test_sample.txt")


if __name__ == "__main__":
    main()