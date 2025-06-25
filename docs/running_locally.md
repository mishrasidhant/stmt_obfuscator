# Running the PDF Bank Statement Obfuscator Locally

This guide provides step-by-step instructions for setting up and using the PDF Bank Statement Obfuscator application on your local machine. The application allows you to remove personally identifiable information (PII) from bank statements while preserving the financial data and document layout.

## Table of Contents

1. [Prerequisites and Environment Setup](#prerequisites-and-environment-setup)
2. [Installing Ollama and Required Models](#installing-ollama-and-required-models)
3. [Setting Up the Application](#setting-up-the-application)
4. [Running the Application](#running-the-application)
5. [Using the RAG Features](#using-the-rag-features)
6. [Testing with Your Own Documents](#testing-with-your-own-documents)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)

## Prerequisites and Environment Setup

### Required Software

- **Python**: Version 3.10 or higher (tested with Python 3.13)
- **Ollama**: For running local AI models
- **Git**: For cloning the repository

### Required Hardware

- **Operating System**: macOS (optimized for Apple Silicon M-series chips)
- **Minimum Hardware**: 
  - 16GB RAM
  - 4-core CPU (Apple M1 or equivalent)
  - 500MB free disk space for the application
  - 5GB free disk space for the Ollama model

### Installing Dependencies

Before installing the application, ensure you have Python 3.10+ installed on your system. You can check your Python version with:

```bash
# On macOS, use python3 instead of python
python3 --version
```

If you need to install or update Python, visit the [official Python website](https://www.python.org/downloads/) or use your operating system's package manager.

## Installing Ollama and Required Models

Ollama is a tool for running large language models locally. The PDF Bank Statement Obfuscator uses Ollama to process bank statements without sending data to external services.

### Installing Ollama

1. Visit the [Ollama website](https://ollama.ai) and download the installer for your operating system.
2. Follow the installation instructions for your platform.
3. After installation, verify Ollama is working by opening a terminal and running:

```bash
ollama --version
```

### Installing the Required Model

The application is configured to use the `mistral:7b-instruct` model by default, but you can use any Mistral model available in Ollama. To install the model:

1. Open a terminal window.
2. Run the following command:

```bash
# You can use either of these models
ollama pull mistral:latest
# OR
ollama pull mistral:7b-instruct
```

3. Wait for the download to complete. The model is approximately 4-5GB in size.

### Verifying Ollama Setup

To verify that Ollama is working correctly with the installed model:

1. Start the Ollama service if it's not already running:

```bash
ollama serve
```

2. In a new terminal window, test the model:

```bash
ollama run mistral:latest "Hello, how are you?"
```

You should receive a response from the model. If you encounter any issues, see the [Troubleshooting](#troubleshooting-common-issues) section.

## Setting Up the Application

### Cloning the Repository

1. Open a terminal window.
2. Clone the repository:

```bash
git clone https://github.com/yourusername/stmt_obfuscator.git
cd stmt_obfuscator
```

### Creating a Virtual Environment

It's important to create a virtual environment to avoid conflicts with system packages:

1. Create a virtual environment:

```bash
# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# On Windows
python -m venv .venv
.venv\Scripts\activate
```

2. Your terminal prompt should change to indicate that the virtual environment is active.

### Installing Python Dependencies

Install the required dependencies:

```bash
# Install the required packages
pip install pymupdf pyqt6 chromadb faker requests
```

Note: The specific versions of these packages may vary. If you encounter issues, try installing without specifying versions first.

## Running the Application

### Command-line Usage

To run the main application with the graphical user interface:

1. Ensure you're in the project directory and your virtual environment is activated.
2. Run the following command, specifying the Ollama model you have installed:

```bash
# If you have mistral:latest installed
OLLAMA_MODEL="mistral:latest" python -m stmt_obfuscator.main

# If you have mistral:7b-instruct installed
python -m stmt_obfuscator.main  # Uses the default model
```

### Running the Demo Script

The project includes a comprehensive demo script that demonstrates the complete workflow:

1. Ensure your virtual environment is activated.
2. Run the demo script, specifying the Ollama model you have installed:

```bash
# If you have mistral:latest installed
OLLAMA_MODEL="mistral:latest" python demo_bank_statement_obfuscator_fixed.py

# If you have mistral:7b-instruct installed
python demo_bank_statement_obfuscator_fixed.py  # Uses the default model
```

This script will:
- Check if Ollama is properly set up
- Generate a synthetic bank statement (or use an existing sample)
- Detect PII entities with and without RAG enhancement
- Obfuscate the detected PII
- Compare the results

You can also use the `--use-existing-sample` flag to use an existing sample instead of generating a new one:

```bash
OLLAMA_MODEL="mistral:latest" python demo_bank_statement_obfuscator_fixed.py --use-existing-sample
```

### Launching the UI

After running the main application command, the graphical user interface (GUI) will launch. The main window includes:

- A file selection area for choosing PDF bank statements
- Processing controls
- PII review and editing tools
- Preview and export options

### Basic Navigation and Workflow

1. **Select a PDF File**:
   - Click the "Select PDF" button or use File > Open PDF (Ctrl+O)
   - Navigate to your bank statement PDF file and select it

2. **Process the PDF**:
   - Click the "Process PDF" button
   - The application will begin analyzing the document
   - A progress bar will show the current processing stage

3. **Review Detected PII**:
   - After processing completes, review the detected PII entities in the table
   - Adjust confidence thresholds if needed
   - Add, edit, or remove PII entities as necessary

4. **Generate Preview**:
   - Click the "Generate Preview" button
   - The application will show the original document and the obfuscated version side by side
   - Note: There might be UI issues when highlighting PII entities in the preview

5. **Save the Obfuscated PDF**:
   - Click the "Save Obfuscated PDF" button
   - Choose a location to save the obfuscated document

## Using the RAG Features

The PDF Bank Statement Obfuscator includes Retrieval-Augmented Generation (RAG) capabilities to improve PII detection in ambiguous cases.

### Enabling/Disabling RAG

RAG is enabled by default. To enable or disable it:

1. Edit the configuration file at `~/.stmt_obfuscator/config.yaml`
2. Set the `rag.enabled` value to `true` or `false`
3. Save the file and restart the application

Alternatively, you can toggle RAG in the application's settings menu:

1. Go to Settings > Advanced Settings
2. Check or uncheck the "Enable RAG Enhancement" option
3. Click "Apply" to save the changes

### Comparing RAG Results

To observe how RAG affects PII detection:

1. Process a document with RAG enabled
2. Note the detected PII entities and their confidence scores
3. Disable RAG in the settings
4. Process the same document again
5. Compare the results

The application will store detection results in the output directory, allowing you to compare the effectiveness of RAG enhancement.

## Testing with Your Own Documents

### Supported File Formats

The PDF Bank Statement Obfuscator primarily supports:

- PDF files (.pdf)
- Text files extracted from bank statements (.txt)

### How to Prepare Test Documents

For best results when testing with your own documents:

1. **Use actual bank statements** if possible, as they contain the typical formatting and PII patterns the application is designed to detect.

2. **Ensure good quality PDFs**:
   - Text should be selectable (not scanned images)
   - Document should be properly formatted
   - File size should be under 50MB

3. **For testing purposes**, you can use the demo script to generate synthetic bank statements:

```bash
OLLAMA_MODEL="mistral:latest" python demo_bank_statement_obfuscator_fixed.py
```

This will create sample files in the `demo_output` directory.

### How to Evaluate Results

After processing your document, evaluate the results by:

1. **Reviewing the detected PII**:
   - Check if all expected PII was detected
   - Note any false positives or false negatives

2. **Examining the obfuscated output**:
   - Verify that all PII is properly masked
   - Confirm that financial data and document structure are preserved

3. **Using the demo script**:
   - Run the demo script with your document
   - Review the comparison of original and obfuscated text
   - Check the verification of PII removal

## Troubleshooting Common Issues

### Ollama Model Not Found

**Issue**: Error message: `Error communicating with Ollama: 404 Client Error: Not Found for url: http://localhost:11434/api/generate`

**Solutions**:
1. Check which models you have installed:
   ```bash
   ollama list
   ```

2. Run the application with the `OLLAMA_MODEL` environment variable set to a model you have installed:
   ```bash
   OLLAMA_MODEL="mistral:latest" python -m stmt_obfuscator.main
   ```

3. Alternatively, install the default model:
   ```bash
   ollama pull mistral:7b-instruct
   ```

### Ollama Connection Problems

**Issue**: Application shows "Ollama Connection Error" or fails to connect to Ollama.

**Solutions**:
1. Verify Ollama is running:
   ```bash
   ollama serve
   ```

2. Check if Ollama is running on the expected port (default: 11434):
   ```bash
   curl http://localhost:11434/api/version
   ```

3. If using a custom Ollama host, ensure it's correctly set in the configuration file.

4. Restart Ollama and the application.

### Python Command Not Found

**Issue**: `python: command not found` error when trying to run commands.

**Solutions**:
1. On macOS, use `python3` instead of `python`:
   ```bash
   python3 --version
   python3 -m venv .venv
   ```

2. Ensure Python is installed and in your PATH.

### UI Preview Issues

**Issue**: Errors when generating preview or highlighting PII entities, such as:
- `Error generating preview: 'int' object is not iterable`
- `AttributeError: type object 'ExtraSelection' has no attribute 'KeepAnchor'`

**Solutions**:
1. These are known issues with the UI preview functionality, but they don't affect the core PII detection and obfuscation capabilities.

2. You can still save the obfuscated document even if the preview has errors.

3. If you need to verify the obfuscation, check the saved output file directly.

4. Try using the demo script instead, which provides a text-based comparison of original and obfuscated content:
   ```bash
   OLLAMA_MODEL="mistral:latest" python demo_bank_statement_obfuscator_fixed.py --use-existing-sample
   ```

### PyQt6 Installation Issues

**Issue**: Errors related to PyQt6 when running the application.

**Solutions**:
1. Try reinstalling PyQt6:
   ```bash
   pip uninstall -y pyqt6 pyqt6-qt6 pyqt6-sip
   pip install pyqt6
   ```

2. If you're using Python 3.13, there might be compatibility issues with PyQt6. Try using Python 3.10 or 3.11 instead.

### PyMuPDF Installation Issues

**Issue**: Errors when installing PyMuPDF.

**Solutions**:
1. Install the latest version without specifying a version number:
   ```bash
   pip install pymupdf
   ```

2. If you encounter build errors, try installing the binary distribution:
   ```bash
   pip install --only-binary=pymupdf pymupdf
   ```

### Memory/Performance Issues

**Issue**: Application becomes slow or unresponsive when processing large documents.

**Solutions**:
1. Process smaller documents or split large documents into smaller chunks.

2. Close other memory-intensive applications.

3. Disable RAG for faster processing (at the cost of some accuracy).

### Application Crashes or Errors

**Issue**: Application crashes with error messages or unexpected behavior.

**Solutions**:
1. Check the log files for detailed error information:
   ```bash
   cat ~/.stmt_obfuscator/app.log
   ```

2. Reset the application configuration:
   ```bash
   mv ~/.stmt_obfuscator ~/.stmt_obfuscator_backup
   ```
   Then restart the application to create a fresh configuration.

3. Make sure all dependencies are installed correctly:
   ```bash
   pip install -U pymupdf pyqt6 chromadb faker requests
   ```

4. If the issue persists, report it with:
   - A detailed description of the problem
   - Steps to reproduce the issue
   - Relevant log file contents
   - Your system information

---

By following this guide, you should be able to set up and run the PDF Bank Statement Obfuscator locally on your machine. If you encounter any issues not covered in this guide, please refer to the project's GitHub repository for additional support and resources.