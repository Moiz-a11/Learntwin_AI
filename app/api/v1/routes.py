from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "healthy"}


# Phase 1: routes will be expanded in later phases once the API contract is finalized.
