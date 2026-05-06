from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, Text, func
from sqlmodel import Column, Field, Relationship

from domain.enums.achievement import AchievementRepeatPolicy, AchievementType
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.user_achievements import UserAchievement


class Achievement(BaseModel, table=True):
    """
    Справочник достижений и бонусных правил проекта.

    Описывает игровые бонусы из ТЗ: реферальные пороги, стрики,
    выполнение всех заданий недели, серии викторин и финальные награды.
    """

    __tablename__ = "achievements"
    __table_args__ = (
        CheckConstraint("points > 0", name="points_positive"),
    )

    achievements_id: int | None = Field(default=None, primary_key=True)
    code: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Стабильный уникальный код достижения для seed-данных и логики приложения",
    )
    achievement_name: str = Field(
        nullable=False, description="Название достижения для пользователя"
    )
    description: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="Подробное описание условия получения достижения",
    )
    achievement_type: AchievementType = Field(
        sa_column=Column(
            SAEnum(
                AchievementType,
                name="achievement_type",
                values_callable=enum_values,
            ),
            nullable=False,
        ),
        description="Тип достижения, по которому приложение выбирает правило проверки",
    )
    repeat_policy: AchievementRepeatPolicy = Field(
        default=AchievementRepeatPolicy.ONCE,
        sa_column=Column(
            SAEnum(
                AchievementRepeatPolicy,
                name="achievement_repeat_policy",
                values_callable=enum_values,
            ),
            nullable=False,
        ),
        description="Правило повторной выдачи достижения одному пользователю",
    )
    points: int = Field(
        nullable=False,
        description="Количество очков, начисляемое за получение достижения",
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        index=True,
        description="Участвует ли достижение в автоматической проверке и выдаче",
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

    user_achievements: list["UserAchievement"] = Relationship(
        back_populates="achievement"
    )
