"""B 功能测试：管理员和教师排课均拒绝教师账号，学生可正常排课。"""

import pytest

from app.models import Course, Role, ScheduleUser, User
from conftest import _make_token
from test_classroom_api import _create_course, _create_session


@pytest.mark.parametrize("operator", ["teacher", "administrator"])
async def test_schedule_rejects_teachers_and_accepts_students(client, operator):
    session_id = await _create_session(client, await _create_course(client))
    token = client.teacher_token
    if operator == "administrator":
        admin = await User.create(
            username="schedule-admin",
            email="schedule-admin@example.com",
            password="unused",
            is_active=True,
            is_superuser=True,
        )
        token = _make_token(admin)
    headers = {"token": token}
    teacher_role = await Role.create(name="TEACHER")
    student_role = await Role.create(name="STUDENT")
    role_teacher = await User.create(
        username="role-teacher", email="role-teacher@example.com", password="unused", is_active=True
    )
    await role_teacher.roles.add(teacher_role)
    dual = await User.create(username="dual-teacher", email="dual@example.com", password="unused", is_active=True)
    await dual.roles.add(teacher_role, student_role)
    other_teacher = await User.create(
        username="other-owner", email="owner@example.com", password="unused", is_active=True
    )
    await Course.create(name="Other owned course", teacher_id=other_teacher.id)
    for target in [client.teacher, role_teacher, dual, other_teacher]:
        response = await client.post(
            f"/api/v1/sessions/{session_id}/schedule", json={"user_id": target.id}, headers=headers
        )
        assert response.status_code == 422
        assert not await ScheduleUser.filter(session_id=session_id, user_id=target.id).exists()
    await client.student.roles.add(student_role)
    response = await client.post(
        f"/api/v1/sessions/{session_id}/schedule", json={"user_id": client.student.id}, headers=headers
    )
    assert response.status_code == 200
    assert await ScheduleUser.filter(session_id=session_id, user_id=client.student.id).exists()
