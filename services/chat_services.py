import logging
from typing import AsyncIterator, List, Optional
from uuid import UUID

from domain.entities import ChatSession, Message, ModelInfo, Role
from domain.ports import ChatRepository, LLMClient

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service layer for Chat operations.
    Orchestrates persistence and LLM interaction.
    """

    def __init__(self, llm_client: LLMClient, chat_repo: ChatRepository):
        self.llm = llm_client
        self.repo = chat_repo

    async def get_all_sessions(self) -> List[ChatSession]:
        return await self.repo.list_sessions()

    async def create_new_session(self, model_name: str = "llama2") -> ChatSession:
        return await self.repo.create_session(title="New Chat", model_name=model_name)

    async def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        return await self.repo.get_session(session_id)

    async def delete_session(self, session_id: UUID) -> None:
        await self.repo.delete_session(session_id)

    async def rename_session(self, session_id: UUID, new_title: str) -> None:
        await self.repo.update_session_title(session_id, new_title)

    async def list_models(self) -> List[ModelInfo]:
        return await self.llm.list_models()

    async def stream_chat(
        self,
        session_id: UUID,
        user_input: str,
        model_name: str,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Main chat loop:
        1. Save User Message
        2. Load History
        3. Stream from LLM
        4. Save Assistant Message
        """
        # 1. Save User Message
        user_msg = Message(role=Role.USER, content=user_input)
        await self.repo.add_message(session_id, user_msg)

        # 2. Load History (re-fetch session to get context)
        session = await self.repo.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Construct context window
        # TODO: Implement context window limiting here based on token counts
        history = session.messages

        # Prepend system prompt if exists and not already there
        if system_prompt:
            # Basic check, in prod we might handle system prompts more robustly in the entity
            if not history or history[0].role != Role.SYSTEM:
                history.insert(0, Message(role=Role.SYSTEM, content=system_prompt))

        # 3. Stream from LLM
        accumulated_response = []
        try:
            stream = self.llm.chat_stream(model=model_name, messages=history)

            async for chunk in stream:
                accumulated_response.append(chunk)
                yield chunk

        except Exception as e:
            logger.error(f"Error during chat stream: {e}")
            yield f"\n\n*Error generating response: {str(e)}*"
            raise e
        finally:
            # 4. Save Assistant Message (even if partial/failed, we might want to save what we got)
            if accumulated_response:
                full_content = "".join(accumulated_response)
                ai_msg = Message(role=Role.ASSISTANT, content=full_content)
                await self.repo.add_message(session_id, ai_msg)

                # Auto-title (simple heuristic for first turn)
                if len(session.messages) <= 2:  # System + User or just User
                    short_title = user_input[:30] + "..." if len(user_input) > 30 else user_input
                    await self.repo.update_session_title(session_id, short_title)
