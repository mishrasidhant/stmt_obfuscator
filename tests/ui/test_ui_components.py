"""
UI tests for the PDF Bank Statement Obfuscator.

These tests verify that the UI components work correctly.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtTest import QTest

from stmt_obfuscator.ui.main_window import MainWindow, PIIEntityDialog


# Skip all tests if PyQt is not available
pytestmark = pytest.mark.skipif(
    "PyQt6.QtWidgets" not in sys.modules,
    reason="PyQt6 is not installed"
)


@pytest.fixture
def app():
    """Create a QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(app):
    """Create a MainWindow instance for testing."""
    window = MainWindow()
    yield window
    window.close()


@pytest.fixture
def mock_pdf_path(temp_test_dir):
    """Create a mock PDF file for testing."""
    pdf_path = os.path.join(temp_test_dir, "test.pdf")
    with open(pdf_path, "w") as f:
        f.write("Mock PDF content")
    return pdf_path


class TestMainWindowUI:
    """Tests for the MainWindow UI."""

    def test_window_initialization(self, main_window):
        """Test that the main window initializes correctly."""
        assert main_window is not None
        assert main_window.windowTitle() == "PDF Bank Statement Obfuscator"
        assert main_window.isVisible() is False  # Window is not shown yet
        
        # Check that the UI components are initialized
        assert main_window.file_path_label is not None
        assert main_window.progress_bar is not None
        assert main_window.tab_widget is not None
        assert main_window.process_button is not None
        assert main_window.save_button is not None
        
        # Check initial state
        assert main_window.pdf_path is None
        assert main_window.processing_worker is None
        assert main_window.processing_result is None
        assert main_window.pii_entities == []
        assert main_window.document_text == ""
        assert main_window.entity_inclusion == {}
        
        # Check that the tabs are disabled initially
        assert main_window.tab_widget.isEnabled() is False
        
        # Check that the process button is disabled initially
        assert main_window.process_button.isEnabled() is False
        
        # Check that the save button is disabled initially
        assert main_window.save_button.isEnabled() is False
    
    @patch.object(QFileDialog, 'getOpenFileName')
    def test_file_selection(self, mock_get_open_file_name, main_window, mock_pdf_path):
        """Test file selection functionality."""
        # Mock the file dialog to return our mock PDF path
        mock_get_open_file_name.return_value = (mock_pdf_path, "PDF Files (*.pdf)")
        
        # Call the file selection method
        main_window._on_select_file()
        
        # Check that the file path was set correctly
        assert main_window.pdf_path == mock_pdf_path
        assert main_window.file_path_label.text() == str(mock_pdf_path)
        
        # Check that the process button is enabled
        assert main_window.process_button.isEnabled() is True
        
        # Check that the progress bar was reset
        assert main_window.progress_bar.value() == 0
        
        # Check that the tabs are still disabled
        assert main_window.tab_widget.isEnabled() is False
        
        # Check that the save button is still disabled
        assert main_window.save_button.isEnabled() is False
    
    @patch.object(QFileDialog, 'getOpenFileName')
    def test_file_selection_cancelled(self, mock_get_open_file_name, main_window):
        """Test file selection when cancelled."""
        # Mock the file dialog to return an empty path (cancelled)
        mock_get_open_file_name.return_value = ("", "")
        
        # Call the file selection method
        main_window._on_select_file()
        
        # Check that the file path was not set
        assert main_window.pdf_path is None
        assert main_window.file_path_label.text() == "No file selected"
        
        # Check that the process button is still disabled
        assert main_window.process_button.isEnabled() is False
    
    @patch.object(MainWindow, '_processing_finished')
    def test_process_file(self, mock_processing_finished, main_window, mock_pdf_path):
        """Test file processing functionality."""
        # Set up the main window with a mock PDF path
        main_window.pdf_path = mock_pdf_path
        main_window.process_button.setEnabled(True)
        
        # Create a mock result
        mock_result = {
            "document": {
                "full_text": "Test document text"
            },
            "pii_entities": [
                {
                    "type": "PERSON_NAME",
                    "text": "John Doe",
                    "start": 0,
                    "end": 8,
                    "confidence": 0.95
                }
            ],
            "parser": MagicMock(),
            "detector": MagicMock(),
            "obfuscator": MagicMock()
        }
        
        # Call the process file method
        main_window._on_process_file()
        
        # Check that the process button is disabled during processing
        assert main_window.process_button.isEnabled() is False
        
        # Check that the progress bar was reset
        assert main_window.progress_bar.value() == 0
        
        # Check that the worker was created
        assert main_window.processing_worker is not None
        
        # Simulate worker completion
        main_window.processing_worker.signals.finished.emit(mock_result)
        
        # Check that the processing_finished method was called
        mock_processing_finished.assert_called_once_with(mock_result)
    
    def test_processing_finished(self, main_window):
        """Test processing completion handling."""
        # Create a mock result
        mock_result = {
            "document": {
                "full_text": "Test document text"
            },
            "pii_entities": [
                {
                    "type": "PERSON_NAME",
                    "text": "John Doe",
                    "start": 0,
                    "end": 8,
                    "confidence": 0.95
                }
            ],
            "parser": MagicMock(),
            "detector": MagicMock(),
            "obfuscator": MagicMock()
        }
        
        # Call the processing finished method
        main_window._processing_finished(mock_result)
        
        # Check that the result was stored
        assert main_window.processing_result == mock_result
        assert main_window.document_text == "Test document text"
        assert main_window.pii_entities == mock_result["pii_entities"]
        
        # Check that the entity inclusion map was initialized
        assert main_window.entity_inclusion == {0: True}
        
        # Check that the UI was updated
        assert main_window.process_button.isEnabled() is True
        assert main_window.tab_widget.isEnabled() is True
        assert main_window.preview_button.isEnabled() is True
        
        # Check that the PII table was populated
        assert main_window.pii_table.rowCount() > 0
    
    @patch.object(QFileDialog, 'getSaveFileName')
    def test_save_file(self, mock_get_save_file_name, main_window, mock_pdf_path, temp_test_dir):
        """Test file saving functionality."""
        # Set up the main window with mock data
        main_window.pdf_path = mock_pdf_path
        
        # Create a mock result
        mock_result = {
            "document": {
                "full_text": "Test document text"
            },
            "pii_entities": [
                {
                    "type": "PERSON_NAME",
                    "text": "John Doe",
                    "start": 0,
                    "end": 8,
                    "confidence": 0.95
                }
            ],
            "parser": MagicMock(),
            "detector": MagicMock(),
            "obfuscator": MagicMock()
        }
        
        # Mock the obfuscator to return a simple obfuscated document
        mock_obfuscator = MagicMock()
        mock_obfuscator.obfuscate_document.return_value = {
            "full_text": "Obfuscated text"
        }
        mock_result["obfuscator"] = mock_obfuscator
        
        main_window.processing_result = mock_result
        main_window.pii_entities = mock_result["pii_entities"]
        main_window.entity_inclusion = {0: True}
        
        # Mock the file dialog to return a save path
        output_path = os.path.join(temp_test_dir, "obfuscated.pdf")
        mock_get_save_file_name.return_value = (output_path, "PDF Files (*.pdf)")
        
        # Mock the message box to avoid showing it
        with patch.object(QMessageBox, 'information') as mock_info:
            # Call the save file method
            main_window._on_save_file()
            
            # Check that the obfuscator was called
            mock_obfuscator.obfuscate_document.assert_called_once()
            
            # Check that the file was saved
            assert os.path.exists(output_path)
            
            # Check that the message box was shown
            mock_info.assert_called_once()
    
    @patch.object(QFileDialog, 'getSaveFileName')
    def test_save_file_cancelled(self, mock_get_save_file_name, main_window):
        """Test file saving when cancelled."""
        # Set up the main window with mock data
        main_window.processing_result = {
            "document": {
                "full_text": "Test document text"
            },
            "pii_entities": [],
            "parser": MagicMock(),
            "detector": MagicMock(),
            "obfuscator": MagicMock()
        }
        
        # Mock the file dialog to return an empty path (cancelled)
        mock_get_save_file_name.return_value = ("", "")
        
        # Call the save file method
        main_window._on_save_file()
        
        # Check that the obfuscator was not called
        main_window.processing_result["obfuscator"].obfuscate_document.assert_not_called()
    
    def test_pii_table_population(self, main_window):
        """Test PII table population."""
        # Create mock entities
        mock_entities = [
            {
                "type": "PERSON_NAME",
                "text": "John Doe",
                "start": 0,
                "end": 8,
                "confidence": 0.95
            },
            {
                "type": "ADDRESS",
                "text": "123 Main St",
                "start": 10,
                "end": 22,
                "confidence": 0.85
            },
            {
                "type": "PHONE_NUMBER",
                "text": "555-1234",
                "start": 30,
                "end": 38,
                "confidence": 0.75
            }
        ]
        
        # Set up the main window with mock entities
        main_window.pii_entities = mock_entities
        main_window.entity_inclusion = {i: True for i in range(len(mock_entities))}
        
        # Call the populate table method
        main_window._populate_pii_table()
        
        # Check that the table was populated correctly
        assert main_window.pii_table.rowCount() == 3
        
        # Check the first row
        assert main_window.pii_table.item(0, 0).text() == "PERSON_NAME"
        assert main_window.pii_table.item(0, 1).text() == "John Doe"
        assert main_window.pii_table.item(0, 2).text() == "0.95"
        
        # Check the second row
        assert main_window.pii_table.item(1, 0).text() == "ADDRESS"
        assert main_window.pii_table.item(1, 1).text() == "123 Main St"
        assert main_window.pii_table.item(1, 2).text() == "0.85"
        
        # Check the third row
        assert main_window.pii_table.item(2, 0).text() == "PHONE_NUMBER"
        assert main_window.pii_table.item(2, 1).text() == "555-1234"
        assert main_window.pii_table.item(2, 2).text() == "0.75"
    
    def test_confidence_threshold_filtering(self, main_window):
        """Test filtering entities by confidence threshold."""
        # Create mock entities with different confidence levels
        mock_entities = [
            {
                "type": "PERSON_NAME",
                "text": "John Doe",
                "start": 0,
                "end": 8,
                "confidence": 0.95
            },
            {
                "type": "ADDRESS",
                "text": "123 Main St",
                "start": 10,
                "end": 22,
                "confidence": 0.85
            },
            {
                "type": "PHONE_NUMBER",
                "text": "555-1234",
                "start": 30,
                "end": 38,
                "confidence": 0.75
            },
            {
                "type": "EMAIL",
                "text": "john@example.com",
                "start": 40,
                "end": 56,
                "confidence": 0.65
            }
        ]
        
        # Set up the main window with mock entities
        main_window.pii_entities = mock_entities
        main_window.entity_inclusion = {i: True for i in range(len(mock_entities))}
        
        # Set the confidence threshold to 90%
        main_window.confidence_threshold.setValue(90)
        
        # Call the populate table method
        main_window._populate_pii_table()
        
        # Check that only entities with confidence >= 90% are shown
        assert main_window.pii_table.rowCount() == 1
        assert main_window.pii_table.item(0, 0).text() == "PERSON_NAME"
        
        # Set the confidence threshold to 80%
        main_window.confidence_threshold.setValue(80)
        
        # Call the populate table method
        main_window._populate_pii_table()
        
        # Check that only entities with confidence >= 80% are shown
        assert main_window.pii_table.rowCount() == 2
        assert main_window.pii_table.item(0, 0).text() == "PERSON_NAME"
        assert main_window.pii_table.item(1, 0).text() == "ADDRESS"
        
        # Set the confidence threshold to 70%
        main_window.confidence_threshold.setValue(70)
        
        # Call the populate table method
        main_window._populate_pii_table()
        
        # Check that only entities with confidence >= 70% are shown
        assert main_window.pii_table.rowCount() == 3
        
        # Set the confidence threshold to 60%
        main_window.confidence_threshold.setValue(60)
        
        # Call the populate table method
        main_window._populate_pii_table()
        
        # Check that all entities are shown
        assert main_window.pii_table.rowCount() == 4


