"""
Tests for the obfuscation module.
"""

import pytest
from unittest.mock import MagicMock, patch
import json

from stmt_obfuscator.obfuscation import Obfuscator


@pytest.fixture
def sample_document():
    """Return a sample document for testing."""
    return {
        "metadata": {
            "title": "Test Bank Statement",
            "author": "Test Bank",
            "subject": "Monthly Statement",
            "keywords": "bank,statement,test",
            "creator": "PDF Generator",
        },
        "full_text": """
        PNC Bank
        123 Main Street, Pittsburgh, PA 15222
        Phone: (800) 555-1212
        Website: www.pnc.com

        ACCOUNT STATEMENT

        Statement Period: 01/01/2025 - 01/31/2025

        CUSTOMER INFORMATION:
        John Doe
        456 Oak Avenue, Apt 789, Anytown, CA 90210
        Phone: (555) 123-4567
        Email: john.doe@example.com

        ACCOUNT SUMMARY:
        Account Number: XXXX-XXXX-XXXX-1234
        Routing Number: 123456789
        Beginning Balance: $1,234.56
        Ending Balance: $2,345.67

        TRANSACTION HISTORY:
        Date       Description                                Amount      Balance
        ----------------------------------------------------------------------------------
        01/01/2025 Beginning Balance                                     $1,234.56
        01/05/2025 Deposit                                   $500.00     $1,734.56
        01/10/2025 Withdrawal                               -$100.00     $1,634.56
        01/15/2025 Check #1001                              -$200.00     $1,434.56
        01/20/2025 Direct Deposit - ABC Company              $1,000.00   $2,434.56
        01/25/2025 Payment to Credit Card                   -$88.89      $2,345.67
        """,
        "text_blocks": [
            {
                "page": 0,
                "block_id": "block_0_0",
                "text": "PNC Bank\n123 Main Street, Pittsburgh, PA 15222\nPhone: (800) 555-1212\nWebsite: www.pnc.com",
                "bbox": [50, 50, 500, 100],
            },
            {
                "page": 0,
                "block_id": "block_0_1",
                "text": "CUSTOMER INFORMATION:\nJohn Doe\n456 Oak Avenue, Apt 789, Anytown, CA 90210\nPhone: (555) 123-4567\nEmail: john.doe@example.com",
                "bbox": [50, 150, 500, 200],
            },
        ],
        "tables": [
            {
                "page": 0,
                "table_id": "table_0_0",
                "headers": ["Date", "Description", "Amount", "Balance"],
                "rows": [
                    ["01/01/2025", "Beginning Balance", "", "$1,234.56"],
                    ["01/05/2025", "Deposit", "$500.00", "$1,734.56"],
                    ["01/10/2025", "Withdrawal", "-$100.00", "$1,634.56"],
                    ["01/15/2025", "Check #1001", "-$200.00", "$1,434.56"],
                    ["01/20/2025", "Direct Deposit - ABC Company", "$1,000.00", "$2,434.56"],
                    ["01/25/2025", "Payment to Credit Card", "-$88.89", "$2,345.67"],
                ],
                "bbox": [50, 250, 500, 400],
            }
        ],
    }


@pytest.fixture
def sample_pii_entities():
    """Return sample PII entities for testing."""
    return [
        {
            "id": "entity_0",
            "type": "PERSON_NAME",
            "text": "John Doe",
            "start": 123,
            "end": 131,
            "confidence": 0.95,
        },
        {
            "id": "entity_1",
            "type": "ADDRESS",
            "text": "456 Oak Avenue, Apt 789, Anytown, CA 90210",
            "start": 132,
            "end": 175,
            "confidence": 0.92,
        },
        {
            "id": "entity_2",
            "type": "PHONE_NUMBER",
            "text": "(555) 123-4567",
            "start": 183,
            "end": 197,
            "confidence": 0.98,
        },
        {
            "id": "entity_3",
            "type": "EMAIL",
            "text": "john.doe@example.com",
            "start": 204,
            "end": 224,
            "confidence": 0.99,
        },
        {
            "id": "entity_4",
            "type": "ACCOUNT_NUMBER",
            "text": "XXXX-XXXX-XXXX-1234",
            "start": 243,
            "end": 263,
            "confidence": 0.97,
        },
        {
            "id": "entity_5",
            "type": "ROUTING_NUMBER",
            "text": "123456789",
            "start": 282,
            "end": 291,
            "confidence": 0.96,
        },
        {
            "id": "entity_6",
            "type": "ORGANIZATION_NAME",
            "text": "PNC Bank",
            "start": 1,
            "end": 9,
            "confidence": 0.94,
        },
        {
            "id": "entity_7",
            "type": "ORGANIZATION_NAME",
            "text": "ABC Company",
            "start": 500,
            "end": 511,
            "confidence": 0.91,
        },
    ]


