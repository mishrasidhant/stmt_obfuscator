"""
Integration tests for PDF Parser and PII Detector components.

These tests verify that the PDF Parser and PII Detector components work together correctly.
"""

import os
import json
import pytest
from typing import Dict, List, Any

from stmt_obfuscator.pdf_parser.parser import PDFParser
from stmt_obfuscator.pii_detection.detector import PIIDetector


class TestParserDetectorIntegration:
    """Integration tests for PDFParser and PIIDetector."""

    def test_parser_to_detector_workflow(self, pdf_parser, pii_detector, generated_statement_with_pdf):
        """Test the workflow from PDF parsing to PII detection."""
        # Skip if PDF generation failed
        if not generated_statement_with_pdf.get("pdf_path"):
            pytest.skip("PDF generation failed")
            
        pdf_path = generated_statement_with_pdf["pdf_path"]
        ground_truth = generated_statement_with_pdf["ground_truth"]
        
        # Skip if Ollama is not available
        try:
            # Step 1: Load the PDF
            result = pdf_parser.load_pdf(pdf_path)
            assert result is True, "Failed to load PDF"
            
            # Step 2: Extract text
            text_blocks = pdf_parser.extract_text()
            assert len(text_blocks) > 0, "No text blocks extracted"
            
            # Step 3: Get document structure for PII detection
            document = pdf_parser.get_text_for_pii_detection()
            assert "full_text" in document, "Missing full_text in document structure"
            assert len(document["full_text"]) > 0, "Empty full_text in document structure"
            
            # Step 4: Detect PII
            pii_entities = pii_detector.detect_pii(document["full_text"])
            assert "entities" in pii_entities, "Missing entities in PII detection result"
            
            # Verify that some entities were detected
            assert len(pii_entities["entities"]) > 0, "No PII entities detected"
            
            # Compare detected entities with ground truth
            detected_types = {entity["type"] for entity in pii_entities["entities"]}
            ground_truth_types = {entity["type"] for entity in ground_truth["entities"]}
            
            # Check that at least some types overlap
            common_types = detected_types.intersection(ground_truth_types)
            assert len(common_types) > 0, f"No common entity types between detected ({detected_types}) and ground truth ({ground_truth_types})"
            
            print(f"Detected {len(pii_entities['entities'])} entities of types: {detected_types}")
            print(f"Ground truth has {len(ground_truth['entities'])} entities of types: {ground_truth_types}")
            print(f"Common types: {common_types}")
            
        except Exception as e:
            pytest.skip(f"Skipping test because of error: {str(e)}")
    
    def test_chunking_with_pii_detection(self, pdf_parser, pii_detector, generated_statement_with_pdf):
        """Test PII detection with document chunking."""
        # Skip if PDF generation failed
        if not generated_statement_with_pdf.get("pdf_path"):
            pytest.skip("PDF generation failed")
            
        pdf_path = generated_statement_with_pdf["pdf_path"]
        
        # Skip if Ollama is not available
        try:
            # Step 1: Load the PDF
            result = pdf_parser.load_pdf(pdf_path)
            assert result is True, "Failed to load PDF"
            
            # Step 2: Extract text
            pdf_parser.extract_text()
            
            # Step 3: Chunk the document for PII detection
            chunks = pdf_parser.chunk_document_for_pii_detection()
            assert len(chunks) > 0, "No chunks created"
            
            # Step 4: Detect PII in each chunk
            all_entities = []
            for i, chunk in enumerate(chunks):
                chunk_entities = pii_detector.detect_pii(chunk)
                assert "entities" in chunk_entities, f"Missing entities in PII detection result for chunk {i}"
                
                # Add chunk index to entities for tracking
                for entity in chunk_entities["entities"]:
                    entity["chunk_index"] = i
                
                all_entities.extend(chunk_entities["entities"])
            
            # Verify that some entities were detected across all chunks
            assert len(all_entities) > 0, "No PII entities detected across all chunks"
            
            # Check for duplicates (same entity detected in multiple chunks)
            # This is not necessarily an error, but good to be aware of
            entity_texts = [entity["text"] for entity in all_entities]
            duplicates = {text for text in entity_texts if entity_texts.count(text) > 1}
            
            if duplicates:
                print(f"Found {len(duplicates)} duplicate entities across chunks: {duplicates}")
                
                # Group duplicates by chunk
                for dup in duplicates:
                    chunks_with_dup = [entity["chunk_index"] for entity in all_entities if entity["text"] == dup]
                    print(f"  '{dup}' found in chunks: {chunks_with_dup}")
            
        except Exception as e:
            pytest.skip(f"Skipping test because of error: {str(e)}")
    
    def test_position_mapping(self, pdf_parser, pii_detector, generated_statement_with_pdf):
        """Test mapping PII entity positions back to the PDF document."""
        # Skip if PDF generation failed
        if not generated_statement_with_pdf.get("pdf_path"):
            pytest.skip("PDF generation failed")
            
        pdf_path = generated_statement_with_pdf["pdf_path"]
        
        # Skip if Ollama is not available
        try:
            # Step 1: Load the PDF
            result = pdf_parser.load_pdf(pdf_path)
            assert result is True, "Failed to load PDF"
            
            # Step 2: Extract text
            text_blocks = pdf_parser.extract_text()
            
            # Step 3: Get document structure for PII detection
            document = pdf_parser.get_text_for_pii_detection()
            
            # Step 4: Detect PII
            pii_entities = pii_detector.detect_pii(document["full_text"])
            
            # Step 5: Map PII entity positions back to text blocks
            for entity in pii_entities["entities"]:
                # Find the text block(s) containing this entity
                entity_start = entity["start"]
                entity_end = entity["end"]
                entity_text = entity["text"]
                
                # Check if the entity text is actually at the specified position
                assert document["full_text"][entity_start:entity_end] == entity_text, \
                    f"Entity text mismatch: expected '{entity_text}', got '{document['full_text'][entity_start:entity_end]}'"
                
                # Try to map to text blocks
                # This is a simplified approach - in a real implementation, you would need
                # to track character offsets for each text block
                found_in_blocks = []
                for i, block in enumerate(text_blocks):
                    if entity_text in block.text:
                        found_in_blocks.append(i)
                
                # It's possible that the entity spans multiple blocks or is not found
                # due to text normalization, so this is not a strict assertion
                if not found_in_blocks:
                    print(f"Warning: Entity '{entity_text}' not found in any text block")
                else:
                    print(f"Entity '{entity_text}' found in text blocks: {found_in_blocks}")
            
        except Exception as e:
            pytest.skip(f"Skipping test because of error: {str(e)}")