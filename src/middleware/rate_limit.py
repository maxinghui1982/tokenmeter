"""
TokenMeter Rate Limiting 中间件
请求限流保护
"""
import time
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..config.settings import settings


class RateLimiter:
    """简单内存限流器（生产环境建议使用 Redis）"""

    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.clients: Dict[str, list] = {}  # client_id -> [timestamps]

    def is_allowed(self, client_id: str) -> Tuple[bool, Optional[int]]:
        """
        检查请求是否允许
        Returns: (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - 60  # 1分钟窗口

        # 清理过期记录
        if client_id in self.clients:
            self.clients[client_id] = [
                ts for ts in self.clients[client_id] if ts > window_start
            ]
        else:
            self.clients[client_id] = []

        # 检查突发限制
        if len(self.clients[client_id]) >= self.burst_size:
            retry_after = int(60 - (now - self.clients[client_id][0]))
            return False, max(1, retry_after)

        # 检查速率限制
        if len(self.clients[client_id]) >= self.requests_per_minute:
            retry_after = int(60 - (now - self.clients[client_id][0]))
            return False, max(1, retry_after)

        # 允许请求
        self.clients[client_id].append(now)
        return True, None

    def reset(self, client_id: str):
        """重置客户端限制"""
        if client_id in self.clients:
            del self.clients[client_id]


# 全局限流器实例
rate_limiter = RateLimiter(
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    burst_size=settings.RATE_LIMIT_BURST,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""

    async def dispatch(self, request: Request, call_next):
        # 获取客户端标识
        client_id = self._get_client_id(request)

        # 检查健康检查端点（不限流）
        if request.url.path in ["/api/v1/health", "/api/v1/ready", "/"]:
            return await call_next(request)

        # 检查限流
        is_allowed, retry_after = rate_limiter.is_allowed(client_id)

        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": f"请求过于频繁，请在 {retry_after} 秒后重试",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # 继续处理请求
        response = await call_next(request)

        # 添加限流响应头
        remaining = max(
            0, settings.RATE_LIMIT_PER_MINUTE - len(rate_limiter.clients.get(client_id, []))
        )
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response

    def _get_client_id(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用 X-Forwarded-For（代理场景）
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # 使用 X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 使用直接连接的客户端 IP
        if request.client:
            return request.client.host

        # 兜底方案
        return "unknown"


# 登录尝试限制器
class LoginAttemptLimiter:
    """登录尝试限制器（防止暴力破解）"""

    def __init__(self):
        self.attempts: Dict[str, Dict] = {}  # username/identifier -> {count, locked_until}

    def is_allowed(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """检查是否允许登录尝试"""
        now = time.time()

        if identifier in self.attempts:
            attempt = self.attempts[identifier]

            # 检查是否仍在锁定中
            if attempt.get("locked_until") and now < attempt["locked_until"]:
                remaining = int(attempt["locked_until"] - now)
                return False, remaining

            # 锁定已过期，重置计数
            if attempt.get("locked_until") and now >= attempt["locked_until"]:
                del self.attempts[identifier]

        return True, None

    def record_attempt(self, identifier: str):
        """记录一次失败尝试"""
        now = time.time()

        if identifier not in self.attempts:
            self.attempts[identifier] = {"count": 0}

        self.attempts[identifier]["count"] += 1

        # 超过限制，锁定账户
        if self.attempts[identifier]["count"] >= settings.MAX_LOGIN_ATTEMPTS:
            lockout_seconds = settings.LOGIN_LOCKOUT_MINUTES * 60
            self.attempts[identifier]["locked_until"] = now + lockout_seconds
            return settings.LOGIN_LOCKOUT_MINUTES

        return None

    def reset(self, identifier: str):
        """重置登录尝试（成功登录后调用）"""
        if identifier in self.attempts:
            del self.attempts[identifier]


# 全局登录限制器
login_limiter = LoginAttemptLimiter()
