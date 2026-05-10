from abc import ABC, abstractmethod

from application.common.dto.task import (
    VKLikeTaskCreationDTO,
    VKLikeTaskDTO,
    VKRepostTaskCreationDTO,
    VKRepostTaskDTO,
    VKSubscriptionTaskDTO,
    VKUserAvailableTaskDTO,
)
from domain.enums.task import TaskRepeatPolicy


class ITaskRepository(ABC):
    """Репозиторий справочника заданий.

    Отвечает только за чтение и запись строк таблицы tasks. Любая бизнес-логика
    (начисление баллов, фиксация выполнения, обновление баланса) находится
    в AwardTaskService и других репозиториях.
    """

    @abstractmethod
    async def create_repost_task_if_not_exists(
        self,
        code: str,
        task_name: str,
        description: str,
        external_id: str,
        points: int,
        week_number: int | None,
        repeat_policy: TaskRepeatPolicy,
        event_id: str | None,
    ) -> VKRepostTaskCreationDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_active_repost_task_by_external_ids(
        self,
        external_ids: tuple[str, ...],
    ) -> VKRepostTaskDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def get_or_create_subscription_task(
        self,
        code: str,
        task_name: str,
        description: str,
        external_id: str,
        points: int,
        week_number: int | None,
        repeat_policy: TaskRepeatPolicy,
    ) -> VKSubscriptionTaskDTO:
        raise NotImplementedError

    @abstractmethod
    async def create_like_task_if_not_exists(
        self,
        code: str,
        task_name: str,
        description: str,
        external_id: str,
        points: int,
        week_number: int | None,
        repeat_policy: TaskRepeatPolicy,
        event_id: str | None,
    ) -> VKLikeTaskCreationDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_active_like_task_by_external_ids(
        self,
        external_ids: tuple[str, ...],
    ) -> VKLikeTaskDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def list_available_tasks_for_vk_user(
        self,
        vk_user_id: int,
    ) -> list[VKUserAvailableTaskDTO]:
        raise NotImplementedError
