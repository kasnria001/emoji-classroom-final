"""实时课堂情绪看板 API。"""

from fastapi import APIRouter

from .dashboard import router

dashboard_router = APIRouter()
dashboard_router.include_router(router, prefix="/dashboard", tags=["看板模块"])

__all__ = ["dashboard_router"]

