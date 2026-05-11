from dataclasses import dataclass
from datetime import UTC, datetime

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.task import (
    TaskCompletionResult,
    TaskCompletionResultStatus,
)
from application.interface.repositories.tasks import ITaskRepository
from application.interface.uow import IUnitOfWork
from application.services.award_task_service import (
    AwardTaskService,
    TaskAwardSpec,
)
from application.services.task_completion_key import build_task_completion_key
from application.services.task_completion_result import build_task_completion_result


@dataclass(slots=True, frozen=True, kw_only=True)
class CompleteVKLikeTaskCommand:
    event_id: str | None
    vk_user_id: int
    liked_post_external_ids: tuple[str, ...]


class CompleteVKLikeTaskHandler(
    Interactor[CompleteVKLikeTaskCommand, TaskCompletionResult],
):
    def __init__(
        self,
        task_repository: ITaskRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
    ) -> None:
        self.task_repository = task_repository
        self.award_service = award_service
        self.uow = uow

    async def __call__(
        self,
        command_data: CompleteVKLikeTaskCommand,
    ) -> TaskCompletionResult:
        task = await self.task_repository.get_active_like_task_by_external_ids(
            external_ids=command_data.liked_post_external_ids,
        )
        if task is None:
            logger.info(
                "ВРЕМЕННО Задание на лайк VK не найдено: event_id={}, vk_user_id={}, liked_post_external_ids={}",
                command_data.event_id,
                command_data.vk_user_id,
                command_data.liked_post_external_ids,
            )
            return TaskCompletionResult(
                status=TaskCompletionResultStatus.TASK_NOT_FOUND,
                vk_user_id=command_data.vk_user_id,
            )

        outcome = await self.award_service.award(
            vk_user_id=command_data.vk_user_id,
            task=TaskAwardSpec(
                tasks_id=task.tasks_id,
                task_name=task.task_name,
                points=task.points,
            ),
            completion_key=build_task_completion_key(
                repeat_policy=task.repeat_policy,
                week_number=task.week_number,
                checked_at=datetime.now(tz=UTC),
            ),
            event_id=command_data.event_id,
            evidence_external_id=None,
        )
        await self.uow.commit()

        result = build_task_completion_result(outcome=outcome)
        logger.info(
            "ВРЕМЕННО Выполнение задания на лайк VK обработано: "
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
