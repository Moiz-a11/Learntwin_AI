import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import router as api_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger("learntwin")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Starting LearnTwin AI Core application")
    app.state.logger = logger


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Shutting down LearnTwin AI Core application")


@app.get("/", tags=["root"])
def root() -> dict:
    return {"status": "ok", "service": settings.APP_NAME}
