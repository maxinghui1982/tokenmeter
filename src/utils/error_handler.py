"""
TokenMeter 错误处理模块
提供统一的异常处理和错误响应
"""
import traceback
from typing import Any, Dict, Optional, Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..utils.logging_config import get_logger, set_request_id, get_request_id, error

logger = get_logger(__name__)


class APIException(Exception):
    """API 自定义异常基类"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = 'INTERNAL_ERROR',
        details: Optional[Dict] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIException):
    """参数验证错误"""
    def __init__(self, message: str = '参数验证失败', details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code='VALIDATION_ERROR',
            details=details
        )


class NotFoundError(APIException):
    """资源不存在错误"""
    def __init__(self, message: str = '资源不存在', resource: str = ''):
        super().__init__(
            message=message,
            status_code=404,
            error_code='NOT_FOUND',
            details={'resource': resource}
        )


class AuthorizationError(APIException):
    """权限不足错误"""
    def __init__(self, message: str = '权限不足'):
        super().__init__(
            message=message,
            status_code=403,
            error_code='FORBIDDEN'
        )


class AuthenticationError(APIException):
    """认证失败错误"""
    def __init__(self, message: str = '认证失败'):
        super().__init__(
            message=message,
            status_code=401,
            error_code='UNAUTHORIZED'
        )


class RateLimitError(APIException):
    """请求频率限制错误"""
    def __init__(self, message: str = '请求过于频繁'):
        super().__init__(
            message=message,
            status_code=429,
            error_code='RATE_LIMIT_EXCEEDED'
        )


class ProviderError(APIException):
    """MaaS 提供商错误"""
    def __init__(self, message: str = '提供商服务错误', provider: str = ''):
        super().__init__(
            message=message,
            status_code=502,
            error_code='PROVIDER_ERROR',
            details={'provider': provider}
        )


def create_error_response(
    exception: Exception,
    request_id: str,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """
    创建标准错误响应格式
    
    Args:
        exception: 异常对象
        request_id: 请求ID
        include_traceback: 是否包含堆栈信息（仅开发环境）
    
    Returns:
        错误响应字典
    """
    if isinstance(exception, APIException):
        response = {
            'success': False,
            'error': {
                'code': exception.error_code,
                'message': exception.message,
                'details': exception.details
            },
            'request_id': request_id,
            'status_code': exception.status_code
        }
    else:
        # 未知错误
        response = {
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误',
                'details': {}
            },
            'request_id': request_id,
            'status_code': 500
        }
    
    if include_traceback:
        response['error']['traceback'] = traceback.format_exc()
    
    return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全局错误处理中间件"""
    
    def __init__(self, app: ASGIApp, debug: bool = False):
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并捕获异常"""
        # 设置 request_id
        request_id = request.headers.get('X-Request-ID') or request.query_params.get('request_id')
        set_request_id(request_id)
        
        try:
            response = await call_next(request)
            
            # 在响应头中添加 request_id
            response.headers['X-Request-ID'] = get_request_id()
            return response
            
        except APIException as e:
            # 已知 API 异常
            error(logger, f"API Exception: {e.message}", 
                  error_code=e.error_code,
                  status_code=e.status_code,
                  path=request.url.path,
                  method=request.method)
            
            error_response = create_error_response(e, get_request_id(), self.debug)
            return JSONResponse(
                status_code=e.status_code,
                content=error_response,
                headers={'X-Request-ID': get_request_id()}
            )
            
        except Exception as e:
            # 未知异常
            error(logger, f"Unexpected Exception: {str(e)}",
                  exception_type=type(e).__name__,
                  path=request.url.path,
                  method=request.method,
                  traceback=traceback.format_exc() if self.debug else None)
            
            error_response = create_error_response(e, get_request_id(), self.debug)
            return JSONResponse(
                status_code=500,
                content=error_response,
                headers={'X-Request-ID': get_request_id()}
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """记录请求和响应信息"""
        from time import time
        from ..utils.logging_config import info
        
        start_time = time()
        
        # 设置 request_id
        request_id = request.headers.get('X-Request-ID')
        if not request_id:
            import uuid
            request_id = str(uuid.uuid4())[:16]
        set_request_id(request_id)
        
        # 记录请求开始
        info(logger, f"Request started",
             method=request.method,
             path=request.url.path,
             query=str(request.query_params),
             client=request.client.host if request.client else None,
             user_agent=request.headers.get('user-agent'))
        
        try:
            response = await call_next(request)
            
            # 计算耗时
            duration_ms = (time() - start_time) * 1000
            
            # 记录请求完成
            info(logger, f"Request completed",
                 method=request.method,
                 path=request.url.path,
                 status_code=response.status_code,
                 duration_ms=round(duration_ms, 2))
            
            # 添加响应头
            response.headers['X-Request-ID'] = get_request_id()
            response.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"
            
            return response
            
        except Exception as e:
            duration_ms = (time() - start_time) * 1000
            error(logger, f"Request failed",
                  method=request.method,
                  path=request.url.path,
                  error=str(e),
                  duration_ms=round(duration_ms, 2))
            raise


def setup_exception_handlers(app):
    """为 FastAPI 应用设置异常处理器"""
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        error_response = create_error_response(exc, get_request_id())
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={'X-Request-ID': get_request_id()}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        error_response = create_error_response(exc, get_request_id(), debug=True)
        return JSONResponse(
            status_code=500,
            content=error_response,
            headers={'X-Request-ID': get_request_id()}
        )