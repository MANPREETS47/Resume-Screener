"""
Unit tests for LLM service.
Tests LLM API communication and response parsing with mocked API.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from src.services.llm_service import GroqLLMProvider
from src.interfaces.llm_interface import LLMProvider
from src.core.exceptions import (
    LLMAPIException,
    LLMTimeoutException,
    InvalidLLMResponseException,
    LLMRetryException
)


class TestGroqLLMProvider:
    """Test suite for Groq LLM Provider."""
    
    @pytest.fixture
    def llm_provider(self):
        """Create LLMProvider instance for testing."""
        return GroqLLMProvider()
    
    @pytest.fixture
    def valid_json_response(self):
        """Sample valid JSON response from LLM."""
        return json.dumps({
            "candidate_name": "John Doe",
            "skills": ["Python", "FastAPI", "Docker"],
            "experience_years": 5,
            "education": ["BS Computer Science - MIT"],
            "projects": ["Resume Screener - AI tool"],
            "summary": "Experienced backend engineer",
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Kubernetes"],
            "matching_score": 78
        })
    
    def test_llm_provider_implements_interface(self, llm_provider):
        """Test that Groq provider implements LLMProvider interface."""
        assert isinstance(llm_provider, LLMProvider)
        assert hasattr(llm_provider, 'call_llm')
        assert hasattr(llm_provider, 'validate_response')
        assert hasattr(llm_provider, 'parse_response')
    
    def test_validate_response_valid_json(self, llm_provider, valid_json_response):
        """Test validation of valid JSON response."""
        assert llm_provider.validate_response(valid_json_response) is True
    
    def test_validate_response_invalid_json(self, llm_provider):
        """Test validation of invalid JSON response."""
        invalid_response = "This is not JSON {invalid:"
        assert llm_provider.validate_response(invalid_response) is False
    
    def test_parse_response_valid_json(self, llm_provider, valid_json_response):
        """Test parsing of valid JSON response."""
        result = llm_provider.parse_response(valid_json_response)
        
        assert isinstance(result, dict)
        assert result["candidate_name"] == "John Doe"
        assert "Python" in result["skills"]
        assert result["experience_years"] == 5
        assert result["matching_score"] == 78
        assert "Python" in result["matched_skills"]
        assert "Kubernetes" in result["missing_skills"]
    
    def test_parse_response_invalid_json(self, llm_provider):
        """Test error handling for invalid JSON response."""
        invalid_response = "This is not JSON"
        
        with pytest.raises(InvalidLLMResponseException):
            llm_provider.parse_response(invalid_response)
    
    def test_parse_response_with_markdown(self, llm_provider):
        """Test parsing JSON response wrapped with markdown."""
        markdown_response = '''```json
        {
            "candidate_name": "Jane Smith",
            "skills": ["Python"],
            "experience_years": 3,
            "education": [],
            "projects": [],
            "summary": "Developer",
            "matched_skills": ["Python"],
            "missing_skills": [],
            "matching_score": 65
        }
        ```'''
        
        # This should extract the JSON from markdown
        result = llm_provider.parse_response(markdown_response)
        assert result["candidate_name"] == "Jane Smith"
        assert result["matching_score"] == 65
    
    @pytest.mark.asyncio
    async def test_call_llm_with_mock_api(self, llm_provider, valid_json_response):
        """Test LLM call with mocked API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": valid_json_response
                    }
                }
            ]
        }
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await llm_provider.call_llm("Test prompt")
            assert result == valid_json_response
    
    @pytest.mark.asyncio
    async def test_call_llm_api_authentication_error(self, llm_provider):
        """Test handling of API authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(LLMAPIException):
                await llm_provider.call_llm("Test prompt")
    
    @pytest.mark.asyncio
    async def test_call_llm_timeout(self, llm_provider):
        """Test handling of API timeout."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post.side_effect = asyncio.TimeoutError()
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(LLMTimeoutException):
                await llm_provider.call_llm("Test prompt")
    
    def test_llm_provider_configuration(self, llm_provider):
        """Test that provider is configured with settings."""
        assert llm_provider.api_key is not None
        assert llm_provider.model is not None
        assert llm_provider.temperature >= 0
        assert llm_provider.max_tokens > 0
        assert llm_provider.timeout > 0
        assert llm_provider.max_retries > 0
    
    def test_llm_provider_model_override(self):
        """Test that model can be overridden via constructor."""
        provider = GroqLLMProvider(model_override="llama-3.1-8b-instant")
        assert provider.model == "llama-3.1-8b-instant"
    
    def test_groq_api_base_url(self, llm_provider):
        """Test that the API base URL points to Groq."""
        assert "groq.com" in llm_provider.api_base_url


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLMProvider for integration tests."""
    provider = Mock(spec=LLMProvider)
    provider.call_llm = AsyncMock(return_value=json.dumps({
        "candidate_name": "Test User",
        "skills": ["Test"],
        "experience_years": 1,
        "education": [],
        "projects": [],
        "summary": "Test summary",
        "matched_skills": ["Test"],
        "missing_skills": [],
        "matching_score": 50
    }))
    provider.validate_response.return_value = True
    provider.parse_response.return_value = {
        "candidate_name": "Test User",
        "skills": ["Test"],
        "experience_years": 1,
        "education": [],
        "projects": [],
        "summary": "Test summary",
        "matched_skills": ["Test"],
        "missing_skills": [],
        "matching_score": 50
    }
    return provider
