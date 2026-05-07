from fastapi import APIRouter

from presentation.http.routers.v1.routers import vk_callback_router

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(vk_callback_router)

__all__ = ["api_v1_router"]
