# RAG Module Test Suite

This directory contains the test suite for the RAG (Retrieval-Augmented Generation) module of the PDF Bank Statement Obfuscator project.

## Overview

The RAG module enhances PII detection by providing contextual information from a vector database (ChromaDB). This test suite verifies the functionality, integration, and performance of the RAG module.

## Test Structure

The test suite is organized into three main categories:

### 1. Unit Tests (`test_context_enhancer.py`)

These tests verify the core functionality of the RAG module in isolation, with mocked dependencies:

- Initialization and configuration
- Context retrieval functionality
- Pattern addition
- Knowledge base initialization
- Error handling and edge cases

### 2. Integration Tests (`../integration/test_rag_integration.py`)

These tests verify the interaction between the RAG module and other components:

- Integration with the PII detection system
- Verification that context enhancement improves PII detection accuracy
- Testing with actual ChromaDB instances

### 3. Performance Tests (`../performance/test_rag_performance.py`)

These tests measure the performance characteristics of the RAG module:

- Query latency
- Throughput
- Scaling with data volume

### 4. Test Utilities (`test_data.py`)

Utilities for generating synthetic test data for RAG module tests:

- PII pattern generation
- Text with PII entities
- Mock ChromaDB query results

## Running the Tests

### Prerequisites

Ensure you have all the required dependencies installed:

```bash
pip install -r requirements.txt
```

### Running All RAG Tests

To run all tests for the RAG module:

```bash
pytest tests/rag tests/integration/test_rag_integration.py tests/performance/test_rag_performance.py -v
```

### Running Specific Test Categories

To run only unit tests:

```bash
pytest tests/rag/test_context_enhancer.py -v
```

To run only integration tests:

```bash
pytest tests/integration/test_rag_integration.py -v
```

To run only performance tests:

```bash
pytest tests/performance/test_rag_performance.py -v
```

### Running with Coverage

To run tests with coverage reporting:

```bash
pytest tests/rag tests/integration/test_rag_integration.py --cov=stmt_obfuscator.rag
```

## Test Data

The tests use a combination of:

1. Mocked data for unit tests
2. Synthetic data generated using `test_data.py` and `tests/test_utils/data_generator.py`
3. Real ChromaDB instances with test data for integration and performance tests

## Notes

- Performance tests are skipped in CI environments to avoid inconsistent results
- Some tests require significant memory for ChromaDB operations
- The test suite is designed to be idempotent and not affect the production environment