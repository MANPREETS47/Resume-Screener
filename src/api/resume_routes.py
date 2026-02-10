"""
Resume screening API routes.
No business logic here - only request handling, dependency injection, and response formatting.
"""

import logging
from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status

from src.services.resume_service import ResumeScreeningService
from src.services.pdf_service import PDFService
from src.services.llm_service import GeminiLLMProvider
from src.interfaces.llm_interface import LLMProvider
from src.models.response_models import ResumeScreeningResponse, ErrorResponse
from src.core.exceptions import (
    PDFSizeException,
    InvalidPDFException,
    EmptyPDFException,
    PDFExtractionException,
    LLMException,
    InvalidLLMResponseException
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["resume-screening"])


# Dependency Injection Functions
def get_pdf_service() -> PDFService:
    """Provide PDFService instance (Dependency Injection)."""
    return PDFService()


def get_llm_provider() -> LLMProvider:
    """Provide LLMProvider instance (Dependency Injection)."""
    return GeminiLLMProvider()


def get_resume_service(
    pdf_service: PDFService = Depends(get_pdf_service),
    llm_provider: LLMProvider = Depends(get_llm_provider)
) -> ResumeScreeningService:
    """Provide ResumeScreeningService with all dependencies injected."""
    return ResumeScreeningService(
        pdf_service=pdf_service,
        llm_provider=llm_provider
    )


@router.post(
    "/screen-resume",
    response_model=ResumeScreeningResponse,
    responses={
        200: {
            "description": "Resume screening successful",
            "model": ResumeScreeningResponse
        },
        400: {
            "description": "Invalid request",
            "model": ErrorResponse
        },
        422: {
            "description": "Unprocessable entity",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def screen_resume(
    resume_file: Annotated[
        UploadFile,
        File(..., description="PDF resume file to analyze")
    ],
    job_description: Annotated[
        str,
        Form(..., min_length=10, max_length=5000, description="Job description to match against")
    ],
    resume_service: Annotated[
        ResumeScreeningService,
        Depends(get_resume_service)
    ]
) -> ResumeScreeningResponse:
    """
    Screen a resume against a job description.
    
    This endpoint:
    1. Accepts a PDF resume file and job description
    2. Extracts text from the PDF
    3. Sends resume and job description to LLM for analysis
    4. Returns structured candidate data with matching score
    
    Args:
        resume_file: PDF file to analyze
        job_description: Job description text
        resume_service: Injected service
        
    Returns:
        ResumeScreeningResponse: Structured resume data with matching score
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        # Log request
        logger.info(
            f"Resume screening request received: "
            f"file={resume_file.filename}, "
            f"job_description_length={len(job_description)}"
        )
        
        # Validate file type
        if resume_file.content_type not in ["application/pdf", "application/x-pdf"]:
            logger.warning(f"Invalid file type: {resume_file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a PDF"
            )
        
        # Validate filename
        if not resume_file.filename or not resume_file.filename.lower().endswith(".pdf"):
            logger.warning(f"Invalid filename: {resume_file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have .pdf extension"
            )
        
        # Validate job description
        if not job_description.strip():
            logger.warning("Empty job description provided")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Job description cannot be empty"
            )
        
        # Read file contents (async to avoid blocking event loop)
        logger.info(f"Reading file: {resume_file.filename}")
        pdf_bytes = await resume_file.read()
        
        if not pdf_bytes:
            logger.error("Received empty file")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        # Process resume
        logger.info("Starting resume screening pipeline")
        response = await resume_service.screen_resume(
            pdf_bytes=pdf_bytes,
            job_description=job_description.strip()
        )
        
        logger.info(f"Resume screening completed successfully for {resume_file.filename}")
        return response
    
    except HTTPException:
        raise
    
    except PDFSizeException as e:
        logger.error(f"PDF size error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    
    except InvalidPDFException as e:
        logger.error(f"Invalid PDF: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    
    except EmptyPDFException as e:
        logger.error(f"Empty PDF: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    
    except PDFExtractionException as e:
        logger.error(f"PDF extraction error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF: {e.message}"
        )
    
    except InvalidLLMResponseException as e:
        logger.error(f"Invalid LLM response: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM returned invalid data format"
        )
    
    except LLMException as e:
        logger.error(f"LLM error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume analysis failed: {e.message}"
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during resume screening"
        )


@router.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "message": "Resume Screener API is running"
    }
