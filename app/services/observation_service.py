"""Service layer for processing learning observations."""

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.schemas.observation import ObservationCreate, ObservationResponse
from app.schemas.digital_twin import (
    DigitalTwinResponse,
    DigitalTwinUpdate,
    LearningHistoryEntry,
)
from app.services.digital_twin_service import DigitalTwinService


class ObservationService:
    """Encapsulate observation processing and digital twin updates."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._twin_service = DigitalTwinService(db)

    def record_observation(self, observation: ObservationCreate) -> ObservationResponse:
        """Record a learning observation and update the learner's digital twin."""
        twin = self._twin_service.get_twin(observation.user_id)
        if twin is None:
            return ObservationResponse(
                success=False,
                message="Digital Twin not found",
                updated_metrics={},
            )

        history_entry = self._build_history_entry(observation)
        updates = self._build_updates(twin, observation, history_entry)

        updated_twin = self._twin_service.update_twin(observation.user_id, updates)
        if updated_twin is None:
            return ObservationResponse(
                success=False,
                message="Failed to update Digital Twin",
                updated_metrics={},
            )

        return ObservationResponse(
            success=True,
            message="Observation recorded and digital twin updated",
            updated_metrics={
                "knowledge_score": updated_twin.knowledge_score,
                "confidence": updated_twin.confidence,
                "engagement": updated_twin.engagement,
                "current_topic": updated_twin.current_topic,
            },
        )

    def _build_history_entry(self, observation: ObservationCreate) -> LearningHistoryEntry:
        return LearningHistoryEntry(
            timestamp=datetime.utcnow(),
            topic=observation.topic,
            duration_minutes=observation.duration_minutes,
            notes=observation.notes,
            metadata={
                "activity_type": observation.activity_type,
                "score": observation.score,
            },
        )

    def _build_updates(self, twin: DigitalTwinResponse, observation: ObservationCreate, history_entry: LearningHistoryEntry) -> DigitalTwinUpdate:
        new_knowledge = self._compute_knowledge_score(twin, observation)
        new_engagement = self._compute_engagement(twin, observation)
        new_confidence = self._compute_confidence(twin, observation)

        updated_history = list(twin.learning_history) + [history_entry]
        updated_completed_topics = self._compute_completed_topics(twin, observation)

        return DigitalTwinUpdate(
            knowledge_score=new_knowledge,
            confidence=new_confidence,
            engagement=new_engagement,
            learning_style=twin.learning_style,
            strengths=twin.strengths,
            weaknesses=twin.weaknesses,
            learning_history=updated_history,
            revision_schedule=twin.revision_schedule,
            completed_topics=updated_completed_topics,
            current_topic=observation.topic,
        )

    def _compute_knowledge_score(self, twin: DigitalTwinResponse, observation: ObservationCreate) -> float:
        if observation.score is None:
            return twin.knowledge_score
        previous_score = twin.knowledge_score or 0.0
        previous_count = max(len(twin.learning_history), 1)
        return (previous_score * previous_count + observation.score) / (previous_count + 1)

    def _compute_engagement(self, twin: DigitalTwinResponse, observation: ObservationCreate) -> float:
        return (twin.engagement + observation.duration_minutes / 60.0) if twin.engagement is not None else observation.duration_minutes / 60.0

    def _compute_confidence(self, twin: DigitalTwinResponse, observation: ObservationCreate) -> float:
        return observation.confidence if observation.confidence is not None else twin.confidence

    def _compute_completed_topics(self, twin: DigitalTwinResponse, observation: ObservationCreate) -> list[str]:
        completed = list(twin.completed_topics)
        if observation.topic not in completed:
            completed.append(observation.topic)
        return completed
