"""课堂情绪统计服务。

负责把 EmojiRecord 按课程、班级、时间段等维度聚合成管理端统计图表
所需的数据结构。本服务只做聚合与格式化，权限过滤由调用方在传入
查询集时完成。
"""

from collections import Counter
from datetime import datetime

from tortoise.queryset import QuerySet

from app.models.classroom import EmojiRecord


async def _records(
    actor_id: int,
    is_superuser: bool,
    course_id: int | None = None,
    class_name: str | None = None,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> list[EmojiRecord]:
    query: QuerySet = EmojiRecord.all().select_related("session__course")
    if not is_superuser:
        query = query.filter(session__course__teacher_id=actor_id)
    if course_id is not None:
        query = query.filter(session__course_id=course_id)
    if class_name:
        query = query.filter(session__class_name=class_name)
    if from_time is not None:
        query = query.filter(timestamp__gte=from_time)
    if to_time is not None:
        query = query.filter(timestamp__lte=to_time)
    return await query.order_by("timestamp")


def _ratio(count: int, total: int) -> float:
    return round(count * 100 / total, 2) if total else 0.0


async def get_statistics(
    actor_id: int,
    is_superuser: bool,
    course_id: int | None = None,
    class_name: str | None = None,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> dict:
    """聚合多维统计数据，供管理端统计图表使用。"""

    records = await _records(actor_id, is_superuser, course_id, class_name, from_time, to_time)
    total = len(records)

    type_counter: Counter = Counter()
    course_counter: Counter = Counter()
    class_counter: Counter = Counter()
    source_counter: Counter = Counter()
    day_counter: Counter = Counter()
    hour_counter: Counter = Counter()
    student_ids: set[int] = set()

    for record in records:
        type_counter[str(record.emoji_type.value if hasattr(record.emoji_type, "value") else record.emoji_type)] += 1
        source = str(record.source.value if hasattr(record.source, "value") else record.source)
        source_counter[source] += 1
        if record.user_id is not None:
            student_ids.add(record.user_id)
        course_name = record.session.course.name if record.session.course else "未知课程"
        course_counter[(record.session.course_id, course_name)] += 1
        class_counter[record.session.class_name or "未分班"] += 1
        if record.timestamp is not None:
            day_counter[record.timestamp.strftime("%Y-%m-%d")] += 1
            hour_counter[record.timestamp.strftime("%H:00")] += 1

    def _sort(counter: Counter) -> list[dict]:
        return [{"key": key, "count": count} for key, count in counter.most_common()]

    return {
        "overview": {
            "total_records": total,
            "total_students": len(student_ids),
            "manual_records": source_counter.get("MANUAL", 0),
            "ai_records": source_counter.get("AI", 0),
        },
        "by_type": [
            {"emoji_type": item["key"], "count": item["count"], "percentage": _ratio(item["count"], total)}
            for item in _sort(type_counter)
        ],
        "by_course": [
            {"course_id": key[0], "course_name": key[1], "count": count, "percentage": _ratio(count, total)}
            for key, count in course_counter.most_common()
        ],
        "by_class": [
            {"class_name": item["key"], "count": item["count"], "percentage": _ratio(item["count"], total)}
            for item in _sort(class_counter)
        ],
        "by_source": [
            {"source": item["key"], "count": item["count"], "percentage": _ratio(item["count"], total)}
            for item in _sort(source_counter)
        ],
        "by_day": [{"day": key, "count": count} for key, count in sorted(day_counter.items())],
        "by_hour": [{"hour": key, "count": count} for key, count in sorted(hour_counter.items())],
    }


async def get_realtime_dashboard(
    actor_id: int,
    is_superuser: bool,
    session_id: int,
) -> dict:
    """聚合单个课堂会话的实时看板数据。"""

    from app.models.classroom import ClassSession

    session = await ClassSession.get_or_none(id=session_id).prefetch_related("course")
    if session is None:
        return {"found": False}

    # 教师只能查看自己所授课程的课堂。
    if not is_superuser and session.course.teacher_id != actor_id:
        return {"found": True, "forbidden": True}

    records = await EmojiRecord.filter(session_id=session_id).order_by("timestamp")
    total = len(records)

    type_counter: Counter = Counter()
    source_counter: Counter = Counter()
    minute_counter: Counter = Counter()
    student_ids: set[int] = set()

    for record in records:
        type_counter[str(record.emoji_type.value if hasattr(record.emoji_type, "value") else record.emoji_type)] += 1
        source = str(record.source.value if hasattr(record.source, "value") else record.source)
        source_counter[source] += 1
        if record.user_id is not None:
            student_ids.add(record.user_id)
        if record.timestamp is not None:
            minute_counter[record.timestamp.strftime("%Y-%m-%d %H:%M")] += 1

    return {
        "found": True,
        "forbidden": False,
        "session": {
            "id": session.id,
            "course_id": session.course_id,
            "course_name": session.course.name if session.course else "",
            "class_name": session.class_name,
            "classroom": session.classroom,
            "start_time": session.start_time.strftime("%Y-%m-%d %H:%M:%S") if session.start_time else None,
            "end_time": session.end_time.strftime("%Y-%m-%d %H:%M:%S") if session.end_time else None,
        },
        "summary": [
            {"emoji_type": key, "count": count, "percentage": _ratio(count, total)}
            for key, count in type_counter.most_common()
        ],
        "total_count": total,
        "student_count": len(student_ids),
        "manual_count": source_counter.get("MANUAL", 0),
        "ai_count": source_counter.get("AI", 0),
        "timeline": [{"time": key, "count": count} for key, count in sorted(minute_counter.items())],
    }
