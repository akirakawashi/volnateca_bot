from application.command.award_monthly_top import AwardMonthlyTopHandler
from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.record_vk_user_activity import RecordVKUserActivityHandler
from application.command.register_vk_user import RegisterVKUserHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionHandler,
)

__all__ = [
    "AwardMonthlyTopHandler",
    "CompleteVKLikeTaskHandler",
    "CompleteVKRepostTaskHandler",
    "CompleteVKSubscriptionTaskHandler",
    "GetVKUserTasksHandler",
    "RecordVKUserActivityHandler",
    "RegisterVKUserAndCheckSubscriptionHandler",
    "RegisterVKUserHandler",
]
