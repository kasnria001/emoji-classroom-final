r"""导入演示数据：教师/学生账号、课程、课堂、排课与 Emoji 记录。

脚本会先执行 init_data 确保表结构与基础角色存在（幂等），再写入演示数据。
重复运行不会产生重复记录。

用法（在仓库根目录执行）：

    .\.venv\Scripts\python.exe scripts\seed_demo.py
"""

import asyncio
import sys
from datetime import timedelta
from pathlib import Path

# 允许从仓库任意位置直接运行本脚本。
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tortoise import Tortoise

from app.core.init_app import init_data
from app.models.admin import Role, User
from app.models.classroom import ClassSession, Course, EmojiRecord, ScheduleUser
from app.models.enums import EmojiSource, EmojiType
from app.utils.password import get_password_hash
from app.utils.time import beijing_now


async def ensure_user(username: str, email: str, password: str, role_name: str) -> User:
    user = await User.filter(username=username).first()
    if user is None:
        user = await User.create(
            username=username,
            email=email,
            password=get_password_hash(password),
            is_active=True,
            is_superuser=False,
        )
    role = await Role.get_or_none(name=role_name)
    if role is not None and not await user.roles.filter(id=role.id).exists():
        await user.roles.add(role)
    if not user.user_no:
        user.user_no = await User.next_user_no(role_name)
        await user.save()
    return user


async def main() -> None:
    await init_data()

    teacher = await ensure_user("teacher", "teacher@example.com", "Teacher123", "TEACHER")
    student = await ensure_user("student", "student@example.com", "Student123", "STUDENT")
    student2 = await ensure_user("student2", "student2@example.com", "Student123", "STUDENT")

    courses = []
    for name in ["数据结构", "软件工程"]:
        course = await Course.filter(name=name, teacher_id=teacher.id).first()
        if course is None:
            course = await Course.create(name=name, teacher_id=teacher.id, description=f"{name}课堂演示")
        courses.append(course)

    now = beijing_now()
    sessions = []
    for index, course in enumerate([courses[0], courses[0], courses[1]]):
        start = now - timedelta(days=2 - index, hours=1)
        end = start + timedelta(hours=1)
        classroom = f"A10{index + 1}"
        class_name = f"计科230{index + 1}"
        session = await ClassSession.filter(course_id=course.id, classroom=classroom).first()
        if session is None:
            session = await ClassSession.create(
                course_id=course.id,
                start_time=start,
                end_time=end,
                classroom=classroom,
                class_name=class_name,
            )
        sessions.append(session)

    for session in sessions[:2]:
        for user in (student, student2):
            if not await ScheduleUser.filter(session_id=session.id, user_id=user.id).exists():
                await ScheduleUser.create(session_id=session.id, user_id=user.id)

    if await EmojiRecord.exists():
        print("已存在 Emoji 记录，跳过 Emoji 导入")
    else:
        s1, s2, s3 = sessions
        manual_records = [
            (s1, student, EmojiType.HAPPY),
            (s1, student2, EmojiType.SURPRISED),
            (s1, student, EmojiType.NEUTRAL),
            (s2, student, EmojiType.SAD),
            (s2, student2, EmojiType.HAPPY),
            (s2, student, EmojiType.ANGRY),
            (s3, student, EmojiType.HAPPY),
            (s3, student2, EmojiType.NEUTRAL),
        ]
        for session, user, emoji_type in manual_records:
            await EmojiRecord.create(
                user_id=user.id,
                session_id=session.id,
                emoji_type=emoji_type,
                source=EmojiSource.MANUAL,
            )
        await EmojiRecord.create(
            session_id=s1.id,
            emoji_type=EmojiType.HAPPY,
            source=EmojiSource.AI,
            confidence=0.91,
            device_source="camera-01",
        )
        await EmojiRecord.create(
            session_id=s2.id,
            emoji_type=EmojiType.NEUTRAL,
            source=EmojiSource.AI,
            confidence=0.78,
            device_source="camera-01",
        )

    await Tortoise.close_connections()
    print("演示数据导入完成")
    print("账号：teacher/Teacher123（教师）、student/Student123、student2/Student123（学生）")
    print("数据：课程 2 门、课堂 3 个、排课 4 条、Emoji 10 条（8 手动 + 2 AI）")


if __name__ == "__main__":
    asyncio.run(main())
