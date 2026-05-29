from fastapi import APIRouter, Depends

from presentation.http.routers.admin.auth import auth_admin_router, verify_admin_credentials, verify_admin_token
from presentation.http.routers.admin.broadcast import broadcast_admin_router
from presentation.http.routers.admin.db import db_admin_router
from presentation.http.routers.admin.dev import dev_admin_router
from presentation.http.routers.admin.message_templates import message_templates_admin_router
from presentation.http.routers.admin.monthly_top import monthly_top_admin_router
from presentation.http.routers.admin.prizes import prizes_admin_router
from presentation.http.routers.admin.quiz import quiz_admin_router
from presentation.http.routers.admin.task_promo_code import task_promo_code_admin_router
from presentation.http.routers.admin.wall_post import wall_admin_router

admin_router = APIRouter(
    prefix="/v1/admin",
    tags=["Admin"],
    dependencies=[Depends(verify_admin_credentials), Depends(verify_admin_token)],
)
admin_router.include_router(auth_admin_router)
admin_router.include_router(broadcast_admin_router)
admin_router.include_router(quiz_admin_router)
admin_router.include_router(prizes_admin_router)
admin_router.include_router(task_promo_code_admin_router)
admin_router.include_router(wall_admin_router)
admin_router.include_router(message_templates_admin_router)
admin_router.include_router(monthly_top_admin_router)
admin_router.include_router(db_admin_router)
# TODO: удалить dev_admin_router перед релизом — только для локальной отладки.
admin_router.include_router(dev_admin_router)

__all__ = ["admin_router"]
