"""
Custom exception classes for Resume Screener application.
Provides clear error handling and logging.
"""


class ResumeScreenerException(Exception):
    """Base exception for Resume Screener application."""
    
    def __init__(self, message: str, details: str = None):
        """
        Initialize exception.
        
        Args:
            message: User-friendly error message
            details: Additional technical details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class PDFExtractionException(ResumeScreenerException):
    """Exception raised during PDF extraction."""
    pass


class InvalidPDFException(PDFExtractionException):
    """Exception raised when PDF file is invalid or corrupted."""
    pass


class EmptyPDFException(PDFExtractionException):
    """Exception raised when PDF contains no extractable text."""
    pass


class PDFSizeException(PDFExtractionException):
    """Exception raised when PDF exceeds size limit."""
    pass


class LLMException(ResumeScreenerException):
    """Exception raised during LLM operations."""
    pass


class LLMAPIException(LLMException):
    """Exception raised during LLM API communication."""
    pass


class LLMTimeoutException(LLMException):
    """Exception raised when LLM API call times out."""
    pass


class InvalidLLMResponseException(LLMException):
    """Exception raised when LLM returns invalid JSON."""
    pass


class LLMRetryException(LLMException):
    """Exception raised when LLM retries are exhausted."""
    pass


class ConfigurationException(ResumeScreenerException):
    """Exception raised when configuration is invalid."""
    pass
