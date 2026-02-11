from typing import AsyncIterator, List, Optional, Protocol, runtime_checkable
from uuid import UUID

from domain.entities import ChatSession, Message, ModelInfo


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


@runtime_checkable
class ChatRepository(Protocol):
    """Interface for persisting chat sessions and messages."""

    async def get_session(self, session_id: UUID) -> Optional[ChatSession]: ...

    async def create_session(self, title: str, model_name: str) -> ChatSession: ...

    async def add_message(self, session_id: UUID, message: Message) -> None: ...

    async def list_sessions(self) -> List[ChatSession]: ...

    async def update_session_title(self, session_id: UUID, title: str) -> None: ...

    async def delete_session(self, session_id: UUID) -> None: ...
