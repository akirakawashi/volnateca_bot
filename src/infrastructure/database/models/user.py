from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.database.models.prize_redemption import PrizeRedemption
    from infrastructure.database.models.task_completion import TaskCompletion
    from infrastructure.database.models.transaction import Transaction


class User(BaseModel, table=True):
    """
    Таблица для хранения информации о пользователях, зарегистрированных в боте.

    Содержит идентификатор пользователя ВКонтакте, контактные данные из профиля,
    текущий баланс и агрегаты по заработанным/потраченным очкам.
    """

    __tablename__ = "user"

    user_id: int | None = Field(default=None, primary_key=True)
    vk_user_id: int = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Уникальный ID пользователя ВКонтакте, полученный из события или API VK",
    )
    first_name: str | None = Field(default=None, description="Имя пользователя")
    last_name: str | None = Field(default=None, description="Фамилия пользователя")
    mid_name: str | None = Field(default=None, description="Отчество пользователя")
    balance_points: int = Field(
        default=0,
        nullable=False,
        description="Текущий доступный баланс очков, который пользователь может потратить на призы",
    )
    earned_points_total: int = Field(
        default=0,
        nullable=False,
        description="Суммарное количество очков, заработанных пользователем за всё время проекта",
    )
    spent_points_total: int = Field(
        default=0,
        nullable=False,
        description="Суммарное количество очков, потраченных пользователем на призы и списания",
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        description="Активен ли пользователь в боте; неактивные пользователи не участвуют в новых начислениях",
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

    prize_redemptions: list["PrizeRedemption"] = Relationship(back_populates="user")
    task_completions: list["TaskCompletion"] = Relationship(back_populates="user")
    transactions: list["Transaction"] = Relationship(back_populates="user")
