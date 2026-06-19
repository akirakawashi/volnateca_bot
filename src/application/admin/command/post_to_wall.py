from dataclasses import dataclass

from application.admin.dto.wall_post import PostedToWallDTO
from application.base_interactor import Interactor
from application.common.dto.vk import VKWallPostDTO
from application.interface.clients import IVKWallClient
from application.interface.repositories.tasks import ITaskRepository
from application.interface.uow import IUnitOfWork
from domain.enums.task import TaskRepeatPolicy
from domain.project_rules import TASK_DESCRIPTION_MAX_LENGTH
from settings.vk import VKSettings


@dataclass(slots=True, frozen=True, kw_only=True)
class PostToWallCommand:
    message: str
    like_points: int
    comment_points: int  # 0 — задание на комментарий не создаётся
    week_number: int | None
    attachments: tuple[str, ...] | None = None


class PostToWallHandler(Interactor[PostToWallCommand, PostedToWallDTO]):
    """Публикует запись на стене сообщества VK и создаёт задания в БД."""

    def __init__(
        self,
        vk_wall_client: IVKWallClient,
        task_repository: ITaskRepository,
        uow: IUnitOfWork,
        vk_settings: VKSettings,
    ) -> None:
        self.vk_wall_client = vk_wall_client
        self.task_repository = task_repository
        self.uow = uow
        self.vk_settings = vk_settings

    async def __call__(self, command_data: PostToWallCommand) -> PostedToWallDTO:
        post_id = await self.vk_wall_client.post_to_wall(
            message=command_data.message,
            attachments=command_data.attachments,
        )
        if post_id is None:
            raise RuntimeError("VK API не вернул post_id — проверьте токен и права группы")

        group_id = abs(self.vk_settings.GROUP_ID)
        vk_post = VKWallPostDTO(owner_id=-group_id, post_id=post_id)
        external_id = vk_post.external_id

        description = (f"Создано из поста {external_id}.\n\n{command_data.message}")[
            :TASK_DESCRIPTION_MAX_LENGTH
        ]

        like_result = await self.task_repository.create_like_task_if_not_exists(
            code=f"vk_like_wall_{group_id}_{post_id}",
            task_name="Поставить лайк посту",
            description=description,
            external_id=external_id,
            points=command_data.like_points,
            week_number=command_data.week_number,
            repeat_policy=TaskRepeatPolicy.ONCE,
            event_id=None,
        )

        comment_tasks_id: int | None = None
        if command_data.comment_points > 0:
            comment_result = await self.task_repository.create_comment_task_if_not_exists(
                code=f"vk_comment_wall_{group_id}_{post_id}",
                task_name="Написать комментарий",
                description=description,
                external_id=external_id,
                points=command_data.comment_points,
                week_number=command_data.week_number,
                repeat_policy=TaskRepeatPolicy.ONCE,
                event_id=None,
            )
            comment_tasks_id = comment_result.tasks_id

        await self.uow.commit()

        return PostedToWallDTO(
            post_id=post_id,
            external_id=external_id,
            like_tasks_id=like_result.tasks_id,
            comment_tasks_id=comment_tasks_id,
        )


__all__ = [
    "PostToWallCommand",
    "PostToWallHandler",
]
