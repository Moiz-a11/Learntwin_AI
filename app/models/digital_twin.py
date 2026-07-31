from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    JSON,
    DateTime,
    Text,
)

from app.db.base import Base


class DigitalTwinState(Base):
    """SQLAlchemy model representing a learner's digital twin.

    This table stores a compact representation of the learner's state used by
    the recommendation and personalization systems.
    """

    __tablename__ = "digital_twin_state"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), nullable=False, unique=True, index=True)

    # Core learner metrics
    knowledge_score = Column(Float, nullable=True, default=0.0, index=True)
    confidence = Column(Float, nullable=True, default=0.0, index=True)
    engagement = Column(Float, nullable=True, default=0.0, index=True)

    # Profile and preferences
    learning_style = Column(String(64), nullable=True)
    strengths = Column(JSON, nullable=True, default=list)
    weaknesses = Column(JSON, nullable=True, default=list)

    # History and schedule
    learning_history = Column(JSON, nullable=True, default=list)
    revision_schedule = Column(JSON, nullable=True, default=dict)

    # Topic tracking
    completed_topics = Column(JSON, nullable=True, default=list)
    current_topic = Column(String(256), nullable=True)

    # Optional free-form summary and timestamps
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
