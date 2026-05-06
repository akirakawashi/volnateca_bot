from presentation.http.routers.healthcheck import healthcheck_router
from presentation.http.routers.vk_callbacks import vk_callback_router

__all__ = [
    "healthcheck_router",
    "vk_callback_router",
]
