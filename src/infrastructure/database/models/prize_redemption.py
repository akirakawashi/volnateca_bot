from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, Text, func
from sqlmodel import Column, Field, Relationship

from domain.enums.prize import PrizeReceiveType, PrizeRedemptionStatus
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.prize import Prize
    from infrastructure.database.models.transaction import Transaction
    from infrastructure.database.models.user import User


class PrizeRedemption(BaseModel, table=True):
    """
    Факт получения или резерва приза пользователем.

    Таблица отделяет справочник призов от конкретных пользовательских заявок:
    кто какой приз запросил, сколько очков было списано и в каком статусе выдача.
    """

    __tablename__ = "prize_redemptions"
    __table_args__ = (
        CheckConstraint("points_spent >= 0", name="points_spent_non_negative"),
    )

    prize_redemptions_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="user.user_id",
        nullable=False,
        index=True,
        description="ID пользователя, который запросил или получил приз",
    )
    prize_id: int = Field(
        foreign_key="prize.prize_id",
        nullable=False,
        index=True,
        description="ID приза, который пользователь запросил или получил",
    )
    transaction_id: int | None = Field(
        default=None,
        foreign_key="transaction.transaction_id",
        unique=True,
        description="ID транзакции списания очков за получение приза",
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
            SAEnum(PrizeReceiveType, name="prize_receive_type", values_callable=enum_values),
            nullable=False,
        ),
        description="Фактический способ получения приза на момент заявки",
    )
    points_spent: int = Field(
        nullable=False,
        description="Количество очков, списанное или зарезервированное за получение приза",
    )
    comment: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="Служебный комментарий по выдаче приза",
    )
    issued_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Дата и время фактической выдачи приза или отправки промокода",
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
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
    transaction: Optional["Transaction"] = Relationship(back_populates="prize_redemption")
