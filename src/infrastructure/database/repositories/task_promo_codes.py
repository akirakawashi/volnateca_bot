from sqlalchemy import select
from sqlmodel import col

from application.common.dto.task_promo_code import (
    TaskPromoCodeRecord,
    normalize_task_promo_code,
)
from application.interface.repositories.task_promo_codes import ITaskPromoCodeRepository
from infrastructure.database.models.task_promo_codes import TaskPromoCode
from infrastructure.database.repositories.base import SQLAlchemyRepository


class TaskPromoCodeRepository(SQLAlchemyRepository, ITaskPromoCodeRepository):
    async def get_by_task_for_update(
        self,
        *,
        tasks_id: int,
    ) -> TaskPromoCodeRecord | None:
        code = await self._get_by_task(tasks_id=tasks_id, lock=True)
        if code is None:
            return None
        return self._to_record(code=code)

    async def get_by_task(
        self,
        *,
        tasks_id: int,
    ) -> TaskPromoCodeRecord | None:
        code = await self._get_by_task(tasks_id=tasks_id, lock=False)
        if code is None:
            return None
        return self._to_record(code=code)

    async def create_for_task(
        self,
        *,
        tasks_id: int,
        promo_code: str,
    ) -> TaskPromoCodeRecord:
        normalized_code = normalize_task_promo_code(promo_code)
        if not normalized_code:
            raise ValueError("Промокод задания не может быть пустым")

        code = TaskPromoCode(
            tasks_id=tasks_id,
            promo_code=normalized_code,
        )
        self._session.add(code)
        await self._session.flush()
        return self._to_record(code=code)

    async def _get_by_task(
        self,
        *,
        tasks_id: int,
        lock: bool,
    ) -> TaskPromoCode | None:
        statement = select(TaskPromoCode).where(col(TaskPromoCode.tasks_id) == tasks_id)
        if lock:
            statement = statement.with_for_update()
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    def _to_record(*, code: TaskPromoCode) -> TaskPromoCodeRecord:
        if code.task_promo_codes_id is None:
            raise RuntimeError("Первичный ключ промокода задания не был сгенерирован")

        return TaskPromoCodeRecord(
            task_promo_codes_id=code.task_promo_codes_id,
            tasks_id=code.tasks_id,
            promo_code=code.promo_code,
        )