def test_obfuscator_initialization():
    """Test that the Obfuscator initializes correctly."""
    obfuscator = Obfuscator()
    assert obfuscator is not None
    assert obfuscator.confidence_threshold == 0.85
    assert isinstance(obfuscator.entity_handlers, dict)
    assert len(obfuscator.entity_handlers) > 0


def test_build_replacement_map(sample_pii_entities):
    """Test building the replacement map."""
    obfuscator = Obfuscator()
    obfuscator._build_replacement_map(sample_pii_entities)
    
    # Check that all entities are in the replacement map
    assert len(obfuscator.replacement_map) == len(sample_pii_entities)
    
    # Check that each entity has a replacement
    for entity in sample_pii_entities:
        assert entity["text"] in obfuscator.replacement_map
        
    # Check specific replacements
    person_name = next(e for e in sample_pii_entities if e["type"] == "PERSON_NAME")
    assert obfuscator.replacement_map[person_name["text"]] == "XXXX XXX"
    
    email = next(e for e in sample_pii_entities if e["type"] == "EMAIL")
    assert "@" in obfuscator.replacement_map[email["text"]]
    
    account_number = next(e for e in sample_pii_entities if e["type"] == "ACCOUNT_NUMBER")
    assert "1234" in obfuscator.replacement_map[account_number["text"]]


def test_obfuscate_document(sample_document, sample_pii_entities):
    """Test obfuscating a document."""
    obfuscator = Obfuscator()
    obfuscated_doc = obfuscator.obfuscate_document(sample_document, sample_pii_entities)
    
    # Check that the document was obfuscated
    assert obfuscated_doc["metadata"]["obfuscated"] is True
    assert "obfuscation_timestamp" in obfuscated_doc["metadata"]
    assert obfuscated_doc["metadata"]["entities_obfuscated"] == len(sample_pii_entities)
    
    # Check that PII was obfuscated in full text
    full_text = obfuscated_doc["full_text"]
    for entity in sample_pii_entities:
        # Skip account number that's already in obfuscated format (XXXX-XXXX-XXXX-1234)
        if entity["type"] == "ACCOUNT_NUMBER" and entity["text"].startswith("XXXX-"):
            continue
        assert entity["text"] not in full_text
    
    # Check that PII was obfuscated in text blocks
    for block in obfuscated_doc["text_blocks"]:
        for entity in sample_pii_entities:
            # Skip account number that's already in obfuscated format
            if entity["type"] == "ACCOUNT_NUMBER" and entity["text"].startswith("XXXX-"):
                continue
            assert entity["text"] not in block["text"]


