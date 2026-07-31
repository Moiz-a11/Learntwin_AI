from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ObservationCreate(BaseModel):
    user_id: str
    timestamp: datetime
    event_type: str
    payload: Dict[str, Any]


class DigitalTwinStateResponse(BaseModel):
    user_id: str
    profile: Dict[str, Any] = Field(default_factory=dict)
    skills: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    learning_goals: Dict[str, Any] = Field(default_factory=dict)
    summary: Optional[str]
    last_updated: Optional[datetime]

    class Config:
        orm_mode = True


class RecommendationRequest(BaseModel):
    objective: Optional[str] = None
    max_results: int = 5


class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[Dict[str, Any]]
    model_used: str
    generated_at: datetime


class RecommendationHistoryItem(BaseModel):
    user_id: str
    recommendations: List[Dict[str, Any]]
    generated_at: datetime
