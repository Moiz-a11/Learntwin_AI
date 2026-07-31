"""Database engine and session factory.

Provides a single engine and the `get_db` dependency for FastAPI. The engine
is created with `future=True` and `pool_pre_ping=True` to improve resiliency
against stale connections (useful for desktop deployments and some hosting
environments).
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger("learntwin.db")

# Create engine with pool pre-ping to avoid stale connections
engine = create_engine(
    settings.DATABASE_URL, future=True, pool_pre_ping=True
)

logger.info("Database engine created")

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    """Yield a SQLAlchemy session and ensure it is closed after use.

    Intended to be used as a FastAPI dependency: `Depends(get_db)`.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
