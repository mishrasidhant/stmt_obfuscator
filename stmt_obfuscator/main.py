"""
PDF Bank Statement Obfuscator - Main Application Module.

This module serves as the entry point for the PDF Bank Statement Obfuscator application.
It initializes the UI and connects the various components of the application.
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from stmt_obfuscator.ui.main_window import MainWindow


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path.home() / ".stmt_obfuscator" / "app.log"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Run the PDF Bank Statement Obfuscator application."""
    # Ensure log directory exists
    log_dir = Path.home() / ".stmt_obfuscator"
    log_dir.mkdir(exist_ok=True)
    
    logger.info("Starting PDF Bank Statement Obfuscator")
    
    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Bank Statement Obfuscator")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())