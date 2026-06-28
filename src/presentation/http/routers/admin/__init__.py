from fastapi import APIRouter, Depends

from presentation.http.routers.admin.auth import auth_admin_router, verify_admin_session
from presentation.http.routers.admin.broadcast import broadcast_admin_router
from presentation.http.routers.admin.message_templates import message_templates_admin_router
from presentation.http.routers.admin.monthly_top import monthly_top_admin_router
from presentation.http.routers.admin.prize_redemptions import prize_redemptions_admin_router
from presentation.http.routers.admin.prizes import prizes_admin_router
from presentation.http.routers.admin.stats import stats_admin_router
from presentation.http.routers.admin.quiz import quiz_admin_router
from presentation.http.routers.admin.task_promo_code import task_promo_code_admin_router
from presentation.http.routers.admin.users import users_admin_router
from presentation.http.routers.admin.wall_post import wall_admin_router

admin_router = APIRouter(
    prefix="/v1/admin",
    tags=["Admin"],
)

protected_admin_router = APIRouter(
    dependencies=[Depends(verify_admin_session)],
)

admin_router.include_router(auth_admin_router)
protected_admin_router.include_router(broadcast_admin_router)
protected_admin_router.include_router(quiz_admin_router)
protected_admin_router.include_router(prizes_admin_router)
protected_admin_router.include_router(prize_redemptions_admin_router)
protected_admin_router.include_router(stats_admin_router)
protected_admin_router.include_router(users_admin_router)
protected_admin_router.include_router(task_promo_code_admin_router)
protected_admin_router.include_router(wall_admin_router)
protected_admin_router.include_router(message_templates_admin_router)
protected_admin_router.include_router(monthly_top_admin_router)
admin_router.include_router(protected_admin_router)

__all__ = ["admin_router"]
