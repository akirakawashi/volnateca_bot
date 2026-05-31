import re
from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.vk import VKPollDTO
from application.interface.repositories.tasks import ITaskRepository
from application.interface.uow import IUnitOfWork
from domain.enums.task import TaskRepeatPolicy
from domain.project_rules import (
    POLL_TASK_HASHTAG_PATTERN,
    POLL_TASK_NAME,
    POLL_TASK_POINTS,
)

_MAX_DESCRIPTION_LEN = 500
_VOLNATECA_HASHTAG_PATTERN = re.compile(POLL_TASK_HASHTAG_PATTERN, re.IGNORECASE)


@dataclass(slots=True, frozen=True, kw_only=True)
class EnsureVKPollTaskCommand:
    post_text: str
    poll: VKPollDTO
    poll_question: str | None = None


class EnsureVKPollTaskHandler(Interactor[EnsureVKPollTaskCommand, None]):
    """Создаёт бессрочное задание по VK-опросу с хештегом #volnateca."""

    def __init__(
        self,
        task_repository: ITaskRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.task_repository = task_repository
        self.uow = uow

    async def __call__(self, command_data: EnsureVKPollTaskCommand) -> None:
        if not _VOLNATECA_HASHTAG_PATTERN.search(command_data.post_text):
            return

        description = self._build_description(
            post_text=command_data.post_text,
            poll_question=command_data.poll_question,
        )
        await self.task_repository.get_or_create_poll_task(
            code=f"vk_poll_{command_data.poll.owner_id}_{command_data.poll.poll_id}",
            task_name=POLL_TASK_NAME,
            description=description,
            external_id=command_data.poll.external_id,
            points=POLL_TASK_POINTS,
            repeat_policy=TaskRepeatPolicy.ONCE,
        )
        await self.uow.commit()

    @staticmethod
    def _build_description(*, post_text: str, poll_question: str | None) -> str:
        parts = ["Автоматически создано по VK-опросу с хештегом #volnateca."]
        if poll_question:
            parts.append(f"Вопрос опроса: {poll_question}")
        if post_text:
            parts.append(f"Текст поста: {post_text}")
        return "\n\n".join(parts)[:_MAX_DESCRIPTION_LEN]
