from presentation.http.routers.v1.routers.vk_callbacks.handlers.confirmation import (
    handle_confirmation_callback,
)
from presentation.http.routers.v1.routers.vk_callbacks.handlers.ignored import handle_ignored_callback
from presentation.http.routers.v1.routers.vk_callbacks.handlers.like import handle_like_callback
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration import (
    handle_registration_callback,
)

__all__ = [
    "handle_confirmation_callback",
    "handle_ignored_callback",
    "handle_like_callback",
    "handle_registration_callback",
]
