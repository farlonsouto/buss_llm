"""
LLM Processing Engine for Transit Intelligence.

This module handles the interaction with local LLM instances (via Ollama)
and ensures structured output using prompt engineering and JSON validation.
"""

import json
import logging

import httpx

from .schemas import FeedbackAnalysis, TransitFeedbackRequest

logger = logging.getLogger(__name__)


class LLMProcessor:
    """
    Orchestrates the transformation of raw text into structured transit information.
    """

    def __init__(self, base_url: str = "http://docker.internal", model: str = "llama3"):
        """
        Initializes the processor with local LLM connectivity.

        Args:
            base_url: The endpoint where Ollama is served.
            model: The specific local model to invoke (e.g., llama3, mistral).
        """
        self.base_url = base_url
        self.model = model
        self.api_endpoint = f"{base_url}/api/generate"

    # Inside backend/src/processor.py
    def _generate_system_prompt(self) -> str:
        """ Generates a system prompt for the LLM. Following the best practices of prompt engineering, the prompt shall
        establish a persona and constraints. Furthermore, it shall be concise and focused. """
        return (
            "You are a strict JSON generator for a transit engine. "
            "Analyze the user feedback and output ONLY valid JSON. "
            "Do not include any conversational text, headers, or markdown formatting. "
            "Required format: "
            '{"category": "string", "sentiment": "string", "priority": integer, "extracted_entities": ["string"]}'
        )

    async def analyze_text(self, request: TransitFeedbackRequest) -> FeedbackAnalysis:
        """
        Sends raw text to the local LLM and parses the structured response.

        Args:
            request: The validated feedback request object.

        Returns:
            A FeedbackAnalysis object validated against the project schema.

        Raises:
            RuntimeError: If the LLM fails to return valid JSON or is unreachable.
        """
        payload = {
            "model": self.model,
            "prompt": f"Text to analyze: {request.raw_text}",
            "system": self._generate_system_prompt(),
            "stream": False,
            "format": "json"  # Forces Ollama to output valid JSON
        }

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(self.api_endpoint, json=payload)
                response.raise_for_status()

                result = response.json()
                raw_response_text = result.get("response", "{}")

                # Parse the raw string from LLM into a dictionary
                analysis_data = json.loads(raw_response_text)

                logger.info(f"LLM successfully processed text. Category: {analysis_data.get('category')}")

                # Validation happens here: Pydantic will raise an error if JSON is malformed
                return FeedbackAnalysis(**analysis_data)

        except httpx.ConnectError:
            logger.error(f"Could not connect to Ollama at {self.base_url}. Is it running?")
            raise RuntimeError("LLM Service Unreachable")
        except json.JSONDecodeError:
            logger.error("LLM returned invalid JSON.")
            raise RuntimeError("Internal Model Processing Error")
        except Exception as e:
            logger.error(f"Unexpected error in LLMProcessor: {str(e)}")
            raise
