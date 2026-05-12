from fastapi import APIRouter

from presentation.http.routers.admin.db import db_admin_router
from presentation.http.routers.admin.quiz import quiz_admin_router

admin_router = APIRouter(prefix="/v1/admin", tags=["Admin"])
admin_router.include_router(quiz_admin_router)
admin_router.include_router(db_admin_router)

__all__ = ["admin_router"]
