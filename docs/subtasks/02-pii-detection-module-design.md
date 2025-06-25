# Enhanced PII Detection Module Design

## Task Description
Design an enhanced PII detection module that addresses the challenges identified in the proof-of-concept, incorporating a two-stage detection approach, type-specific prompts, post-processing rules, confidence thresholds, and integration with Ollama.

## Design Details

### 1. Two-Stage Detection Approach

#### Stage 1: Candidate Identification (Broad Pass)
- **Purpose:** Identify all potential PII spans with high recall
- **Method:**
  - Use a general prompt to identify any text that might contain PII
  - Focus on text spans and approximate types
  - Output a list of `CandidatePIIEntity` objects with text, position, and general type

#### Stage 2: Validation and Classification (Refined Pass)
- **Purpose:** Validate and precisely classify each candidate
- **Method:**
  - Apply type-specific prompts for each candidate
  - Use post-processing rules for validation and standardization
  - Apply confidence thresholds
  - Output refined `PIIEntity` objects with exact type, text, position, and confidence score

### 2. Type-Specific Prompts
- **Structure:** Dictionary mapping PII types to prompt templates
- **Content:** Each prompt includes:
  - Clear definition of the PII type
  - Examples of valid and invalid formats
  - Instructions for identification
  - Request for boolean confirmation and confidence level
- **Management:** Configurable prompts stored in a separate configuration file or managed by a `PromptManager` class

### 3. Post-Processing Rules
- **Rules:** Defined for each PII type:
  - **Regex validation:** For structured PII like phone numbers, account numbers, emails
  - **Length checks:** Ensure values fall within expected ranges
  - **Standardization:** Convert to consistent formats
- **Implementation:** `PostProcessor` class with methods to process and validate entities

### 4. Confidence Thresholds
- **Confidence Source:**
  - LLM-derived confidence scores
  - Heuristic-based scores when direct confidence is unavailable
- **Threshold Application:**
  - Each entity has a confidence score (0.0 to 1.0)
  - Configurable thresholds per PII type
  - Entities below threshold can be discarded, flagged, or marked as low confidence
- **User Control:** Exposed thresholds for tuning precision/recall trade-off

### 5. Integration with Ollama
- **Core Class:** Enhanced `PIIDetector` as the main orchestrator
- **Key Methods:**
  - `detect_pii`: Orchestrates the two-stage process
  - `_identify_pii_candidates`: Implements Stage 1
  - `_validate_and_classify_candidate`: Implements Stage 2
  - `_apply_post_processing`: Applies post-processing rules
- **Helper Classes:**
  - `PromptManager`: Manages and generates prompts
  - `PostProcessor`: Handles validation and standardization
  - `PIIDetectionConfig`: Holds configurable parameters
  - Data structures: `PIIEntity` and `CandidatePIIEntity`

### 6. Implementation Considerations
- **Error Handling:** Robust handling for API calls and JSON parsing
- **LLM Response Variations:** Flexible parsing logic for inconsistent outputs
- **Performance:** Strategies for handling multiple API calls
- **Context Preservation:** Support for document structure and layout information
- **Evaluation:** Support for granular evaluation by PII type

## Outcome
The enhanced PII detection module design addresses the challenges identified in the proof-of-concept and provides a blueprint for implementation. The two-stage approach, combined with type-specific prompts and post-processing rules, should significantly improve detection accuracy while the confidence thresholds provide flexibility in balancing precision and recall.

## Next Steps
Implement the enhanced PII detection module according to this design, ensuring integration with the PDF parser and obfuscation modules.
