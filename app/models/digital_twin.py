from sqlalchemy import Column, Integer, String

from app.db.base import Base


class DigitalTwinState(Base):
    __tablename__ = "digital_twin_state"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), nullable=False, unique=True, index=True)
