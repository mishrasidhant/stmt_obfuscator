# PDF Bank Statement Obfuscator

A privacy-focused desktop application designed to process bank statements while removing personally identifiable information (PII) with surgical precision.

## The Problem

Financial professionals, auditors, and individuals often need to share bank statements for various purposes, but these documents contain sensitive personal information. Manual redaction is time-consuming and error-prone, while generic redaction tools often remove too much information or miss critical PII.

## The Solution

The PDF Bank Statement Obfuscator uses AI-powered detection to identify and remove PII from bank statements while preserving the financial data and document layout. It operates completely offline, ensuring your sensitive documents never leave your computer.

## Key Features

- **Complete Offline Processing**: Zero external API dependencies for maximum privacy
- **AI-Powered Anonymization**: Leverages Mistral 7B via Ollama for context-aware PII detection
- **Transaction Integrity**: Preserves all financial data with 100% accuracy
- **Hardware Optimized**: Designed for Apple Silicon (M-series chips) for fast processing
- **Configurable Architecture**: Supports model swapping for future enhancements
- **User-Friendly Interface**: Simple workflow with preview and verification capabilities
- **Pattern-Preserving Masking**: Maintains format while obfuscating sensitive data
- **RAG Enhancement**: Uses retrieval-augmented generation for ambiguous cases

## Getting Started

### Installation

1. Download the latest release from the [releases page](https://github.com/yourusername/stmt_obfuscator/releases)
2. Install [Ollama](https://ollama.ai/) and download the Mistral 7B model
3. Run the application and select a PDF bank statement to process

For detailed installation instructions, see the [Setup Guide](docs/setup_guide.md).

### Usage Examples

**Basic Usage:**
1. Launch the application
2. Click "Select PDF" and choose your bank statement
3. Click "Process PDF" to detect PII
4. Review and adjust detected PII entities
5. Click "Generate Preview" to see the obfuscated result
6. Save the anonymized statement

**Advanced Usage:**
- Adjust confidence thresholds for more or less aggressive PII detection
- Manually add missed PII entities
- Configure custom obfuscation patterns
- Process batches of statements

For more detailed usage instructions, see the [User Guide](docs/user_guide.md).

## Project Status

This project has completed all planned development phases. The following components have been implemented:

- ✅ Project setup and environment configuration
- ✅ PDF parsing module with layout preservation
- ✅ Enhanced PII detection module design
- ✅ RAG module design for ambiguous cases
- ✅ Obfuscation module with pattern-preserving masking
- ✅ User interface with PII review capabilities
- ✅ Comprehensive testing framework

For detailed documentation on completed subtasks, see the [subtask documentation](docs/subtasks/README.md).

## Architecture Overview

The application follows a modular pipeline architecture with seven core components:

```
stmt_obfuscator/
├── ui/                  # User interface components
├── pdf_parser/          # PDF parsing and text extraction
├── pii_detection/       # PII detection using Ollama
├── rag/                 # RAG context enhancement
├── pii_management/      # PII entity management
├── obfuscation/         # PDF obfuscation
└── output_generator/    # Output generation
```

For a more detailed architecture description, see the [Architecture Document](architecture_document.md).

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works (`pytest`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure your code follows our [docstring style guide](.docstring_style.md) and passes all tests.

## Documentation

- [User Guide](docs/user_guide.md) - Comprehensive guide for installing and using the application
- [Architecture Document](architecture_document.md) - Detailed technical architecture
- [Project Status](docs/project_status.md) - Current status of all project components
- [RAG Implementation](docs/rag_implementation.md) - Details on the RAG context enhancement module
- [Subtask Documentation](docs/subtasks/README.md) - Detailed documentation for all completed subtasks
- [Setup Guide](docs/setup_guide.md) - Detailed setup instructions
- [Troubleshooting](docs/troubleshooting.md) - Solutions to common issues

## Development Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) with Mistral 7B model installed
- Poetry (for dependency management)

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stmt_obfuscator.git
   cd stmt_obfuscator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install Poetry:
   ```bash
   pip install poetry
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
pytest
```

### Running the Application

```bash
python -m stmt_obfuscator.main
```

### Generating Documentation

To generate the documentation using Sphinx:

```bash
cd docs
make html
```

Then open `docs/_build/html/index.html` in your browser to view the documentation.

## License

[MIT License](LICENSE)
