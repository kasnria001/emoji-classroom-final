"""课堂会话和用户排课控制器。"""

from fastapi import HTTPException
from tortoise.exceptions import IntegrityError
from tortoise.expressions import Q

from app.core.crud import CRUDBase
from app.models.admin import User
from app.models.classroom import ClassSession, ScheduleUser
from app.schemas.classroom import (
    ClassSessionCreate,
    ClassSessionUpdate,
    ScheduleUserCreate,
)

from .course import course_controller


class SessionController(CRUDBase[ClassSession, ClassSessionCreate, ClassSessionUpdate]):
    def __init__(self):
        super().__init__(model=ClassSession)

    async def _require_user(self, user_id: int) -> User:
        user = await User.filter(id=user_id, is_active=True).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_for_teacher(self, session_id: int, teacher_id: int) -> ClassSession:
        session = await self.model.get_or_none(id=session_id).prefetch_related("course")
        if session is None:
            raise HTTPException(status_code=404, detail="Class session not found")
        if session.course.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Class session does not belong to the teacher")
        return session

    async def get_for_actor(self, session_id: int, actor_id: int) -> ClassSession:
        """按操作者校验课堂归属，允许管理员操作任意课堂。"""

        session = await self.model.get_or_none(id=session_id).prefetch_related("course")
        if session is None:
            raise HTTPException(status_code=404, detail="Class session not found")
        actor = await self._require_user(actor_id)
        if not actor.is_superuser and session.course.teacher_id != actor_id:
            raise HTTPException(status_code=403, detail="Class session does not belong to the teacher")
        return session

    async def create_session(self, obj_in: ClassSessionCreate, actor_id: int) -> ClassSession:
        await course_controller.get_for_actor(obj_in.course_id, actor_id)
        return await self.create(obj_in)

    async def update_session(self, obj_in: ClassSessionUpdate, actor_id: int) -> ClassSession:
        session = await self.get_for_actor(obj_in.id, actor_id)
        values = obj_in.model_dump(exclude_unset=True, exclude={"id"})
        if "course_id" in values:
            await course_controller.get_for_actor(values["course_id"], actor_id)
        start_time = values.get("start_time", session.start_time)
        end_time = values.get("end_time", session.end_time)
        if end_time <= start_time:
            raise HTTPException(status_code=422, detail="end_time must be later than start_time")
        return await self.update(obj_in.id, values)

    async def delete_session(self, session_id: int, actor_id: int) -> None:
        await self.get_for_actor(session_id, actor_id)
        await self.remove(session_id)

    async def list_for_teacher(self, teacher_id: int, page: int = 1, page_size: int = 20, course_id: int | None = None):
        search = Q(course__teacher_id=teacher_id)
        if course_id is not None:
            search &= Q(course_id=course_id)
        return await self.list(page, page_size, search=search, order=["-start_time"])

    async def list_for_user(self, user_id: int, page: int = 1, page_size: int = 20):
        """返回学生被安排的课堂，避免学生通过 course_id 越权读取。"""

        await self._require_user(user_id)
        schedule_query = ScheduleUser.filter(user_id=user_id).order_by("-scheduled_at")
        total = await schedule_query.count()
        schedules = await schedule_query.offset((page - 1) * page_size).limit(page_size).prefetch_related("session")
        return total, [item.session for item in schedules]

    async def schedule_user(self, obj_in: ScheduleUserCreate, actor_id: int) -> ScheduleUser:
        session = await self.get_for_actor(obj_in.session_id, actor_id)
        await self._require_user(obj_in.user_id)
        if await ScheduleUser.filter(session_id=session.id, user_id=obj_in.user_id).exists():
            raise HTTPException(status_code=409, detail="User is already scheduled for this session")
        values = obj_in.model_dump(exclude_unset=True)
        try:
            return await ScheduleUser.create(**values)
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail="Unable to schedule user") from exc

    async def unschedule_user(self, session_id: int, user_id: int, actor_id: int) -> None:
        await self.get_for_actor(session_id, actor_id)
        await ScheduleUser.filter(session_id=session_id, user_id=user_id).delete()

    async def is_user_scheduled(self, session_id: int, user_id: int) -> bool:
        return await ScheduleUser.filter(session_id=session_id, user_id=user_id).exists()

    async def list_scheduled_users(self, session_id: int, actor_id: int) -> list[ScheduleUser]:
        """查询某课堂已安排的用户（管理员或该课堂教师）。"""

        await self.get_for_actor(session_id, actor_id)
        return await ScheduleUser.filter(session_id=session_id).prefetch_related("user").order_by("scheduled_at")


session_controller = SessionController()
