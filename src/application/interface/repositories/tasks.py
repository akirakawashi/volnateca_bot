from abc import ABC, abstractmethod

from application.common.dto.task import (
    VKLikeTaskCompletionDTO,
    VKLikeTaskCreationDTO,
    VKLikeTaskDTO,
    VKRepostTaskCompletionDTO,
    VKRepostTaskCreationDTO,
    VKRepostTaskDTO,
    VKSubscriptionTaskCompletionDTO,
    VKSubscriptionTaskDTO,
)
from domain.enums.task import TaskRepeatPolicy


class ITaskCompletionRepository(ABC):
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
    async def complete_repost_task_for_vk_user(
        self,
        vk_user_id: int,
        task: VKRepostTaskDTO,
        completion_key: str,
        event_id: str | None,
        evidence_external_id: str | None,
    ) -> VKRepostTaskCompletionDTO:
        raise NotImplementedError

    @abstractmethod
    async def reject_repost_task_for_vk_user(
        self,
        vk_user_id: int,
        task: VKRepostTaskDTO,
        completion_key: str,
        event_id: str | None,
        evidence_external_id: str | None,
        rejected_reason: str,
    ) -> VKRepostTaskCompletionDTO:
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
    async def complete_subscription_task_for_vk_user(
        self,
        vk_user_id: int,
        task: VKSubscriptionTaskDTO,
        completion_key: str,
        event_id: str | None,
        evidence_external_id: str | None,
    ) -> VKSubscriptionTaskCompletionDTO:
        raise NotImplementedError

    @abstractmethod
    async def reject_subscription_task_for_vk_user(
        self,
        vk_user_id: int,
        task: VKSubscriptionTaskDTO,
        completion_key: str,
        event_id: str | None,
        evidence_external_id: str | None,
        rejected_reason: str,
    ) -> VKSubscriptionTaskCompletionDTO:
        raise NotImplementedError

    @abstractmethod
    async def is_subscription_task_completed(
        self,
        vk_user_id: int,
        task: VKSubscriptionTaskDTO,
        completion_key: str,
    ) -> bool:
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
    async def complete_like_task_for_vk_user(
        self,
        vk_user_id: int,
        task: VKLikeTaskDTO,
        completion_key: str,
        event_id: str | None,
    ) -> VKLikeTaskCompletionDTO:
        raise NotImplementedError
