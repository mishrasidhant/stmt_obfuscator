"""
Test data utilities for RAG module tests.

This module provides utilities for generating test data for RAG module tests.
"""

import random
import re
from typing import Dict, List, Tuple, Optional

from faker import Faker


class RAGTestDataGenerator:
    """Generator for RAG test data."""

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the RAGTestDataGenerator.

        Args:
            seed: Random seed for reproducibility (default: None)
        """
        if seed is not None:
            random.seed(seed)
            
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        
        # PII patterns for testing
        self.pii_patterns = {
            "ACCOUNT_NUMBER": [
                r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                r"\bXXXX[-\s]?XXXX[-\s]?XXXX[-\s]?\d{4}\b"
            ],
            "ROUTING_NUMBER": [
                r"\b\d{9}\b"
            ],
            "PERSON_NAME": [
                r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"
            ],
            "ADDRESS": [
                r"\b\d+ [A-Za-z]+ (?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Plaza|Plz|Terrace|Ter)\b"
            ],
            "PHONE_NUMBER": [
                r"\b\(\d{3}\) \d{3}-\d{4}\b",
                r"\b\d{3}-\d{3}-\d{4}\b"
            ],
            "EMAIL": [
                r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
            ],
            "ORGANIZATION_NAME": [
                r"\b(?:Bank of America|Chase|Wells Fargo|Citibank|PNC Bank|TD Bank|Capital One|US Bank|Truist Bank)\b"
            ],
            "SSN": [
                r"\b\d{3}-\d{2}-\d{4}\b"
            ],
            "CREDIT_CARD_NUMBER": [
                r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
            ],
            "IP_ADDRESS": [
                r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
            ]
        }
        
        # Example PII values for testing
        self.pii_examples = {
            "ACCOUNT_NUMBER": [
                "1234-5678-9012-3456",
                "1234567890123456",
                "XXXX-XXXX-XXXX-3456"
            ],
            "ROUTING_NUMBER": [
                "123456789"
            ],
            "PERSON_NAME": [
                "John Doe",
                "Jane Smith",
                "Robert Johnson"
            ],
            "ADDRESS": [
                "123 Main Street",
                "456 Oak Avenue",
                "789 Elm Boulevard"
            ],
            "PHONE_NUMBER": [
                "(555) 123-4567",
                "555-123-4567"
            ],
            "EMAIL": [
                "john.doe@example.com",
                "jane.smith@company.org"
            ],
            "ORGANIZATION_NAME": [
                "Bank of America",
                "Chase",
                "Wells Fargo"
            ],
            "SSN": [
                "123-45-6789"
            ],
            "CREDIT_CARD_NUMBER": [
                "4111-1111-1111-1111",
                "5555555555554444"
            ],
            "IP_ADDRESS": [
                "192.168.1.1",
                "10.0.0.1"
            ]
        }

    def generate_pattern_with_example(self, pii_type: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Generate a pattern with an example for a specific PII type.

        Args:
            pii_type: The type of PII pattern to generate (default: random)

        Returns:
            A tuple containing:
                - The PII type
                - The pattern
                - An example of the pattern
        """
        if pii_type is None:
            pii_type = random.choice(list(self.pii_patterns.keys()))
            
        pattern = random.choice(self.pii_patterns[pii_type])
        example = random.choice(self.pii_examples[pii_type])
        
        return pii_type, pattern, example

    def generate_patterns(self, count: int = 10) -> List[Dict]:
        """
        Generate a list of patterns with examples.

        Args:
            count: The number of patterns to generate (default: 10)

        Returns:
            A list of dictionaries containing pattern information
        """
        patterns = []
        
        for _ in range(count):
            pii_type, pattern, example = self.generate_pattern_with_example()
            
            patterns.append({
                "pattern": pattern,
                "type": pii_type,
                "example": example
            })
            
        return patterns

    def generate_text_with_pii(self, pii_types: Optional[List[str]] = None, length: int = 500) -> Tuple[str, Dict]:
        """
        Generate text containing PII entities with ground truth annotations.

        Args:
            pii_types: List of PII types to include (default: random selection)
            length: Approximate length of the text to generate (default: 500)

        Returns:
            A tuple containing:
                - The generated text
                - A dictionary with ground truth PII annotations
        """
        if pii_types is None:
            # Randomly select 3-5 PII types
            pii_types = random.sample(list(self.pii_patterns.keys()), random.randint(3, 5))
            
        # Generate base text
        paragraphs = []
        remaining_length = length
        
        while remaining_length > 0:
            paragraph = self.faker.paragraph()
            paragraphs.append(paragraph)
            remaining_length -= len(paragraph)
        
        text = "\n\n".join(paragraphs)
        
        # Insert PII entities
        entities = []
        
        for pii_type in pii_types:
            # Select a random example
            example = random.choice(self.pii_examples[pii_type])
            
            # Find a suitable position to insert
            position = random.randint(0, len(text) - len(example))
            
            # Insert the PII entity
            text = text[:position] + example + text[position:]
            
            # Add to ground truth
            entities.append({
                "type": pii_type,
                "text": example,
                "start": position,
                "end": position + len(example),
                "confidence": 1.0  # Ground truth has perfect confidence
            })
            
        return text, {"entities": entities}

    def generate_query_results(self, query_text: str, top_k: int = 5) -> Dict:
        """
        Generate mock ChromaDB query results for testing.

        Args:
            query_text: The query text
            top_k: The number of results to generate (default: 5)

        Returns:
            A dictionary containing mock ChromaDB query results
        """
        documents = []
        metadatas = []
        distances = []
        
        for _ in range(top_k):
            pii_type, pattern, example = self.generate_pattern_with_example()
            
            documents.append(pattern)
            
            metadata = {
                "type": pii_type
            }
            
            # Add example to metadata with 80% probability
            if random.random() < 0.8:
                metadata["example"] = example
                
            metadatas.append(metadata)
            
            # Generate a random distance between 0 and 1
            distances.append(random.random())
            
        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances]
        }