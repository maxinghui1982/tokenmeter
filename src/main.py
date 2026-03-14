"""
TokenMeter Main Application
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database.models import db_manager
from .api.routes import router as api_router
from .api.budget_routes import router as budget_router
from .api.auth_routes import router as auth_router
from .api.export_routes import router as export_router
from .web.dashboard import router as web_router
from .proxy.handler import ProxyHandler
from .utils.logging_config import setup_logging, get_logger
from .utils.error_handler import (
    ErrorHandlerMiddleware,
    RequestLoggingMiddleware,
    setup_exception_handlers,
    APIException,
    ValidationError,
)

# 配置日志
logger = get_logger(__name__)


def load_provider_configs():
    """从环境变量加载提供商配置"""
    configs = {
        "openai": {
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com"),
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        "azure": {
            "base_url": os.getenv(
                "AZURE_OPENAI_BASE_URL", "https://your-resource.openai.azure.com"
            ),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        },
        "anthropic": {
            "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "api_version": os.getenv("ANTHROPIC_API_VERSION", "2023-06-01"),
        },
        "dashscope": {
            "base_url": os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"),
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
        },
    }
    return configs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    setup_logging(level="INFO", log_file="./logs/tokenmeter.log", json_format=True)
    logger.info("🚀 Starting TokenMeter...")

    db_manager.init_database()
    logger.info("✅ TokenMeter is ready!")

    yield

    # 关闭时清理
    logger.info("🛑 Shutting down TokenMeter...")
    db_manager.close()


# 创建 FastAPI 应用
app = FastAPI(
    title="TokenMeter", description="企业级 MaaS 成本追踪与归因分析平台", version="0.5.0", lifespan=lifespan
)

# 添加错误处理中间件（最先添加，最后执行）
app.add_middleware(ErrorHandlerMiddleware, debug=False)

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置异常处理器
setup_exception_handlers(app)

# 注册路由
app.include_router(api_router)
app.include_router(budget_router)
app.include_router(auth_router)
app.include_router(export_router)
app.include_router(web_router)


# 代理路由 - 动态处理
@app.api_route("/proxy/{provider}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_route(provider: str, path: str, request: Request):
    """
    代理 API 请求

    支持提供商:
    - openai: /proxy/openai/v1/chat/completions
    - azure: /proxy/azure/openai/deployments/{deployment}/chat/completions
    - anthropic: /proxy/anthropic/v1/messages
    - dashscope: /proxy/dashscope/api/v1/services/aigc/text-generation/generation
    """
    from .database.models import db_manager

    db = db_manager.get_session()

    # 加载配置
    provider_configs = load_provider_configs()
    handler = ProxyHandler(db, provider_configs)

    try:
        response = await handler.proxy_request(
            provider=provider, request=request, path=f"/{path}" if path else ""
        )
        return response
    finally:
        await handler.close()


@app.api_route("/proxy/{provider}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_route_root(provider: str, request: Request):
    """代理根路径请求"""
    from .database.models import db_manager

    db = db_manager.get_session()

    # 加载配置
    provider_configs = load_provider_configs()
    handler = ProxyHandler(db, provider_configs)

    try:
        response = await handler.proxy_request(provider=provider, request=request)
        return response
    finally:
        await handler.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
