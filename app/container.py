import logging
from typing import Optional

from adapters.chat_repository import SqlAlchemyChatRepository
from adapters.ollama_client import OllamaClient
from domain.ports import ChatRepository, LLMClient
from infra.config import Settings, get_settings
from infra.logging import configure_logging
from services.chat_services import ChatService

logger = logging.getLogger(__name__)


class Container:
    """
    Dependency Injection Container.

    This class manages the lifecycle of application dependencies (Singletons).
    """

    def __init__(self) -> None:
        self._settings: Optional[Settings] = None
        self._llm_client: Optional[LLMClient] = None
        self._chat_repo: Optional[ChatRepository] = None
        self._chat_service: Optional[ChatService] = None

    @property
    def settings(self) -> Settings:
        if self._settings is None:
            self._settings = get_settings()
            configure_logging(self._settings.log_level, self._settings.environment)
            logger.info("Settings loaded and logging configured.")
        return self._settings

    @property
    def llm_client(self) -> LLMClient:
        if self._llm_client is None:
            # Auto-register default adapter
            self._llm_client = OllamaClient(
                base_url=self.settings.OLLAMA_BASE_URL, timeout=self.settings.OLLAMA_TIMEOUT
            )
        return self._llm_client

    @property
    def chat_repo(self) -> ChatRepository:
        if self._chat_repo is None:
            self._chat_repo = SqlAlchemyChatRepository()
        return self._chat_repo

    @property
    def chat_service(self) -> ChatService:
        if self._chat_service is None:
            self._chat_service = ChatService(llm_client=self.llm_client, chat_repo=self.chat_repo)
        return self._chat_service


# Global container instance
container = Container()
