"""
FastAPI Main Application.
Initializes and configures the Resume Screener API.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.api.resume_routes import router as resume_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("=" * 50)
    logger.info(f"{settings.API_TITLE} v{settings.API_VERSION} starting")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"LLM Model: {settings.LLM_MODEL}")
    logger.info("=" * 50)
    yield
    # Shutdown
    logger.info("=" * 50)
    logger.info(f"{settings.API_TITLE} shutting down")
    logger.info("=" * 50)


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered resume screening system using LLM",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume_router)

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information."""
    logger.info("Root endpoint accessed")
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server at {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
