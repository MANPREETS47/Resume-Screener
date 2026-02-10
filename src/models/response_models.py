"""
Response models for API endpoints.
Uses Pydantic for validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone


class ResumeScreeningResponse(BaseModel):
    """Response model for resume screening endpoint."""
    
    candidate_name: str = Field(..., description="Full name of the candidate")
    skills: List[str] = Field(default_factory=list, description="List of candidate skills")
    experience_years: float = Field(..., ge=0, description="Total years of experience")
    education: List[str] = Field(default_factory=list, description="Education background")
    projects: List[str] = Field(default_factory=list, description="Notable projects")
    summary: str = Field(..., description="Brief summary of the candidate")
    matched_skills: List[str] = Field(default_factory=list, description="Skills matching the job description")
    missing_skills: List[str] = Field(default_factory=list, description="Skills required but not found in resume")
    matching_score: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Job-fit matching score (0-100)"
    )
    confidence_score: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0,
        description="Confidence score of the extraction (0-1)"
    )
    processing_time_ms: Optional[int] = Field(
        None, 
        description="Time taken to process in milliseconds"
    )
    rank: Optional[int] = Field(
        None,
        ge=1,
        description="Candidate rank when comparing multiple resumes (future feature)"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "candidate_name": "John Doe",
                "skills": ["Python", "FastAPI", "Docker"],
                "experience_years": 5,
                "education": ["BS Computer Science - MIT"],
                "projects": ["Resume Screener - Built FastAPI-based system"],
                "summary": "Experienced software engineer with 5 years in backend development.",
                "matched_skills": ["Python", "FastAPI"],
                "missing_skills": ["Kubernetes", "Go"],
                "matching_score": 78,
                "confidence_score": 0.95,
                "processing_time_ms": 2500,
                "rank": None
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Error timestamp"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "Invalid PDF file",
                "detail": "PDF file is corrupted or empty",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
