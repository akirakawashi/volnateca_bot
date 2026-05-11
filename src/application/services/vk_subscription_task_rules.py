from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class VKSubscriptionTaskRules:
    """Параметры одноразового задания за подписку на VK-сообщество."""

    points: int = 15
    week_number: int = 1
    completion_key: str = "once"
    rejected_reason: str = "vk_user_is_not_group_member"
