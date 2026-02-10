"""
Streamlit Frontend for AI Resume Screener (Gemini Edition).
Provides a web interface for uploading resumes, entering job descriptions,
and viewing structured screening results with matching scores.
"""

import asyncio
import streamlit as st
import sys
from pathlib import Path

# Ensure src package is importable
sys.path.insert(0, str(Path(__file__).parent))

from src.services.pdf_service import PDFService
from src.services.llm_service import GeminiLLMProvider
from src.services.resume_service import ResumeScreeningService
from src.core.exceptions import (
    PDFSizeException,
    InvalidPDFException,
    EmptyPDFException,
    PDFExtractionException,
    LLMException,
    InvalidLLMResponseException
)

# ──────────────── Page Config ────────────────
st.set_page_config(
    page_title="Resume Screener (Gemini)",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────── Custom CSS ────────────────
st.markdown("""
<style>
    /* Main container */
    .block-container { padding-top: 2rem; }
    
    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border: 1px solid #3d3d5c;
        border-radius: 12px;
        padding: 1rem;
    }
    div[data-testid="stMetric"] label {
        color: #a0a0c0;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e0e0ff;
    }
    
    /* Skill tags */
    .skill-tag {
        display: inline-block;
        padding: 4px 12px;
        margin: 3px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .skill-matched {
        background: linear-gradient(135deg, #1a472a, #2d6a4f);
        color: #95d5b2;
        border: 1px solid #40916c;
    }
    .skill-missing {
        background: linear-gradient(135deg, #4a1a1a, #6a2d2d);
        color: #f4a0a0;
        border: 1px solid #914040;
    }
    .skill-all {
        background: linear-gradient(135deg, #1a2a4a, #2d3d6a);
        color: #a0c4f4;
        border: 1px solid #405c91;
    }
    
    /* Score ring */
    .score-container {
        text-align: center;
        padding: 1rem;
    }
    .score-number {
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1;
    }
    .score-label {
        font-size: 0.9rem;
        color: #a0a0c0;
        margin-top: 0.5rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #c0c0e0;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #3d3d5c;
        padding-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────── Sidebar ────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    model_choice = st.selectbox(
        "LLM Model",
        options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"],
        index=0,
        help="Flash is faster/cheaper. Pro is more capable."
    )
    
    st.divider()
    
    st.markdown("## 📖 About")
    st.markdown(
        "**Resume Screener (Gemini Edition)** uses Google's Gemini models "
        "to analyze resumes against job descriptions. "
        "It extracts skills, calculates a matching score, "
        "and provides structured candidate insights."
    )
    
    st.markdown("---")
    st.caption("Built with Streamlit • Google Gemini")


# ──────────────── Helper ────────────────
def run_async(coro):
    """Run an async coroutine from synchronous Streamlit context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def get_score_color(score: int) -> str:
    """Return a color hex based on the matching score."""
    if score >= 80:
        return "#2d6a4f"
    elif score >= 60:
        return "#e9c46a"
    elif score >= 40:
        return "#f4a261"
    else:
        return "#e76f51"


def render_skill_tags(skills: list, css_class: str) -> str:
    """Render a list of skills as styled HTML tags."""
    if not skills:
        return "<span style='color: #888;'>None</span>"
    return " ".join(
        f'<span class="skill-tag {css_class}">{skill}</span>' 
        for skill in skills
    )


# ──────────────── Main UI ────────────────
st.markdown("# ✨ AI Resume Screener")
st.markdown("Upload a PDF resume and enter a job description to get an AI-powered analysis with skill matching.")

st.divider()

# ── Input Section ──
col_upload, col_jd = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown("### 📄 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a PDF resume (max 10 MB)"
    )
    if uploaded_file:
        st.success(f"✅ **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

with col_jd:
    st.markdown("### 📝 Job Description")
    job_description = st.text_area(
        "Paste the job description",
        height=200,
        placeholder="e.g. We are looking for a Senior Python developer with 5+ years of experience in FastAPI, Docker, and AWS...",
        help="Minimum 10 characters required"
    )

st.divider()

# ── Analyze Button ──
analyze_clicked = st.button(
    "🔍 Analyze Resume",
    type="primary",
    use_container_width=True,
    disabled=not (uploaded_file and job_description and len(job_description.strip()) >= 10)
)

# ── Processing & Results ──
if analyze_clicked:
    with st.spinner("🧠 Analyzing resume with Gemini..."):
        try:
            # Read file bytes
            pdf_bytes = uploaded_file.read()
            
            # Create services
            pdf_service = PDFService()
            llm_provider = GeminiLLMProvider(model_override=model_choice)
            resume_service = ResumeScreeningService(
                pdf_service=pdf_service,
                llm_provider=llm_provider
            )
            
            # Run the screening pipeline
            result = run_async(
                resume_service.screen_resume(
                    pdf_bytes=pdf_bytes,
                    job_description=job_description.strip()
                )
            )
            
            # ── Display Results ──
            st.divider()
            st.markdown("## 📊 Screening Results")
            
            # Top row: Score + Candidate Info
            col_score, col_info = st.columns([1, 3], gap="large")
            
            with col_score:
                score_color = get_score_color(result.matching_score)
                st.markdown(f"""
                <div class="score-container">
                    <div class="score-number" style="color: {score_color};">
                        {result.matching_score}%
                    </div>
                    <div class="score-label">Matching Score</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.progress(result.matching_score / 100)
                
                if result.confidence_score is not None:
                    st.caption(f"Extraction confidence: {result.confidence_score:.0%}")
            
            with col_info:
                st.markdown(f"### 👤 {result.candidate_name}")
                st.markdown(f"_{result.summary}_")
                
                info_cols = st.columns(3)
                with info_cols[0]:
                    st.metric("📅 Experience", f"{result.experience_years} years")
                with info_cols[1]:
                    st.metric("🎓 Education", f"{len(result.education)} entries")
                with info_cols[2]:
                    st.metric("⏱️ Processed In", f"{(result.processing_time_ms or 0) / 1000:.1f}s")
            
            st.divider()
            
            # Skills Section
            skill_cols = st.columns(3, gap="medium")
            
            with skill_cols[0]:
                st.markdown('<div class="section-header">✅ Matched Skills</div>', unsafe_allow_html=True)
                st.markdown(render_skill_tags(result.matched_skills, "skill-matched"), unsafe_allow_html=True)
            
            with skill_cols[1]:
                st.markdown('<div class="section-header">❌ Missing Skills</div>', unsafe_allow_html=True)
                st.markdown(render_skill_tags(result.missing_skills, "skill-missing"), unsafe_allow_html=True)
            
            with skill_cols[2]:
                st.markdown('<div class="section-header">🛠️ All Skills</div>', unsafe_allow_html=True)
                st.markdown(render_skill_tags(result.skills, "skill-all"), unsafe_allow_html=True)
            
            st.divider()
            
            # Details Expanders
            detail_cols = st.columns(2, gap="medium")
            
            with detail_cols[0]:
                with st.expander("🎓 Education", expanded=False):
                    if result.education:
                        for edu in result.education:
                            st.markdown(f"- {edu}")
                    else:
                        st.caption("No education data extracted.")
            
            with detail_cols[1]:
                with st.expander("🚀 Projects", expanded=False):
                    if result.projects:
                        for proj in result.projects:
                            st.markdown(f"- {proj}")
                    else:
                        st.caption("No project data extracted.")
            
            # Raw JSON
            with st.expander("🔧 Raw JSON Response", expanded=False):
                st.json(result.model_dump())
        
        except PDFSizeException as e:
            st.error(f"📏 **PDF Too Large**: {e.message}")
        except InvalidPDFException as e:
            st.error(f"📄 **Invalid PDF**: {e.message}")
        except EmptyPDFException as e:
            st.error(f"📄 **Empty PDF**: {e.message}")
        except PDFExtractionException as e:
            st.error(f"📄 **PDF Error**: {e.message}")
        except InvalidLLMResponseException as e:
            st.error(f"🤖 **LLM Response Error**: The AI returned an invalid response. Please try again.")
        except LLMException as e:
            st.error(f"🤖 **LLM Error**: {e.message}")
        except Exception as e:
            st.error(f"❌ **Unexpected Error**: {str(e)}")
            st.exception(e)
