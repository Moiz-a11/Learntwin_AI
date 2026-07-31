from fastapi import FastAPI

from app.api.v1.routes import router as api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="LearnTwin AI Core backend",
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
def root() -> dict:
    return {"status": "ok", "service": settings.APP_NAME}
