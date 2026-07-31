"""Ollama integration placeholder.

Phase 1: no business logic is implemented here. Concrete integration comes later.
"""

from typing import Optional


class OllamaClient:
    def __init__(self, api_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_url = api_url
        self.model = model
