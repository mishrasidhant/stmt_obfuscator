"""
RAG Context Enhancer module for the PDF Bank Statement Obfuscator.

This module provides context enhancement for PII detection using RAG (Retrieval Augmented Generation).
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

import chromadb
from chromadb.config import Settings

from stmt_obfuscator.config import CACHE_DIR, RAG_ENABLED


logger = logging.getLogger(__name__)


class RAGContextEnhancer:
    """RAG Context Enhancer for improving PII detection with contextual information."""

    def __init__(self, collection_name: str = "pii_patterns"):
        """
        Initialize the RAG Context Enhancer.

        Args:
            collection_name: The name of the ChromaDB collection to use
        """
        self.enabled = RAG_ENABLED
        self.collection_name = collection_name
        self.db_path = CACHE_DIR / "chromadb"
        self.db_path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "PII patterns for bank statements"}
            )
            logger.info(f"Initialized RAG Context Enhancer with collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection: {e}")
            self.enabled = False
    
    def get_context(self, text_chunk: str, top_k: int = 5) -> Optional[Dict[str, Any]]:
        """
        Get context for a text chunk to enhance PII detection.

        Args:
            text_chunk: The text chunk to get context for
            top_k: The number of top results to return

        Returns:
            A dictionary containing context information, or None if RAG is disabled
        """
        if not self.enabled:
            logger.info("RAG is disabled, skipping context enhancement")
            return None
        
        try:
            # Query the collection for similar patterns
            results = self.collection.query(
                query_texts=[text_chunk],
                n_results=top_k
            )
            
            if not results["documents"] or not results["documents"][0]:
                logger.info("No relevant context found in RAG")
                return None
            
            # Build context from results
            context = {
                "patterns": [],
                "examples": []
            }
            
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] and results["metadatas"][0] else {}
                pattern_type = metadata.get("type", "UNKNOWN")
                
                context["patterns"].append({
                    "type": pattern_type,
                    "pattern": doc,
                    "score": results["distances"][0][i] if results["distances"] and results["distances"][0] else 0
                })
                
                if "example" in metadata:
                    context["examples"].append({
                        "type": pattern_type,
                        "text": metadata["example"]
                    })
            
            logger.info(f"Found {len(context['patterns'])} relevant patterns for context enhancement")
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context from RAG: {e}")
            return None
    
    def add_pattern(self, pattern: str, pattern_type: str, example: Optional[str] = None) -> bool:
        """
        Add a PII pattern to the RAG knowledge base.

        Args:
            pattern: The pattern to add
            pattern_type: The type of PII pattern
            example: An optional example of the pattern

        Returns:
            True if the pattern was added successfully, False otherwise
        """
        if not self.enabled:
            logger.info("RAG is disabled, skipping pattern addition")
            return False
        
        try:
            metadata = {
                "type": pattern_type
            }
            
            if example:
                metadata["example"] = example
            
            self.collection.add(
                documents=[pattern],
                metadatas=[metadata],
                ids=[f"{pattern_type}_{len(pattern)}_{hash(pattern) % 10000}"]
            )
            
            logger.info(f"Added pattern to RAG: {pattern_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding pattern to RAG: {e}")
            return False
    
    def initialize_knowledge_base(self) -> bool:
        """
        Initialize the knowledge base with common PII patterns.

        Returns:
            True if the knowledge base was initialized successfully, False otherwise
        """
        if not self.enabled:
            logger.info("RAG is disabled, skipping knowledge base initialization")
            return False
        
        try:
            # Check if collection is empty
            if self.collection.count() > 0:
                logger.info("Knowledge base already initialized")
                return True
            
            # Add common PII patterns
            patterns = [
                # Account numbers
                {
                    "pattern": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                    "type": "ACCOUNT_NUMBER",
                    "example": "1234-5678-9012-3456"
                },
                {
                    "pattern": r"\bXXXX[-\s]?XXXX[-\s]?XXXX[-\s]?\d{4}\b",
                    "type": "ACCOUNT_NUMBER",
                    "example": "XXXX-XXXX-XXXX-1234"
                },
                # Routing numbers
                {
                    "pattern": r"\b\d{9}\b",
                    "type": "ROUTING_NUMBER",
                    "example": "123456789"
                },
                # Names
                {
                    "pattern": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
                    "type": "PERSON_NAME",
                    "example": "John Doe"
                },
                # Addresses
                {
                    "pattern": r"\b\d+ [A-Za-z]+ (?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Plaza|Plz|Terrace|Ter)\b",
                    "type": "ADDRESS",
                    "example": "123 Main Street"
                },
                # Phone numbers
                {
                    "pattern": r"\b\(\d{3}\) \d{3}-\d{4}\b",
                    "type": "PHONE_NUMBER",
                    "example": "(555) 123-4567"
                },
                {
                    "pattern": r"\b\d{3}-\d{3}-\d{4}\b",
                    "type": "PHONE_NUMBER",
                    "example": "555-123-4567"
                },
                # Email addresses
                {
                    "pattern": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
                    "type": "EMAIL",
                    "example": "john.doe@example.com"
                },
                # Bank names
                {
                    "pattern": r"\b(?:Bank of America|Chase|Wells Fargo|Citibank|PNC Bank|TD Bank|Capital One|US Bank|Truist Bank)\b",
                    "type": "ORGANIZATION_NAME",
                    "example": "Bank of America"
                }
            ]
            
            for pattern_info in patterns:
                self.add_pattern(
                    pattern=pattern_info["pattern"],
                    pattern_type=pattern_info["type"],
                    example=pattern_info.get("example")
                )
            
            logger.info(f"Initialized knowledge base with {len(patterns)} patterns")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
            return False