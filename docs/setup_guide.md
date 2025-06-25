# Local Setup Guide

This guide provides instructions for setting up the PDF Bank Statement Obfuscator project locally.

## Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)

## Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd stmt_obfuscator
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Known Issues and Workarounds

### PyMuPDF Installation Issues

The project depends on PyMuPDF (fitz) for PDF parsing. There might be issues with installing the exact version required:

#### Issue 1: Building PyMuPDF from source fails

If you encounter errors when pip tries to build PyMuPDF from source, you can try the following:

1. Install the binary distribution instead:
   ```bash
   pip install --only-binary=pymupdf pymupdf==1.23.7
   ```

2. If that doesn't work, you can use the PyMuPDFb package which contains just the shared libraries:
   ```bash
   pip install PyMuPDFb==1.23.7
   ```

#### Issue 2: `Rect` class not found

If you encounter an error like `ImportError: cannot import name 'Rect' from 'fitz'`, this is due to differences in PyMuPDF versions. The code has been updated to handle this, but if you encounter this in other parts of the code, you can:

1. Use tuples for bounding boxes instead of the `Rect` class
2. Add a fallback mechanism:
   ```python
   try:
       from fitz import Rect
   except ImportError:
       # Define a simple tuple-based bounding box
       pass
   ```

### Testing with Mock Objects

When running tests, you might encounter issues with MagicMock objects. The code has been updated to handle these cases, but if you're adding new functionality, keep in mind:

1. Always add proper error handling for attributes that might be mocked
2. Check for instance types before performing operations
3. Use try/except blocks to catch potential errors

## Running Tests

To run the tests:

```bash
pytest
```

To run specific test modules:

```bash
pytest tests/pdf_parser/test_parser.py
pytest tests/obfuscation/test_obfuscator.py
```

## Running the Application

To run the application:

```bash
python -m stmt_obfuscator.main
```

## Troubleshooting

For more detailed troubleshooting information, see [Troubleshooting Guide](troubleshooting.md).
