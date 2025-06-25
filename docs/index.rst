PDF Bank Statement Obfuscator Documentation
==========================================

Welcome to the PDF Bank Statement Obfuscator documentation. This documentation provides comprehensive information about the project, its architecture, and how to use it.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   user_guide
   architecture
   api_reference
   development
   troubleshooting
   changelog

Introduction
-----------

The PDF Bank Statement Obfuscator is a privacy-focused desktop application designed to process bank statements while removing personally identifiable information (PII) with surgical precision.

Key features include:

* Complete offline processing with zero external API dependencies
* AI-powered anonymization using Mistral 7B via Ollama
* Transaction integrity that preserves all financial data
* Hardware optimization for Apple Silicon (M-series chips)
* Configurable architecture that supports model swapping

For more details, see the :doc:`introduction` page.

Quick Start
----------

1. Install the application from the `releases page <https://github.com/yourusername/stmt_obfuscator/releases>`_
2. Install `Ollama <https://ollama.ai/>`_ and download the Mistral 7B model
3. Launch the application and select a PDF bank statement to process
4. Review and adjust detected PII entities
5. Generate and save the obfuscated PDF

For detailed installation instructions, see the :doc:`installation` page.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`