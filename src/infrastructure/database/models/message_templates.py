from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlmodel import Column, Field

from infrastructure.database.base import BaseModel


class MessageTemplate(BaseModel, table=True):
    __tablename__ = "message_templates"

    message_templates_id: int | None = Field(default=None, primary_key=True)
    code: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Стабильный код шаблона сообщения",
    )
    template_text: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Переопределённый текст шаблона с placeholders вида {name}",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )
