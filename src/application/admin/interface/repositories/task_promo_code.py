from abc import ABC, abstractmethod

from application.admin.dto.task_promo_code import (
    CreateTaskPromoCodeTaskCommand,
    CreatedTaskPromoCodeTaskDTO,
)
from application.common.dto.task_promo_code import TaskPromoCodeStatsDTO


class ITaskPromoCodeAdminRepository(ABC):
    @abstractmethod
    async def create_task_with_codes(
        self,
        command: CreateTaskPromoCodeTaskCommand,
    ) -> CreatedTaskPromoCodeTaskDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_stats(
        self,
        *,
        tasks_id: int,
    ) -> TaskPromoCodeStatsDTO:
        raise NotImplementedError
