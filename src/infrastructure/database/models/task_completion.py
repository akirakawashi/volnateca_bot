from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SAEnum, Text, UniqueConstraint, func
from sqlmodel import Column, Field, Relationship

from domain.enums.task import TaskCompletionStatus
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.task import Task
    from infrastructure.database.models.transaction import Transaction
    from infrastructure.database.models.user import User


class TaskCompletion(BaseModel, table=True):
    """
    Факт выполнения задания пользователем.

    Таблица отделяет проверку выполнения задания от движения баллов:
    задание может быть проверено, отклонено или подтверждено, а начисление
    фиксируется отдельной записью в журнале транзакций.
    """

    __tablename__ = "task_completions"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", "completion_key", name="uq_task_completions_user_task_key"),
    )

    task_completions_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="user.user_id",
        nullable=False,
        index=True,
        description="ID пользователя, для которого зафиксировано выполнение задания",
    )
    task_id: int = Field(
        foreign_key="task.task_id",
        nullable=False,
        index=True,
        description="ID задания, выполнение которого проверяется",
    )
    completion_key: str = Field(
        nullable=False,
        index=True,
        description=(
            "Ключ периода выполнения задания для ограничения повторов. "
            "Для once используется 'once', для daily дата вида 'YYYY-MM-DD', "
            "для weekly ключ недели вида 'week_01'."
        ),
    )
    transaction_id: int | None = Field(
        default=None,
        foreign_key="transaction.transaction_id",
        unique=True,
        description="ID транзакции начисления очков, созданной после подтверждения выполнения задания",
    )
    task_completion_status: TaskCompletionStatus = Field(
        default=TaskCompletionStatus.PENDING,
        sa_column=Column(
            SAEnum(
                TaskCompletionStatus,
                name="task_completion_status",
                values_callable=enum_values,
            ),
            nullable=False,
        ),
        description="Текущий статус проверки выполнения задания пользователем",
    )
    points_awarded: int = Field(
        default=0,
        nullable=False,
        description="Фактически начисленное количество очков; 0 до начисления или при отклонении",
    )
    external_event_id: str | None = Field(
        default=None,
        index=True,
        description=(
            "ID внешнего события или callback, по которому была зафиксирована попытка выполнения. "
            "Используется для идемпотентности и расследования повторных событий VK."
        ),
    )
    rejected_reason: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="Причина отклонения, если задание проверено и не засчитано",
    )
    checked_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Дата и время последней проверки выполнения задания",
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

    user: "User" = Relationship(back_populates="task_completions")
    task: "Task" = Relationship(back_populates="task_completions")
    transaction: Optional["Transaction"] = Relationship(
        back_populates="task_completion"
    )
