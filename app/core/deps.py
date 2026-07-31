from functools import lru_cache
from typing import Callable

from app.core.config import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance for dependency injection.

    Use this with FastAPI dependencies (e.g. `Depends(get_settings)`) so the
    Settings object is constructed once and reused across requests.
    """
    return Settings()
