"""
Request models for API endpoints.
Uses Pydantic for validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ResumeScreeningRequest(BaseModel):
    """Request model for resume screening endpoint."""
    
    job_description: str = Field(
        ..., 
        min_length=10, 
        max_length=5000,
        description="Job description text to compare against resume"
    )
    
    @field_validator('job_description')
    @classmethod
    def validate_job_description(cls, v: str) -> str:
        """Validate and clean job description."""
        if not v.strip():
            raise ValueError("Job description cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "job_description": "We are looking for a Python developer with 5+ years experience..."
            }
        }
