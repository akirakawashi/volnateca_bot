from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SAEnum, Index, UniqueConstraint, func
from sqlmodel import Column, Field, Relationship

from domain.enums.task import TaskPromoCodeStatus
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.tasks import Task
    from infrastructure.database.models.users import User


class TaskPromoCode(BaseModel, table=True):
    """Промокод, который подтверждает выполнение задания в боте."""

    __tablename__ = "task_promo_codes"
    __table_args__ = (
        UniqueConstraint("tasks_id", "promo_code", name="uq_task_promo_codes_tasks_code"),
        Index("ix_task_promo_codes_tasks_id_status", "tasks_id", "promo_code_status"),
    )

    task_promo_codes_id: int | None = Field(default=None, primary_key=True)
    tasks_id: int = Field(
        foreign_key="tasks.tasks_id",
        nullable=False,
        index=True,
        description="ID задания, к которому относится промокод",
    )
    users_id: int | None = Field(
        default=None,
        foreign_key="users.users_id",
        index=True,
        description="ID пользователя, активировавшего код",
    )
    promo_code: str = Field(
        nullable=False,
        index=True,
        description="Нормализованное значение промокода, которое пользователь вводит в боте",
    )
    promo_code_status: TaskPromoCodeStatus = Field(
        default=TaskPromoCodeStatus.AVAILABLE,
        sa_column=Column(
            SAEnum(
                TaskPromoCodeStatus,
                name="task_promo_code_status",
                values_callable=enum_values,
            ),
            index=True,
            nullable=False,
        ),
    )
    activated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Дата и время успешной активации кода в боте",
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

    task: "Task" = Relationship(back_populates="task_promo_codes")
    user: Optional["User"] = Relationship(back_populates="task_promo_codes")
