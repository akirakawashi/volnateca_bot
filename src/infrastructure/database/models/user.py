from datetime import datetime

from sqlalchemy import DateTime, func
from sqlmodel import Column, Field

from infrastructure.database.base import BaseModel


class User(BaseModel, table=True):
    __tablename__ = "user"

    user_id: int | None = Field(default=None, primary_key=True)
    vk_user_id: int = Field(nullable=False, unique=True, index=True, description="ID пользователя ВКонтакте")
    first_name: str | None = Field(default=None, description="Имя пользователя")
    last_name: str | None = Field(default=None, description="Фамилия пользователя")
    mid_name: str | None = Field(default=None, description="Отчество пользователя")
    balance_points: int = Field(default=0, nullable=False, description="Текущий баланс очков пользователя")
    earned_points_total: int = Field(default=0, nullable=False, description="Общее количество заработанных очков пользователя")
    spent_points_total: int = Field(default=0, nullable=False, description="Общее количество потраченных очков пользователя")
    is_active: bool = Field(default=True, nullable=False, description="Статус активности пользователя")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
    )
