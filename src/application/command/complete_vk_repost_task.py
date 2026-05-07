from dataclasses import dataclass
from datetime import UTC, datetime

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.task import (
    VKRepostTaskCompletionDTO,
    VKRepostTaskCompletionStatus,
    VKRepostTaskDTO,
)
from application.interface.clients import IVKUserClient
from application.interface.repositories.tasks import ITaskCompletionRepository
from application.interface.uow import IUnitOfWork
from domain.enums.task import TaskRepeatPolicy


REPOST_SUBSCRIPTION_REJECTED_REASON = "vk_user_is_not_group_member"


@dataclass(slots=True, frozen=True, kw_only=True)
class CompleteVKRepostTaskCommand:
    event_id: str | None
    vk_user_id: int
    repost_external_id: str | None
    target_post_external_ids: tuple[str, ...]


class CompleteVKRepostTaskHandler(
    Interactor[CompleteVKRepostTaskCommand, VKRepostTaskCompletionDTO],
):
    def __init__(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
        vk_user_client: IVKUserClient,
        required_subscription_group_id: int,
    ) -> None:
        self.repository = repository
        self.uow = uow
        self.vk_user_client = vk_user_client
        self.required_subscription_group_id = required_subscription_group_id

    async def __call__(
        self,
        command_data: CompleteVKRepostTaskCommand,
    ) -> VKRepostTaskCompletionDTO:
        task = await self.repository.get_active_repost_task_by_external_ids(
            external_ids=command_data.target_post_external_ids,
        )
        if task is None:
            logger.info(
                "TEMP VK repost task not found: event_id={}, vk_user_id={}, target_post_external_ids={}",
                command_data.event_id,
                command_data.vk_user_id,
                command_data.target_post_external_ids,
            )
            return VKRepostTaskCompletionDTO(
                status=VKRepostTaskCompletionStatus.TASK_NOT_FOUND,
                vk_user_id=command_data.vk_user_id,
            )

        is_member = await self.vk_user_client.is_group_member(
            vk_user_id=command_data.vk_user_id,
            group_id=self.required_subscription_group_id,
        )
        if is_member is None:
            logger.warning(
                "TEMP VK repost task subscription check unavailable: "
                "event_id={}, vk_user_id={}, group_id={}, tasks_id={}",
                command_data.event_id,
                command_data.vk_user_id,
                self.required_subscription_group_id,
                task.tasks_id,
            )
            return VKRepostTaskCompletionDTO(
                status=VKRepostTaskCompletionStatus.VK_API_UNAVAILABLE,
                vk_user_id=command_data.vk_user_id,
                tasks_id=task.tasks_id,
            )

        completion_key = self._get_completion_key(task=task, checked_at=datetime.now(tz=UTC))
        if not is_member:
            result = await self.repository.reject_repost_task_for_vk_user(
                vk_user_id=command_data.vk_user_id,
                task=task,
                completion_key=completion_key,
                event_id=command_data.event_id,
                evidence_external_id=command_data.repost_external_id,
                rejected_reason=REPOST_SUBSCRIPTION_REJECTED_REASON,
            )
            await self.uow.commit()
            return result

        result = await self.repository.complete_repost_task_for_vk_user(
            vk_user_id=command_data.vk_user_id,
            task=task,
            completion_key=completion_key,
            event_id=command_data.event_id,
            evidence_external_id=command_data.repost_external_id,
        )
        await self.uow.commit()
        return result

    @staticmethod
    def _get_completion_key(
        task: VKRepostTaskDTO,
        checked_at: datetime,
    ) -> str:
        if task.repeat_policy == TaskRepeatPolicy.ONCE:
            return "once"
        if task.repeat_policy == TaskRepeatPolicy.DAILY:
            return checked_at.date().isoformat()
        if task.week_number is not None:
            return f"week_{task.week_number:02d}"

        iso_calendar = checked_at.isocalendar()
        return f"{iso_calendar.year}-W{iso_calendar.week:02d}"
