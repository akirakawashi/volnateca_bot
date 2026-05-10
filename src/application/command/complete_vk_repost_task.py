from dataclasses import dataclass
from datetime import UTC, datetime

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.task import (
    VKRepostTaskCompletionDTO,
    VKRepostTaskCompletionStatus,
)
from application.interface.repositories.tasks import ITaskRepository
from application.interface.uow import IUnitOfWork
from application.services.award_task_service import (
    AwardTaskOutcome,
    AwardTaskOutcomeStatus,
    AwardTaskService,
    TaskAwardSpec,
)
from application.services.task_completion_key import build_task_completion_key


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
        task_repository: ITaskRepository,
        award_service: AwardTaskService,
        uow: IUnitOfWork,
    ) -> None:
        self.task_repository = task_repository
        self.award_service = award_service
        self.uow = uow

    async def __call__(
        self,
        command_data: CompleteVKRepostTaskCommand,
    ) -> VKRepostTaskCompletionDTO:
        task = await self.task_repository.get_active_repost_task_by_external_ids(
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

        # wall_repost arrives from VK at repost time, so no extra repost verification is needed.
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
            evidence_external_id=command_data.repost_external_id,
        )
        await self.uow.commit()
        return self._to_completion_dto(outcome=outcome)

    @staticmethod
    def _to_completion_dto(outcome: AwardTaskOutcome) -> VKRepostTaskCompletionDTO:
        return VKRepostTaskCompletionDTO(
            status=_map_status(outcome=outcome.status),
            vk_user_id=outcome.vk_user_id,
            users_id=outcome.users_id,
            tasks_id=outcome.tasks_id,
            task_completions_id=outcome.task_completions_id,
            transactions_id=outcome.transactions_id,
            points_awarded=outcome.points_awarded,
            balance_points=outcome.balance_points,
        )

def _map_status(outcome: AwardTaskOutcomeStatus) -> VKRepostTaskCompletionStatus:
    match outcome:
        case AwardTaskOutcomeStatus.COMPLETED:
            return VKRepostTaskCompletionStatus.COMPLETED
        case AwardTaskOutcomeStatus.ALREADY_COMPLETED:
            return VKRepostTaskCompletionStatus.ALREADY_COMPLETED
        case AwardTaskOutcomeStatus.USER_NOT_REGISTERED:
            return VKRepostTaskCompletionStatus.USER_NOT_REGISTERED
        case AwardTaskOutcomeStatus.REJECTED:
            raise RuntimeError("VK repost task does not support REJECTED outcome")
