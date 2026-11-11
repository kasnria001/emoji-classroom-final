"""AI JSON 读取前字节限制，含 chunked 请求，先于 audit。"""

import json

from starlette.responses import JSONResponse


class AIBoundaryMiddleware:
    def __init__(self, app, limit=256 * 1024):
        self.app, self.limit = app, limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope["path"].startswith("/api/v1/ai/"):
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        if scope["method"] not in ("POST", "PUT", "PATCH"):
            return await self.app(scope, receive, send)

        async def error(code, msg):
            await JSONResponse({"code": code, "msg": msg, "data": None}, code)(scope, receive, send)

        try:
            length = int(headers.get(b"content-length", b"0"))
        except ValueError:
            return await error(400, "Invalid Content-Length")
        if length < 0 or length > self.limit:
            return await error(413, "AI request exceeds byte limit")
        if not headers.get(b"content-type", b"").lower().startswith(b"application/json"):
            return await error(415, "AI API requires JSON metadata")
        chunks, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > self.limit:
                return await error(413, "AI request exceeds byte limit")
            chunks.append(chunk)
            if not message.get("more_body"):
                break
        body = b"".join(chunks)
        try:
            if not isinstance(json.loads(body), dict):
                raise ValueError()
        except (ValueError, UnicodeError):
            return await error(422, "Invalid JSON metadata")
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        await self.app(scope, replay, send)
