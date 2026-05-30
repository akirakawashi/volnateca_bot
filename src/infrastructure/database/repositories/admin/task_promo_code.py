from application.admin.dto.task_promo_code import (
    CreateTaskPromoCodeTaskCommand,
    CreatedTaskPromoCodeTaskDTO,
)
from application.admin.interface.repositories.task_promo_code import ITaskPromoCodeAdminRepository
from application.common.dto.task_promo_code import normalize_task_promo_code
from domain.enums.task import TaskPromoCodeStatus, TaskType
from infrastructure.database.models.task_promo_codes import TaskPromoCode
from infrastructure.database.models.tasks import Task
from infrastructure.database.repositories.base import SQLAlchemyRepository


class TaskPromoCodeAdminRepository(SQLAlchemyRepository, ITaskPromoCodeAdminRepository):
    async def create_task_with_codes(
        self,
        command: CreateTaskPromoCodeTaskCommand,
    ) -> CreatedTaskPromoCodeTaskDTO:
        task = Task(
            code=command.code,
            task_name=command.task_name,
            description=command.description,
            task_type=TaskType.CUSTOM,
            points=command.points,
            week_number=command.week_number,
            external_id=None,
            starts_at=command.starts_at,
            ends_at=command.ends_at,
            repeat_policy=command.repeat_policy,
            is_active=True,
        )
        self._session.add(task)
        await self._session.flush()
        if task.tasks_id is None:
            raise RuntimeError("Первичный ключ задания не был сгенерирован")

        codes = [
            TaskPromoCode(
                tasks_id=task.tasks_id,
                promo_code=normalize_task_promo_code(promo_code),
                promo_code_status=TaskPromoCodeStatus.AVAILABLE,
            )
            for promo_code in command.promo_codes
        ]
        self._session.add_all(codes)
        await self._session.flush()
        return CreatedTaskPromoCodeTaskDTO(
            tasks_id=task.tasks_id,
            code=task.code,
            task_name=task.task_name,
            promo_codes_total=len(codes),
        )
