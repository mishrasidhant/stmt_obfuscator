# PDF Bank Statement Obfuscator - User Guide

This guide provides detailed instructions on how to install, set up, and use the PDF Bank Statement Obfuscator application to safely remove personally identifiable information (PII) from your bank statements.

## Table of Contents

1. [Installation](#installation)
2. [Setup](#setup)
3. [Using the Application](#using-the-application)
4. [Reviewing and Correcting PII](#reviewing-and-correcting-pii)
5. [Understanding Confidence Levels](#understanding-confidence-levels)
6. [Using PDF Export Functionality](#using-pdf-export-functionality)
7. [Customizing Application Settings](#customizing-application-settings)
8. [Troubleshooting](#troubleshooting)

## Installation

### System Requirements

- **Operating System**: macOS (optimized for Apple Silicon M-series chips)
- **Minimum Hardware**: Apple M1 Pro, 16GB RAM
- **Recommended Hardware**: M3 Pro, 32GB RAM for processing large documents (>100 pages)
- **Disk Space**: At least 500MB free space

### Installation Steps

1. **Download the Application**:
   - Download the latest release from the [releases page](https://github.com/yourusername/stmt_obfuscator/releases)
   - Choose the appropriate version for your system (macOS .dmg)

2. **Install the Application**:
   - Open the downloaded .dmg file
   - Drag the PDF Bank Statement Obfuscator icon to your Applications folder
   - Right-click the application and select "Open" (required for first launch due to security settings)

3. **Install Ollama**:
   - The application requires Ollama to run the local AI model
   - Download and install Ollama from [ollama.ai](https://ollama.ai)
   - Follow the Ollama installation instructions for your operating system

4. **Install the Required Model**:
   - Open Terminal
   - Run the following command to download the Mistral 7B model:
     ```bash
     ollama pull mistral:7b-instruct
     ```
   - Wait for the model to download (approximately 4-5GB)

## Setup

### First Launch

1. **Launch the Application**:
   - Open the PDF Bank Statement Obfuscator from your Applications folder
   - The application will create a configuration directory at `~/.stmt_obfuscator`

2. **Verify Ollama Connection**:
   - The application will automatically attempt to connect to Ollama
   - If successful, you'll see "Ollama Connected" in the status bar
   - If unsuccessful, ensure Ollama is running by opening Terminal and running:
     ```bash
     ollama serve
     ```

### Configuration

The application uses a default configuration that works well for most users. However, you can customize settings by editing the configuration file:

- Configuration file location: `~/.stmt_obfuscator/config.yaml`
- You can modify this file with a text editor to change settings (see [Customizing Application Settings](#customizing-application-settings))

## Using the Application

### Processing a Bank Statement

1. **Select a PDF File**:
   - Click the "Select PDF" button or use File > Open PDF (Ctrl+O)
   - Navigate to your bank statement PDF file and select it
   - The file path will appear in the input file field

2. **Process the PDF**:
   - Click the "Process PDF" button
   - The application will begin analyzing the document
   - A progress bar will show the current processing stage
   - Processing time varies based on document size and complexity (typically 10-30 seconds per page)

3. **Review Detected PII**:
   - After processing completes, the application will display the PII Review tab
   - Review the detected PII entities in the table (see [Reviewing and Correcting PII](#reviewing-and-correcting-pii))

4. **Generate Preview**:
   - After reviewing and adjusting PII entities, click the "Generate Preview" button
   - The application will switch to the Output Preview tab
   - You'll see the original document on the left and the obfuscated version on the right

5. **Save the Obfuscated Document**:
   - Click the "Save Obfuscated Document" button or use File > Save Obfuscated Document (Ctrl+S)
   - Select the desired format (Text or PDF) from the dropdown menu
   - Configure PDF export options if PDF format is selected
   - Choose a location to save the obfuscated document
   - The application will create a new document with all selected PII entities obfuscated

### Workflow Example

Here's a typical workflow for processing a bank statement:

1. Open the application
2. Select your bank statement PDF
3. Click "Process PDF" and wait for processing to complete
4. Review the detected PII entities, adjusting as needed
5. Click "Generate Preview" to see how the obfuscated document will look
6. Click "Save Obfuscated PDF" to save the final document
7. Verify the saved document to ensure all sensitive information is properly obfuscated

## Reviewing and Correcting PII

The PII Review tab allows you to examine and modify the detected PII entities before obfuscation.

### Understanding the PII Table

The PII table displays all detected PII entities with the following information:

- **Type**: The category of PII (e.g., PERSON_NAME, ACCOUNT_NUMBER)
- **Text**: The actual text identified as PII
- **Confidence**: The AI's confidence level in this detection (0.00-1.00)
- **Actions**: Buttons to edit or delete the entity
- **Include**: Checkbox to include/exclude this entity from obfuscation

### Color Coding

Entities are color-coded based on confidence level:
- **Green**: High confidence (≥0.90)
- **Yellow**: Medium confidence (0.70-0.89)
- **Red**: Low confidence (<0.70)

### Adjusting the Confidence Threshold

You can filter the displayed entities by adjusting the confidence threshold:

1. Use the "Confidence Threshold" spinner at the top of the PII table
2. Entities with confidence below the threshold will be hidden
3. The document preview will update to show only the visible entities

### Adding a New PII Entity

If the AI missed a PII entity, you can add it manually:

1. Click the "Add Entity" button
2. In the dialog that appears:
   - Select the entity type from the dropdown
   - Enter the exact text to be obfuscated
   - Set the confidence level
3. Click "OK" to add the entity

### Editing an Existing PII Entity

To modify a detected entity:

1. Click the "Edit" button in the Actions column for that entity
2. In the dialog that appears:
   - Modify the entity type, text, or confidence as needed
3. Click "OK" to save your changes

### Deleting a PII Entity

To remove an incorrectly detected entity:

1. Click the "Delete" button in the Actions column for that entity
2. Confirm the deletion when prompted

### Including/Excluding Entities

You can choose which entities to include in the obfuscation:

1. Use the checkbox in the "Include" column to toggle inclusion
2. Unchecked entities will remain visible in the document preview but will not be obfuscated in the final output

### Document Preview

The document preview shows the original text with highlighted PII entities:

- Entities are highlighted with the same color coding as the table
- Clicking on an entity in the table will scroll the preview to that entity
- The preview updates automatically when you change the confidence threshold or toggle entity inclusion

## Understanding Confidence Levels

The application uses AI to detect PII with varying levels of confidence. Understanding these confidence levels helps you make better decisions about what to obfuscate.

### Confidence Scale

- **0.90-1.00 (High)**: The AI is very confident this is PII. These detections are rarely incorrect.
- **0.70-0.89 (Medium)**: The AI is moderately confident. These may require review.
- **0.00-0.69 (Low)**: The AI is uncertain. These often require manual verification.

### Recommended Approach

1. **Start with high confidence**: Begin by reviewing entities with high confidence (≥0.90)
2. **Review medium confidence**: Carefully check entities with medium confidence (0.70-0.89)
3. **Be cautious with low confidence**: Thoroughly verify entities with low confidence (<0.70)

### Factors Affecting Confidence

Several factors influence the AI's confidence in PII detection:

- **Context**: Text surrounded by typical banking terms is more likely to be correctly identified
- **Format**: Text matching common PII patterns (e.g., XXX-XX-XXXX for SSNs) receives higher confidence
- **Ambiguity**: Text that could have multiple interpretations receives lower confidence
- **Document Quality**: Poor quality scans or unusual formatting can reduce confidence

## Using PDF Export Functionality

The PDF Bank Statement Obfuscator provides robust PDF export capabilities that allow you to generate professionally formatted obfuscated bank statements while preserving the original document's layout.

### PDF Export Options

When saving an obfuscated document, you can select "PDF" from the format dropdown menu to access the following PDF export options:

1. **Layout Preservation**:
   - **Enable Layout Preservation**: When checked, the application will attempt to preserve the original document's layout, including columns, spacing, and positioning of elements.
   - **Layout Detail Level**: Choose between Low, Medium, or High detail levels. Higher detail levels provide more accurate layout preservation but may require more processing time.

2. **Font Settings**:
   - **Font Family**: Select the primary font to use in the PDF. Default is Helvetica.
   - **Font Size**: Set the base font size for the document. Default is 11pt.
   - **Enable Font Fallbacks**: When checked, the application will automatically use alternative fonts for characters not supported by the primary font.

3. **Page Settings**:
   - **Margins**: Set the page margins in points (1/72 inch). Default is 72pt (1 inch).
   - **Include Page Numbers**: When checked, page numbers will be added to the document.
   - **Include Timestamps**: When checked, a timestamp will be added to the document header.
   - **Include Metadata**: When checked, metadata about the obfuscation process will be included in the document.

### PDF Export Workflow

To export an obfuscated document as a PDF:

1. Process your bank statement as normal
2. Review and edit the detected PII entities
3. Click the "Generate Preview" button to see how the obfuscated document will look
4. Click the "Save Obfuscated Document" button
5. Select "PDF" from the format dropdown menu
6. Configure the PDF export options as desired
7. Click "Save" to generate the PDF

### PDF Preview

The application provides an accurate preview of how the final PDF will look:

1. **Preview Modes**:
   - **Text Mode**: Shows a simple text representation of the document
   - **PDF Mode**: Shows an exact preview of how the PDF will look

2. **Preview Quality**:
   - **Low**: Faster rendering but lower image quality
   - **Medium**: Balanced performance and quality
   - **High**: Highest quality but slower rendering

3. **Navigation**:
   - Use the page navigation controls to move between pages in multi-page documents
   - Use the zoom controls to adjust the preview size

### Key PDF Export Features

1. **Advanced Layout Preservation**:
   - Preserves the original document's layout, including columns, spacing, and positioning of elements
   - Maintains text alignment (left, center, right)
   - Identifies and properly positions headers and footers
   - Falls back to standard formatting when layout preservation is not possible

2. **Intelligent Text Wrapping**:
   - Automatically wraps text within page margins
   - Handles long words by splitting them across lines when necessary
   - Preserves paragraph breaks with consistent spacing

3. **Font Fallback System**:
   - Automatically selects appropriate fonts for different character sets
   - Ensures special characters and symbols are properly displayed
   - Provides consistent rendering across different systems

### Tips for Best Results

1. **For Complex Layouts**:
   - Use the "High" layout detail level for documents with complex formatting
   - Enable font fallbacks to ensure all characters are properly displayed

2. **For Large Documents**:
   - Use the "Low" or "Medium" layout detail level to improve performance
   - Consider disabling metadata inclusion to reduce file size

3. **For Official Documents**:
   - Use a professional font like Times-Roman or Helvetica
   - Enable page numbers and timestamps for better document tracking
   - Consider adjusting margins to match the original document

## Customizing Application Settings

The application can be customized by editing the configuration file at `~/.stmt_obfuscator/config.yaml`.

### Available Settings

```yaml
# AI Model Settings
model:
  name: "mistral:7b-instruct"  # The Ollama model to use
  fallback: "llama3:8b"        # Fallback model if primary unavailable
  confidence_threshold: 0.70   # Default confidence threshold

# RAG Settings
rag:
  enabled: true                # Enable/disable RAG context enhancement
  similarity_threshold: 0.75   # Threshold for RAG activation

# Obfuscation Settings
obfuscation:
  person_name_pattern: "XXXX XXX"  # Pattern for person names
  account_number_pattern: "XXXX-XXXX-XXXX-XXXX"  # Pattern for account numbers
  preserve_first_last: false  # Preserve first/last digits of numbers

# UI Settings
ui:
  default_confidence: 0.70     # Default confidence threshold in UI
  theme: "system"              # UI theme (system, light, dark)

# Logging Settings
logging:
  level: "INFO"                # Logging level (DEBUG, INFO, WARNING, ERROR)
  retain_days: 7               # Number of days to keep logs
```

### Editing the Configuration

1. Close the application
2. Open `~/.stmt_obfuscator/config.yaml` in a text editor
3. Modify the settings as needed
4. Save the file
5. Restart the application for changes to take effect

### Recommended Customizations

- **For maximum privacy**: Lower the `confidence_threshold` to 0.50 to catch more potential PII
- **For faster processing**: Set `rag.enabled` to false (reduces accuracy but improves speed)
- **For better number obfuscation**: Set `obfuscation.preserve_first_last` to true to keep first/last digits

## Troubleshooting

This section provides solutions to common issues you might encounter when using the PDF Bank Statement Obfuscator.

### Common Issues

#### Application Won't Start

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Application crashes on startup | • Ollama not installed<br>• Ollama not running<br>• Insufficient system resources | • Verify Ollama is installed by running `ollama list` in Terminal<br>• Start Ollama with `ollama serve`<br>• Ensure you meet minimum system requirements |
| "Model not found" error | • Required model not downloaded | • Run `ollama pull mistral:7b-instruct` in Terminal |
| Permission denied error | • Insufficient permissions | • Right-click the app and select "Open" for first launch<br>• Check file permissions in the application directory |
| Blank or frozen screen | • GUI initialization issue | • Check the log file at `~/.stmt_obfuscator/app.log`<br>• Restart your computer and try again |

#### Processing Fails

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| "Failed to process PDF" error | • PDF is password-protected<br>• PDF is corrupted<br>• Unsupported PDF format | • Remove password protection from the PDF<br>• Try repairing the PDF with another tool<br>• Convert the PDF to a standard format |
| Processing hangs or times out | • PDF is too large<br>• System resources exhausted | • Try processing a smaller section of the PDF<br>• Close other resource-intensive applications<br>• Increase the timeout in config.yaml |
| "Ollama connection error" | • Ollama service stopped<br>• Network configuration issue | • Restart Ollama with `ollama serve`<br>• Check if another service is using port 11434<br>• Verify firewall settings |
| "Memory error" | • PDF too complex for available RAM | • Close other applications<br>• Process a smaller PDF<br>• Upgrade your system RAM |

#### PII Detection Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Too many false positives | • Confidence threshold too low<br>• Unusual formatting in PDF | • Increase confidence threshold (try 0.85 or higher)<br>• Manually deselect incorrect entities |
| Missing PII | • Confidence threshold too high<br>• Unusual PII format | • Decrease confidence threshold (try 0.65)<br>• Use "Add Entity" button to manually add missed PII<br>• Enable RAG enhancement in settings |
| Incorrect entity boundaries | • Complex PDF layout<br>• Mixed formatting | • Use the Edit function to adjust entity boundaries<br>• Try regenerating with different confidence settings |
| Inconsistent detection | • Varying context in document | • Process the document in smaller chunks<br>• Add examples to the RAG knowledge base |

#### Obfuscation Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Garbled text in output | • Font compatibility issues<br>• Complex layout | • Try a different obfuscation pattern<br>• Use the "Preserve Layout" option in settings |
| Missing obfuscation | • Entities not included<br>• Processing error | • Verify entities are checked in the "Include" column<br>• Regenerate the preview and check again |
| Disrupted layout | • Complex PDF structure | • Try the "Conservative Layout" option in settings<br>• Process tables separately from regular text |
| Partial obfuscation | • Entity boundary detection issue | • Edit the entity to include the full text<br>• Try using regex patterns for consistent entities |

#### Performance Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Slow processing | • Large PDF<br>• Complex layout<br>• Limited system resources | • Process smaller batches of pages<br>• Disable RAG for faster processing<br>• Close other applications |
| High memory usage | • Large document in memory | • Process the document in smaller chunks<br>• Adjust memory settings in config.yaml |
| Application becomes unresponsive | • Processing thread blocking UI | • Wait for processing to complete<br>• Check Task Manager/Activity Monitor<br>• Restart the application |

### Advanced Troubleshooting

#### Checking Log Files

The application maintains detailed logs that can help diagnose issues:

1. Main application log: `~/.stmt_obfuscator/app.log`
2. Ollama interaction log: `~/.stmt_obfuscator/ollama.log`
3. PDF processing log: `~/.stmt_obfuscator/pdf_processing.log`

To view these logs:

```bash
cat ~/.stmt_obfuscator/app.log
```

Look for lines marked `[ERROR]` or `[WARNING]` for potential issues.

#### Resetting the Application

If you encounter persistent issues, you can reset the application to its default state:

1. Close the application
2. Rename or delete the configuration directory:
   ```bash
   mv ~/.stmt_obfuscator ~/.stmt_obfuscator_backup
   ```
3. Restart the application (it will create a new configuration directory)

#### Debugging Mode

For advanced users, you can enable debugging mode:

1. Edit `~/.stmt_obfuscator/config.yaml`
2. Set `logging.level` to `"DEBUG"`
3. Restart the application
4. Check the log files for detailed information

### Getting Help

If you encounter issues not covered in this guide:

1. Check the log files as described above
2. Refer to the [troubleshooting guide](troubleshooting.md) for more detailed solutions
3. Search for similar issues in the [GitHub repository](https://github.com/yourusername/stmt_obfuscator/issues)
4. Submit a new issue with:
   - A detailed description of the problem
   - Steps to reproduce the issue
   - Relevant log file contents
   - Your system information
