"""
LLM Service implementation using Google Gemini API.
"""

import json
import logging
from google import genai
from google.genai.types import HarmCategory, HarmBlockThreshold
from typing import Dict, Any

from src.interfaces.llm_interface import LLMProvider
from src.core.config import get_settings
from src.core.exceptions import (
    LLMAPIException,
    InvalidLLMResponseException,
    LLMException
)

logger = logging.getLogger(__name__)


class GeminiLLMProvider(LLMProvider):
    """
    Gemini LLM Provider implementation using google-generativeai SDK.
    """
    
    def __init__(self, model_override: str = None):
        """Initialize Provider."""
        self.settings = get_settings()
        self.api_key = self.settings.GEMINI_API_KEY
        self.model_name = "gemini-3.0-flash"
        
        # Configure the SDK
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set in settings")
        else:
            self.client = genai.Client(api_key=self.api_key)
            
        logger.info(f"Gemini LLM Provider initialized with model: {self.model_name}")
        
    async def call_llm(self, prompt: str, max_tokens: int = None) -> str:
        """
        Call Gemini API.
        Uses synchronous SDK method wrapped in async default (or just sync if okay).
        For simplicity and reliability, we run it directly.
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
            )
            
            if not response.text:
                raise LLMAPIException(
                    message="Empty response from Gemini", 
                    details=str(response.prompt_feedback)
                )
                
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API Error: {str(e)}")
            # Check if it's a block
            if "finish_reason" in str(e).lower():
                 raise LLMAPIException(message="Gemini blocked content", details=str(e))
                 
            raise LLMAPIException(message="Failed to call Gemini API", details=str(e))

    def validate_response(self, response: str) -> bool:
        """Validate JSON response."""
        try:
            json.loads(response.strip())
            return True
        except json.JSONDecodeError:
            return False
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response."""
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {response[:100]}... Error: {e}")
            raise InvalidLLMResponseException(message="Invalid JSON from Gemini", details=str(e))
