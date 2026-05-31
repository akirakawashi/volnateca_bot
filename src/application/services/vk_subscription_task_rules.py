from dataclasses import dataclass

from domain.project_rules import (
    VK_SUBSCRIPTION_COMPLETION_KEY,
    VK_SUBSCRIPTION_REJECTED_REASON,
    VK_SUBSCRIPTION_TASK_POINTS,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class VKSubscriptionTaskRules:
    """Параметры одноразового задания за подписку на VK-сообщество."""

    points: int = VK_SUBSCRIPTION_TASK_POINTS
    completion_key: str = VK_SUBSCRIPTION_COMPLETION_KEY
    rejected_reason: str = VK_SUBSCRIPTION_REJECTED_REASON
