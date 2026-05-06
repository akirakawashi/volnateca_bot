from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, Text, func
from sqlmodel import Column, Field, Relationship

from domain.enums.task import TaskRepeatPolicy, TaskType
from infrastructure.database.base import BaseModel, enum_values

if TYPE_CHECKING:
    from infrastructure.database.models.task_completion import TaskCompletion
    from infrastructure.database.models.transaction import Transaction


class Task(BaseModel, table=True):
    """
    Справочник заданий проекта.

    Описывает действие, которое бот показывает пользователю и умеет проверять:
    подписку, лайк, репост, комментарий, опрос, упоминание в истории или викторину.
    """

    __tablename__ = "task"

    task_id: int | None = Field(default=None, primary_key=True)
    code: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Стабильный уникальный код задания для seed-данных, логики приложения и админки",
    )
    task_name: str = Field(
        nullable=False, description="Название задания для пользователя"
    )
    description: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="Подробное описание условий выполнения задания для пользователя",
    )
    task_type: TaskType = Field(
        sa_column=Column(
            SAEnum(TaskType, name="task_type", values_callable=enum_values),
            nullable=False,
        ),
        description="Тип задания, по которому приложение выбирает способ автоматической проверки",
    )
    points: int = Field(
        nullable=False, description="Количество очков, начисляемое после подтверждения выполнения задания"
    )
    week_number: int | None = Field(
        default=None,
        index=True,
        description="Номер недели проекта от 1 до 12; NULL означает, что задание не привязано к конкретной неделе",
    )
    external_id: str | None = Field(
        default=None,
        index=True,
        description=(
            "Идентификатор внешнего объекта для проверки задания. "
            "Для VK-заданий это может быть ID поста, опроса или другой сущности VK, "
            "по которой бот проверяет лайк, репост, комментарий или голос."
        ),
    )
    starts_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Дата и время, начиная с которых задание доступно; NULL означает отсутствие отдельного ограничения",
    )
    ends_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Дата и время, после которых задание недоступно; NULL означает отсутствие отдельного ограничения",
    )
    repeat_policy: TaskRepeatPolicy = Field(
        default=TaskRepeatPolicy.ONCE,
        sa_column=Column(
            SAEnum(TaskRepeatPolicy, name="task_repeat_policy", values_callable=enum_values),
            nullable=False,
        ),
        description="Правило повторного выполнения задания одним пользователем",
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        description="Участвует ли задание в выдаче пользователям и автоматических проверках",
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

    task_completions: list["TaskCompletion"] = Relationship(back_populates="task")
    transactions: list["Transaction"] = Relationship(back_populates="task")
