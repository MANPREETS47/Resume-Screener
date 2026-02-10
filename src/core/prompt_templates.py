"""
Prompt templates for LLM API calls.
Separated from business logic for maintainability.
"""

RESUME_SCREENING_PROMPT = """You are an expert resume screener. Analyze the provided resume against the job description, extract structured information, and evaluate how well the candidate matches.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Extract the following information from the resume in valid JSON format (no markdown, no extra text):

{{
  "candidate_name": "Full name of the candidate",
  "skills": ["skill1", "skill2", "skill3"],
  "experience_years": number of years of total experience,
  "education": ["Degree - Field - University"],
  "projects": ["Project name - Brief description"],
  "summary": "A 2-3 sentence summary of the candidate",
  "matched_skills": ["skills from the resume that match the job description"],
  "missing_skills": ["skills required in the job description but NOT found in the resume"],
  "matching_score": integer from 0 to 100 representing how well the candidate fits the job description
}}

Important instructions:
- "matched_skills" should ONLY include skills that appear in BOTH the resume AND job description.
- "missing_skills" should ONLY include skills mentioned in the job description but NOT in the resume.
- "matching_score" should be based on: skill overlap, relevant experience, education fit, and project relevance.
- Return ONLY the JSON object, nothing else."""


class PromptTemplate:
    """Container for prompt templates."""
    
    RESUME_SCREENING = RESUME_SCREENING_PROMPT
    
    @staticmethod
    def get_resume_screening_prompt(resume_text: str, job_description: str) -> str:
        """
        Generate resume screening prompt with variables filled.
        
        Args:
            resume_text: Extracted text from PDF resume
            job_description: Job description text
            
        Returns:
            str: Formatted prompt ready for LLM
        """
        return RESUME_SCREENING_PROMPT.format(
            resume_text=resume_text,
            job_description=job_description
        )
