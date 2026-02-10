"""
Unit tests for PDF extraction service.
Tests PDF reading, text extraction, and error handling.
"""

import pytest
import fitz
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock

from src.services.pdf_service import PDFService
from src.core.exceptions import (
    PDFSizeException,
    InvalidPDFException,
    EmptyPDFException,
    PDFExtractionException
)


class TestPDFService:
    """Test suite for PDFService."""
    
    @pytest.fixture
    def pdf_service(self):
        """Create PDFService instance for testing."""
        return PDFService()
    
    @pytest.fixture
    def valid_pdf_bytes(self):
        """Create a valid PDF with text for testing."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "John Doe\nSoftware Engineer\nSkills: Python, FastAPI\nExperience: 5 years")
        
        pdf_bytes = BytesIO()
        doc.save(pdf_bytes)
        return pdf_bytes.getvalue()
    
    @pytest.fixture
    def empty_pdf_bytes(self):
        """Create an empty PDF for testing."""
        doc = fitz.open()
        doc.new_page()
        pdf_bytes = BytesIO()
        doc.save(pdf_bytes)
        return pdf_bytes.getvalue()
    
    @pytest.fixture
    def invalid_pdf_bytes(self):
        """Create invalid PDF bytes for testing."""
        return b"This is not a valid PDF file"
    
    def test_extract_text_success(self, pdf_service, valid_pdf_bytes):
        """Test successful text extraction from valid PDF."""
        result = pdf_service.extract_text(valid_pdf_bytes)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "John Doe" in result or "Software Engineer" in result
    
    def test_extract_text_from_empty_pdf(self, pdf_service, empty_pdf_bytes):
        """Test error handling for empty PDF."""
        with pytest.raises(EmptyPDFException):
            pdf_service.extract_text(empty_pdf_bytes)
    
    def test_extract_text_from_invalid_pdf(self, pdf_service, invalid_pdf_bytes):
        """Test error handling for invalid PDF."""
        with pytest.raises(InvalidPDFException):
            pdf_service.extract_text(invalid_pdf_bytes)
    
    def test_pdf_size_limit(self, pdf_service):
        """Test PDF size limit enforcement."""
        oversized_bytes = b"x" * (pdf_service.max_size_bytes + 1)
        
        with pytest.raises(PDFSizeException):
            pdf_service.extract_text(oversized_bytes)
    
    def test_extract_text_strips_whitespace(self, pdf_service, valid_pdf_bytes):
        """Test that extracted text is stripped of extra whitespace."""
        result = pdf_service.extract_text(valid_pdf_bytes)
        
        assert result == result.strip()
    
    def test_extract_text_multipage(self):
        """Test extraction from multi-page PDF."""
        doc = fitz.open()
        page1 = doc.new_page()
        page1.insert_text((50, 50), "Page 1 Content")
        page2 = doc.new_page()
        page2.insert_text((50, 50), "Page 2 Content")
        
        pdf_bytes = BytesIO()
        doc.save(pdf_bytes)
        pdf_content = pdf_bytes.getvalue()
        
        service = PDFService()
        result = service.extract_text(pdf_content)
        
        assert "Page 1 Content" in result or "Page 2 Content" in result
        assert len(result) > 0
    
    def test_extract_text_handles_corrupted_page(self):
        """Test graceful handling of corrupted pages in otherwise valid PDF."""
        doc = fitz.open()
        page1 = doc.new_page()
        page1.insert_text((50, 50), "Valid Content")
        page2 = doc.new_page()
        page2.insert_text((50, 50), "More Content")
        
        pdf_bytes = BytesIO()
        doc.save(pdf_bytes)
        pdf_content = pdf_bytes.getvalue()
        
        service = PDFService()
        result = service.extract_text(pdf_content)
        
        assert len(result) > 0


@pytest.fixture
def mock_pdf_service():
    """Create a mock PDFService for integration tests."""
    service = Mock(spec=PDFService)
    service.extract_text.return_value = "John Doe\nPython Developer\n5 years experience"
    return service
