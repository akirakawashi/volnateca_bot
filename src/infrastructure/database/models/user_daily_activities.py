from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, UniqueConstraint, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.database.models.users import User


class UserDailyActivity(BaseModel, table=True):
    """
    Факт активности пользователя в конкретный календарный день проекта.

    Таблица нужна для расчёта ежедневных стриков: 7, 30, 60 дней подряд
    и для защиты от повторной фиксации одного дня.
    """

    __tablename__ = "user_daily_activities"
    __table_args__ = (
        UniqueConstraint(
            "users_id",
            "activity_date",
            name="uq_user_daily_activities_users_date",
        ),
        CheckConstraint("streak_days > 0", name="streak_days_positive"),
    )

    user_daily_activities_id: int | None = Field(default=None, primary_key=True)
    users_id: int = Field(
        foreign_key="users.users_id",
        nullable=False,
        index=True,
        description="ID пользователя, активность которого зафиксирована",
    )
    activity_date: date = Field(
        nullable=False,
        index=True,
        description="Календарная дата активности в timezone проекта",
    )
    streak_days: int = Field(
        default=1,
        nullable=False,
        description="Длина непрерывного ежедневного стрика на эту дату",
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

    user: "User" = Relationship(back_populates="daily_activities")
