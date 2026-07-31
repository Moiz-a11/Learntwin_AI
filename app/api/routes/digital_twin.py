from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_settings
from app.db.database import get_db
from app.schemas.digital_twin import (
    DigitalTwinCreate,
    DigitalTwinResponse,
    DigitalTwinUpdate,
)
from app.services.digital_twin_service import DigitalTwinService

router = APIRouter(prefix="/digital-twin", tags=["Digital Twin"])


@router.post("/", response_model=DigitalTwinResponse, status_code=status.HTTP_201_CREATED, summary="Create a digital twin", description="Create a new learner digital twin record.")
def create_digital_twin(
    payload: DigitalTwinCreate,
    db=Depends(get_db),
) -> DigitalTwinResponse:
    service = DigitalTwinService(db)
    return service.create_twin(payload)


@router.get("/{user_id}", response_model=DigitalTwinResponse, summary="Get a digital twin", description="Retrieve a learner digital twin by the provided user_id.")
def get_digital_twin(user_id: str, db=Depends(get_db)) -> DigitalTwinResponse:
    service = DigitalTwinService(db)
    twin = service.get_twin(user_id)
    if twin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Digital Twin not found")
    return twin


@router.put("/{user_id}", response_model=DigitalTwinResponse, summary="Update a digital twin", description="Apply a partial update to the learner's digital twin.")
def update_digital_twin(user_id: str, payload: DigitalTwinUpdate, db=Depends(get_db)) -> DigitalTwinResponse:
    service = DigitalTwinService(db)
    twin = service.update_twin(user_id, payload)
    if twin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Digital Twin not found")
    return twin


@router.delete("/{user_id}", summary="Delete a digital twin", description="Delete the learner's digital twin.", status_code=status.HTTP_200_OK)
def delete_digital_twin(user_id: str, db=Depends(get_db)) -> dict:
    service = DigitalTwinService(db)
    deleted = service.delete_twin(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Digital Twin not found")
    return {"success": True}


@router.get("/", response_model=List[DigitalTwinResponse], summary="List digital twins", description="List learner digital twins with pagination.")
def list_digital_twins(limit: int = 100, offset: int = 0, db=Depends(get_db)) -> List[DigitalTwinResponse]:
    service = DigitalTwinService(db)
    return service.list_twins(limit=limit, offset=offset)
