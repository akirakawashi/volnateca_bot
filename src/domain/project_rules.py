from enum import StrEnum


# ===== Shared codes =====

class AchievementCode(StrEnum):
    """Коды достижений, которые должны совпадать с записями в справочнике БД."""

    REFERRAL_MILESTONE_3 = "referral_milestone_3"
    REFERRAL_MILESTONE_5 = "referral_milestone_5"
    REFERRAL_MILESTONE_10 = "referral_milestone_10"
    WEEK_COMPLETION = "week_completion"
    PROJECT_COMPLETION = "project_completion_12_weeks"
    MONTHLY_TOP = "monthly_top_10"


class AchievementKey(StrEnum):
    """Ключи одноразовых достижений и completion-записей."""

    ONCE = "once"


class TaskRejectedReason(StrEnum):
    """Причины отклонения автоматической проверки задания."""

    VK_USER_IS_NOT_GROUP_MEMBER = "vk_user_is_not_group_member"


# ===== Registration =====

# Сколько баллов получает пользователь после регистрации.
REGISTRATION_BONUS_POINTS = 15


# ===== VK subscription =====

# Сколько баллов начисляется за подписку на VK-группу.
VK_SUBSCRIPTION_TASK_POINTS = 15

# Ключ выполнения подписки: задание можно засчитать один раз за проект.
VK_SUBSCRIPTION_COMPLETION_KEY = AchievementKey.ONCE.value

# Причина отклонения, если пользователь не состоит в VK-группе.
VK_SUBSCRIPTION_REJECTED_REASON = TaskRejectedReason.VK_USER_IS_NOT_GROUP_MEMBER.value


# ===== Referrals =====

# Сколько баллов получает пригласивший за одного подтвержденного друга.
REFERRAL_BONUS_POINTS = 30

# Пороги рефералов и коды достижений, которые выдаются на этих порогах.
REFERRAL_MILESTONES: dict[int, str] = {
    3: AchievementCode.REFERRAL_MILESTONE_3.value,
    5: AchievementCode.REFERRAL_MILESTONE_5.value,
    10: AchievementCode.REFERRAL_MILESTONE_10.value,
}

# Ключ достижения за реферальный порог: каждый порог выдается один раз.
REFERRAL_MILESTONE_ACHIEVEMENT_KEY = AchievementKey.ONCE.value


# ===== VK poll tasks =====

# Сколько баллов начисляется за участие в VK-опросе.
POLL_TASK_POINTS = 20

# Название задания, которое создается для VK-опроса.
POLL_TASK_NAME = "Проголосовать в опросе Волны"

# Хештег, по которому бот понимает, что по посту с опросом нужно создать задание.
POLL_TASK_HASHTAG_PATTERN = r"(?<!\w)#volnateca\b"


# ===== VK task descriptions =====

# Максимальная длина описания задания, которое сохраняется в БД.
TASK_DESCRIPTION_MAX_LENGTH = 500


# ===== Bot pagination =====

# Сколько заданий показывается на одной странице карусели заданий.
TASKS_PAGE_SIZE = 6

# Сколько призов показывается на одной странице карусели магазина.
STORE_PAGE_SIZE = 3

# Сколько заявок на приз показывается на одной странице раздела «Мои призы».
USER_REDEMPTIONS_PAGE_SIZE = 10


# ===== Completion achievements =====

# Код достижения за закрытие всех заданий одной недели.
WEEK_COMPLETION_ACHIEVEMENT_CODE = AchievementCode.WEEK_COMPLETION.value

# Код достижения за закрытие всех недель проекта.
PROJECT_COMPLETION_ACHIEVEMENT_CODE = AchievementCode.PROJECT_COMPLETION.value

# Сколько недель нужно закрыть для достижения завершения проекта.
PROJECT_COMPLETION_REQUIRED_WEEK_COUNT = 12


# ===== Monthly top =====

# Код достижения для пользователей из топа месяца.
MONTHLY_TOP_ACHIEVEMENT_CODE = AchievementCode.MONTHLY_TOP.value

# Сколько пользователей награждается в monthly top по умолчанию.
MONTHLY_TOP_DEFAULT_LIMIT = 10


# ===== Helpers =====

def build_week_completion_key(*, week_number: int) -> str:
    """Строит ключ completion-записи для конкретной недели."""

    return f"week_{week_number:02d}"


# Все недельные ключи, которые нужны для проверки завершения проекта.
PROJECT_COMPLETION_REQUIRED_WEEK_KEYS = tuple(
    build_week_completion_key(week_number=week_number)
    for week_number in range(1, PROJECT_COMPLETION_REQUIRED_WEEK_COUNT + 1)
)


__all__ = [
    "AchievementCode",
    "AchievementKey",
    "MONTHLY_TOP_ACHIEVEMENT_CODE",
    "MONTHLY_TOP_DEFAULT_LIMIT",
    "POLL_TASK_HASHTAG_PATTERN",
    "POLL_TASK_NAME",
    "POLL_TASK_POINTS",
    "PROJECT_COMPLETION_ACHIEVEMENT_CODE",
    "PROJECT_COMPLETION_REQUIRED_WEEK_COUNT",
    "PROJECT_COMPLETION_REQUIRED_WEEK_KEYS",
    "REFERRAL_BONUS_POINTS",
    "REFERRAL_MILESTONE_ACHIEVEMENT_KEY",
    "REFERRAL_MILESTONES",
    "REGISTRATION_BONUS_POINTS",
    "STORE_PAGE_SIZE",
    "TASK_DESCRIPTION_MAX_LENGTH",
    "TASKS_PAGE_SIZE",
    "TaskRejectedReason",
    "USER_REDEMPTIONS_PAGE_SIZE",
    "VK_SUBSCRIPTION_COMPLETION_KEY",
    "VK_SUBSCRIPTION_REJECTED_REASON",
    "VK_SUBSCRIPTION_TASK_POINTS",
    "WEEK_COMPLETION_ACHIEVEMENT_CODE",
    "build_week_completion_key",
]
