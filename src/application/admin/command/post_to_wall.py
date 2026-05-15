from application.base_interactor import Interactor
from application.admin.dto.wall_post import PostToWallCommand, PostedToWallDTO
from application.common.dto.vk import VKWallPostDTO
from application.interface.clients import IVKWallClient
from application.interface.repositories.tasks import ITaskRepository
from application.interface.uow import IUnitOfWork
from domain.enums.task import TaskRepeatPolicy
from settings.vk import VKSettings

_MAX_DESCRIPTION_LEN = 500


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

        description = (f"Создано из поста {external_id}.\n\n{command_data.message}")[:_MAX_DESCRIPTION_LEN]

        like_result = await self.task_repository.create_like_task_if_not_exists(
            code=f"vk_like_wall_{group_id}_{post_id}",
            task_name=self._like_task_name(command_data),
            description=description,
            external_id=external_id,
            points=command_data.like_points,
            week_number=command_data.week_number,
            repeat_policy=TaskRepeatPolicy.ONCE,
            event_id=None,
        )

        repost_result = await self.task_repository.create_repost_task_if_not_exists(
            code=f"vk_repost_wall_{group_id}_{post_id}",
            task_name=self._repost_task_name(command_data),
            description=description,
            external_id=external_id,
            points=command_data.repost_points,
            week_number=command_data.week_number,
            repeat_policy=TaskRepeatPolicy.ONCE,
            event_id=None,
        )

        comment_tasks_id: int | None = None
        if command_data.comment_points > 0:
            comment_result = await self.task_repository.create_comment_task_if_not_exists(
                code=f"vk_comment_wall_{group_id}_{post_id}",
                task_name=self._comment_task_name(command_data),
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
            repost_tasks_id=repost_result.tasks_id,
            comment_tasks_id=comment_tasks_id,
        )

    @staticmethod
    def _like_task_name(cmd: PostToWallCommand) -> str:
        if cmd.week_number is not None:
            return f"Поставить лайк посту недели {cmd.week_number}"
        return "Поставить лайк посту"

    @staticmethod
    def _repost_task_name(cmd: PostToWallCommand) -> str:
        if cmd.repost_points >= 60:
            return "Сделать репост партнёрского поста"
        if cmd.week_number is not None:
            return f"Сделать репост поста недели {cmd.week_number}"
        return "Сделать репост поста"

    @staticmethod
    def _comment_task_name(cmd: PostToWallCommand) -> str:
        if cmd.week_number is not None:
            return f"Оставить комментарий к посту недели {cmd.week_number}"
        return "Оставить комментарий к посту"
