"""
TokenMeter Main Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database.models import db_manager
from .api.routes import router as api_router
from .web.dashboard import router as web_router
from .proxy.handler import ProxyHandler
from .utils.logging_config import setup_logging, get_logger
from .utils.error_handler import (
    ErrorHandlerMiddleware, 
    RequestLoggingMiddleware,
    setup_exception_handlers,
    APIException,
    ValidationError
)

# 配置日志
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    setup_logging(
        level='INFO',
        log_file='./logs/tokenmeter.log',
        json_format=True
    )
    logger.info("🚀 Starting TokenMeter...")
    
    db_manager.init_database()
    logger.info("✅ TokenMeter is ready!")
    
    yield
    
    # 关闭时清理
    logger.info("🛑 Shutting down TokenMeter...")
    db_manager.close()


# 创建 FastAPI 应用
app = FastAPI(
    title="TokenMeter",
    description="企业级 MaaS 成本追踪与归因分析平台",
    version="0.5.0",
    lifespan=lifespan
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
app.include_router(web_router)


# 代理路由 - 动态处理
@app.api_route("/proxy/{provider}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_route(provider: str, path: str, request: Request):
    """
    代理 API 请求
    
    示例:
    - /proxy/openai/v1/chat/completions -> 转发到 OpenAI
    - /proxy/azure/openai/deployments/gpt-4/chat/completions -> 转发到 Azure
    """
    from .database.models import db_manager
    db = db_manager.get_session()
    handler = ProxyHandler(db)
    
    try:
        response = await handler.proxy_request(
            provider=provider,
            request=request,
            path=f"/{path}" if path else ""
        )
        return response
    finally:
        await handler.close()


@app.api_route("/proxy/{provider}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_route_root(provider: str, request: Request):
    """代理根路径请求"""
    from .database.models import db_manager
    db = db_manager.get_session()
    handler = ProxyHandler(db)
    
    try:
        response = await handler.proxy_request(
            provider=provider,
            request=request
        )
        return response
    finally:
        await handler.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)