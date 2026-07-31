from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "LearnTwin AI Core"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str
    OLLAMA_API_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "qwen2.5-vl"
    CHROMA_PERSIST_DIR: Path = Path(".chromadb")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
