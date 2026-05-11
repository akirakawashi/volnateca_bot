from enum import Enum


class TaskType(str, Enum):
    """Тип задания, определяющий способ автоматической проверки."""

    VK_SUBSCRIBE = "vk_subscribe"  # Подписка на группу ВКонтакте
    VK_LIKE = "vk_like"  # Лайк поста ВКонтакте
    VK_REPOST = "vk_repost"  # Репост поста ВКонтакте
    VK_COMMENT = "vk_comment"  # Комментарий под постом ВКонтакте
    VK_POLL = "vk_poll"  # Участие в опросе ВКонтакте
    VK_STORY_MENTION = "vk_story_mention"  # Упоминание в истории ВКонтакте
    QUIZ = "quiz"
    CUSTOM = "custom"  # Нестандартное задание


class TaskRepeatPolicy(str, Enum):
    """Правило повторного выполнения задания одним пользователем."""

    ONCE = "once"  # Один раз за всё время проекта
    DAILY = "daily"  # Один раз в день
    WEEKLY = "weekly"  # Один раз в неделю


class TaskCompletionStatus(str, Enum):
    """Статус проверки выполнения задания пользователем."""

    PENDING = "pending"  # Задание ожидает проверки
    COMPLETED = "completed"  # Задание выполнено и подтверждено
    REJECTED = "rejected"  # Задание проверено, но не выполнено
    CANCELED = "canceled"  # Выполнение отменено администратором или системой


__all__ = [
    "TaskCompletionStatus",
    "TaskRepeatPolicy",
    "TaskType",
]
