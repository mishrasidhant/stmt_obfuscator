#!/usr/bin/env python3
"""
PII Detection Proof-of-Concept using Ollama with local LLMs

This script demonstrates PII detection in bank statements using Ollama with local LLMs.
It connects to Ollama API, sends prompts to detect PII, and parses the responses.
"""

import argparse
import json
import re
import requests
import sys
from typing import Dict, List, Optional, Tuple, Union


class OllamaPIIDetector:
    """
    A class for detecting PII in bank statements using Ollama with local LLMs.
    """

    def __init__(self, model: str = "mistral:latest", host: str = "http://localhost:11434"):
        """
        Initialize the OllamaPIIDetector.

        Args:
            model: The name of the Ollama model to use (default: "mistral:7b-instruct")
            host: The Ollama API host URL (default: "http://localhost:11434")
        """
        self.model = model
        self.host = host
        self.api_url = f"{host}/api/generate"
        
        # Test connection to Ollama
        self._test_connection()

    def _test_connection(self) -> None:
        """
        Test the connection to Ollama API.
        
        Raises:
            ConnectionError: If the connection to Ollama API fails
        """
        try:
            response = requests.get(f"{self.host}/api/tags")
            if response.status_code != 200:
                raise ConnectionError(f"Failed to connect to Ollama API: {response.status_code}")
            
            # Check if the model is available
            models = response.json().get("models", [])
            model_names = [model.get("name") for model in models]
            
            if self.model not in model_names:
                print(f"Warning: Model '{self.model}' not found in available models: {model_names}")
                print(f"You may need to pull the model using: ollama pull {self.model}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama API: {e}")

    def detect_pii(self, text: str) -> Dict:
        """
        Detect PII in the given text using Ollama.

        Args:
            text: The text to analyze for PII

        Returns:
            A dictionary containing the detected PII entities
        """
        prompt = self._create_prompt(text)
        response = self._send_to_ollama(prompt)
        pii_entities = self._parse_response(response)
        
        return pii_entities

    def _create_prompt(self, text: str) -> str:
        """
        Create a prompt for PII detection.

        Args:
            text: The text to analyze for PII

        Returns:
            A formatted prompt for the LLM
        """
        return f"""
You are a specialized PII (Personally Identifiable Information) detection system for bank statements.

Analyze the following bank statement text and identify ALL instances of PII.
For each PII instance found, provide:
1. The type of PII (using EXACTLY the types listed below)
2. The exact text that contains the PII
3. The start and end position of the PII in the text (character index)

IMPORTANT: Use ONLY these exact PII type names:
- PERSON_NAME (for individual names)
- ORGANIZATION_NAME (for bank names, company names)
- ADDRESS (for physical addresses)
- PHONE_NUMBER (for phone numbers)
- EMAIL (for email addresses)
- ACCOUNT_NUMBER (for bank account numbers)
- ROUTING_NUMBER (for bank routing numbers)
- WEBSITE (for website URLs)

Return your findings in a structured JSON format like this:
{{
  "entities": [
    {{
      "type": "PERSON_NAME",
      "text": "John Doe",
      "start": 10,
      "end": 18
    }},
    {{
      "type": "ACCOUNT_NUMBER",
      "text": "1234567890",
      "start": 42,
      "end": 52
    }}
  ]
}}

Only include actual PII in your response. Do not include transaction amounts, dates, or other non-PII information.
Be precise with the start and end positions - they should correspond exactly to the character positions in the text.

Bank statement text:
{text}
"""

    def _send_to_ollama(self, prompt: str) -> str:
        """
        Send a prompt to Ollama API and get the response.

        Args:
            prompt: The prompt to send to Ollama

        Returns:
            The response from Ollama

        Raises:
            ConnectionError: If the request to Ollama API fails
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to send prompt to Ollama: {e}")

    def _parse_response(self, response: str) -> Dict:
        """
        Parse the response from Ollama to extract PII entities.

        Args:
            response: The response from Ollama

        Returns:
            A dictionary containing the detected PII entities
        """
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r'({[\s\S]*})', response)
            if json_match:
                json_str = json_match.group(1)
            else:
                return {"entities": []}
        
        try:
            # Clean up the JSON string
            json_str = json_str.strip()
            result = json.loads(json_str)
            
            # Ensure the result has the expected structure
            if "entities" not in result:
                result = {"entities": []}
            
            return result
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from response: {response}")
            return {"entities": []}


def main():
    """
    Main function to run the PII detector from the command line.
    """
    parser = argparse.ArgumentParser(description="Detect PII in bank statements using Ollama")
    parser.add_argument("--model", default="mistral:7b-instruct", help="Ollama model to use")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama API host URL")
    parser.add_argument("--input", help="Input text file containing bank statement")
    
    args = parser.parse_args()
    
    try:
        detector = OllamaPIIDetector(model=args.model, host=args.host)
        
        if args.input:
            with open(args.input, 'r') as f:
                text = f.read()
        else:
            print("Reading from stdin...")
            text = sys.stdin.read()
        
        result = detector.detect_pii(text)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()