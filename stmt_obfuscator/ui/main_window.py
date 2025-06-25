"""
Main Window UI for the PDF Bank Statement Obfuscator.

This module defines the main application window and its components.
"""

import logging
import os
from pathlib import Path
import threading
from typing import Dict, List, Any, Optional

from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject, pyqtSlot
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
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QTextEdit,
    QSplitter,
    QScrollArea,
    QFrame,
    QGridLayout,
    QToolButton,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
)
from PyQt6.QtGui import QIcon, QAction, QColor, QFont, QPixmap

from stmt_obfuscator.pdf_parser.parser import PDFParser
from stmt_obfuscator.pii_detection.detector import PIIDetector
from stmt_obfuscator.obfuscation.obfuscator import Obfuscator

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """Signals for worker thread communication."""

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal(object)


class ProcessingWorker(threading.Thread):
    """Worker thread for PDF processing."""

    def __init__(self, pdf_path: str):
        """Initialize the worker thread."""
        super().__init__()
        self.pdf_path = pdf_path
        self.signals = WorkerSignals()
        self.daemon = True
        self.cancelled = False

    def run(self):
        """Run the processing task."""
        try:
            # Initialize components
            self.signals.status.emit("Initializing...")
            self.signals.progress.emit(5)

            parser = PDFParser()
            detector = PIIDetector()
            obfuscator = Obfuscator()

            # Load PDF
            self.signals.status.emit("Loading PDF...")
            self.signals.progress.emit(10)
            if not parser.load_pdf(self.pdf_path):
                self.signals.error.emit("Failed to load PDF file")
                return

            # Extract text
            self.signals.status.emit("Extracting text...")
            self.signals.progress.emit(20)
            parser.extract_text()

            # Detect tables
            self.signals.status.emit("Detecting tables...")
            self.signals.progress.emit(30)
            parser.detect_tables()

            # Get document structure for PII detection
            self.signals.status.emit("Preparing document for PII detection...")
            self.signals.progress.emit(40)
            document = parser.get_text_for_pii_detection()

            # Detect PII
            self.signals.status.emit("Detecting PII entities...")
            self.signals.progress.emit(50)
            pii_entities = detector.detect_pii(document["full_text"])

            # Map PII entities to document positions
            self.signals.status.emit("Mapping PII entities to document...")
            self.signals.progress.emit(70)

            # Prepare results for review
            self.signals.status.emit("Preparing results for review...")
            self.signals.progress.emit(90)

            # Create result object
            result = {
                "document": document,
                "pii_entities": pii_entities.get("entities", []),
                "parser": parser,
                "detector": detector,
                "obfuscator": obfuscator,
            }

            self.signals.progress.emit(100)
            self.signals.status.emit("Processing complete")
            self.signals.finished.emit(result)

        except Exception as e:
            logger.error(f"Error in processing worker: {e}")
            self.signals.error.emit(f"Processing error: {str(e)}")

    def cancel(self):
        """Cancel the processing task."""
        self.cancelled = True


