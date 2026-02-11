import json
import logging
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from domain.entities import Message, ModelInfo
from domain.exceptions import LLMConnectionError, LLMException
from domain.ports import LLMClient

logger = logging.getLogger(__name__)


class OllamaClient(LLMClient):
    """
    Implementation of LLMClient for Ollama.
    Uses httpx for async HTTP requests.
    """

    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}

    async def _handle_request_error(self, e: Exception, context: str) -> None:
        logger.error(f"Ollama request failed during {context}: {str(e)}")
        if isinstance(e, httpx.ConnectError):
            raise LLMConnectionError(f"Could not connect to Ollama at {self.base_url}") from e
        raise LLMException(f"Ollama error: {str(e)}") from e

    async def list_models(self) -> List[ModelInfo]:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                models = []
                for m in data.get("models", []):
                    # Parse ISO format timestamp provided by Ollama
                    # Example: "2023-11-04T15:23:45.123456Z"
                    try:
                        # Python 3.11 fromisoformat handles 'Z'
                        modified_at = datetime.fromisoformat(m.get("modified_at", ""))
                    except ValueError:
                        modified_at = datetime.now()

                    models.append(
                        ModelInfo(
                            name=m.get("name", "unknown"),
                            size=m.get("size", 0),
                            digest=m.get("digest", ""),
                            modified_at=modified_at,
                            details=m.get("details", {}),
                        )
                    )
                return models
        except Exception as e:
            await self._handle_request_error(e, "list_models")
            return []

    async def chat_stream(
        self, model: str, messages: List[Message], options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        url = f"{self.base_url}/api/chat"

        # Convert domain messages to Ollama API format
        api_messages = [{"role": msg.role.value, "content": msg.content} for msg in messages]

        payload = {
            "model": model,
            "messages": api_messages,
            "stream": True,
        }

        if options:
            payload["options"] = options

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST", url, json=payload, headers=self.headers
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)

                            if chunk.get("done", False):
                                # Could capture total_duration here if needed
                                break

                            if "message" in chunk:
                                content = chunk["message"].get("content", "")
                                if content:
                                    yield content

                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode JSON chunk: {line}")
                            continue
        except Exception as e:
            await self._handle_request_error(e, "chat_stream")

    async def pull_model(self, name: str) -> AsyncIterator[dict]:
        url = f"{self.base_url}/api/pull"
        payload = {"name": name, "stream": True}

        try:
            async with httpx.AsyncClient(timeout=None) as client:  # No timeout for long downloads
                async with client.stream(
                    "POST", url, json=payload, headers=self.headers
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            yield data
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            await self._handle_request_error(e, "pull_model")

    async def delete_model(self, name: str) -> bool:
        url = f"{self.base_url}/api/delete"
        payload = {"name": name}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return True
        except Exception as e:
            await self._handle_request_error(e, "delete_model")
            return False
