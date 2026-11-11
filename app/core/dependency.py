from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException, Request

from app.core.ctx import CTX_USER_ID
from app.models import Course, Role, User
from app.settings import settings


class AuthControl:
    # 认证层负责确认当前用户身份，并把用户 ID 放入请求上下文。
    @classmethod
    async def is_authed(cls, token: str = Header(..., description="token验证")) -> Optional["User"]:
        try:
            decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
            user_id = decode_data.get("user_id")
            user = await User.filter(id=user_id).first()
            if not user or not user.is_active:
                raise HTTPException(status_code=401, detail="Authentication failed")
            CTX_USER_ID.set(int(user_id))
            return user
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="无效的Token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="登录已过期")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{repr(e)}")


class PermissionControl:
    # 权限层根据 HTTP 方法和完整路径匹配角色拥有的 API 权限。
    @classmethod
    async def has_permission(cls, request: Request, current_user: User = Depends(AuthControl.is_authed)) -> None:
        if current_user.is_superuser:
            return
        method = request.method
        # 以匹配到的 APIRoute 模板授权，不能用字符串前缀放行任意资源。
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        # 与 B 的 legacy course owner 身份一致，仅开放 D 教师功能，数据归属仍由服务强制。
        if (
            "AI控制" in getattr(route, "tags", [])
            and (method == "GET" or (method == "POST" and "/ai/jobs" in path))
            and await Course.filter(teacher_id=current_user.id).exists()
        ):
            return
        roles: list[Role] = await current_user.roles
        if not roles:
            raise HTTPException(status_code=403, detail="The user is not bound to a role")
        apis = [await role.apis for role in roles]
        permission_apis = list(set((api.method, api.path) for api in sum(apis, [])))
        # path = "/api/v1/auth/userinfo"
        # method = "GET"
        if (method, path) not in permission_apis:
            raise HTTPException(status_code=403, detail=f"Permission denied method:{method} path:{path}")


DependAuth = Depends(AuthControl.is_authed)
DependPermission = Depends(PermissionControl.has_permission)