def test_entity_type_handlers():
    """Test entity type-specific handlers."""
    obfuscator = Obfuscator()
    
    # Test person name handler
    person_entity = {
        "type": "PERSON_NAME",
        "text": "John Doe",
    }
    masked_person = obfuscator._handle_person_name(person_entity)
    assert masked_person == "XXXX XXX"
    assert len(masked_person) == len(person_entity["text"])
    
    # Test email handler
    email_entity = {
        "type": "EMAIL",
        "text": "john.doe@example.com",
    }
    masked_email = obfuscator._handle_email(email_entity)
    assert "@" in masked_email
    assert "." in masked_email
    assert masked_email != email_entity["text"]
    
    # Test account number handler
    account_entity = {
        "type": "ACCOUNT_NUMBER",
        "text": "1234-5678-9012-3456",
    }
    masked_account = obfuscator._handle_account_number(account_entity)
    assert "3456" in masked_account
    assert masked_account.startswith("XXXX")
    
    # Test phone number handler
    phone_entity = {
        "type": "PHONE_NUMBER",
        "text": "(555) 123-4567",
    }
    masked_phone = obfuscator._handle_phone_number(phone_entity)
    assert "(" in masked_phone
    assert ")" in masked_phone
    assert "-" in masked_phone
    assert masked_phone != phone_entity["text"]


def test_financial_integrity_checks(sample_document):
    """Test financial integrity checks."""
    obfuscator = Obfuscator()
    
    # Extract financial data
    obfuscator._extract_financial_data(sample_document)
    
    # Check that beginning and ending balances were extracted
    assert "beginning_balance" in obfuscator.financial_integrity_checks
    assert obfuscator.financial_integrity_checks["beginning_balance"] == 1234.56
    
    assert "ending_balance" in obfuscator.financial_integrity_checks
    assert obfuscator.financial_integrity_checks["ending_balance"] == 2345.67
    
    # Check that transactions were extracted
    assert "transactions" in obfuscator.financial_integrity_checks
    assert len(obfuscator.financial_integrity_checks["transactions"]) == 6


def test_normalize_text():
    """Test text normalization for entity grouping."""
    obfuscator = Obfuscator()
    
    # Test phone number normalization
    phone1 = "(555) 123-4567"
    phone2 = "555-123-4567"
    phone3 = "5551234567"
    
    assert obfuscator._normalize_text(phone1, "PHONE_NUMBER") == \
           obfuscator._normalize_text(phone2, "PHONE_NUMBER") == \
           obfuscator._normalize_text(phone3, "PHONE_NUMBER")
    
    # Test person name normalization
    name1 = "John Doe"
    name2 = "john doe"
    name3 = "Mr. John Doe"
    
    assert obfuscator._normalize_text(name1, "PERSON_NAME") == \
           obfuscator._normalize_text(name2, "PERSON_NAME")
    
    assert obfuscator._normalize_text(name3, "PERSON_NAME") == \
           obfuscator._normalize_text(name1, "PERSON_NAME")


def test_group_similar_entities():
    """Test grouping similar entities."""
    obfuscator = Obfuscator()
    
    entities = [
        {
            "type": "PERSON_NAME",
            "text": "John Doe",
            "confidence": 0.95,
        },
        {
            "type": "PERSON_NAME",
            "text": "john doe",
            "confidence": 0.92,
        },
        {
            "type": "PERSON_NAME",
            "text": "Mr. John Doe",
            "confidence": 0.90,
        },
        {
            "type": "PHONE_NUMBER",
            "text": "(555) 123-4567",
            "confidence": 0.98,
        },
        {
            "type": "PHONE_NUMBER",
            "text": "555-123-4567",
            "confidence": 0.97,
        },
    ]
    
    groups = obfuscator._group_similar_entities(entities)
    
    # Should have 2 groups: one for John Doe and one for the phone number
    assert len(groups) == 2
    
    # Check that all John Doe variants are in the same group
    person_group = next(g for g in groups.values() if g[0]["type"] == "PERSON_NAME")
    assert len(person_group) == 3
    
    # Check that all phone number variants are in the same group
    phone_group = next(g for g in groups.values() if g[0]["type"] == "PHONE_NUMBER")
    assert len(phone_group) == 2


def test_parse_amount():
    """Test parsing financial amounts."""
    obfuscator = Obfuscator()
    
    assert obfuscator._parse_amount("$1,234.56") == 1234.56
    assert obfuscator._parse_amount("1,234.56") == 1234.56
    assert obfuscator._parse_amount("-$100.00") == -100.00
    assert obfuscator._parse_amount("$0.00") == 0.0
    assert obfuscator._parse_amount("invalid") == 0.0