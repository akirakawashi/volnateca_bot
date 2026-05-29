from sqlalchemy import select
from sqlmodel import col

from application.common.dto.task_promo_code import TaskPromoCodeWaitRecord
from application.interface.repositories.task_promo_code_waits import ITaskPromoCodeWaitRepository
from domain.enums.task import TaskPromoCodeWaitStatus
from infrastructure.database.models.task_promo_code_waits import TaskPromoCodeWait
from infrastructure.database.repositories.base import SQLAlchemyRepository


class TaskPromoCodeWaitRepository(SQLAlchemyRepository, ITaskPromoCodeWaitRepository):
    async def get_waiting(
        self,
        *,
        users_id: int,
    ) -> TaskPromoCodeWaitRecord | None:
        wait = await self._get_latest_waiting(users_id=users_id, lock=False)
        if wait is None:
            return None
        return self._to_record(wait=wait)

    async def get_waiting_for_update(
        self,
        *,
        users_id: int,
    ) -> TaskPromoCodeWaitRecord | None:
        wait = await self._get_latest_waiting(users_id=users_id, lock=True)
        if wait is None:
            return None
        return self._to_record(wait=wait)

    async def start_waiting(
        self,
        *,
        users_id: int,
        tasks_id: int,
    ) -> TaskPromoCodeWaitRecord:
        existing = await self._list_waiting_for_update(users_id=users_id)
        for wait in existing:
            wait.wait_status = TaskPromoCodeWaitStatus.CANCELED

        wait = TaskPromoCodeWait(
            users_id=users_id,
            tasks_id=tasks_id,
            wait_status=TaskPromoCodeWaitStatus.WAITING,
        )
        self._session.add(wait)
        await self._session.flush()
        return self._to_record(wait=wait)

    async def complete_waiting(
        self,
        *,
        task_promo_code_waits_id: int,
    ) -> TaskPromoCodeWaitRecord:
        return await self._update_status(
            task_promo_code_waits_id=task_promo_code_waits_id,
            wait_status=TaskPromoCodeWaitStatus.COMPLETED,
        )

    async def cancel_waiting(
        self,
        *,
        task_promo_code_waits_id: int,
    ) -> TaskPromoCodeWaitRecord:
        return await self._update_status(
            task_promo_code_waits_id=task_promo_code_waits_id,
            wait_status=TaskPromoCodeWaitStatus.CANCELED,
        )

    async def _get_latest_waiting(
        self,
        *,
        users_id: int,
        lock: bool,
    ) -> TaskPromoCodeWait | None:
        statement = (
            select(TaskPromoCodeWait)
            .where(
                col(TaskPromoCodeWait.users_id) == users_id,
                col(TaskPromoCodeWait.wait_status) == TaskPromoCodeWaitStatus.WAITING,
            )
            .order_by(col(TaskPromoCodeWait.task_promo_code_waits_id).desc())
        )
        if lock:
            statement = statement.with_for_update()
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def _list_waiting_for_update(
        self,
        *,
        users_id: int,
    ) -> tuple[TaskPromoCodeWait, ...]:
        result = await self._session.execute(
            select(TaskPromoCodeWait)
            .where(
                col(TaskPromoCodeWait.users_id) == users_id,
                col(TaskPromoCodeWait.wait_status) == TaskPromoCodeWaitStatus.WAITING,
            )
            .with_for_update(),
        )
        return tuple(result.scalars().all())

    async def _update_status(
        self,
        *,
        task_promo_code_waits_id: int,
        wait_status: TaskPromoCodeWaitStatus,
    ) -> TaskPromoCodeWaitRecord:
        wait = await self._session.get(TaskPromoCodeWait, task_promo_code_waits_id)
        if wait is None:
            raise RuntimeError(
                f"Ожидание промокода task_promo_code_waits_id={task_promo_code_waits_id} не найдено",
            )

        wait.wait_status = wait_status
        await self._session.flush()
        return self._to_record(wait=wait)

    @staticmethod
    def _to_record(*, wait: TaskPromoCodeWait) -> TaskPromoCodeWaitRecord:
        if wait.task_promo_code_waits_id is None:
            raise RuntimeError("Первичный ключ ожидания промокода не был сгенерирован")

        return TaskPromoCodeWaitRecord(
            task_promo_code_waits_id=wait.task_promo_code_waits_id,
            users_id=wait.users_id,
            tasks_id=wait.tasks_id,
            wait_status=wait.wait_status,
        )
