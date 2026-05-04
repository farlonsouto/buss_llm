"""
Data Transfer Objects (DTOs) for the Transit Intelligence Engine.

This module defines the 'Contract' between the Frontend and Backend,
and the 'Gold' layer schema for the data pipeline.
"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class TransitFeedbackRequest(BaseModel):
    """Data model for incoming passenger feedback."""
    raw_text: str = Field(
        ...,
        min_length=5,
        description="The raw unstructured text submitted by the traveler.",
        examples=["The 4:15 PM bus to Lade was late."]
    )
    source: str = Field(
        default="mobile_app",
        description="Originating platform of the feedback."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "raw_text": "Bus 1 is always late at Prinsens gate.",
                "source": "web_portal"
            }
        }
    )


class FeedbackAnalysis(BaseModel):
    """The 'Gold' layer structured output from the LLM processing."""
    category: str = Field(..., description="Thematic classification (e.g., Delay, Hygiene).")
    sentiment: str = Field(..., description="Sentiment analysis result.")
    priority: int = Field(..., ge=1, le=5, description="Urgency score from 1 (low) to 5 (critical).")
    extracted_entities: List[str] = Field(
        default_factory=list,
        description="List of detected bus lines, stops, or locations."
    )


class TransitFeedbackResponse(BaseModel):
    """The final processed object returned to the consumer and saved to the DB."""
    id: str = Field(..., description="Unique UUID for the feedback record.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC processing time.")
    original_input: TransitFeedbackRequest
    analysis: FeedbackAnalysis
    status: str = Field("processed", description="Current lifecycle stage of the record.")

    model_config = ConfigDict(from_attributes=True)