class PIIEntityDialog(QDialog):
    """Dialog for adding or editing a PII entity."""

    def __init__(self, parent=None, entity=None, text=""):
        """Initialize the dialog."""
        super().__init__(parent)
        self.entity = entity
        self.full_text = text
        self.setWindowTitle("Add PII Entity" if entity is None else "Edit PII Entity")
        self.setMinimumWidth(500)
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)

        # Entity type selection
        type_group = QGroupBox("Entity Type")
        type_layout = QVBoxLayout()

        self.entity_types = [
            "PERSON_NAME",
            "ADDRESS",
            "ACCOUNT_NUMBER",
            "ROUTING_NUMBER",
            "PHONE_NUMBER",
            "EMAIL",
            "ORGANIZATION_NAME",
            "CREDIT_CARD_NUMBER",
            "SSN",
            "DATE_OF_BIRTH",
            "IP_ADDRESS",
            "URL",
        ]

        self.type_combo = QComboBox()
        self.type_combo.addItems(self.entity_types)
        if self.entity and "type" in self.entity:
            index = (
                self.entity_types.index(self.entity["type"])
                if self.entity["type"] in self.entity_types
                else 0
            )
            self.type_combo.setCurrentIndex(index)

        type_layout.addWidget(self.type_combo)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Text selection
        text_group = QGroupBox("Entity Text")
        text_layout = QVBoxLayout()

        if self.full_text:
            # Show a preview of the document text
            preview_label = QLabel("Document Preview:")
            text_layout.addWidget(preview_label)

            preview_text = QTextEdit()
            preview_text.setReadOnly(True)
            preview_text.setText(
                self.full_text[:1000] + ("..." if len(self.full_text) > 1000 else "")
            )
            preview_text.setMaximumHeight(100)
            text_layout.addWidget(preview_text)

        text_label = QLabel("Entity Text:")
        text_layout.addWidget(text_label)

        self.text_edit = QLineEdit()
        if self.entity and "text" in self.entity:
            self.text_edit.setText(self.entity["text"])
        text_layout.addWidget(self.text_edit)

        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # Confidence
        confidence_group = QGroupBox("Confidence")
        confidence_layout = QHBoxLayout()

        confidence_label = QLabel("Confidence Level:")
        confidence_layout.addWidget(confidence_label)

        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(1, 100)
        self.confidence_spin.setSuffix("%")
        if self.entity and "confidence" in self.entity:
            self.confidence_spin.setValue(int(self.entity["confidence"] * 100))
        else:
            self.confidence_spin.setValue(90)  # Default 90%

        confidence_layout.addWidget(self.confidence_spin)
        confidence_group.setLayout(confidence_layout)
        layout.addWidget(confidence_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_entity(self):
        """Get the entity data from the dialog."""
        entity_type = self.type_combo.currentText()
        entity_text = self.text_edit.text()
        confidence = self.confidence_spin.value() / 100.0

        entity = {
            "type": entity_type,
            "text": entity_text,
            "confidence": confidence,
        }

        # If editing an existing entity, preserve other fields
        if self.entity:
            for key, value in self.entity.items():
                if key not in entity:
                    entity[key] = value

        return entity


class MainWindow(QMainWindow):
    """Main application window for the PDF Bank Statement Obfuscator."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        self.setWindowTitle("PDF Bank Statement Obfuscator")
        self.setMinimumSize(QSize(1000, 700))

        # Initialize data
        self.pdf_path = None
        self.processing_worker = None
        self.processing_result = None
        self.pii_entities = []
        self.document_text = ""
        self.entity_inclusion = {}  # Track which entities to include in obfuscation

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

        # Add tab widget for different stages
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # Create tabs
        self.pii_review_tab = self._create_pii_review_tab()
        self.output_preview_tab = self._create_output_preview_tab()

        # Add tabs to widget
        self.tab_widget.addTab(self.pii_review_tab, "PII Review")
        self.tab_widget.addTab(self.output_preview_tab, "Output Preview")

        # Disable tabs initially
        self.tab_widget.setEnabled(False)

        main_layout.addWidget(self.tab_widget, 1)

        # Add action buttons
        button_layout = QHBoxLayout()

        self.process_button = QPushButton("Process PDF")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self._on_process_file)

        self.save_button = QPushButton("Save Obfuscated PDF")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._on_save_file)

        button_layout.addStretch()
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)

    def _create_pii_review_tab(self):
        """Create the PII review tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Create a splitter for the review area
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Top section: PII entities table
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        # Table controls
        table_controls = QHBoxLayout()

        confidence_label = QLabel("Confidence Threshold:")
        self.confidence_threshold = QSpinBox()
        self.confidence_threshold.setRange(1, 100)
        self.confidence_threshold.setValue(70)
        self.confidence_threshold.setSuffix("%")
        self.confidence_threshold.valueChanged.connect(self._filter_pii_table)

        add_entity_button = QPushButton("Add Entity")
        add_entity_button.clicked.connect(self._add_pii_entity)

        table_controls.addWidget(confidence_label)
        table_controls.addWidget(self.confidence_threshold)
        table_controls.addStretch()
        table_controls.addWidget(add_entity_button)

        top_layout.addLayout(table_controls)

        # PII entities table
        self.pii_table = QTableWidget()
        self.pii_table.setColumnCount(5)
        self.pii_table.setHorizontalHeaderLabels(
            ["Type", "Text", "Confidence", "Actions", "Include"]
        )
        self.pii_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.pii_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pii_table.itemSelectionChanged.connect(self._on_pii_selection_changed)

        top_layout.addWidget(self.pii_table)

        # Bottom section: Document preview with highlighted PII
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        preview_label = QLabel("Document Preview:")
        bottom_layout.addWidget(preview_label)

        self.document_preview = QTextEdit()
        self.document_preview.setReadOnly(True)
        bottom_layout.addWidget(self.document_preview)

        # Add widgets to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([300, 400])

        layout.addWidget(splitter)

        return tab

    def _create_output_preview_tab(self):
        """Create the output preview tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Create a splitter for the preview area
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left section: Original document
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        original_label = QLabel("Original Document:")
        left_layout.addWidget(original_label)

        self.original_preview = QTextEdit()
        self.original_preview.setReadOnly(True)
        left_layout.addWidget(self.original_preview)

        # Right section: Obfuscated document
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        obfuscated_label = QLabel("Obfuscated Document:")
        right_layout.addWidget(obfuscated_label)

        self.obfuscated_preview = QTextEdit()
        self.obfuscated_preview.setReadOnly(True)
        right_layout.addWidget(self.obfuscated_preview)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        layout.addWidget(splitter)

        # Add preview controls
        controls_layout = QHBoxLayout()

        self.preview_button = QPushButton("Generate Preview")
        self.preview_button.clicked.connect(self._generate_preview)
        self.preview_button.setEnabled(False)

        controls_layout.addStretch()
        controls_layout.addWidget(self.preview_button)

        layout.addLayout(controls_layout)

        return tab

    def _create_menu(self):
        """Create the application menu."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open PDF...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_select_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Obfuscated PDF...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_file)
        save_action.setEnabled(False)
        self.save_action = save_action
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")

        add_entity_action = QAction("&Add PII Entity", self)
        add_entity_action.triggered.connect(self._add_pii_entity)
        edit_menu.addAction(add_entity_action)

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
            self.pdf_path = file_path
            self.file_path_label.setText(str(file_path))
            self.process_button.setEnabled(True)
            self.status_bar.showMessage(f"Selected file: {Path(file_path).name}")
            logger.info(f"Selected file: {file_path}")

            # Reset UI state
            self.progress_bar.setValue(0)
            self.tab_widget.setEnabled(False)
            self.save_button.setEnabled(False)
            self.save_action.setEnabled(False)
            self.preview_button.setEnabled(False)
            self.pii_table.setRowCount(0)
            self.document_preview.clear()
            self.original_preview.clear()
            self.obfuscated_preview.clear()

    def _on_process_file(self):
        """Handle file processing."""
        if not self.pdf_path:
            return

        # Disable UI during processing
        self.process_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Processing file...")

        # Start processing in a background thread
        self.processing_worker = ProcessingWorker(self.pdf_path)
        self.processing_worker.signals.progress.connect(self._update_progress)
        self.processing_worker.signals.status.connect(self._update_status)
        self.processing_worker.signals.error.connect(self._show_error)
        self.processing_worker.signals.finished.connect(self._processing_finished)
        self.processing_worker.start()

    def _update_progress(self, value):
        """Update the progress bar."""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update the status bar."""
        self.status_bar.showMessage(message)

    def _show_error(self, message):
        """Show an error message."""
        QMessageBox.critical(self, "Processing Error", message)
        self.process_button.setEnabled(True)
        self.status_bar.showMessage("Ready")

    def _processing_finished(self, result):
        """Handle processing completion."""
        self.processing_result = result
        self.document_text = result["document"]["full_text"]
        self.pii_entities = result["pii_entities"]

        # Initialize entity inclusion map
        self.entity_inclusion = {i: True for i in range(len(self.pii_entities))}

        # Update UI
        self.status_bar.showMessage(
            "Processing complete. Review detected PII entities."
        )
        self.process_button.setEnabled(True)
        self.tab_widget.setEnabled(True)
        self.preview_button.setEnabled(True)

        # Populate PII table
        self._populate_pii_table()

        # Update document preview
        self._update_document_preview()

        # Switch to PII review tab
        self.tab_widget.setCurrentIndex(0)

    def _populate_pii_table(self):
        """Populate the PII entities table."""
        self.pii_table.setRowCount(0)

        threshold = self.confidence_threshold.value() / 100.0

        for i, entity in enumerate(self.pii_entities):
            if entity.get("confidence", 1.0) < threshold:
                continue

            row = self.pii_table.rowCount()
            self.pii_table.insertRow(row)

            # Type
            type_item = QTableWidgetItem(entity.get("type", "UNKNOWN"))
            self.pii_table.setItem(row, 0, type_item)

            # Text
            text_item = QTableWidgetItem(entity.get("text", ""))
            self.pii_table.setItem(row, 1, text_item)

            # Confidence
            confidence = entity.get("confidence", 1.0)
            confidence_item = QTableWidgetItem(f"{confidence:.2f}")

            # Color-code confidence
            if confidence >= 0.9:
                confidence_item.setBackground(QColor(200, 255, 200))  # Light green
            elif confidence >= 0.7:
                confidence_item.setBackground(QColor(255, 255, 200))  # Light yellow
            else:
                confidence_item.setBackground(QColor(255, 200, 200))  # Light red

            self.pii_table.setItem(row, 2, confidence_item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)

            edit_button = QToolButton()
            edit_button.setText("Edit")
            edit_button.clicked.connect(
                lambda checked, idx=i: self._edit_pii_entity(idx)
            )

            delete_button = QToolButton()
            delete_button.setText("Delete")
            delete_button.clicked.connect(
                lambda checked, idx=i: self._delete_pii_entity(idx)
            )

            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            actions_layout.addStretch()

            self.pii_table.setCellWidget(row, 3, actions_widget)

            # Include checkbox
            include_widget = QWidget()
            include_layout = QHBoxLayout(include_widget)
            include_layout.setContentsMargins(2, 2, 2, 2)
            include_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            include_checkbox = QCheckBox()
            include_checkbox.setChecked(self.entity_inclusion.get(i, True))
            include_checkbox.stateChanged.connect(
                lambda state, idx=i: self._toggle_entity_inclusion(idx, state)
            )

            include_layout.addWidget(include_checkbox)

            self.pii_table.setCellWidget(row, 4, include_widget)

    def _filter_pii_table(self):
        """Filter the PII table based on confidence threshold."""
        self._populate_pii_table()
        self._update_document_preview()

    def _update_document_preview(self):
        """Update the document preview with highlighted PII entities."""
        if not self.document_text:
            return

        # Create HTML for the document with highlighted PII
        html = "<html><body style='font-family: monospace;'>"

        # Get the threshold
        threshold = self.confidence_threshold.value() / 100.0

        # Create a list of entities to highlight
        entities_to_highlight = []
        for i, entity in enumerate(self.pii_entities):
            if entity.get("confidence", 1.0) >= threshold and self.entity_inclusion.get(
                i, True
            ):
                entities_to_highlight.append((i, entity))

        # If there are no entities to highlight, just show the plain text
        if not entities_to_highlight:
            html += self.document_text.replace("\n", "<br>").replace(" ", "&nbsp;")
        else:
            # Sort entities by position if available
            if all(
                "start" in entity and "end" in entity
                for _, entity in entities_to_highlight
            ):
                entities_to_highlight.sort(key=lambda x: x[1]["start"])

            # Highlight entities in the text
            last_pos = 0
            for i, entity in entities_to_highlight:
                if "start" in entity and "end" in entity:
                    # Add text before this entity
                    html += (
                        self.document_text[last_pos : entity["start"]]
                        .replace("\n", "<br>")
                        .replace(" ", "&nbsp;")
                    )

                    # Add highlighted entity
                    confidence = entity.get("confidence", 1.0)
                    if confidence >= 0.9:
                        color = "#c8ffc8"  # Light green
                    elif confidence >= 0.7:
                        color = "#ffffc8"  # Light yellow
                    else:
                        color = "#ffc8c8"  # Light red

                    entity_text = self.document_text[entity["start"] : entity["end"]]
                    html += f'<span style="background-color: {color}; border: 1px solid #888; border-radius: 2px;" title="{entity["type"]} (Confidence: {confidence:.2f})">{entity_text.replace("\n", "<br>").replace(" ", "&nbsp;")}</span>'

                    last_pos = entity["end"]

            # Add remaining text
            html += (
                self.document_text[last_pos:]
                .replace("\n", "<br>")
                .replace(" ", "&nbsp;")
            )

        html += "</body></html>"

        # Set the HTML in the preview
        self.document_preview.setHtml(html)

    def _on_pii_selection_changed(self):
        """Handle PII table selection change."""
        selected_rows = self.pii_table.selectedItems()
        if not selected_rows:
            return

        # Get the selected row
        row = selected_rows[0].row()

        # Get the entity text
        text_item = self.pii_table.item(row, 1)
        if not text_item:
            return

        entity_text = text_item.text()

        # Find the entity in the document and scroll to it
        if self.document_text and entity_text in self.document_text:
            # Find the position of the entity in the text
            pos = self.document_text.find(entity_text)
            if pos >= 0:
                # Create a cursor at that position
                cursor = self.document_preview.textCursor()
                cursor.setPosition(pos)
                cursor.setPosition(
                    pos + len(entity_text), QTextEdit.ExtraSelection.KeepAnchor
                )

                # Set the cursor and ensure it's visible
                self.document_preview.setTextCursor(cursor)
                self.document_preview.ensureCursorVisible()

    def _add_pii_entity(self):
        """Add a new PII entity."""
        if not self.document_text:
            QMessageBox.warning(self, "No Document", "Please process a document first.")
            return

        dialog = PIIEntityDialog(self, text=self.document_text)
        if dialog.exec():
            entity = dialog.get_entity()

            # Add the entity to the list
            self.pii_entities.append(entity)

            # Update the inclusion map
            self.entity_inclusion[len(self.pii_entities) - 1] = True

            # Update the UI
            self._populate_pii_table()
            self._update_document_preview()

    def _edit_pii_entity(self, entity_index):
        """Edit a PII entity."""
        if entity_index < 0 or entity_index >= len(self.pii_entities):
            return

        entity = self.pii_entities[entity_index]
        dialog = PIIEntityDialog(self, entity=entity, text=self.document_text)

        if dialog.exec():
            # Update the entity
            self.pii_entities[entity_index] = dialog.get_entity()

            # Update the UI
            self._populate_pii_table()
            self._update_document_preview()

    def _delete_pii_entity(self, entity_index):
        """Delete a PII entity."""
        if entity_index < 0 or entity_index >= len(self.pii_entities):
            return

        # Confirm deletion
        entity = self.pii_entities[entity_index]
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the {entity.get('type', 'UNKNOWN')} entity '{entity.get('text', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            # Remove the entity
            self.pii_entities.pop(entity_index)

            # Update the inclusion map
            new_inclusion = {}
            for i in range(len(self.pii_entities)):
                if i < entity_index:
                    new_inclusion[i] = self.entity_inclusion.get(i, True)
                else:
                    new_inclusion[i] = self.entity_inclusion.get(i + 1, True)

            self.entity_inclusion = new_inclusion

            # Update the UI
            self._populate_pii_table()
            self._update_document_preview()

    def _toggle_entity_inclusion(self, entity_index, state):
        """Toggle the inclusion of a PII entity in obfuscation."""
        if entity_index < 0 or entity_index >= len(self.pii_entities):
            return

        self.entity_inclusion[entity_index] = bool(state)
        self._update_document_preview()

    def _generate_preview(self):
        """Generate a preview of the obfuscated document."""
        if not self.processing_result:
            return

        # Show the original document
        self.original_preview.setText(self.document_text)

        # Get the selected entities for obfuscation
        selected_entities = [
            entity
            for i, entity in enumerate(self.pii_entities)
            if self.entity_inclusion.get(i, True)
        ]

        # Create a worker to generate the preview
        self.status_bar.showMessage("Generating obfuscation preview...")

        try:
            # Get the obfuscator from the processing result
            obfuscator = self.processing_result["obfuscator"]
            document = self.processing_result["document"]

            # Obfuscate the document
            obfuscated_document = obfuscator.obfuscate_document(
                document, selected_entities
            )

            # Show the obfuscated document
            if "full_text" in obfuscated_document:
                self.obfuscated_preview.setText(obfuscated_document["full_text"])
            else:
                self.obfuscated_preview.setText(
                    "Error: Could not generate obfuscated text"
                )

            # Enable the save button
            self.save_button.setEnabled(True)
            self.save_action.setEnabled(True)

            self.status_bar.showMessage("Preview generated successfully")

            # Switch to the output preview tab
            self.tab_widget.setCurrentIndex(1)

        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            QMessageBox.critical(
                self, "Preview Error", f"Error generating obfuscation preview: {str(e)}"
            )
            self.status_bar.showMessage("Error generating preview")

    def _on_save_file(self):
        """Handle saving the obfuscated file."""
        if not self.processing_result:
            return

        # Get the output file path
        input_path = Path(self.pdf_path)
        default_output_path = input_path.with_stem(f"{input_path.stem}_obfuscated")

        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Obfuscated PDF", str(default_output_path), "PDF Files (*.pdf)"
        )

        if not output_path:
            return

        # Show a progress dialog
        self.status_bar.showMessage("Saving obfuscated file...")
        self.progress_bar.setValue(0)

        try:
            # Get the selected entities for obfuscation
            selected_entities = [
                entity
                for i, entity in enumerate(self.pii_entities)
                if self.entity_inclusion.get(i, True)
            ]

            # Get the obfuscator from the processing result
            obfuscator = self.processing_result["obfuscator"]
            document = self.processing_result["document"]

            # Obfuscate the document
            self.progress_bar.setValue(50)
            obfuscated_document = obfuscator.obfuscate_document(
                document, selected_entities
            )

            # Save the obfuscated document
            self.progress_bar.setValue(90)

            # TODO: Implement actual PDF saving logic
            # For now, just save the text to a file
            with open(output_path, "w") as f:
                f.write(obfuscated_document.get("full_text", ""))

            self.progress_bar.setValue(100)
            self.status_bar.showMessage(f"Saved obfuscated file to {output_path}")

            QMessageBox.information(
                self, "File Saved", f"Obfuscated file saved to:\n{output_path}"
            )

        except Exception as e:
            logger.error(f"Error saving file: {e}")
            QMessageBox.critical(
                self, "Save Error", f"Error saving obfuscated file: {str(e)}"
            )
            self.status_bar.showMessage("Error saving file")

    def _show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About PDF Bank Statement Obfuscator",
            "PDF Bank Statement Obfuscator v0.1.0\n\n"
            "A privacy-focused desktop application for removing PII from bank statements.\n\n"
            "© 2025",
        )
