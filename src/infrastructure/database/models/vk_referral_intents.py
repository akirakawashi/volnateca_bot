from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint, func
from sqlmodel import Column, Field

from infrastructure.database.base import BaseModel


class VKReferralIntent(BaseModel, table=True):
    """Временное сохранение ref до согласия пользователя на регистрацию."""

    __tablename__ = "vk_referral_intents"
    __table_args__ = (
        UniqueConstraint("invited_vk_user_id", name="uq_vk_referral_intents_invited_vk_user_id"),
    )

    vk_referral_intents_id: int | None = Field(default=None, primary_key=True)
    invited_vk_user_id: int = Field(
        nullable=False,
        index=True,
        description="VK ID пользователя, который пришёл по реферальной ссылке",
    )
    raw_ref: str = Field(
        nullable=False,
        description="Исходный ref из VK deep link до регистрации пользователя",
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
