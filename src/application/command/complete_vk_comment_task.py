from dataclasses import dataclass
from datetime import UTC, datetime

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
class CompleteVKCommentTaskCommand:
    event_id: str | None
    vk_user_id: int
    commented_post_external_ids: tuple[str, ...]


class CompleteVKCommentTaskHandler(
    Interactor[CompleteVKCommentTaskCommand, TaskCompletionResult],
):
    """Засчитывает комментарий под VK-постом, если по нему есть активное задание.

    Событие wall_reply_new считается достаточным доказательством действия,
    поэтому обработчик только находит задание по external_id поста и передаёт
    начисление в AwardTaskService.
    """

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
        command_data: CompleteVKCommentTaskCommand,
    ) -> TaskCompletionResult:
        task = await self.task_repository.get_active_comment_task_by_external_ids(
            external_ids=command_data.commented_post_external_ids,
        )
        if task is None:
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
                week_number=task.week_number,
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
        return build_task_completion_result(outcome=outcome)
