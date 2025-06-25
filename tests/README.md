# PDF Bank Statement Obfuscator Testing Framework

This directory contains a comprehensive testing framework for the PDF Bank Statement Obfuscator. The framework includes unit tests, integration tests, end-to-end tests, performance benchmarks, and UI tests.

## Overview

The testing framework is designed to:

1. Create diverse synthetic bank statement samples for testing
2. Test PII detection across different statement types and formats
3. Evaluate performance for different PII types separately
4. Benchmark multiple Ollama models (if available)
5. Validate transaction integrity after obfuscation
6. Test the UI components and user interactions

## Directory Structure

- `tests/` - Root directory for all tests
  - `conftest.py` - Pytest configuration and fixtures
  - `test_basic.py` - Basic tests to verify the testing infrastructure
  - `test_utils/` - Utilities for testing
    - `data_generator.py` - Synthetic bank statement generator
  - `pii_detection/` - Tests for the PII detection module
    - `test_detector_unit.py` - Unit tests for the PII detector
  - `integration/` - Integration tests
    - `test_parser_detector_integration.py` - Tests for PDF parser and PII detector integration
    - `test_detector_obfuscator_integration.py` - Tests for PII detector and obfuscator integration
  - `end_to_end/` - End-to-end tests
    - `test_complete_workflow.py` - Tests for the complete workflow
  - `performance/` - Performance benchmarks
    - `test_benchmarks.py` - Performance benchmark tests
  - `ui/` - UI tests
    - `test_ui_components.py` - Tests for UI components
  - `run_tests.py` - Script to run tests and generate reports
  - `README.md` - This file

## Requirements

To run the tests, you need:

1. Python 3.8 or higher
2. PyQt6 (for UI tests)
3. Pytest and related packages
4. Ollama running locally (for PII detection tests)
5. Other dependencies as specified in `pyproject.toml`

You can install the required packages with:

```bash
pip install -e ".[dev]"
```

## Running Tests

### Using the Test Runner

The easiest way to run the tests is to use the `run_tests.py` script:

```bash
python tests/run_tests.py --test-types unit integration end_to_end
```

Available test types:
- `unit` - Unit tests for individual components
- `integration` - Integration tests for component interactions
- `end_to_end` - End-to-end tests for the complete workflow
- `performance` - Performance benchmark tests
- `ui` - UI tests
- `all` - All test types

Additional options:
- `--output-dir` - Directory to save test results (default: `test_results`)
- `--verbose` - Show verbose output

### Running Tests Manually

You can also run the tests manually using pytest:

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/pii_detection/
pytest tests/integration/
pytest tests/end_to_end/
pytest tests/performance/
pytest tests/ui/

# Run with verbose output
pytest -v

# Generate HTML report
pytest --html=report.html --self-contained-html
```

## Test Data Generation

The testing framework includes a synthetic bank statement generator that can create diverse test data with ground truth annotations. You can use this generator to create test data for your own tests:

```python
from tests.test_utils.data_generator import EnhancedBankStatementGenerator

# Create a generator
generator = EnhancedBankStatementGenerator(seed=42)

# Generate a single statement
statement_text, ground_truth, pdf_path = generator.generate_statement(
    format_name="standard",
    pii_distribution_name="standard",
    num_transactions=15,
    include_pdf=True,
    output_dir="test_data"
)

# Generate a dataset
samples = generator.generate_dataset(
    num_samples=10,
    output_dir="test_data",
    include_pdfs=True
)
```

## Performance Benchmarks

The performance benchmark tests measure:

1. PII detection performance with different text sizes
2. Obfuscation performance with different numbers of entities
3. PDF parsing performance with different PDF sizes
4. End-to-end performance with different statement complexities
5. Performance comparison of different Ollama models

The benchmark results are saved as JSON files and visualized as charts.

## UI Tests

The UI tests verify that the UI components work correctly. These tests use PyQt's testing framework to simulate user interactions with the application.

Note: UI tests require PyQt6 to be installed and may not work in headless environments.

## Continuous Integration

The testing framework is designed to be used in a continuous integration (CI) pipeline. The `run_tests.py` script generates JUnit XML reports that can be consumed by CI systems.

## Extending the Framework

To add new tests:

1. Create a new test file in the appropriate directory
2. Use the existing fixtures from `conftest.py`
3. Follow the pytest conventions for test naming and organization
4. Update this README if necessary

## Troubleshooting

### Ollama Tests

If Ollama is not available, the tests that require Ollama will be skipped. To run these tests, make sure Ollama is running locally and the required models are available.

### UI Tests

If PyQt6 is not installed, the UI tests will be skipped. To run these tests, install PyQt6:

```bash
pip install PyQt6
```

### PDF Generation

If PDF generation fails, the tests that require PDFs will be skipped. This may happen if the required dependencies for PDF generation are not installed.