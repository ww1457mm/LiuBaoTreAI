import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.utils.logging_config import logger

# Rate limiting storage: openid -> [(timestamp, path), ...]
_rate_store: dict[str, list[tuple[float, str]]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """基于 IP + User-Agent 的简单限流中间件，每个端点每分钟最多 N 次请求。"""

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        burst_size: int = 10,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.window = 60.0

    def _key(self, request: Request) -> str:
        openid = request.query_params.get("openid", "")
        if openid:
            return f"openid:{openid}"
        return f"ip:{request.client.host if request.client else 'unknown'}"

    def _is_rate_limited(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window
        entries = _rate_store[key]
        entries[:] = [(ts, p) for ts, p in entries if ts > window_start]
        if len(entries) >= self.requests_per_minute:
            return True
        entries.append((now, ""))
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        key = self._key(request)
        if self._is_rate_limited(key):
            return JSONResponse(
                status_code=429,
                content={"code": 429, "message": "请求过于频繁，请稍后再试"},
            )
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件，记录每个请求的耗时、状态码和路径。"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start = time.perf_counter()
        path = request.url.path
        method = request.method

        logger.info(
            f"[{request_id}] --> {method} {path} | query: {dict(request.query_params)}"
        )

        try:
            response = await call_next(request)
            elapsed = round((time.perf_counter() - start) * 1000, 1)
            status = response.status_code
            logger.info(
                f"[{request_id}] <-- {method} {path} | {status} | {elapsed}ms"
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            elapsed = round((time.perf_counter() - start) * 1000, 1)
            logger.error(
                f"[{request_id}] !! {method} {path} | ERROR | {elapsed}ms | {exc}"
            )
            raise


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(f"[{request_id}] Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器内部错误，请稍后重试",
                "request_id": request_id,
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": f"参数错误：{exc}"},
        )

    @app.exception_handler(TimeoutError)
    async def timeout_error_handler(request: Request, exc: TimeoutError):
        return JSONResponse(
            status_code=504,
            content={"code": 504, "message": "请求超时，请稍后重试"},
        )
