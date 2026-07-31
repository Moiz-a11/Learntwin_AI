from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    APP_NAME: str = "LearnTwin AI Core"
    APP_VERSION: str = "0.1.0"
    DESCRIPTION: str = "Offline desktop AI learning companion backend"
    DATABASE_URL: str
    OLLAMA_API_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "qwen2.5-vl"
    CHROMA_PERSIST_DIR: Path = Path(".chromadb")
    LOG_LEVEL: str = "INFO"
    BACKEND_CORS_ORIGINS: str = "http://localhost,http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
