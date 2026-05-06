from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, Text, func
from sqlmodel import Column, Field, Relationship

from domain.enums.transaction import (
    TransactionSource,
    TransactionType,
)
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.prize_redemptions import PrizeRedemption
    from infrastructure.database.models.prizes import Prize
    from infrastructure.database.models.referrals import Referral
    from infrastructure.database.models.task_completions import TaskCompletion
    from infrastructure.database.models.tasks import Task
    from infrastructure.database.models.users import User


class Transaction(BaseModel, table=True):
    """
    Журнал движения очков пользователя.

    Таблица хранит каждое начисление или списание, чтобы баланс пользователя
    был проверяемым и восстанавливаемым по истории операций.
    """

    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("balance_before >= 0", name="balance_before_non_negative"),
        CheckConstraint("balance_after >= 0", name="balance_after_non_negative"),
    )

    transactions_id: int | None = Field(default=None, primary_key=True)
    users_id: int = Field(
        foreign_key="users.users_id",
        nullable=False,
        index=True,
        description="ID пользователя, чей баланс изменяется этой операцией",
    )
    tasks_id: int | None = Field(
        default=None,
        foreign_key="tasks.tasks_id",
        index=True,
        description="ID задания, если операция является начислением или корректировкой по заданию",
    )
    prizes_id: int | None = Field(
        default=None,
        foreign_key="prizes.prizes_id",
        index=True,
        description="ID приза, если операция является списанием за приз или возвратом очков по призу",
    )
    transaction_type: TransactionType = Field(
        sa_column=Column(
            SAEnum(
                TransactionType, name="transaction_type", values_callable=enum_values
            ),
            nullable=False,
        ),
        description="Направление движения баланса: начисление увеличивает баланс, списание уменьшает",
    )
    transaction_source: TransactionSource = Field(
        sa_column=Column(
            SAEnum(
                TransactionSource,
                name="transaction_source",
                values_callable=enum_values,
            ),
            nullable=False,
        ),
        description="Бизнес-причина появления операции: регистрация, задание, приз, реферал или ручная корректировка",
    )
    amount: int = Field(
        nullable=False,
        description="Положительная сумма операции без знака; направление задаётся полем transaction_type",
    )
    balance_before: int = Field(
        nullable=False, description="Баланс пользователя до применения этой операции"
    )
    balance_after: int = Field(
        nullable=False, description="Баланс пользователя после применения этой операции"
    )
    description: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="Пояснение операции для аудита, админки и расследования ручных корректировок",
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )

    user: "User" = Relationship(back_populates="transactions")
    task: Optional["Task"] = Relationship(back_populates="transactions")
    task_completion: Optional["TaskCompletion"] = Relationship(
        back_populates="transaction"
    )
    prize: Optional["Prize"] = Relationship(back_populates="transactions")
    prize_redemption: Optional["PrizeRedemption"] = Relationship(
        back_populates="transaction"
    )
    referral_bonus: Optional["Referral"] = Relationship(
        back_populates="bonus_transaction"
    )
