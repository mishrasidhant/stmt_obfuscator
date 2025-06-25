# PII Detection Proof-of-Concept using Ollama with Local LLMs

This proof-of-concept demonstrates PII (Personally Identifiable Information) detection in bank statements using Ollama with local LLMs. It validates that Ollama with local LLMs can effectively detect PII in bank statement text.

## Components

1. **PII Detector** (`scripts/pii_detector.py`): Connects to Ollama API, sends prompts to detect PII, and parses responses.
2. **Sample Generator** (`scripts/generate_samples.py`): Creates synthetic bank statement samples with ground truth annotations.
3. **Evaluation Script** (`scripts/evaluate.py`): Calculates precision, recall, and F1-score metrics by comparing detected PII with ground truth.
4. **Quick Test Script** (`scripts/quick_test.py`): Demonstrates the PII detection with a sample bank statement in one simple step.

## Prerequisites

- Python 3.10+
- Ollama installed on your machine
- Mistral model (or another compatible model)

## Installation

1. **Install Ollama**

   Follow the instructions at [Ollama's official website](https://ollama.ai/download) to install Ollama for your platform:

   - **macOS**:
     ```
     brew install ollama
     ```

   - **Linux**:
     ```
     curl -fsSL https://ollama.ai/install.sh | sh
     ```

   - **Windows**:
     Download the installer from [Ollama's website](https://ollama.ai/download).

2. **Pull the Mistral model**

   After installing Ollama, pull the Mistral model:
   ```
   ollama pull mistral:latest
   ```

3. **Install Python dependencies**

   ```
   cd pii_detection_poc
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

For a quick demonstration of the PII detection capabilities:

```
cd pii_detection_poc
python scripts/quick_test.py
```

This script will:
1. Generate a sample bank statement
2. Detect PII using Ollama
3. Display the results and ground truth
4. Save all files to the `data` directory

### 1. Generate Synthetic Samples

Generate synthetic bank statement samples with ground truth annotations:

```
cd pii_detection_poc
python scripts/generate_samples.py --num-samples 5 --output-dir data
```

Options:
- `--num-samples`: Number of samples to generate (default: 5)
- `--output-dir`: Output directory for samples (default: ../data)
- `--seed`: Random seed for reproducibility (optional)

### 2. Run PII Detection

Detect PII in a bank statement:

```
python scripts/pii_detector.py --input data/statement_1.txt
```

Options:
- `--model`: Ollama model to use (default: mistral:latest)
- `--host`: Ollama API host URL (default: http://localhost:11434)
- `--input`: Input text file containing bank statement

### 3. Evaluate Performance

Evaluate PII detection performance against ground truth:

```
python scripts/evaluate.py
```

Options:
- `--model`: Ollama model to use (default: mistral:latest)
- `--host`: Ollama API host URL (default: http://localhost:11434)
- `--data-dir`: Directory containing samples (default: ../data)
- `--output`: Output file for evaluation results (default: ../data/evaluation_results.json)

## Interpreting Results

The evaluation script calculates the following metrics:

- **Precision**: The proportion of detected PII entities that are correct (true positives / (true positives + false positives))
- **Recall**: The proportion of actual PII entities that were detected (true positives / (true positives + false negatives))
- **F1-Score**: The harmonic mean of precision and recall (2 * precision * recall / (precision + recall))

A higher F1-score indicates better overall performance. The ideal system would have both high precision (few false positives) and high recall (few false negatives).

Example output:
```
Evaluated statement_1.txt: Precision=0.92, Recall=0.85, F1=0.88
Evaluated statement_2.txt: Precision=0.88, Recall=0.90, F1=0.89
...

Overall Results:
Precision: 0.9000
Recall: 0.8750
F1-Score: 0.8874
Number of Samples: 5

Results saved to data/evaluation_results.json
```

## Customizing the Model

You can use a different model by:

1. Pulling the model with Ollama:
   ```
   ollama pull llama3:latest
   ```

2. Specifying the model when running the scripts:
   ```
   python scripts/pii_detector.py --model llama3:latest --input data/statement_1.txt
   python scripts/evaluate.py --model llama3:latest
   ```

## Results and Findings

The proof-of-concept demonstrated that Ollama with local LLMs can effectively detect PII in bank statements, with performance varying across different samples:

- Overall F1-Score: 0.34
- Best Sample Precision: 0.70
- Best Sample Recall: 0.50

For detailed findings and recommendations based on this proof-of-concept, see the [findings and recommendations](findings_and_recommendations.md) document.

## Limitations

- This proof-of-concept focuses on text-based bank statements and does not handle PDF parsing.
- The synthetic data generator creates simplified bank statements that may not capture all the complexity of real statements.
- Performance varies significantly between samples and PII types.
- Position detection (start/end indices) is challenging for the model.

## Next Steps

Based on the findings from this proof-of-concept, the next steps would be:
1. Enhance PII detection with improved prompts and post-processing
2. Integrate with PDF parsing using PyMuPDF
3. Implement the obfuscation module
4. Develop the user interface with confidence visualization
5. Add targeted RAG enhancement for ambiguous cases