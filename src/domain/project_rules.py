from enum import StrEnum


# ===== Shared codes =====

class AchievementCode(StrEnum):
    REFERRAL_MILESTONE_3 = "referral_milestone_3"
    REFERRAL_MILESTONE_5 = "referral_milestone_5"
    REFERRAL_MILESTONE_10 = "referral_milestone_10"
    WEEK_COMPLETION = "week_completion"
    PROJECT_COMPLETION = "project_completion_12_weeks"
    MONTHLY_TOP = "monthly_top_10"


class AchievementKey(StrEnum):
    ONCE = "once"


class TaskRejectedReason(StrEnum):
    VK_USER_IS_NOT_GROUP_MEMBER = "vk_user_is_not_group_member"


# ===== Registration =====

REGISTRATION_BONUS_POINTS = 15


# ===== VK subscription =====

VK_SUBSCRIPTION_TASK_POINTS = 15
VK_SUBSCRIPTION_COMPLETION_KEY = AchievementKey.ONCE.value
VK_SUBSCRIPTION_REJECTED_REASON = TaskRejectedReason.VK_USER_IS_NOT_GROUP_MEMBER.value


# ===== Referrals =====

REFERRAL_BONUS_POINTS = 30
REFERRAL_MILESTONES: dict[int, str] = {
    3: AchievementCode.REFERRAL_MILESTONE_3.value,
    5: AchievementCode.REFERRAL_MILESTONE_5.value,
    10: AchievementCode.REFERRAL_MILESTONE_10.value,
}
REFERRAL_MILESTONE_ACHIEVEMENT_KEY = AchievementKey.ONCE.value


# ===== VK poll tasks =====

POLL_TASK_POINTS = 20
POLL_TASK_NAME = "Проголосовать в опросе Волны"
POLL_TASK_HASHTAG_PATTERN = r"(?<!\w)#volnateca\b"


# ===== Completion achievements =====

WEEK_COMPLETION_ACHIEVEMENT_CODE = AchievementCode.WEEK_COMPLETION.value
PROJECT_COMPLETION_ACHIEVEMENT_CODE = AchievementCode.PROJECT_COMPLETION.value
PROJECT_COMPLETION_REQUIRED_WEEK_COUNT = 12


# ===== Monthly top =====

MONTHLY_TOP_ACHIEVEMENT_CODE = AchievementCode.MONTHLY_TOP.value
MONTHLY_TOP_DEFAULT_LIMIT = 10


# ===== Helpers =====

def build_week_completion_key(*, week_number: int) -> str:
    return f"week_{week_number:02d}"


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
    "TaskRejectedReason",
    "VK_SUBSCRIPTION_COMPLETION_KEY",
    "VK_SUBSCRIPTION_REJECTED_REASON",
    "VK_SUBSCRIPTION_TASK_POINTS",
    "WEEK_COMPLETION_ACHIEVEMENT_CODE",
    "build_week_completion_key",
]
