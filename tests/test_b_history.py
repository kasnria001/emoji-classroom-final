"""B 功能测试：个人历史与教师课堂记录的筛选、分页、统计及归属权限。"""
from datetime import datetime

import pytest

from app.models import EmojiRecord, ScheduleUser, User
from app.models.enums import EmojiSource, EmojiType
from conftest import _make_token
from test_classroom_api import _create_course, _create_session


@pytest.fixture
async def records(client):
    course_id = await _create_course(client)
    session_id = await _create_session(client, course_id)
    await ScheduleUser.create(session_id=session_id, user_id=client.student.id)
    other = await User.create(username="other-student", email="other@example.com", password="unused", is_active=True)
    for user_id, emotion, source, time in [
        (client.student.id, "HAPPY", "MANUAL", "10:00:00"),
        (client.student.id, "SAD", "MANUAL", "10:30:00"),
        (other.id, "ANGRY", "MANUAL", "10:15:00"),
        (None, "NEUTRAL", "AI", "11:00:00"),
        (client.student.id, "SURPRISED", "MANUAL", "12:00:00"),
    ]:
        record = await EmojiRecord.create(
            session_id=session_id,
            user_id=user_id,
            emoji_type=EmojiType(emotion),
            source=EmojiSource(source),
            confidence=0.9 if source == "AI" else None,
        )
        # auto_now_add is bypassed only in this isolated fixture for exact boundary tests.
        await EmojiRecord.filter(id=record.id).update(timestamp=datetime.fromisoformat("2026-11-09T" + time))
    return session_id


async def test_personal_history_is_own_paginated_and_inclusive(client, records):
    params = dict(session_id=records, from_time="2026-11-09 10:00:00", to_time="2026-11-09 11:00:00", page_size=1)
    headers = {"token": client.student_token}
    first = await client.get("/api/v1/emoji/history", params=params, headers=headers)
    assert first.status_code == 200
    body = first.json()
    assert body["total"] == 2 and body["page_size"] == 1
    assert len(body["data"]) == 1 and body["data"][0]["user_id"] == client.student.id
    second = (await client.get("/api/v1/emoji/history", params={**params, "page": 2}, headers=headers)).json()
    assert second["total"] == 2 and second["data"][0]["id"] != body["data"][0]["id"]
    exact = (
        await client.get("/api/v1/emoji/history", params={**params, "to_time": params["from_time"]}, headers=headers)
    ).json()
    assert exact["total"] == 1 and exact["data"][0]["emoji_type"] == "HAPPY"
    empty = (await client.get("/api/v1/emoji/history", params={**params, "page": 3}, headers=headers)).json()
    assert empty["total"] == 2 and empty["data"] == []


async def test_teacher_history_and_aggregate_use_identical_full_scope(client, records):
    headers = {"token": client.teacher_token}
    params = dict(session_id=records, from_time="2026-11-09 10:00:00", to_time="2026-11-09 11:00:00")
    for extra, expected in [
        ({}, 4),
        ({"source": "MANUAL"}, 3),
        ({"source": "AI"}, 1),
        ({"user_id": client.student.id}, 2),
        ({"user_id": client.student.id, "source": "AI"}, 0),
    ]:
        scope = {**params, **extra}
        response = await client.get("/api/v1/emoji", params={**scope, "page_size": 1}, headers=headers)
        aggregate = await client.get("/api/v1/emoji/statistics", params=scope, headers=headers)
        assert response.status_code == aggregate.status_code == 200
        listing, summary = response.json(), aggregate.json()["data"]
        assert listing["total"] == expected
        assert sum(item["count"] for item in summary) == expected
        assert len(listing["data"]) == min(1, expected)
        if expected:
            assert sum(item["percentage"] for item in summary) == pytest.approx(100, abs=0.02)
        else:
            assert summary == []
    ai = (await client.get("/api/v1/emoji", params={**params, "source": "AI"}, headers=headers)).json()["data"]
    assert ai[0]["user_id"] is None and ai[0]["username"] is None
    assert ai[0]["timestamp"] == "2026-11-09 11:00:00"


async def test_statistics_denies_students_and_other_teachers_even_empty_classroom(client, records):
    other = await User.create(username="other-teacher", email="teacher2@example.com", password="unused", is_active=True)
    for token in [client.student_token, _make_token(other)]:
        response = await client.get(
            "/api/v1/emoji/statistics", params={"session_id": records}, headers={"token": token}
        )
        assert response.status_code == 403
    # A valid teacher may read an empty owned classroom; foreign ownership still fails.
    empty = await _create_session(client, await _create_course(client, name="empty"))
    allowed = await client.get(
        "/api/v1/emoji/statistics", params={"session_id": empty}, headers={"token": client.teacher_token}
    )
    assert allowed.status_code == 200 and allowed.json()["data"] == []
    denied = await client.get(
        "/api/v1/emoji/statistics", params={"session_id": empty}, headers={"token": client.student_token}
    )
    assert denied.status_code == 403
    other_history = await client.get(
        "/api/v1/emoji/history", params={"user_id": other.id}, headers={"token": client.student_token}
    )
    assert other_history.status_code == 403


async def test_history_pagination_has_stable_tie_breaker(client, records):
    await EmojiRecord.filter(session_id=records).update(timestamp=datetime(2026, 11, 9, 10))
    for path, token, filters in [
        ("/emoji", client.teacher_token, {}),
        ("/emoji/history", client.student_token, {"user_id": client.student.id}),
    ]:
        expected = await EmojiRecord.filter(session_id=records, **filters).order_by("-id").values_list("id", flat=True)
        actual = []
        for page in range(1, len(expected) + 1):
            response = await client.get(
                "/api/v1" + path, params={"session_id": records, "page": page, "page_size": 1}, headers={"token": token}
            )
            assert response.status_code == 200
            actual.append(response.json()["data"][0]["id"])
        assert actual == expected


@pytest.mark.parametrize("field", ["session_id", "user_id"])
async def test_statistics_rejects_zero_identifier_instead_of_widening_scope(client, field):
    response = await client.get("/api/v1/emoji/statistics", params={field: 0}, headers={"token": client.teacher_token})
    assert response.status_code == 422


@pytest.mark.parametrize("path", ["/emoji", "/emoji/history", "/emoji/statistics"])
@pytest.mark.parametrize(
    "times",
    [
        {"from_time": "2026-11-10 00:00:00", "to_time": "2026-11-09 00:00:00"},
        {"from_time": "2026-11-09T00:00:00+08:00"},
        {"to_time": "2026-11-09T00:00:00Z"},
    ],
)
async def test_filter_rejects_reverse_ranges_and_timezone_offsets(client, path, times):
    response = await client.get("/api/v1" + path, params=times, headers={"token": client.teacher_token})
    assert response.status_code == 422
