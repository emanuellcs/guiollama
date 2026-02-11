import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, desc, select
from sqlalchemy.orm import selectinload

from adapters.db import SessionLocal
from adapters.orm import ChatSessionModel, MessageModel
from domain.entities import ChatSession, Message, Role
from domain.ports import ChatRepository

logger = logging.getLogger(__name__)


class SqlAlchemyChatRepository(ChatRepository):
    """
    SQLAlchemy implementation of the ChatRepository port.
    """

    def _to_domain_session(self, model: ChatSessionModel) -> ChatSession:
        return ChatSession(
            id=UUID(model.id),
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
            model_name=model.model_name,
            messages=[
                Message(
                    id=UUID(m.id),
                    role=Role(m.role),
                    content=m.content,
                    created_at=m.created_at,
                    metadata=m.metadata_,
                )
                for m in model.messages
            ],
        )

    async def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        with SessionLocal() as db:
            stmt = (
                select(ChatSessionModel)
                .options(selectinload(ChatSessionModel.messages))
                .where(ChatSessionModel.id == str(session_id))
            )
            model = db.execute(stmt).scalar_one_or_none()
            if model:
                return self._to_domain_session(model)
            return None

    async def create_session(self, title: str, model_name: str) -> ChatSession:
        with SessionLocal() as db:
            model = ChatSessionModel(title=title, model_name=model_name)
            db.add(model)
            db.commit()
            db.refresh(model)
            return self._to_domain_session(model)

    async def add_message(self, session_id: UUID, message: Message) -> None:
        with SessionLocal() as db:
            model = MessageModel(
                id=str(message.id),
                session_id=str(session_id),
                role=message.role.value,
                content=message.content,
                created_at=message.created_at,
                metadata_=message.metadata,
            )
            db.add(model)
            # Update session timestamp
            session_stmt = select(ChatSessionModel).where(ChatSessionModel.id == str(session_id))
            session = db.execute(session_stmt).scalar_one()
            session.updated_at = message.created_at

            db.commit()

    async def list_sessions(self) -> List[ChatSession]:
        with SessionLocal() as db:
            # For listing, we might not need all messages, but for simplicity we load them or just header info
            # Optimization: don't load messages for list view if not needed.
            # Here we keep it simple.
            stmt = select(ChatSessionModel).order_by(desc(ChatSessionModel.updated_at))
            models = db.execute(stmt).scalars().all()
            # We map without messages for the list view to be faster?
            # Let's return full objects for consistency for now, but in prod we'd split this.
            return [
                ChatSession(
                    id=UUID(m.id),
                    title=m.title,
                    created_at=m.created_at,
                    updated_at=m.updated_at,
                    model_name=m.model_name,
                    messages=[],  # Lazy load optimization: empty messages in list view
                )
                for m in models
            ]

    async def update_session_title(self, session_id: UUID, title: str) -> None:
        with SessionLocal() as db:
            stmt = select(ChatSessionModel).where(ChatSessionModel.id == str(session_id))
            model = db.execute(stmt).scalar_one_or_none()
            if model:
                model.title = title
                db.commit()

    async def delete_session(self, session_id: UUID) -> None:
        with SessionLocal() as db:
            stmt = delete(ChatSessionModel).where(ChatSessionModel.id == str(session_id))
            db.execute(stmt)
            db.commit()
