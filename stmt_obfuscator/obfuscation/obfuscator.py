"""
Obfuscation module for the PDF Bank Statement Obfuscator.

This module handles the obfuscation of detected PII entities in bank statements,
applying pattern-preserving masking while maintaining document integrity.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
import json
import hashlib

from stmt_obfuscator.config import CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)


class Obfuscator:
    """
    Obfuscator for handling PII entity obfuscation in bank statements.
    
    This class applies pattern-preserving masking to detected PII entities,
    maintains consistency across the document, and preserves document layout
    and structure while ensuring transaction integrity.
    """

    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        """
        Initialize the Obfuscator.

        Args:
            confidence_threshold: The confidence threshold for PII obfuscation
        """
        self.confidence_threshold = confidence_threshold
        self.replacement_map = {}
        self.entity_consistency_map = {}
        self.transaction_totals = {}
        self.financial_integrity_checks = {}
        
        # Define entity type handling strategies
        self.entity_handlers = {
            "PERSON_NAME": self._handle_person_name,
            "ADDRESS": self._handle_address,
            "ACCOUNT_NUMBER": self._handle_account_number,
            "ROUTING_NUMBER": self._handle_routing_number,
            "PHONE_NUMBER": self._handle_phone_number,
            "EMAIL": self._handle_email,
            "ORGANIZATION_NAME": self._handle_organization_name,
            "CREDIT_CARD_NUMBER": self._handle_credit_card_number,
            "SSN": self._handle_ssn,
            "DATE_OF_BIRTH": self._handle_date_of_birth,
            "IP_ADDRESS": self._handle_ip_address,
            "URL": self._handle_url,
        }
        
        logger.info("Initialized Obfuscator")

    def obfuscate_document(self, document: Dict[str, Any], pii_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Obfuscate a document based on detected PII entities.

        Args:
            document: The document to obfuscate, containing text and layout information
            pii_entities: List of detected PII entities

        Returns:
            The obfuscated document with PII entities masked
        """
        try:
            # Validate inputs
            if not isinstance(document, dict):
                logger.error(f"Document is not a dictionary: {type(document)}")
                raise TypeError(f"Document must be a dictionary, got {type(document)}")
                
            if not isinstance(pii_entities, (list, tuple)):
                logger.error(f"PII entities is not a list: {type(pii_entities)}")
                raise TypeError(f"PII entities must be a list, got {type(pii_entities)}")
            
            # Ensure document has required fields
            if "full_text" not in document:
                logger.warning("Document missing 'full_text', adding empty string")
                document["full_text"] = ""
                
            if "metadata" not in document:
                logger.warning("Document missing 'metadata', adding empty dict")
                document["metadata"] = {}
                
            if "text_blocks" not in document:
                logger.warning("Document missing 'text_blocks', adding empty list")
                document["text_blocks"] = []
            
            # Extract financial data for integrity checks
            try:
                self._extract_financial_data(document)
            except Exception as e:
                logger.error(f"Error extracting financial data: {e}")
                # Continue processing even if financial data extraction fails
            
            # Create a deep copy of the document to avoid modifying the original
            try:
                obfuscated_document = self._deep_copy_document(document)
            except Exception as e:
                logger.error(f"Error creating deep copy: {e}")
                # Fall back to using the original document
                obfuscated_document = document
            
            # Process entities and build replacement map
            try:
                self._build_replacement_map(pii_entities)
            except Exception as e:
                logger.error(f"Error building replacement map: {e}")
                # Continue with empty replacement map if building fails
                self.replacement_map = {}
            
            # Apply obfuscation to document text
            obfuscated_document = self._apply_obfuscation(obfuscated_document)
            
            # Verify financial integrity
            try:
                integrity_verified = self._verify_financial_integrity(obfuscated_document)
                if not integrity_verified:
                    logger.warning("Financial integrity check failed after obfuscation")
            except Exception as e:
                logger.error(f"Error verifying financial integrity: {e}")
                # Continue even if integrity verification fails
            
            # Add obfuscation metadata
            try:
                if "metadata" not in obfuscated_document:
                    obfuscated_document["metadata"] = {}
                    
                obfuscated_document["metadata"]["obfuscated"] = True
                obfuscated_document["metadata"]["obfuscation_timestamp"] = self._get_timestamp()
                obfuscated_document["metadata"]["entities_obfuscated"] = len(self.replacement_map)
            except Exception as e:
                logger.error(f"Error adding metadata: {e}")
                # Continue even if adding metadata fails
            
            logger.info(f"Obfuscated document with {len(self.replacement_map)} PII entities")
            return obfuscated_document
            
        except Exception as e:
            logger.error(f"Error in obfuscate_document: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return a minimal valid document in case of error
            return {
                "full_text": document.get("full_text", "") if isinstance(document, dict) else "",
                "metadata": {
                    "error": str(e),
                    "obfuscated": False
                },
                "text_blocks": []
            }

    def _build_replacement_map(self, pii_entities: List[Dict[str, Any]]) -> None:
        """
        Build a replacement map for PII entities.

        Args:
            pii_entities: List of detected PII entities
        """
        try:
            self.replacement_map = {}
            self.entity_consistency_map = {}
            
            # Validate input
            if not isinstance(pii_entities, (list, tuple)):
                logger.error(f"PII entities is not a list: {type(pii_entities)}")
                raise TypeError(f"PII entities must be a list, got {type(pii_entities)}")
            
            # Filter entities by confidence threshold
            filtered_entities = []
            for entity in pii_entities:
                if not isinstance(entity, dict):
                    logger.warning(f"Entity is not a dictionary: {type(entity)}")
                    continue
                    
                confidence = entity.get("confidence", 1.0)
                if not isinstance(confidence, (int, float)):
                    logger.warning(f"Confidence is not a number: {type(confidence)}")
                    confidence = 1.0
                    
                if confidence >= self.confidence_threshold:
                    filtered_entities.append(entity)
            
            logger.info(f"Filtered {len(pii_entities)} entities to {len(filtered_entities)} based on confidence threshold")
            
            # Group similar entities for consistency
            try:
                entity_groups = self._group_similar_entities(filtered_entities)
            except Exception as e:
                logger.error(f"Error grouping entities: {e}")
                # Fall back to simple grouping by type
                entity_groups = {}
                for entity in filtered_entities:
                    entity_type = entity.get("type", "UNKNOWN")
                    if entity_type not in entity_groups:
                        entity_groups[entity_type] = []
                    entity_groups[entity_type].append(entity)
            
            # Process each entity group
            for group_id, entities in entity_groups.items():
                try:
                    # Use the highest confidence entity as the representative
                    representative = max(entities, key=lambda e: e.get("confidence", 0))
                    entity_type = representative.get("type", "UNKNOWN")
                    
                    # Generate consistent replacement for all entities in the group
                    if entity_type in self.entity_handlers:
                        replacement = self.entity_handlers[entity_type](representative)
                    else:
                        # Default handler for unknown entity types
                        replacement = self._handle_default(representative)
                    
                    # Apply the same replacement to all entities in the group
                    for entity in entities:
                        if "text" not in entity:
                            logger.warning(f"Entity missing 'text' field: {entity}")
                            continue
                            
                        original_text = entity["text"]
                        self.replacement_map[original_text] = replacement
                        
                        # Store in consistency map for future reference
                        try:
                            entity_hash = self._compute_entity_hash(original_text, entity_type)
                            self.entity_consistency_map[entity_hash] = replacement
                        except Exception as hash_error:
                            logger.error(f"Error computing entity hash: {hash_error}")
                            # Continue without storing in consistency map
                except Exception as group_error:
                    logger.error(f"Error processing entity group {group_id}: {group_error}")
                    # Continue with next group
            
            logger.info(f"Built replacement map with {len(self.replacement_map)} entries")
        except Exception as e:
            logger.error(f"Error in _build_replacement_map: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Reset maps to empty to avoid partial state
            self.replacement_map = {}
            self.entity_consistency_map = {}

    def _group_similar_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group similar entities for consistent replacement.

        Args:
            entities: List of PII entities

        Returns:
            Dictionary mapping group IDs to lists of entities
        """
        groups = {}
        
        for entity in entities:
            entity_type = entity["type"]
            text = entity["text"]
            
            # Create a normalized version for comparison
            normalized_text = self._normalize_text(text, entity_type)
            
            # Compute a group ID based on normalized text and type
            group_id = f"{entity_type}_{normalized_text}"
            
            if group_id not in groups:
                groups[group_id] = []
            
            groups[group_id].append(entity)
        
        return groups

    def _normalize_text(self, text: str, entity_type: str) -> str:
        """
        Normalize text for entity grouping.

        Args:
            text: The text to normalize
            entity_type: The type of entity

        Returns:
            Normalized text for comparison
        """
        # Remove whitespace and convert to lowercase
        normalized = text.lower().strip()
        
        # Entity-specific normalization
        if entity_type == "PHONE_NUMBER":
            # Keep only digits
            normalized = re.sub(r'\D', '', normalized)
        elif entity_type == "EMAIL":
            # Lowercase is sufficient for emails
            pass
        elif entity_type == "ACCOUNT_NUMBER" or entity_type == "CREDIT_CARD_NUMBER":
            # Keep only digits and remove separators
            normalized = re.sub(r'\D', '', normalized)
        elif entity_type == "PERSON_NAME":
            # Remove titles and suffixes
            normalized = re.sub(r'^(mr|mrs|ms|dr|prof)\.?\s+', '', normalized)
            normalized = re.sub(r'\s+(jr|sr|phd|md|esq)\.?$', '', normalized)
        
        return normalized

    def _apply_obfuscation(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply obfuscation to document text.

        Args:
            document: The document to obfuscate

        Returns:
            The obfuscated document
        """
        try:
            # Obfuscate full text
            if "full_text" in document:
                document["full_text"] = self._obfuscate_text(document["full_text"])
            
            # Obfuscate text blocks
            if "text_blocks" in document:
                text_blocks = document["text_blocks"]
                if not isinstance(text_blocks, (list, tuple)):
                    logger.warning(f"text_blocks is not iterable: {type(text_blocks)}")
                    # Fix the issue by creating a proper list
                    document["text_blocks"] = [{"text": document.get("full_text", "")}]
                else:
                    for i, block in enumerate(text_blocks):
                        if not isinstance(block, dict):
                            logger.warning(f"Block is not a dictionary: {type(block)}")
                            continue
                        if "text" in block:
                            document["text_blocks"][i]["text"] = self._obfuscate_text(block["text"])
            
            # Obfuscate tables if present
            if "tables" in document:
                tables = document.get("tables", [])
                if not isinstance(tables, (list, tuple)):
                    logger.warning(f"tables is not iterable: {type(tables)}")
                    # Fix the issue by setting tables to an empty list
                    document["tables"] = []
                else:
                    for i, table in enumerate(tables):
                        if not isinstance(table, dict):
                            logger.warning(f"Table is not a dictionary: {type(table)}")
                            continue
                        
                        rows = table.get("rows", [])
                        if not isinstance(rows, (list, tuple)):
                            logger.warning(f"rows is not iterable: {type(rows)}")
                            continue
                            
                        for j, row in enumerate(rows):
                            if not isinstance(row, (list, tuple)):
                                logger.warning(f"row is not iterable: {type(row)}")
                                continue
                                
                            for k, cell in enumerate(row):
                                if isinstance(cell, str):
                                    document["tables"][i]["rows"][j][k] = self._obfuscate_text(cell)
            
            return document
        except Exception as e:
            logger.error(f"Error in _apply_obfuscation: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Return the original document if obfuscation fails
            return document

    def _obfuscate_text(self, text: str) -> str:
        """
        Obfuscate text by replacing PII entities.

        Args:
            text: The text to obfuscate

        Returns:
            The obfuscated text
        """
        # Sort replacements by length (descending) to avoid partial replacements
        sorted_replacements = sorted(
            self.replacement_map.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        # Apply replacements
        obfuscated_text = text
        for original, replacement in sorted_replacements:
            # Special handling for phone numbers and other entities with special characters
            if re.search(r'[().-]', original):
                # Use exact string replacement for entities with special characters
                obfuscated_text = obfuscated_text.replace(original, replacement)
            else:
                # Use word boundaries for normal text to avoid partial replacements
                pattern = r'\b' + re.escape(original) + r'\b'
                obfuscated_text = re.sub(pattern, replacement, obfuscated_text)
        
        return obfuscated_text

    def _extract_financial_data(self, document: Dict[str, Any]) -> None:
        """
        Extract financial data for integrity checks.

        Args:
            document: The document containing financial data
        """
        # Reset transaction totals
        self.transaction_totals = {}
        self.financial_integrity_checks = {}
        
        # Extract beginning and ending balances
        full_text = document.get("full_text", "")
        
        # Look for beginning balance
        beginning_balance_match = re.search(
            r'beginning\s+balance:?\s*\$?([\d,]+\.\d{2})',
            full_text,
            re.IGNORECASE
        )
        if beginning_balance_match:
            beginning_balance = self._parse_amount(beginning_balance_match.group(1))
            self.financial_integrity_checks["beginning_balance"] = beginning_balance
        
        # Look for ending balance
        ending_balance_match = re.search(
            r'ending\s+balance:?\s*\$?([\d,]+\.\d{2})',
            full_text,
            re.IGNORECASE
        )
        if ending_balance_match:
            ending_balance = self._parse_amount(ending_balance_match.group(1))
            self.financial_integrity_checks["ending_balance"] = ending_balance
        
        # Extract transactions if available
        if "tables" in document:
            # Ensure tables is iterable
            tables = document.get("tables", [])
            if not isinstance(tables, (list, tuple)):
                logger.warning(f"Tables is not iterable: {type(tables)}")
                return
                
            for table in tables:
                # Ensure table is a dictionary
                if not isinstance(table, dict):
                    logger.warning(f"Table is not a dictionary: {type(table)}")
                    continue
                    
                # Look for transaction tables
                if self._is_transaction_table(table):
                    transactions = self._extract_transactions(table)
                    self.financial_integrity_checks["transactions"] = transactions
                    
                    # Calculate transaction total
                    transaction_total = sum(t.get("amount", 0) for t in transactions)
                    self.financial_integrity_checks["transaction_total"] = transaction_total

    def _is_transaction_table(self, table: Dict[str, Any]) -> bool:
        """
        Determine if a table contains transaction data.

        Args:
            table: The table to check

        Returns:
            True if the table contains transaction data, False otherwise
        """
        # Check if the table has headers that suggest it's a transaction table
        headers = table.get("headers", [])
        header_text = " ".join(headers).lower()
        
        transaction_keywords = ["date", "description", "amount", "balance", "transaction"]
        return any(keyword in header_text for keyword in transaction_keywords)

    def _extract_transactions(self, table: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract transactions from a table.

        Args:
            table: The table containing transaction data

        Returns:
            List of transactions with date, description, amount, and balance
        """
        transactions = []
        
        # Get headers and determine column indices
        headers = [h.lower() for h in table.get("headers", [])]
        date_col = next((i for i, h in enumerate(headers) if "date" in h), None)
        desc_col = next((i for i, h in enumerate(headers) if "description" in h), None)
        amount_col = next((i for i, h in enumerate(headers) if "amount" in h), None)
        balance_col = next((i for i, h in enumerate(headers) if "balance" in h), None)
        
        # Extract transactions from rows
        for row in table.get("rows", []):
            if len(row) < max(filter(None, [date_col, desc_col, amount_col, balance_col])) + 1:
                continue
                
            transaction = {}
            
            if date_col is not None:
                transaction["date"] = row[date_col]
                
            if desc_col is not None:
                transaction["description"] = row[desc_col]
                
            if amount_col is not None:
                amount_str = row[amount_col]
                transaction["amount"] = self._parse_amount(amount_str)
                
            if balance_col is not None:
                balance_str = row[balance_col]
                transaction["balance"] = self._parse_amount(balance_str)
                
            transactions.append(transaction)
            
        return transactions

    def _parse_amount(self, amount_str: str) -> float:
        """
        Parse a financial amount from a string.

        Args:
            amount_str: The string containing the amount

        Returns:
            The parsed amount as a float
        """
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.-]', '', amount_str)
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _verify_financial_integrity(self, document: Dict[str, Any]) -> bool:
        """
        Verify financial integrity after obfuscation.

        Args:
            document: The obfuscated document

        Returns:
            True if financial integrity is maintained, False otherwise
        """
        # If we don't have financial data to check, return True
        if not self.financial_integrity_checks:
            return True
            
        # Extract financial data from obfuscated document
        obfuscated_financials = {}
        
        # Extract beginning and ending balances
        full_text = document.get("full_text", "")
        
        # Look for beginning balance
        beginning_balance_match = re.search(
            r'beginning\s+balance:?\s*\$?([\d,]+\.\d{2})',
            full_text,
            re.IGNORECASE
        )
        if beginning_balance_match:
            beginning_balance = self._parse_amount(beginning_balance_match.group(1))
            obfuscated_financials["beginning_balance"] = beginning_balance
        
        # Look for ending balance
        ending_balance_match = re.search(
            r'ending\s+balance:?\s*\$?([\d,]+\.\d{2})',
            full_text,
            re.IGNORECASE
        )
        if ending_balance_match:
            ending_balance = self._parse_amount(ending_balance_match.group(1))
            obfuscated_financials["ending_balance"] = ending_balance
        
        # Check if beginning and ending balances match
        for key in ["beginning_balance", "ending_balance"]:
            if (key in self.financial_integrity_checks and 
                key in obfuscated_financials and 
                self.financial_integrity_checks[key] != obfuscated_financials[key]):
                logger.warning(f"Financial integrity check failed: {key} mismatch")
                return False
        
        return True

    def _deep_copy_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deep copy of a document.

        Args:
            document: The document to copy

        Returns:
            A deep copy of the document
        """
        return json.loads(json.dumps(document))

    def _get_timestamp(self) -> str:
        """
        Get the current timestamp.

        Returns:
            The current timestamp as a string
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def _compute_entity_hash(self, text: str, entity_type: str) -> str:
        """
        Compute a hash for an entity for consistency tracking.

        Args:
            text: The entity text
            entity_type: The entity type

        Returns:
            A hash string for the entity
        """
        normalized = self._normalize_text(text, entity_type)
        return hashlib.md5(f"{entity_type}:{normalized}".encode()).hexdigest()

    # Entity type-specific handlers

    def _handle_person_name(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for person names.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        words = text.split()
        
        # Replace each word with X's of the same length
        masked_words = ["X" * len(word) for word in words]
        return " ".join(masked_words)

    def _handle_address(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for addresses.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Preserve structure by replacing with X's but keeping punctuation and spaces
        pattern = r'[a-zA-Z0-9]'
        return re.sub(pattern, 'X', text)

    def _handle_account_number(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for account numbers.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Keep last 4 digits if available
        digits = re.sub(r'\D', '', text)
        if len(digits) >= 4:
            last_four = digits[-4:]
            
            # Preserve format by replacing non-last-4 digits with X
            pattern = r'(\d)(?!\d{0,3}$)'
            masked = re.sub(pattern, 'X', text)
            return masked
        else:
            # If less than 4 digits, mask everything
            pattern = r'\d'
            return re.sub(pattern, 'X', text)

    def _handle_routing_number(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for routing numbers.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Mask all digits
        pattern = r'\d'
        return re.sub(pattern, 'X', text)

    def _handle_phone_number(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for phone numbers.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Preserve format by replacing digits with X
        pattern = r'\d'
        return re.sub(pattern, 'X', text)

    def _handle_email(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for email addresses.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Split into username and domain
        parts = text.split('@')
        if len(parts) != 2:
            # Not a valid email, mask everything
            return "X" * len(text)
            
        username, domain = parts
        
        # Mask username but preserve first character
        if len(username) > 1:
            masked_username = username[0] + "X" * (len(username) - 1)
        else:
            masked_username = "X"
            
        # Preserve domain structure but mask characters
        domain_parts = domain.split('.')
        masked_domain_parts = []
        
        for part in domain_parts:
            if part:
                masked_part = "X" * len(part)
                masked_domain_parts.append(masked_part)
            else:
                masked_domain_parts.append("")
                
        masked_domain = '.'.join(masked_domain_parts)
        
        return f"{masked_username}@{masked_domain}"

    def _handle_organization_name(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for organization names.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # For organization names, we'll use a generic replacement
        # but preserve length and structure
        words = text.split()
        masked_words = []
        
        for word in words:
            if len(word) <= 2:  # Keep short words like "of", "in", etc.
                masked_words.append(word)
            else:
                masked_words.append("X" * len(word))
                
        return " ".join(masked_words)

    def _handle_credit_card_number(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for credit card numbers.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Keep last 4 digits if available
        digits = re.sub(r'\D', '', text)
        if len(digits) >= 4:
            last_four = digits[-4:]
            
            # Standard credit card format: XXXX-XXXX-XXXX-1234
            if len(digits) >= 16:
                return f"XXXX-XXXX-XXXX-{last_four}"
            else:
                # Preserve format by replacing non-last-4 digits with X
                pattern = r'(\d)(?!\d{0,3}$)'
                return re.sub(pattern, 'X', text)
        else:
            # If less than 4 digits, mask everything
            pattern = r'\d'
            return re.sub(pattern, 'X', text)

    def _handle_ssn(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for social security numbers.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Keep last 4 digits if available
        digits = re.sub(r'\D', '', text)
        if len(digits) >= 4:
            last_four = digits[-4:]
            
            # Standard SSN format: XXX-XX-1234
            if len(digits) == 9:
                return f"XXX-XX-{last_four}"
            else:
                # Preserve format by replacing non-last-4 digits with X
                pattern = r'(\d)(?!\d{0,3}$)'
                return re.sub(pattern, 'X', text)
        else:
            # If less than 4 digits, mask everything
            pattern = r'\d'
            return re.sub(pattern, 'X', text)

    def _handle_date_of_birth(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for dates of birth.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Replace all digits with X but keep separators
        pattern = r'\d'
        return re.sub(pattern, 'X', text)

    def _handle_ip_address(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for IP addresses.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Replace all digits with X but keep dots
        pattern = r'\d'
        return re.sub(pattern, 'X', text)

    def _handle_url(self, entity: Dict[str, Any]) -> str:
        """
        Handle obfuscation for URLs.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        
        # Preserve protocol and domain structure but mask characters
        if '://' in text:
            protocol, rest = text.split('://', 1)
        else:
            protocol, rest = '', text
            
        # Handle domain and path
        if '/' in rest:
            domain, path = rest.split('/', 1)
            masked_domain = self._mask_domain(domain)
            masked_path = "X" * len(path)
            return f"{protocol}://{masked_domain}/{masked_path}"
        else:
            masked_domain = self._mask_domain(rest)
            return f"{protocol}://{masked_domain}" if protocol else masked_domain

    def _mask_domain(self, domain: str) -> str:
        """
        Mask a domain name while preserving structure.

        Args:
            domain: The domain to mask

        Returns:
            The masked domain
        """
        parts = domain.split('.')
        masked_parts = []
        
        for part in parts:
            if part:
                masked_part = "X" * len(part)
                masked_parts.append(masked_part)
            else:
                masked_parts.append("")
                
        return '.'.join(masked_parts)

    def _handle_default(self, entity: Dict[str, Any]) -> str:
        """
        Default handler for unknown entity types.

        Args:
            entity: The entity to obfuscate

        Returns:
            The obfuscated text
        """
        text = entity["text"]
        entity_type = entity["type"]
        
        # Create a generic replacement
        prefix = entity_type[:3] if len(entity_type) >= 3 else entity_type
        return f"{prefix}_{'X' * (len(text) // 2)}"