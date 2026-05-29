from abc import ABC, abstractmethod

from application.common.dto.task_promo_code import TaskPromoCodeWaitRecord


class ITaskPromoCodeWaitRepository(ABC):
    """Репозиторий состояния ожидания промокода от пользователя."""

    @abstractmethod
    async def get_waiting(
        self,
        *,
        users_id: int,
    ) -> TaskPromoCodeWaitRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def get_waiting_for_update(
        self,
        *,
        users_id: int,
    ) -> TaskPromoCodeWaitRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def start_waiting(
        self,
        *,
        users_id: int,
        tasks_id: int,
    ) -> TaskPromoCodeWaitRecord:
        raise NotImplementedError

    @abstractmethod
    async def complete_waiting(
        self,
        *,
        task_promo_code_waits_id: int,
    ) -> TaskPromoCodeWaitRecord:
        raise NotImplementedError

    @abstractmethod
    async def cancel_waiting(
        self,
        *,
        task_promo_code_waits_id: int,
    ) -> TaskPromoCodeWaitRecord:
        raise NotImplementedError
