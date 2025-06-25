# Obfuscation Module

The Obfuscation Module is responsible for applying pattern-preserving masking to detected PII entities in bank statements while maintaining document integrity.

## Features

- **Pattern-Preserving Masking**: Applies entity type-specific obfuscation techniques that preserve the format and structure of the original text
- **Entity Type Handling**: Specialized handling for different types of PII (names, addresses, account numbers, etc.)
- **Consistency Management**: Ensures the same PII is obfuscated consistently throughout the document
- **Document Layout Preservation**: Maintains the original document structure and formatting
- **Financial Integrity Checks**: Validates transaction totals and financial data before and after obfuscation

## Usage

```python
from stmt_obfuscator.obfuscation import Obfuscator

# Initialize the obfuscator
obfuscator = Obfuscator()

# Obfuscate a document with detected PII entities
obfuscated_document = obfuscator.obfuscate_document(document, pii_entities)

# The obfuscated document can now be passed to the output generator
```

## Entity Type Handling

The module provides specialized handling for different types of PII:

| Entity Type | Obfuscation Strategy |
|-------------|----------------------|
| PERSON_NAME | Replaces each word with X's of the same length (e.g., "John Doe" → "XXXX XXX") |
| ADDRESS | Preserves structure by replacing with X's but keeping punctuation and spaces |
| ACCOUNT_NUMBER | Keeps last 4 digits, masks the rest (e.g., "1234-5678-9012-3456" → "XXXX-XXXX-XXXX-3456") |
| ROUTING_NUMBER | Masks all digits with X's |
| PHONE_NUMBER | Preserves format by replacing digits with X's (e.g., "(555) 123-4567" → "(XXX) XXX-XXXX") |
| EMAIL | Masks username and domain while preserving structure (e.g., "john.doe@example.com" → "jXXXXXXX@XXXXXX.XXX") |
| ORGANIZATION_NAME | Uses a generic replacement that preserves length and structure |
| CREDIT_CARD_NUMBER | Keeps last 4 digits, masks the rest (e.g., "4111-1111-1111-1111" → "XXXX-XXXX-XXXX-1111") |
| SSN | Keeps last 4 digits, masks the rest (e.g., "123-45-6789" → "XXX-XX-6789") |
| DATE_OF_BIRTH | Replaces all digits with X's but keeps separators |
| IP_ADDRESS | Replaces all digits with X's but keeps dots |
| URL | Preserves protocol and domain structure but masks characters |

## Consistency Management

The module ensures that the same PII entity is obfuscated consistently throughout the document, even if it appears in different formats or contexts. This is achieved by:

1. Normalizing entity text for comparison
2. Grouping similar entities
3. Applying the same replacement to all entities in a group

## Financial Integrity Checks

The module includes integrity checks to validate transaction totals and financial data:

1. Extracts beginning and ending balances
2. Identifies transaction tables
3. Extracts transaction amounts and balances
4. Verifies that financial data is preserved after obfuscation

## Integration with Other Modules

The Obfuscation Module sits between the PII Management Module and the Output Generator Module in the processing pipeline:

```
PII Detection → PII Management → Obfuscation → Output Generator
```

It takes the detected PII entities from the PII Management Module and applies obfuscation techniques to the document before passing it to the Output Generator Module.