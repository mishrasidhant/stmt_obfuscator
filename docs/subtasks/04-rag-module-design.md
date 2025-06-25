# RAG Module Design

## Task Description
Design a targeted RAG (Retrieval-Augmented Generation) module for the PDF Bank Statement Obfuscator that focuses on ambiguous cases, prioritizes bank-specific patterns, incorporates document context, and uses ChromaDB for efficient retrieval.

## Design Details

### 1. Ambiguity Detection and RAG Triggering
- **Mechanism:** The PII detection module flags text segments with low confidence or ambiguous classification
- **Input to RAG:**
  - Ambiguous text segment
  - Surrounding context (lines before and after)
  - Structural metadata (e.g., "is part of a table," "is a header")
- **Selective Activation:** RAG is only triggered for ambiguous cases, not all text

### 2. Knowledge Base (ChromaDB) Construction
- **Content:**
  - **Bank-specific patterns:** Common bank statement fields, PII types in banking context, typical layouts
  - **Disambiguation rules/examples:** Rules to distinguish PII from non-PII in ambiguous contexts
  - **Document Context Encoding:** Information about text elements being part of headers, tables, etc.
- **Process:**
  - Create document chunks from curated banking knowledge
  - Generate embeddings using a Sentence Transformer
  - Store embeddings and original text in ChromaDB

### 3. Retrieval Mechanism
- **Query Generation:**
  - Create query embedding from ambiguous text, context, and metadata
  - Incorporate structural hints (e.g., "ambiguous number in table column 'Description'")
- **ChromaDB Query:** Perform similarity search to find relevant patterns and rules
- **Output:** Retrieve top-k most relevant items from the knowledge base

### 4. Generation/Re-evaluation
- **Integration with PII Detector:** Pass retrieved context back to PII detection module
- **Re-classification:**
  - Apply retrieved rules directly
  - Use retrieved examples as few-shot prompts
  - Adjust confidence scores based on retrieved patterns

### 5. Module Structure
- **Components:**
  - `rag_module.py`: Encapsulates ChromaDB interaction
  - `context_enhancer.py`: Orchestrates interaction between PII detector and RAG module
- **Key Classes and Methods:**
  - `RAGModule`: Main class for RAG functionality
  - `KnowledgeBase`: Manages the ChromaDB instance
  - `QueryGenerator`: Creates effective queries from ambiguous text
  - `ContextEnhancer`: Integrates RAG results with PII detection

### 6. Integration with PII Detection
- **Interface:**
  - PII detector calls `resolve_ambiguity` function in `context_enhancer.py`
  - Function mediates call to RAG module and enhances detection with retrieved context
- **Data Flow:**
  - PII detector → Context Enhancer → RAG Module → ChromaDB → Context Enhancer → PII detector

### 7. Optionality
- **Configuration:**
  - `ENABLE_RAG_MODULE` flag in `config.py`
  - If disabled, ambiguous cases handled by existing fallbacks
- **Performance Considerations:**
  - RAG operations add latency
  - Optional activation balances performance and accuracy

## Considerations and Challenges
1. **Defining "Ambiguous Cases":** Need precise criteria for when to trigger RAG
2. **Bank-Specific Pattern Collection:** Curating a robust knowledge base is critical
3. **Context Extraction:** Requires rich structural information from PDF parser
4. **ChromaDB Management:** Persistence, updates, and maintenance
5. **Performance Impact:** Need to balance accuracy and speed
6. **False Positives/Negatives:** RAG could introduce new errors if retrieved context is irrelevant
7. **Integration Complexity:** Ensuring seamless data flow between components
8. **Embedding Model Selection:** Need appropriate model for financial texts

## Outcome
The RAG module design provides a targeted approach to enhancing PII detection for ambiguous cases, addressing the recommendations from the proof-of-concept findings. The optional nature of the module allows for flexibility in balancing performance and accuracy.

## Next Steps
Implement the RAG module according to this design, ensuring integration with the PII detection module and proper configuration for optional activation.
