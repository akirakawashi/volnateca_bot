from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Text, UniqueConstraint, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.database.models.achievements import Achievement
    from infrastructure.database.models.transactions import Transaction
    from infrastructure.database.models.users import User


class UserAchievement(BaseModel, table=True):
    """
    Факт выдачи достижения пользователю.

    Таблица защищает от повторного начисления одного и того же бонуса:
    разового, недельного или месячного.
    """

    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint(
            "users_id",
            "achievements_id",
            "achievement_key",
            name="uq_user_achievements_users_achievements_key",
        ),
        CheckConstraint("points_awarded > 0", name="points_awarded_positive"),
    )

    user_achievements_id: int | None = Field(default=None, primary_key=True)
    users_id: int = Field(
        foreign_key="users.users_id",
        nullable=False,
        index=True,
        description="ID пользователя, которому выдано достижение",
    )
    achievements_id: int = Field(
        foreign_key="achievements.achievements_id",
        nullable=False,
        index=True,
        description="ID достижения, которое выдано пользователю",
    )
    transactions_id: int = Field(
        foreign_key="transactions.transactions_id",
        nullable=False,
        unique=True,
        description="ID транзакции начисления очков за достижение",
    )
    achievement_key: str = Field(
        nullable=False,
        index=True,
        description=(
            "Ключ периода выдачи достижения. "
            "Для once используется 'once', для weekly 'week_01', "
            "для monthly '2026-07'."
        ),
    )
    points_awarded: int = Field(
        nullable=False,
        description="Фактически начисленное количество очков за достижение",
    )
    comment: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="Служебный комментарий по выдаче достижения",
    )
    awarded_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )

    user: "User" = Relationship(back_populates="user_achievements")
    achievement: "Achievement" = Relationship(back_populates="user_achievements")
    transaction: "Transaction" = Relationship(back_populates="user_achievement")
