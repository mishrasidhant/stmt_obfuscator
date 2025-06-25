"""
Performance tests for the RAG Context Enhancer module.

This module contains tests for measuring the performance of the RAG module.
"""

import os
import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import patch

import pytest
import numpy as np
import pandas as pd
import chromadb
from chromadb.config import Settings

from stmt_obfuscator.rag.context_enhancer import RAGContextEnhancer
from tests.test_utils.data_generator import EnhancedBankStatementGenerator


class TestRAGPerformance:
    """Test suite for RAG performance metrics."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary directory for the ChromaDB cache."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def rag_enhancer(self, temp_cache_dir):
        """Create a RAGContextEnhancer with a temporary cache directory."""
        with patch('stmt_obfuscator.config.CACHE_DIR', Path(temp_cache_dir)):
            enhancer = RAGContextEnhancer(collection_name="performance_test")
            yield enhancer

    @pytest.fixture
    def data_generator(self):
        """Return an instance of the EnhancedBankStatementGenerator."""
        return EnhancedBankStatementGenerator(seed=42)

    @pytest.fixture
    def generated_statements(self, data_generator, temp_cache_dir):
        """Generate a set of synthetic bank statements for testing."""
        statements = []
        for i in range(10):  # Generate 10 statements
            statement_text, ground_truth, _ = data_generator.generate_statement(
                format_name="standard",
                pii_distribution_name="standard",
                num_transactions=15,
                include_pdf=False,
                output_dir=temp_cache_dir
            )
            statements.append({
                "text": statement_text,
                "ground_truth": ground_truth
            })
        return statements

    @pytest.fixture
    def populated_rag_enhancer(self, rag_enhancer, generated_statements):
        """Create a RAGContextEnhancer populated with test data."""
        # Initialize the knowledge base with default patterns
        rag_enhancer.initialize_knowledge_base()
        
        # Add additional patterns from generated statements
        for statement in generated_statements:
            for entity in statement["ground_truth"]["entities"]:
                # Create a simple regex pattern based on the entity text
                pattern = entity["text"].replace("(", "\\(").replace(")", "\\)").replace(".", "\\.")
                pattern = f"\\b{pattern}\\b"
                
                rag_enhancer.add_pattern(
                    pattern=pattern,
                    pattern_type=entity["type"],
                    example=entity["text"]
                )
        
        return rag_enhancer

    def test_query_latency(self, populated_rag_enhancer, generated_statements):
        """Test the latency of RAG context queries."""
        # Skip if running in CI environment
        if os.environ.get("CI") == "true":
            pytest.skip("Skipping performance test in CI environment")
        
        latencies = []
        
        # Measure query latency for each statement
        for statement in generated_statements:
            # Extract a chunk of text (first 200 characters)
            text_chunk = statement["text"][:200]
            
            # Measure query time
            start_time = time.time()
            context = populated_rag_enhancer.get_context(text_chunk)
            end_time = time.time()
            
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            latencies.append(latency)
        
        # Calculate statistics
        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
        max_latency = np.max(latencies)
        
        # Log results
        print(f"RAG Query Latency (ms):")
        print(f"  Average: {avg_latency:.2f}")
        print(f"  P95: {p95_latency:.2f}")
        print(f"  Max: {max_latency:.2f}")
        
        # Assert reasonable performance (adjust thresholds as needed)
        assert avg_latency < 500, f"Average latency ({avg_latency:.2f}ms) exceeds threshold (500ms)"
        assert p95_latency < 1000, f"P95 latency ({p95_latency:.2f}ms) exceeds threshold (1000ms)"

    def test_throughput(self, populated_rag_enhancer, generated_statements):
        """Test the throughput of RAG context queries."""
        # Skip if running in CI environment
        if os.environ.get("CI") == "true":
            pytest.skip("Skipping performance test in CI environment")
        
        # Extract text chunks from statements
        text_chunks = [statement["text"][:200] for statement in generated_statements]
        
        # Measure throughput over a fixed time period (e.g., 5 seconds)
        duration = 5  # seconds
        start_time = time.time()
        query_count = 0
        
        while time.time() - start_time < duration:
            # Cycle through text chunks
            chunk = text_chunks[query_count % len(text_chunks)]
            populated_rag_enhancer.get_context(chunk)
            query_count += 1
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # Calculate queries per second
        qps = query_count / actual_duration
        
        # Log results
        print(f"RAG Throughput:")
        print(f"  Queries: {query_count}")
        print(f"  Duration: {actual_duration:.2f}s")
        print(f"  QPS: {qps:.2f}")
        
        # Assert reasonable throughput (adjust threshold as needed)
        assert qps > 5, f"Throughput ({qps:.2f} QPS) below threshold (5 QPS)"

    def test_scaling_with_data_volume(self, rag_enhancer, data_generator, temp_cache_dir):
        """Test how RAG performance scales with increasing data volume."""
        # Skip if running in CI environment
        if os.environ.get("CI") == "true":
            pytest.skip("Skipping performance test in CI environment")
        
        # Define data volume levels to test
        volume_levels = [10, 50, 100, 200]
        
        results = []
        
        # Test each volume level
        for volume in volume_levels:
            # Reset the collection - get all IDs and then delete them
            all_ids = rag_enhancer.collection.get()["ids"]
            if all_ids:
                rag_enhancer.collection.delete(ids=all_ids)
            # Alternatively, we could delete and recreate the collection
            rag_enhancer.collection = rag_enhancer.client.get_or_create_collection(
                name=rag_enhancer.collection_name,
                metadata={"description": "PII patterns for bank statements"}
            )
            
            # Initialize with default patterns
            rag_enhancer.initialize_knowledge_base()
            
            # Add additional patterns based on volume
            pattern_count = 0
            while pattern_count < volume:
                statement_text, ground_truth, _ = data_generator.generate_statement(
                    format_name="standard",
                    pii_distribution_name="heavy",  # Use heavy distribution for more entities
                    num_transactions=15,
                    include_pdf=False,
                    output_dir=temp_cache_dir
                )
                
                for entity in ground_truth["entities"]:
                    # Create a simple regex pattern based on the entity text
                    pattern = entity["text"].replace("(", "\\(").replace(")", "\\)").replace(".", "\\.")
                    pattern = f"\\b{pattern}\\b"
                    
                    rag_enhancer.add_pattern(
                        pattern=pattern,
                        pattern_type=entity["type"],
                        example=entity["text"]
                    )
                    
                    pattern_count += 1
                    if pattern_count >= volume:
                        break
            
            # Generate a test query
            test_text = "John Doe has account number 1234-5678-9012-3456 and phone (555) 123-4567"
            
            # Measure query latency
            latencies = []
            for _ in range(10):  # Run 10 queries for each volume level
                start_time = time.time()
                context = rag_enhancer.get_context(test_text)
                end_time = time.time()
                
                latency = (end_time - start_time) * 1000  # Convert to milliseconds
                latencies.append(latency)
            
            # Calculate statistics
            avg_latency = np.mean(latencies)
            p95_latency = np.percentile(latencies, 95)
            
            # Store results
            results.append({
                "volume": volume,
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "pattern_count": pattern_count
            })
            
            # Log results
            print(f"Volume: {volume} patterns")
            print(f"  Average Latency: {avg_latency:.2f}ms")
            print(f"  P95 Latency: {p95_latency:.2f}ms")
        
        # Convert results to DataFrame for analysis
        df = pd.DataFrame(results)
        
        # Calculate scaling factor (how much latency increases per additional pattern)
        if len(df) > 1:
            scaling_factor = np.polyfit(df["volume"], df["avg_latency"], 1)[0]
            print(f"Scaling Factor: {scaling_factor:.4f}ms per pattern")
            
            # Assert sub-linear scaling (adjust threshold as needed)
            assert scaling_factor < 1.0, f"Scaling factor ({scaling_factor:.4f}) exceeds threshold (1.0)"