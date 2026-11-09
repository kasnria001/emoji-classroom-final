"""安全测试：弱密码、SQL 注入与 CSV 公式注入防护。"""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

from app.api.v1.base import base_router
from app.api.v1.courses import courses_router
from app.api.v1.emoji import emoji_router
from app.api.v1.sessions import sessions_router
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
from app.models import User
from app.services.export import build_csv
from app.utils.password import get_password_hash


def _register_exceptions(app: FastAPI) -> None:
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)


@pytest.fixture
async def client(tmp_path):
    """独立的 SQLite 测试库，挂载认证、课程、课堂和 Emoji 路由。"""

    config = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": str(tmp_path / "security_test.sqlite3")},
            }
        },
        "apps": {
            "models": {
                "models": ["app.models"],
                "default_connection": "default",
            }
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    }

    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()

    student = await User.create(
        username="student",
        email="student@example.com",
        password=get_password_hash("Student123"),
        is_active=True,
        is_superuser=False,
    )

    app = FastAPI(title="emoji-classroom-security-test")
    _register_exceptions(app)
    app.include_router(base_router, prefix="/api/v1/base")
    app.include_router(courses_router, prefix="/api/v1")
    app.include_router(sessions_router, prefix="/api/v1")
    app.include_router(emoji_router, prefix="/api/v1")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        test_client.student = student
        yield test_client

    await Tortoise.close_connections()


# ---------- 弱密码 ----------

async def test_register_rejects_weak_passwords(client):
    for weak in ["password", "12345678", "pass", "abcdefgh"]:
        resp = await client.post(
            "/api/v1/base/register",
            json={"username": "weak", "email": f"weak-{weak}@example.com", "password": weak},
        )
        assert resp.status_code == 422, f"weak password accepted: {weak!r}"


async def test_register_accepts_strong_password_and_logs_in(client):
    resp = await client.post(
        "/api/v1/base/register",
        json={"username": "strong", "email": "strong@example.com", "password": "Passw0rd123"},
    )
    assert resp.status_code == 200

    resp = await client.post(
        "/api/v1/base/access_token", json={"username": "strong", "password": "Passw0rd123"}
    )
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    info = await client.get("/api/v1/base/userinfo", headers={"token": token})
    assert "STUDENT" in info.json()["data"]["role_codes"]


async def test_teacher_registration_assigns_teacher_role(client):
    resp = await client.post(
        "/api/v1/base/register-teacher",
        json={"username": "teacher2", "email": "teacher2@example.com", "password": "Teacher123"},
    )
    assert resp.status_code == 200

    resp = await client.post(
        "/api/v1/base/access_token", json={"username": "teacher2", "password": "Teacher123"}
    )
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    info = await client.get("/api/v1/base/userinfo", headers={"token": token})
    assert "TEACHER" in info.json()["data"]["role_codes"]


async def test_user_no_uses_independent_per_role_sequence(client):
    first = await client.post(
        "/api/v1/base/register",
        json={"username": "first", "email": "first@example.com", "password": "Student123"},
    )
    assert first.status_code == 200
    assert first.json()["data"]["user_no"] == "PB0001"

    second = await client.post(
        "/api/v1/base/register",
        json={"username": "second", "email": "second@example.com", "password": "Student123"},
    )
    assert second.status_code == 200
    assert second.json()["data"]["user_no"] == "PB0002"

    teacher = await client.post(
        "/api/v1/base/register-teacher",
        json={"username": "seqteacher", "email": "seqteacher@example.com", "password": "Teacher123"},
    )
    assert teacher.status_code == 200
    assert teacher.json()["data"]["user_no"] == "TB0001"


async def test_update_password_rejects_weak_password(client):
    resp = await client.post(
        "/api/v1/base/access_token", json={"username": "student", "password": "Student123"}
    )
    token = resp.json()["data"]["access_token"]

    resp = await client.post(
        "/api/v1/base/update_password",
        json={"old_password": "Student123", "new_password": "allletters"},
        headers={"token": token},
    )
    assert resp.status_code == 422


# ---------- SQL 注入 ----------

async def test_sql_injection_login_does_not_authenticate(client):
    resp = await client.post(
        "/api/v1/base/access_token",
        json={"username": "student' OR '1'='1", "password": "whatever1"},
    )
    assert resp.status_code == 400


async def test_sql_injection_user_id_param_is_rejected(client):
    login = await client.post(
        "/api/v1/base/access_token", json={"username": "student", "password": "Student123"}
    )
    token = login.json()["data"]["access_token"]

    resp = await client.get(
        "/api/v1/emoji/history",
        params={"user_id": "1 OR 1=1"},
        headers={"token": token},
    )
    # 参数类型为 int，注入字符串会在查询执行前被校验拒绝。
    assert resp.status_code == 422


async def test_sql_injection_in_login_username_not_found(client):
    resp = await client.post(
        "/api/v1/base/access_token",
        json={"username": "'; DROP TABLE user", "password": "whatever1"},
    )
    # 注入字符串被当作普通用户名处理，未匹配到账号即拒绝登录。
    assert resp.status_code == 400


# ---------- CSV 公式注入 ----------

def test_csv_formula_injection_is_neutralized():
    content = build_csv(
        ["device_source", "username"],
        [["=cmd|' /C calc'!A0", "=HYPERLINK(\"http://evil\")"], ["normal", "ok"]],
    )
    assert "'=cmd" in content
    assert "'=HYPERLINK" in content
    # 普通值不应被错误加前缀。
    assert "normal" in content
