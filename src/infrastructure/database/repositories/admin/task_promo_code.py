from datetime import UTC, datetime

from sqlalchemy import select
from sqlmodel import col

from application.admin.command.task_promo_code import (
    CreateTaskPromoCodeTaskCommand,
    UpdateTaskPromoCodeTaskCommand,
)
from application.admin.dto.task_promo_code import CreatedTaskPromoCodeTaskDTO, TaskPromoCodeTaskAdminDTO
from application.admin.interface.repositories.task_promo_code import ITaskPromoCodeAdminRepository
from application.common.dto.task_promo_code import normalize_task_promo_code
from domain.enums.task import TaskRepeatPolicy, TaskType
from infrastructure.database.models.task_promo_codes import TaskPromoCode
from infrastructure.database.models.tasks import Task
from infrastructure.database.repositories.base import SQLAlchemyRepository


class TaskPromoCodeAdminRepository(SQLAlchemyRepository, ITaskPromoCodeAdminRepository):
    async def list_tasks(self) -> tuple[TaskPromoCodeTaskAdminDTO, ...]:
        now = datetime.now(tz=UTC)
        result = await self._session.execute(
            select(Task, TaskPromoCode)
            .join(TaskPromoCode, col(TaskPromoCode.tasks_id) == col(Task.tasks_id))
            .where(col(Task.task_type) == TaskType.CUSTOM)
            .order_by(
                col(Task.starts_at).is_(None),
                col(Task.starts_at),
                col(Task.tasks_id),
            ),
        )
        return tuple(
            self._to_task_admin_dto(task=task, promo_code=promo_code, now=now)
            for task, promo_code in result.all()
        )

    async def create_task_with_code(
        self,
        command: CreateTaskPromoCodeTaskCommand,
    ) -> CreatedTaskPromoCodeTaskDTO:
        task = Task(
            code=command.code,
            task_name=command.task_name,
            description=command.description,
            image_attachment=command.image_attachment,
            task_type=TaskType.CUSTOM,
            points=command.points,
            week_number=command.week_number,
            external_id=None,
            starts_at=command.starts_at,
            ends_at=command.ends_at,
            repeat_policy=TaskRepeatPolicy.ONCE,
            is_active=True,
        )
        self._session.add(task)
        await self._session.flush()
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")

        normalized_promo_code = normalize_task_promo_code(command.promo_code)
        if not normalized_promo_code:
            raise ValueError("Промокод задания не может быть пустым")
        code = TaskPromoCode(
            tasks_id=task.tasks_id,
            promo_code=normalized_promo_code,
        )
        self._session.add(code)
        await self._session.flush()
        return CreatedTaskPromoCodeTaskDTO(
            tasks_id=task.tasks_id,
            code=task.code,
            task_name=task.task_name,
            promo_code=normalized_promo_code,
        )

    async def update_task(
        self,
        command: UpdateTaskPromoCodeTaskCommand,
    ) -> TaskPromoCodeTaskAdminDTO | None:
        result = await self._session.execute(
            select(Task, TaskPromoCode)
            .join(TaskPromoCode, col(TaskPromoCode.tasks_id) == col(Task.tasks_id))
            .where(
                col(Task.tasks_id) == command.tasks_id,
                col(Task.task_type) == TaskType.CUSTOM,
            )
            .with_for_update(of=Task),
        )
        row = result.one_or_none()
        if row is None:
            return None

        task, promo_code = row
        now = datetime.now(tz=UTC)
        if not self._can_edit_task(task=task, now=now):
            raise ValueError("Можно редактировать только задания с будущей датой начала")

        if "description" in command.fields:
            task.description = command.description
        if "image_attachment" in command.fields:
            task.image_attachment = command.image_attachment

        await self._session.flush()
        return self._to_task_admin_dto(task=task, promo_code=promo_code, now=now)

    @classmethod
    def _to_task_admin_dto(
        cls,
        *,
        task: Task,
        promo_code: TaskPromoCode,
        now: datetime,
    ) -> TaskPromoCodeTaskAdminDTO:
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")

        return TaskPromoCodeTaskAdminDTO(
            tasks_id=task.tasks_id,
            code=task.code,
            task_name=task.task_name,
            description=task.description,
            points=task.points,
            week_number=task.week_number,
            starts_at=task.starts_at,
            ends_at=task.ends_at,
            promo_code=promo_code.promo_code,
            image_attachment=task.image_attachment,
            can_edit=cls._can_edit_task(task=task, now=now),
        )

    @staticmethod
    def _can_edit_task(*, task: Task, now: datetime) -> bool:
        starts_at = task.starts_at
        if starts_at is None:
            return False
        if starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=UTC)
        return starts_at > now
