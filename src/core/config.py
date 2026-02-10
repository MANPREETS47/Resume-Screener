"""
Configuration management for Resume Screener application.
Uses environment variables with pydantic for validation.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_TITLE: str = "Resume Screener API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Gemini LLM Configuration
    GEMINI_API_KEY: str
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT: int = 30
    LLM_MAX_RETRIES: int = 3
    
    # PDF Configuration
    MAX_PDF_SIZE_MB: int = 10
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        """Pydantic config for Settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached singleton).
    
    Returns:
        Settings: Application configuration
    """
    return Settings()
