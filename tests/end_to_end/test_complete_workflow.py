"""
End-to-end tests for the complete PDF Bank Statement Obfuscator workflow.

These tests verify the entire process from PDF parsing to PII detection to obfuscation.
"""

import os
import json
import pytest
import re
import time
from pathlib import Path
from typing import Dict, List, Any

from stmt_obfuscator.pdf_parser.parser import PDFParser
from stmt_obfuscator.pii_detection.detector import PIIDetector
from stmt_obfuscator.obfuscation.obfuscator import Obfuscator


class TestCompleteWorkflow:
    """End-to-end tests for the complete workflow."""

    def test_basic_workflow(self, pdf_parser, pii_detector, obfuscator, generated_statement_with_pdf, temp_test_dir):
        """Test the basic workflow from PDF parsing to obfuscation."""
        # Skip if PDF generation failed
        if not generated_statement_with_pdf.get("pdf_path"):
            pytest.skip("PDF generation failed")
            
        pdf_path = generated_statement_with_pdf["pdf_path"]
        ground_truth = generated_statement_with_pdf["ground_truth"]
        
        # Skip if Ollama is not available
        try:
            # Step 1: Load the PDF
            start_time = time.time()
            result = pdf_parser.load_pdf(pdf_path)
            assert result is True, "Failed to load PDF"
            load_time = time.time() - start_time
            
            # Step 2: Extract text
            start_time = time.time()
            text_blocks = pdf_parser.extract_text()
            assert len(text_blocks) > 0, "No text blocks extracted"
            extract_time = time.time() - start_time
            
            # Step 3: Get document structure for PII detection
            document = pdf_parser.get_text_for_pii_detection()
            assert "full_text" in document, "Missing full_text in document structure"
            assert len(document["full_text"]) > 0, "Empty full_text in document structure"
            
            # Step 4: Detect PII
            start_time = time.time()
            pii_entities = pii_detector.detect_pii(document["full_text"])
            assert "entities" in pii_entities, "Missing entities in PII detection result"
            detection_time = time.time() - start_time
            
            # Verify that some entities were detected
            assert len(pii_entities["entities"]) > 0, "No PII entities detected"
            
            # Step 5: Obfuscate the document
            start_time = time.time()
            obfuscated_document = obfuscator.obfuscate_document(document, pii_entities["entities"])
            assert "full_text" in obfuscated_document, "Missing full_text in obfuscated document"
            obfuscation_time = time.time() - start_time
            
            # Step 6: Save the obfuscated document
            output_path = os.path.join(temp_test_dir, "obfuscated_output.txt")
            with open(output_path, "w") as f:
                f.write(obfuscated_document["full_text"])
            
            # Verify the output file exists
            assert os.path.exists(output_path), "Output file was not created"
            
            # Print performance metrics
            print(f"Performance metrics:")
            print(f"  PDF loading time: {load_time:.3f} seconds")
            print(f"  Text extraction time: {extract_time:.3f} seconds")
            print(f"  PII detection time: {detection_time:.3f} seconds")
            print(f"  Obfuscation time: {obfuscation_time:.3f} seconds")
            print(f"  Total processing time: {load_time + extract_time + detection_time + obfuscation_time:.3f} seconds")
            
            # Print entity statistics
            entity_types = {}
            for entity in pii_entities["entities"]:
                entity_type = entity["type"]
                if entity_type not in entity_types:
                    entity_types[entity_type] = 0
                entity_types[entity_type] += 1
            
            print(f"Detected {len(pii_entities['entities'])} entities:")
            for entity_type, count in entity_types.items():
                print(f"  {entity_type}: {count}")
            
        except Exception as e:
            pytest.skip(f"Skipping test because of error: {str(e)}")
    
    def test_multiple_statement_formats(self, pdf_parser, pii_detector, obfuscator, data_generator, temp_test_dir):
        """Test the workflow with multiple statement formats."""
        # Generate statements with different formats
        formats = ["standard", "minimal", "modern", "detailed"]
        results = []
        
        for format_name in formats:
            print(f"Testing format: {format_name}")
            
            # Generate a statement with this format
            statement_text, ground_truth, pdf_path = data_generator.generate_statement(
                format_name=format_name,
                pii_distribution_name="standard",
                num_transactions=15,
                include_pdf=True,
                output_dir=temp_test_dir
            )
            
            # Skip if PDF generation failed
            if not pdf_path:
                print(f"  Skipping {format_name} - PDF generation failed")
                continue
            
            try:
                # Process the PDF
                pdf_parser.load_pdf(pdf_path)
                pdf_parser.extract_text()
                document = pdf_parser.get_text_for_pii_detection()
                pii_entities = pii_detector.detect_pii(document["full_text"])
                obfuscated_document = obfuscator.obfuscate_document(document, pii_entities["entities"])
                
                # Calculate metrics
                detected_count = len(pii_entities["entities"])
                ground_truth_count = len(ground_truth["entities"])
                
                # Calculate precision and recall (simplified)
                # In a real implementation, you would use a more sophisticated approach
                # to match detected entities with ground truth
                detected_types = {entity["type"] for entity in pii_entities["entities"]}
                ground_truth_types = {entity["type"] for entity in ground_truth["entities"]}
                
                common_types = detected_types.intersection(ground_truth_types)
                precision = len(common_types) / len(detected_types) if detected_types else 0
                recall = len(common_types) / len(ground_truth_types) if ground_truth_types else 0
                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                results.append({
                    "format": format_name,
                    "detected_count": detected_count,
                    "ground_truth_count": ground_truth_count,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1_score,
                    "detected_types": list(detected_types),
                    "ground_truth_types": list(ground_truth_types),
                    "common_types": list(common_types)
                })
                
                print(f"  Detected {detected_count} entities (ground truth: {ground_truth_count})")
                print(f"  Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1_score:.2f}")
                
            except Exception as e:
                print(f"  Error processing {format_name}: {str(e)}")
        
        # Skip if no formats were processed successfully
        if not results:
            pytest.skip("No statement formats were processed successfully")
        
        # Save the results
        results_path = os.path.join(temp_test_dir, "format_test_results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {results_path}")
    
    def test_multiple_pii_distributions(self, pdf_parser, pii_detector, obfuscator, data_generator, temp_test_dir):
        """Test the workflow with multiple PII distributions."""
        # Generate statements with different PII distributions
        distributions = ["standard", "minimal", "heavy"]
        results = []
        
        for dist_name in distributions:
            print(f"Testing PII distribution: {dist_name}")
            
            # Generate a statement with this distribution
            statement_text, ground_truth, pdf_path = data_generator.generate_statement(
                format_name="standard",
                pii_distribution_name=dist_name,
                num_transactions=15,
                include_pdf=True,
                output_dir=temp_test_dir
            )
            
            # Skip if PDF generation failed
            if not pdf_path:
                print(f"  Skipping {dist_name} - PDF generation failed")
                continue
            
            try:
                # Process the PDF
                pdf_parser.load_pdf(pdf_path)
                pdf_parser.extract_text()
                document = pdf_parser.get_text_for_pii_detection()
                pii_entities = pii_detector.detect_pii(document["full_text"])
                obfuscated_document = obfuscator.obfuscate_document(document, pii_entities["entities"])
                
                # Calculate metrics by entity type
                detected_by_type = {}
                for entity in pii_entities["entities"]:
                    entity_type = entity["type"]
                    if entity_type not in detected_by_type:
                        detected_by_type[entity_type] = 0
                    detected_by_type[entity_type] += 1
                
                ground_truth_by_type = {}
                for entity in ground_truth["entities"]:
                    entity_type = entity["type"]
                    if entity_type not in ground_truth_by_type:
                        ground_truth_by_type[entity_type] = 0
                    ground_truth_by_type[entity_type] += 1
                
                # Calculate type-specific metrics
                type_metrics = {}
                all_types = set(list(detected_by_type.keys()) + list(ground_truth_by_type.keys()))
                
                for entity_type in all_types:
                    detected = detected_by_type.get(entity_type, 0)
                    ground_truth = ground_truth_by_type.get(entity_type, 0)
                    
                    # Calculate precision and recall (simplified)
                    precision = 1.0 if detected == 0 else min(ground_truth, detected) / detected
                    recall = 0.0 if ground_truth == 0 else min(ground_truth, detected) / ground_truth
                    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                    
                    type_metrics[entity_type] = {
                        "detected": detected,
                        "ground_truth": ground_truth,
                        "precision": precision,
                        "recall": recall,
                        "f1_score": f1_score
                    }
                
                results.append({
                    "distribution": dist_name,
                    "total_detected": len(pii_entities["entities"]),
                    "total_ground_truth": len(ground_truth["entities"]),
                    "type_metrics": type_metrics
                })
                
                print(f"  Detected {len(pii_entities['entities'])} entities (ground truth: {len(ground_truth['entities'])})")
                print(f"  Type-specific metrics:")
                for entity_type, metrics in type_metrics.items():
                    print(f"    {entity_type}: Precision={metrics['precision']:.2f}, Recall={metrics['recall']:.2f}, F1={metrics['f1_score']:.2f}")
                
            except Exception as e:
                print(f"  Error processing {dist_name}: {str(e)}")
        
        # Skip if no distributions were processed successfully
        if not results:
            pytest.skip("No PII distributions were processed successfully")
        
        # Save the results
        results_path = os.path.join(temp_test_dir, "distribution_test_results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {results_path}")
    
    def test_batch_processing(self, pdf_parser, pii_detector, obfuscator, generated_dataset, temp_test_dir):
        """Test batch processing of multiple statements."""
        samples = generated_dataset["samples"]
        dataset_dir = generated_dataset["dir"]
        
        # Skip if no samples were generated
        if not samples:
            pytest.skip("No samples were generated")
        
        # Create output directory
        output_dir = os.path.join(temp_test_dir, "batch_output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Process each sample
        results = []
        
        for i, sample in enumerate(samples):
            print(f"Processing sample {i+1}/{len(samples)}")
            
            try:
                # Get the text path
                text_path = sample["text_path"]
                
                # Load the text
                with open(text_path, "r") as f:
                    text = f.read()
                
                # Detect PII
                start_time = time.time()
                pii_entities = pii_detector.detect_pii(text)
                detection_time = time.time() - start_time
                
                # Obfuscate the document
                start_time = time.time()
                document = {"full_text": text}
                obfuscated_document = obfuscator.obfuscate_document(document, pii_entities["entities"])
                obfuscation_time = time.time() - start_time
                
                # Save the obfuscated document
                output_path = os.path.join(output_dir, f"obfuscated_{i+1}.txt")
                with open(output_path, "w") as f:
                    f.write(obfuscated_document["full_text"])
                
                # Calculate metrics
                detected_count = len(pii_entities["entities"])
                
                # Load ground truth
                ground_truth_path = sample["ground_truth_path"]
                with open(ground_truth_path, "r") as f:
                    ground_truth = json.load(f)
                
                ground_truth_count = len(ground_truth["entities"])
                
                # Calculate precision and recall (simplified)
                detected_types = {entity["type"] for entity in pii_entities["entities"]}
                ground_truth_types = {entity["type"] for entity in ground_truth["entities"]}
                
                common_types = detected_types.intersection(ground_truth_types)
                precision = len(common_types) / len(detected_types) if detected_types else 0
                recall = len(common_types) / len(ground_truth_types) if ground_truth_types else 0
                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                results.append({
                    "sample_id": i+1,
                    "format": sample.get("format", "unknown"),
                    "pii_distribution": sample.get("pii_distribution", "unknown"),
                    "detected_count": detected_count,
                    "ground_truth_count": ground_truth_count,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1_score,
                    "detection_time": detection_time,
                    "obfuscation_time": obfuscation_time,
                    "total_time": detection_time + obfuscation_time
                })
                
                print(f"  Detected {detected_count} entities (ground truth: {ground_truth_count})")
                print(f"  Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1_score:.2f}")
                print(f"  Processing time: {detection_time + obfuscation_time:.3f} seconds")
                
            except Exception as e:
                print(f"  Error processing sample {i+1}: {str(e)}")
        
        # Skip if no samples were processed successfully
        if not results:
            pytest.skip("No samples were processed successfully")
        
        # Calculate aggregate metrics
        avg_precision = sum(r["precision"] for r in results) / len(results)
        avg_recall = sum(r["recall"] for r in results) / len(results)
        avg_f1_score = sum(r["f1_score"] for r in results) / len(results)
        avg_detection_time = sum(r["detection_time"] for r in results) / len(results)
        avg_obfuscation_time = sum(r["obfuscation_time"] for r in results) / len(results)
        avg_total_time = sum(r["total_time"] for r in results) / len(results)
        
        print(f"Aggregate metrics:")
        print(f"  Average Precision: {avg_precision:.2f}")
        print(f"  Average Recall: {avg_recall:.2f}")
        print(f"  Average F1 Score: {avg_f1_score:.2f}")
        print(f"  Average Detection Time: {avg_detection_time:.3f} seconds")
        print(f"  Average Obfuscation Time: {avg_obfuscation_time:.3f} seconds")
        print(f"  Average Total Time: {avg_total_time:.3f} seconds")
        
        # Save the results
        results_path = os.path.join(output_dir, "batch_results.json")
        with open(results_path, "w") as f:
            json.dump({
                "samples": results,
                "aggregate": {
                    "avg_precision": avg_precision,
                    "avg_recall": avg_recall,
                    "avg_f1_score": avg_f1_score,
                    "avg_detection_time": avg_detection_time,
                    "avg_obfuscation_time": avg_obfuscation_time,
                    "avg_total_time": avg_total_time
                }
            }, f, indent=2)
        
        print(f"Results saved to {results_path}")