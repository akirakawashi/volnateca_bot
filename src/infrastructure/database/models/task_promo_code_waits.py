from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, Index, func
from sqlmodel import Column, Field, Relationship

from domain.enums.task import TaskPromoCodeWaitStatus
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.tasks import Task
    from infrastructure.database.models.users import User


class TaskPromoCodeWait(BaseModel, table=True):
    """Состояние диалога, в котором бот ждёт промокод для задания."""

    __tablename__ = "task_promo_code_waits"
    __table_args__ = (
        Index("ix_task_promo_code_waits_users_id_status", "users_id", "wait_status"),
    )

    task_promo_code_waits_id: int | None = Field(default=None, primary_key=True)
    users_id: int = Field(
        foreign_key="users.users_id",
        nullable=False,
        index=True,
        description="ID пользователя, от которого бот ждёт код",
    )
    tasks_id: int = Field(
        foreign_key="tasks.tasks_id",
        nullable=False,
        index=True,
        description="ID задания, для которого ожидается код",
    )
    wait_status: TaskPromoCodeWaitStatus = Field(
        default=TaskPromoCodeWaitStatus.WAITING,
        sa_column=Column(
            SAEnum(
                TaskPromoCodeWaitStatus,
                name="task_promo_code_wait_status",
                values_callable=enum_values,
            ),
            index=True,
            nullable=False,
        ),
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

    user: "User" = Relationship(back_populates="task_promo_code_waits")
    task: "Task" = Relationship(back_populates="task_promo_code_waits")
