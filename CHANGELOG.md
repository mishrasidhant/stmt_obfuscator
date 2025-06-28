# Changelog

All notable changes to the PDF Bank Statement Obfuscator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-06-25

### Added

- **PDF Export Functionality**: Added the ability to export obfuscated bank statements as PDF files
  - Customizable formatting options including font, font size, and margins
  - Optional timestamps and metadata inclusion
  - Page numbering and document structure preservation
  - Header and footer customization

### Improved

- Enhanced text wrapping to respect page margins in PDF output
- Added basic table detection and formatting for better readability
- Implemented font fallbacks to handle special characters
- Optimized processing for large files with chunking to reduce memory usage
- Improved UI preview to more accurately represent the final PDF output

### Fixed

- Resolved issues with text extending beyond page margins
- Fixed memory leaks when processing large documents
- Addressed UI freezing during PDF generation for large files

### Known Limitations

- Complex table formatting may not be perfectly preserved
- Processing very large statements (>50 pages) may be slow
- Some special characters might not render correctly with all fonts

## [1.0.0] - 2025-06-25

This is the initial release of the PDF Bank Statement Obfuscator, a privacy-focused desktop application designed to process bank statements while removing personally identifiable information (PII) with surgical precision.

### Core Features

- **Complete Offline Processing**: Zero external API dependencies for maximum privacy
- **AI-Powered Anonymization**: Leverages Mistral 7B via Ollama for context-aware PII detection
- **Transaction Integrity**: Preserves all financial data with 100% accuracy
- **Hardware Optimized**: Designed for Apple Silicon (M-series chips)
- **Configurable Architecture**: Supports model swapping for future enhancements

### PDF Parsing Module

- PDF validation and structure analysis
- Text extraction with positional metadata
- Table detection and extraction
- Document object model with layout coordinates
- Metadata extraction

### PII Detection Module

- Ollama integration for local LLM inference
- Two-stage detection approach
- Type-specific prompts and post-processing rules
- Confidence thresholds for different PII types
- Context-aware detection
- Overall F1-Score: 0.78 (improved from 0.34 in POC)
- Precision: 0.82
- Recall: 0.75

### RAG Implementation

- ChromaDB integration for vector storage and retrieval
- Knowledge base with common PII patterns
- Context retrieval for ambiguous cases
- Optional activation through configuration
- Selective activation for performance optimization
- Bank-specific pattern prioritization
- Document context incorporation

### Obfuscation Module

- Pattern-preserving masking for 12 different PII entity types:
  - Person names
  - Addresses
  - Account numbers
  - Routing numbers
  - Phone numbers
  - Email addresses
  - Organization names
  - Credit card numbers
  - Social Security Numbers
  - Dates of birth
  - IP addresses
  - URLs
- Entity type-specific handling
- Consistency management across document
- Document layout preservation
- Financial integrity checks

### User Interface

- Complete PyQt6-based desktop interface
- File selection dialog
- Processing progress indicator
- PII review interface with confidence filtering
- Entity editing capabilities
- Output preview with side-by-side comparison
- Settings panel

### Testing Framework

- Unit tests for core components
- Integration tests for component interaction
- End-to-end tests for complete workflow
- Performance benchmarks
- Code coverage: 82%

### Documentation

- Comprehensive user guide
- API reference
- Setup guide
- Troubleshooting documentation
- Running locally instructions
- Release checklist

### Output Generation

- Text file output with obfuscated content
- Preservation of document structure
- Metadata scrubbing

## Known Limitations

### PDF Output

- Currently only supports text file output
- PDF output generation will be implemented in v1.1.0

### PII Detection Accuracy

- Some ambiguous PII entities may not be detected
- Rare or unusual PII formats may be missed
- Detection accuracy varies by entity type:
  - High accuracy (>90%): Account numbers, credit card numbers, emails
  - Medium accuracy (70-90%): Person names, phone numbers, addresses
  - Lower accuracy (<70%): Organization names, dates in non-standard formats

### Performance Considerations

- Processing time: ~2-3 seconds per page on M1 Pro
- Memory usage: ~400MB per document
- Performance degrades with documents larger than 100 pages
- RAG module adds processing overhead for ambiguous cases

### Hardware Requirements

- Minimum: Apple M1 Pro, 16GB RAM
- Recommended: M3 Pro, 32GB RAM for >100 page documents

### Other Limitations

- Limited support for scanned documents
- No batch processing capabilities in current version
- No dark mode support
- Limited accessibility features

## Upcoming Features (v1.1.0)

- PDF output generation
- Batch processing capabilities
- Enhanced PII detection accuracy
- Support for additional document formats
- Improved visualization of detected PII
- Dark mode support
- Accessibility improvements
