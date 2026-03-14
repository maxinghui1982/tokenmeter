"""
TokenMeter Prometheus Metrics
监控指标收集
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from functools import wraps
import time
from typing import Callable

# 应用信息
APP_INFO = Info("tokenmeter_app", "TokenMeter application information")

# HTTP 请求指标
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently in progress",
    ["method", "endpoint"],
)

# 业务指标 - API 调用
API_CALLS_TOTAL = Counter(
    "tokenmeter_api_calls_total", "Total API calls to providers", ["provider", "model", "status"]
)

API_CALL_DURATION = Histogram(
    "tokenmeter_api_call_duration_seconds",
    "API call duration",
    ["provider", "model"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

API_CALL_TOKENS = Counter(
    "tokenmeter_api_call_tokens_total",
    "Total tokens used",
    ["provider", "model", "token_type"],  # token_type: prompt, completion
)

# 业务指标 - 成本
COST_TOTAL = Counter(
    "tokenmeter_cost_total", "Total cost in USD", ["provider", "model", "project", "team"]
)

COST_CURRENT = Gauge(
    "tokenmeter_cost_current_period",
    "Current period cost in USD",
    ["period", "project"],  # period: daily, weekly, monthly
)

# 业务指标 - 预算
BUDGET_ALERTS = Counter(
    "tokenmeter_budget_alerts_total",
    "Total budget alerts triggered",
    ["severity"],  # severity: warning, critical
)

BUDGET_USAGE = Gauge(
    "tokenmeter_budget_usage_percent", "Budget usage percentage", ["budget_name", "project"]
)

# 系统指标
ACTIVE_USERS = Gauge("tokenmeter_active_users", "Number of active users", [])

DB_CONNECTIONS = Gauge("tokenmeter_db_connections", "Database connection pool size", [])


# 初始化应用信息
def init_metrics(app_version: str, app_env: str):
    """初始化指标"""
    APP_INFO.info({"version": app_version, "environment": app_env})


def metrics_middleware():
    """FastAPI 中间件 - 收集 HTTP 指标"""
    from starlette.middleware.base import BaseHTTPMiddleware

    class PrometheusMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            method = request.method
            path = request.url.path

            # 跳过指标端点自身
            if path == "/metrics":
                return await call_next(request)

            # 记录进行中请求
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).inc()

            start_time = time.time()

            try:
                response = await call_next(request)
                status_code = str(response.status_code)
            except Exception as e:
                status_code = "500"
                raise
            finally:
                # 记录请求完成
                duration = time.time() - start_time
                HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).dec()
                HTTP_REQUESTS_TOTAL.labels(
                    method=method, endpoint=path, status_code=status_code
                ).inc()
                HTTP_REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)

            return response

    return PrometheusMiddleware


def track_api_call(provider: str, model: str, status: str):
    """追踪 API 调用"""
    API_CALLS_TOTAL.labels(provider=provider, model=model, status=status).inc()


def track_api_duration(provider: str, model: str, duration: float):
    """追踪 API 调用耗时"""
    API_CALL_DURATION.labels(provider=provider, model=model).observe(duration)


def track_tokens(provider: str, model: str, prompt_tokens: int, completion_tokens: int):
    """追踪 Token 使用量"""
    API_CALL_TOKENS.labels(provider=provider, model=model, token_type="prompt").inc(prompt_tokens)
    API_CALL_TOKENS.labels(provider=provider, model=model, token_type="completion").inc(
        completion_tokens
    )


def track_cost(
    provider: str, model: str, cost: float, project: str = "default", team: str = "default"
):
    """追踪成本"""
    COST_TOTAL.labels(provider=provider, model=model, project=project, team=team).inc(cost)


def get_metrics():
    """获取 Prometheus 格式的指标"""
    return generate_latest()
