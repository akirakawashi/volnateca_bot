from presentation.http.routers.v1.routers.vk_callbacks.handlers.confirmation import (
    handle_confirmation_callback,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.ignored import handle_ignored_callback
from presentation.http.routers.v1.routers.vk_callbacks.handlers.like import handle_like_callback
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration import (
    handle_registration_callback,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.comment import handle_comment_callback
from presentation.http.routers.v1.routers.vk_callbacks.handlers.repost import handle_repost_callback
from presentation.http.routers.v1.routers.vk_callbacks.handlers.subscription import (
    handle_subscription_callback,
)

__all__ = [
    "handle_comment_callback",
    "handle_confirmation_callback",
    "handle_ignored_callback",
    "handle_like_callback",
    "handle_registration_callback",
    "handle_repost_callback",
    "handle_subscription_callback",
]
