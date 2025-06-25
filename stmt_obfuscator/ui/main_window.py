"""
Main Window UI for the PDF Bank Statement Obfuscator.

This module defines the main application window and its components.
"""

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QProgressBar,
    QStatusBar,
    QMessageBox,
)
from PyQt6.QtGui import QIcon, QAction

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window for the PDF Bank Statement Obfuscator."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle("PDF Bank Statement Obfuscator")
        self.setMinimumSize(QSize(800, 600))
        
        # Initialize UI components
        self._init_ui()
        self._create_menu()
        
        # Set up status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        logger.info("Main window initialized")

    def _init_ui(self):
        """Initialize the UI components."""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("PDF Bank Statement Obfuscator")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px;")
        main_layout.addWidget(header_label)
        
        # Add file selection area
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("font-style: italic;")
        
        select_file_button = QPushButton("Select PDF")
        select_file_button.clicked.connect(self._on_select_file)
        
        file_layout.addWidget(QLabel("Input File:"))
        file_layout.addWidget(self.file_path_label, 1)
        file_layout.addWidget(select_file_button)
        
        main_layout.addLayout(file_layout)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Add action buttons
        button_layout = QHBoxLayout()
        
        self.process_button = QPushButton("Process PDF")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self._on_process_file)
        
        button_layout.addStretch()
        button_layout.addWidget(self.process_button)
        
        main_layout.addLayout(button_layout)
        
        # Add spacer
        main_layout.addStretch(1)

    def _create_menu(self):
        """Create the application menu."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        open_action = QAction("&Open PDF...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_select_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _on_select_file(self):
        """Handle file selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.file_path_label.setText(str(file_path))
            self.process_button.setEnabled(True)
            self.status_bar.showMessage(f"Selected file: {Path(file_path).name}")
            logger.info(f"Selected file: {file_path}")

    def _on_process_file(self):
        """Handle file processing."""
        # This is a placeholder for the actual processing logic
        self.status_bar.showMessage("Processing file...")
        self.process_button.setEnabled(False)
        
        # TODO: Implement actual processing logic
        
        QMessageBox.information(
            self,
            "Not Implemented",
            "PDF processing is not yet implemented.",
        )
        
        self.process_button.setEnabled(True)
        self.status_bar.showMessage("Ready")

    def _show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About PDF Bank Statement Obfuscator",
            "PDF Bank Statement Obfuscator v0.1.0\n\n"
            "A privacy-focused desktop application for removing PII from bank statements.\n\n"
            "© 2025",
        )