from datetime import datetime

from sqlalchemy import func, select
from sqlmodel import col

from application.common.dto.task_promo_code import (
    TaskPromoCodeRecord,
    TaskPromoCodeStatsDTO,
    normalize_task_promo_code,
)
from application.interface.repositories.task_promo_codes import ITaskPromoCodeRepository
from domain.enums.task import TaskPromoCodeStatus
from infrastructure.database.models.task_promo_codes import TaskPromoCode
from infrastructure.database.repositories.base import SQLAlchemyRepository


class TaskPromoCodeRepository(SQLAlchemyRepository, ITaskPromoCodeRepository):
    async def activate_available_code(
        self,
        *,
        tasks_id: int,
        promo_code: str,
        users_id: int,
        activated_at: datetime,
    ) -> TaskPromoCodeRecord | None:
        normalized_code = normalize_task_promo_code(promo_code)
        if not normalized_code:
            return None

        result = await self._session.execute(
            select(TaskPromoCode)
            .where(
                col(TaskPromoCode.tasks_id) == tasks_id,
                col(TaskPromoCode.promo_code) == normalized_code,
                col(TaskPromoCode.promo_code_status) == TaskPromoCodeStatus.AVAILABLE,
            )
            .with_for_update(),
        )
        code = result.scalar_one_or_none()
        if code is None:
            return None

        code.promo_code_status = TaskPromoCodeStatus.USED
        code.users_id = users_id
        code.activated_at = activated_at
        await self._session.flush()
        return self._to_record(code=code)

    async def bulk_create_available_codes(
        self,
        *,
        tasks_id: int,
        promo_codes: tuple[str, ...],
    ) -> tuple[TaskPromoCodeRecord, ...]:
        codes = [
            TaskPromoCode(
                tasks_id=tasks_id,
                promo_code=normalize_task_promo_code(promo_code),
                promo_code_status=TaskPromoCodeStatus.AVAILABLE,
            )
            for promo_code in promo_codes
            if normalize_task_promo_code(promo_code)
        ]
        self._session.add_all(codes)
        await self._session.flush()
        return tuple(self._to_record(code=code) for code in codes)

    async def get_stats(
        self,
        *,
        tasks_id: int,
    ) -> TaskPromoCodeStatsDTO:
        result = await self._session.execute(
            select(
                func.count(col(TaskPromoCode.task_promo_codes_id)),
                func.count(col(TaskPromoCode.task_promo_codes_id)).filter(
                    col(TaskPromoCode.promo_code_status) == TaskPromoCodeStatus.AVAILABLE,
                ),
                func.count(col(TaskPromoCode.task_promo_codes_id)).filter(
                    col(TaskPromoCode.promo_code_status) == TaskPromoCodeStatus.USED,
                ),
            ).where(col(TaskPromoCode.tasks_id) == tasks_id),
        )
        total_count, available_count, used_count = result.one()
        return TaskPromoCodeStatsDTO(
            tasks_id=tasks_id,
            total_count=int(total_count),
            available_count=int(available_count),
            used_count=int(used_count),
        )

    @staticmethod
    def _to_record(*, code: TaskPromoCode) -> TaskPromoCodeRecord:
        if code.task_promo_codes_id is None:
            raise RuntimeError("Первичный ключ промокода задания не был сгенерирован")

        return TaskPromoCodeRecord(
            task_promo_codes_id=code.task_promo_codes_id,
            tasks_id=code.tasks_id,
            promo_code=code.promo_code,
            promo_code_status=code.promo_code_status,
            users_id=code.users_id,
            activated_at=code.activated_at,
        )
