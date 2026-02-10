#Resume Screener API

A production-quality backend system for AI-powered resume screening using FastAPI and LLM APIs. This project demonstrates clean architecture, SOLID principles, and industry best practices.

##Objective

Build a resume screening system that:
- Accepts PDF resumes and job descriptions
- Extracts structured data from resumes using LLM APIs
- Returns validated, structured JSON responses
- Follows SOLID principles and clean architecture patterns

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                 │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │      API Routes (resume_routes.py)           │   │
│  │  - Request validation                        │   │
│  │  - Dependency injection                      │   │
│  │  - Error handling                            │   │
│  └──────────────────┬───────────────────────────┘   │
│                     │                                 │
│  ┌──────────────────▼───────────────────────────┐   │
│  │   ResumeScreeningService (Orchestrator)      │   │
│  │  - Coordinates PDF & LLM services            │   │
│  │  - Implements pipeline logic                 │   │
│  │  - Response formatting                       │   │
│  └─┬────────────────────────────────────────┬──┘   │
│    │                                        │        │
│  ┌─▼──────────────────┐      ┌─────────────▼───┐   │
│  │  PDFService        │      │  LLMProvider     │   │
│  │  ─────────────────  │      │  (Interface)     │   │
│  │  - PDF reading      │      │  ─────────────── │   │
│  │  - Text extraction  │      │  - call_llm()    │   │
│  │  - Validation       │      │  - validate()    │   │
│  │                     │      │  - parse()       │   │
│  └─────────────────────┘      └─────────────────┘   │
│                                         ▲             │
│                                         │             │
│                                ─────────────────     │
│                                │OpenAILLMProvider│    │
│                                └─────────────────     │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### Directory Structure

```
src/
 ├ main.py                          # FastAPI application
 │
 ├ api/
 │   └ resume_routes.py            # API endpoints with DI
 │
 ├ services/
 │   ├ pdf_service.py              # PDF extraction
 │   ├ llm_service.py              # LLM API wrapper
 │   └ resume_service.py           # Orchestrator
 │
 ├ interfaces/
 │   └ llm_interface.py            # LLMProvider abstract class
 │
 ├ models/
 │   ├ request_models.py           # Pydantic request schemas
 │   └ response_models.py          # Pydantic response schemas
 │
 ├ core/
 │   ├ config.py                   # Settings management
 │   ├ exceptions.py               # Custom exceptions
 │   └ prompt_templates.py         # LLM prompts
 │
tests/
 ├ unit/
 │   ├ test_pdf_service.py         # PDF service tests
 │   └ test_llm_service.py         # LLM service tests
 │
 └ integration/
     └ test_api_endpoint.py        # API endpoint tests
```

## 🏛️ SOLID Principles Implementation

### 1. **S — Single Responsibility Principle**

Each class has **one reason to change**:

- **PDFService**: Only responsible for PDF text extraction
  - Changes only when PDF extraction logic changes
  - Does not know about LLM or API responses

```python
class PDFService:
    """Responsible ONLY for PDF text extraction."""
    def extract_text(self, pdf_bytes: bytes) -> str:
        # PDF extraction logic only
```

- **OpenAILLMProvider**: Only communicates with LLM API
  - Changes only when LLM API integration changes
  - Does not know about PDF or pipeline logic

```python
class OpenAILLMProvider:
    """Responsible ONLY for LLM communication."""
    async def call_llm(self, prompt: str) -> str:
        # LLM API calls only
```

- **ResumeScreeningService**: Only orchestrates the pipeline
  - Changes only when business logic changes
  - Delegates to specific services

```python
class ResumeScreeningService:
    """Responsible ONLY for coordinating services."""
    async def screen_resume(self, pdf_bytes, job_description):
        # Call PDF service
        # Call LLM service
        # Format response
```

### 2. **O — Open/Closed Principle**

System is **open for extension, closed for modification**:

Instead of modifying `ResumeScreeningService` to support new LLM providers:

```python
# ❌ WRONG - Modifying existing code
if provider_type == "openai":
    call_openai_api()
elif provider_type == "anthropic":
    call_anthropic_api()
elif provider_type == "cohere":
    ...
```

We implement new providers **without modifying existing code**:

```python
# ✅ RIGHT - Extend via new implementations
class AnthropicLLMProvider(LLMProvider):
    async def call_llm(self, prompt: str) -> str:
        # Anthropic-specific implementation

class CohereLLMProvider(LLMProvider):
    async def call_llm(self, prompt: str) -> str:
        # Cohere-specific implementation
```

### 3. **L — Liskov Substitution Principle**

