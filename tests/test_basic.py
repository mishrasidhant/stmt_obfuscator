"""
Basic tests to verify that the testing infrastructure is working correctly.
"""

import os
import sys
import pytest


def test_environment_setup():
    """Test that the environment is set up correctly."""
    # Check that the project root is in the Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    assert project_root in sys.path, "Project root not in Python path"
    
    # Check that we can import from the project
    import stmt_obfuscator
    assert stmt_obfuscator is not None, "Failed to import stmt_obfuscator package"


def test_sample_text_fixture(sample_text):
    """Test that the sample_text fixture is working."""
    assert sample_text is not None, "sample_text fixture not working"
    assert "PNC Bank" in sample_text, "Expected content not in sample_text"
    assert "John Doe" in sample_text, "Expected PII not in sample_text"