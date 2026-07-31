"""Service layer for Digital Twin operations.

This module contains the business-facing service class that delegates
persistence to the repository and translates between Pydantic models and
ORM models.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories.digital_twin_repository import (
    create as repo_create,
    delete as repo_delete,
    get_by_student_id as repo_get_by_student_id,
    list_all as repo_list_all,
    update as repo_update,
)
from app.schemas.digital_twin import (
    DigitalTwinCreate,
    DigitalTwinResponse,
    DigitalTwinUpdate,
)
from app.models.digital_twin import DigitalTwinState


class DigitalTwinService:
    """Service for managing learner digital twins.

    This class encapsulates business-facing operations and keeps SQLAlchemy
    models isolated inside the service layer.
    """

    def __init__(self, db: Session) -> None:
        """Initialize the service with a SQLAlchemy session."""
        self._db = db

    def create_twin(self, data: DigitalTwinCreate) -> DigitalTwinResponse:
        """Create a new Digital Twin from validated data."""
        payload = self._to_dict(data)
        twin = repo_create(self._db, payload)
        return self._to_response(twin)

    def get_twin(self, user_id: str) -> Optional[DigitalTwinResponse]:
        """Return a Digital Twin response for the specified user id."""
        twin = repo_get_by_student_id(self._db, user_id)
        if twin is None:
            return None
        return self._to_response(twin)

    def update_twin(self, user_id: str, data: DigitalTwinUpdate) -> Optional[DigitalTwinResponse]:
        """Update an existing Digital Twin and return the updated response."""
        existing = repo_get_by_student_id(self._db, user_id)
        if existing is None:
            return None

        updates = self._to_dict(data, exclude_unset=True)
        if not updates:
            return self._to_response(existing)

        twin = repo_update(self._db, user_id, updates)
        if twin is None:
            return None
        return self._to_response(twin)

    def delete_twin(self, user_id: str) -> bool:
        """Delete the Digital Twin for the specified user id."""
        existing = repo_get_by_student_id(self._db, user_id)
        if existing is None:
            return False
        return repo_delete(self._db, user_id)

    def list_twins(self, limit: int = 100, offset: int = 0) -> List[DigitalTwinResponse]:
        """Return a list of Digital Twin responses in pagination order."""
        twins = repo_list_all(self._db, limit=limit, offset=offset)
        return [self._to_response(twin) for twin in twins]

    def _to_response(self, twin: DigitalTwinState) -> DigitalTwinResponse:
        """Convert an ORM model into a Pydantic response model."""
        return DigitalTwinResponse.from_orm(twin)

    def _to_dict(self, data: DigitalTwinCreate | DigitalTwinUpdate, exclude_unset: bool = False) -> dict:
        """Convert a Pydantic model into a plain dict for repository persistence."""
        return data.model_dump(exclude_unset=exclude_unset)
