````md
# 🚀 Resume Screener API

AI-powered resume screening backend built with **FastAPI + LLM APIs**, designed using **Clean Architecture** and **SOLID principles**.

> Production-style backend project demonstrating scalable service design, dependency injection, and pluggable AI providers.
---

## ✨ Features

- 📄 PDF Resume Upload  
- 🧠 LLM-based Structured Data Extraction  
- ✅ Validated JSON Responses  
- 🔌 Pluggable LLM Provider Architecture  
- ⚡ Fully Async FastAPI Backend  
- 🧪 Unit + Integration Tests  
- 📊 Confidence Scoring System  

---

## 🏗 Architecture

```
FastAPI → ResumeScreeningService → (PDFService + LLMProvider Interface)
```

Supports easy extension:

```
OpenAI | Anthropic | Cohere | Custom Providers
```

---

## 🛠 Tech Stack

- Python 3.11+  
- FastAPI  
- Pydantic  
- PyMuPDF  
- OpenAI API (Provider Pattern)  
- pytest  
- httpx  

---

## ⚙️ Quick Start

### 1️⃣ Clone
```bash
git clone <repo-url>
cd resume-screener
```

---

### 2️⃣ Setup Environment
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure `.env`
```
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4-turbo-preview
```

---

### ▶ Run Server
```bash
python -m uvicorn src.main:app --reload
```
---

## 📡 API Example

### Request
```bash
curl -X POST "http://localhost:8000/api/v1/screen-resume" \
-F "resume_file=@resume.pdf" \
-F "job_description=Senior Python Developer"
```

---

### Response
```json
{
  "candidate_name": "John Doe",
  "skills": ["Python", "FastAPI", "Docker"],
  "experience_years": 5,
  "confidence_score": 0.95
}
```

---

## 🧪 Testing
```bash
pytest
```

## 🎯 What This Project Shows

- Real-world backend architecture  
- SOLID principles in production-style services  
- Async API design  
- Testable dependency-injected system  
- Extensible AI integration design  

---

## 📄 License
Portfolio / Educational Use

---

⭐ Star if useful!
````
