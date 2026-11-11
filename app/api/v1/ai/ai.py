"""AI 推理服务入库 REST API。"""

from fastapi import APIRouter

router = APIRouter()

# AI 服务使用独立设备凭证，不复用学生 JWT，也不使用永久全局 token。
# 设备/job/lease/receipt 完成前不注册入库路由；契约见 docs/AI_INTEGRATION.md。
