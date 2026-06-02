from abc import ABC, abstractmethod
from datetime import datetime

from application.common.dto.task_promo_code import TaskPromoCodeRecord, TaskPromoCodeStatsDTO


class ITaskPromoCodeRepository(ABC):
    """Репозиторий кодов, которыми пользователь подтверждает выполнение задания."""

    @abstractmethod
    async def get_available_code_for_update(
        self,
        *,
        tasks_id: int,
        promo_code: str,
    ) -> TaskPromoCodeRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def mark_code_used(
        self,
        *,
        task_promo_codes_id: int,
        users_id: int,
        activated_at: datetime,
    ) -> TaskPromoCodeRecord:
        raise NotImplementedError

    @abstractmethod
    async def get_stats(
        self,
        *,
        tasks_id: int,
    ) -> TaskPromoCodeStatsDTO:
        raise NotImplementedError
