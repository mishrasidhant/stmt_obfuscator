"""
Pytest configuration file for the PDF Bank Statement Obfuscator.

This file contains fixtures and configuration for pytest.
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator

import pytest
import pandas as pd
import numpy as np
from faker import Faker

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import project modules
from stmt_obfuscator.pdf_parser.parser import PDFParser
from stmt_obfuscator.pii_detection.detector import PIIDetector
from stmt_obfuscator.obfuscation.obfuscator import Obfuscator
from tests.test_utils.data_generator import EnhancedBankStatementGenerator


# Basic fixtures
@pytest.fixture
def sample_pdf_path():
    """Return the path to a sample PDF file for testing."""
    return os.path.join(os.path.dirname(__file__), 'data', 'sample_statement.pdf')


@pytest.fixture
def sample_text():
    """Return sample text containing PII for testing."""
    return """
    PNC Bank
    123 Main Street, Pittsburgh, PA 15222
    Phone: (800) 555-1212
    Website: www.pnc.com

    ACCOUNT STATEMENT

    Statement Period: 01/01/2025 - 01/31/2025

    CUSTOMER INFORMATION:
    John Doe
    456 Oak Avenue, Apt 789, Anytown, CA 90210
    Phone: (555) 123-4567
    Email: john.doe@example.com

    ACCOUNT SUMMARY:
    Account Number: XXXX-XXXX-XXXX-1234
    Routing Number: 123456789
    Beginning Balance: $1,234.56
    Ending Balance: $2,345.67
    """


# Test data generator fixtures
@pytest.fixture(scope="session")
def data_generator():
    """Return an instance of the EnhancedBankStatementGenerator."""
    return EnhancedBankStatementGenerator(seed=42)


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def generated_statement(data_generator, temp_test_dir):
    """Generate a single synthetic bank statement for testing."""
    statement_text, ground_truth, _ = data_generator.generate_statement(
        format_name="standard",
        pii_distribution_name="standard",
        num_transactions=15,
        include_pdf=False,
        output_dir=temp_test_dir
    )
    
    # Save the statement to a file
    statement_path = os.path.join(temp_test_dir, "test_statement.txt")
    with open(statement_path, "w") as f:
        f.write(statement_text)
    
    # Save the ground truth to a file
    ground_truth_path = os.path.join(temp_test_dir, "test_statement_ground_truth.json")
    with open(ground_truth_path, "w") as f:
        json.dump(ground_truth, f, indent=2)
    
    return {
        "text": statement_text,
        "ground_truth": ground_truth,
        "text_path": statement_path,
        "ground_truth_path": ground_truth_path
    }


@pytest.fixture
def generated_statement_with_pdf(data_generator, temp_test_dir):
    """Generate a single synthetic bank statement with PDF for testing."""
    statement_text, ground_truth, pdf_path = data_generator.generate_statement(
        format_name="standard",
        pii_distribution_name="standard",
        num_transactions=15,
        include_pdf=True,
        output_dir=temp_test_dir
    )
    
    # Save the statement to a file
    statement_path = os.path.join(temp_test_dir, "test_statement.txt")
    with open(statement_path, "w") as f:
        f.write(statement_text)
    
    # Save the ground truth to a file
    ground_truth_path = os.path.join(temp_test_dir, "test_statement_ground_truth.json")
    with open(ground_truth_path, "w") as f:
        json.dump(ground_truth, f, indent=2)
    
    return {
        "text": statement_text,
        "ground_truth": ground_truth,
        "text_path": statement_path,
        "ground_truth_path": ground_truth_path,
        "pdf_path": pdf_path
    }


@pytest.fixture
def generated_dataset(data_generator, temp_test_dir):
    """Generate a dataset of synthetic bank statements for testing."""
    samples = data_generator.generate_dataset(
        num_samples=5,
        output_dir=temp_test_dir,
        include_pdfs=False
    )
    
    return {
        "samples": samples,
        "dir": temp_test_dir
    }


# Component fixtures
@pytest.fixture
def pdf_parser():
    """Return an instance of the PDFParser."""
    return PDFParser()


@pytest.fixture
def pii_detector():
    """Return an instance of the PIIDetector."""
    return PIIDetector()


@pytest.fixture
def obfuscator():
    """Return an instance of the Obfuscator."""
    return Obfuscator()


# Mock fixtures for testing
@pytest.fixture
def mock_pii_entities():
    """Return mock PII entities for testing."""
    return {
        "entities": [
            {
                "type": "PERSON_NAME",
                "text": "John Doe",
                "start": 123,
                "end": 131,
                "confidence": 0.95
            },
            {
                "type": "ADDRESS",
                "text": "456 Oak Avenue, Apt 789, Anytown, CA 90210",
                "start": 156,
                "end": 201,
                "confidence": 0.92
            },
            {
                "type": "PHONE_NUMBER",
                "text": "(555) 123-4567",
                "start": 209,
                "end": 223,
                "confidence": 0.98
            },
            {
                "type": "EMAIL",
                "text": "john.doe@example.com",
                "start": 230,
                "end": 250,
                "confidence": 0.99
            },
            {
                "type": "ACCOUNT_NUMBER",
                "text": "1234",
                "start": 287,
                "end": 291,
                "confidence": 0.90
            },
            {
                "type": "ROUTING_NUMBER",
                "text": "123456789",
                "start": 310,
                "end": 319,
                "confidence": 0.94
            }
        ]
    }


@pytest.fixture
def mock_document_structure():
    """Return a mock document structure for testing."""
    return {
        "metadata": {
            "title": "Test Bank Statement",
            "author": "Test Bank",
            "subject": "Monthly Statement",
            "keywords": "bank,statement,test",
            "creator": "PDF Generator"
        },
        "page_count": 2,
        "full_text": sample_text(),
        "text_blocks": [
            {
                "page": 1,
                "text": "PNC Bank",
                "bbox": (10, 10, 100, 30)
            },
            {
                "page": 1,
                "text": "123 Main Street, Pittsburgh, PA 15222",
                "bbox": (10, 40, 300, 60)
            },
            {
                "page": 1,
                "text": "John Doe",
                "bbox": (10, 100, 100, 120)
            }
        ],
        "layout_map": {}
    }


# Performance testing fixtures
@pytest.fixture
def benchmark_results_dir(temp_test_dir):
    """Create a directory for benchmark results."""
    benchmark_dir = os.path.join(temp_test_dir, "benchmarks")
    os.makedirs(benchmark_dir, exist_ok=True)
    return benchmark_dir