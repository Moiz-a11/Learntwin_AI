"""Pydantic schemas for the Observation Engine."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ObservationCreate(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the learner")
    topic: str = Field(..., description="Learning topic associated with the observation")
    activity_type: str = Field(..., description="Type of learning activity")
    duration_minutes: int = Field(..., description="Observed learning duration in minutes")
    score: Optional[float] = Field(None, description="Measured score or quality of the observation")
    confidence: Optional[float] = Field(None, description="Observer confidence rating")
    notes: Optional[str] = Field(None, description="Optional notes about the observation")


class ObservationResponse(BaseModel):
    success: bool
    message: str
    updated_metrics: Dict[str, Any] = Field(default_factory=dict)
