from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, UniqueConstraint, func
from sqlmodel import Column, Field, Relationship

from infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.database.models.tasks import Task


class TaskPromoCode(BaseModel, table=True):
    """Промокод, который подтверждает выполнение задания в боте."""

    __tablename__ = "task_promo_codes"
    __table_args__ = (
        UniqueConstraint("tasks_id", name="uq_task_promo_codes_tasks_id"),
        UniqueConstraint("promo_code", name="uq_task_promo_codes_promo_code"),
    )

    task_promo_codes_id: int | None = Field(default=None, primary_key=True)
    tasks_id: int = Field(
        foreign_key="tasks.tasks_id",
        nullable=False,
        index=True,
        description="ID задания, к которому относится промокод",
    )
    promo_code: str = Field(
        nullable=False,
        index=True,
        description="Нормализованное значение промокода, которое пользователь вводит в боте",
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
