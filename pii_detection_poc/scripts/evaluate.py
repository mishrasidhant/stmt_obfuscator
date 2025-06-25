#!/usr/bin/env python3
"""
Evaluate PII detection performance against ground truth.

This script evaluates the performance of the PII detection by comparing
the detected entities with ground truth annotations and calculating
precision, recall, and F1-score metrics.
"""

import argparse
import json
import os
from typing import Dict, List, Tuple

import sys
import os

# Add the scripts directory to the path to import pii_detector
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pii_detector import OllamaPIIDetector


def calculate_metrics(detected_entities: List[Dict], ground_truth_entities: List[Dict]) -> Dict:
    """
    Calculate precision, recall, and F1-score for PII detection.

    Args:
        detected_entities: List of detected PII entities
        ground_truth_entities: List of ground truth PII entities

    Returns:
        A dictionary containing precision, recall, and F1-score metrics
    """
    # Count true positives, false positives, and false negatives
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    
    # Create a copy of ground truth entities to mark matches
    remaining_ground_truth = ground_truth_entities.copy()
    
    # Check each detected entity against ground truth
    for detected in detected_entities:
        # Try to find a matching entity in ground truth
        match_found = False
        
        for i, ground_truth in enumerate(remaining_ground_truth):
            # Check if the entity types match
            if detected["type"] == ground_truth["type"]:
                # Check if the text overlaps
                detected_start = detected.get("start", 0)
                detected_end = detected.get("end", len(detected["text"]))
                ground_truth_start = ground_truth.get("start", 0)
                ground_truth_end = ground_truth.get("end", len(ground_truth["text"]))
                
                # Check for overlap
                if (detected_start <= ground_truth_end and 
                    detected_end >= ground_truth_start):
                    # Consider it a match
                    true_positives += 1
                    match_found = True
                    # Remove the matched ground truth entity
                    remaining_ground_truth.pop(i)
                    break
        
        if not match_found:
            false_positives += 1
    
    # Any remaining ground truth entities are false negatives
    false_negatives = len(remaining_ground_truth)
    
    # Calculate metrics
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "total_detected": len(detected_entities),
        "total_ground_truth": len(ground_truth_entities)
    }


def evaluate_sample(detector: OllamaPIIDetector, statement_path: str, ground_truth_path: str) -> Dict:
    """
    Evaluate PII detection on a single sample.

    Args:
        detector: The OllamaPIIDetector instance
        statement_path: Path to the statement text file
        ground_truth_path: Path to the ground truth JSON file

    Returns:
        A dictionary containing evaluation metrics
    """
    # Load the statement text
    with open(statement_path, 'r') as f:
        statement_text = f.read()
    
    # Load the ground truth
    with open(ground_truth_path, 'r') as f:
        ground_truth = json.load(f)
    
    # Detect PII in the statement
    detected = detector.detect_pii(statement_text)
    
    # Calculate metrics
    metrics = calculate_metrics(detected["entities"], ground_truth["entities"])
    
    # Add sample information
    metrics["sample"] = os.path.basename(statement_path)
    
    return metrics


def evaluate_all_samples(detector: OllamaPIIDetector, data_dir: str) -> Dict:
    """
    Evaluate PII detection on all samples in the data directory.

    Args:
        detector: The OllamaPIIDetector instance
        data_dir: Path to the directory containing samples

    Returns:
        A dictionary containing overall evaluation metrics
    """
    # Find all statement files
    statement_files = [f for f in os.listdir(data_dir) if f.startswith("statement_") and f.endswith(".txt")]
    
    # Evaluate each sample
    sample_metrics = []
    
    for statement_file in statement_files:
        statement_path = os.path.join(data_dir, statement_file)
        ground_truth_path = os.path.join(data_dir, statement_file.replace(".txt", "_ground_truth.json"))
        
        if os.path.exists(ground_truth_path):
            metrics = evaluate_sample(detector, statement_path, ground_truth_path)
            sample_metrics.append(metrics)
            print(f"Evaluated {statement_file}: Precision={metrics['precision']:.2f}, Recall={metrics['recall']:.2f}, F1={metrics['f1_score']:.2f}")
    
    # Calculate overall metrics
    overall_metrics = {
        "precision": sum(m["precision"] for m in sample_metrics) / len(sample_metrics) if sample_metrics else 0,
        "recall": sum(m["recall"] for m in sample_metrics) / len(sample_metrics) if sample_metrics else 0,
        "f1_score": sum(m["f1_score"] for m in sample_metrics) / len(sample_metrics) if sample_metrics else 0,
        "samples": len(sample_metrics),
        "sample_metrics": sample_metrics
    }
    
    return overall_metrics


def main():
    """
    Main function to evaluate PII detection performance.
    """
    parser = argparse.ArgumentParser(description="Evaluate PII detection performance")
    parser.add_argument("--model", default="mistral:latest", help="Ollama model to use")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama API host URL")
    parser.add_argument("--data-dir", default="../data", help="Directory containing samples")
    parser.add_argument("--output", default="../data/evaluation_results.json", help="Output file for evaluation results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the detector
        detector = OllamaPIIDetector(model=args.model, host=args.host)
        
        # Evaluate all samples
        results = evaluate_all_samples(detector, args.data_dir)
        
        # Print overall results
        print("\nOverall Results:")
        print(f"Precision: {results['precision']:.4f}")
        print(f"Recall: {results['recall']:.4f}")
        print(f"F1-Score: {results['f1_score']:.4f}")
        print(f"Number of Samples: {results['samples']}")
        
        # Save results to file
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {args.output}")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()