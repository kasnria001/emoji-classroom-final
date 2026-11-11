from aerich import Command
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from tortoise.expressions import Q

from app.api import api_router
from app.controllers.api import api_controller
from app.controllers.user import UserCreate, user_controller
from app.core.exceptions import (
    DoesNotExist,
    DoesNotExistHandle,
    HTTPException,
    HttpExcHandle,
    IntegrityError,
    IntegrityHandle,
    RequestValidationError,
    RequestValidationHandle,
    ResponseValidationError,
    ResponseValidationHandle,
)
from app.log import logger
from app.models.admin import Api, Menu, Role
from app.schemas.menus import MenuType
from app.settings.config import settings

from .middlewares import BackGroundTaskMiddleware, HttpAuditLogMiddleware
from .ai_boundary import AIBoundaryMiddleware


def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
        ),
        Middleware(BackGroundTaskMiddleware),
        Middleware(AIBoundaryMiddleware),
        Middleware(
            HttpAuditLogMiddleware,
            methods=["GET", "POST", "PUT", "DELETE"],
            exclude_paths=[
                "/api/v1/base/access_token",
                "/api/v1/base/register",
                "/api/v1/base/update_password",
                "/docs",
                "/openapi.json",
                "^/healthz$",
            ],
        ),
    ]
    return middleware


def register_exceptions(app: FastAPI):
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)


def register_routers(app: FastAPI, prefix: str = "/api"):
    app.include_router(api_router, prefix=prefix)


async def init_superuser():
    user = await user_controller.model.exists()
    if not user:
        await user_controller.create_user(
            UserCreate(
                username="admin",
                email="admin@admin.com",
                password=settings.BOOTSTRAP_ADMIN_PASSWORD,
                is_active=True,
                is_superuser=True,
            )
        )


async def init_menus():
    menus = await Menu.exists()
    if not menus:
        parent_menu = await Menu.create(
            menu_type=MenuType.CATALOG,
            name="系统管理",
            path="/system",
            order=1,
            parent_id=0,
            icon="carbon:gui-management",
            is_hidden=False,
            component="Layout",
            keepalive=False,
            redirect="/system/user",
        )
        children_menu = [
            Menu(
                menu_type=MenuType.MENU,
                name="用户管理",
                path="user",
                order=1,
                parent_id=parent_menu.id,
                icon="material-symbols:person-outline-rounded",
                is_hidden=False,
                component="/system/user",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="角色管理",
                path="role",
                order=2,
                parent_id=parent_menu.id,
                icon="carbon:user-role",
                is_hidden=False,
                component="/system/role",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="审计日志",
                path="auditlog",
                order=3,
                parent_id=parent_menu.id,
                icon="ph:clipboard-text-bold",
                is_hidden=False,
                component="/system/auditlog",
                keepalive=False,
            ),
        ]
        await Menu.bulk_create(children_menu)


async def init_classroom_menus():
    """补齐管理端课堂情绪菜单（幂等，兼容已初始化过的数据库）。"""

    parent = await Menu.get_or_none(path="/classroom", parent_id=0)
    if parent is None:
        parent = await Menu.create(
            menu_type=MenuType.CATALOG,
            name="课堂情绪管理",
            path="/classroom",
            order=3,
            parent_id=0,
            icon="carbon:activity",
            is_hidden=False,
            component="Layout",
            keepalive=False,
            redirect="/classroom/dashboard",
        )

    children = [
        ("实时看板", "dashboard", "material-symbols:dashboard-outline", 1),
        ("多维统计", "statistics", "carbon:chart-line", 2),
        ("课程管理", "course", "carbon:book", 3),
        ("课堂会话", "session", "carbon:calendar", 4),
        ("Emoji 数据", "emoji", "material-symbols:mood-outline", 5),
    ]
    for name, path, icon, order in children:
        if not await Menu.filter(path=path, parent_id=parent.id).exists():
            await Menu.create(
                menu_type=MenuType.MENU,
                name=name,
                path=path,
                order=order,
                parent_id=parent.id,
                icon=icon,
                is_hidden=False,
                component=f"/classroom/{path}",
                keepalive=False,
            )


