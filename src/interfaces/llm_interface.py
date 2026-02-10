"""
LLM Interface definition.
Follows Interface Segregation Principle (ISP).
Allows for multiple LLM provider implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    Any LLM provider (OpenAI, Anthropic, etc.) must implement this interface.
    
    This follows:
    - Interface Segregation Principle (small, focused interface)
    - Open/Closed Principle (open for extension, closed for modification)
    - Liskov Substitution Principle (any provider is substitutable)
    """
    
    @abstractmethod
    async def call_llm(self, prompt: str, max_tokens: int = None) -> str:
        """
        Make asynchronous call to LLM API.
        
        Args:
            prompt: The prompt to send to LLM
            max_tokens: Maximum tokens in response
            
        Returns:
            str: LLM response text
            
        Raises:
            LLMTimeoutException: If API call times out
            LLMAPIException: If API call fails
        """
        pass
    
    @abstractmethod
    def validate_response(self, response: str) -> bool:
        """
        Validate that LLM response is valid JSON.
        
        Args:
            response: LLM response text
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response from string to dictionary.
        
        Args:
            response: LLM response text
            
        Returns:
            Dict: Parsed response
            
        Raises:
            InvalidLLMResponseException: If parsing fails
        """
        pass
