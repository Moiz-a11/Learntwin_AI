"""API contracts for LearnTwin AI (version 1).

This module defines request and response Pydantic models for the v1 REST
endpoints. These are documentation-first schemas; no business logic is
implemented here.

Endpoints covered:
- POST /observation
- POST /digital-twin/update
- GET /digital-twin/{user_id}
- POST /recommendation
- GET /dashboard/{user_id}
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ObservationCreate(BaseModel):
    """Request schema for `POST /observation`.

    Example usage: the Observation service posts sensor/UI events or learning
    interactions to this endpoint. `payload` stores structured event data.
    """

    user_id: str = Field(..., description="Unique user identifier")
    timestamp: datetime = Field(..., description="ISO-8601 timestamp of the event")
    source: Optional[str] = Field(None, description="Source system (e.g. observation-agent)")
    event_type: str = Field(..., description="Short event type identifier")
    payload: Dict[str, Any] = Field(..., description="Event payload with domain-specific fields")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional transport/ingestion metadata")


class ObservationAccepted(BaseModel):
    """Response for `POST /observation` when an observation is accepted.

    The server should return an identifier that the observation pipeline can
    use for tracking and de-duplication.
    """

    observation_id: str = Field(..., description="Server-assigned observation id")
    status: str = Field(..., description="Processing status, e.g. 'accepted' or 'queued'")
    received_at: datetime = Field(..., description="Server receipt timestamp")


class DigitalTwinUpdateRequest(BaseModel):
    """Request schema for `POST /digital-twin/update`.

    Clients post desired twin updates—small, explicit patches describing the
    changes to apply to the user's digital twin. The backend determines how to
    validate and persist these updates.
    """

    user_id: str = Field(..., description="User identifier whose twin will be updated")
    updates: Dict[str, Any] = Field(..., description="Partial digital twin fields to update")
    reason: Optional[str] = Field(None, description="Human-readable reason for the update")
    apply_immediately: bool = Field(True, description="Whether to apply the change synchronously")
    source: Optional[str] = Field(None, description="Origin of the update request")


class DigitalTwinUpdateResponse(BaseModel):
    """Response for `POST /digital-twin/update` describing the result."""

    user_id: str
    status: str = Field(..., description="Result status, e.g. 'ok', 'queued', 'rejected'")
    updated_at: Optional[datetime] = Field(None, description="When the twin was updated (if applied)")
    applied_changes: Optional[Dict[str, Any]] = Field(None, description="Echo of applied changes when available")


class DigitalTwinState(BaseModel):
    """Response schema for `GET /digital-twin/{user_id}`.

    Includes the canonical fields that make up the user's digital twin.
    """

    user_id: str
    profile: Dict[str, Any] = Field(default_factory=dict)
    skills: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    learning_goals: Dict[str, Any] = Field(default_factory=dict)
    summary: Optional[str] = None
    last_updated: Optional[datetime] = None

    class Config:
        orm_mode = True


class RecommendationItem(BaseModel):
    """Single recommendation item returned by the recommendation API."""

    id: Optional[str] = None
    title: str
    description: str
    type: Optional[str] = None
    source: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    rationale: Optional[str] = None
    url: Optional[str] = None


class RecommendationRequest(BaseModel):
    """Request schema for `POST /recommendation`.

    Frontend or orchestration services post recommendation requests with an
    optional objective and contextual hints to influence the produced list.
    """

    user_id: str = Field(..., description="User identifier to generate recommendations for")
    objective: Optional[str] = Field(None, description="Optional short objective (e.g. 'improve math skills')")
    context: Optional[Dict[str, Any]] = Field(None, description="Extra contextual hints for recommendation generation")
    max_results: int = Field(5, ge=1, le=50)


class RecommendationResponse(BaseModel):
    """Response for `POST /recommendation`.

    Returns a list of recommendation items and metadata about the generator.
    """

    user_id: str
    recommendations: List[RecommendationItem]
    model: Optional[str] = Field(None, description="Identifier of the model or engine used")
    generated_at: datetime


class DashboardMetrics(BaseModel):
    """Small metrics summary used by the dashboard endpoint."""

    interactions_last_7d: int = 0
    total_learning_minutes: int = 0
    last_active: Optional[datetime] = None


class DashboardResponse(BaseModel):
    """Response schema for `GET /dashboard/{user_id}`.

    The dashboard aggregates metrics, recent recommendations, and recent
    observations about the user to support the UI.
    """

    user_id: str
    metrics: DashboardMetrics
    recent_recommendations: List[RecommendationItem] = Field(default_factory=list)
    recent_observations: List[Dict[str, Any]] = Field(default_factory=list)
