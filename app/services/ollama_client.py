"""Client for communicating with a local Ollama server."""

import logging
from json import JSONDecodeError
from typing import Any, Callable, Optional

import httpx

from app.core.config import settings


class OllamaClient:
    """Asynchronous client for Ollama model inference."""

    def __init__(self, host: Optional[str] = None, model: Optional[str] = None) -> None:
        self.host = host or settings.OLLAMA_HOST
        self.model = model or settings.OLLAMA_MODEL
        self.logger = logging.getLogger(__name__)
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        self.max_retries = 1

    async def generate(self, prompt: str) -> str:
        """Generate a completion from Ollama using a single prompt.

        Args:
            prompt: The text prompt to send to Ollama.

        Returns:
            The generated text, or an empty string on failure.
        """
        payload = {"model": self.model, "prompt": prompt}
        response = await self._post_json("/generate", payload)
        return self._parse_text_response(response)

    async def chat(self, messages: list[dict]) -> str:
        """Send a chat-style message sequence to Ollama.

        Args:
            messages: A list of message objects compatible with Ollama.

        Returns:
            The chat response text, or an empty string on failure.
        """
        payload = {"model": self.model, "messages": messages}
        response = await self._post_json("/chat", payload)
        return self._parse_text_response(response)

    async def health_check(self) -> bool:
        """Check whether the Ollama server is reachable and healthy.

        Returns:
            True if the server responds successfully, False otherwise.
        """
        url = self._build_url("/health")
        response = await self._send_request("GET", url)
        return response is not None

    async def _post_json(self, path: str, payload: dict[str, Any]) -> Optional[dict[str, Any]]:
        url = self._build_url(path)
        return await self._send_request("POST", url, json=payload)

    def _build_url(self, path: str) -> str:
        return f"{self.host.rstrip('/')}/{path.lstrip('/')}"

    async def _send_request(self, method: str, url: str, **kwargs: Any) -> Optional[dict[str, Any]]:
        attempt = 0
        while attempt <= self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError, JSONDecodeError, ValueError) as exc:
                self.logger.warning(
                    "Ollama request failed on attempt %d/%d for %s: %s",
                    attempt + 1,
                    self.max_retries + 1,
                    url,
                    exc,
                )
                if attempt < self.max_retries:
                    attempt += 1
                    continue
                self.logger.error("Ollama request permanently failed: %s", exc)
                return None

    def _parse_text_response(self, response: Optional[dict[str, Any]]) -> str:
        if not response or not isinstance(response, dict):
            self.logger.error("Invalid Ollama response payload: %r", response)
            return ""

        if "output" in response:
            output = response["output"]
            if isinstance(output, str):
                return output
            if isinstance(output, list):
                return "".join(str(item) for item in output)
            return str(output)

        if "text" in response and isinstance(response["text"], str):
            return response["text"]

        if "results" in response and isinstance(response["results"], list):
            parts = []
            for item in response["results"]:
                if isinstance(item, dict) and "content" in item:
                    parts.append(str(item["content"]))
                else:
                    parts.append(str(item))
            return "".join(parts)

        self.logger.error("Unable to parse Ollama response fields: %s", list(response.keys()))
        return ""
