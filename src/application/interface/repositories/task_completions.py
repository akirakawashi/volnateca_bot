from abc import ABC, abstractmethod
from datetime import datetime

from application.common.dto.task_completion import TaskCompletionRecord
from domain.enums.task import TaskCompletionStatus


class ITaskCompletionRepository(ABC):
    """Репозиторий фактов выполнения заданий.

    Отвечает только за CRUD таблицы task_completions. Любые проверки,
    блокировки баланса и начисления выполняются вне репозитория.
    """

    @abstractmethod
    async def get_for_update(
        self,
        *,
        users_id: int,
        tasks_id: int,
        completion_key: str,
    ) -> TaskCompletionRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def create(
        self,
        *,
        users_id: int,
        tasks_id: int,
        completion_key: str,
        task_completion_status: TaskCompletionStatus,
        points_awarded: int,
        transactions_id: int | None,
        external_event_id: str | None,
        evidence_external_id: str | None,
        rejected_reason: str | None,
        checked_at: datetime,
    ) -> TaskCompletionRecord:
        raise NotImplementedError

    @abstractmethod
    async def update_status(
        self,
        *,
        task_completions_id: int,
        task_completion_status: TaskCompletionStatus,
        points_awarded: int,
        transactions_id: int | None,
        external_event_id: str | None,
        evidence_external_id: str | None,
        rejected_reason: str | None,
        checked_at: datetime,
    ) -> TaskCompletionRecord:
        raise NotImplementedError

    @abstractmethod
    async def is_completed_by_vk_user(
        self,
        *,
        vk_user_id: int,
        tasks_id: int,
        completion_key: str,
    ) -> bool:
        raise NotImplementedError
