# PDF Bank Statement Obfuscator

A privacy-focused desktop application designed to process bank statements while removing personally identifiable information (PII) with surgical precision.

## Features

- **Complete Offline Processing**: Zero external API dependencies
- **AI-Powered Anonymization**: Leverages Mistral 7B via Ollama for context-aware PII detection
- **Transaction Integrity**: Preserves all financial data with 100% accuracy
- **Hardware Optimized**: Designed for Apple Silicon (M-series chips)
- **Configurable Architecture**: Supports model swapping for future enhancements

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