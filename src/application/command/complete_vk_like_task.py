from dataclasses import dataclass
from datetime import UTC, datetime

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.task import (
    VKLikeTaskCompletionDTO,
    VKLikeTaskCompletionStatus,
    VKLikeTaskDTO,
)
from application.interface.repositories.tasks import ITaskCompletionRepository
from application.interface.uow import IUnitOfWork
from domain.enums.task import TaskRepeatPolicy


@dataclass(slots=True, frozen=True, kw_only=True)
class CompleteVKLikeTaskCommand:
    event_id: str | None
    vk_user_id: int
    liked_post_external_ids: tuple[str, ...]


class CompleteVKLikeTaskHandler(
    Interactor[CompleteVKLikeTaskCommand, VKLikeTaskCompletionDTO],
):
    def __init__(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.repository = repository
        self.uow = uow

    async def __call__(
        self,
        command_data: CompleteVKLikeTaskCommand,
    ) -> VKLikeTaskCompletionDTO:
        task = await self.repository.get_active_like_task_by_external_ids(
            external_ids=command_data.liked_post_external_ids,
        )
        if task is None:
            logger.info(
                "TEMP VK like task not found: event_id={}, vk_user_id={}, liked_post_external_ids={}",
                command_data.event_id,
                command_data.vk_user_id,
                command_data.liked_post_external_ids,
            )
            return VKLikeTaskCompletionDTO(
                status=VKLikeTaskCompletionStatus.TASK_NOT_FOUND,
                vk_user_id=command_data.vk_user_id,
            )

        completion_key = self._get_completion_key(task=task, checked_at=datetime.now(tz=UTC))
        result = await self.repository.complete_like_task_for_vk_user(
            vk_user_id=command_data.vk_user_id,
            task=task,
            completion_key=completion_key,
            event_id=command_data.event_id,
        )
        await self.uow.commit()
        logger.info(
            "TEMP VK like task completion handled: "
            "event_id={}, vk_user_id={}, status={}, users_id={}, tasks_id={}, "
            "task_completions_id={}, transactions_id={}, points_awarded={}, balance_points={}",
            command_data.event_id,
            command_data.vk_user_id,
            result.status,
            result.users_id,
            result.tasks_id,
            result.task_completions_id,
            result.transactions_id,
            result.points_awarded,
            result.balance_points,
        )
        return result

    @staticmethod
    def _get_completion_key(
        task: VKLikeTaskDTO,
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
