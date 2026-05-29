from application.command.award_monthly_top import AwardMonthlyTopHandler
from application.command.capture_vk_referral_intent import CaptureVKReferralIntentHandler
from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_poll_task import CompleteVKPollTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.command.ensure_vk_poll_task import EnsureVKPollTaskHandler
from application.command.get_store_catalog import GetStoreCatalogHandler, GetStorePrizeCardHandler
from application.command.get_vk_user_tasks import GetVKUserTasksHandler
from application.command.register_vk_user import RegisterVKUserHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.command.register_vk_user_with_referral_context import (
    RegisterVKUserWithReferralContextHandler,
)
from application.command.task_promo_code import (
    ActivateTaskPromoCodeHandler,
    CancelTaskPromoCodeHandler,
    GetTaskPromoCodeWaitHandler,
    StartTaskPromoCodeHandler,
)

__all__ = [
    "ActivateTaskPromoCodeHandler",
    "AwardMonthlyTopHandler",
    "CancelTaskPromoCodeHandler",
    "CaptureVKReferralIntentHandler",
    "CompleteVKLikeTaskHandler",
    "CompleteVKPollTaskHandler",
    "CompleteVKRepostTaskHandler",
    "CompleteVKSubscriptionTaskHandler",
    "EnsureVKPollTaskHandler",
    "GetStoreCatalogHandler",
    "GetStorePrizeCardHandler",
    "GetTaskPromoCodeWaitHandler",
    "GetVKUserTasksHandler",
    "RegisterVKUserAndCheckSubscriptionHandler",
    "RegisterVKUserHandler",
    "RegisterVKUserWithReferralContextHandler",
    "StartTaskPromoCodeHandler",
]
