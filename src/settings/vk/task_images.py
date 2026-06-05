from pydantic_settings import SettingsConfigDict

from domain.enums.task import TaskType
from settings.base import Settings


class TaskTypeImagesSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="VK_")

    TASK_IMAGE_VK_SUBSCRIBE: str | None = "photo-213947338_457239022"
    TASK_IMAGE_VK_LIKE: str | None = "photo147820319_457263584"
    TASK_IMAGE_VK_REPOST: str | None = "photo147820319_457263585"
    TASK_IMAGE_VK_COMMENT: str | None = "photo147820319_457263583"
    TASK_IMAGE_VK_POLL: str | None = "photo-213947338_457239027"
    TASK_IMAGE_CUSTOM: str | None = "photo-213947338_457239022"

    def get_image(self, task_type: TaskType) -> str | None:
        return {
            TaskType.VK_SUBSCRIBE: self.TASK_IMAGE_VK_SUBSCRIBE,
            TaskType.VK_LIKE: self.TASK_IMAGE_VK_LIKE,
            TaskType.VK_REPOST: self.TASK_IMAGE_VK_REPOST,
            TaskType.VK_COMMENT: self.TASK_IMAGE_VK_COMMENT,
            TaskType.VK_POLL: self.TASK_IMAGE_VK_POLL,
            TaskType.CUSTOM: self.TASK_IMAGE_CUSTOM,
        }.get(task_type)
