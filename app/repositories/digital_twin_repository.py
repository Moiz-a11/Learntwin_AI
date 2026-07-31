"""Repository layer for Digital Twin persistence.

This module provides simple CRUD operations using a SQLAlchemy `Session`.
It contains no business logic or AI integrations — just direct DB access.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.digital_twin import DigitalTwinState


def create(db: Session, values: Dict[str, Any]) -> DigitalTwinState:
    """Create a new DigitalTwinState record.

    Args:
        db: SQLAlchemy Session
        values: dict of field values to set on the model

    Returns:
        The persisted DigitalTwinState instance (with identity populated).
    """
    twin = DigitalTwinState(**values)
    db.add(twin)
    db.commit()
    db.refresh(twin)
    return twin


def get_by_student_id(db: Session, user_id: str) -> Optional[DigitalTwinState]:
    """Return a DigitalTwinState by `user_id` or `None` if not found."""
    return db.query(DigitalTwinState).filter(DigitalTwinState.user_id == user_id).first()


def update(db: Session, user_id: str, updates: Dict[str, Any]) -> Optional[DigitalTwinState]:
    """Apply a partial update to the DigitalTwinState identified by `user_id`.

    Args:
        db: SQLAlchemy Session
        user_id: identifier of the learner
        updates: dictionary of attributes to update

    Returns:
        The updated DigitalTwinState or None if no record was found.
    """
    twin = get_by_student_id(db, user_id)
    if not twin:
        return None
    for key, val in updates.items():
        if hasattr(twin, key):
            setattr(twin, key, val)
    db.add(twin)
    db.commit()
    db.refresh(twin)
    return twin


def delete(db: Session, user_id: str) -> bool:
    """Delete the DigitalTwinState for `user_id`.

    Returns True if a record was deleted, False otherwise.
    """
    twin = get_by_student_id(db, user_id)
    if not twin:
        return False
    db.delete(twin)
    db.commit()
    return True


def list_all(db: Session, limit: int = 100, offset: int = 0) -> List[DigitalTwinState]:
    """Return a paginated list of DigitalTwinState records."""
    return db.query(DigitalTwinState).offset(offset).limit(limit).all()
