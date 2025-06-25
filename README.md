# PDF Bank Statement Obfuscator

A privacy-focused desktop application designed to process bank statements while removing personally identifiable information (PII) with surgical precision.

## Features

- **Complete Offline Processing**: Zero external API dependencies
- **AI-Powered Anonymization**: Leverages Mistral 7B via Ollama for context-aware PII detection
- **Transaction Integrity**: Preserves all financial data with 100% accuracy
- **Hardware Optimized**: Designed for Apple Silicon (M-series chips)
- **Configurable Architecture**: Supports model swapping for future enhancements

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

## Project Structure

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

## Documentation

- [User Guide](docs/user_guide.md) - Comprehensive guide for installing and using the application
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

## License

[MIT License](LICENSE)
