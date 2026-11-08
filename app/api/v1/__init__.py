from fastapi import APIRouter

from app.core.dependency import DependPermission

from .apis import apis_router
from .auditlog import auditlog_router
from .base import base_router
from .courses import courses_router
from .dashboard import dashboard_router
from .depts import depts_router
from .emoji import emoji_router
from .menus import menus_router
from .roles import roles_router
from .sessions import sessions_router
from .statistics import statistics_router
from .users import users_router

v1_router = APIRouter()

v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(users_router, prefix="/user", dependencies=[DependPermission])
v1_router.include_router(roles_router, prefix="/role", dependencies=[DependPermission])
v1_router.include_router(menus_router, prefix="/menu", dependencies=[DependPermission])
v1_router.include_router(apis_router, prefix="/api", dependencies=[DependPermission])
v1_router.include_router(depts_router, prefix="/dept", dependencies=[DependPermission])
v1_router.include_router(auditlog_router, prefix="/auditlog", dependencies=[DependPermission])
v1_router.include_router(courses_router)
v1_router.include_router(sessions_router)
v1_router.include_router(emoji_router)
v1_router.include_router(dashboard_router)
v1_router.include_router(statistics_router)
