from pydantic_settings import SettingsConfigDict

from domain.enums.task import TaskType
from settings.base import Settings


class TaskTypeImagesSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="VK_")

    TASK_IMAGE_VK_SUBSCRIBE: str | None = "photo-238388485_456239105"
    TASK_IMAGE_VK_LIKE: str | None = "photo-238388485_456239108"
    TASK_IMAGE_VK_COMMENT: str | None = "photo-238388485_456239107"
    TASK_IMAGE_VK_POLL: str | None = "photo-238388485_456239106"
    TASK_IMAGE_CUSTOM: str | None = "photo-238388485_456239086" # нужны картинка для кастомных задач (общая если нет других)

    def get_image(self, task_type: TaskType) -> str | None:
        return {
            TaskType.VK_SUBSCRIBE: self.TASK_IMAGE_VK_SUBSCRIBE,
            TaskType.VK_LIKE: self.TASK_IMAGE_VK_LIKE,
            TaskType.VK_COMMENT: self.TASK_IMAGE_VK_COMMENT,
            TaskType.VK_POLL: self.TASK_IMAGE_VK_POLL,
            TaskType.CUSTOM: self.TASK_IMAGE_CUSTOM,
        }.get(task_type)

# TODO еще проверка на ссылки