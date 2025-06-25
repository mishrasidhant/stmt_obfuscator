"""
Performance benchmark tests for the PDF Bank Statement Obfuscator.

These tests measure the performance of the application under different conditions.
"""

import os
import json
import time
import pytest
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Optional

from stmt_obfuscator.pdf_parser.parser import PDFParser
from stmt_obfuscator.pii_detection.detector import PIIDetector
from stmt_obfuscator.obfuscation.obfuscator import Obfuscator


class TestPerformanceBenchmarks:
    """Performance benchmark tests for the application."""

    def test_pii_detection_performance(self, pii_detector, data_generator, benchmark_results_dir):
        """Benchmark PII detection performance with different text sizes."""
        # Skip if Ollama is not available
        try:
            # Test with different text sizes
            text_sizes = [1000, 5000, 10000, 20000, 50000]
            results = []
            
            for size in text_sizes:
                print(f"Testing PII detection with text size: {size} characters")
                
                # Generate a statement with approximately the desired size
                # We'll generate a larger statement and truncate it
                statement_text, _, _ = data_generator.generate_statement(
                    format_name="standard",
                    pii_distribution_name="heavy",  # Use heavy distribution for more entities
                    num_transactions=max(10, size // 200)  # Rough estimate to get desired size
                )
                
                # Truncate to the desired size
                if len(statement_text) > size:
                    statement_text = statement_text[:size]
                
                # Measure detection time
                start_time = time.time()
                pii_entities = pii_detector.detect_pii(statement_text)
                detection_time = time.time() - start_time
                
                # Record results
                results.append({
                    "text_size": size,
                    "actual_size": len(statement_text),
                    "detection_time": detection_time,
                    "entities_detected": len(pii_entities["entities"]),
                    "entities_per_second": len(pii_entities["entities"]) / detection_time if detection_time > 0 else 0,
                    "chars_per_second": len(statement_text) / detection_time if detection_time > 0 else 0
                })
                
                print(f"  Detected {len(pii_entities['entities'])} entities in {detection_time:.3f} seconds")
                print(f"  Processing speed: {len(statement_text) / detection_time:.1f} chars/sec, {len(pii_entities['entities']) / detection_time:.1f} entities/sec")
            
            # Save results
            results_path = os.path.join(benchmark_results_dir, "pii_detection_benchmark.json")
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)
            
            # Create a visualization
            self._create_performance_chart(
                results, 
                "text_size", 
                "detection_time",
                "Text Size (characters)",
                "Detection Time (seconds)",
                "PII Detection Performance",
                os.path.join(benchmark_results_dir, "pii_detection_benchmark.png")
            )
            
            print(f"Results saved to {results_path}")
            
        except Exception as e:
            pytest.skip(f"Skipping benchmark because of error: {str(e)}")
    
    def test_obfuscation_performance(self, obfuscator, data_generator, benchmark_results_dir):
        """Benchmark obfuscation performance with different numbers of entities."""
        # Test with different numbers of entities
        entity_counts = [10, 50, 100, 200, 500]
        results = []
        
        for count in entity_counts:
            print(f"Testing obfuscation with {count} entities")
            
            # Generate a statement with many entities
            statement_text, ground_truth, _ = data_generator.generate_statement(
                format_name="standard",
                pii_distribution_name="heavy",  # Use heavy distribution for more entities
                num_transactions=max(10, count // 5)  # Rough estimate to get desired entity count
            )
            
            # Create synthetic entities if we don't have enough
            entities = ground_truth["entities"]
            if len(entities) < count:
                # Duplicate existing entities with modified positions
                original_count = len(entities)
                text_length = len(statement_text)
                
                for i in range(original_count, count):
                    # Copy a random entity and modify its position
                    entity = entities[i % original_count].copy()
                    entity["start"] = (entity["start"] + i * 10) % (text_length - len(entity["text"]))
                    entity["end"] = entity["start"] + len(entity["text"])
                    entities.append(entity)
            
            # Truncate to the desired count
            entities = entities[:count]
            
            # Measure obfuscation time
            document = {"full_text": statement_text}
            start_time = time.time()
            obfuscated_document = obfuscator.obfuscate_document(document, entities)
            obfuscation_time = time.time() - start_time
            
            # Record results
            results.append({
                "entity_count": count,
                "actual_count": len(entities),
                "text_size": len(statement_text),
                "obfuscation_time": obfuscation_time,
                "entities_per_second": len(entities) / obfuscation_time if obfuscation_time > 0 else 0
            })
            
            print(f"  Obfuscated {len(entities)} entities in {obfuscation_time:.3f} seconds")
            print(f"  Processing speed: {len(entities) / obfuscation_time:.1f} entities/sec")
        
        # Save results
        results_path = os.path.join(benchmark_results_dir, "obfuscation_benchmark.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        # Create a visualization
        self._create_performance_chart(
            results, 
            "entity_count", 
            "obfuscation_time",
            "Entity Count",
            "Obfuscation Time (seconds)",
            "Obfuscation Performance",
            os.path.join(benchmark_results_dir, "obfuscation_benchmark.png")
        )
        
        print(f"Results saved to {results_path}")
    
    def test_pdf_parsing_performance(self, pdf_parser, data_generator, benchmark_results_dir):
        """Benchmark PDF parsing performance with different PDF sizes."""
        # Generate PDFs of different sizes
        pdf_sizes = [1, 5, 10, 20, 50]  # Number of pages (approximate)
        results = []
        
        for size in pdf_sizes:
            print(f"Testing PDF parsing with approximately {size} pages")
            
            # Generate a statement with the desired size
            # For this test, we'll use the number of transactions to control the size
            statement_text, _, pdf_path = data_generator.generate_statement(
                format_name="standard",
                pii_distribution_name="standard",
                num_transactions=size * 10,  # Rough estimate to get desired page count
                include_pdf=True,
                output_dir=benchmark_results_dir
            )
            
            # Skip if PDF generation failed
            if not pdf_path:
                print(f"  Skipping {size} pages - PDF generation failed")
                continue
            
            try:
                # Measure loading time
                start_time = time.time()
                pdf_parser.load_pdf(pdf_path)
                load_time = time.time() - start_time
                
                # Measure extraction time
                start_time = time.time()
                text_blocks = pdf_parser.extract_text()
                extraction_time = time.time() - start_time
                
                # Record results
                results.append({
                    "target_pages": size,
                    "actual_pages": pdf_parser.page_count,
                    "load_time": load_time,
                    "extraction_time": extraction_time,
                    "total_time": load_time + extraction_time,
                    "text_blocks": len(text_blocks),
                    "pages_per_second": pdf_parser.page_count / (load_time + extraction_time) if (load_time + extraction_time) > 0 else 0
                })
                
                print(f"  Parsed {pdf_parser.page_count} pages in {load_time + extraction_time:.3f} seconds")
                print(f"  Processing speed: {pdf_parser.page_count / (load_time + extraction_time):.1f} pages/sec")
                
            except Exception as e:
                print(f"  Error processing {size} pages: {str(e)}")
        
        # Skip if no PDFs were processed successfully
        if not results:
            pytest.skip("No PDFs were processed successfully")
        
        # Save results
        results_path = os.path.join(benchmark_results_dir, "pdf_parsing_benchmark.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        # Create a visualization
        self._create_performance_chart(
            results, 
            "actual_pages", 
            "total_time",
            "Page Count",
            "Parsing Time (seconds)",
            "PDF Parsing Performance",
            os.path.join(benchmark_results_dir, "pdf_parsing_benchmark.png")
        )
        
        print(f"Results saved to {results_path}")
    
    def test_end_to_end_performance(self, pdf_parser, pii_detector, obfuscator, data_generator, benchmark_results_dir):
        """Benchmark end-to-end performance with different statement complexities."""
        # Test with different statement complexities
        complexities = [
            {"format": "minimal", "distribution": "minimal", "transactions": 5},
            {"format": "standard", "distribution": "standard", "transactions": 15},
            {"format": "detailed", "distribution": "heavy", "transactions": 30},
            {"format": "modern", "distribution": "heavy", "transactions": 50}
        ]
        
        results = []
        
        for complexity in complexities:
            format_name = complexity["format"]
            distribution = complexity["distribution"]
            transactions = complexity["transactions"]
            
            print(f"Testing end-to-end performance with complexity: {format_name}, {distribution}, {transactions} transactions")
            
            # Generate a statement with this complexity
            statement_text, ground_truth, pdf_path = data_generator.generate_statement(
                format_name=format_name,
                pii_distribution_name=distribution,
                num_transactions=transactions,
                include_pdf=True,
                output_dir=benchmark_results_dir
            )
            
            # Skip if PDF generation failed
            if not pdf_path:
                print(f"  Skipping complexity {format_name} - PDF generation failed")
                continue
            
            try:
                # Measure PDF parsing time
                start_time = time.time()
                pdf_parser.load_pdf(pdf_path)
                pdf_parser.extract_text()
                document = pdf_parser.get_text_for_pii_detection()
                parsing_time = time.time() - start_time
                
                # Measure PII detection time
                start_time = time.time()
                pii_entities = pii_detector.detect_pii(document["full_text"])
                detection_time = time.time() - start_time
                
                # Measure obfuscation time
                start_time = time.time()
                obfuscated_document = obfuscator.obfuscate_document(document, pii_entities["entities"])
                obfuscation_time = time.time() - start_time
                
                # Calculate total time
                total_time = parsing_time + detection_time + obfuscation_time
                
                # Record results
                results.append({
                    "format": format_name,
                    "distribution": distribution,
                    "transactions": transactions,
                    "text_size": len(document["full_text"]),
                    "entity_count": len(pii_entities["entities"]),
                    "ground_truth_count": len(ground_truth["entities"]),
                    "parsing_time": parsing_time,
                    "detection_time": detection_time,
                    "obfuscation_time": obfuscation_time,
                    "total_time": total_time,
                    "entities_per_second": len(pii_entities["entities"]) / total_time if total_time > 0 else 0
                })
                
                print(f"  Processed in {total_time:.3f} seconds:")
                print(f"    Parsing: {parsing_time:.3f}s, Detection: {detection_time:.3f}s, Obfuscation: {obfuscation_time:.3f}s")
                print(f"    Detected {len(pii_entities['entities'])} entities (ground truth: {len(ground_truth['entities'])})")
                
            except Exception as e:
                print(f"  Error processing complexity {format_name}: {str(e)}")
        
        # Skip if no complexities were processed successfully
        if not results:
            pytest.skip("No complexities were processed successfully")
        
        # Save results
        results_path = os.path.join(benchmark_results_dir, "end_to_end_benchmark.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        # Create a stacked bar chart for time breakdown
        self._create_stacked_time_chart(
            results,
            ["parsing_time", "detection_time", "obfuscation_time"],
            ["PDF Parsing", "PII Detection", "Obfuscation"],
            "End-to-End Performance Breakdown",
            os.path.join(benchmark_results_dir, "end_to_end_benchmark.png")
        )
        
        print(f"Results saved to {results_path}")
    
    def test_model_comparison(self, data_generator, benchmark_results_dir):
        """Benchmark different Ollama models for PII detection."""
        # Skip if Ollama is not available
        try:
            # Test with different models
            models = ["mistral:latest", "llama2:latest", "orca-mini:latest"]
            
            # Generate a test statement
            statement_text, ground_truth, _ = data_generator.generate_statement(
                format_name="standard",
                pii_distribution_name="standard",
                num_transactions=15
            )
            
            results = []
            
            for model_name in models:
                print(f"Testing model: {model_name}")
                
                try:
                    # Initialize detector with this model
                    detector = PIIDetector(model=model_name)
                    
                    # Measure detection time
                    start_time = time.time()
                    pii_entities = detector.detect_pii(statement_text)
                    detection_time = time.time() - start_time
                    
                    # Calculate metrics
                    detected_count = len(pii_entities["entities"])
                    ground_truth_count = len(ground_truth["entities"])
                    
                    # Calculate precision and recall (simplified)
                    detected_types = {entity["type"] for entity in pii_entities["entities"]}
                    ground_truth_types = {entity["type"] for entity in ground_truth["entities"]}
                    
                    common_types = detected_types.intersection(ground_truth_types)
                    precision = len(common_types) / len(detected_types) if detected_types else 0
                    recall = len(common_types) / len(ground_truth_types) if ground_truth_types else 0
                    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                    
                    # Record results
                    results.append({
                        "model": model_name,
                        "detection_time": detection_time,
                        "detected_count": detected_count,
                        "ground_truth_count": ground_truth_count,
                        "precision": precision,
                        "recall": recall,
                        "f1_score": f1_score,
                        "entities_per_second": detected_count / detection_time if detection_time > 0 else 0
                    })
                    
                    print(f"  Detected {detected_count} entities in {detection_time:.3f} seconds")
                    print(f"  Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1_score:.2f}")
                    print(f"  Processing speed: {detected_count / detection_time:.1f} entities/sec")
                    
                except Exception as e:
                    print(f"  Error testing model {model_name}: {str(e)}")
            
            # Skip if no models were tested successfully
            if not results:
                pytest.skip("No models were tested successfully")
            
            # Save results
            results_path = os.path.join(benchmark_results_dir, "model_comparison_benchmark.json")
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)
            
            # Create visualizations
            self._create_model_comparison_chart(
                results,
                benchmark_results_dir
            )
            
            print(f"Results saved to {results_path}")
            
        except Exception as e:
            pytest.skip(f"Skipping benchmark because of error: {str(e)}")
    
    def _create_performance_chart(self, results, x_key, y_key, x_label, y_label, title, output_path):
        """Create a performance chart from benchmark results."""
        try:
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            plt.plot(df[x_key], df[y_key], 'o-', linewidth=2, markersize=8)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(title)
            plt.grid(True)
            
            # Add data labels
            for i, row in df.iterrows():
                plt.annotate(
                    f"{row[y_key]:.2f}s",
                    (row[x_key], row[y_key]),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center'
                )
            
            # Save the plot
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
        except Exception as e:
            print(f"Error creating performance chart: {str(e)}")
    
    def _create_stacked_time_chart(self, results, time_keys, time_labels, title, output_path):
        """Create a stacked bar chart for time breakdown."""
        try:
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            
            # Create labels for x-axis
            x_labels = [f"{r['format']}\n{r['transactions']} trans" for r in results]
            
            # Create the plot
            plt.figure(figsize=(12, 7))
            
            # Create the stacked bars
            bottom = np.zeros(len(results))
            for i, (key, label) in enumerate(zip(time_keys, time_labels)):
                plt.bar(x_labels, df[key], bottom=bottom, label=label)
                bottom += df[key]
            
            # Add total time labels
            for i, row in df.iterrows():
                plt.annotate(
                    f"{row['total_time']:.2f}s",
                    (i, row['total_time']),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center'
                )
            
            plt.xlabel("Statement Complexity")
            plt.ylabel("Processing Time (seconds)")
            plt.title(title)
            plt.legend()
            plt.grid(axis='y')
            
            # Save the plot
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
        except Exception as e:
            print(f"Error creating stacked time chart: {str(e)}")
    
    def _create_model_comparison_chart(self, results, output_dir):
        """Create charts comparing different models."""
        try:
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            
            # Create bar chart for detection time
            plt.figure(figsize=(10, 6))
            plt.bar(df["model"], df["detection_time"])
            plt.xlabel("Model")
            plt.ylabel("Detection Time (seconds)")
            plt.title("PII Detection Time by Model")
            plt.grid(axis='y')
            
            # Add data labels
            for i, row in df.iterrows():
                plt.annotate(
                    f"{row['detection_time']:.2f}s",
                    (i, row['detection_time']),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center'
                )
            
            # Save the plot
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "model_comparison_time.png"))
            plt.close()
            
            # Create bar chart for F1 score
            plt.figure(figsize=(10, 6))
            plt.bar(df["model"], df["f1_score"])
            plt.xlabel("Model")
            plt.ylabel("F1 Score")
            plt.title("PII Detection Accuracy by Model")
            plt.grid(axis='y')
            
            # Add data labels
            for i, row in df.iterrows():
                plt.annotate(
                    f"{row['f1_score']:.2f}",
                    (i, row['f1_score']),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center'
                )
            
            # Save the plot
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "model_comparison_accuracy.png"))
            plt.close()
            
        except Exception as e:
            print(f"Error creating model comparison charts: {str(e)}")