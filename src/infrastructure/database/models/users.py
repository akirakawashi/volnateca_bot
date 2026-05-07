from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.database.models.user_achievements import UserAchievement
    from infrastructure.database.models.prize_redemptions import PrizeRedemption
    from infrastructure.database.models.referrals import Referral
    from infrastructure.database.models.task_completions import TaskCompletion
    from infrastructure.database.models.transactions import Transaction
    from infrastructure.database.models.user_daily_activities import UserDailyActivity


class User(BaseModel, table=True):
    """
    Таблица для хранения информации о пользователях, зарегистрированных в боте.

    Содержит идентификатор пользователя ВКонтакте, контактные данные из профиля,
    текущий баланс и агрегаты по заработанным/потраченным очкам.
    """

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("balance_points >= 0", name="balance_points_non_negative"),
        CheckConstraint("earned_points_total >= 0", name="earned_points_total_non_negative"),
        CheckConstraint("spent_points_total >= 0", name="spent_points_total_non_negative"),
    )

    users_id: int | None = Field(default=None, primary_key=True)
    vk_user_id: int = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Уникальный ID пользователя ВКонтакте, полученный из события или API VK",
    )
    first_name: str | None = Field(default=None, description="Имя пользователя")
    last_name: str | None = Field(default=None, description="Фамилия пользователя")
    vk_screen_name: str | None = Field(
        default=None,
        index=True,
        description="Короткий адрес профиля ВКонтакте, например akirakawashii",
    )
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

    sent_referrals: list["Referral"] = Relationship(
        back_populates="inviter",
        sa_relationship_kwargs={"foreign_keys": "Referral.inviter_users_id"},
    )
    received_referral: Optional["Referral"] = Relationship(
        back_populates="invited",
        sa_relationship_kwargs={
            "foreign_keys": "Referral.invited_users_id",
            "uselist": False,
        },
    )
    daily_activities: list["UserDailyActivity"] = Relationship(back_populates="user")
    user_achievements: list["UserAchievement"] = Relationship(back_populates="user")
    prize_redemptions: list["PrizeRedemption"] = Relationship(back_populates="user")
    task_completions: list["TaskCompletion"] = Relationship(back_populates="user")
    transactions: list["Transaction"] = Relationship(back_populates="user")
