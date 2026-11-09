"""B 功能测试：教师不能删除课程，管理员可删除课程。"""

from app.models import Course, User
from conftest import _make_token
from test_classroom_api import _create_course


async def test_course_delete_requires_administrator(client):
    course_id = await _create_course(client)
    for token in [client.teacher_token, client.student_token]:
        response = await client.delete(f"/api/v1/courses/{course_id}", headers={"token": token})
        assert response.status_code == 403
        assert await Course.filter(id=course_id).exists()
    admin = await User.create(
        username="delete-admin", email="delete-admin@example.com", password="unused", is_active=True, is_superuser=True
    )
    response = await client.delete(f"/api/v1/courses/{course_id}", headers={"token": _make_token(admin)})
    assert response.status_code == 200
    assert not await Course.filter(id=course_id).exists()
