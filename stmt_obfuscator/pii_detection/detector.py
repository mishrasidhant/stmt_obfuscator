"""
PII Detection module for the PDF Bank Statement Obfuscator.

This module handles PII detection using Ollama with local LLMs.
"""

import json
import logging
import re
import sys
from typing import Dict, List, Any, Optional

import requests

from stmt_obfuscator.config import OLLAMA_HOST, DEFAULT_MODEL, CONFIDENCE_THRESHOLD


logger = logging.getLogger(__name__)


class PIIDetector:
    """PII Detector for identifying personally identifiable information in text."""

    def __init__(self, model: str = DEFAULT_MODEL, host: str = OLLAMA_HOST):
        """
        Initialize the PII detector.

        Args:
            model: The Ollama model to use (default: from config)
            host: The Ollama API host URL (default: from config)
        """
        self.model = model
        self.host = host
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        
        logger.info(f"Initialized PII detector with model: {model}")

    def detect_pii(self, text: str, rag_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detect PII in the given text using Ollama.

        Args:
            text: The text to analyze for PII
            rag_context: Optional RAG context to enhance detection

        Returns:
            A dictionary containing the detected PII entities
        """
        prompt = self._create_prompt(text, rag_context)
        response = self._send_to_ollama(prompt)
        pii_entities = self._parse_response(response)
        
        logger.info(f"Detected {len(pii_entities['entities'])} PII entities")
        return pii_entities

    def _create_prompt(self, text: str, rag_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a prompt for PII detection.

        Args:
            text: The text to analyze for PII
            rag_context: Optional RAG context to enhance detection

        Returns:
            A formatted prompt for the LLM
        """
        # Base prompt
        prompt = f"""
You are a specialized PII (Personally Identifiable Information) detection system for bank statements.

Analyze the following bank statement text and identify ALL instances of PII. 
For each PII instance found, provide:
1. The type of PII (e.g., PERSON_NAME, ADDRESS, ACCOUNT_NUMBER, PHONE_NUMBER, EMAIL, etc.)
2. The exact text that contains the PII
3. The start and end position of the PII in the text (character index)

Return your findings in a structured JSON format like this:
{{
  "entities": [
    {{
      "type": "PERSON_NAME",
      "text": "John Doe",
      "start": 10,
      "end": 18,
      "confidence": 0.95
    }},
    {{
      "type": "ACCOUNT_NUMBER",
      "text": "1234567890",
      "start": 42,
      "end": 52,
      "confidence": 0.98
    }}
  ]
}}

Only include actual PII in your response. Do not include transaction amounts, dates, or other non-PII information.
"""

        # Add RAG context if provided
        if rag_context:
            prompt += "\n\nAdditional context for detection:\n"
            for key, value in rag_context.items():
                prompt += f"{key}: {value}\n"

        # Add the text to analyze
        prompt += f"\nBank statement text:\n{text}"
        
        return prompt

    def _send_to_ollama(self, prompt: str) -> str:
        """
        Send a prompt to Ollama and get the response.

        Args:
            prompt: The prompt to send to Ollama

        Returns:
            The response from Ollama

        Raises:
            Exception: If there is an error communicating with Ollama
        """
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )
            
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Ollama: {e}")
            raise Exception(f"Error communicating with Ollama: {e}")

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the response from Ollama to extract PII entities.

        Args:
            response: The response from Ollama

        Returns:
            A dictionary containing the detected PII entities
        """
        try:
            # Extract JSON from the response
            json_match = re.search(r'({[\s\S]*})', response)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                # Filter entities by confidence threshold
                if "entities" in data:
                    data["entities"] = [
                        entity for entity in data["entities"]
                        if entity.get("confidence", 1.0) >= self.confidence_threshold
                    ]
                
                return data
            else:
                logger.warning("No JSON found in response")
                return {"entities": []}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            return {"entities": []}
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            return {"entities": []}