class TestPIIEntityDialog:
    """Tests for the PIIEntityDialog."""
    
    @pytest.fixture
    def entity_dialog(self, app):
        """Create a PIIEntityDialog instance for testing."""
        dialog = PIIEntityDialog()
        yield dialog
        dialog.close()
    
    def test_dialog_initialization(self, entity_dialog):
        """Test that the dialog initializes correctly."""
        assert entity_dialog is not None
        assert entity_dialog.windowTitle() == "Add PII Entity"
        
        # Check that the UI components are initialized
        assert entity_dialog.type_combo is not None
        assert entity_dialog.text_edit is not None
        assert entity_dialog.confidence_spin is not None
        
        # Check initial state
        assert entity_dialog.entity is None
        assert entity_dialog.full_text == ""
        
        # Check default values
        assert entity_dialog.confidence_spin.value() == 90  # Default 90%
    
    def test_dialog_with_entity(self, app):
        """Test dialog initialization with an existing entity."""
        # Create a mock entity
        mock_entity = {
            "type": "PERSON_NAME",
            "text": "John Doe",
            "confidence": 0.85,
            "start": 0,
            "end": 8
        }
        
        # Create the dialog with the mock entity
        dialog = PIIEntityDialog(entity=mock_entity)
        
        # Check that the entity was set correctly
        assert dialog.entity == mock_entity
        assert dialog.windowTitle() == "Edit PII Entity"
        
        # Check that the UI components were initialized with the entity values
        assert dialog.type_combo.currentText() == "PERSON_NAME"
        assert dialog.text_edit.text() == "John Doe"
        assert dialog.confidence_spin.value() == 85  # 85%
        
        dialog.close()
    
    def test_get_entity(self, entity_dialog):
        """Test getting the entity from the dialog."""
        # Set values in the dialog
        entity_dialog.type_combo.setCurrentText("EMAIL")
        entity_dialog.text_edit.setText("john@example.com")
        entity_dialog.confidence_spin.setValue(75)
        
        # Get the entity
        entity = entity_dialog.get_entity()
        
        # Check that the entity was created correctly
        assert entity["type"] == "EMAIL"
        assert entity["text"] == "john@example.com"
        assert entity["confidence"] == 0.75
    
    def test_get_entity_with_existing(self, app):
        """Test getting the entity from the dialog with an existing entity."""
        # Create a mock entity with additional fields
        mock_entity = {
            "type": "PERSON_NAME",
            "text": "John Doe",
            "confidence": 0.85,
            "start": 0,
            "end": 8,
            "custom_field": "custom value"
        }
        
        # Create the dialog with the mock entity
        dialog = PIIEntityDialog(entity=mock_entity)
        
        # Modify some values
        dialog.type_combo.setCurrentText("EMAIL")
        dialog.text_edit.setText("john@example.com")
        dialog.confidence_spin.setValue(75)
        
        # Get the entity
        entity = dialog.get_entity()
        
        # Check that the entity was updated correctly
        assert entity["type"] == "EMAIL"
        assert entity["text"] == "john@example.com"
        assert entity["confidence"] == 0.75
        
        # Check that the additional fields were preserved
        assert entity["start"] == 0
        assert entity["end"] == 8
        assert entity["custom_field"] == "custom value"
        
        dialog.close()