async def init_apis():
    apis = await api_controller.model.exists()
    if not apis:
        await api_controller.refresh_api()
    # 旧库只补齐 D 控制 API，不删除/重置他人自定义权限。
    from app import app
    from fastapi.routing import APIRoute

    for route in app.routes:
        if isinstance(route, APIRoute) and "AI控制" in route.tags:
            for method in route.methods:
                await Api.get_or_create(
                    method=method, path=route.path, defaults={"summary": route.summary, "tags": "AI控制"}
                )


async def init_db():
    command = Command(tortoise_config=settings.TORTOISE_ORM)
    await command.init()
    # 永不生成迁移；唯一启动路径是仓库已提交的 0→1→… SQL。
    await command.upgrade(run_in_transaction=True)


async def _add_missing_apis(role: Role, apis: list[Api]) -> None:
    existing = set(await role.apis.all().values_list("id", flat=True))
    missing = [api for api in apis if api.id not in existing]
    if missing:
        await role.apis.add(*missing)


async def _add_missing_menus(role: Role, menus: list[Menu]) -> None:
    existing = set(await role.menus.all().values_list("id", flat=True))
    missing = [menu for menu in menus if menu.id not in existing]
    if missing:
        await role.menus.add(*missing)


async def init_roles():
    """初始化统一的 ADMIN / TEACHER / STUDENT 角色并幂等分配权限。

    课堂业务按角色名 STUDENT / TEACHER 判断归属，因此统一使用英文角色名；
    历史库中已有的中文模板角色不会被删除，只补齐缺失的业务角色。
    """

    await Role.get_or_create(name="ADMIN", defaults={"desc": "管理员角色"})
    await Role.get_or_create(name="TEACHER", defaults={"desc": "教师角色"})
    await Role.get_or_create(name="STUDENT", defaults={"desc": "学生角色"})

    admin_role = await Role.get(name="ADMIN")
    teacher_role = await Role.get(name="TEACHER")
    student_role = await Role.get(name="STUDENT")

    all_apis = await Api.all()
    all_menus = await Menu.all()
    basic_apis = await Api.filter(Q(tags="基础模块"))

    # 管理员：全部 API 与菜单。
    await _add_missing_apis(admin_role, all_apis)
    await _add_missing_menus(admin_role, all_menus)

    # 教师：基础模块 API + 实时课堂看板与多维统计菜单。
    await _add_missing_apis(teacher_role, basic_apis)
    ai_teacher_apis = await Api.filter(tags="AI控制").exclude(path__contains="credentials")
    ai_teacher_apis = [api for api in ai_teacher_apis if api.method == "GET" or "/jobs" in api.path]
    await _add_missing_apis(teacher_role, ai_teacher_apis)
    classroom_menu = await Menu.get_or_none(path="/classroom", parent_id=0)
    if classroom_menu is not None:
        teacher_menus = [classroom_menu] + await Menu.filter(
            parent_id=classroom_menu.id, path__in=["dashboard", "statistics", "ai-jobs"]
        )
        await _add_missing_menus(teacher_role, teacher_menus)

    # 学生：仅基础模块 API；学生入口由前端按 role_codes 渲染，无需后端菜单。
    await _add_missing_apis(student_role, basic_apis)


async def init_data():
    await init_db()
    await init_superuser()
    await init_menus()
    await init_classroom_menus()
    parent = await Menu.get(path="/classroom", parent_id=0)
    for name, path in [("AI采集设备", "ai-devices"), ("AI课堂任务", "ai-jobs")]:
        await Menu.get_or_create(
            parent_id=parent.id,
            path=path,
            defaults={
                "name": name,
                "menu_type": MenuType.MENU,
                "component": f"/classroom/{path}",
                "icon": "carbon:camera",
                "order": 6,
                "keepalive": False,
            },
        )
    await init_apis()
    await init_roles()
