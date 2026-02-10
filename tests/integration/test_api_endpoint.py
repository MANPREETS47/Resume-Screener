"""
Integration tests for Resume Screening API endpoint.
Tests the complete pipeline with mocked LLM service.
"""

import pytest
import json
from io import BytesIO
from unittest.mock import Mock, AsyncMock, patch
import fitz

from fastapi.testclient import TestClient
from src.main import app
from src.services.pdf_service import PDFService
from src.services.resume_service import ResumeScreeningService
from src.services.llm_service import GroqLLMProvider
from src.interfaces.llm_interface import LLMProvider
from src.models.response_models import ResumeScreeningResponse
from src.api.resume_routes import get_resume_service


# ── Mock service for deterministic testing ──
def _create_mock_resume_service():
    """Create a ResumeScreeningService with mocked LLM provider."""
    mock_pdf_service = Mock(spec=PDFService)
    mock_pdf_service.extract_text.return_value = "John Doe, Python Developer, 5 years experience"
    
    mock_llm_provider = Mock(spec=LLMProvider)
    mock_llm_provider.call_llm = AsyncMock(return_value=json.dumps({
        "candidate_name": "John Doe",
        "skills": ["Python", "FastAPI"],
        "experience_years": 5,
        "education": ["BS Computer Science"],
        "projects": ["Some Project"],
        "summary": "Experienced developer",
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": ["Docker"],
        "matching_score": 75
    }))
    mock_llm_provider.validate_response.return_value = True
    mock_llm_provider.parse_response.return_value = {
        "candidate_name": "John Doe",
        "skills": ["Python", "FastAPI"],
        "experience_years": 5,
        "education": ["BS Computer Science"],
        "projects": ["Some Project"],
        "summary": "Experienced developer",
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": ["Docker"],
        "matching_score": 75
    }
    
    return ResumeScreeningService(
        pdf_service=mock_pdf_service,
        llm_provider=mock_llm_provider
    )


@pytest.fixture
def client():
    """Create test client with mocked resume service for deterministic results."""
    mock_service = _create_mock_resume_service()
    app.dependency_overrides[get_resume_service] = lambda: mock_service
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def raw_client():
    """Create test client WITHOUT mocked service (for validation-only tests)."""
    return TestClient(app)


@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), 
        "John Doe\n"
        "Email: john@example.com\n"
        "Phone: 123-456-7890\n\n"
        "EXPERIENCE:\n"
        "Senior Software Engineer\n"
        "Tech Company Inc (2020-2024)\n"
        "5+ years of experience in Python and FastAPI\n\n"
        "EDUCATION:\n"
        "BS Computer Science\n"
        "Stanford University\n\n"
        "SKILLS:\n"
        "Python, FastAPI, Docker, PostgreSQL, AWS"
    )
    
    pdf_bytes = BytesIO()
    doc.save(pdf_bytes)
    return pdf_bytes.getvalue()


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return "We are looking for a Python developer with 5+ years experience in backend development and FastAPI expertise."


class TestResumeScreeningEndpoint:
    """Test suite for resume screening API endpoint."""
    
    def test_screen_resume_success(self, client, sample_pdf, sample_job_description):
        """Test successful resume screening request with mocked LLM."""
        response = client.post(
            "/api/v1/screen-resume",
            files={"resume_file": ("resume.pdf", sample_pdf, "application/pdf")},
            data={"job_description": sample_job_description}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["candidate_name"] == "John Doe"
        assert data["matching_score"] == 75
        assert "Python" in data["matched_skills"]
        assert "Docker" in data["missing_skills"]
    
    def test_screen_resume_missing_file(self, raw_client, sample_job_description):
        """Test error handling for missing PDF file."""
        response = raw_client.post(
            "/api/v1/screen-resume",
            data={"job_description": sample_job_description}
        )
        
        assert response.status_code == 422  # Unprocessable entity
    
    def test_screen_resume_missing_job_description(self, raw_client, sample_pdf):
        """Test error handling for missing job description."""
        response = raw_client.post(
            "/api/v1/screen-resume",
            files={"resume_file": ("resume.pdf", sample_pdf, "application/pdf")}
        )
        
        assert response.status_code == 422
    
    def test_screen_resume_invalid_file_type(self, raw_client, sample_job_description):
        """Test error handling for invalid file type."""
        invalid_file = b"This is not a PDF"
        
        response = raw_client.post(
            "/api/v1/screen-resume",
            files={"resume_file": ("file.txt", invalid_file, "text/plain")},
            data={"job_description": sample_job_description}
        )
        
        assert response.status_code == 400
    
    def test_screen_resume_empty_file(self, raw_client, sample_job_description):
        """Test error handling for empty file."""
        response = raw_client.post(
            "/api/v1/screen-resume",
            files={"resume_file": ("resume.pdf", b"", "application/pdf")},
            data={"job_description": sample_job_description}
        )
        
        assert response.status_code == 400
    
    def test_screen_resume_empty_job_description(self, raw_client, sample_pdf):
        """Test error handling for empty job description."""
        response = raw_client.post(
            "/api/v1/screen-resume",
            files={"resume_file": ("resume.pdf", sample_pdf, "application/pdf")},
            data={"job_description": ""}
        )
        
        assert response.status_code == 422
    
    def test_screen_resume_short_job_description(self, raw_client, sample_pdf):
        """Test error handling for too short job description."""
        response = raw_client.post(
            "/api/v1/screen-resume",
            files={"resume_file": ("resume.pdf", sample_pdf, "application/pdf")},
            data={"job_description": "short"}
        )
        
        assert response.status_code == 422
    
    def test_health_check(self, raw_client):
        """Test health check endpoint."""
        response = raw_client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_root_endpoint(self, raw_client):
        """Test root endpoint returns API information."""
        response = raw_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestResumeScreeningServiceIntegration:
    """Integration tests for ResumeScreeningService."""
    
    @pytest.mark.asyncio
    async def test_resume_screening_service_with_mocks(self, sample_pdf, sample_job_description):
        """Test ResumeScreeningService with mocked dependencies."""
        # Create mock services
        mock_pdf_service = Mock(spec=PDFService)
        mock_pdf_service.extract_text.return_value = "John Doe, Python Developer, 5 years experience"
        
        mock_llm_provider = Mock(spec=LLMProvider)
        mock_llm_provider.call_llm = AsyncMock(return_value=json.dumps({
            "candidate_name": "John Doe",
            "skills": ["Python", "FastAPI"],
            "experience_years": 5,
            "education": ["BS Computer Science"],
            "projects": ["Some Project"],
            "summary": "Experienced developer",
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Docker"],
            "matching_score": 80
        }))
        mock_llm_provider.validate_response.return_value = True
        mock_llm_provider.parse_response.return_value = {
            "candidate_name": "John Doe",
            "skills": ["Python", "FastAPI"],
            "experience_years": 5,
            "education": ["BS Computer Science"],
            "projects": ["Some Project"],
            "summary": "Experienced developer",
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Docker"],
            "matching_score": 80
        }
        
        # Create service with mocks
        service = ResumeScreeningService(
            pdf_service=mock_pdf_service,
            llm_provider=mock_llm_provider
        )
        
        # Call service
        response = await service.screen_resume(sample_pdf, sample_job_description)
        
        # Verify response
        assert isinstance(response, ResumeScreeningResponse)
        assert response.candidate_name == "John Doe"
        assert response.experience_years == 5
        assert len(response.skills) > 0
        assert response.matching_score == 80
        assert "Python" in response.matched_skills
        assert "Docker" in response.missing_skills
        assert response.confidence_score is not None
        assert response.processing_time_ms is not None
