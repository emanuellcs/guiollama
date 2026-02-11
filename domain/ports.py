from typing import AsyncIterator, List, Protocol, runtime_checkable

from guiollama.domain.entities import Message, ModelInfo


@runtime_checkable
class LLMClient(Protocol):
    """Interface for interacting with the LLM provider (Ollama)."""

    async def list_models(self) -> List[ModelInfo]:
        """Fetch list of available models."""
        ...

    async def chat_stream(
        self, model: str, messages: List[Message], options: dict | None = None
    ) -> AsyncIterator[str]:
        """Stream chat completion."""
        ...

    async def pull_model(self, name: str) -> AsyncIterator[dict]:
        """Pull a model, yielding progress updates."""
        ...

    async def delete_model(self, name: str) -> bool:
        """Delete a model."""
        ...
