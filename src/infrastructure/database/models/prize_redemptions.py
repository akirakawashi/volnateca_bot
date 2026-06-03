from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, Index, Text, UniqueConstraint, func
from sqlmodel import Column, Field, Relationship

from domain.enums.prize import PrizeReceiveType, PrizeRedemptionStatus
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.prizes import Prize
    from infrastructure.database.models.transactions import Transaction
    from infrastructure.database.models.users import User


class PrizeRedemption(BaseModel, table=True):
    """
    Факт получения или резерва приза пользователем.

    Таблица отделяет справочник призов от конкретных пользовательских заявок:
    кто какой приз запросил, сколько очков было списано и в каком статусе выдача.
    """

    __tablename__ = "prize_redemptions"
    __table_args__ = (
        CheckConstraint("points_spent >= 0", name="points_spent_non_negative"),
        Index(
            "ix_prize_redemptions_users_id_status",
            "users_id",
            "prize_redemption_status",
        ),
        Index(
            "ix_prize_redemptions_prizes_id_status",
            "prizes_id",
            "prize_redemption_status",
        ),
        Index(
            "ix_prize_redemptions_status_created_at",
            "prize_redemption_status",
            "created_at",
        ),
        UniqueConstraint(
            "users_id",
            "idempotency_key",
            name="uq_prize_redemptions_users_id_idempotency_key",
        ),
    )

    prize_redemptions_id: int | None = Field(default=None, primary_key=True)
    users_id: int = Field(
        foreign_key="users.users_id",
        nullable=False,
        index=True,
        description="ID пользователя, который запросил или получил приз",
    )
    prizes_id: int = Field(
        foreign_key="prizes.prizes_id",
        nullable=False,
        index=True,
        description="ID приза, который пользователь запросил или получил",
    )
    transactions_id: int = Field(
        foreign_key="transactions.transactions_id",
        nullable=False,
        unique=True,
        description="ID транзакции списания очков за получение приза",
    )
    refund_transactions_id: int | None = Field(
        default=None,
        foreign_key="transactions.transactions_id",
        unique=True,
        description="ID транзакции возврата очков при отмене заявки",
    )
    prize_redemption_status: PrizeRedemptionStatus = Field(
        default=PrizeRedemptionStatus.RESERVED,
        sa_column=Column(
            SAEnum(
                PrizeRedemptionStatus,
                name="prize_redemption_status",
                values_callable=enum_values,
            ),
            nullable=False,
        ),
        description="Статус пользовательской заявки на приз",
    )
    receive_type: PrizeReceiveType = Field(
        sa_column=Column(
            SAEnum(
                PrizeReceiveType,
                name="prize_receive_type",
                values_callable=enum_values,
            ),
            nullable=False,
        ),
        description="Фактический способ получения приза на момент заявки",
    )
    redemption_code: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Код заявки для пункта выдачи",
    )
    idempotency_key: str = Field(
        nullable=False,
        description="Ключ идемпотентности покупки из VK",
    )
    points_spent: int = Field(
        nullable=False,
        description="Количество очков, списанное за получение приза",
    )
    comment: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="Комментарий пользователя или служебная пометка по выдаче",
    )
    issued_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Дата и время фактической выдачи приза",
    )
    canceled_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Дата и время отмены заявки",
    )
    cancel_reason: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="Причина отмены заявки",
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

    user: "User" = Relationship(back_populates="prize_redemptions")
    prize: "Prize" = Relationship(back_populates="prize_redemptions")
    transaction: "Transaction" = Relationship(
        back_populates="prize_redemption",
        sa_relationship_kwargs={"foreign_keys": "[PrizeRedemption.transactions_id]"},
    )
    refund_transaction: Optional["Transaction"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PrizeRedemption.refund_transactions_id]"},
    )
