from abc import ABC, abstractmethod

from application.common.dto.task_promo_code import TaskPromoCodeRecord


class ITaskPromoCodeRepository(ABC):
    """Репозиторий кодов, которыми пользователь подтверждает выполнение задания."""

    @abstractmethod
    async def get_by_task_for_update(
        self,
        *,
        tasks_id: int,
    ) -> TaskPromoCodeRecord | None:
        raise NotImplementedError
