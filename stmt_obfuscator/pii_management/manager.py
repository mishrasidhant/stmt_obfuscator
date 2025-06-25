"""
PII Management module for the PDF Bank Statement Obfuscator.

This module handles the management of detected PII entities, including categorization,
replacement mapping, and user review.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple

from stmt_obfuscator.config import CONFIDENCE_THRESHOLD


logger = logging.getLogger(__name__)


class PIIManager:
    """PII Manager for handling detected PII entities."""

    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        """
        Initialize the PII Manager.

        Args:
            confidence_threshold: The confidence threshold for PII detection
        """
        self.confidence_threshold = confidence_threshold
        self.pii_entities = []
        self.replacement_map = {}
        self.entity_categories = {
            "PERSON_NAME": {"prefix": "PERSON", "mask_char": "X"},
            "ADDRESS": {"prefix": "ADDRESS", "mask_char": "X"},
            "ACCOUNT_NUMBER": {"prefix": "ACCT", "mask_char": "X"},
            "ROUTING_NUMBER": {"prefix": "ROUTING", "mask_char": "X"},
            "PHONE_NUMBER": {"prefix": "PHONE", "mask_char": "X"},
            "EMAIL": {"prefix": "EMAIL", "mask_char": "X"},
            "ORGANIZATION_NAME": {"prefix": "ORG", "mask_char": "X"},
            "CREDIT_CARD_NUMBER": {"prefix": "CC", "mask_char": "X"},
            "SSN": {"prefix": "SSN", "mask_char": "X"},
            "DATE_OF_BIRTH": {"prefix": "DOB", "mask_char": "X"},
            "IP_ADDRESS": {"prefix": "IP", "mask_char": "X"},
            "URL": {"prefix": "URL", "mask_char": "X"},
        }
        
        logger.info("Initialized PII Manager")

    def process_entities(self, detected_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process detected PII entities.

        Args:
            detected_entities: List of detected PII entities

        Returns:
            List of processed PII entities with additional metadata
        """
        self.pii_entities = []
        self.replacement_map = {}
        
        # Filter entities by confidence threshold
        filtered_entities = [
            entity for entity in detected_entities
            if entity.get("confidence", 1.0) >= self.confidence_threshold
        ]
        
        # Process each entity
        for entity in filtered_entities:
            processed_entity = self._process_entity(entity)
            self.pii_entities.append(processed_entity)
            
            # Add to replacement map
            original_text = processed_entity["text"]
            replacement = processed_entity["replacement"]
            self.replacement_map[original_text] = replacement
        
        logger.info(f"Processed {len(self.pii_entities)} PII entities")
        return self.pii_entities

    def get_replacement_map(self) -> Dict[str, str]:
        """
        Get the replacement map for PII entities.

        Returns:
            A dictionary mapping original text to replacement text
        """
        return self.replacement_map

    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a PII entity with user-provided changes.

        Args:
            entity_id: The ID of the entity to update
            updates: Dictionary of updates to apply

        Returns:
            True if the entity was updated successfully, False otherwise
        """
        for i, entity in enumerate(self.pii_entities):
            if entity.get("id") == entity_id:
                # Update entity
                for key, value in updates.items():
                    if key in entity:
                        entity[key] = value
                
                # Regenerate replacement if needed
                if "type" in updates or "text" in updates:
                    entity["replacement"] = self._generate_replacement(
                        entity["text"], entity["type"]
                    )
                    
                    # Update replacement map
                    self.replacement_map[entity["text"]] = entity["replacement"]
                
                logger.info(f"Updated PII entity: {entity_id}")
                return True
        
        logger.warning(f"PII entity not found: {entity_id}")
        return False

    def add_entity(self, entity: Dict[str, Any]) -> str:
        """
        Add a new PII entity.

        Args:
            entity: The PII entity to add

        Returns:
            The ID of the added entity
        """
        # Generate entity ID
        entity_id = f"entity_{len(self.pii_entities)}"
        
        # Process entity
        processed_entity = self._process_entity({
            "id": entity_id,
            "type": entity.get("type", "UNKNOWN"),
            "text": entity.get("text", ""),
            "start": entity.get("start", 0),
            "end": entity.get("end", 0),
            "confidence": entity.get("confidence", 1.0),
        })
        
        self.pii_entities.append(processed_entity)
        
        # Add to replacement map
        original_text = processed_entity["text"]
        replacement = processed_entity["replacement"]
        self.replacement_map[original_text] = replacement
        
        logger.info(f"Added new PII entity: {entity_id}")
        return entity_id

    def remove_entity(self, entity_id: str) -> bool:
        """
        Remove a PII entity.

        Args:
            entity_id: The ID of the entity to remove

        Returns:
            True if the entity was removed successfully, False otherwise
        """
        for i, entity in enumerate(self.pii_entities):
            if entity.get("id") == entity_id:
                # Remove from replacement map
                if entity["text"] in self.replacement_map:
                    del self.replacement_map[entity["text"]]
                
                # Remove entity
                self.pii_entities.pop(i)
                
                logger.info(f"Removed PII entity: {entity_id}")
                return True
        
        logger.warning(f"PII entity not found: {entity_id}")
        return False

    def _process_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a PII entity to add additional metadata.

        Args:
            entity: The PII entity to process

        Returns:
            The processed PII entity with additional metadata
        """
        # Ensure entity has an ID
        if "id" not in entity:
            entity["id"] = f"entity_{len(self.pii_entities)}"
        
        # Generate replacement text
        entity["replacement"] = self._generate_replacement(
            entity["text"], entity["type"]
        )
        
        # Add category info
        category_info = self.entity_categories.get(
            entity["type"], {"prefix": "PII", "mask_char": "X"}
        )
        entity["category"] = category_info
        
        return entity

    def _generate_replacement(self, text: str, entity_type: str) -> str:
        """
        Generate a replacement for a PII entity.

        Args:
            text: The original text
            entity_type: The type of PII entity

        Returns:
            The replacement text
        """
        category_info = self.entity_categories.get(
            entity_type, {"prefix": "PII", "mask_char": "X"}
        )
        
        prefix = category_info["prefix"]
        mask_char = category_info["mask_char"]
        
        # Special handling for different entity types
        if entity_type == "ACCOUNT_NUMBER":
            # Keep last 4 digits if available
            if len(text) >= 4:
                return f"XXXX-XXXX-XXXX-{text[-4:]}"
            else:
                return mask_char * len(text)
        
        elif entity_type == "PHONE_NUMBER":
            # Format as (XXX) XXX-XXXX
            digits = re.sub(r'\D', '', text)
            if len(digits) >= 10:
                return f"({mask_char * 3}) {mask_char * 3}-{mask_char * 4}"
            else:
                return mask_char * len(text)
        
        elif entity_type == "EMAIL":
            # Format as XXXX@XXXX.XXX
            parts = text.split('@')
            if len(parts) == 2:
                domain_parts = parts[1].split('.')
                if len(domain_parts) >= 2:
                    return f"{mask_char * 4}@{mask_char * 4}.{mask_char * 3}"
            
            return mask_char * len(text)
        
        elif entity_type == "PERSON_NAME":
            # Replace each word with mask characters of the same length
            words = text.split()
            masked_words = [mask_char * len(word) for word in words]
            return ' '.join(masked_words)
        
        elif entity_type == "ADDRESS":
            # Replace with generic format
            return f"{prefix}_{mask_char * (len(text) // 2)}"
        
        else:
            # Default replacement
            return f"{prefix}_{mask_char * (len(text) // 2)}"