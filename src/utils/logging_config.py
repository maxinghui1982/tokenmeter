"""
TokenMeter 日志配置模块
提供结构化日志（JSON格式）
"""
import json
import logging
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar

# 请求上下文变量
request_id_context: ContextVar[str] = ContextVar("request_id", default="")
user_context: ContextVar[str] = ContextVar("user", default="anonymous")


class JSONFormatter(logging.Formatter):
    """JSON 格式日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_context.get() or None,
            "user": user_context.get() or "anonymous",
        }

        # 添加额外字段
        if hasattr(record, "extra_fields"):
            log_obj.update(record.extra_fields)

        # 添加异常信息
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # 添加调用位置信息（开发环境）
        if record.levelno <= logging.DEBUG:
            log_obj["source"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }

        return json.dumps(log_obj, ensure_ascii=False, default=str)


class RequestIDFilter(logging.Filter):
    """自动添加 request_id 到日志记录"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get() or "-"
        return True


def setup_logging(
    level: str = "INFO", log_file: Optional[str] = None, json_format: bool = True
) -> logging.Logger:
    """
    配置日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_file: 日志文件路径（可选）
        json_format: 是否使用 JSON 格式

    Returns:
        配置好的 root logger
    """
    # 创建 formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # 配置 root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # 清除现有 handlers
    root_logger.handlers.clear()

    # 添加控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIDFilter())
    root_logger.addHandler(console_handler)

    # 添加文件输出（如果指定）
    if log_file:
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestIDFilter())
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取 logger 实例"""
    return logging.getLogger(name)


def set_request_id(request_id: Optional[str] = None) -> str:
    """
    设置当前请求的 request_id

    Args:
        request_id: 指定的 request_id，如不指定则自动生成

    Returns:
        request_id
    """
    if request_id is None:
        request_id = str(uuid.uuid4())[:16]
    request_id_context.set(request_id)
    return request_id


def set_user(user: str) -> None:
    """设置当前用户"""
    user_context.set(user)


def get_request_id() -> str:
    """获取当前 request_id"""
    return request_id_context.get() or "-"


def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs) -> None:
    """
    带上下文的日志记录

    Args:
        logger: logger 实例
        level: 日志级别
        message: 日志消息
        **kwargs: 额外字段
    """
    extra = {"extra_fields": kwargs}
    getattr(logger, level.lower())(message, extra=extra)


# 常用日志快捷方法
def info(logger: logging.Logger, message: str, **kwargs):
    """记录 INFO 级别日志"""
    log_with_context(logger, "INFO", message, **kwargs)


def warning(logger: logging.Logger, message: str, **kwargs):
    """记录 WARNING 级别日志"""
    log_with_context(logger, "WARNING", message, **kwargs)


def error(logger: logging.Logger, message: str, **kwargs):
    """记录 ERROR 级别日志"""
    log_with_context(logger, "ERROR", message, **kwargs)


def debug(logger: logging.Logger, message: str, **kwargs):
    """记录 DEBUG 级别日志"""
    log_with_context(logger, "DEBUG", message, **kwargs)
