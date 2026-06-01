from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from application.admin.dto.task_promo_code import CreatedTaskPromoCodeTaskDTO

if TYPE_CHECKING:
    from application.admin.command.task_promo_code import CreateTaskPromoCodeTaskCommand


class ITaskPromoCodeAdminRepository(ABC):
    @abstractmethod
    async def create_task_with_codes(
        self,
        command: CreateTaskPromoCodeTaskCommand,
    ) -> CreatedTaskPromoCodeTaskDTO:
        raise NotImplementedError
