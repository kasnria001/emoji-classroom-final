"""多维统计 API。"""

from fastapi import APIRouter

from .statistics import router

statistics_router = APIRouter()
statistics_router.include_router(router, prefix="/statistics", tags=["统计模块"])

__all__ = ["statistics_router"]

