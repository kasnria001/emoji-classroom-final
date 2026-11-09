"""B 功能测试：教师和学生不能删除课堂会话，管理员可删除。"""

from app.models import ClassSession, User
from conftest import _make_token
from test_classroom_api import _create_course, _create_session


async def test_session_delete_requires_administrator(client):
    session_id = await _create_session(client, await _create_course(client))
    for token in [client.teacher_token, client.student_token]:
        response = await client.delete(f"/api/v1/sessions/{session_id}", headers={"token": token})
        assert response.status_code == 403
        assert await ClassSession.filter(id=session_id).exists()
    admin = await User.create(
        username="session-admin", email="session-admin@example.com", password="unused", is_active=True, is_superuser=True
    )
    response = await client.delete(f"/api/v1/sessions/{session_id}", headers={"token": _make_token(admin)})
    assert response.status_code == 200
    assert not await ClassSession.filter(id=session_id).exists()
