class LLMException(Exception):
    """Base exception for LLM related errors."""

    pass


class LLMConnectionError(LLMException):
    """Raised when the LLM provider cannot be reached."""

    pass


class LLMModelNotFoundError(LLMException):
    """Raised when a requested model is not found."""

    pass