Any `LLMProvider` implementation can be **used interchangeably**:

```python
# These all work identically from the caller's perspective
llm_provider: LLMProvider = OpenAILLMProvider()      # or
llm_provider: LLMProvider = AnthropicLLMProvider()   # or
llm_provider: LLMProvider = CohereLLMProvider()

# Works with any provider without changes
service = ResumeScreeningService(pdf_service, llm_provider)
response = await service.screen_resume(pdf, job_desc)
```

### 4. **I — Interface Segregation Principle**

Clients depend on **small, focused interfaces**, not large ones:

```python
class LLMProvider(ABC):
    """Small, focused interface for ONE responsibility."""
    @abstractmethod
    async def call_llm(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    def validate_response(self, response: str) -> bool:
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Dict:
        pass
```

NOT a bloated interface:

```python
# ❌ WRONG - Large, unfocused interface
class LLMProvider(ABC):
    def call_llm(self) ...
    def train_model(self) ...
    def fine_tune(self) ...
    def evaluate(self) ...
    def deploy(self) ...
    def monitor(self) ...
```

### 5. **D — Dependency Inversion Principle**

High-level modules depend on **abstractions, not concrete implementations**:

```python
# ✅ RIGHT - Depends on interface (abstraction)
class ResumeScreeningService:
    def __init__(self, pdf_service: PDFService, llm_provider: LLMProvider):
        self.llm_provider = llm_provider  # Abstract
```

Not on concrete classes:

```python
# ❌ WRONG - Depends on concrete class
class ResumeScreeningService:
    def __init__(self):
        self.llm_provider = OpenAILLMProvider()  # Concrete, hard to test
```

### API Routes also follow Dependency Inversion:

```python
async def screen_resume(
    resume_file: UploadFile,
    job_description: str,
    # Depends on interface, injected by FastAPI
    resume_service: Annotated[ResumeScreeningService, Depends(get_resume_service)]
):
    response = await resume_service.screen_resume(pdf_bytes, job_description)
```

## 🚀 Tech Stack

- **Python 3.11+** - Latest Python with type hints
- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation with type hints
- **PyMuPDF (fitz)** - PDF text extraction
- **OpenAI API** - LLM integration (pluggable)
- **python-dotenv** - Environment configuration
- **pytest** - Testing framework
- **httpx** - Async HTTP client

## 📦 Installation & Setup

### 1. Clone and Navigate

```bash
cd path/to/devlopathon
```

### 2. Create Virtual Environment

```bash
# Python 3.11+
python -m venv venv

# Activate
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env with your values
# Get OpenAI API key from https://platform.openai.com/api-keys
```

**Example .env:**
```
LLM_API_KEY="sk-your-openai-api-key"
LLM_MODEL="gpt-4-turbo-preview"
DEBUG=False
```

## ▶️ Running the Application

### Start Development Server

```bash
# From project root
python -m uvicorn src.main:app --reload
```

Server runs at: `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src
```

### Run Specific Test Suite

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_pdf_service.py

# Specific test class
pytest tests/unit/test_pdf_service.py::TestPDFService

# Specific test
pytest tests/unit/test_pdf_service.py::TestPDFService::test_extract_text_success
```

### Test Coverage

Current test coverage includes:
- ✅ PDF extraction (valid, empty, invalid, oversized PDFs)
- ✅ LLM communication (mock API responses, error handling)
- ✅ Resume screening service orchestration
- ✅ API endpoint validation (file type, size, job description)
- ✅ Error handling and exceptions
- ✅ Response formatting and confidence scoring

## 📡 API Usage

### Endpoint: `/api/v1/screen-resume`

**Method**: `POST`

**Content-Type**: `multipart/form-data`

### Request

```bash
curl -X POST "http://localhost:8000/api/v1/screen-resume" \\
  -F "resume_file=@path/to/resume.pdf" \\
  -F "job_description=Senior Python developer with 5+ years experience"
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/screen-resume" \\
  -F "resume_file=@resume.pdf" \\
  -F "job_description=Looking for backend engineer with Python and FastAPI skills"
```

### Python Example

```python
import requests

with open("resume.pdf", "rb") as pdf:
    response = requests.post(
        "http://localhost:8000/api/v1/screen-resume",
        files={"resume_file": pdf},
        data={"job_description": "Senior Python developer with FastAPI experience"}
    )

