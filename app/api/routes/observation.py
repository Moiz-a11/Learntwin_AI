from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.schemas.observation import ObservationCreate, ObservationResponse
from app.services.observation_service import ObservationService

router = APIRouter(prefix="/observation", tags=["Observation"])


@router.post("/", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED, summary="Record an observation", description="Record a learning observation and update the learner's digital twin.")
def record_observation(payload: ObservationCreate, db=Depends(get_db)) -> ObservationResponse:
    service = ObservationService(db)
    response = service.record_observation(payload)
    if not response.success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    return response
