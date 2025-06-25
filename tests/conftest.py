"""
Pytest configuration file for the PDF Bank Statement Obfuscator.

This file contains fixtures and configuration for pytest.
"""

import os
import sys
import pytest

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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