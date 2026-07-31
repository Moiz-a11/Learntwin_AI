from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LearningHistoryEntry(BaseModel):
    timestamp: datetime
    topic: str
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RevisionScheduleEntry(BaseModel):
    topic: str
    next_review: datetime
    interval_days: int
    priority: Optional[int] = Field(None, description="Higher value => higher priority")


class DigitalTwinCreate(BaseModel):
    user_id: str
    knowledge_score: Optional[float] = 0.0
    confidence: Optional[float] = 0.0
    engagement: Optional[float] = 0.0
    learning_style: Optional[str] = None
    strengths: Optional[List[str]] = Field(default_factory=list)
    weaknesses: Optional[List[str]] = Field(default_factory=list)
    learning_history: Optional[List[LearningHistoryEntry]] = Field(default_factory=list)
    revision_schedule: Optional[List[RevisionScheduleEntry]] = Field(default_factory=list)
    completed_topics: Optional[List[str]] = Field(default_factory=list)
    current_topic: Optional[str] = None


class DigitalTwinUpdate(BaseModel):
    knowledge_score: Optional[float]
    confidence: Optional[float]
    engagement: Optional[float]
    learning_style: Optional[str]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    learning_history: Optional[List[LearningHistoryEntry]]
    revision_schedule: Optional[List[RevisionScheduleEntry]]
    completed_topics: Optional[List[str]]
    current_topic: Optional[str]


class DigitalTwinResponse(BaseModel):
    user_id: str
    knowledge_score: float = 0.0
    confidence: float = 0.0
    engagement: float = 0.0
    learning_style: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    learning_history: List[LearningHistoryEntry] = Field(default_factory=list)
    revision_schedule: List[RevisionScheduleEntry] = Field(default_factory=list)
    completed_topics: List[str] = Field(default_factory=list)
    current_topic: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