result = response.json()
print(f"Candidate: {result['candidate_name']}")
print(f"Skills: {result['skills']}")
print(f"Experience: {result['experience_years']} years")
print(f"Confidence: {result['confidence_score']:.2%}")
```

### Response

```json
{
  "candidate_name": "John Doe",
  "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS"],
  "experience_years": 5,
  "education": ["BS Computer Science - Stanford University"],
  "projects": [
    "Resume Screener - AI-powered resume analysis tool",
    "E-commerce Platform - Built FastAPI backend"
  ],
  "summary": "Experienced backend engineer with strong Python and async programming skills. Demonstrated expertise in building scalable APIs and microservices.",
  "confidence_score": 0.95,
  "processing_time_ms": 2543
}
```

## 🔧 Extension Guide: Adding New LLM Providers

### 1. Create New Provider Class

```python
# src/services/new_llm_provider.py
from src.interfaces.llm_interface import LLMProvider

class AnthropicLLMProvider(LLMProvider):
    """Anthropic Claude LLM provider."""
    
    async def call_llm(self, prompt: str, max_tokens: int = None) -> str:
        # Implement Anthropic API calls
        pass
    
    def validate_response(self, response: str) -> bool:
        # Implement validation
        pass
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        # Implement parsing
        pass
```

### 2. Update get_llm_provider Dependency

```python
# src/api/resume_routes.py
def get_llm_provider() -> LLMProvider:
    # Select provider via environment variable
    provider_type = get_settings().LLM_PROVIDER
    
    if provider_type == "openai":
        return OpenAILLMProvider()
    elif provider_type == "anthropic":
        return AnthropicLLMProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_type}")
```

### 3. No Other Changes Required!

The rest of the system works **unchanged** thanks to Dependency Inversion:
- `ResumeScreeningService` still works
- `resume_routes.py` still works
- All tests still pass
- No business logic changes needed

## 📊 Response Confidence Scoring

Confidence score (0-1) is calculated based on response completeness:

```
candidate_name validity      → 25%
skills extraction            → 20%
experience_years validity    → 20%
education extraction         → 15%
projects extraction          → 10%
summary extraction           → 10%
─────────────────────────────────
Total possible              → 100%
```

## 🔍 Error Handling

### PDF Errors
- `PDFSizeException` - File exceeds max size
- `InvalidPDFException` - Corrupted PDF
- `EmptyPDFException` - No extractable text

### LLM Errors
- `LLMAPIException` - API communication failed
- `LLMTimeoutException` - Request timed out
- `InvalidLLMResponseException` - Invalid JSON response
- `LLMRetryException` - Retries exhausted

### HTTP Status Codes
- `200` - Success
- `400` - Invalid input (file, size, format)
- `422` - Validation error (job description)
- `500` - Server error (LLM failure)

## 📝 Project Structure Quality

### Code Organization
- ✅ **Clear separation of concerns** - Each module has one responsibility
- ✅ **Type hints everywhere** - Full type hinting for IDE support
- ✅ **Comprehensive docstrings** - Clear documentation
- ✅ **Error handling** - Custom exceptions for different scenarios
- ✅ **Logging** - Structured logging at each step
- ✅ **Testing** - Unit and integration tests

### Best Practices
- ✅ Dependency Injection pattern
- ✅ Service layer architecture
- ✅ Interface-based design
- ✅ Environment configuration
- ✅ Async/await for I/O operations
- ✅ Pydantic validation
- ✅ Proper HTTP status codes

## 🎓 Academic Evaluation

This project demonstrates:

1. **Software Architecture**
   - Clean architecture principles
   - SOLID principles in practice
   - Design patterns (Service Layer, Dependency Injection)

2. **Python Best Practices**
   - Type hints
   - Docstrings
   - Exception handling
   - Async programming

3. **API Design**
   - RESTful principles
   - Request/response validation
   - Proper HTTP status codes
   - Error handling

4. **Testing**
   - Unit test coverage
   - Integration tests
   - Mock-based testing

5. **Production Quality**
   - Configuration management
   - Logging
   - Security considerations
   - Extensibility

## 📚 Additional Resources

### SOLID Principles
- [SOLID Principles Wikipedia](https://en.wikipedia.org/wiki/SOLID)
- [Clean Code by Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)

### FastAPI
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)

### Design Patterns
- [Design Patterns by Gang of Four](https://en.wikipedia.org/wiki/Design_Patterns)
- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)

## 📄 License

This project is provided for educational purposes.

## 👤 Author

Created as a college-level project demonstrating production-quality backend development.

---

**Built with ❤️ following SOLID principles and clean architecture practices.**
#   R e s u m e - S c r e e n e r 
 
 #   R e s u m e - S c r e e n e r 
 
 #   R e s u m e - S c r e e n e r 
 
 

