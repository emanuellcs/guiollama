import logging
from typing import Optional

from domain.ports import LLMClient
from infra.config import Settings, get_settings
from infra.logging import configure_logging

logger = logging.getLogger(__name__)


class Container:
    """
    Dependency Injection Container.

    This class manages the lifecycle of application dependencies (Singletons).
    """

    def __init__(self) -> None:
        self._settings: Optional[Settings] = None
        self._llm_client: Optional[LLMClient] = None

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
            raise RuntimeError("LLM Client not initialized. Call register_adapter first.")
        return self._llm_client

    def register_llm_client(self, client: LLMClient) -> None:
        self._llm_client = client
        logger.info(f"Registered LLM Client: {client.__class__.__name__}")


# Global container instance
container = Container()
