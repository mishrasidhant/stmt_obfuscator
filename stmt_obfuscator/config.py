"""
Configuration module for the PDF Bank Statement Obfuscator.

This module contains configuration settings for the application.
"""

import os
from pathlib import Path
from typing import Any, Dict

# Application paths
APP_DIR = Path.home() / ".stmt_obfuscator"
LOG_DIR = APP_DIR / "logs"
CACHE_DIR = APP_DIR / "cache"
CONFIG_FILE = APP_DIR / "config.yaml"

# Ensure directories exist
APP_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# Ollama configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:7b-instruct")
FALLBACK_MODEL = "llama3:8b"

# PII detection configuration
CONFIDENCE_THRESHOLD = 0.85
RAG_ENABLED = True

# PDF processing configuration
MAX_PAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB

# PDF export configuration
PDF_EXPORT_ENABLED = True
PDF_DEFAULT_FONT = "Helvetica"
PDF_FONT_SIZE = 11
PDF_MARGIN = 72  # 1 inch in points
PDF_INCLUDE_TIMESTAMP = True
PDF_INCLUDE_METADATA = True
PDF_FONT_FALLBACKS = ["Times-Roman", "Courier", "Symbol", "ZapfDingbats"]

# UI configuration
UI_THEME = "light"  # "light" or "dark"
UI_FONT_SIZE = 12


def get_default_config() -> Dict[str, Any]:
    """Return the default configuration."""
    return {
        "ollama": {
            "host": OLLAMA_HOST,
            "default_model": DEFAULT_MODEL,
            "fallback_model": FALLBACK_MODEL,
        },
        "pii_detection": {
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "rag_enabled": RAG_ENABLED,
        },
        "pdf_processing": {
            "max_page_size": MAX_PAGE_SIZE,
            "max_document_size": MAX_DOCUMENT_SIZE,
        },
        "pdf_export": {
            "enabled": PDF_EXPORT_ENABLED,
            "default_font": PDF_DEFAULT_FONT,
            "font_size": PDF_FONT_SIZE,
            "margin": PDF_MARGIN,
            "include_timestamp": PDF_INCLUDE_TIMESTAMP,
            "include_metadata": PDF_INCLUDE_METADATA,
            "font_fallbacks": PDF_FONT_FALLBACKS,
        },
        "ui": {
            "theme": UI_THEME,
            "font_size": UI_FONT_SIZE,
        },
    }
