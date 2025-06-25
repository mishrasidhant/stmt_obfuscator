# PDF Bank Statement Obfuscator - User Guide

This guide provides detailed instructions on how to install, set up, and use the PDF Bank Statement Obfuscator application to safely remove personally identifiable information (PII) from your bank statements.

## Table of Contents

1. [Installation](#installation)
2. [Setup](#setup)
3. [Using the Application](#using-the-application)
4. [Reviewing and Correcting PII](#reviewing-and-correcting-pii)
5. [Understanding Confidence Levels](#understanding-confidence-levels)
6. [Customizing Application Settings](#customizing-application-settings)
7. [Troubleshooting](#troubleshooting)

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

5. **Save the Obfuscated PDF**:
   - Click the "Save Obfuscated PDF" button or use File > Save Obfuscated PDF (Ctrl+S)
   - Choose a location to save the obfuscated document
   - The application will create a new PDF with all selected PII entities obfuscated

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

### Common Issues

#### Application Won't Start

- Ensure Ollama is installed and running
- Check system requirements
- Verify you have sufficient disk space
- Look for error messages in the log file at `~/.stmt_obfuscator/app.log`

#### Processing Fails

- Ensure the PDF is not password-protected
- Check if the PDF is corrupted or has unusual formatting
- Verify Ollama is running and the model is properly installed
- Try with a smaller or simpler PDF first

#### PII Detection Issues

- If too many false positives: Increase the confidence threshold
- If missing PII: Decrease the confidence threshold and manually add missed entities
- For unusual bank statements: You may need to add more entities manually

#### Obfuscation Problems

- If the obfuscated PDF looks incorrect: Try regenerating the preview
- If specific entities aren't being obfuscated: Verify they're checked in the "Include" column
- If the layout is disrupted: This can happen with complex PDFs; try adjusting entity boundaries

### Getting Help

If you encounter issues not covered in this guide:

1. Check the log file at `~/.stmt_obfuscator/app.log`
2. Refer to the [troubleshooting guide](troubleshooting.md) for more detailed solutions
3. Submit an issue on the [GitHub repository](https://github.com/yourusername/stmt_obfuscator/issues)
