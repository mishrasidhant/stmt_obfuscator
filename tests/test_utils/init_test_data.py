#!/usr/bin/env python3
"""
Initialize test data for the PDF Bank Statement Obfuscator.

This script generates synthetic bank statement samples for testing.
"""

import os
import argparse
import json
from pathlib import Path

from tests.test_utils.data_generator import EnhancedBankStatementGenerator


def init_test_data(output_dir: str, num_samples: int = 5, include_pdfs: bool = False, seed: int = 42) -> None:
    """
    Initialize test data for the PDF Bank Statement Obfuscator.
    
    Args:
        output_dir: Directory to save the test data
        num_samples: Number of samples to generate
        include_pdfs: Whether to generate PDF versions of the statements
        seed: Random seed for reproducibility
    """
    print(f"Initializing test data in {output_dir}")
    print(f"Generating {num_samples} samples (include_pdfs={include_pdfs})")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a generator
    generator = EnhancedBankStatementGenerator(seed=seed)
    
    # Generate samples with different formats and distributions
    formats = ["standard", "minimal", "modern", "detailed"]
    distributions = ["standard", "minimal", "heavy"]
    
    samples = []
    
    # Generate one sample for each format and distribution combination
    for i, format_name in enumerate(formats):
        for j, distribution_name in enumerate(distributions):
            sample_idx = i * len(distributions) + j
            if sample_idx >= num_samples:
                break
                
            print(f"Generating sample {sample_idx + 1}/{num_samples}: format={format_name}, distribution={distribution_name}")
            
            # Generate the sample
            statement_text, ground_truth, pdf_path = generator.generate_statement(
                format_name=format_name,
                pii_distribution_name=distribution_name,
                num_transactions=15,
                include_pdf=include_pdfs,
                output_dir=output_dir
            )
            
            # Save the statement text
            text_path = os.path.join(output_dir, f"statement_{sample_idx + 1}.txt")
            with open(text_path, 'w') as f:
                f.write(statement_text)
            
            # Save the ground truth
            ground_truth_path = os.path.join(output_dir, f"statement_{sample_idx + 1}_ground_truth.json")
            with open(ground_truth_path, 'w') as f:
                json.dump(ground_truth, f, indent=2)
            
            # Add to samples
            samples.append({
                "id": sample_idx + 1,
                "format": format_name,
                "pii_distribution": distribution_name,
                "text_path": text_path,
                "ground_truth_path": ground_truth_path,
                "pdf_path": pdf_path,
                "entity_count": len(ground_truth["entities"]),
                "entity_types": list({entity["type"] for entity in ground_truth["entities"]})
            })
        
        if sample_idx >= num_samples:
            break
    
    # Generate any remaining samples with random formats and distributions
    for i in range(len(samples), num_samples):
        print(f"Generating sample {i + 1}/{num_samples}: random format and distribution")
        
        # Generate the sample
        statement_text, ground_truth, pdf_path = generator.generate_statement(
            include_pdf=include_pdfs,
            output_dir=output_dir
        )
        
        # Save the statement text
        text_path = os.path.join(output_dir, f"statement_{i + 1}.txt")
        with open(text_path, 'w') as f:
            f.write(statement_text)
        
        # Save the ground truth
        ground_truth_path = os.path.join(output_dir, f"statement_{i + 1}_ground_truth.json")
        with open(ground_truth_path, 'w') as f:
            json.dump(ground_truth, f, indent=2)
        
        # Add to samples
        samples.append({
            "id": i + 1,
            "format": "random",
            "pii_distribution": "random",
            "text_path": text_path,
            "ground_truth_path": ground_truth_path,
            "pdf_path": pdf_path,
            "entity_count": len(ground_truth["entities"]),
            "entity_types": list({entity["type"] for entity in ground_truth["entities"]})
        })
    
    # Save dataset metadata
    metadata_path = os.path.join(output_dir, "dataset_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump({
            "num_samples": num_samples,
            "samples": samples,
            "include_pdfs": include_pdfs,
            "seed": seed
        }, f, indent=2)
    
    print(f"Generated {len(samples)} samples")
    print(f"Dataset metadata saved to {metadata_path}")


def main():
    """Main function to initialize test data."""
    parser = argparse.ArgumentParser(description="Initialize test data for PDF Bank Statement Obfuscator")
    parser.add_argument("--output-dir", default="tests/data/samples",
                        help="Directory to save the test data")
    parser.add_argument("--num-samples", type=int, default=5,
                        help="Number of samples to generate")
    parser.add_argument("--include-pdfs", action="store_true",
                        help="Generate PDF versions of the statements")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    init_test_data(args.output_dir, args.num_samples, args.include_pdfs, args.seed)


if __name__ == "__main__":
    main()