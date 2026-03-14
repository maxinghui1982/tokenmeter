"""
TokenMeter Metrics API
Prometheus 指标端点
"""
from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST

from .metrics import get_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics():
    """
    Prometheus 指标端点

    返回 Prometheus 格式的监控指标，包括：
    - HTTP 请求指标（数量、耗时、状态码）
    - API 调用指标（按提供商、模型）
    - 成本指标（总成本、当前周期成本）
    - 预算指标（使用率、告警次数）
    """
    return Response(content=get_metrics(), media_type=CONTENT_TYPE_LATEST)
