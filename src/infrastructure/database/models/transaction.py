from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, Text, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.prize import Prize
    from infrastructure.database.models.task import Task
    from infrastructure.database.models.task_completion import TaskCompletion
    from infrastructure.database.models.user import User


class TransactionType(str, Enum):
    ACCRUAL = "accrual"  # Начисление очков пользователю
    SPEND = "spend"  # Списание очков с баланса пользователя


class TransactionSource(str, Enum):
    REGISTRATION = "registration"  # Начисление за регистрацию в боте
    TASK = "task"  # Начисление за выполнение задания или списание за невыполнение
    PRIZE = "prize"  # Списание за покупку приза или возврат очков при отмене приза
    REFERRAL = "referral"  # Начисление за приглашенного друга, который зарегистрировался и выполнил условия
    ADJUSTMENT = "adjustment"  # Ручная корректировка баланса администратором


class TransactionStatus(str, Enum):
    PENDING = (
        "pending"  # Операция ожидает обработки (например, проверка выполнения задания)
    )
    COMPLETED = "completed"  # Операция успешно завершена и баланс обновлен
    CANCELED = "canceled"  # Операция отменена (например, задание не выполнено в срок или приз отменен)


class Transaction(BaseModel, table=True):
    """
    Журнал движения очков пользователя.

    Таблица хранит каждое начисление или списание, чтобы баланс пользователя
    был проверяемым и восстанавливаемым по истории операций.
    """

    __tablename__ = "transaction"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("balance_before >= 0", name="balance_before_non_negative"),
        CheckConstraint("balance_after >= 0", name="balance_after_non_negative"),
    )

    transaction_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="user.user_id",
        nullable=False,
        index=True,
        description="ID пользователя, чей баланс изменяется этой операцией",
    )
    task_id: int | None = Field(
        default=None,
        foreign_key="task.task_id",
        index=True,
        description="ID задания, если операция является начислением или корректировкой по заданию",
    )
    prize_id: int | None = Field(
        default=None,
        foreign_key="prize.prize_id",
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
    transaction_status: TransactionStatus = Field(
        default=TransactionStatus.COMPLETED,
        sa_column=Column(
            SAEnum(
                TransactionStatus,
                name="transaction_status",
                values_callable=enum_values,
            ),
            nullable=False,
        ),
        description="Статус применения операции к балансу пользователя",
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
