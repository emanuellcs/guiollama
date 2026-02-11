import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), default="New Chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    model_name: Mapped[str] = mapped_column(String(100), default="llama2")

    # Relationships
    messages: Mapped[list["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="MessageModel.created_at",
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "model_name": self.model_name,
        }


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(50))  # system, user, assistant
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    # Relationships
    session: Mapped["ChatSessionModel"] = relationship(
        "ChatSessionModel", back_populates="messages"
    )
