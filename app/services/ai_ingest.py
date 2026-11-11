"""AI 入库的可测试边界规则。

设备认证、租约和幂等事务尚未实现，本模块不提供无鉴权写库入口。
"""

import hashlib
import json
from datetime import datetime, timedelta

from app.schemas.ai import AIIngestEvent
from app.utils.time import BEIJING


def canonical_event(event: AIIngestEvent) -> str:
    """归一化 UUID/UTC/浮点字段，为相同事件的重试生成稳定内容。"""

    return json.dumps(
        event.model_dump(mode="json", exclude_none=True),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def event_payload_hash(event: AIIngestEvent) -> str:
    return hashlib.sha256(canonical_event(event).encode("utf-8")).hexdigest()


def business_timestamp(event: AIIngestEvent) -> datetime:
    """仅在新 AI 边界将 UTC 转为旧 A/B/C 使用的北京 wall-clock。"""

    return event.captured_at.astimezone(BEIJING).replace(tzinfo=None)


def validate_capture_time(
    event: AIIngestEvent,
    *,
    session_start: datetime,
    session_end: datetime,
    now: datetime,
    max_lateness: timedelta = timedelta(minutes=15),
    future_skew: timedelta = timedelta(seconds=30),
) -> datetime:
    """校验课堂 [start,end) 与实时补交窗；租约采集窗须额外校验。

    课堂输入沿用已有无时区北京时间，now 必须有时区。阈值是协议初值，
    不意味着允许绕过任务、已撤销设备或 generation/fencing 校验。
    """

    if session_start.utcoffset() is not None or session_end.utcoffset() is not None:
        raise ValueError("Session times must use Beijing wall-clock")
    if now.utcoffset() is None:
        raise ValueError("Server time must be timezone-aware")
    if session_end <= session_start or max_lateness < timedelta(0) or future_skew < timedelta(0):
        raise ValueError("Invalid capture time policy")
    timestamp = business_timestamp(event)
    if not session_start <= timestamp < session_end:
        raise ValueError("Capture is outside the classroom time window")
    if event.captured_at > now + future_skew:
        raise ValueError("Capture is too far in the future")
    if event.captured_at < now - max_lateness:
        raise ValueError("Capture is outside the realtime retry window")
    return timestamp
