from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, UniqueConstraint, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.database.models.transactions import Transaction
    from infrastructure.database.models.users import User


class Referral(BaseModel, table=True):
    """
    Факт приглашения одного пользователя другим.

    Таблица нужна, чтобы один приглашённый пользователь не дал реферальный
    бонус несколько раз и чтобы можно было связать бонус с транзакцией.
    """

    __tablename__ = "referrals"
    __table_args__ = (
        UniqueConstraint("invited_users_id", name="uq_referrals_invited_users_id"),
        UniqueConstraint("bonus_transactions_id", name="uq_referrals_bonus_transactions_id"),
        CheckConstraint("inviter_users_id <> invited_users_id", name="different_users"),
    )

    referrals_id: int | None = Field(default=None, primary_key=True)
    inviter_users_id: int = Field(
        foreign_key="users.users_id",
        nullable=False,
        index=True,
        description="ID пользователя, который пригласил друга",
    )
    invited_users_id: int = Field(
        foreign_key="users.users_id",
        nullable=False,
        index=True,
        description="ID пользователя, который зарегистрировался по приглашению",
    )
    bonus_transactions_id: int | None = Field(
        default=None,
        foreign_key="transactions.transactions_id",
        description="ID транзакции начисления реферального бонуса пригласившему пользователю",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )

    inviter: "User" = Relationship(
        back_populates="sent_referrals",
        sa_relationship_kwargs={"foreign_keys": "Referral.inviter_users_id"},
    )
    invited: "User" = Relationship(
        back_populates="received_referral",
        sa_relationship_kwargs={"foreign_keys": "Referral.invited_users_id"},
    )
    bonus_transaction: Optional["Transaction"] = Relationship(back_populates="referral_bonus")
