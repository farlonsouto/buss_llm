"""
Main entry point for the Transit Intelligence API.

This service orchestrates the ingestion of unstructured transit data
and its transformation into structured intelligence via the LLMProcessor.
"""
import logging
import os
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .processor import LLMProcessor
from .schemas import TransitFeedbackRequest, TransitFeedbackResponse

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Transit Intelligence Engine",
    description="Production-grade API for processing public transport feedback using local LLMs.",
    version="1.0.0"
)

# CORS configuration for Dockerized environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global processor instance (Singleton pattern)
# OLLAMA_URL can be set via environment variables in docker-compose.yml
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://docker.internal")
processor = LLMProcessor(base_url=OLLAMA_URL)


@app.get("/health", tags=["System"])
async def health_check():
    """Service health check for container orchestration."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "config": {"ollama_url": OLLAMA_URL}
    }


@app.post(
    "/analyze",
    response_model=TransitFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Intelligence"]
)
async def analyze_feedback(request: TransitFeedbackRequest):
    """
    Ingests raw text and returns structured 'Gold' layer analysis.

    The process:
    1. Validate input schema (Pydantic).
    2. Invoke local LLM for intent classification and entity extraction.
    3. Return a structured record ready for downstream BI or operational systems.
    """
    logger.info(f"Incoming feedback from {request.source}: '{request.raw_text[:50]}...'")

    try:
        # Perform LLM Analysis
        analysis = await processor.analyze_text(request)

        # Build the final 'Gold' record
        response = TransitFeedbackResponse(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            original_input=request,
            analysis=analysis,
            status="processed"
        )

        logger.info(f"Successfully processed feedback ID: {response.id}")
        return response

    except RuntimeError as e:
        # Handle specific LLM connection or parsing errors
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        # Generic error fallback
        logger.exception("An unexpected error occurred during analysis.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during data processing."
        )
