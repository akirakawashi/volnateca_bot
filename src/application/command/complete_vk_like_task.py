from dataclasses import dataclass
from datetime import UTC, datetime

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.task import (
    VKLikeTaskCompletionDTO,
    VKLikeTaskCompletionStatus,
    VKLikeTaskDTO,
)
from application.interface.repositories.tasks import ITaskRepository
from application.interface.uow import IUnitOfWork
from application.services.award_task_service import (
    AwardTaskOutcome,
    AwardTaskOutcomeStatus,
    AwardTaskService,
    TaskAwardSpec,
)
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
    ) -> VKLikeTaskCompletionDTO:
        task = await self.task_repository.get_active_like_task_by_external_ids(
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

        outcome = await self.award_service.award(
            vk_user_id=command_data.vk_user_id,
            task=TaskAwardSpec(
                tasks_id=task.tasks_id,
                task_name=task.task_name,
                points=task.points,
            ),
            completion_key=self._get_completion_key(task=task, checked_at=datetime.now(tz=UTC)),
            event_id=command_data.event_id,
            evidence_external_id=None,
        )
        await self.uow.commit()

        result = self._to_completion_dto(outcome=outcome)
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
    def _to_completion_dto(outcome: AwardTaskOutcome) -> VKLikeTaskCompletionDTO:
        return VKLikeTaskCompletionDTO(
            status=_map_status(outcome=outcome.status),
            vk_user_id=outcome.vk_user_id,
            users_id=outcome.users_id,
            tasks_id=outcome.tasks_id,
            task_completions_id=outcome.task_completions_id,
            transactions_id=outcome.transactions_id,
            points_awarded=outcome.points_awarded,
            balance_points=outcome.balance_points,
        )

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


def _map_status(outcome: AwardTaskOutcomeStatus) -> VKLikeTaskCompletionStatus:
    match outcome:
        case AwardTaskOutcomeStatus.COMPLETED:
            return VKLikeTaskCompletionStatus.COMPLETED
        case AwardTaskOutcomeStatus.ALREADY_COMPLETED:
            return VKLikeTaskCompletionStatus.ALREADY_COMPLETED
        case AwardTaskOutcomeStatus.USER_NOT_REGISTERED:
            return VKLikeTaskCompletionStatus.USER_NOT_REGISTERED
        case AwardTaskOutcomeStatus.REJECTED:
            raise RuntimeError("VK like task does not support REJECTED outcome")
