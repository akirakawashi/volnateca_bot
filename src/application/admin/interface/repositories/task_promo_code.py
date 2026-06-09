from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from application.admin.dto.task_promo_code import CreatedTaskPromoCodeTaskDTO, TaskPromoCodeTaskAdminDTO

if TYPE_CHECKING:
    from application.admin.command.task_promo_code import (
        CreateTaskPromoCodeTaskCommand,
        UpdateTaskPromoCodeTaskCommand,
    )


class ITaskPromoCodeAdminRepository(ABC):
    @abstractmethod
    async def list_tasks(self) -> tuple[TaskPromoCodeTaskAdminDTO, ...]:
        raise NotImplementedError

    @abstractmethod
    async def create_task_with_code(
        self,
        command: CreateTaskPromoCodeTaskCommand,
    ) -> CreatedTaskPromoCodeTaskDTO:
        raise NotImplementedError

    @abstractmethod
    async def update_task(
        self,
        command: UpdateTaskPromoCodeTaskCommand,
    ) -> TaskPromoCodeTaskAdminDTO | None:
        raise NotImplementedError
