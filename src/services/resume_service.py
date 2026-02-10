"""
Resume Screening Service (Orchestrator).
Single Responsibility: Orchestrate PDF and LLM services.
Implements pipeline: PDF extraction → LLM processing → response formatting.
"""

import logging
import time
from typing import Dict, Any, List

from src.services.pdf_service import PDFService
from src.interfaces.llm_interface import LLMProvider
from src.core.prompt_templates import PromptTemplate
from src.models.response_models import ResumeScreeningResponse
from src.core.exceptions import (
    PDFExtractionException,
    LLMException,
    InvalidLLMResponseException
)

logger = logging.getLogger(__name__)


class ResumeScreeningService:
    """
    Main orchestrator service for resume screening pipeline.
    
    Pipeline:
    1. Extract text from PDF using PDFService
    2. Call LLM with resume text and job description
    3. Parse and validate LLM response
    4. Return structured response with matching score
    
    Follows:
    - Single Responsibility: Only orchestrates, doesn't implement details
    - Dependency Inversion: Depends on LLMProvider interface, not concrete class
    - Separation of Concerns: Delegates to specific services
    
    Scalability:
    - Designed for future multi-resume ranking via rank_candidates() method
    """
    
    def __init__(self, pdf_service: PDFService, llm_provider: LLMProvider):
        """
        Initialize Resume Screening Service with dependencies.
        
        Args:
            pdf_service: PDFService instance for PDF extraction
            llm_provider: LLMProvider implementation for LLM calls
        """
        self.pdf_service = pdf_service
        self.llm_provider = llm_provider
        logger.info("ResumeScreeningService initialized")
    
    async def screen_resume(
        self,
        pdf_bytes: bytes,
        job_description: str
    ) -> ResumeScreeningResponse:
        """
        Screen a resume against a job description.
        
        Pipeline:
        1. Extract text from PDF
        2. Generate prompt with resume and job description
        3. Call LLM API
        4. Parse and validate response
        5. Calculate confidence score
        6. Return structured response with matching score
        
        Args:
            pdf_bytes: PDF file contents as bytes
            job_description: Job description text
            
        Returns:
            ResumeScreeningResponse: Structured resume data with matching score
            
        Raises:
            PDFExtractionException: If PDF extraction fails
            LLMException: If LLM processing fails
            InvalidLLMResponseException: If response is invalid
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract text from PDF
            logger.info("Step 1: Extracting text from PDF")
            resume_text = self.pdf_service.extract_text(pdf_bytes)
            logger.info(f"Extracted {len(resume_text)} characters from PDF")
            
            # Step 2: Generate prompt
            logger.info("Step 2: Generating LLM prompt")
            prompt = PromptTemplate.get_resume_screening_prompt(
                resume_text=resume_text,
                job_description=job_description
            )
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Step 3: Call LLM
            logger.info("Step 3: Calling LLM API")
            llm_response = await self.llm_provider.call_llm(prompt)
            logger.info("LLM API call successful")
            
            # Step 4: Validate response
            logger.info("Step 4: Validating LLM response")
            if not self.llm_provider.validate_response(llm_response):
                logger.error("LLM response is not valid JSON")
                raise InvalidLLMResponseException(
                    message="LLM response does not contain valid JSON",
                    details="Unable to parse response as JSON"
                )
            
            # Step 5: Parse response
            logger.info("Step 5: Parsing LLM response")
            parsed_response = self.llm_provider.parse_response(llm_response)
            logger.info("LLM response parsed successfully")
            
            # Step 6: Create structured response
            logger.info("Step 6: Creating structured response")
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            response = self._create_response(
                parsed_response=parsed_response,
                processing_time_ms=processing_time_ms
            )
            
            logger.info(f"Resume screening completed in {processing_time_ms}ms")
            return response
        
        except PDFExtractionException as e:
            logger.error(f"PDF extraction failed: {e.message}")
            raise
        
        except LLMException as e:
            logger.error(f"LLM processing failed: {e.message}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error during resume screening: {str(e)}")
            raise
    
    def _create_response(
        self,
        parsed_response: Dict[str, Any],
        processing_time_ms: int
    ) -> ResumeScreeningResponse:
        """
        Create structured response from parsed LLM output.
        
        Args:
            parsed_response: Dictionary parsed from LLM response
            processing_time_ms: Time taken to process in milliseconds
            
        Returns:
            ResumeScreeningResponse: Validated response model
        """
        # Calculate confidence score based on field completeness
        confidence_score = self._calculate_confidence_score(parsed_response)
        
        # Clamp matching_score to 0-100
        raw_matching_score = parsed_response.get("matching_score", 0)
        matching_score = max(0, min(100, int(raw_matching_score) if raw_matching_score else 0))
        
        # Create response with all available fields
        response = ResumeScreeningResponse(
            candidate_name=parsed_response.get("candidate_name", "Unknown"),
            skills=parsed_response.get("skills", []),
            experience_years=parsed_response.get("experience_years", 0),
            education=parsed_response.get("education", []),
            projects=parsed_response.get("projects", []),
            summary=parsed_response.get("summary", ""),
            matched_skills=parsed_response.get("matched_skills", []),
            missing_skills=parsed_response.get("missing_skills", []),
            matching_score=matching_score,
            confidence_score=confidence_score,
            processing_time_ms=processing_time_ms
        )
        
        return response
    
    def _calculate_confidence_score(self, parsed_response: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on response completeness.
        
        Confidence is based on:
        - Non-empty candidate name (20%)
        - Non-empty skills list (15%)
        - Valid experience years (15%)
        - Non-empty education (10%)
        - Non-empty projects (10%)
        - Non-empty summary (10%)
        - Non-empty matched_skills (10%)
        - Valid matching_score (10%)
        
        Args:
            parsed_response: Dictionary parsed from LLM response
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        score = 0.0
        max_score = 1.0
        
        # Candidate name
        if parsed_response.get("candidate_name") and parsed_response["candidate_name"].strip():
            score += 0.20
        
        # Skills
        if isinstance(parsed_response.get("skills"), list) and len(parsed_response["skills"]) > 0:
            score += 0.15
        
        # Experience years
        if isinstance(parsed_response.get("experience_years"), (int, float)) and parsed_response["experience_years"] >= 0:
            score += 0.15
        
        # Education
        if isinstance(parsed_response.get("education"), list) and len(parsed_response["education"]) > 0:
            score += 0.10
        
        # Projects
        if isinstance(parsed_response.get("projects"), list) and len(parsed_response["projects"]) > 0:
            score += 0.10
        
        # Summary
        if parsed_response.get("summary") and parsed_response["summary"].strip():
            score += 0.10
        
        # Matched skills
        if isinstance(parsed_response.get("matched_skills"), list) and len(parsed_response["matched_skills"]) > 0:
            score += 0.10
        
        # Matching score
        if isinstance(parsed_response.get("matching_score"), (int, float)) and 0 <= parsed_response["matching_score"] <= 100:
            score += 0.10
        
        return round(min(score, max_score), 2)
